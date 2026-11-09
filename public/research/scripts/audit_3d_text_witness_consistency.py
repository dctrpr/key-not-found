#!/usr/bin/env python3
"""Compare the 3D map text witness against the corrected article text.

This is a source-fidelity check, not a key-generation pass. The goal is to
identify places where the 3D map's internal Markdown/OCR text should not be
trusted as final wording even though its page images/geometry remain useful.
"""

from __future__ import annotations

import difflib
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
CANONICAL = ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt"
OUT_DIR = ROOT / "analysis_outputs/plain_text_transcript"
OUT_JSON = OUT_DIR / "3d_text_witness_consistency_audit.json"
OUT_MD = OUT_DIR / "3d_text_witness_consistency_audit.md"


KNOWN_CHECKS = [
    ("puts an end", "puts and end"),
    ("Volcano Bonds", "collateralized to pay off the IMF"),
    ("has gone", "nas gone"),
    ("100,000", "1000,000"),
    ("salesmen", "salesman"),
    ("gargantuanly", "gargantually"),
    ("money printing", "requires printing"),
    ("$2 trillion fiat cuck-bucks", "2 trillion fiat cuck bucks"),
    ("Bitcoin fills in the gap", "Bitcoin fills the gap"),
    ("The economy of love is infinitely more efficient than hate and war.", "right there in the Genesis Block.\n\nTo wrap this up"),
    ("gets monetized for the first time", "gets monetized and for the first time"),
]


def article_only(text: str) -> str:
    marker = "BITCOIN IS TOXIC AF"
    idx = text.find(marker)
    return text[idx:] if idx >= 0 else text


def flatten_model_text(model: dict) -> str:
    pages = sorted(model["pages"].values(), key=lambda page: page["articlePage"])
    return "\n".join(page["plain"] for page in pages if 75 <= page["articlePage"] <= 79)


def normalize_for_tokens(text: str) -> str:
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
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9$%']+|[.,;:!?()\"-]", normalize_for_tokens(text))


def nearby(text: str, needle: str, span: int = 80) -> str:
    folded = normalize_for_tokens(text)
    n = normalize_for_tokens(needle)
    idx = folded.find(n)
    if idx < 0:
        return ""
    return folded[max(0, idx - span) : idx + len(n) + span]


def diff_windows(a: list[str], b: list[str], limit: int = 18) -> list[dict]:
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    windows = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        windows.append(
            {
                "tag": tag,
                "canonicalRange": [i1, i2],
                "modelRange": [j1, j2],
                "canonical": " ".join(a[max(0, i1 - 8) : min(len(a), i2 + 8)]),
                "model": " ".join(b[max(0, j1 - 8) : min(len(b), j2 + 8)]),
            }
        )
        if len(windows) >= limit:
            break
    return windows


def main() -> None:
    model = json.loads(MODEL.read_text())
    canonical_text = article_only(CANONICAL.read_text())
    model_text = flatten_model_text(model)
    can_tokens = tokens(canonical_text)
    model_tokens = tokens(model_text)

    matcher = difflib.SequenceMatcher(a=can_tokens, b=model_tokens, autojunk=False)
    matching = sum(block.size for block in matcher.get_matching_blocks())
    ratio = matching / max(len(can_tokens), 1)

    checks = []
    for canonical_phrase, suspect_phrase in KNOWN_CHECKS:
        checks.append(
            {
                "canonicalPhrase": canonical_phrase,
                "suspectPhrase": suspect_phrase,
                "canonicalHasCanonical": normalize_for_tokens(canonical_phrase) in normalize_for_tokens(canonical_text),
                "modelHasCanonical": normalize_for_tokens(canonical_phrase) in normalize_for_tokens(model_text),
                "modelHasSuspect": normalize_for_tokens(suspect_phrase) in normalize_for_tokens(model_text),
                "modelContextCanonical": nearby(model_text, canonical_phrase),
                "modelContextSuspect": nearby(model_text, suspect_phrase),
            }
        )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Compare corrected DOCM-derived text against 3D map internal text; no key derivation.",
        "sources": {"canonical": str(CANONICAL), "model": str(MODEL)},
        "tokenCounts": {"canonical": len(can_tokens), "model": len(model_tokens)},
        "sequenceMatchRatio": round(ratio, 6),
        "knownChecks": checks,
        "diffWindows": diff_windows(can_tokens, model_tokens),
        "assessment": [
            "The 3D map text is close enough for visual labels, but it is not exact wording truth.",
            "Use the corrected DOCM-derived plain text for phrase/word selectors after a visual region is selected.",
            "Do not derive key material from the 3D map OCR/Markdown text without reconciling the affected span first.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# 3D Text Witness Consistency Audit",
        "",
        "Scope: compare the 3D map's internal text witness against the corrected DOCM-derived article text. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Canonical tokens: `{len(can_tokens)}`",
        f"- 3D-map tokens: `{len(model_tokens)}`",
        f"- Sequence match ratio: `{result['sequenceMatchRatio']}`",
        "",
        "## Known Hotspots",
        "",
    ]
    for item in checks:
        lines.append(
            f"- `{item['canonicalPhrase']}`: canonical has canonical=`{item['canonicalHasCanonical']}`, "
            f"3D has canonical=`{item['modelHasCanonical']}`, 3D has suspect=`{item['modelHasSuspect']}`"
        )
        if item["modelContextSuspect"]:
            lines.append(f"  - 3D suspect context: `{item['modelContextSuspect']}`")

    lines.extend(["", "## First Diff Windows", ""])
    for item in result["diffWindows"]:
        lines.append(f"- `{item['tag']}` canonical[{item['canonicalRange'][0]}:{item['canonicalRange'][1]}] model[{item['modelRange'][0]}:{item['modelRange'][1]}]")
        lines.append(f"  - canonical: `{item['canonical']}`")
        lines.append(f"  - 3D model: `{item['model']}`")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The 3D map remains useful for visual/geometry inspection, but its text layer is a label witness, not exact source truth.",
            "- The most important live discrepancy for page-77 text is `has gone` vs 3D-map `nas gone`; the zero hotspot remains canonical `100,000`, not `1000,000`.",
            "- Future selectors should use this order: high-res scan for geometry, corrected DOCM/plain text for wording, and the 3D map only for navigation/visual labeling.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
