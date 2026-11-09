#!/usr/bin/env python3
"""Test the visible OVERDOSE dosage numbers as small human selectors.

The provenance layer repeatedly exposes simple counts/numbers:
- five opener capsules on p73
- five reused p79 pill fragments
- p80 "5 SYMPTOM RELIEF"
- p80 "6 FL OZ"

This pass applies only 5 and 6 as one-based selectors to already-verified
page-76 lists. It is deliberately not a broad brute-force/index search and it
does not generate key candidates.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
MANUAL_GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT = ROOT / "analysis_outputs/source_audit/overdose_dose_number_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_dose_number_selector.json"
OUT_MD = OUT / "overdose_dose_number_selector.md"

NUMBERS = [5, 6]
INSTRUCTION_RE = re.compile(r"\b(read|take|fold|mirror|line|word|letter|key|private|seed|left|right|reverse|backward|up|down)\b", re.I)
TARGET_RE = re.compile(r"\b(bitcoin|shitcoin|volcano|imf|bukele|billion|dip|heart|rabbit|toxic|dose|symptom)\b", re.I)


def page76_lines() -> list[dict]:
    data = json.loads(CANONICAL.read_text())
    for page in data["pages"].values():
        if page.get("articlePage") == 76:
            return page["lines"]
    raise RuntimeError("page 76 not found")


def orange_page76() -> list[dict]:
    data = json.loads(MANUAL_ORANGE.read_text())
    rows = []
    for key, text in data["visualOrangeBoxes"].items():
        if key.startswith("p76_orange_"):
            rows.append({"id": key, "kind": "orange", "text": text})
    return sorted(rows, key=lambda row: int(row["id"].rsplit("_", 1)[1]))


def grey_page76() -> list[dict]:
    data = json.loads(MANUAL_GREY.read_text())
    rows = []
    for row in data["rows"]:
        if row["page"] == 76:
            rows.append(
                {
                    "id": row["id"],
                    "kind": "grey",
                    "text": row["expected"],
                    "y": row["highresBox"][1],
                    "x": row["highresBox"][0],
                }
            )
    return sorted(rows, key=lambda row: int(row["id"].rsplit("_", 1)[1]))


def page76_highlight_reading_order() -> list[dict]:
    orange = orange_page76()
    grey = grey_page76()
    orange_y = {
        "p76_orange_1": 203,
        "p76_orange_2": 258,
        "p76_orange_3": 1376,
        "p76_orange_4": 2614,
        "p76_orange_5": 2932,
    }
    rows = []
    for row in orange:
        rows.append({**row, "y": orange_y.get(row["id"], 0), "x": 0})
    for row in grey:
        rows.append(row)
    return sorted(rows, key=lambda row: (row["y"], row["x"]))


def corridor_lines() -> list[dict]:
    lines = page76_lines()
    wanted = []
    for row in lines:
        if 19 <= row["lineIndex"] <= 32:
            wanted.append(
                {
                    "id": f"p76_line_{row['lineIndex']}",
                    "kind": "line",
                    "lineIndex": row["lineIndex"],
                    "text": row["text"].strip(),
                }
            )
    return wanted


def highlighted_corridor_lines() -> list[dict]:
    highlighted = {22, 25, 27, 28, 29, 31, 32}
    return [row for row in corridor_lines() if row["lineIndex"] in highlighted]


def p80_symptom_lines() -> list[dict]:
    text = json.loads(MANUAL_ORANGE.read_text())["visualOrangeBoxes"]["p80_orange_1"]
    parts = [part.strip() for part in text.split("/") if part.strip()]
    return [{"id": f"p80_symptom_{i}", "kind": "package_line", "text": part} for i, part in enumerate(parts, 1)]


def select_number(surface_name: str, rows: list[dict], number: int) -> dict:
    if number > len(rows):
        return {
            "surface": surface_name,
            "number": number,
            "available": len(rows),
            "selected": None,
            "instructionHit": False,
            "targetHit": False,
        }
    selected = rows[number - 1]
    text = selected["text"]
    return {
        "surface": surface_name,
        "number": number,
        "available": len(rows),
        "selected": selected,
        "instructionHit": bool(INSTRUCTION_RE.search(text)),
        "targetHit": bool(TARGET_RE.search(text)),
    }


def main() -> None:
    surfaces = {
        "page76_orange_boxes": orange_page76(),
        "page76_grey_boxes": grey_page76(),
        "page76_all_highlights_reading_order": page76_highlight_reading_order(),
        "page76_el_salvador_corridor_lines": corridor_lines(),
        "page76_highlighted_corridor_lines": highlighted_corridor_lines(),
        "page80_package_lines": p80_symptom_lines(),
    }
    selections = []
    for name, rows in surfaces.items():
        for number in NUMBERS:
            selections.append(select_number(name, rows, number))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "OVERDOSE visible numbers 5 and 6 as bounded selectors; no key derivation",
        "numberSources": [
            "p73 has five opener capsules",
            "p79 has five reused pill fragments",
            "p80 says 5 SYMPTOM RELIEF",
            "p80 says 6 FL OZ",
        ],
        "surfaces": {name: rows for name, rows in surfaces.items()},
        "selections": selections,
        "assessment": [
            "The number 5 reinforces the existing page-76 lower corridor: p76 orange #5 is shitcoiner at heart, and p76 grey #5 is Volcano Bonds.",
            "The number 6 selects the volcano-mining line in the El Salvador corridor, but only when applied to corridor lines.",
            "No selected item contains a direct instruction such as read/take/fold/mirror/word/letter/key.",
            "The dosage numbers corroborate the same semantic cluster but do not supply the missing extraction rule.",
        ],
        "nextMove": "Do not keep expanding numeric selectors. Search for an explicit source/layout instruction that tells how the five-capsule or p80 dosage layer should choose page-76 words or letters.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# OVERDOSE Dose-Number Selector Audit",
        "",
        "Scope: apply only the visible OVERDOSE numbers `5` and `6` to already verified page-76 lists. No key candidates are generated.",
        "",
        "## Number Sources",
        "",
        "- p73 has five opener capsules.",
        "- p79 has five reused pill fragments.",
        "- p80 says `5 SYMPTOM RELIEF`.",
        "- p80 says `6 FL OZ`.",
        "",
        "## Selections",
        "",
    ]
    for row in selections:
        chosen = row["selected"]
        if chosen:
            flags = []
            if row["instructionHit"]:
                flags.append("instruction-word")
            if row["targetHit"]:
                flags.append("target-word")
            flag_text = ", ".join(flags) if flags else "-"
            lines.append(
                f"- `{row['surface']}` #{row['number']} of {row['available']}: `{chosen['text']}` [{flag_text}]"
            )
        else:
            lines.append(f"- `{row['surface']}` #{row['number']} of {row['available']}: unavailable")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The strongest hit is corroborative, not instructional: `5` selects p76 orange #5 `shitcoiner at heart.` and p76 grey #5 `Volcano Bonds`.",
            "- `6` selects the corridor line `he was going to tap his nation's volcanoes to mine`, which keeps the same El Salvador / volcano context alive.",
            "- None of the selected strings contains a direct instruction such as `read`, `take`, `fold`, `mirror`, `word`, `letter`, or `key`.",
            "- This supports the page-76 target corridor but does not solve the selector gap.",
            "",
            "## Next Best Move",
            "",
            "- Stop expanding raw numeric selectors unless a new clue names an index unit. Look for an explicit source/layout rule that tells how p73/p79/p80 provenance should pick page-76 words or letters.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
