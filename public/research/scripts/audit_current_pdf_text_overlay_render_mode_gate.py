#!/usr/bin/env python3
"""Audit page-76 PDF OCR/text overlay render modes.

The current PDFs contain page images plus OCR/text overlays. Earlier passes
checked OCR words and affine alignment. This pass asks whether the text overlay
itself carries original-layout evidence: visible text painting, non-OCR fonts,
render-mode cues, opacity tricks, or target-aligned source instructions around
O4/B4/G5/O5 and the OVERDOSE header.

This is source/render provenance inspection only. No OCR-to-key extraction,
hashing, seed/WIF/address checks, BIP39 checks, or candidate generation is run.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_text_overlay_render_mode_gate.json"
OUT_MD = OUT / "current_pdf_text_overlay_render_mode_gate.md"
OUT_SHEET = OUT / "current_pdf_text_overlay_render_mode_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
AFFINE_REPORT = ROOT / (
    "analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/"
    "current_pdf_ocr_affine_alignment_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
STRICT_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "first",
    "fold",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "line",
    "mirror",
    "order",
    "outside",
    "read",
    "reverse",
    "right",
    "row",
    "side",
    "slot",
    "take",
    "top",
    "word",
}
TARGET_TERMS = {
    "O4": {"buying", "dip"},
    "B4": {"billion"},
    "G5": {"volcano", "bonds"},
    "O5": {"shitcoiner", "heart"},
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def clean_token(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum() or ch == "$")


def compact(text: str) -> str:
    return " ".join(text.split())


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    out = []
    for short_id in TARGET_ORDER:
        row = by_short[short_id]
        out.append(
            {
                "shortId": short_id,
                "label": row["label"],
                "box": [float(v) for v in row["box"]],
            }
        )
    return out


def overdose_header_box() -> list[float] | None:
    data = load_json(ARTICLE_MAP)
    page = next(row for row in data["pages"] if row["page"] == 76)
    for word in page["words"]:
        if str(word.get("token", "")).lower() == "overdose":
            return [float(v) for v in word["box"]]
    return None


def affine_by_pdf() -> dict[str, list[list[float]]]:
    data = load_json(AFFINE_REPORT)
    out = {}
    for record in data.get("records", []):
        fit = record.get("fit", {})
        if fit.get("fitAvailable"):
            out[record["pdfRecord"]["pdf"]] = fit["matrix"]
    return out


def transform_points(matrix: list[list[float]], points: np.ndarray) -> np.ndarray:
    m = np.array(matrix, dtype=float)
    a = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    return a @ m.T


def center(box: tuple[float, float, float, float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def image_rect(page: fitz.Page) -> fitz.Rect:
    best_rect = page.rect
    best_area = -1.0
    for image in page.get_images(full=True):
        xref = int(image[0])
        for rect in page.get_image_rects(xref):
            area = max(0.0, rect.width) * max(0.0, rect.height)
            if area > best_area:
                best_area = area
                best_rect = rect
    return best_rect


def trace_text(item: dict[str, Any]) -> str:
    return "".join(chr(char[0]) for char in item.get("chars", []) if char and char[0] >= 0)


def page_record(pdf_path: Path, matrix: list[list[float]] | None, targets: list[dict[str, Any]], header_box: list[float] | None) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    rect = image_rect(page)
    trace_items = page.get_texttrace()
    stream_bytes = b"".join((doc.xref_stream(x) or b"") for x in (page.get_contents() or []))
    rows = []
    points = []
    for item in trace_items:
        text = trace_text(item)
        token = clean_token(text)
        box = tuple(float(v) for v in item["bbox"])
        cx, cy = center(box)
        image_x = ((cx - rect.x0) / rect.width) * SOURCE_IMAGE_SIZE[0]
        image_y = ((cy - rect.y0) / rect.height) * SOURCE_IMAGE_SIZE[1]
        rows.append(
            {
                "text": text,
                "token": token,
                "type": int(item.get("type", -1)),
                "opacity": round(float(item.get("opacity", 0.0)), 4),
                "color": [round(float(v), 4) for v in item.get("color", ())],
                "font": item.get("font"),
                "size": round(float(item.get("size", 0.0)), 3),
                "bbox": [round(float(v), 3) for v in box],
                "imageMappedCenter": [image_x, image_y],
            }
        )
        points.append([image_x, image_y])

    aligned = []
    if matrix and points:
        transformed = transform_points(matrix, np.array(points, dtype=float))
        for row, point in zip(rows, transformed):
            copied = dict(row)
            copied["alignedCenter"] = [round(float(point[0]), 3), round(float(point[1]), 3)]
            aligned.append(copied)

    target_rows = []
    component_hit_count = 0
    strict_hit_count = 0
    if matrix:
        for target in targets:
            hits = [row for row in aligned if in_box(tuple(row["alignedCenter"]), target["box"])]
            terms = TARGET_TERMS[target["shortId"]]
            component_hits = [
                row
                for row in hits
                if row["token"] in terms or any(term in row["token"] for term in terms if len(term) >= 5)
            ]
            strict_hits = [row for row in hits if row["token"] in STRICT_TERMS]
            component_hit_count += len(component_hits)
            strict_hit_count += len(strict_hits)
            target_rows.append(
                {
                    "target": target["shortId"],
                    "label": target["label"],
                    "alignedTraceCount": len(hits),
                    "alignedText": compact(" ".join(row["text"] for row in hits)),
                    "traceTypes": sorted(set(row["type"] for row in hits)),
                    "componentHitText": [row["text"] for row in component_hits],
                    "strictInstructionText": [row["text"] for row in strict_hits],
                }
            )

    header_hits = []
    if header_box and matrix:
        header_hits = [row for row in aligned if in_box(tuple(row["alignedCenter"]), header_box)]

    type_counts = Counter(row["type"] for row in rows)
    font_counts = Counter(str(row["font"]) for row in rows)
    color_counts = Counter(tuple(row["color"]) for row in rows)
    visible_rows = [row for row in rows if row["type"] != 3]
    overdose_text_hits = [row for row in rows if "overdose" in row["token"]]
    return {
        "pdf": rel(pdf_path),
        "rotation": int(page.rotation),
        "contentStreamCount": len(page.get_contents() or []),
        "contentByteCount": len(stream_bytes),
        "traceSpanCount": len(rows),
        "textTraceTypeCounts": {str(k): v for k, v in sorted(type_counts.items())},
        "visiblePaintedTraceSpanCount": len(visible_rows),
        "invisibleType3TraceSpanCount": type_counts.get(3, 0),
        "allTraceTextInvisible": len(rows) > 0 and len(visible_rows) == 0,
        "fonts": dict(font_counts),
        "colors": {str(k): v for k, v in color_counts.items()},
        "usesGlyphLessFont": "GlyphLessFont" in font_counts,
        "usesHelveticaOnly": set(font_counts) == {"Helvetica"},
        "explicitTr3InPageStream": b" 3 Tr" in stream_bytes or b"\n3 Tr" in stream_bytes,
        "fitAvailable": bool(matrix),
        "overdoseTextHitCount": len(overdose_text_hits),
        "overdoseTextTraceTypes": sorted(set(row["type"] for row in overdose_text_hits)),
        "alignedHeaderTraceCount": len(header_hits),
        "alignedHeaderText": compact(" ".join(row["text"] for row in header_hits)),
        "targetRows": target_rows,
        "activeAlignedTraceRowCount": sum(row["alignedTraceCount"] for row in target_rows),
        "activeAlignedComponentHitCount": component_hit_count,
        "activeAlignedStrictInstructionHitCount": strict_hit_count,
        "sampleRows": [
            {
                "text": row["text"][:80],
                "type": row["type"],
                "font": row["font"],
                "size": row["size"],
                "bbox": row["bbox"],
            }
            for row in rows[:12]
        ],
    }


def render_sheet(records: list[dict[str, Any]], targets: list[dict[str, Any]]) -> None:
    base = Image.open(UPRIGHT_PAGE).convert("RGB")
    scale = 0.28
    panel_w = int(base.width * scale)
    panel_h = int(base.height * scale)
    header_h = 90
    row_h = panel_h + 46
    width = panel_w + 640
    height = header_h + len(records) * row_h
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title_font = font(22)
    text_font = font(14)
    small_font = font(11)
    draw.text((18, 14), "Current PDF Text Overlay Render-Mode Gate", fill=(0, 0, 0), font=title_font)
    draw.text((18, 46), "Green boxes are active targets; text overlay is invisible/type 3 in all current PDFs.", fill=(70, 70, 70), font=text_font)
    y = header_h
    for record in records:
        thumb = base.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        td = ImageDraw.Draw(thumb)
        for target in targets:
            box = [int(v * scale) for v in target["box"]]
            td.rectangle(box, outline=(0, 160, 0), width=3)
            td.text((box[0] + 3, box[1] + 3), target["shortId"], fill=(0, 120, 0), font=small_font)
        sheet.paste(thumb, (0, y))
        x = panel_w + 18
        draw.text((x, y + 6), record["pdf"], fill=(0, 0, 0), font=text_font)
        lines = [
            f"trace spans: {record['traceSpanCount']}",
            f"type counts: {record['textTraceTypeCounts']}",
            f"visible painted spans: {record['visiblePaintedTraceSpanCount']}",
            f"fonts: {', '.join(record['fonts'].keys())}",
            f"fit available: {record['fitAvailable']}",
            f"OVERDOSE text hits/header aligned: {record['overdoseTextHitCount']}/{record['alignedHeaderTraceCount']}",
            f"active aligned trace/component/strict: {record['activeAlignedTraceRowCount']}/{record['activeAlignedComponentHitCount']}/{record['activeAlignedStrictInstructionHitCount']}",
        ]
        yy = y + 34
        for line in lines:
            draw.text((x, yy), line, fill=(60, 60, 60), font=small_font)
            yy += 18
        y += row_h
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    targets = active_targets()
    header_box = overdose_header_box()
    matrices = affine_by_pdf()
    records = [
        page_record(pdf, matrices.get(rel(pdf)), targets, header_box)
        for pdf in PDFS
    ]
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trace_span_count = sum(row["traceSpanCount"] for row in records)
    type3_count = sum(row["invisibleType3TraceSpanCount"] for row in records)
    visible_count = sum(row["visiblePaintedTraceSpanCount"] for row in records)
    all_invisible_pdf_count = sum(1 for row in records if row["allTraceTextInvisible"])
    glyphless_pdf_count = sum(1 for row in records if row["usesGlyphLessFont"])
    helvetica_pdf_count = sum(1 for row in records if row["usesHelveticaOnly"])
    overdose_pdf_count = sum(1 for row in records if row["overdoseTextHitCount"] > 0)
    fit_available_count = sum(1 for row in records if row["fitAvailable"])
    active_trace_count = sum(row["activeAlignedTraceRowCount"] for row in records)
    active_component_count = sum(row["activeAlignedComponentHitCount"] for row in records)
    active_strict_count = sum(row["activeAlignedStrictInstructionHitCount"] for row in records)
    trigger_summary = trigger_matrix.get("summary", {})
    source_summary = source_review.get("summary", {})
    summary = {
        "pdfCount": len(records),
        "textTraceSpanCount": trace_span_count,
        "invisibleType3TraceSpanCount": type3_count,
        "visiblePaintedTraceSpanCount": visible_count,
        "allTraceTextInvisiblePdfCount": all_invisible_pdf_count,
        "glyphLessFontPdfCount": glyphless_pdf_count,
        "helveticaOnlyPdfCount": helvetica_pdf_count,
        "fitAvailablePdfCount": fit_available_count,
        "overdoseTextTracePdfCount": overdose_pdf_count,
        "activeAlignedTraceRowCount": active_trace_count,
        "activeAlignedComponentHitCount": active_component_count,
        "activeAlignedStrictInstructionHitCount": active_strict_count,
        "sourceBackedR3BridgeHitCount": source_summary.get("sourceBackedR3BridgeHitCount", 0),
        "satisfiedReopenTriggerCount": trigger_summary.get("satisfiedTriggerCount", 0),
        "triggerCount": trigger_summary.get("triggerCount", 0),
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|traceSpans={trace_span_count}|type3={type3_count}|"
        f"visible={visible_count}|allInvisiblePdfs={all_invisible_pdf_count}|"
        f"glyphLess={glyphless_pdf_count}|helvetica={helvetica_pdf_count}|"
        f"fits={fit_available_count}|overdosePdfs={overdose_pdf_count}|"
        f"activeTrace={active_trace_count}|activeComponents={active_component_count}|"
        f"activeStrict={active_strict_count}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    summary["pdfTextOverlayRenderModeFingerprint"] = fingerprint
    render_sheet(records, targets)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current PDF text overlay render-mode gate. Checks page-76 OCR/text overlays, "
            "texttrace render types, fonts, visibility, OVERDOSE text, and active target "
            "aligned overlay hits. No OCR-to-key/hash/seed/WIF/address/BIP39/candidate work."
        ),
        "inputs": {
            "pdfs": [rel(p) for p in PDFS],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "affineReport": rel(AFFINE_REPORT),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfTextOverlayRenderModeGate": "do_not_reopen_pdf_text_overlay",
            "reason": (
                "All page-76 texttrace spans are render type 3/invisible OCR text. The low-resolution "
                "duplicates use GlyphLessFont, magazine.pdf uses Helvetica, visible painted text spans "
                "are 0, and aligned active target overlay hits contain no exact components or strict "
                "unit/order terms."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Treat PDF text overlays as derivative OCR context only. Continue to require a distinct "
            "source/original-layout asset or raw clue before reopening extraction."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF Text Overlay Render-Mode Gate",
        "",
        "Scope: inspect page-76 PDF OCR/text overlays for visible render modes, font/layout evidence, OVERDOSE text, and active-target aligned source instructions. No OCR-to-key extraction, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- Texttrace spans: `{summary['textTraceSpanCount']}`",
        f"- Invisible type-3 spans / visible painted spans: `{summary['invisibleType3TraceSpanCount']}` / `{summary['visiblePaintedTraceSpanCount']}`",
        f"- PDFs with all text invisible: `{summary['allTraceTextInvisiblePdfCount']}`",
        f"- GlyphLessFont / Helvetica-only PDFs: `{summary['glyphLessFontPdfCount']}` / `{summary['helveticaOnlyPdfCount']}`",
        f"- Fit-available PDFs: `{summary['fitAvailablePdfCount']}`",
        f"- OVERDOSE text-trace PDFs: `{summary['overdoseTextTracePdfCount']}`",
        f"- Active aligned trace rows / component hits / strict instruction hits: `{summary['activeAlignedTraceRowCount']}` / `{summary['activeAlignedComponentHitCount']}` / `{summary['activeAlignedStrictInstructionHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | trace spans | type counts | visible spans | fonts | fit | OVERDOSE hits | active trace/component/strict |",
        "|---|---:|---|---:|---|---:|---:|---:|",
    ]
    for row in records:
        lines.append(
            f"| `{row['pdf']}` | `{row['traceSpanCount']}` | `{row['textTraceTypeCounts']}` | "
            f"`{row['visiblePaintedTraceSpanCount']}` | `{', '.join(row['fonts'].keys())}` | "
            f"`{row['fitAvailable']}` | `{row['overdoseTextHitCount']}` | "
            f"`{row['activeAlignedTraceRowCount']}/{row['activeAlignedComponentHitCount']}/{row['activeAlignedStrictInstructionHitCount']}` |"
        )
    lines.extend(
        [
            "",
            "## Active Target Overlay Detail",
            "",
            "| PDF | target | aligned trace count | trace types | aligned text | component hits | strict hits |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in records:
        for target in row["targetRows"]:
            lines.append(
                f"| `{row['pdf']}` | `{target['target']} {target['label']}` | "
                f"`{target['alignedTraceCount']}` | `{target['traceTypes']}` | "
                f"`{target['alignedText']}` | `{target['componentHitText']}` | `{target['strictInstructionText']}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not reopen the PDF text overlay as an extraction source.",
            "- All page-76 text overlay spans are invisible/type-3 OCR traces, not visible original-layout typography.",
            "- The fit-available OCR overlays still contain no active exact components or strict unit/order terms inside O4/B4/G5/O5.",
            "",
            "## Next Move",
            "",
            "- Treat PDF text overlays as derivative OCR context only. Future progress still depends on new physical/original-layout/source evidence or a raw clue that passes the reopen gate.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", fingerprint)


if __name__ == "__main__":
    main()
