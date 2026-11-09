#!/usr/bin/env python3
"""Audit exact-text consistency for the active lower page-76 corridor.

This is a guardrail pass, not an extraction pass. It checks whether the
currently important page-76 phrases are present across the text witnesses, and
flags sources that should not be treated as authoritative wording.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/plain_text_transcript/active_corridor_witness_consistency"
OUT_JSON = OUT / "active_corridor_witness_consistency.json"
OUT_MD = OUT / "active_corridor_witness_consistency.md"


TEXT_WITNESSES = [
    {
        "id": "canonical_plain_article_body",
        "path": ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt",
        "role": "canonical corrected plain text",
        "authoritative": True,
    },
    {
        "id": "article_with_fonts_text",
        "path": ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_text.txt",
        "role": "DOCM text/font witness",
        "authoritative": True,
    },
    {
        "id": "full_article_corrected",
        "path": ROOT / "full_article_corrected.txt",
        "role": "earlier corrected plain text",
        "authoritative": True,
    },
    {
        "id": "full_article_raw",
        "path": ROOT / "full_article.txt",
        "role": "earlier plain text",
        "authoritative": False,
    },
    {
        "id": "user_plain_article_latest",
        "path": ROOT / "analysis_outputs/plain_text_transcript/user_plain_article_latest.txt",
        "role": "latest user plain text before correction",
        "authoritative": False,
    },
    {
        "id": "user_markdown_transcript",
        "path": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
        "role": "user markdown with bold markup",
        "authoritative": False,
    },
    {
        "id": "user_annotated_transcript",
        "path": ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
        "role": "user prose annotation with formatting notes",
        "authoritative": False,
    },
]

THREED_DATA = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"

TARGETS = [
    {"id": "buying_dip", "phrase": "buying the dip", "role": "orange-highlighted target phrase"},
    {"id": "one_billion", "phrase": "$1 billion", "role": "grey-highlighted money phrase"},
    {"id": "should_sell", "phrase": "should sell", "role": "p78-frame source/edge anchor"},
    {
        "id": "future_bitcoin_earnings",
        "phrase": "future bitcoin earnings",
        "role": "p78-frame source band",
    },
    {"id": "volcano_bonds", "phrase": "Volcano Bonds", "role": "G5 trusted target"},
    {"id": "imf_loan", "phrase": "IMF loan", "role": "G5 neighboring target"},
    {"id": "tagged_mike", "phrase": "I tagged Mike", "role": "lower corridor source band"},
    {"id": "novogratz", "phrase": "Novogratz", "role": "lower corridor source band"},
    {"id": "trust_that_guy", "phrase": "I don't really trust that guy", "role": "Typeka Mix nearby phrase"},
    {"id": "shitcoiner_heart", "phrase": "shitcoiner at heart", "role": "O5 primary target"},
]


def normalize(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2028": "\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("\\.", ".")
    text = re.sub(r"[*_`~#>]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def snippet_for(norm_text: str, norm_phrase: str, fallback: str = "collateralized") -> str:
    idx = norm_text.find(norm_phrase)
    if idx < 0 and fallback:
        idx = norm_text.find(fallback)
    if idx < 0:
        return ""
    start = max(0, idx - 95)
    end = min(len(norm_text), idx + len(norm_phrase) + 95)
    return norm_text[start:end]


def load_3d_char_text() -> str:
    data = json.loads(THREED_DATA.read_text())
    chunks: list[str] = []
    for page in data.get("pages", []):
        if page.get("page") != 76:
            continue
        chars = sorted(page.get("chars", []), key=lambda c: c.get("i", 0))
        chunks.append("".join(ch.get("c", "") for ch in chars))
    return "\n".join(chunks)


def audit_source(source: dict[str, Any], text: str) -> dict[str, Any]:
    norm_text = normalize(text)
    checks = []
    missing = []
    for target in TARGETS:
        norm_phrase = normalize(target["phrase"])
        present = norm_phrase in norm_text
        item = {
            **target,
            "present": present,
            "snippet": snippet_for(norm_text, norm_phrase) if present or target["id"] == "volcano_bonds" else "",
        }
        checks.append(item)
        if not present:
            missing.append(target["id"])

    notes: list[str] = []
    if "volcano_bonds" in missing and "collateralized to pay off the imf" in norm_text:
        notes.append("Contains the corridor sentence with `Volcano Bonds` omitted between `collateralized` and `to pay off the IMF`.")
    if source["id"] == "article_3d_map_page76_chars" and missing:
        notes.append("3D OCR/char labels are incomplete for exact wording; use for navigation only.")

    return {
        **source,
        "path": str(source.get("path", "")),
        "exists": True,
        "charCount": len(text),
        "presentCount": sum(1 for check in checks if check["present"]),
        "missingCount": len(missing),
        "missing": missing,
        "checks": checks,
        "notes": notes,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    sources: list[dict[str, Any]] = []
    for source in TEXT_WITNESSES:
        if not source["path"].exists():
            sources.append({**source, "path": str(source["path"]), "exists": False})
            continue
        sources.append(audit_source(source, read_text(source["path"])))

    three_d_source = {
        "id": "article_3d_map_page76_chars",
        "path": THREED_DATA,
        "role": "3D viewer OCR/char labels for page 76",
        "authoritative": False,
    }
    sources.append(audit_source(three_d_source, load_3d_char_text()))

    critical_failures = [
        {
            "source": source["id"],
            "missing": source.get("missing", []),
            "notes": source.get("notes", []),
        }
        for source in sources
        if source.get("exists")
        and (source.get("id") in {"user_plain_article_latest", "article_3d_map_page76_chars"})
        and source.get("missing")
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active lower page-76 corridor text-witness consistency; no key derivation",
        "targets": TARGETS,
        "sources": sources,
        "criticalFailures": critical_failures,
        "assessment": [
            "The corrected/DOCM witnesses preserve all active corridor targets.",
            "The latest raw user plain text omits `Volcano Bonds`; do not use it as authoritative for G5 wording.",
            "The 3D character/OCR layer misses several active targets and remains navigation-only.",
        ],
        "decision": "For lower page-76 work, use canonical_plain_article_body/article_with_fonts_text for exact wording, then use the 3D viewer and source crops only for geometry.",
        "nextMove": "Continue source-gated geometry work; only reopen font/text extraction if a new clue names a unit/order or a new source changes the active corridor wording.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Active Corridor Witness Consistency",
        "",
        "Scope: check the exact text witnesses for the active lower page-76 corridor. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        "## Target Phrases",
        "",
        "| id | phrase | role |",
        "| --- | --- | --- |",
    ]
    for target in TARGETS:
        lines.append(f"| `{target['id']}` | `{target['phrase']}` | {target['role']} |")

    lines.extend(
        [
            "",
            "## Witness Results",
            "",
            "| witness | role | authoritative | present | missing | notes |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for source in sources:
        if not source.get("exists"):
            lines.append(f"| `{source['id']}` | {source['role']} | `{source['authoritative']}` | n/a | missing file | |")
            continue
        missing = ", ".join(f"`{item}`" for item in source["missing"]) or "none"
        notes = " ".join(source.get("notes", []))
        lines.append(
            f"| `{source['id']}` | {source['role']} | `{source['authoritative']}` | "
            f"{source['presentCount']}/{len(TARGETS)} | {missing} | {notes} |"
        )

    lines.extend(
        [
            "",
            "## Important Failure",
            "",
            "- `user_plain_article_latest` is not safe as the exact G5 source because it contains the local sentence but omits `Volcano Bonds`.",
            "- `article_3d_map_page76_chars` is not safe as exact text because it misses active targets already identified by source crops and corrected transcript.",
            "",
            "## Decision",
            "",
            "- Use `analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt` and `analysis_outputs/docm_format_sources/article_with_fonts_text.txt` for exact wording.",
            "- Use the 3D view, bridge sheet, and source crops for geometry/navigation only.",
            "- Do not reopen text/font extraction unless a new source or clue names the extraction unit/order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print("critical_failures", len(critical_failures))


if __name__ == "__main__":
    main()
