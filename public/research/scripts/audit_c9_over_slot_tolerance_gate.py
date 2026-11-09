#!/usr/bin/env python3
"""Bounded tolerance test for C9 OVER slot mechanics.

This checks whether the B4/G5 `OVER` span is robust under small horizontal
slot-grid shifts and overlap thresholds. It also tracks the p75 grey control
row that independently spans `OVER` in the same C9 lower-frame geometry.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SLOT_GATE_JSON = ROOT / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.json"
OVER_CONTROL_JSON = ROOT / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.json"
OUT = ROOT / "analysis_outputs/source_audit/c9_over_slot_tolerance_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_over_slot_tolerance_gate.json"
OUT_MD = OUT / "c9_over_slot_tolerance_gate.md"
SHEET = OUT / "c9_over_slot_tolerance_gate_sheet.jpg"

LETTERS = "OVERDOSE"
GRID_SHIFTS_PX = [-80, -60, -40, -20, -10, 0, 10, 20, 40, 60, 80]
OVERLAP_THRESHOLDS_PX = [1, 4, 25, 50, 75, 100, 120, 150, 200]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def shifted_slots(frame: list[float], shift: float) -> list[dict[str, Any]]:
    x0, _, x1, _ = frame
    width = x1 - x0
    slot_width = width / len(LETTERS)
    return [
        {
            "index": i,
            "letter": letter,
            "left": x0 + shift + slot_width * i,
            "right": x0 + shift + slot_width * (i + 1),
        }
        for i, letter in enumerate(LETTERS)
    ]


def span_letters(box: list[float], slots: list[dict[str, Any]], threshold: float) -> str:
    left = float(box[0])
    right = float(box[2])
    letters = []
    for slot in slots:
        overlap = max(0.0, min(right, slot["right"]) - max(left, slot["left"]))
        if overlap >= threshold:
            letters.append(slot["letter"])
    return "".join(letters)


def get_box(rows: list[dict[str, Any]], row_id: str) -> list[float]:
    for row in rows:
        if row["id"] == row_id:
            return [float(v) for v in row["box"]]
    raise KeyError(row_id)


def build_results() -> dict[str, Any]:
    slot_gate = load_json(SLOT_GATE_JSON)
    over_control = load_json(OVER_CONTROL_JSON)
    frame = [float(v) for v in slot_gate["c9Frame"]]
    active_rows = slot_gate["activeRows"]
    grey_rows = over_control["c9GreyBlackRows"]

    b4 = get_box(active_rows, "one_billion")
    g5 = get_box(active_rows, "volcano_bonds")
    o4 = get_box(active_rows, "buying_dip")
    o5 = get_box(active_rows, "shitcoiner_heart")
    p75_control = get_box(grey_rows, "p75_grey_3")

    rows = []
    for threshold in OVERLAP_THRESHOLDS_PX:
        for shift in GRID_SHIFTS_PX:
            slots = shifted_slots(frame, shift)
            b4_span = span_letters(b4, slots, threshold)
            g5_span = span_letters(g5, slots, threshold)
            o4_span = span_letters(o4, slots, threshold)
            o5_span = span_letters(o5, slots, threshold)
            p75_span = span_letters(p75_control, slots, threshold)
            active_black_pair = b4_span + g5_span
            active_all_x = b4_span + g5_span + o5_span + o4_span
            rows.append(
                {
                    "shiftPx": shift,
                    "thresholdPx": threshold,
                    "b4Span": b4_span,
                    "g5Span": g5_span,
                    "o5Span": o5_span,
                    "o4Span": o4_span,
                    "activeBlackPairStream": active_black_pair,
                    "activeAllXStream": active_all_x,
                    "p75GreyControlSpan": p75_span,
                    "activeBlackPairHasOver": "OVER" in active_black_pair,
                    "activeAllXHasOver": "OVER" in active_all_x,
                    "p75GreyControlHasOver": "OVER" in p75_span,
                }
            )

    canonical = next(row for row in rows if row["shiftPx"] == 0 and row["thresholdPx"] == 4)
    active_over_rows = [row for row in rows if row["activeBlackPairHasOver"]]
    control_over_rows = [row for row in rows if row["p75GreyControlHasOver"]]
    both_over_rows = [row for row in rows if row["activeBlackPairHasOver"] and row["p75GreyControlHasOver"]]

    by_threshold = []
    for threshold in OVERLAP_THRESHOLDS_PX:
        subset = [row for row in rows if row["thresholdPx"] == threshold]
        by_threshold.append(
            {
                "thresholdPx": threshold,
                "activeBlackPairOverShiftCount": sum(1 for row in subset if row["activeBlackPairHasOver"]),
                "p75ControlOverShiftCount": sum(1 for row in subset if row["p75GreyControlHasOver"]),
                "bothOverShiftCount": sum(1 for row in subset if row["activeBlackPairHasOver"] and row["p75GreyControlHasOver"]),
                "shiftCount": len(subset),
            }
        )

    return {
        "c9Frame": frame,
        "gridShiftsPx": GRID_SHIFTS_PX,
        "overlapThresholdsPx": OVERLAP_THRESHOLDS_PX,
        "canonical": canonical,
        "toleranceRows": rows,
        "byThreshold": by_threshold,
        "summary": {
            "totalCombinations": len(rows),
            "activeBlackPairOverCount": len(active_over_rows),
            "p75ControlOverCount": len(control_over_rows),
            "bothOverCount": len(both_over_rows),
            "canonicalActiveBlackPairStream": canonical["activeBlackPairStream"],
            "canonicalP75GreyControlSpan": canonical["p75GreyControlSpan"],
            "activeOverFailsAtThresholds": [
                item["thresholdPx"]
                for item in by_threshold
                if item["activeBlackPairOverShiftCount"] == 0
            ],
            "controlOverPersistsAtCanonical": canonical["p75GreyControlHasOver"],
            "selectorUnlocked": False,
        },
    }


def draw_sheet(result: dict[str, Any]) -> None:
    margin = 28
    row_h = 28
    header_h = 124
    sheet_w = 1200
    sheet_h = header_h + row_h * (len(result["byThreshold"]) + 6)
    img = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(img)
    title = font(26)
    normal = font(15)
    small = font(12)
    mono = font(13)

    draw.text((margin, 18), "C9 OVER Slot Tolerance Gate", fill=(240, 244, 248), font=title)
    draw.text((margin, 56), "B4/G5 OVER and p75 grey control OVER across fixed grid shifts and overlap thresholds.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 82), f"Shifts: {GRID_SHIFTS_PX}; thresholds: {OVERLAP_THRESHOLDS_PX}", fill=(178, 188, 199), font=small)

    y = header_h
    cols = [margin, 170, 380, 590, 790]
    headers = ["threshold", "active OVER shifts", "p75 control OVER shifts", "both", "decision"]
    for x, h in zip(cols, headers):
        draw.text((x, y), h, fill=(178, 188, 199), font=small)
    y += 24
    for row in result["byThreshold"]:
        active = row["activeBlackPairOverShiftCount"]
        control = row["p75ControlOverShiftCount"]
        both = row["bothOverShiftCount"]
        fill = (16, 21, 29)
        draw.rectangle([margin - 6, y - 5, sheet_w - margin, y + row_h - 7], fill=fill)
        draw.text((cols[0], y), str(row["thresholdPx"]), fill="#c6d1df", font=mono)
        draw.text((cols[1], y), f"{active}/{row['shiftCount']}", fill="#ffd166" if active else "#ff8fa3", font=mono)
        draw.text((cols[2], y), f"{control}/{row['shiftCount']}", fill="#ffd166" if control else "#c6d1df", font=mono)
        draw.text((cols[3], y), f"{both}/{row['shiftCount']}", fill="#ffd166" if both else "#c6d1df", font=mono)
        decision = "controlled" if both else ("active fragile" if active else "inactive")
        draw.text((cols[4], y), decision, fill="#e8eef5", font=mono)
        y += row_h

    y += 18
    notes = [
        f"Canonical active pair: {result['summary']['canonicalActiveBlackPairStream']}; p75 control: {result['summary']['canonicalP75GreyControlSpan']}.",
        f"Active OVER combinations: {result['summary']['activeBlackPairOverCount']}/{result['summary']['totalCombinations']}.",
        f"Control OVER combinations: {result['summary']['p75ControlOverCount']}/{result['summary']['totalCombinations']}.",
        "Decision: OVER is neither source-backed nor uniquely active; do not extract.",
    ]
    for note in notes:
        draw.text((margin, y), note, fill="#ffcf7a", font=normal)
        y += 24
    img.save(SHEET, quality=94)


def main() -> None:
    data = build_results()
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 OVER slot tolerance gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "c9OverdoseLetterSlotGate": rel(SLOT_GATE_JSON),
            "c9GreyBlackOverSlotControl": rel(OVER_CONTROL_JSON),
        },
        **data,
        "assessment": [
            "Canonical zero-shift, 4 px threshold reproduces B4/G5 OVER and p75 grey control OVER.",
            "The active B4/G5 OVER depends on low overlap thresholds; at threshold 120 px and above it disappears across all tested shifts.",
            "The p75 grey control preserves OVER at the canonical setting and overlaps the same lower C9 frame, so the result is not uniquely active.",
            "No source-backed unit/order instruction is introduced by varying slot tolerance.",
        ],
        "decision": {
            "c9OverSlotToleranceGate": "fragile_and_controlled_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Do not tune C9 OVER slot thresholds. Keep source/original-layout validation as the only useful next move unless a clue names OVERDOSE slots or an 8-column reading order.",
        },
        "sheet": rel(SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 OVER Slot Tolerance Gate",
        "",
        "Scope: test whether the B4/G5 `OVER` span is stable under fixed small horizontal C9 slot-grid shifts and overlap thresholds, while tracking the p75 grey control row. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Canonical",
        "",
        f"- Active black pair stream: `{result['canonical']['activeBlackPairStream']}`.",
        f"- p75 grey control span: `{result['canonical']['p75GreyControlSpan']}`.",
        f"- Active pair has OVER: `{result['canonical']['activeBlackPairHasOver']}`.",
        f"- p75 control has OVER: `{result['canonical']['p75GreyControlHasOver']}`.",
        "",
        "## Threshold Summary",
        "",
        "| threshold px | active OVER shifts | p75 control OVER shifts | both OVER shifts | tested shifts |",
        "|---|---|---|---|---|",
    ]
    for row in result["byThreshold"]:
        lines.append(
            f"| `{row['thresholdPx']}` | `{row['activeBlackPairOverShiftCount']}` | `{row['p75ControlOverShiftCount']}` | `{row['bothOverShiftCount']}` | `{row['shiftCount']}` |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Total combinations: `{result['summary']['totalCombinations']}`.",
            f"- Active B4/G5 OVER combinations: `{result['summary']['activeBlackPairOverCount']}`.",
            f"- p75 control OVER combinations: `{result['summary']['p75ControlOverCount']}`.",
            f"- Both OVER combinations: `{result['summary']['bothOverCount']}`.",
            f"- Active OVER fails completely at thresholds: `{result['summary']['activeOverFailsAtThresholds']}`.",
            "",
            "## Decision",
            "",
            "- Do not tune C9 OVER slot thresholds into an extraction rule.",
            "- The active `OVER` is tolerance-sensitive and controlled by p75 at the canonical setting.",
            "- Reopen only if a new source/clue names OVERDOSE slots or an 8-column reading order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
