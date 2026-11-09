#!/usr/bin/env python3
"""Control-test the C9 OVER slot signal against grey/black highlights.

The previous C9 slot pass found that the active black targets B4/G5 span
`OV` + `ER`, yielding `OVER` in x-order. This bounded control checks whether
the same OVER slot-span appears in non-active grey/black highlights inside the
same C9 lower-page frame.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
C9_SLOT_JSON = ROOT / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.json"
GREY_CROPS_JSON = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
GREY_READING_JSON = ROOT / "analysis_outputs/highlight_audit/highres_manual_grey_reading.json"
CROP_COMPLETION_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
OUT = ROOT / "analysis_outputs/source_audit/c9_grey_black_over_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_grey_black_over_slot_control.json"
OUT_MD = OUT / "c9_grey_black_over_slot_control.md"
SHEET = OUT / "c9_grey_black_over_slot_control_sheet.jpg"

MIN_SLOT_OVERLAP_PX = 4.0
STRICT_INSTRUCTION_TERMS = [
    "take",
    "read",
    "word",
    "letter",
    "line",
    "first",
    "last",
    "key",
    "seed",
    "private",
    "mirror",
    "fold",
]
LAYOUT_TERMS = ["OVER", "DOSE", "OVERDOSE"]


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


def compact(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text).upper()


def term_hits(stream: str, terms: list[str]) -> list[str]:
    cstream = compact(stream)
    return [term for term in terms if compact(term) in cstream]


def overlap(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def center_slot(box: list[float], slots: list[dict[str, Any]]) -> dict[str, Any]:
    cx = (box[0] + box[2]) / 2
    for slot in slots:
        if slot["left"] <= cx < slot["right"] or slot["index"] == len(slots) - 1 and cx <= slot["right"]:
            return {**slot, "centerX": cx}
    return {**slots[-1], "centerX": cx}


def span_slots(box: list[float], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for slot in slots:
        span = max(0.0, min(box[2], slot["right"]) - max(box[0], slot["left"]))
        if span >= MIN_SLOT_OVERLAP_PX:
            out.append({**slot, "overlapPx": round(span, 2)})
    return out


def annotate(row: dict[str, Any], slots: list[dict[str, Any]], c9_frame: list[float]) -> dict[str, Any]:
    box = [float(v) for v in row["box"]]
    cslot = center_slot(box, slots)
    spans = span_slots(box, slots)
    ov = overlap(box, c9_frame)
    return {
        **row,
        "box": box,
        "centerX": round(cslot["centerX"], 2),
        "centerSlotLetter": cslot["letter"],
        "centerSlotIndex": cslot["index"],
        "spanSlotLetters": "".join(slot["letter"] for slot in spans),
        "spanSlotIndexes": [slot["index"] for slot in spans],
        "spanSlotOverlapsPx": [slot["overlapPx"] for slot in spans],
        "overlapAreaWithC9": round(ov, 2),
        "overlapVsBox": round(ov / area(box), 6) if area(box) else 0,
        "singleRowLayoutHits": term_hits("".join(slot["letter"] for slot in spans), LAYOUT_TERMS),
        "strictInstructionHitsInText": term_hits(row.get("expected", ""), STRICT_INSTRUCTION_TERMS),
    }


def build_rows() -> dict[str, Any]:
    slot_data = load_json(C9_SLOT_JSON)
    grey_crops = load_json(GREY_CROPS_JSON)
    grey_reading = load_json(GREY_READING_JSON)
    crop_completion = load_json(CROP_COMPLETION_JSON)

    c9_frame = [float(v) for v in slot_data["c9Frame"]]
    slots = [
        {
            "index": int(slot["index"]),
            "letter": slot["letter"],
            "left": float(slot["left"]),
            "right": float(slot["right"]),
        }
        for slot in slot_data["slots"]
    ]
    active_boxes = {row["id"]: row for row in crop_completion["targets"]}

    rows = []
    for raw in grey_crops["rows"]:
        row = {
            "id": raw["id"],
            "page": raw["page"],
            "expected": raw["expected"],
            "box": raw["highresBox"],
            "source": "manual_grey_highres_crops.highresBox",
            "isActiveCorrectedBlack": False,
        }
        if raw["id"] == "p76_grey_4":
            row["box"] = active_boxes["one_billion"]["box"]
            row["expected"] = "$1 billion"
            row["source"] = "page76_active_target_crop_completion.one_billion"
            row["isActiveCorrectedBlack"] = True
        elif raw["id"] == "p76_grey_5":
            row["box"] = active_boxes["volcano_bonds"]["box"]
            row["expected"] = "Volcano Bonds"
            row["source"] = "page76_active_target_crop_completion.volcano_bonds"
            row["isActiveCorrectedBlack"] = True
        rows.append(annotate(row, slots, c9_frame))

    c9_rows = [row for row in rows if row["overlapAreaWithC9"] > 0]
    by_page: dict[str, list[dict[str, Any]]] = {}
    for row in c9_rows:
        by_page.setdefault(str(row["page"]), []).append(row)

    pair_rows = []
    for page, page_rows in sorted(by_page.items(), key=lambda item: int(item[0])):
        ordered = sorted(page_rows, key=lambda row: row["centerX"])
        for a, b in zip(ordered, ordered[1:]):
            stream = a["spanSlotLetters"] + b["spanSlotLetters"]
            pair_rows.append(
                {
                    "page": int(page),
                    "pairIds": [a["id"], b["id"]],
                    "pairText": [a["expected"], b["expected"]],
                    "stream": stream,
                    "layoutHits": term_hits(stream, LAYOUT_TERMS),
                    "strictInstructionHitsInTexts": sorted(set(a["strictInstructionHitsInText"] + b["strictInstructionHitsInText"])),
                    "containsActiveCorrectedBlack": bool(a["isActiveCorrectedBlack"] or b["isActiveCorrectedBlack"]),
                    "bothActiveCorrectedBlack": bool(a["isActiveCorrectedBlack"] and b["isActiveCorrectedBlack"]),
                }
            )

    single_over_rows = [row for row in c9_rows if "OVER" in row["singleRowLayoutHits"]]
    pair_over_rows = [row for row in pair_rows if "OVER" in row["layoutHits"]]
    active_pair_over = [row for row in pair_over_rows if row["bothActiveCorrectedBlack"]]
    control_single_over = [row for row in single_over_rows if not row["isActiveCorrectedBlack"]]

    return {
        "c9Frame": c9_frame,
        "slots": slot_data["slots"],
        "greyBlackRows": rows,
        "c9GreyBlackRows": c9_rows,
        "adjacentPairRows": pair_rows,
        "summary": {
            "totalGreyBlackRows": len(rows),
            "c9GreyBlackRowCount": len(c9_rows),
            "singleRowOverCount": len(single_over_rows),
            "controlSingleRowOverCount": len(control_single_over),
            "singleRowOverIds": [row["id"] for row in single_over_rows],
            "pairOverCount": len(pair_over_rows),
            "activeCorrectedPairOverCount": len(active_pair_over),
            "pairOverIds": [row["pairIds"] for row in pair_over_rows],
            "activeCorrectedPairOverStream": active_pair_over[0]["stream"] if active_pair_over else None,
            "activeCorrectedPairOverSource": active_pair_over[0]["pairIds"] if active_pair_over else [],
            "controlSingleOverTexts": [row["expected"] for row in control_single_over],
            "strictInstructionHitCount": sum(len(row["strictInstructionHitsInText"]) for row in c9_rows)
            + sum(len(row["strictInstructionHitsInTexts"]) for row in pair_rows),
            "selectorUnlocked": False,
        },
        "sourceText": {
            "greyReadingSource": grey_reading.get("source"),
            "greyReadingCaveats": grey_reading.get("caveats"),
            "greyReadingCorrections": grey_reading.get("correctionsVersusSuppliedTranscript"),
        },
    }


def draw_sheet(result: dict[str, Any]) -> None:
    margin = 28
    row_h = 52
    header_h = 128
    sheet_w = 1420
    sheet_h = header_h + row_h * (len(result["c9GreyBlackRows"]) + len(result["adjacentPairRows"]) + 5)
    img = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(img)
    title = font(26)
    normal = font(15)
    small = font(12)
    mono = font(13)

    draw.text((margin, 18), "C9 Grey/Black OVER Slot Control", fill=(240, 244, 248), font=title)
    draw.text((margin, 56), "Controls B4/G5's OVER span against grey/black rows that overlap the same C9 frame.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 82), "Green marks active corrected black boxes; yellow marks control layout hits.", fill=(178, 188, 199), font=small)

    y = header_h
    draw.text((margin, y), "C9 grey/black rows", fill=(240, 244, 248), font=normal)
    y += 30
    cols = [margin, 112, 190, 520, 660, 770, 900, 1040]
    headers = ["page", "id", "text", "source", "span", "center", "OVER?", "overlap"]
    for x, h in zip(cols, headers):
        draw.text((x, y), h, fill=(178, 188, 199), font=small)
    y += 22
    for row in sorted(result["c9GreyBlackRows"], key=lambda item: (item["page"], item["centerX"])):
        bg = (18, 27, 24) if row["isActiveCorrectedBlack"] else (16, 21, 29)
        draw.rectangle([margin - 6, y - 6, sheet_w - margin, y + row_h - 12], fill=bg)
        draw.text((cols[0], y), str(row["page"]), fill="#c6d1df", font=mono)
        draw.text((cols[1], y), row["id"], fill="#e8eef5", font=mono)
        draw.text((cols[2], y), row["expected"][:36], fill="#e8eef5", font=normal)
        draw.text((cols[3], y), row["source"].split(".")[-1][:14], fill="#c6d1df", font=mono)
        draw.text((cols[4], y), row["spanSlotLetters"], fill="#ffd166", font=mono)
        draw.text((cols[5], y), row["centerSlotLetter"], fill="#72f1b8", font=mono)
        draw.text((cols[6], y), "yes" if "OVER" in row["singleRowLayoutHits"] else "no", fill="#ffd166" if "OVER" in row["singleRowLayoutHits"] else "#c6d1df", font=mono)
        draw.text((cols[7], y), str(row["overlapVsBox"]), fill="#c6d1df", font=mono)
        y += row_h

    y += 10
    draw.text((margin, y), "Adjacent x-order pair streams", fill=(240, 244, 248), font=normal)
    y += 30
    for pair in result["adjacentPairRows"]:
        color = "#ffd166" if "OVER" in pair["layoutHits"] else "#c6d1df"
        active = " active" if pair["bothActiveCorrectedBlack"] else ""
        text = f"p{pair['page']} {'+'.join(pair['pairIds'])}: {pair['stream']} {','.join(pair['layoutHits']) or '-'}{active}"
        draw.text((margin, y), text, fill=color, font=mono)
        y += 24

    y += 8
    draw.text((margin, y), "Decision: the active B4/G5 OVER pair is controlled by p75_grey_3, which spans OVER as a non-active single grey row.", fill="#ffcf7a", font=normal)
    img.save(SHEET, quality=94)


def main() -> None:
    rows = build_rows()
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 grey/black OVER slot control; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "c9OverdoseLetterSlotGate": rel(C9_SLOT_JSON),
            "manualGreyHighresCrops": rel(GREY_CROPS_JSON),
            "manualGreyReading": rel(GREY_READING_JSON),
            "activeCropCompletion": rel(CROP_COMPLETION_JSON),
        },
        **rows,
        "assessment": [
            "The active corrected black B4/G5 pair does produce OVER as `OV` + `ER` in x-order.",
            "A non-active p75 grey row, `Don't fall for shitcoinery`, spans OVER as a single C9 slot row in the same lower-frame geometry.",
            "The OVER slot signal is therefore not unique to the active black pair under the current C9/equal-slot rule.",
            "No grey/black row or adjacent pair supplies strict unit/order wording.",
        ],
        "decision": {
            "c9GreyBlackOverSlotControl": "active_over_controlled_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Keep B4/G5 OVER as a source-comparison curiosity only. Reopen only if a source clue explicitly names grey/black OVER slots or supplies an 8-column reading rule.",
        },
        "sheet": rel(SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Grey/Black OVER Slot Control",
        "",
        "Scope: control-test the `OVER` span from the active black B4/G5 boxes against grey/black rows that overlap the same C9 lower-page frame. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## C9 Grey/Black Rows",
        "",
        "| page | id | text | source | center | span | single OVER? | active corrected? |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in sorted(result["c9GreyBlackRows"], key=lambda item: (item["page"], item["centerX"])):
        lines.append(
            f"| `{row['page']}` | `{row['id']}` | `{row['expected']}` | `{row['source']}` | `{row['centerSlotLetter']}` | `{row['spanSlotLetters']}` | `{'OVER' in row['singleRowLayoutHits']}` | `{row['isActiveCorrectedBlack']}` |"
        )

    lines.extend(["", "## Adjacent Pair Streams", "", "| page | pair | stream | layout hits | active corrected pair? |", "|---|---|---|---|---|"])
    for pair in result["adjacentPairRows"]:
        lines.append(
            f"| `{pair['page']}` | `{' + '.join(pair['pairIds'])}` | `{pair['stream']}` | `{','.join(pair['layoutHits']) or '-'}` | `{pair['bothActiveCorrectedBlack']}` |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- C9 grey/black rows: `{result['summary']['c9GreyBlackRowCount']}`.",
            f"- Single-row OVER hits: `{result['summary']['singleRowOverCount']}`.",
            f"- Control single-row OVER hits: `{result['summary']['controlSingleRowOverCount']}`.",
            f"- Pair OVER hits: `{result['summary']['pairOverCount']}`.",
            f"- Active corrected pair OVER hits: `{result['summary']['activeCorrectedPairOverCount']}`.",
            f"- Strict instruction hits: `{result['summary']['strictInstructionHitCount']}`.",
            "",
            "## Decision",
            "",
            "- Do not promote B4/G5's `OVER` slot stream as extraction permission.",
            "- The same C9 lower-frame slot rule gives a non-active p75 grey control row an `OVER` span by itself.",
            "- Reopen only if a new source/clue explicitly names grey/black OVER slots or supplies an 8-column reading rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
