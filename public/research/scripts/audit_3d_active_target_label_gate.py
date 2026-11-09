#!/usr/bin/env python3
"""Audit the 3D map word-label layer around active target terms.

The 3D map is useful for visual navigation, but its word layer came from OCR
and can omit or distort text. This pass checks only whether the current active
target/corridor phrases are present in that layer versus the corrected
canonical article text. It does not derive keys, hash strings, generate seed
phrases, scan WIF/Base58, or check addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
CANONICAL = ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt"
OUT = ROOT / "analysis_outputs/3d_article_map/active_target_label_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_target_label_gate.json"
OUT_MD = OUT / "active_target_label_gate.md"


TARGETS = [
    {"id": "p76_open_heart", "page": 76, "phrase": "Open your heart to Bitcoin", "role": "orange target"},
    {"id": "p76_buying_dip", "page": 76, "phrase": "buying the dip", "role": "orange target"},
    {"id": "p76_bukele", "page": 76, "phrase": "President Nayib Bukele", "role": "corridor target"},
    {"id": "p76_one_billion", "page": 76, "phrase": "$1 billion", "role": "grey target"},
    {"id": "p76_should_sell", "page": 76, "phrase": "should sell", "role": "p78 frame edge phrase"},
    {"id": "p76_future_earnings", "page": 76, "phrase": "future bitcoin earnings", "role": "p78 frame band"},
    {"id": "p76_volcano_bonds", "page": 76, "phrase": "Volcano Bonds", "role": "G5 / grey target"},
    {"id": "p76_imf_loan", "page": 76, "phrase": "IMF loan", "role": "corridor target"},
    {"id": "p76_mike_novogratz", "page": 76, "phrase": "Mike Novogratz", "role": "Typeka Mix anchor"},
    {"id": "p76_trust_that_guy", "page": 76, "phrase": "trust that guy", "role": "Typeka Mix anchor"},
    {"id": "p76_shitcoiner_heart", "page": 76, "phrase": "shitcoiner at heart", "role": "O5 / orange target"},
    {"id": "p77_100000", "page": 77, "phrase": "100,000", "role": "zero/#0 benchmark"},
    {"id": "p77_has_gone", "page": 77, "phrase": "has gone", "role": "known correction"},
    {"id": "p77_nas_gone", "page": 77, "phrase": "nas gone", "role": "known OCR error"},
    {"id": "p77_monetizing", "page": 77, "phrase": "It does this by monetizing", "role": "p77 near-miss source"},
    {"id": "p78_fills_in_gap", "page": 78, "phrase": "Bitcoin fills in the gap", "role": "known correction"},
    {"id": "p78_fills_gap", "page": 78, "phrase": "Bitcoin fills the gap", "role": "known OCR/alternate wording"},
]


def normalize(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": "-",
        "\u2013": "-",
        "\u00a0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r"[^a-z0-9$%#]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def context(text: str, phrase: str, radius: int = 90) -> str:
    folded = normalize(text)
    needle = normalize(phrase)
    idx = folded.find(needle)
    if idx < 0:
        return ""
    return folded[max(0, idx - radius) : idx + len(needle) + radius]


def page_texts(data: dict[str, Any]) -> dict[int, str]:
    texts: dict[int, str] = {}
    for page in data["pages"]:
        words = page.get("words", [])
        texts[int(page["page"])] = " ".join(str(word.get("text", "")) for word in words)
    return texts


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    canonical = CANONICAL.read_text(encoding="utf-8")
    page_text = page_texts(data)
    canonical_norm = normalize(canonical)

    rows = []
    for target in TARGETS:
        text3d = page_text.get(target["page"], "")
        phrase = target["phrase"]
        rows.append(
            {
                **target,
                "canonicalHasPhrase": normalize(phrase) in canonical_norm,
                "threeDHasPhrase": normalize(phrase) in normalize(text3d),
                "threeDContext": context(text3d, phrase),
            }
        )

    active_ids = {
        "p76_buying_dip",
        "p76_bukele",
        "p76_one_billion",
        "p76_volcano_bonds",
        "p76_imf_loan",
        "p76_mike_novogratz",
        "p76_trust_that_guy",
        "p76_shitcoiner_heart",
    }
    active_rows = [row for row in rows if row["id"] in active_ids]
    active_missing = [row for row in active_rows if row["canonicalHasPhrase"] and not row["threeDHasPhrase"]]
    suspect_present = [row for row in rows if row["id"] in {"p77_nas_gone", "p78_fills_gap"} and row["threeDHasPhrase"]]
    trusted_present = [row for row in rows if row["id"] in {"p77_100000", "p76_should_sell", "p76_future_earnings"} and row["threeDHasPhrase"]]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D map active-target label gate; no key derivation or candidate generation",
        "sources": {"threeDMap": str(DATA.relative_to(ROOT)), "canonicalText": str(CANONICAL.relative_to(ROOT))},
        "pageWordCounts": {str(page): len(data_page.get("words", [])) for data_page in data["pages"] for page in [data_page["page"]]},
        "rows": rows,
        "activeMissingCount": len(active_missing),
        "activeMissingIds": [row["id"] for row in active_missing],
        "suspectPresentIds": [row["id"] for row in suspect_present],
        "trustedPresentIds": [row["id"] for row in trusted_present],
        "assessment": [
            "The 3D word-label layer is not exact enough for active target extraction.",
            "It preserves some navigation anchors such as `should sell`, `future bitcoin earnings`, and p77 `100,000`.",
            "It misses or distorts critical active phrases, including G5/O5-style target text; the canonical DOCM/plain text remains the wording truth.",
            "The 3D viewer should stay a visual/geometry map only. Any future selected region must be translated to exact text using the corrected transcript or source crop review.",
        ],
        "decision": "Do not use article_3d_map_data word labels as extraction text for the page-76 lower corridor.",
        "nextMove": "If the viewer is edited later, add a visible 'OCR label only / exact text in transcript' cue for target phrases; otherwise continue source-gated investigation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 3D Active Target Label Gate",
        "",
        "Scope: check whether the 3D map word-label layer can be trusted for the active page-76 target/corridor phrases. No key derivation, hashing, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active target phrases missing from 3D word labels: `{len(active_missing)}`",
        f"- Suspect OCR/alternate phrases present: `{', '.join(result['suspectPresentIds']) or 'none'}`",
        f"- Trusted navigation phrases present: `{', '.join(result['trustedPresentIds']) or 'none'}`",
        "",
        "## Phrase Checks",
        "",
        "| id | page | role | canonical | 3D label | context |",
        "|---|---:|---|---:|---:|---|",
    ]
    for row in rows:
        ctx = row["threeDContext"] or "-"
        if len(ctx) > 180:
            ctx = ctx[:177] + "..."
        lines.append(
            f"| `{row['id']}` | {row['page']} | {row['role']} | `{row['canonicalHasPhrase']}` | `{row['threeDHasPhrase']}` | `{ctx}` |"
        )

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("activeMissingCount:", len(active_missing))
    print("suspectPresentIds:", ",".join(result["suspectPresentIds"]) or "none")


if __name__ == "__main__":
    main()
