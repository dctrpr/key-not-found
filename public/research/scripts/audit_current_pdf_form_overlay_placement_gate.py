#!/usr/bin/env python3
"""Audit the duplicate-PDF OCR form overlay placement.

The content-matrix gate showed a repeated `OL2` form placement with a tiny
vertical offset. This pass applies that placement matrix to the form XObject
BBox to determine whether it is a hidden/local layout signal or simply a
near-full-page invisible OCR overlay.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_form_overlay_placement_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_form_overlay_placement_gate.json"
OUT_MD = OUT / "current_pdf_form_overlay_placement_gate.md"
OUT_SHEET = OUT / "current_pdf_form_overlay_placement_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_TARGETS = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
CONTENT_MATRIX = ROOT / (
    "analysis_outputs/source_audit/current_pdf_content_transform_matrix_gate/"
    "current_pdf_content_transform_matrix_gate.json"
)
FORM_DICTIONARY = ROOT / (
    "analysis_outputs/source_audit/current_pdf_form_xobject_dictionary_gate/"
    "current_pdf_form_xobject_dictionary_gate.json"
)
TEXT_RENDER_MODE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/"
    "current_pdf_text_overlay_render_mode_gate.json"
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


Matrix = tuple[float, float, float, float, float, float]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def apply_matrix(matrix: Matrix, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def transformed_bbox(matrix: Matrix, bbox: list[float]) -> list[float]:
    x0, y0, x1, y1 = bbox
    points = [
        apply_matrix(matrix, x0, y0),
        apply_matrix(matrix, x1, y0),
        apply_matrix(matrix, x0, y1),
        apply_matrix(matrix, x1, y1),
    ]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [round(min(xs), 6), round(min(ys), 6), round(max(xs), 6), round(max(ys), 6)]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def project_active_box_to_page(active_box: list[float], page_rect: list[float]) -> list[float]:
    src_w, src_h = SOURCE_IMAGE_SIZE
    px0, py0, px1, py1 = page_rect
    pw = px1 - px0
    ph = py1 - py0
    x0, y0, x1, y1 = active_box
    return [
        px0 + (x0 / src_w) * pw,
        py0 + (y0 / src_h) * ph,
        px0 + (x1 / src_w) * pw,
        py0 + (y1 / src_h) * ph,
    ]


def page_rects_by_pdf() -> dict[tuple[str, int], list[float]]:
    rows: dict[tuple[str, int], list[float]] = {}
    for path in PDFS:
        if not path.exists():
            continue
        doc = fitz.open(path)
        for index, page in enumerate(doc, start=1):
            article_page = 73 + index - 1 if doc.page_count == 8 else index
            rows[(rel(path), article_page)] = [
                round(page.rect.x0, 6),
                round(page.rect.y0, 6),
                round(page.rect.x1, 6),
                round(page.rect.y1, 6),
            ]
        doc.close()
    return rows


def flatten_form_placements(content_matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in content_matrix.get("pdfRows", []):
        for row in pdf_row.get("placementRows", []):
            if row.get("role") == "form":
                rows.append(row)
    return rows


def flatten_form_objects(form_dictionary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in form_dictionary.get("pdfRows", []):
        for row in pdf_row.get("formRows", []):
            rows.append(row)
    return rows


def draw_sheet(summary: dict[str, Any], p76_rows: list[dict[str, Any]], active_targets: list[dict[str, Any]]) -> None:
    width, height = 1700, 1050
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 28)
        header_font = ImageFont.truetype("Arial.ttf", 18)
        small = ImageFont.truetype("Arial.ttf", 15)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 110), fill=(28, 34, 44))
    draw.text((28, 22), "Current PDF Form Overlay Placement Gate", fill="white", font=title_font)
    draw.text(
        (28, 66),
        "Applies the OL2 form matrix to its BBox to test whether the OCR overlay offset is meaningful.",
        fill=(235, 238, 242),
        font=small,
    )

    cards = [
        ("form placements", summary["formPlacementCount"]),
        ("page-76 forms", summary["page76FormPlacementCount"]),
        ("near-full overlays", summary["nearFullOverlayCount"]),
        ("unique page-76 groups", summary["page76UniqueOverlaySignatureCount"]),
        ("visible text rows", summary["visibleTextPlacementCount"]),
        ("R3/triggers", f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"),
    ]
    x = 28
    y = 132
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 252, y + 78), radius=6, fill=(247, 248, 250), outline=(210, 215, 222))
        draw.text((x + 14, y + 12), label, fill=(85, 90, 100), font=tiny)
        draw.text((x + 14, y + 38), str(value), fill=(20, 25, 32), font=header_font)
        x += 270

    draw.text((28, 244), "Page-76 OL2 overlays", fill=(20, 25, 32), font=header_font)
    headers = ["PDF", "xref", "matrix", "display bbox", "coverage", "strict", "visible", "verdict"]
    xs = [28, 442, 500, 700, 970, 1060, 1125, 1200]
    y = 276
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(85, 90, 100), font=tiny)
    y += 22
    for row in p76_rows:
        values = [
            row["pdf"],
            row["formXref"],
            ",".join(f"{value:.3f}" for value in row["placementMatrix"]),
            ",".join(f"{value:.2f}" for value in row["displayBBox"]),
            f"{row['pageCoverage']:.6f}",
            row["strictHitCount"],
            row["visibleTextRenderModeCount"],
            "near-full invisible OCR overlay",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value)[:60], fill=(35, 38, 45), font=tiny)
        y += 24

    source_path = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
    if source_path.exists():
        source = Image.open(source_path).convert("RGB")
        panel_w = 610
        scale = panel_w / source.width
        panel_h = int(source.height * scale)
        page = source.resize((panel_w, panel_h))
        px, py = 60, 390
        sheet.paste(page, (px, py))
        draw.rectangle((px, py, px + panel_w, py + panel_h), outline=(40, 45, 55), width=2)
        if p76_rows:
            row = p76_rows[0]
            page_rect = row["pageRect"]
            bbox = row["displayBBox"]
            left = int(((bbox[0] - page_rect[0]) / (page_rect[2] - page_rect[0])) * panel_w)
            top = int(((bbox[1] - page_rect[1]) / (page_rect[3] - page_rect[1])) * panel_h)
            right = int(((bbox[2] - page_rect[0]) / (page_rect[2] - page_rect[0])) * panel_w)
            bottom = int(((bbox[3] - page_rect[1]) / (page_rect[3] - page_rect[1])) * panel_h)
            draw.rectangle((px + left, py + top, px + right, py + bottom), outline=(35, 135, 220), width=4)
        for target in active_targets:
            box = [int(value * scale) for value in target["box"]]
            draw.rectangle((px + box[0], py + box[1], px + box[2], py + box[3]), outline=(255, 125, 0), width=3)
            draw.text((px + box[0], py + box[1] - 15), target["id"], fill=(255, 125, 0), font=tiny)
        draw.text((px, py + panel_h + 10), "Blue: near-full OCR form overlay. Orange: active targets.", fill=(35, 38, 45), font=small)

    explanation = [
        "The OL2 matrix offset is 0.119995 pt, less than one sixth of a PDF point.",
        "Applied to the form BBox it makes a near-full-page overlay, not a 1x1 mark.",
        "The same normalized placement repeats across every duplicate-PDF article page.",
        "The overlay text is invisible OCR only; visible painted spans and strict terms remain zero.",
    ]
    ty = 680
    for line in explanation:
        draw.text((760, ty), line, fill=(35, 38, 45), font=small)
        ty += 32

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_TARGETS)
    content_matrix = load_json(CONTENT_MATRIX)
    form_dictionary = load_json(FORM_DICTIONARY)
    text_render_mode = load_json(TEXT_RENDER_MODE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_targets = active.get("targets", [])
    page_rects = page_rects_by_pdf()
    placement_rows = flatten_form_placements(content_matrix)
    form_rows = flatten_form_objects(form_dictionary)
    form_by_key = {
        (row.get("pdf"), row.get("articlePage"), row.get("resourceName")): row
        for row in form_rows
    }

    overlay_rows: list[dict[str, Any]] = []
    for placement in placement_rows:
        key = (placement.get("pdf"), placement.get("articlePage"), placement.get("resourceName"))
        form = form_by_key.get(key, {})
        page_rect = page_rects.get((placement.get("pdf"), placement.get("articlePage")), [0.0, 0.0, 612.0, 792.0])
        matrix = tuple(float(value) for value in placement.get("cumulativeMatrix", [1, 0, 0, 1, 0, 0]))
        form_bbox = form.get("bboxFromPage") or [0.0, 0.0, page_rect[2] - page_rect[0], page_rect[3] - page_rect[1]]
        display_bbox = transformed_bbox(matrix, [float(value) for value in form_bbox])
        page_coverage = area(display_bbox) / area(page_rect) if area(page_rect) else 0.0
        top_gap = display_bbox[1] - page_rect[1]
        bottom_gap = page_rect[3] - display_bbox[3]
        left_gap = display_bbox[0] - page_rect[0]
        right_gap = page_rect[2] - display_bbox[2]
        row = {
            "pdf": placement.get("pdf"),
            "pdfPage": placement.get("pdfPage"),
            "articlePage": placement.get("articlePage"),
            "pageXref": placement.get("pageXref"),
            "resourceName": placement.get("resourceName"),
            "formXref": form.get("xref"),
            "placementMatrix": [round(value, 6) for value in matrix],
            "formBBox": [round(float(value), 6) for value in form_bbox],
            "displayBBox": display_bbox,
            "pageRect": page_rect,
            "pageCoverage": round(page_coverage, 6),
            "leftGapPt": round(left_gap, 6),
            "rightGapPt": round(right_gap, 6),
            "topGapPt": round(top_gap, 6),
            "bottomGapPt": round(bottom_gap, 6),
            "nearFullOverlay": page_coverage >= 0.995,
            "strictHitCount": len(form.get("strictHitTerms", [])),
            "contextHitCount": len(form.get("contextHitTerms", [])),
            "visibleTextRenderModeCount": int(form.get("visibleTextRenderModeCount") or 0),
            "invisibleTextRenderModeCount": int(form.get("invisibleTextRenderModeCount") or 0),
            "textObjectCount": int(form.get("textObjectCount") or 0),
            "textShowOperatorCount": int(form.get("textShowOperatorCount") or 0),
            "decodedStreamByteCount": int(form.get("decodedStreamByteCount") or 0),
            "normalizedDictionaryHash16": form.get("normalizedDictionaryHash16"),
            "placementSignatureHash16": placement.get("placementSignatureHash16"),
        }
        row["overlaySignatureHash16"] = sha16(
            json.dumps(
                {
                    "resource": row["resourceName"],
                    "matrix": row["placementMatrix"],
                    "formBBox": row["formBBox"],
                    "displayBBox": row["displayBBox"],
                    "nearFull": row["nearFullOverlay"],
                    "dict": row["normalizedDictionaryHash16"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        overlay_rows.append(row)

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in overlay_rows:
        groups.setdefault(row["overlaySignatureHash16"], []).append(row)
    for row in overlay_rows:
        group = groups[row["overlaySignatureHash16"]]
        pages = sorted({member["articlePage"] for member in group if member.get("articlePage")})
        pdfs = sorted({member["pdf"] for member in group if member.get("pdf")})
        row["signatureRecordCount"] = len(group)
        row["signatureArticlePages"] = pages
        row["signaturePdfs"] = pdfs
        row["signatureRepeatsEveryPageInPdfSet"] = pages == list(range(73, 81))
        row["page76UniqueOverlaySignature"] = len(group) == 1

    projection_rows: list[dict[str, Any]] = []
    for overlay in [row for row in overlay_rows if row["articlePage"] == 76]:
        for target in active_targets:
            page_box = project_active_box_to_page(target["box"], overlay["pageRect"])
            coverage = overlap_area(page_box, overlay["displayBBox"]) / area(page_box)
            projection_rows.append(
                {
                    "pdf": overlay["pdf"],
                    "articlePage": overlay["articlePage"],
                    "formXref": overlay["formXref"],
                    "targetId": target["id"],
                    "targetLabel": target["label"],
                    "targetPhrase": target["phrase"],
                    "projectedPageBox": [round(value, 6) for value in page_box],
                    "coverageInsideOverlay": round(coverage, 6),
                    "insideOverlay": coverage >= 0.995,
                }
            )

    source_r3 = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    triggers = int(reopen.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(reopen.get("summary", {}).get("triggerCount") or 0)
    p76_rows = [row for row in overlay_rows if row["articlePage"] == 76]
    active_inside = sum(1 for row in projection_rows if row["insideOverlay"])
    p76_signature_hashes = {row["overlaySignatureHash16"] for row in p76_rows}
    unique_p76_signatures = {sig for sig in p76_signature_hashes if len(groups[sig]) == 1}
    offsets = sorted({row["topGapPt"] for row in overlay_rows})
    active_pages = {76, 78, 79, 80}
    active_unique_signatures = {
        row["overlaySignatureHash16"]
        for row in overlay_rows
        if row["articlePage"] in active_pages
        and all(member["articlePage"] in active_pages for member in groups[row["overlaySignatureHash16"]])
    }

    summary = {
        "pdfCount": len([path for path in PDFS if path.exists()]),
        "formPlacementCount": len(overlay_rows),
        "page76FormPlacementCount": len(p76_rows),
        "overlaySignatureGroupCount": len(groups),
        "page76UniqueOverlaySignatureCount": len(unique_p76_signatures),
        "activeUniqueOverlaySignatureCount": len(active_unique_signatures),
        "nearFullOverlayCount": sum(1 for row in overlay_rows if row["nearFullOverlay"]),
        "page76NearFullOverlayCount": sum(1 for row in p76_rows if row["nearFullOverlay"]),
        "allPageRepeatingOverlayGroupCount": sum(
            1 for group in groups.values()
            if sorted({row["articlePage"] for row in group if row.get("articlePage")}) == list(range(73, 81))
        ),
        "visibleTextPlacementCount": sum(1 for row in overlay_rows if row["visibleTextRenderModeCount"] > 0),
        "invisibleTextPlacementCount": sum(1 for row in overlay_rows if row["invisibleTextRenderModeCount"] > 0),
        "strictHitCount": sum(row["strictHitCount"] for row in overlay_rows),
        "contextHitCount": sum(row["contextHitCount"] for row in overlay_rows),
        "topOffsetPtValues": offsets,
        "topOffsetPage76Values": sorted({row["topGapPt"] for row in p76_rows}),
        "activeProjectionInsideCount": active_inside,
        "activeProjectionRowCount": len(projection_rows),
        "activeInsideRatio": round(active_inside / len(projection_rows), 6) if projection_rows else 0.0,
        "textOverlayVisiblePaintedTraceSpanCount": text_render_mode.get("summary", {}).get("visiblePaintedTraceSpanCount"),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"forms={summary['formPlacementCount']}|p76Forms={summary['page76FormPlacementCount']}|"
        f"groups={summary['overlaySignatureGroupCount']}|p76Unique={summary['page76UniqueOverlaySignatureCount']}|"
        f"activeUnique={summary['activeUniqueOverlaySignatureCount']}|nearFull={summary['nearFullOverlayCount']}|"
        f"p76NearFull={summary['page76NearFullOverlayCount']}|allPageGroups={summary['allPageRepeatingOverlayGroupCount']}|"
        f"visiblePlacements={summary['visibleTextPlacementCount']}|invisiblePlacements={summary['invisibleTextPlacementCount']}|"
        f"strict={summary['strictHitCount']}|offsets={','.join(map(str, offsets))}|"
        f"activeInside={summary['activeProjectionInsideCount']}/{summary['activeProjectionRowCount']}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors=0"
    )

    decision = {
        "currentPdfFormOverlayPlacementGate": "current_pdf_form_overlay_placement_no_selector",
        "selectorUnlocked": False,
        "reason": (
            "The repeated OL2 form matrix offset applies to a near-full-page OCR form BBox, not a local "
            "page-76 mark. The same overlay signature repeats across every duplicate-PDF article page, "
            "has no page-76-unique group, contains only invisible OCR text, and has no strict unit/order "
            "terms or source-backed R3 bridge."
        ),
        "nextMove": (
            "Treat the duplicate-PDF OCR form overlay as a text-search aid only. Keep the next best move "
            "on true source/original-layout/raw clue acquisition rather than PDF OCR-wrapper geometry."
        ),
    }

    draw_sheet(summary, p76_rows, active_targets)
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF OCR form overlay placement audit; no extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "activeTargets": rel(ACTIVE_TARGETS),
            "contentTransformMatrix": rel(CONTENT_MATRIX),
            "formXobjectDictionary": rel(FORM_DICTIONARY),
            "textOverlayRenderMode": rel(TEXT_RENDER_MODE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "overlayRows": overlay_rows,
        "activeProjectionRows": projection_rows,
        "fingerprint": fingerprint,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Form Overlay Placement Gate",
        "",
        "Scope: applied the duplicate-PDF `OL2` form placement matrix to its form BBox to test whether the tiny offset is a page-76/original-layout selector or only an invisible OCR overlay. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Form placements / page-76 form placements: `{summary['formPlacementCount']}` / `{summary['page76FormPlacementCount']}`",
        f"- Overlay signature groups / page-76 unique groups: `{summary['overlaySignatureGroupCount']}` / `{summary['page76UniqueOverlaySignatureCount']}`",
        f"- Active unique overlay groups: `{summary['activeUniqueOverlaySignatureCount']}`",
        f"- Near-full overlays / page-76 near-full overlays: `{summary['nearFullOverlayCount']}` / `{summary['page76NearFullOverlayCount']}`",
        f"- All-page repeating overlay groups: `{summary['allPageRepeatingOverlayGroupCount']}`",
        f"- Visible/invisible text placements: `{summary['visibleTextPlacementCount']}` / `{summary['invisibleTextPlacementCount']}`",
        f"- Strict/context hits: `{summary['strictHitCount']}` / `{summary['contextHitCount']}`",
        f"- Top offset pt values: `{','.join(map(str, summary['topOffsetPtValues']))}`",
        f"- Active projection rows inside overlay: `{summary['activeProjectionInsideCount']}` / `{summary['activeProjectionRowCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{fingerprint}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Page-76 Form Overlay Rows",
        "",
        "| PDF | form xref | matrix | form bbox | display bbox | coverage | visible | strict | repeats every page |",
        "|---|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for row in p76_rows:
        lines.append(
            f"| `{row['pdf']}` | {row['formXref']} | `{'/'.join(map(str, row['placementMatrix']))}` | `{'/'.join(map(str, row['formBBox']))}` | `{'/'.join(map(str, row['displayBBox']))}` | {row['pageCoverage']:.6f} | {row['visibleTextRenderModeCount']} | {row['strictHitCount']} | `{int(row['signatureRepeatsEveryPageInPdfSet'])}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Decision: `{decision['currentPdfFormOverlayPlacementGate']}`",
            f"- Reason: {decision['reason']}",
            f"- Next move: {decision['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"summary": summary, "fingerprint": fingerprint}, indent=2))


if __name__ == "__main__":
    main()
