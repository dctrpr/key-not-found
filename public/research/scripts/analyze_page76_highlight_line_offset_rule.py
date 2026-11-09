#!/usr/bin/env python3
"""Audit whether page-76 highlight numbers act as line offsets.

After the G5/O5 audit found that "Volcano Bonds" is exactly five corrected
text lines above "shitcoiner at heart", this checks whether the same simple
rule appears elsewhere on page 76:

    from highlighted unit N, move N text lines up/down

No key candidates are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule"
OUT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT / "page76_highlight_line_offset_rule.json"
OUT_MD = OUT / "page76_highlight_line_offset_rule.md"


UNITS = [
    {"id": "O1", "kind": "orange", "index": 1, "line": 0, "label": "Get some toxicity / Open your heart to"},
    {"id": "O2", "kind": "orange", "index": 2, "line": 1, "label": "Bitcoin."},
    {"id": "B1", "kind": "grey", "index": 1, "line": 6, "label": "Gotta be this way... post-1971 fiat money"},
    {"id": "B2", "kind": "grey", "index": 2, "line": 7, "label": "nonsense"},
    {"id": "O3", "kind": "orange", "index": 3, "line": 13, "label": "by the rancid catnip of fiat money"},
    {"id": "B3", "kind": "grey", "index": 3, "line": 16, "label": "It's a stun gun to the genitals"},
    {"id": "O4", "kind": "orange", "index": 4, "line": 22, "label": "buying the dip"},
    {"id": "B4", "kind": "grey", "index": 4, "line": 25, "label": "$1 billion"},
    {"id": "B5", "kind": "grey", "index": 5, "line": 27, "label": "Volcano Bonds"},
    {"id": "O5", "kind": "orange", "index": 5, "line": 32, "label": "shitcoiner at heart"},
]


def load_lines() -> list[str]:
    data = json.loads(CANONICAL.read_text())
    page = next(page for page in data["pages"].values() if page.get("articlePage") == 76)
    return [line["text"].rstrip() for line in page["lines"]]


def line_units() -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    for unit in UNITS:
        out.setdefault(unit["line"], []).append(unit)
    return out


def unit_summary(units: list[dict]) -> str:
    if not units:
        return ""
    return ", ".join(f"{u['id']} {u['label']}" for u in units)


def landing_rows(lines: list[str]) -> list[dict]:
    by_line = line_units()
    rows = []
    for unit in UNITS:
        for direction, sign in (("down", 1), ("up", -1)):
            target_line = unit["line"] + sign * unit["index"]
            if 0 <= target_line < len(lines):
                target_units = by_line.get(target_line, [])
                rows.append(
                    {
                        "sourceId": unit["id"],
                        "sourceKind": unit["kind"],
                        "sourceIndex": unit["index"],
                        "sourceLine": unit["line"],
                        "sourceLabel": unit["label"],
                        "direction": direction,
                        "targetLine": target_line,
                        "targetText": lines[target_line],
                        "targetUnits": [u["id"] for u in target_units],
                        "targetUnitLabels": [u["label"] for u in target_units],
                        "isHighlightHit": bool(target_units),
                    }
                )
            else:
                rows.append(
                    {
                        "sourceId": unit["id"],
                        "sourceKind": unit["kind"],
                        "sourceIndex": unit["index"],
                        "sourceLine": unit["line"],
                        "sourceLabel": unit["label"],
                        "direction": direction,
                        "targetLine": target_line,
                        "targetText": "",
                        "targetUnits": [],
                        "targetUnitLabels": [],
                        "isHighlightHit": False,
                        "outOfRange": True,
                    }
                )
    return rows


def pair_rows(lines: list[str]) -> list[dict]:
    rows = []
    for source in UNITS:
        for target in UNITS:
            if source["id"] == target["id"]:
                continue
            gap = target["line"] - source["line"]
            if gap <= 0:
                continue
            rows.append(
                {
                    "sourceId": source["id"],
                    "targetId": target["id"],
                    "sourceIndex": source["index"],
                    "targetIndex": target["index"],
                    "sourceLine": source["line"],
                    "targetLine": target["line"],
                    "lineGap": gap,
                    "gapEqualsSourceIndex": gap == source["index"],
                    "gapEqualsTargetIndex": gap == target["index"],
                    "sameIndex": source["index"] == target["index"],
                    "sourceLabel": source["label"],
                    "targetLabel": target["label"],
                    "sourceLineText": lines[source["line"]],
                    "targetLineText": lines[target["line"]],
                }
            )
    return rows


def main() -> None:
    lines = load_lines()
    landings = landing_rows(lines)
    pairs = pair_rows(lines)
    down_hits = [row for row in landings if row["direction"] == "down" and row["isHighlightHit"]]
    up_hits = [row for row in landings if row["direction"] == "up" and row["isHighlightHit"]]
    gap_equals_source = [row for row in pairs if row["gapEqualsSourceIndex"]]
    gap_equals_both = [row for row in pairs if row["gapEqualsSourceIndex"] and row["gapEqualsTargetIndex"]]
    same_index_gap = [row for row in pairs if row["sameIndex"] and row["gapEqualsSourceIndex"]]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 highlight-number-as-line-offset audit; no key derivation.",
        "units": UNITS,
        "landingRows": landings,
        "downHighlightHits": down_hits,
        "upHighlightHits": up_hits,
        "gapEqualsSourceIndexPairs": gap_equals_source,
        "gapEqualsBothIndexPairs": gap_equals_both,
        "sameIndexGapPairs": same_index_gap,
        "assessment": [
            "The five-line G5/O5 locator is part of a broader, but incomplete, line-offset pattern.",
            "Clean down-offset hits exist for O1->O2, B1->B2, O3->B3, and B5->O5.",
            "The same-index hits are O3->B3 and B5->O5; O1->O2 and B1->B2 are continuation-like but not same-index.",
            "No clean down-offset highlight hit exists for #2 or #4 as a complete rule.",
            "This supports highlight numbering as a locator/orientation mechanism, not yet an extraction unit.",
        ],
        "nextMove": "Inspect whether the down-offset hit sequence O1/O2, B1/B2, O3/B3, B5/O5 carries ordering/color information, while keeping #2/#4 failures as a constraint.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Page 76 Highlight Line-Offset Rule Audit",
        "",
        "Scope: test whether a highlighted unit's number tells us how many corrected text lines to move. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Down-Offset Highlight Hits",
        "",
        "| source | rule | target | target line text |",
        "|---|---:|---|---|",
    ]
    for row in down_hits:
        target = ", ".join(row["targetUnits"])
        text = row["targetText"].replace("|", "\\|")
        md.append(f"| {row['sourceId']} `{row['sourceLabel']}` | +{row['sourceIndex']} lines | {target} | {text} |")

    md.extend(
        [
            "",
            "## All Down-Offset Landings",
            "",
            "| source | target line | highlighted target | line text |",
            "|---|---:|---|---|",
        ]
    )
    for row in [r for r in landings if r["direction"] == "down"]:
        target = ", ".join(row["targetUnits"]) or "-"
        text = row["targetText"].replace("|", "\\|")
        md.append(f"| {row['sourceId']} +{row['sourceIndex']} | {row['targetLine']} | {target} | {text} |")

    md.extend(
        [
            "",
            "## Gap Matches",
            "",
            "| source | target | line gap | source index | target index | same index |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in gap_equals_source:
        md.append(
            f"| {row['sourceId']} | {row['targetId']} | {row['lineGap']} | {row['sourceIndex']} | {row['targetIndex']} | {row['sameIndex']} |"
        )

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The G5/O5 five-line locator is real, but it is not isolated.",
            "- Down-offset hits appear for `O1 -> O2`, `B1 -> B2`, `O3 -> B3`, and `B5 -> O5`.",
            "- The same-index subset is cleaner but shorter: `O3 -> B3` and `B5 -> O5`.",
            "- The rule is incomplete because #2 and #4 do not land on highlighted target units under the same simple operation.",
            "- Treat this as locator/orientation evidence. It still does not define whether to extract words, letters, colors, or adjacent text.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
