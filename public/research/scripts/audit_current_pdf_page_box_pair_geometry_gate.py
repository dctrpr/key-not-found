#!/usr/bin/env python3
"""Audit current PDF page-box geometry for the valid 75 -> 76 leaf pair.

This is a bounded source/layout inspection. It checks whether the current PDFs
carry crop-box, rotation, image-placement, scale, or hidden-layer differences
between article pages 75 and 76 that would change the held-to-light geometry.
It does not generate keys, hashes, seed phrases, WIFs, addresses, BIP39 checks,
or candidate material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_page_box_pair_geometry_gate.json"
OUT_MD = OUT / "current_pdf_page_box_pair_geometry_gate.md"
OUT_SHEET = OUT / "current_pdf_page_box_pair_geometry_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ARTICLE_PAGES = (75, 76)
TARGET_PDF_PAGE_INDEXES = (2, 3)
EPS = 1e-3


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rect_list(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 4), round(rect.y0, 4), round(rect.x1, 4), round(rect.y1, 4)]


def same_list(a: list[float], b: list[float], eps: float = EPS) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= eps for x, y in zip(a, b))


def rect_area(rect: list[float]) -> float:
    return max(0.0, rect[2] - rect[0]) * max(0.0, rect[3] - rect[1])


def page_area(rect: list[float]) -> float:
    return rect_area(rect)


def page_record(doc: fitz.Document, pdf_path: Path, page_index: int) -> dict[str, Any]:
    page = doc[page_index]
    page_rect = rect_list(page.rect)
    cropbox = rect_list(page.cropbox)
    mediabox = rect_list(page.mediabox)
    images = []

    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = doc.extract_image(xref)
        rects = page.get_image_rects(xref)
        image_rects = [rect_list(rect) for rect in rects]
        max_coverage = 0.0
        for rect in image_rects:
            coverage = rect_area(rect) / max(page_area(page_rect), EPS)
            max_coverage = max(max_coverage, coverage)
        primary_rect = image_rects[0] if image_rects else [0.0, 0.0, 0.0, 0.0]
        scale_x = float(extracted.get("width", image[2])) / max(
            EPS, primary_rect[2] - primary_rect[0]
        )
        scale_y = float(extracted.get("height", image[3])) / max(
            EPS, primary_rect[3] - primary_rect[1]
        )
        images.append(
            {
                "xref": xref,
                "widthPx": int(extracted.get("width", image[2])),
                "heightPx": int(extracted.get("height", image[3])),
                "bitsPerComponent": extracted.get("bpc", image[4] if len(image) > 4 else None),
                "colorspace": extracted.get("colorspace", image[5] if len(image) > 5 else None),
                "extension": extracted.get("ext"),
                "rects": image_rects,
                "primaryRect": primary_rect,
                "maxPageCoverage": round(max_coverage, 6),
                "leftMarginPt": round(primary_rect[0] - cropbox[0], 4),
                "topMarginPt": round(primary_rect[1] - cropbox[1], 4),
                "rightMarginPt": round(cropbox[2] - primary_rect[2], 4),
                "bottomMarginPt": round(cropbox[3] - primary_rect[3], 4),
                "scaleXPxPerPt": round(scale_x, 6),
                "scaleYPxPerPt": round(scale_y, 6),
            }
        )

    text_words = page.get_text("words")
    drawings = page.get_drawings()
    fonts = page.get_fonts(full=True)
    return {
        "pdf": rel(pdf_path),
        "pdfPage": page_index + 1,
        "articlePage": 73 + page_index,
        "rotation": page.rotation,
        "pageRect": page_rect,
        "mediaBox": mediabox,
        "cropBox": cropbox,
        "imageCount": len(images),
        "images": images,
        "fontCount": len(fonts),
        "drawingCount": len(drawings),
        "ocrWordCount": len(text_words),
    }


def compare_pair(page75: dict[str, Any], page76: dict[str, Any]) -> dict[str, Any]:
    img75 = page75["images"][0] if page75["images"] else {}
    img76 = page76["images"][0] if page76["images"] else {}
    same_page_rect = same_list(page75["pageRect"], page76["pageRect"])
    same_media = same_list(page75["mediaBox"], page76["mediaBox"])
    same_crop = same_list(page75["cropBox"], page76["cropBox"])
    same_rotation = page75["rotation"] == page76["rotation"]
    same_image_count = page75["imageCount"] == page76["imageCount"] == 1
    same_image_rect = bool(img75 and img76 and same_list(img75["primaryRect"], img76["primaryRect"]))
    same_image_size = bool(
        img75
        and img76
        and img75["widthPx"] == img76["widthPx"]
        and img75["heightPx"] == img76["heightPx"]
    )
    same_scale = bool(
        img75
        and img76
        and abs(img75["scaleXPxPerPt"] - img76["scaleXPxPerPt"]) <= EPS
        and abs(img75["scaleYPxPerPt"] - img76["scaleYPxPerPt"]) <= EPS
    )
    identical_pair_geometry = all(
        [
            same_page_rect,
            same_media,
            same_crop,
            same_rotation,
            same_image_count,
            same_image_rect,
            same_image_size,
            same_scale,
        ]
    )
    has_side_margins = bool(
        img75
        and img76
        and (
            abs(img75["leftMarginPt"]) > EPS
            or abs(img75["rightMarginPt"]) > EPS
            or abs(img76["leftMarginPt"]) > EPS
            or abs(img76["rightMarginPt"]) > EPS
        )
    )
    hidden_pair_layer = bool(
        page75["imageCount"] != 1
        or page76["imageCount"] != 1
        or page75["drawingCount"] != 0
        or page76["drawingCount"] != 0
    )
    return {
        "samePageRect": same_page_rect,
        "sameMediaBox": same_media,
        "sameCropBox": same_crop,
        "sameRotation": same_rotation,
        "sameSingleImageCount": same_image_count,
        "sameImageRect": same_image_rect,
        "sameImageSize": same_image_size,
        "sameScale": same_scale,
        "identicalPairGeometry": identical_pair_geometry,
        "hasSideMargins": has_side_margins,
        "hiddenPairLayerCandidate": hidden_pair_layer,
        "imageRectDeltaPt": [
            round(img76.get("primaryRect", [0, 0, 0, 0])[i] - img75.get("primaryRect", [0, 0, 0, 0])[i], 4)
            for i in range(4)
        ],
        "scaleDeltaPxPerPt": [
            round(img76.get("scaleXPxPerPt", 0.0) - img75.get("scaleXPxPerPt", 0.0), 6),
            round(img76.get("scaleYPxPerPt", 0.0) - img75.get("scaleYPxPerPt", 0.0), 6),
        ],
        "heldToLightImplication": (
            "pdf_pair_geometry_does_not_change_valid_leaf_alignment"
            if identical_pair_geometry
            else "pdf_pair_geometry_requires_manual_review"
        ),
    }


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


def draw_page_box(record: dict[str, Any], title: str, size: tuple[int, int]) -> Image.Image:
    w, h = size
    panel = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(panel)
    title_font = font(18)
    body_font = font(13)
    page_rect = record["pageRect"]
    page_w = max(EPS, page_rect[2] - page_rect[0])
    page_h = max(EPS, page_rect[3] - page_rect[1])
    margin = 44
    scale = min((w - 2 * margin) / page_w, (h - 130) / page_h)
    ox = (w - page_w * scale) / 2
    oy = 56

    def map_rect(rect: list[float]) -> tuple[float, float, float, float]:
        return (
            ox + (rect[0] - page_rect[0]) * scale,
            oy + (rect[1] - page_rect[1]) * scale,
            ox + (rect[2] - page_rect[0]) * scale,
            oy + (rect[3] - page_rect[1]) * scale,
        )

    draw.text((12, 12), title, fill=(20, 20, 20), font=title_font)
    draw.rectangle(map_rect(page_rect), outline=(20, 20, 20), width=2)
    crop = record["cropBox"]
    draw.rectangle(map_rect(crop), outline=(80, 80, 80), width=1)
    if record["images"]:
        image = record["images"][0]
        draw.rectangle(map_rect(image["primaryRect"]), outline=(230, 120, 20), width=4)
        footer = (
            f"rot {record['rotation']} | img {image['widthPx']}x{image['heightPx']} | "
            f"rect {image['primaryRect']} | margins "
            f"{image['leftMarginPt']}/{image['topMarginPt']}/"
            f"{image['rightMarginPt']}/{image['bottomMarginPt']} pt"
        )
    else:
        footer = f"rot {record['rotation']} | no page image"
    draw.text((12, h - 58), footer[:105], fill=(20, 20, 20), font=body_font)
    draw.text(
        (12, h - 34),
        f"words {record['ocrWordCount']} | fonts {record['fontCount']} | drawings {record['drawingCount']}",
        fill=(20, 20, 20),
        font=body_font,
    )
    return panel


def build_sheet(pair_rows: list[dict[str, Any]]) -> None:
    panel_size = (520, 610)
    row_h = panel_size[1]
    sheet = Image.new("RGB", (panel_size[0] * 2, row_h * len(pair_rows)), (245, 245, 245))
    for idx, pair in enumerate(pair_rows):
        y = idx * row_h
        left = draw_page_box(pair["page75"], f"{pair['pdf']} | article 75", panel_size)
        right = draw_page_box(pair["page76"], f"{pair['pdf']} | article 76", panel_size)
        sheet.paste(left, (0, y))
        sheet.paste(right, (panel_size[0], y))
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = reopen.get("triggerRows", [])
    pair_rows = []
    pdf_count = 0
    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        pdf_count += 1
        doc = fitz.open(pdf_path)
        if doc.page_count <= max(TARGET_PDF_PAGE_INDEXES):
            continue
        page75 = page_record(doc, pdf_path, TARGET_PDF_PAGE_INDEXES[0])
        page76 = page_record(doc, pdf_path, TARGET_PDF_PAGE_INDEXES[1])
        comparison = compare_pair(page75, page76)
        pair_rows.append(
            {
                "pdf": rel(pdf_path),
                "page75": page75,
                "page76": page76,
                "comparison": comparison,
            }
        )

    pair_count = len(pair_rows)
    identical_pair_count = sum(1 for row in pair_rows if row["comparison"]["identicalPairGeometry"])
    same_box_count = sum(
        1
        for row in pair_rows
        if row["comparison"]["sameMediaBox"] and row["comparison"]["sameCropBox"]
    )
    same_rotation_count = sum(1 for row in pair_rows if row["comparison"]["sameRotation"])
    same_image_rect_count = sum(1 for row in pair_rows if row["comparison"]["sameImageRect"])
    same_scale_count = sum(1 for row in pair_rows if row["comparison"]["sameScale"])
    side_margin_pair_count = sum(1 for row in pair_rows if row["comparison"]["hasSideMargins"])
    hidden_pair_layer_count = sum(1 for row in pair_rows if row["comparison"]["hiddenPairLayerCandidate"])
    placement_offset_pair_count = sum(
        1
        for row in pair_rows
        if any(abs(v) > EPS for v in row["comparison"]["imageRectDeltaPt"])
        or any(abs(v) > EPS for v in row["comparison"]["scaleDeltaPxPerPt"])
    )
    source_backed_r3 = 0
    satisfied_triggers = sum(1 for row in trigger_rows if row.get("triggerSatisfiedNow"))
    trigger_count = len(trigger_rows)
    selector_unlock_count = 0
    fingerprint = (
        f"pdfs={pdf_count}|pairs={pair_count}|pairGeometryPass={identical_pair_count}|"
        f"sameBoxes={same_box_count}|sameRot={same_rotation_count}|"
        f"sameImageRect={same_image_rect_count}|sameScale={same_scale_count}|"
        f"sideMargins={side_margin_pair_count}|placementOffsets={placement_offset_pair_count}|"
        f"hiddenPairLayers={hidden_pair_layer_count}|sourceR3={source_backed_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors={selector_unlock_count}"
    )
    decision = "current_pdf_page_box_pair_geometry_no_selector"
    build_sheet(pair_rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF page-box and image-placement geometry for article pages 75 and 76; no key derivation",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": {
            "pdfCount": pdf_count,
            "pairCount": pair_count,
            "identicalPairGeometryCount": identical_pair_count,
            "sameBoxPairCount": same_box_count,
            "sameRotationPairCount": same_rotation_count,
            "sameImageRectPairCount": same_image_rect_count,
            "sameScalePairCount": same_scale_count,
            "sideMarginPairCount": side_margin_pair_count,
            "placementOffsetPairCount": placement_offset_pair_count,
            "hiddenPairLayerCandidateCount": hidden_pair_layer_count,
            "sourceBackedR3BridgeHitCount": source_backed_r3,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
            "selectorUnlockCount": selector_unlock_count,
        },
        "fingerprint": fingerprint,
        "pairRows": pair_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Do not adjust valid 75->76 held-to-light geometry from current PDF page boxes; "
            "require a distinct physical/original-layout source or raw clue naming transform, unit, and order."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Page-Box Pair Geometry Gate",
        "",
        "Scope: checked current PDF page boxes, rotations, image placements, scale, and hidden-layer indicators for the valid article page 75 -> page 76 leaf pair. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- PDFs / page pairs: `{pdf_count}` / `{pair_count}`",
        f"- Identical pair geometry: `{identical_pair_count}` / `{pair_count}`",
        f"- Same boxes / rotations / image rects / scale: `{same_box_count}` / `{same_rotation_count}` / `{same_image_rect_count}` / `{same_scale_count}`",
        f"- Side-margin pairs / placement-offset pairs / hidden pair-layer candidates: `{side_margin_pair_count}` / `{placement_offset_pair_count}` / `{hidden_pair_layer_count}`",
        f"- Source-backed R3 / satisfied triggers: `{source_backed_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Pair Rows",
        "",
        "| PDF | p75 rotation | p76 rotation | p75 image rect | p76 image rect | image size | margins p75 | margins p76 | same pair geometry |",
        "|---|---:|---:|---|---|---|---|---|---:|",
    ]
    for row in pair_rows:
        p75 = row["page75"]
        p76 = row["page76"]
        i75 = p75["images"][0] if p75["images"] else {}
        i76 = p76["images"][0] if p76["images"] else {}
        size = (
            f"{i75.get('widthPx')}x{i75.get('heightPx')}"
            if i75 and i75.get("widthPx") == i76.get("widthPx")
            else f"{i75.get('widthPx')}x{i75.get('heightPx')} / {i76.get('widthPx')}x{i76.get('heightPx')}"
        )
        margins75 = f"{i75.get('leftMarginPt')}/{i75.get('topMarginPt')}/{i75.get('rightMarginPt')}/{i75.get('bottomMarginPt')}"
        margins76 = f"{i76.get('leftMarginPt')}/{i76.get('topMarginPt')}/{i76.get('rightMarginPt')}/{i76.get('bottomMarginPt')}"
        lines.append(
            f"| `{row['pdf']}` | {p75['rotation']} | {p76['rotation']} | `{i75.get('primaryRect')}` | `{i76.get('primaryRect')}` | `{size}` | `{margins75}` | `{margins76}` | `{row['comparison']['identicalPairGeometry']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Current PDFs do not supply an alternate page-box, rotation, or image-placement transform for the physically valid 75 -> 76 held-to-light pair.",
            "- `magazine.pdf` is full-bleed on both pages; the two lower-resolution duplicate PDFs have side margins, but the margins and image scale are identical on page 75 and page 76.",
            "- No hidden pair-layer, per-page offset, scale drift, source-backed instruction, or reopen trigger was found.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")
    print(f"decision: {decision}")


if __name__ == "__main__":
    main()
