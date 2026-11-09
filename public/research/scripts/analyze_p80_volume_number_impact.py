#!/usr/bin/env python3
"""Audit the p80 `16 FL OZ` vs `6 FL OZ` ambiguity.

Earlier p80/package geometry reads used a clipped crop that recorded
`6 FL OZ (473 mL)`. The full package-copy audit notes that the visible/metric
pair is almost certainly `16 FL OZ (473 mL)`, because 473 mL equals 16 fl oz.

This checks what changes if `16` is treated as the canonical visible number.
No key candidates or hashes are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
PACKAGE_JSON = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json"
LINE_EVIDENCE = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"
OUT = ROOT / "analysis_outputs/source_audit/p80_volume_number_impact"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p80_volume_number_impact.json"
OUT_MD = OUT / "p80_volume_number_impact.md"


def load_page76() -> dict:
    data = json.loads(CANONICAL.read_text())
    return next(page for page in data["pages"].values() if page.get("articlePage") == 76)


def page76_line(page: dict, n: int, zero_based: bool) -> str:
    idx = n if zero_based else n - 1
    if 0 <= idx < len(page["lines"]):
        return page["lines"][idx]["text"].strip()
    return ""


def page76_word(page: dict, n: int) -> str:
    idx = n - 1
    if 0 <= idx < len(page["words"]):
        return page["words"][idx]["text"]
    return ""


def matching_landing(line_index: int) -> list[dict]:
    data = json.loads(LINE_EVIDENCE.read_text())
    return [row for row in data["scoredLandings"] if row["targetLine"] == line_index]


def main() -> None:
    package = json.loads(PACKAGE_JSON.read_text())
    page = load_page76()

    numbers = {
        "5_symptom_relief": 5,
        "16_fl_oz_likely": 16,
        "6_fl_oz_clipped_crop": 6,
        "100_percent_pow": 100,
        "473_ml": 473,
        "page_number": 80,
    }

    number_checks = []
    for label, number in numbers.items():
        zero_line = page76_line(page, number, zero_based=True)
        one_line = page76_line(page, number, zero_based=False)
        word = page76_word(page, number)
        number_checks.append(
            {
                "label": label,
                "number": number,
                "page76LineZeroBased": zero_line,
                "page76LineOneBased": one_line,
                "page76WordOneBased": word,
                "lineOffsetLandingsAtZeroBasedLine": matching_landing(number),
                "lineOffsetLandingsAtOneBasedLine": matching_landing(number - 1),
            }
        )

    # Pull out the crucial comparison so the report is explicit.
    line16 = next(row for row in number_checks if row["label"] == "16_fl_oz_likely")
    line6 = next(row for row in number_checks if row["label"] == "6_fl_oz_clipped_crop")

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Impact audit for p80 volume number ambiguity; no key derivation.",
        "source": str(PACKAGE_JSON),
        "packageAssessment": package.get("assessment", []),
        "numberChecks": number_checks,
        "assessment": [
            "`16 FL OZ (473 mL)` should be treated as the canonical package volume; `6 FL OZ` is a clipped-crop reading.",
            "Using 16 as a zero-based page-76 line selector lands exactly on `laundering lobotomy. It’s a stun gun to the genitals.`, the O3+3 -> B3 line-offset hit.",
            "Using 6 instead lands on the B1/Gotta line and does not explain the p80 volume/metric pair.",
            "This strengthens p80 as provenance support for the B3/stun-gun line, but it does not explain #2/#4 or name an extraction unit.",
            "Future p80 audits should record the volume as `16 FL OZ (473 mL)` while noting the old cropped `6` reading as a source-fidelity artifact.",
        ],
        "nextMove": "Preserve p80 `16` as support for the B3 line-offset hit, then look for physical/source evidence that connects the full package layer to the remaining landing set.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# P80 Volume Number Impact Audit",
        "",
        "Scope: check what changes if the p80 package volume is read as `16 FL OZ (473 mL)` instead of the clipped `6 FL OZ (473 mL)`. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Key Comparison",
        "",
        f"- `16` zero-based page-76 line: `{line16['page76LineZeroBased']}`",
        f"- `16` one-based page-76 line: `{line16['page76LineOneBased']}`",
        f"- `16` one-based word: `{line16['page76WordOneBased']}`",
        f"- `6` zero-based page-76 line: `{line6['page76LineZeroBased']}`",
        f"- `6` one-based page-76 line: `{line6['page76LineOneBased']}`",
        f"- `6` one-based word: `{line6['page76WordOneBased']}`",
        "",
        "## Number Checks",
        "",
        "| source | number | zero-based line | one-based line | one-based word | matching line-offset landing |",
        "|---|---:|---|---|---|---|",
    ]
    for row in number_checks:
        zero = row["page76LineZeroBased"].replace("|", "\\|")
        one = row["page76LineOneBased"].replace("|", "\\|")
        word = row["page76WordOneBased"].replace("|", "\\|")
        landing_ids = []
        for hit in row["lineOffsetLandingsAtZeroBasedLine"]:
            landing_ids.append(f"{hit['sourceId']}+{hit['sourceIndex']} zero")
        for hit in row["lineOffsetLandingsAtOneBasedLine"]:
            landing_ids.append(f"{hit['sourceId']}+{hit['sourceIndex']} one")
        md.append(f"| `{row['label']}` | {row['number']} | {zero} | {one} | `{word}` | `{', '.join(landing_ids) or '-'}` |")

    md.extend(
        [
            "",
            "## Assessment",
            "",
        ]
    )
    for item in result["assessment"]:
        md.append(f"- {item}")
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
