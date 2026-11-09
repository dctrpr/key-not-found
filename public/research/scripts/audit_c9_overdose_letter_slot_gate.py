#!/usr/bin/env python3
"""Check whether the C9 OVERDOSE frame supplies an 8-letter slot rule.

This bounded geometry pass divides the C9 frame into eight horizontal slots
named by OVERDOSE and maps only the active O4/B4/G5/O5 target boxes plus the
same-slot orange-highlight controls. It checks whether the slot streams supply
an independent unit/order instruction.

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
C9_PAGE_CONTROL_JSON = ROOT / "analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json"
C9_HIGHLIGHT_CONTROL_JSON = ROOT / "analysis_outputs/source_audit/c9_highlight_edge_contact_control/c9_highlight_edge_contact_control.json"
CROP_COMPLETION_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
FORMAT_LOCK_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
MARKDOWN_TXT = ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md"
ANNOTATED_TXT = ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt"
CORRECTION_MD = ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.md"

OUT = ROOT / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_overdose_letter_slot_gate.json"
OUT_MD = OUT / "c9_overdose_letter_slot_gate.md"
SHEET = OUT / "c9_overdose_letter_slot_gate_sheet.jpg"

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


def slot_ranges(frame: list[float]) -> list[dict[str, Any]]:
    x0, _, x1, _ = frame
    width = x1 - x0
    slot_width = width / len(LETTERS)
    rows = []
    for i, letter in enumerate(LETTERS):
        left = x0 + slot_width * i
        right = x0 + slot_width * (i + 1)
        rows.append({"index": i, "letter": letter, "left": left, "right": right, "width": slot_width})
    return rows


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


def annotate_box(row: dict[str, Any], slots: list[dict[str, Any]]) -> dict[str, Any]:
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


def stream(rows: list[dict[str, Any]], field: str) -> str:
    return "".join(row[field] for row in rows)


def make_stream_record(name: str, rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    value = stream(rows, field)
    return {
        "name": name,
        "stream": value,
        "targetOrder": [row.get("shortId") or row.get("id") for row in rows],
        "strictInstructionHits": term_hits(value, STRICT_INSTRUCTION_TERMS),
        "layoutTermHits": term_hits(value, LAYOUT_TERMS),
    }


def make_rows() -> dict[str, Any]:
    c9_page = load_json(C9_PAGE_CONTROL_JSON)
    c9_highlights = load_json(C9_HIGHLIGHT_CONTROL_JSON)
    crop_completion = load_json(CROP_COMPLETION_JSON)
    format_lock = load_json(FORMAT_LOCK_JSON)

    c9_frame = [float(v) for v in c9_page["c9Frame"]]
    slots = slot_ranges(c9_frame)
    format_by_id = {row["id"]: row for row in format_lock["activeTargets"]}
    active = []
    for row in crop_completion["targets"]:
        fmt = format_by_id.get(row["id"], {})
        active.append(
            annotate_box(
                {
                    "id": row["id"],
                    "shortId": row["label"].split()[0],
                    "phrase": row["phrase"],
                    "box": row["box"],
                    "visualState": row["visualState"],
                    "pageLine": row["pageLine"],
                    "corridorIndex": row["corridorIndex"],
                    "docmBoldFraction": fmt.get("docmBoldFraction"),
                    "docmHighlightSummary": fmt.get("docmHighlightSummary"),
                },
                slots,
            )
        )

    by_line = sorted(active, key=lambda row: (row["pageLine"], row["corridorIndex"]))
    by_x = sorted(active, key=lambda row: row["centerX"])
    orange_active = [row for row in by_x if row["visualState"] == "Y"]
    black_active = [row for row in by_x if row["visualState"] == "K"]

    highlight_rows = []
    for row in c9_highlights["highlightRows"]:
        hrow = annotate_box(
            {
                "page": row["page"],
                "id": row["id"],
                "kind": row["kind"],
                "box": row["box"],
                "shortId": row["id"],
            },
            slots,
        )
        hrow["isActiveOrange"] = bool(row.get("isP76ActiveOrange"))
        highlight_rows.append(hrow)

    control_highlights = [row for row in highlight_rows if not row["isActiveOrange"]]
    control_by_page = {}
    for row in control_highlights:
        control_by_page.setdefault(str(row["page"]), []).append(row)
    control_streams = []
    for page, rows in sorted(control_by_page.items(), key=lambda item: int(item[0])):
        rows_by_x = sorted(rows, key=lambda row: row["centerX"])
        control_streams.append(make_stream_record(f"p{page}_control_orange_span_x_order", rows_by_x, "spanSlotLetters"))

    active_streams = [
        make_stream_record("active_center_line_order", by_line, "centerSlotLetter"),
        make_stream_record("active_center_x_order", by_x, "centerSlotLetter"),
        make_stream_record("active_span_line_order", by_line, "spanSlotLetters"),
        make_stream_record("active_span_x_order", by_x, "spanSlotLetters"),
        make_stream_record("active_orange_only_span_x_order", orange_active, "spanSlotLetters"),
        make_stream_record("active_black_only_span_x_order", black_active, "spanSlotLetters"),
    ]
    for record in list(active_streams):
        active_streams.append(
            {
                **record,
                "name": record["name"] + "_reverse",
                "stream": record["stream"][::-1],
                "targetOrder": list(reversed(record["targetOrder"])),
                "strictInstructionHits": term_hits(record["stream"][::-1], STRICT_INSTRUCTION_TERMS),
                "layoutTermHits": term_hits(record["stream"][::-1], LAYOUT_TERMS),
            }
        )

    active_span_x = next(row for row in active_streams if row["name"] == "active_span_x_order")
    black_span_x = next(row for row in active_streams if row["name"] == "active_black_only_span_x_order")
    orange_span_x = next(row for row in active_streams if row["name"] == "active_orange_only_span_x_order")

    return {
        "c9Frame": c9_frame,
        "slots": [
            {
                "index": row["index"],
                "letter": row["letter"],
                "left": round(row["left"], 2),
                "right": round(row["right"], 2),
                "width": round(row["width"], 2),
            }
            for row in slots
        ],
        "activeRows": active,
        "activeStreams": active_streams,
        "highlightRows": highlight_rows,
        "controlStreams": control_streams,
        "summary": {
            "slotCount": len(slots),
            "slotWidthPx": round(slots[0]["width"], 2),
            "activeCenterLineOrderStream": next(row for row in active_streams if row["name"] == "active_center_line_order")["stream"],
            "activeCenterXOrderStream": next(row for row in active_streams if row["name"] == "active_center_x_order")["stream"],
            "activeSpanLineOrderStream": next(row for row in active_streams if row["name"] == "active_span_line_order")["stream"],
            "activeSpanXOrderStream": active_span_x["stream"],
            "activeBlackOnlySpanXOrderStream": black_span_x["stream"],
            "activeOrangeOnlySpanXOrderStream": orange_span_x["stream"],
            "activeSpanXOrderLayoutTermHits": active_span_x["layoutTermHits"],
            "activeStrictInstructionHitCount": sum(len(row["strictInstructionHits"]) for row in active_streams),
            "controlOrangeStreamCount": len(control_streams),
            "controlOrangeLayoutHitStreams": [
                row for row in control_streams if row["layoutTermHits"]
            ],
            "overPrefixRequiresBlackTargets": active_span_x["stream"].startswith("OVER")
            and not orange_span_x["stream"].startswith("OVER"),
            "selectorUnlocked": False,
        },
    }


def draw_sheet(result: dict[str, Any]) -> None:
    margin = 28
    row_h = 48
    header_h = 138
    sheet_w = 1420
    sheet_h = header_h + row_h * (len(result["activeRows"]) + len(result["controlStreams"]) + 7)
    img = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(img)
    title = font(26)
    normal = font(15)
    small = font(12)
    mono = font(13)

    draw.text((margin, 20), "C9 OVERDOSE Letter-Slot Gate", fill=(240, 244, 248), font=title)
    draw.text((margin, 58), "Eight equal horizontal C9 slots named OVERDOSE; target boxes and same-slot controls are mapped to center/span letters.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 84), f"Frame {result['c9Frame']} | slot width {result['summary']['slotWidthPx']} px | min overlap {MIN_SLOT_OVERLAP_PX} px", fill=(178, 188, 199), font=small)

    x0 = margin
    y = 112
    slot_w = 104
    for slot in result["slots"]:
        left = x0 + slot["index"] * slot_w
        fill = (24, 33, 45) if slot["index"] % 2 == 0 else (18, 25, 36)
        draw.rectangle([left, y, left + slot_w - 4, y + 28], fill=fill)
        draw.text((left + 42, y + 6), slot["letter"], fill=(255, 219, 137), font=normal)

    y = header_h
    draw.text((margin, y), "Active target slot rows", fill=(240, 244, 248), font=normal)
    y += 28
    headers = ["target", "phrase", "color", "line", "center", "span", "box"]
    cols = [margin, 110, 350, 430, 500, 610, 745]
    for x, h in zip(cols, headers):
        draw.text((x, y), h, fill=(178, 188, 199), font=small)
    y += 22
    for row in sorted(result["activeRows"], key=lambda item: (item["pageLine"], item["corridorIndex"])):
        bg = (16, 21, 29)
        draw.rectangle([margin - 6, y - 6, sheet_w - margin, y + row_h - 12], fill=bg)
        color = "#ff9b2e" if row["visualState"] == "Y" else "#aab4c2"
        draw.text((cols[0], y), row["shortId"], fill=color, font=normal)
        draw.text((cols[1], y), row["phrase"][:28], fill="#e8eef5", font=normal)
        draw.text((cols[2], y), row["visualState"], fill=color, font=mono)
        draw.text((cols[3], y), str(row["pageLine"]), fill="#c6d1df", font=mono)
        draw.text((cols[4], y), row["centerSlotLetter"], fill="#72f1b8", font=mono)
        draw.text((cols[5], y), row["spanSlotLetters"], fill="#ffd166", font=mono)
        draw.text((cols[6], y), str([round(v, 1) for v in row["box"]]), fill="#c6d1df", font=mono)
        y += row_h

    y += 12
    draw.text((margin, y), "Streams", fill=(240, 244, 248), font=normal)
    y += 30
    for record in result["activeStreams"][:6]:
        marker = " layout:" + ",".join(record["layoutTermHits"]) if record["layoutTermHits"] else ""
        draw.text((margin, y), f"{record['name']}: {record['stream']}{marker}", fill="#ffd166", font=mono)
        y += 24

    y += 8
    draw.text((margin, y), "Control orange span streams", fill=(240, 244, 248), font=normal)
    y += 30
    for record in result["controlStreams"]:
        marker = " layout:" + ",".join(record["layoutTermHits"]) if record["layoutTermHits"] else ""
        draw.text((margin, y), f"{record['name']}: {record['stream']}{marker}", fill="#c6d1df", font=mono)
        y += 24

    y += 10
    draw.text((margin, y), "Decision: slot mapping supplies layout coincidences only; it has zero strict instruction hits and no source-backed unit/order.", fill="#ffcf7a", font=normal)
    img.save(SHEET, quality=94)


def main() -> None:
    rows = make_rows()
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 OVERDOSE 8-letter slot geometry gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "c9FramePageControl": rel(C9_PAGE_CONTROL_JSON),
            "c9HighlightEdgeContactControl": rel(C9_HIGHLIGHT_CONTROL_JSON),
            "activeCropCompletion": rel(CROP_COMPLETION_JSON),
            "formatAuthorityLock": rel(FORMAT_LOCK_JSON),
            "userMarkdownTranscript": rel(MARKDOWN_TXT),
            "userAnnotatedTranscript": rel(ANNOTATED_TXT),
            "plainArticleCorrectionReport": rel(CORRECTION_MD),
        },
        **rows,
        "assessment": [
            "Equal 8-slot C9 mapping gives active center streams OVED and VEDO, not an instruction or target order.",
            "The active x-order span stream starts OVERRDODOS and contains a superficial OVER prefix, but that depends on adding the manually completed black B4/G5 boxes to the orange O4/O5 boxes.",
            "Orange-only active controls do not produce OVER, and same-slot control highlights on pages 75/79 produce comparable partial slot fragments without selector wording.",
            "No stream contains a strict unit/order instruction such as take/read/word/letter/line, and the slot rule is not source-backed.",
        ],
        "decision": {
            "c9OverdoseLetterSlotGate": "layout_coincidence_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Keep OVERDOSE letter slots as a visual/source-comparison note only. Reopen only if a source clue explicitly names OVERDOSE letters, slots, or an 8-column reading order.",
        },
        "sheet": rel(SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 OVERDOSE Letter-Slot Gate",
        "",
        "Scope: divide the C9 frame into eight equal horizontal slots named `OVERDOSE`, then map O4/B4/G5/O5 boxes and same-slot orange-highlight controls to center/span slot letters. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Slot width: `{result['summary']['slotWidthPx']} px`.",
        "",
        "## Active Rows",
        "",
        "| target | phrase | color | line | center slot | span slots |",
        "|---|---|---|---|---|---|",
    ]
    for row in sorted(result["activeRows"], key=lambda item: (item["pageLine"], item["corridorIndex"])):
        lines.append(
            f"| `{row['shortId']}` | `{row['phrase']}` | `{row['visualState']}` | `{row['pageLine']}` | `{row['centerSlotLetter']}` | `{row['spanSlotLetters']}` |"
        )

    lines.extend(
        [
            "",
            "## Streams",
            "",
            "| stream | value | layout hits | strict instruction hits |",
            "|---|---|---|---|",
        ]
    )
    for record in result["activeStreams"]:
        lines.append(
            f"| `{record['name']}` | `{record['stream']}` | `{','.join(record['layoutTermHits']) or '-'}` | `{','.join(record['strictInstructionHits']) or '-'}` |"
        )

    lines.extend(["", "## Control Orange Streams", "", "| stream | value | layout hits |", "|---|---|---|"])
    for record in result["controlStreams"]:
        lines.append(
            f"| `{record['name']}` | `{record['stream']}` | `{','.join(record['layoutTermHits']) or '-'}` |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Active center line-order stream: `{result['summary']['activeCenterLineOrderStream']}`.",
            f"- Active center x-order stream: `{result['summary']['activeCenterXOrderStream']}`.",
            f"- Active span line-order stream: `{result['summary']['activeSpanLineOrderStream']}`.",
            f"- Active span x-order stream: `{result['summary']['activeSpanXOrderStream']}`.",
            f"- Active black-only span x-order stream: `{result['summary']['activeBlackOnlySpanXOrderStream']}`.",
            f"- Active orange-only span x-order stream: `{result['summary']['activeOrangeOnlySpanXOrderStream']}`.",
            f"- Active strict instruction hits: `{result['summary']['activeStrictInstructionHitCount']}`.",
            f"- OVER prefix requires black targets: `{result['summary']['overPrefixRequiresBlackTargets']}`.",
            "",
            "## Decision",
            "",
            "- Do not promote C9 OVERDOSE 8-letter slot mapping as a selector.",
            "- The only interesting string, `OVERRDODOS`, is a layout artifact of x-order span bins and depends on the completed black B4/G5 boxes.",
            "- Reopen only if a new source/clue explicitly names OVERDOSE letters, slots, or an 8-column reading order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
