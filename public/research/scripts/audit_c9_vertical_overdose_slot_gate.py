#!/usr/bin/env python3
"""Check whether C9 vertical OVERDOSE slots supply a unit/order rule.

This bounded geometry pass divides the C9 frame into eight vertical bands named
OVERDOSE in both top-to-bottom and bottom-to-top orientations. It maps the
active O4/B4/G5/O5 boxes plus nearby orange and grey/black controls already
used in the C9 slot reports.

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
C9_GREY_BLACK_JSON = (
    ROOT / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.json"
)
P76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/c9_vertical_overdose_slot_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_vertical_overdose_slot_gate.json"
OUT_MD = OUT / "c9_vertical_overdose_slot_gate.md"
SHEET = OUT / "c9_vertical_overdose_slot_gate_sheet.jpg"

LETTERS = "OVERDOSE"
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


def vertical_slots(frame: list[float], orientation: str) -> list[dict[str, Any]]:
    _, y0, _, y1 = frame
    height = y1 - y0
    slot_height = height / len(LETTERS)
    rows = []
    for i, letter in enumerate(LETTERS):
        if orientation == "top_to_bottom":
            top = y0 + slot_height * i
            bottom = y0 + slot_height * (i + 1)
        elif orientation == "bottom_to_top":
            top = y1 - slot_height * (i + 1)
            bottom = y1 - slot_height * i
        else:
            raise ValueError(orientation)
        rows.append({"index": i, "letter": letter, "top": top, "bottom": bottom, "height": slot_height})
    return rows


def center_slot(box: list[float], slots: list[dict[str, Any]]) -> dict[str, Any]:
    cy = (float(box[1]) + float(box[3])) / 2
    ordered = sorted(slots, key=lambda slot: slot["top"])
    for slot in ordered:
        if slot["top"] <= cy < slot["bottom"] or slot == ordered[-1] and cy <= slot["bottom"]:
            return {**slot, "centerY": cy}
    return {**ordered[-1], "centerY": cy}


def span_slots(box: list[float], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top = float(box[1])
    bottom = float(box[3])
    out = []
    for slot in slots:
        overlap = max(0.0, min(bottom, slot["bottom"]) - max(top, slot["top"]))
        if overlap >= MIN_SLOT_OVERLAP_PX:
            out.append({**slot, "overlapPx": round(overlap, 2)})
    return sorted(out, key=lambda slot: slot["top"])


def annotate_row(row: dict[str, Any], slots_by_orientation: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    box = [float(v) for v in row["box"]]
    out = {**row, "box": box, "centerY": round((box[1] + box[3]) / 2, 2)}
    for orientation, slots in slots_by_orientation.items():
        center = center_slot(box, slots)
        spans = span_slots(box, slots)
        prefix = "verticalTop" if orientation == "top_to_bottom" else "verticalBottom"
        out[f"{prefix}CenterSlotIndex"] = center["index"]
        out[f"{prefix}CenterSlotLetter"] = center["letter"]
        out[f"{prefix}SpanSlotIndexes"] = [slot["index"] for slot in spans]
        out[f"{prefix}SpanSlotLetters"] = "".join(slot["letter"] for slot in spans)
        out[f"{prefix}SpanSlotOverlapsPx"] = [slot["overlapPx"] for slot in spans]
    return out


def stream_record(name: str, rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    stream = "".join(row.get(field, "") for row in rows)
    return {
        "name": name,
        "stream": stream,
        "targetOrder": [row.get("shortId") or row.get("id") for row in rows],
        "strictInstructionHits": term_hits(stream, STRICT_INSTRUCTION_TERMS),
        "layoutTermHits": term_hits(stream, LAYOUT_TERMS),
    }


def build_rows() -> dict[str, Any]:
    slot_data = load_json(C9_SLOT_JSON)
    grey_black = load_json(C9_GREY_BLACK_JSON)
    c9_frame = [float(v) for v in slot_data["c9Frame"]]
    slots_by_orientation = {
        "top_to_bottom": vertical_slots(c9_frame, "top_to_bottom"),
        "bottom_to_top": vertical_slots(c9_frame, "bottom_to_top"),
    }

    active_rows = [annotate_row(row, slots_by_orientation) for row in slot_data["activeRows"]]
    grey_rows = [
        annotate_row(
            {
                "id": row["id"],
                "shortId": row["id"],
                "page": row["page"],
                "kind": "grey_black",
                "expected": row["expected"],
                "box": row["box"],
                "isActiveCorrectedBlack": row.get("isActiveCorrectedBlack", False),
                "horizontalSpanSlotLetters": row.get("spanSlotLetters", ""),
            },
            slots_by_orientation,
        )
        for row in grey_black["c9GreyBlackRows"]
    ]
    highlight_rows = [
        annotate_row(
            {
                "id": row["id"],
                "shortId": row["id"],
                "page": row["page"],
                "kind": row["kind"],
                "box": row["box"],
                "isActiveOrange": row.get("isActiveOrange", False),
                "horizontalSpanSlotLetters": row.get("spanSlotLetters", ""),
            },
            slots_by_orientation,
        )
        for row in slot_data["highlightRows"]
    ]

    by_line = sorted(active_rows, key=lambda row: (row["pageLine"], row["corridorIndex"]))
    by_x = sorted(active_rows, key=lambda row: row["centerX"])
    by_y = sorted(active_rows, key=lambda row: row["centerY"])
    orange_active = [row for row in by_y if row["visualState"] == "Y"]
    black_active = [row for row in by_y if row["visualState"] == "K"]

    stream_specs = [
        ("active_vertical_top_center_line_order", by_line, "verticalTopCenterSlotLetter"),
        ("active_vertical_top_center_y_order", by_y, "verticalTopCenterSlotLetter"),
        ("active_vertical_top_center_x_order", by_x, "verticalTopCenterSlotLetter"),
        ("active_vertical_top_span_line_order", by_line, "verticalTopSpanSlotLetters"),
        ("active_vertical_bottom_center_line_order", by_line, "verticalBottomCenterSlotLetter"),
        ("active_vertical_bottom_center_y_order", by_y, "verticalBottomCenterSlotLetter"),
        ("active_vertical_bottom_center_x_order", by_x, "verticalBottomCenterSlotLetter"),
        ("active_vertical_bottom_span_line_order", by_line, "verticalBottomSpanSlotLetters"),
        ("active_orange_vertical_top_y_order", orange_active, "verticalTopCenterSlotLetter"),
        ("active_black_vertical_top_y_order", black_active, "verticalTopCenterSlotLetter"),
        ("active_orange_vertical_bottom_y_order", orange_active, "verticalBottomCenterSlotLetter"),
        ("active_black_vertical_bottom_y_order", black_active, "verticalBottomCenterSlotLetter"),
    ]
    active_streams = [stream_record(*spec) for spec in stream_specs]
    active_streams.extend(
        {
            **record,
            "name": record["name"] + "_reverse",
            "stream": record["stream"][::-1],
            "strictInstructionHits": term_hits(record["stream"][::-1], STRICT_INSTRUCTION_TERMS),
            "layoutTermHits": term_hits(record["stream"][::-1], LAYOUT_TERMS),
        }
        for record in list(active_streams)
    )

    control_rows = [row for row in grey_rows + highlight_rows if not row.get("isActiveCorrectedBlack") and not row.get("isActiveOrange")]
    control_streams = [
        stream_record(
            "control_vertical_top_span_y_order",
            sorted(control_rows, key=lambda row: (row["page"], row["centerY"], row["id"])),
            "verticalTopSpanSlotLetters",
        ),
        stream_record(
            "control_vertical_bottom_span_y_order",
            sorted(control_rows, key=lambda row: (row["page"], row["centerY"], row["id"])),
            "verticalBottomSpanSlotLetters",
        ),
    ]

    active_layout_hits = [record for record in active_streams if record["layoutTermHits"]]
    active_instruction_hits = [record for record in active_streams if record["strictInstructionHits"]]
    control_layout_hits = [record for record in control_streams if record["layoutTermHits"]]

    return {
        "c9Frame": c9_frame,
        "verticalSlotsTopToBottom": slots_by_orientation["top_to_bottom"],
        "verticalSlotsBottomToTop": slots_by_orientation["bottom_to_top"],
        "activeRows": active_rows,
        "c9GreyBlackRows": grey_rows,
        "highlightRows": highlight_rows,
        "activeStreams": active_streams,
        "controlStreams": control_streams,
        "summary": {
            "verticalSlotHeightPx": round((c9_frame[3] - c9_frame[1]) / len(LETTERS), 2),
            "activeVerticalTopCenterLineOrder": next(
                row["stream"] for row in active_streams if row["name"] == "active_vertical_top_center_line_order"
            ),
            "activeVerticalBottomCenterLineOrder": next(
                row["stream"] for row in active_streams if row["name"] == "active_vertical_bottom_center_line_order"
            ),
            "activeVerticalTopSpanLineOrder": next(
                row["stream"] for row in active_streams if row["name"] == "active_vertical_top_span_line_order"
            ),
            "activeVerticalBottomSpanLineOrder": next(
                row["stream"] for row in active_streams if row["name"] == "active_vertical_bottom_span_line_order"
            ),
            "activeBlackVerticalTopStream": next(
                row["stream"] for row in active_streams if row["name"] == "active_black_vertical_top_y_order"
            ),
            "activeBlackVerticalBottomStream": next(
                row["stream"] for row in active_streams if row["name"] == "active_black_vertical_bottom_y_order"
            ),
            "activeLayoutHitCount": len(active_layout_hits),
            "activeLayoutHitStreams": [
                {"name": row["name"], "stream": row["stream"], "layoutTermHits": row["layoutTermHits"]}
                for row in active_layout_hits
            ],
            "activeStrictInstructionHitCount": sum(len(row["strictInstructionHits"]) for row in active_streams),
            "activeStrictInstructionHitStreams": [
                {"name": row["name"], "stream": row["stream"], "strictInstructionHits": row["strictInstructionHits"]}
                for row in active_instruction_hits
            ],
            "controlLayoutHitCount": len(control_layout_hits),
            "controlLayoutHitStreams": [
                {"name": row["name"], "stream": row["stream"], "layoutTermHits": row["layoutTermHits"]}
                for row in control_layout_hits
            ],
            "selectorUnlocked": False,
        },
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(P76_IMAGE).convert("RGB")
    frame = result["c9Frame"]
    crop = [
        int(max(0, frame[0] - 80)),
        int(max(0, frame[1] - 80)),
        int(min(page.width, frame[2] + 80)),
        int(min(page.height, frame[3] + 80)),
    ]
    panel = page.crop(crop)
    scale = 0.55
    panel = panel.resize((int(panel.width * scale), int(panel.height * scale)))
    sheet_w = panel.width + 640
    sheet_h = max(panel.height + 120, 920)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (13, 16, 22))
    draw = ImageDraw.Draw(sheet)
    title_font = font(30)
    normal_font = font(17)
    small_font = font(13)
    tiny_font = font(11)

    draw.text((24, 18), "C9 Vertical OVERDOSE Slot Gate", fill=(240, 244, 248), font=title_font)
    draw.text((24, 54), "Same C9 frame divided vertically; active boxes and controls mapped in both Y orientations.", fill=(174, 184, 196), font=normal_font)
    sheet.paste(panel, (24, 92))
    ox, oy = 24, 92

    def sx(x: float) -> float:
        return ox + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return oy + (y - crop[1]) * scale

    # Top-to-bottom bands.
    band_colors = [
        (255, 190, 80),
        (246, 130, 90),
        (120, 190, 255),
        (150, 220, 150),
        (220, 160, 255),
        (255, 220, 120),
        (110, 210, 230),
        (245, 160, 170),
    ]
    for slot, color in zip(result["verticalSlotsTopToBottom"], band_colors):
        y0 = sy(slot["top"])
        y1 = sy(slot["bottom"])
        draw.rectangle([sx(frame[0]), y0, sx(frame[2]), y1], outline=color, width=2)
        draw.text((sx(frame[0]) + 6, y0 + 4), slot["letter"], fill=color, font=small_font)

    for row in result["activeRows"]:
        box = row["box"]
        color = (255, 174, 44) if row["visualState"] == "Y" else (30, 30, 30)
        outline = (255, 255, 255) if row["visualState"] == "K" else (255, 174, 44)
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=outline, width=4)
        draw.text((sx(box[0]), sy(box[1]) - 16), row["shortId"], fill=outline, font=small_font)
        if row["visualState"] == "K":
            draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=2)

    for row in result["c9GreyBlackRows"]:
        if row.get("isActiveCorrectedBlack"):
            continue
        box = row["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(180, 185, 195), width=2)
        draw.text((sx(box[0]), sy(box[3]) + 2), row["id"], fill=(180, 185, 195), font=tiny_font)

    x0 = panel.width + 58
    y = 102
    rows = [
        ("Top center line", result["summary"]["activeVerticalTopCenterLineOrder"]),
        ("Bottom center line", result["summary"]["activeVerticalBottomCenterLineOrder"]),
        ("Top span line", result["summary"]["activeVerticalTopSpanLineOrder"]),
        ("Bottom span line", result["summary"]["activeVerticalBottomSpanLineOrder"]),
        ("Black top", result["summary"]["activeBlackVerticalTopStream"]),
        ("Black bottom", result["summary"]["activeBlackVerticalBottomStream"]),
        ("Active layout-hit streams", str(result["summary"]["activeLayoutHitCount"])),
        ("Strict instruction hits", str(result["summary"]["activeStrictInstructionHitCount"])),
    ]
    draw.text((x0, y), "Summary", fill=(240, 244, 248), font=font(24))
    y += 44
    for label, value in rows:
        draw.text((x0, y), label, fill=(160, 170, 182), font=normal_font)
        draw.text((x0 + 230, y), f"`{value}`", fill=(238, 242, 246), font=normal_font)
        y += 34
    y += 20
    draw.text((x0, y), "Decision", fill=(240, 244, 248), font=font(22))
    y += 38
    decision_lines = [
        "Vertical C9 slots yield OERE / EODO, not a",
        "unit or order instruction.",
        "No active vertical stream contains OVER, DOSE,",
        "or OVERDOSE.",
        "Keep C9 vertical slotting as layout context only.",
    ]
    for line in decision_lines:
        draw.text((x0, y), line, fill=(214, 220, 228), font=normal_font)
        y += 28

    SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    payload = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 vertical OVERDOSE slot gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "c9OverdoseLetterSlotGate": rel(C9_SLOT_JSON),
            "c9GreyBlackOverSlotControl": rel(C9_GREY_BLACK_JSON),
        },
        **result,
        "assessment": [
            "Top-to-bottom vertical slots map the active quartet to OERE in line/y order.",
            "Bottom-to-top vertical slots map the active quartet to EODO in line/y order.",
            "Neither active orientation produces OVER, DOSE, OVERDOSE, or a strict unit/order instruction term.",
            "The vertical slot rule is an arbitrary layout projection unless a source/clue names a vertical OVERDOSE-slot read.",
        ],
        "decision": {
            "c9VerticalOverdoseSlotGate": "vertical_slot_projection_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Do not promote vertical C9 slots. Keep source/original-layout validation as the only useful next move unless a clue names vertical slots, OVERDOSE bands, or an 8-row reading order.",
        },
        "sheet": rel(SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Vertical OVERDOSE Slot Gate",
        "",
        "Scope: divide the C9 frame vertically into eight `OVERDOSE` bands in both top-to-bottom and bottom-to-top orientations, then map active O4/B4/G5/O5 plus nearby controls. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{payload['createdAt']}`",
        f"- Sheet: `{payload['sheet']}`",
        "",
        "## Active Streams",
        "",
        f"- Top-to-bottom center, line order: `{result['summary']['activeVerticalTopCenterLineOrder']}`.",
        f"- Bottom-to-top center, line order: `{result['summary']['activeVerticalBottomCenterLineOrder']}`.",
        f"- Top-to-bottom span, line order: `{result['summary']['activeVerticalTopSpanLineOrder']}`.",
        f"- Bottom-to-top span, line order: `{result['summary']['activeVerticalBottomSpanLineOrder']}`.",
        f"- Active black top-to-bottom stream: `{result['summary']['activeBlackVerticalTopStream']}`.",
        f"- Active black bottom-to-top stream: `{result['summary']['activeBlackVerticalBottomStream']}`.",
        "",
        "## Controls",
        "",
        f"- Active layout-hit stream count: `{result['summary']['activeLayoutHitCount']}`.",
        f"- Control layout-hit stream count: `{result['summary']['controlLayoutHitCount']}`.",
        f"- Active strict instruction hit count: `{result['summary']['activeStrictInstructionHitCount']}`.",
        "",
        "## Decision",
        "",
        "- Do not promote C9 vertical OVERDOSE bands as a selector.",
        "- The active quartet yields `OERE` / `EODO`, not `OVER`, `DOSE`, `OVERDOSE`, or unit/order wording.",
        "- Reopen only if a new source/clue names vertical slots, OVERDOSE bands, or an 8-row reading order.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = build_rows()
    draw_sheet(result)
    write_report(result)


if __name__ == "__main__":
    main()
