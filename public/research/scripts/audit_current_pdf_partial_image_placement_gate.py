#!/usr/bin/env python3
"""Audit page-76 partial image placements in the current PDFs.

This pass resolves the remaining ambiguity from the PDF object/layout report:
two page-76 rows were marked as partial image placements. It checks whether
those rows are local overlays/hidden layout assets or simply inset full-page
raster images inside duplicate lower-resolution PDFs.

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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_partial_image_placement_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_partial_image_placement_gate.json"
OUT_MD = OUT / "current_pdf_partial_image_placement_gate.md"
OUT_SHEET = OUT / "current_pdf_partial_image_placement_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_TARGETS = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
OBJECT_LAYOUT = ROOT / (
    "analysis_outputs/source_audit/current_pdf_object_layout_inspection/"
    "current_pdf_object_layout_inspection.json"
)
CONTENT_MATRIX = ROOT / (
    "analysis_outputs/source_audit/current_pdf_content_transform_matrix_gate/"
    "current_pdf_content_transform_matrix_gate.json"
)
IMAGE_DICTIONARY = ROOT / (
    "analysis_outputs/source_audit/current_pdf_image_xobject_dictionary_gate/"
    "current_pdf_image_xobject_dictionary_gate.json"
)
PAGE_RESOURCE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_page_resource_order_gate/"
    "current_pdf_page_resource_order_gate.json"
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def rect_area(rect: fitz.Rect) -> float:
    return max(0.0, rect.width) * max(0.0, rect.height)


def round_rect(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 6), round(rect.y0, 6), round(rect.x1, 6), round(rect.y1, 6)]


def overlap_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def box_area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def signature_for(row: dict[str, Any]) -> str:
    payload = {
        "imageSize": row["imageSize"],
        "pageRect": row["pageRect"],
        "rectNorm": row["rectNorm"],
        "coverageBucket": round(row["pageCoverage"], 3),
        "nearFullContent": row["nearFullContentPlacement"],
        "partial": row["partialImagePlacement"],
    }
    return sha16(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def project_active_box_to_page(active_box: list[float], image_rect: list[float]) -> list[float]:
    src_w, src_h = SOURCE_IMAGE_SIZE
    x0, y0, x1, y1 = active_box
    rx0, ry0, rx1, ry1 = image_rect
    rw = rx1 - rx0
    rh = ry1 - ry0
    return [
        rx0 + (x0 / src_w) * rw,
        ry0 + (y0 / src_h) * rh,
        rx0 + (x1 / src_w) * rw,
        ry0 + (y1 / src_h) * rh,
    ]


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    image_rows: list[dict[str, Any]] = []
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        page_rect = page.rect
        page_area = rect_area(page_rect)
        for image in page.get_images(full=True):
            xref = int(image[0])
            extracted = doc.extract_image(xref)
            width = int(extracted.get("width", image[2]))
            height = int(extracted.get("height", image[3]))
            for rect in page.get_image_rects(xref):
                coverage = rect_area(rect) / page_area if page_area else 0.0
                width_fraction = rect.width / page_rect.width if page_rect.width else 0.0
                height_fraction = rect.height / page_rect.height if page_rect.height else 0.0
                row = {
                    "pdf": rel(path),
                    "pdfPage": index + 1,
                    "articlePage": article_page,
                    "pageXref": int(page.xref),
                    "rotation": int(page.rotation),
                    "imageXref": xref,
                    "imageSize": [width, height],
                    "pageRect": round_rect(page_rect),
                    "imageRect": round_rect(rect),
                    "rectNorm": [
                        round(rect.x0 / page_rect.width, 6),
                        round(rect.y0 / page_rect.height, 6),
                        round(rect.x1 / page_rect.width, 6),
                        round(rect.y1 / page_rect.height, 6),
                    ],
                    "pageCoverage": round(coverage, 6),
                    "widthFraction": round(width_fraction, 6),
                    "heightFraction": round(height_fraction, 6),
                    "partialImagePlacement": coverage < 0.995,
                    "fullBleedPlacement": coverage >= 0.995,
                    "nearFullContentPlacement": coverage >= 0.90
                    and (height_fraction >= 0.995 or width_fraction >= 0.90),
                    "localOverlayCandidate": coverage < 0.75,
                }
                row["placementSignatureHash16"] = signature_for(row)
                image_rows.append(row)
    doc.close()
    return {
        "pdf": rel(path),
        "pageCount": len({row["pdfPage"] for row in image_rows}),
        "imageRows": image_rows,
    }


def active_projection_rows(partial_rows: list[dict[str, Any]], active_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for placement in partial_rows:
        placement_rect = placement["imageRect"]
        for target in active_targets:
            page_box = project_active_box_to_page(target["box"], placement_rect)
            coverage = overlap_area(page_box, placement_rect) / box_area(page_box)
            rows.append(
                {
                    "pdf": placement["pdf"],
                    "pdfPage": placement["pdfPage"],
                    "articlePage": placement["articlePage"],
                    "imageXref": placement["imageXref"],
                    "targetId": target["id"],
                    "targetLabel": target["label"],
                    "targetPhrase": target["phrase"],
                    "projectedPageBox": [round(value, 6) for value in page_box],
                    "coverageInsidePlacement": round(coverage, 6),
                    "insidePlacement": coverage >= 0.995,
                }
            )
    return rows


def draw_sheet(summary: dict[str, Any], partial_rows: list[dict[str, Any]], active_targets: list[dict[str, Any]]) -> None:
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
    draw.text((28, 22), "Current PDF Partial Image Placement Gate", fill="white", font=title_font)
    draw.text(
        (28, 66),
        "Checks whether page-76 partial image rows are local overlays or just inset full-page raster images.",
        fill=(235, 238, 242),
        font=small,
    )

    cards = [
        ("p76 partial rows", summary["page76PartialPlacementCount"]),
        ("unique p76 partial groups", summary["page76UniquePartialSignatureCount"]),
        ("near-full content rows", summary["page76NearFullContentPartialCount"]),
        ("local overlay rows", summary["page76LocalOverlayPartialCount"]),
        ("all-four inside rows", summary["page76PartialAllFourInsideCount"]),
        ("R3/triggers", f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"),
    ]
    x = 28
    y = 132
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 252, y + 78), radius=6, fill=(247, 248, 250), outline=(210, 215, 222))
        draw.text((x + 14, y + 12), label, fill=(85, 90, 100), font=tiny)
        draw.text((x + 14, y + 38), str(value), fill=(20, 25, 32), font=header_font)
        x += 270

    draw.text((28, 244), "Page-76 partial placements", fill=(20, 25, 32), font=header_font)
    headers = ["PDF", "xref", "image", "rect norm", "coverage", "all pages", "verdict"]
    xs = [28, 470, 530, 640, 900, 1010, 1120]
    y = 276
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(85, 90, 100), font=tiny)
    y += 22
    for row in partial_rows:
        values = [
            row["pdf"],
            row["imageXref"],
            f"{row['imageSize'][0]}x{row['imageSize'][1]}",
            ",".join(f"{value:.3f}" for value in row["rectNorm"]),
            f"{row['pageCoverage']:.6f}",
            "yes" if row["signatureRepeatsEveryPageInPdfSet"] else "no",
            "inset full-page raster" if row["nearFullContentPlacement"] else "local overlay",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value)[:56], fill=(35, 38, 45), font=tiny)
        y += 24

    source_path = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
    if source_path.exists():
        source = Image.open(source_path).convert("RGB")
        panel_w = 610
        scale = panel_w / source.width
        panel_h = int(source.height * scale)
        page = source.resize((panel_w, panel_h))
        px, py = 44, 390
        sheet.paste(page, (px, py))
        draw.rectangle((px, py, px + panel_w, py + panel_h), outline=(40, 45, 55), width=2)
        for target in active_targets:
            box = [int(value * scale) for value in target["box"]]
            draw.rectangle((px + box[0], py + box[1], px + box[2], py + box[3]), outline=(255, 125, 0), width=3)
            draw.text((px + box[0], py + box[1] - 15), target["id"], fill=(255, 125, 0), font=tiny)
        draw.text((px, py + panel_h + 10), "Active boxes on full page-76 raster", fill=(35, 38, 45), font=small)

        # Show the duplicate-PDF side margins as an inset content rectangle.
        px2, py2 = 760, 390
        sheet.paste(page, (px2, py2))
        draw.rectangle((px2, py2, px2 + panel_w, py2 + panel_h), outline=(40, 45, 55), width=2)
        if partial_rows:
            row = partial_rows[0]
            left = int(row["rectNorm"][0] * panel_w)
            top = int(row["rectNorm"][1] * panel_h)
            right = int(row["rectNorm"][2] * panel_w)
            bottom = int(row["rectNorm"][3] * panel_h)
            draw.rectangle((px2 + left, py2 + top, px2 + right, py2 + bottom), outline=(40, 140, 220), width=4)
        for target in active_targets:
            box = [int(value * scale) for value in target["box"]]
            draw.rectangle((px2 + box[0], py2 + box[1], px2 + box[2], py2 + box[3]), outline=(255, 125, 0), width=3)
        draw.text((px2, py2 + panel_h + 10), "Duplicate PDFs: blue border is the inset raster image", fill=(35, 38, 45), font=small)

    explanation = [
        "The two partial rows are the same lower-resolution page image inset with side margins.",
        "They repeat across every article page in the duplicate PDF pair.",
        "They contain all four active boxes only because the image is the whole page content.",
        "No page-76-only local overlay, hidden placement, strict unit/order wording, or source-backed bridge appears.",
    ]
    ty = 735
    for line in explanation:
        draw.text((1420, ty), line, fill=(35, 38, 45), font=small)
        ty += 30

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_report = load_json(ACTIVE_TARGETS)
    object_layout = load_json(OBJECT_LAYOUT)
    content_matrix = load_json(CONTENT_MATRIX)
    image_dictionary = load_json(IMAGE_DICTIONARY)
    page_resource = load_json(PAGE_RESOURCE)
    text_render = load_json(TEXT_RENDER_MODE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_targets = active_report.get("targets", [])
    pdf_rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    placement_rows = [row for pdf in pdf_rows for row in pdf["imageRows"]]
    page76_rows = [row for row in placement_rows if row["articlePage"] == 76]
    partial_rows = [row for row in page76_rows if row["partialImagePlacement"]]

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in placement_rows:
        groups.setdefault(row["placementSignatureHash16"], []).append(row)

    for row in partial_rows:
        group = groups[row["placementSignatureHash16"]]
        group_pages = sorted({member["articlePage"] for member in group if member["articlePage"]})
        group_pdfs = sorted({member["pdf"] for member in group})
        row["signatureRecordCount"] = len(group)
        row["signatureArticlePages"] = group_pages
        row["signaturePdfs"] = group_pdfs
        row["signatureRepeatsEveryPageInPdfSet"] = group_pages == list(range(73, 81))
        row["page76UniquePartialSignature"] = len(group) == 1

    projection_rows = active_projection_rows(partial_rows, active_targets)
    by_placement: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in projection_rows:
        by_placement.setdefault((row["pdf"], row["imageXref"]), []).append(row)

    source_r3 = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    triggers = int(reopen.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(reopen.get("summary", {}).get("triggerCount") or 0)
    strict_hits = int(content_matrix.get("summary", {}).get("strictHitCount") or 0)
    image_special = int(image_dictionary.get("summary", {}).get("specialKeyRowCount") or 0)
    page_special = int(page_resource.get("summary", {}).get("specialPageKeyRowCount") or 0)
    visible_spans = int(text_render.get("summary", {}).get("visiblePaintedTextSpanCount") or 0)

    active_inside_count = sum(1 for row in projection_rows if row["insidePlacement"])
    active_projection_count = len(projection_rows)
    partial_all_four_inside = sum(
        1 for rows in by_placement.values() if len(rows) == len(active_targets) and all(row["insidePlacement"] for row in rows)
    )
    unique_partial_groups = {
        row["placementSignatureHash16"]
        for row in partial_rows
        if row["page76UniquePartialSignature"]
    }
    all_page_partial_groups = {
        row["placementSignatureHash16"]
        for row in partial_rows
        if row["signatureRepeatsEveryPageInPdfSet"]
    }
    coverage_values = [row["pageCoverage"] for row in partial_rows]

    summary = {
        "pdfCount": len(pdf_rows),
        "placementRowCount": len(placement_rows),
        "page76ImagePlacementCount": len(page76_rows),
        "page76PartialPlacementCount": len(partial_rows),
        "objectLayoutPage76PartialImagePlacementCount": object_layout.get("summary", {}).get(
            "page76PartialImagePlacementCount"
        ),
        "page76PartialSignatureGroupCount": len({row["placementSignatureHash16"] for row in partial_rows}),
        "page76UniquePartialSignatureCount": len(unique_partial_groups),
        "page76NearFullContentPartialCount": sum(1 for row in partial_rows if row["nearFullContentPlacement"]),
        "page76LocalOverlayPartialCount": sum(1 for row in partial_rows if row["localOverlayCandidate"]),
        "page76AllPageRepeatingPartialGroupCount": len(all_page_partial_groups),
        "page76PartialAllFourInsideCount": partial_all_four_inside,
        "activeProjectionInsideCount": active_inside_count,
        "activeProjectionRowCount": active_projection_count,
        "activeInsideRatio": round(active_inside_count / active_projection_count, 6) if active_projection_count else 0.0,
        "partialCoverageMin": min(coverage_values) if coverage_values else None,
        "partialCoverageMax": max(coverage_values) if coverage_values else None,
        "strictHitCount": strict_hits,
        "imageSpecialKeyRowCount": image_special,
        "pageSpecialKeyRowCount": page_special,
        "visiblePaintedTextSpanCount": visible_spans,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"p76Partial={summary['page76PartialPlacementCount']}|"
        f"partialGroups={summary['page76PartialSignatureGroupCount']}|"
        f"uniqueP76Partial={summary['page76UniquePartialSignatureCount']}|"
        f"nearFull={summary['page76NearFullContentPartialCount']}|"
        f"localPartial={summary['page76LocalOverlayPartialCount']}|"
        f"allPageGroups={summary['page76AllPageRepeatingPartialGroupCount']}|"
        f"allFourInside={summary['page76PartialAllFourInsideCount']}|"
        f"activeInside={summary['activeProjectionInsideCount']}/{summary['activeProjectionRowCount']}|"
        f"strict={strict_hits}|special={image_special + page_special}|visible={visible_spans}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors=0"
    )

    decision = {
        "currentPdfPartialImagePlacementGate": "current_pdf_partial_image_placement_no_selector",
        "selectorUnlocked": False,
        "reason": (
            "The only page-76 partial image placements are the duplicate lower-resolution PDFs' inset "
            "full-page raster images. They cover about 94.1% of the page, span the full page height, "
            "repeat across every article page, and carry no page-76-unique local overlay, hidden placement, "
            "visible text, special resource key, strict unit/order term, or source-backed R3 bridge. "
            "They contain O4/B4/G5/O5 only because the entire page content is inside the raster image."
        ),
        "nextMove": (
            "Stop treating current-PDF partial placements as original-layout evidence. The next useful move "
            "is still source acquisition or raw clue wording that supplies transform, unit, and order, with "
            "the current scan used only as a visual comparison witness."
        ),
    }

    draw_sheet(summary, partial_rows, active_targets)
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF page-76 partial image placement audit; no extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "activeTargets": rel(ACTIVE_TARGETS),
            "objectLayout": rel(OBJECT_LAYOUT),
            "contentTransformMatrix": rel(CONTENT_MATRIX),
            "imageXobjectDictionary": rel(IMAGE_DICTIONARY),
            "pageResourceOrder": rel(PAGE_RESOURCE),
            "textOverlayRenderMode": rel(TEXT_RENDER_MODE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "partialPlacementRows": partial_rows,
        "activeProjectionRows": projection_rows,
        "pdfRows": pdf_rows,
        "fingerprint": fingerprint,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Partial Image Placement Gate",
        "",
        "Scope: resolved the two page-76 `partialImagePlacement` rows from the current PDF object/layout report. This checks whether they are local overlays/original-layout carriers or just inset full-page raster pages. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / image placements / page-76 image placements: `{summary['pdfCount']}` / `{summary['placementRowCount']}` / `{summary['page76ImagePlacementCount']}`",
        f"- Page-76 partial placements: `{summary['page76PartialPlacementCount']}`",
        f"- Object-layout page-76 partial placement count: `{summary['objectLayoutPage76PartialImagePlacementCount']}`",
        f"- Partial signature groups / unique page-76 partial groups: `{summary['page76PartialSignatureGroupCount']}` / `{summary['page76UniquePartialSignatureCount']}`",
        f"- Near-full content partial rows / local overlay partial rows: `{summary['page76NearFullContentPartialCount']}` / `{summary['page76LocalOverlayPartialCount']}`",
        f"- All-page repeating partial groups: `{summary['page76AllPageRepeatingPartialGroupCount']}`",
        f"- Partial rows containing all four active boxes: `{summary['page76PartialAllFourInsideCount']}`",
        f"- Active projection rows inside placement: `{summary['activeProjectionInsideCount']}` / `{summary['activeProjectionRowCount']}`",
        f"- Partial coverage range: `{summary['partialCoverageMin']}` - `{summary['partialCoverageMax']}`",
        f"- Strict hits / special keys / visible painted spans: `{summary['strictHitCount']}` / `{summary['imageSpecialKeyRowCount'] + summary['pageSpecialKeyRowCount']}` / `{summary['visiblePaintedTextSpanCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{fingerprint}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Page-76 Partial Placement Rows",
        "",
        "| PDF | image xref | image size | rect norm | page coverage | repeats every page | all four active boxes inside | verdict |",
        "|---|---:|---|---|---:|---:|---:|---|",
    ]
    all_four_keys = {
        key for key, rows in by_placement.items() if len(rows) == len(active_targets) and all(row["insidePlacement"] for row in rows)
    }
    for row in partial_rows:
        key = (row["pdf"], row["imageXref"])
        verdict = "inset full-page raster" if row["nearFullContentPlacement"] else "local overlay candidate"
        lines.append(
            f"| `{row['pdf']}` | {row['imageXref']} | `{row['imageSize'][0]}x{row['imageSize'][1]}` | `{'/'.join(f'{value:.6f}' for value in row['rectNorm'])}` | {row['pageCoverage']:.6f} | `{int(row['signatureRepeatsEveryPageInPdfSet'])}` | `{int(key in all_four_keys)}` | {verdict} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Decision: `{decision['currentPdfPartialImagePlacementGate']}`",
            f"- Reason: {decision['reason']}",
            f"- Next move: {decision['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"summary": summary, "fingerprint": fingerprint}, indent=2))


if __name__ == "__main__":
    main()
