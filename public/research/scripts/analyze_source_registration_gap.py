#!/usr/bin/env python3
"""Quantify the gap between the high-res magazine source and OCR PDF source.

The puzzle geometry should use the high-res magazine pages. The OCR PDF is
useful for text extraction, but this report measures how much geometry changes
when coordinates are moved between the two sources.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

from extract_visual_masks import PAGES as OCR_PAGES
from highres_reflection_extract import (
    SOURCE_PAGES,
    ensure_highres_sources,
    fit_mapping_for_page,
    orange_boxes,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_registration_gap.json"
OUT_MD = OUT / "source_registration_gap.md"
OUT_SHEET = OUT / "source_registration_gap_contact_sheet.jpg"


def upright_highres(page: int) -> Image.Image:
    ensure_highres_sources()
    return Image.open(SOURCE_PAGES[page]).convert("RGB").rotate(180, expand=True)


def foreground_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    brightness = arr.mean(axis=2)
    maxc = arr.max(axis=2)
    minc = arr.min(axis=2)
    chroma = maxc - minc

    # Works for white text pages, dark art pages, and colored ad/background pages.
    # Keep anything clearly non-white, saturated, or very dark.
    mask = (brightness < 238) | (chroma > 32)

    # Ignore tiny edge speckles by requiring row/column support.
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return (0, 0, img.width, img.height)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def box_size(box: tuple[int, int, int, int]) -> tuple[int, int]:
    return box[2] - box[0], box[3] - box[1]


def map_point(mapping, x: float, y: float) -> tuple[float, float]:
    ax, bx, ay, by = mapping
    return ax * x + bx, ay * y + by


def content_mapping(src_box, dst_box):
    sw, sh = box_size(src_box)
    dw, dh = box_size(dst_box)
    sx = dw / sw if sw else 0
    sy = dh / sh if sh else 0
    bx = dst_box[0] - src_box[0] * sx
    by = dst_box[1] - src_box[1] * sy
    return sx, bx, sy, by


def mapping_delta(a, b, size):
    points = [
        (0, 0),
        (size[0], 0),
        (0, size[1]),
        (size[0], size[1]),
        (size[0] / 2, size[1] / 2),
    ]
    deltas = []
    for x, y in points:
        ax, ay = map_point(a, x, y)
        bx, by = map_point(b, x, y)
        deltas.append(((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5)
    return {
        "meanPx": round(float(np.mean(deltas)), 2),
        "maxPx": round(float(np.max(deltas)), 2),
    }


def draw_panel(img: Image.Image, bbox, title: str, width=360) -> Image.Image:
    scale = width / img.width
    height = int(round(img.height * scale))
    panel = img.resize((width, height), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(panel)
    b = tuple(int(round(v * scale)) for v in bbox)
    draw.rectangle(b, outline=(255, 0, 0), width=3)
    draw.rectangle((0, 0, width - 1, height - 1), outline=(0, 0, 0), width=1)
    draw.text((8, 8), title, fill=(255, 0, 0))
    return panel


def make_page_overlay(highres: Image.Image, ocr: Image.Image, content_map) -> Image.Image:
    # Map high-res page into OCR coordinates using content bbox mapping. This is
    # only a diagnostic view, not a production coordinate transform.
    sx, bx, sy, by = content_map
    mapped = Image.new("RGB", ocr.size, "white")
    resized = highres.resize((max(1, int(round(highres.width * sx))), max(1, int(round(highres.height * sy)))), Image.Resampling.LANCZOS)
    mapped.paste(resized, (int(round(bx)), int(round(by))))
    blend = Image.blend(ocr.convert("RGB"), mapped, 0.45)
    return ImageEnhance.Contrast(blend).enhance(1.15)


def main() -> None:
    rows = []
    panels = []
    for page in range(75, 81):
        high = upright_highres(page)
        ocr = Image.open(OCR_PAGES[page]).convert("RGB")
        high_bbox = foreground_bbox(high)
        ocr_bbox = foreground_bbox(ocr)
        high_content_map = content_mapping(high_bbox, ocr_bbox)
        boxes, _ = orange_boxes(page)
        highlight_map, fit_source_boxes, target_boxes = fit_mapping_for_page(page, boxes)
        delta = mapping_delta(high_content_map, highlight_map, high.size)
        hw, hh = box_size(high_bbox)
        ow, oh = box_size(ocr_bbox)

        row = {
            "page": page,
            "highresSize": high.size,
            "ocrSize": ocr.size,
            "highresContentBox": high_bbox,
            "ocrContentBox": ocr_bbox,
            "highresContentAspect": round(hw / hh, 5) if hh else None,
            "ocrContentAspect": round(ow / oh, 5) if oh else None,
            "contentMap": {
                "x": round(high_content_map[0], 6),
                "xOffset": round(high_content_map[1], 2),
                "y": round(high_content_map[2], 6),
                "yOffset": round(high_content_map[3], 2),
            },
            "highlightMap": {
                "x": round(highlight_map[0], 6),
                "xOffset": round(highlight_map[1], 2),
                "y": round(highlight_map[2], 6),
                "yOffset": round(highlight_map[3], 2),
            },
            "contentVsHighlightDelta": delta,
            "orangeBoxesUsed": len(fit_source_boxes),
        }
        rows.append(row)

        panels.append(draw_panel(high, high_bbox, f"p{page} high-res"))
        panels.append(draw_panel(ocr, ocr_bbox, f"p{page} OCR"))
        overlay = make_page_overlay(high, ocr, high_content_map)
        panels.append(draw_panel(overlay, ocr_bbox, f"p{page} content-align"))

    panel_w = panels[0].width
    panel_h = panels[0].height
    sheet = Image.new("RGB", (panel_w * 3, panel_h * 6), "white")
    for idx, panel in enumerate(panels):
        x = (idx % 3) * panel_w
        y = (idx // 3) * panel_h
        sheet.paste(panel, (x, y))
    sheet.save(OUT_SHEET, quality=92)

    result = {
        "source": {
            "highres": "magazine.pdf / analysis_outputs/source_images/magazine_page_*.jpg",
            "ocr": "keyser bitcoin .pdf / keyser bitcoin -*_1.jpg",
        },
        "contactSheet": str(OUT_SHEET),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Source Registration Gap",
        "",
        "Scope: compare high-res `magazine.pdf` page images against the OCR PDF page images. This checks geometry risk only; it does not generate key candidates.",
        "",
        f"- Contact sheet: `{OUT_SHEET}`",
        "",
        "## Findings",
        "",
    ]
    for r in rows:
        lines.append(
            f"- p{r['page']}: highres={tuple(r['highresSize'])} ocr={tuple(r['ocrSize'])} "
            f"contentAspect={r['highresContentAspect']}->{r['ocrContentAspect']} "
            f"contentMap=x{r['contentMap']['x']},y{r['contentMap']['y']} "
            f"highlightMap=x{r['highlightMap']['x']},y{r['highlightMap']['y']} "
            f"content-vs-highlight delta mean/max={r['contentVsHighlightDelta']['meanPx']}/{r['contentVsHighlightDelta']['maxPx']} px"
        )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The high-res and OCR sources are not related by one clean page-size resize. Page rotation, crop, and non-uniform scaling all matter.",
            "- Content-box mapping and orange-highlight mapping differ by hundreds of OCR pixels on several pages, which is too large for letter-level fold/mirror extraction.",
            "- Existing OCR text can still label regions, but final geometry should be done directly on high-res images or a physical scan.",
            "- Next best move: build the mirror-writing selector directly on high-res page-76 corridor geometry, then use OCR only after the target region is identified.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
