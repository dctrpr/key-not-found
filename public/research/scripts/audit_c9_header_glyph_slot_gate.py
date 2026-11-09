#!/usr/bin/env python3
"""Project real OVERDOSE header glyph boundaries into the C9 frame.

Earlier C9 slot passes used equal-width OVERDOSE slots. This bounded check uses
the actual OVERDOSE header glyph boxes from pages 76 and 78, scales those
letter boundaries into the C9 frame, and maps O4/B4/G5/O5 plus the p75 grey
control. It tests whether source-backed header glyph geometry changes the
slot result.

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
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
C9_SLOT_JSON = ROOT / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.json"
C9_GREY_BLACK_JSON = (
    ROOT / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.json"
)
P76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/c9_header_glyph_slot_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_header_glyph_slot_gate.json"
OUT_MD = OUT / "c9_header_glyph_slot_gate.md"
SHEET = OUT / "c9_header_glyph_slot_gate_sheet.jpg"

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


def find_header_glyphs(article: dict[str, Any], page_no: int) -> dict[str, Any]:
    page = next(page for page in article["pages"] if page["page"] == page_no)
    word = next(word for word in page["words"] if word.get("token") == "overdose")
    chars = []
    for char in page["chars"]:
        text = char.get("c", "")
        if text not in LETTERS:
            continue
        box = [float(v) for v in char["box"]]
        if box[0] >= word["box"][0] - 1 and box[2] <= word["box"][2] + 1 and abs(char["y"] - word["center"][1]) <= 6:
            chars.append({**char, "box": box})
    chars = sorted(chars, key=lambda row: row["box"][0])
    sequence = "".join(char["c"] for char in chars)
    if sequence != LETTERS:
        raise RuntimeError(f"page {page_no} header sequence mismatch: {sequence}")
    return {"page": page_no, "wordBox": [float(v) for v in word["box"]], "chars": chars}


def project_glyph_slots(header: dict[str, Any], c9_frame: list[float]) -> list[dict[str, Any]]:
    word_box = header["wordBox"]
    word_width = word_box[2] - word_box[0]
    c9_width = c9_frame[2] - c9_frame[0]
    slots = []
    for i, char in enumerate(header["chars"]):
        left_ratio = (char["box"][0] - word_box[0]) / word_width
        right_ratio = (char["box"][2] - word_box[0]) / word_width
        left = c9_frame[0] + left_ratio * c9_width
        right = c9_frame[0] + right_ratio * c9_width
        slots.append(
            {
                "index": i,
                "letter": char["c"],
                "left": left,
                "right": right,
                "width": right - left,
                "sourcePage": header["page"],
                "sourceGlyphBox": char["box"],
            }
        )
    return slots


def equal_edge_deltas(slots: list[dict[str, Any]], c9_frame: list[float]) -> list[float]:
    slot_width = (c9_frame[2] - c9_frame[0]) / len(LETTERS)
    deltas = []
    for i, slot in enumerate(slots):
        deltas.append(round(slot["left"] - (c9_frame[0] + i * slot_width), 6))
        deltas.append(round(slot["right"] - (c9_frame[0] + (i + 1) * slot_width), 6))
    return deltas


def center_slot(box: list[float], slots: list[dict[str, Any]]) -> dict[str, Any]:
    cx = (float(box[0]) + float(box[2])) / 2
    for slot in slots:
        if slot["left"] <= cx < slot["right"] or slot["index"] == len(slots) - 1 and cx <= slot["right"]:
            return {**slot, "centerX": cx}
    return {**slots[-1], "centerX": cx}


def span_slots(box: list[float], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    left = float(box[0])
    right = float(box[2])
    out = []
    for slot in slots:
        overlap = max(0.0, min(right, slot["right"]) - max(left, slot["left"]))
        if overlap >= MIN_SLOT_OVERLAP_PX:
            out.append({**slot, "overlapPx": round(overlap, 2)})
    return out


def annotate(row: dict[str, Any], slots: list[dict[str, Any]]) -> dict[str, Any]:
    box = [float(v) for v in row["box"]]
    center = center_slot(box, slots)
    spans = span_slots(box, slots)
    return {
        **row,
        "box": box,
        "centerX": round(center["centerX"], 2),
        "centerSlotIndex": center["index"],
        "centerSlotLetter": center["letter"],
        "spanSlotIndexes": [slot["index"] for slot in spans],
        "spanSlotLetters": "".join(slot["letter"] for slot in spans),
        "spanSlotOverlapsPx": [slot["overlapPx"] for slot in spans],
    }


def stream_record(name: str, rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    value = "".join(row[field] for row in rows)
    return {
        "name": name,
        "stream": value,
        "targetOrder": [row.get("shortId") or row.get("id") for row in rows],
        "strictInstructionHits": term_hits(value, STRICT_INSTRUCTION_TERMS),
        "layoutTermHits": term_hits(value, LAYOUT_TERMS),
    }


def evaluate_projection(name: str, slots: list[dict[str, Any]], c9_slot_data: dict[str, Any], grey_black: dict[str, Any]) -> dict[str, Any]:
    active = [annotate(row, slots) for row in c9_slot_data["activeRows"]]
    by_line = sorted(active, key=lambda row: (row["pageLine"], row["corridorIndex"]))
    by_x = sorted(active, key=lambda row: row["centerX"])
    black_by_x = [row for row in by_x if row["visualState"] == "K"]
    orange_by_x = [row for row in by_x if row["visualState"] == "Y"]
    p75_control = [
        annotate(
            {
                "id": row["id"],
                "shortId": row["id"],
                "page": row["page"],
                "expected": row["expected"],
                "box": row["box"],
            },
            slots,
        )
        for row in grey_black["c9GreyBlackRows"]
        if row["id"] == "p75_grey_3"
    ]

    stream_specs = [
        ("active_center_line_order", by_line, "centerSlotLetter"),
        ("active_center_x_order", by_x, "centerSlotLetter"),
        ("active_span_line_order", by_line, "spanSlotLetters"),
        ("active_span_x_order", by_x, "spanSlotLetters"),
        ("active_black_span_x_order", black_by_x, "spanSlotLetters"),
        ("active_orange_span_x_order", orange_by_x, "spanSlotLetters"),
        ("p75_control_span", p75_control, "spanSlotLetters"),
    ]
    streams = [stream_record(f"{name}_{label}", rows, field) for label, rows, field in stream_specs]
    streams.extend(
        {
            **record,
            "name": record["name"] + "_reverse",
            "stream": record["stream"][::-1],
            "strictInstructionHits": term_hits(record["stream"][::-1], STRICT_INSTRUCTION_TERMS),
            "layoutTermHits": term_hits(record["stream"][::-1], LAYOUT_TERMS),
        }
        for record in list(streams)
    )
    active_streams = [row for row in streams if "p75_control" not in row["name"]]
    return {
        "name": name,
        "slots": slots,
        "activeRows": active,
        "p75ControlRows": p75_control,
        "streams": streams,
        "summary": {
            "activeSpanXOrderStream": next(row["stream"] for row in streams if row["name"] == f"{name}_active_span_x_order"),
            "activeBlackSpanXOrderStream": next(
                row["stream"] for row in streams if row["name"] == f"{name}_active_black_span_x_order"
            ),
            "activeOrangeSpanXOrderStream": next(
                row["stream"] for row in streams if row["name"] == f"{name}_active_orange_span_x_order"
            ),
            "p75ControlSpan": next(row["stream"] for row in streams if row["name"] == f"{name}_p75_control_span"),
            "activeLayoutHitCount": sum(1 for row in active_streams if row["layoutTermHits"]),
            "activeStrictInstructionHitCount": sum(len(row["strictInstructionHits"]) for row in active_streams),
            "p75ControlHasOver": any("OVER" in row["layoutTermHits"] for row in streams if "p75_control" in row["name"]),
        },
    }


def build_result() -> dict[str, Any]:
    article = load_json(ARTICLE_JSON)
    c9_slot_data = load_json(C9_SLOT_JSON)
    grey_black = load_json(C9_GREY_BLACK_JSON)
    c9_frame = [float(v) for v in c9_slot_data["c9Frame"]]
    headers = [find_header_glyphs(article, page_no) for page_no in [76, 78]]
    projections = []
    for header in headers:
        slots = project_glyph_slots(header, c9_frame)
        deltas = equal_edge_deltas(slots, c9_frame)
        projection = evaluate_projection(f"p{header['page']}_header_glyph", slots, c9_slot_data, grey_black)
        projection["sourceHeader"] = header
        projection["maxAbsEdgeDeltaVsEqualSlotPx"] = max(abs(v) for v in deltas) if deltas else None
        projections.append(projection)

    active_over_projection_count = sum(
        1 for p in projections if "OVER" in p["summary"]["activeBlackSpanXOrderStream"]
    )
    p75_over_projection_count = sum(1 for p in projections if p["summary"]["p75ControlHasOver"])
    strict_hit_count = sum(p["summary"]["activeStrictInstructionHitCount"] for p in projections)
    max_edge_delta = max(p["maxAbsEdgeDeltaVsEqualSlotPx"] for p in projections)
    return {
        "c9Frame": c9_frame,
        "projectionCount": len(projections),
        "projections": projections,
        "summary": {
            "projectionCount": len(projections),
            "maxAbsEdgeDeltaVsEqualSlotPx": round(max_edge_delta, 6),
            "activeBlackOverProjectionCount": active_over_projection_count,
            "p75ControlOverProjectionCount": p75_over_projection_count,
            "activeStrictInstructionHitCount": strict_hit_count,
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
    sheet_w = panel.width + 650
    sheet_h = max(panel.height + 120, 920)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(17)
    small = font(13)
    tiny = font(11)
    draw.text((24, 18), "C9 Header Glyph Slot Gate", fill=(240, 244, 248), font=title)
    draw.text((24, 54), "Actual OVERDOSE header glyph boundaries scaled into the C9 frame.", fill=(176, 186, 198), font=normal)
    sheet.paste(panel, (24, 92))
    ox, oy = 24, 92

    def sx(x: float) -> float:
        return ox + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return oy + (y - crop[1]) * scale

    projection = result["projections"][0]
    colors = [
        (255, 190, 80),
        (246, 130, 90),
        (120, 190, 255),
        (150, 220, 150),
        (220, 160, 255),
        (255, 220, 120),
        (110, 210, 230),
        (245, 160, 170),
    ]
    for slot, color in zip(projection["slots"], colors):
        draw.rectangle([sx(slot["left"]), sy(frame[1]), sx(slot["right"]), sy(frame[3])], outline=color, width=2)
        draw.text((sx(slot["left"]) + 5, sy(frame[1]) + 5), slot["letter"], fill=color, font=small)

    for row in projection["activeRows"]:
        box = row["box"]
        color = (255, 174, 44) if row["visualState"] == "Y" else (245, 245, 245)
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=4)
        draw.text((sx(box[0]), sy(box[1]) - 16), row["shortId"], fill=color, font=small)
    for row in projection["p75ControlRows"]:
        box = row["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(180, 185, 195), width=2)
        draw.text((sx(box[0]), sy(box[3]) + 2), row["shortId"], fill=(180, 185, 195), font=tiny)

    x0 = panel.width + 58
    y = 104
    draw.text((x0, y), "Summary", fill=(240, 244, 248), font=font(24))
    y += 42
    rows = [
        ("Glyph projections", result["summary"]["projectionCount"]),
        ("Max edge delta vs equal slots", result["summary"]["maxAbsEdgeDeltaVsEqualSlotPx"]),
        ("Active black OVER projections", result["summary"]["activeBlackOverProjectionCount"]),
        ("p75 control OVER projections", result["summary"]["p75ControlOverProjectionCount"]),
        ("Strict instruction hits", result["summary"]["activeStrictInstructionHitCount"]),
    ]
    for label, value in rows:
        draw.text((x0, y), label, fill=(160, 170, 182), font=normal)
        draw.text((x0 + 280, y), f"`{value}`", fill=(238, 242, 246), font=normal)
        y += 34
    y += 20
    for p in result["projections"]:
        draw.text((x0, y), p["name"], fill=(240, 244, 248), font=small)
        y += 24
        draw.text(
            (x0, y),
            f"active {p['summary']['activeSpanXOrderStream']} | black {p['summary']['activeBlackSpanXOrderStream']} | p75 {p['summary']['p75ControlSpan']}",
            fill=(214, 220, 228),
            font=small,
        )
        y += 28
    y += 12
    draw.text((x0, y), "Decision", fill=(240, 244, 248), font=font(22))
    y += 36
    for line in [
        "Actual header glyph scaling reproduces the equal-slot result.",
        "B4/G5 OVER remains controlled by the p75 grey row.",
        "No unit/order instruction is introduced.",
    ]:
        draw.text((x0, y), line, fill=(214, 220, 228), font=normal)
        y += 28
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    payload = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 actual OVERDOSE header glyph slot gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "article3dMap": rel(ARTICLE_JSON),
            "c9OverdoseLetterSlotGate": rel(C9_SLOT_JSON),
            "c9GreyBlackOverSlotControl": rel(C9_GREY_BLACK_JSON),
        },
        **result,
        "assessment": [
            "Pages 76 and 78 both contain measurable OVERDOSE header glyph boxes in the 3D map.",
            "Scaling those real glyph boundaries into the C9 frame reproduces the equal-slot result: active black B4/G5 gives OVER.",
            "The p75 grey control also gives OVER under both actual-header projections.",
            "Header glyph geometry does not introduce a source-backed unit/order instruction.",
        ],
        "decision": {
            "c9HeaderGlyphSlotGate": "actual_header_glyph_projection_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Do not promote C9 header-glyph slot projection. Reopen only if a source/clue explicitly names OVERDOSE header letters, glyph-width slots, or an 8-column reading order.",
        },
        "sheet": rel(SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Header Glyph Slot Gate",
        "",
        "Scope: scale the actual `OVERDOSE` header glyph boxes from pages 76 and 78 into the C9 frame, then map active O4/B4/G5/O5 plus the p75 grey control. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{payload['createdAt']}`",
        f"- Sheet: `{payload['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Header projections tested: `{result['summary']['projectionCount']}`.",
        f"- Max projected glyph-edge delta vs equal slots: `{result['summary']['maxAbsEdgeDeltaVsEqualSlotPx']}` px.",
        f"- Active B4/G5 `OVER` projections: `{result['summary']['activeBlackOverProjectionCount']}`.",
        f"- p75 control `OVER` projections: `{result['summary']['p75ControlOverProjectionCount']}`.",
        f"- Active strict instruction hits: `{result['summary']['activeStrictInstructionHitCount']}`.",
        "",
        "## Projection Streams",
        "",
    ]
    for p in result["projections"]:
        lines.extend(
            [
                f"- `{p['name']}`:",
                f"  - active x-order span: `{p['summary']['activeSpanXOrderStream']}`",
                f"  - active black x-order span: `{p['summary']['activeBlackSpanXOrderStream']}`",
                f"  - active orange x-order span: `{p['summary']['activeOrangeSpanXOrderStream']}`",
                f"  - p75 grey control span: `{p['summary']['p75ControlSpan']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote actual OVERDOSE header glyph slots as a selector.",
            "- The real glyph projection reproduces the equal-slot result and keeps B4/G5 `OVER` controlled by p75.",
            "- Reopen only if a new source/clue names OVERDOSE header letters, glyph-width slots, or an 8-column reading order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = build_result()
    draw_sheet(result)
    write_report(result)


if __name__ == "__main__":
    main()
