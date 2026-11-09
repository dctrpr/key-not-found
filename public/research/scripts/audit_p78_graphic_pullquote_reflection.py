#!/usr/bin/env python3
"""Audit the page-78 graphic pull-quote as a visual layer.

The line "The economy of love is infinitely more efficient than hate and war"
appears twice: once as body/pull-quote text and once inside the lower p78
brush graphic. The graphic text is outside the 3D map's exact text layer, so
this pass treats it as visual geometry and checks what it hits on page 76 under
literal horizontal mirroring.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from extract_visual_masks import connected_components
from highres_reflection_extract import orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_MD = OUT_DIR / "p78_graphic_pullquote_reflection.md"
OUT_JSON = OUT_DIR / "p78_graphic_pullquote_reflection.json"
OVERLAY = OUT_DIR / "p78_graphic_pullquote_reflected_on_p76.jpg"
CROP = OUT_DIR / "p78_graphic_pullquote_crop.jpg"

GREY_JSON = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"

# Tight enough to exclude ordinary p78 body lines; broad enough to keep the
# surrounding X marks and brush/caption graphic.
P78_GRAPHIC_ROI = (150, 2380, 1350, 3150)
GRAPHIC_TEXT = "The economy of love is infinitely more efficient than hate and war."


def box_area(box: tuple[int | float, int | float, int | float, int | float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_box(a, b) -> tuple[float, tuple[float, float, float, float]]:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = (x1, y1, x2, y2)
    return box_area(inter), inter


def hflip_box(box, width: int) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def font(size: int):
    for name in ("Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def detect_graphic_mask(img: Image.Image) -> tuple[np.ndarray, tuple[int, int, int, int], list[dict]]:
    rgb = np.asarray(img.convert("RGB"))
    gray = rgb.mean(axis=2)
    roi = P78_GRAPHIC_ROI
    x1, y1, x2, y2 = roi
    roi_mask = gray[y1:y2, x1:x2] < 105
    comps = connected_components(roi_mask, min_area=150)
    # Ignore any accidental page-edge/speck components. The real graphic pieces
    # are inside the lower-left picture area.
    kept = []
    for comp in comps:
        bx1, by1, bx2, by2 = comp["box"]
        w = bx2 - bx1
        h = by2 - by1
        if w < 8 or h < 8:
            continue
        kept.append(
            {
                **comp,
                "box": (bx1 + x1, by1 + y1, bx2 + x1, by2 + y1),
                "center": (comp["center"][0] + x1, comp["center"][1] + y1),
            }
        )
    if not kept:
        raise RuntimeError("no graphic components found")
    union = (
        min(c["box"][0] for c in kept),
        min(c["box"][1] for c in kept),
        max(c["box"][2] for c in kept),
        max(c["box"][3] for c in kept),
    )
    full = np.zeros(gray.shape, dtype=bool)
    for comp in kept:
        bx1, by1, bx2, by2 = comp["box"]
        # Preserve actual dark pixels rather than filling the component bbox.
        full[by1:by2, bx1:bx2] |= gray[by1:by2, bx1:bx2] < 105
    # Restrict to the union to avoid unrelated dark dust in the ROI.
    restricted = np.zeros_like(full)
    ux1, uy1, ux2, uy2 = union
    restricted[uy1:uy2, ux1:ux2] = full[uy1:uy2, ux1:ux2]
    return restricted, union, kept


def p76_boxes() -> list[dict]:
    rows = []
    for idx, box in enumerate(orange_boxes(76)[0], 1):
        labels = {
            1: "Get some toxicity... Open your heart",
            2: "Bitcoin",
            3: "by the rancid catnip of fiat money",
            4: "buying the dip",
            5: "shitcoiner at heart",
        }
        rows.append({"id": f"p76_orange_{idx}", "kind": "orange", "label": labels.get(idx, ""), "box": box})
    grey = json.loads(GREY_JSON.read_text())
    for row in grey["rows"]:
        if row["page"] != 76:
            continue
        rows.append(
            {
                "id": row["id"],
                "kind": "grey",
                "label": row["expected"],
                "box": tuple(round(v) for v in row["highresBox"]),
            }
        )
    return rows


def mask_overlap(mask: np.ndarray, box) -> tuple[int, float]:
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    x1 = max(0, min(mask.shape[1], x1))
    x2 = max(0, min(mask.shape[1], x2))
    y1 = max(0, min(mask.shape[0], y1))
    y2 = max(0, min(mask.shape[0], y2))
    area = max(1, (x2 - x1) * (y2 - y1))
    count = int(mask[y1:y2, x1:x2].sum())
    return count, round(count / area, 6)


def draw_overlay(p76: Image.Image, p78: Image.Image, graphic_mask, graphic_box, reflected_mask, reflected_box, intersections):
    out = p76.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    arr = np.zeros((out.height, out.width, 4), dtype=np.uint8)
    arr[reflected_mask] = [0, 120, 255, 110]
    overlay = Image.fromarray(arr, "RGBA")
    out = Image.alpha_composite(out, overlay)
    draw = ImageDraw.Draw(out)
    label_font = font(28)
    draw.rectangle(reflected_box, outline=(0, 90, 255, 255), width=6)
    draw.text((reflected_box[0], max(0, reflected_box[1] - 36)), "p78 graphic hflip -> p76", fill=(0, 90, 255, 255), font=label_font)
    for row in p76_boxes():
        color = (255, 120, 0, 255) if row["kind"] == "orange" else (20, 20, 20, 255)
        draw.rectangle(row["box"], outline=color, width=4)
        draw.text((row["box"][0], max(0, row["box"][1] - 30)), row["id"], fill=color, font=label_font)
    for hit in intersections:
        if hit["bboxOverlapArea"] > 0:
            draw.rectangle(hit["intersectionBox"], outline=(255, 0, 180, 255), width=4)
    out.convert("RGB").save(OVERLAY, quality=94)

    x1, y1, x2, y2 = graphic_box
    crop = p78.crop((max(0, x1 - 40), max(0, y1 - 40), min(p78.width, x2 + 40), min(p78.height, y2 + 40)))
    crop.save(CROP, quality=94)


def main() -> None:
    p78 = upright_image(78).convert("RGB")
    p76 = upright_image(76).convert("RGB")
    graphic_mask, graphic_box, comps = detect_graphic_mask(p78)
    reflected_mask = np.fliplr(graphic_mask)
    reflected_box = hflip_box(graphic_box, p78.width)

    intersections = []
    for row in p76_boxes():
        area, inter = overlap_box(reflected_box, row["box"])
        pixels, density = mask_overlap(reflected_mask, row["box"])
        intersections.append(
            {
                **row,
                "box": [int(v) for v in row["box"]],
                "bboxOverlapArea": round(area, 2),
                "bboxOverlapVsTarget": round(area / max(1.0, box_area(row["box"])), 6),
                "reflectedMaskPixelsInsideTarget": pixels,
                "reflectedMaskDensityInsideTarget": density,
                "intersectionBox": [round(v, 2) for v in inter],
            }
        )

    meaningful = [
        item
        for item in intersections
        if item["bboxOverlapArea"] > 0 or item["reflectedMaskPixelsInsideTarget"] > 0
    ]
    draw_overlay(p76, p78, graphic_mask, graphic_box, reflected_mask, reflected_box, meaningful)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Manual visual-layer audit of p78 lower graphic pull-quote mirrored onto p76; no key derivation.",
        "graphicText": GRAPHIC_TEXT,
        "p78GraphicRoi": list(P78_GRAPHIC_ROI),
        "p78GraphicBox": list(map(int, graphic_box)),
        "p78GraphicComponentCount": len(comps),
        "reflectedBoxOnP76": list(map(int, reflected_box)),
        "overlay": str(OVERLAY),
        "crop": str(CROP),
        "intersections": intersections,
        "meaningfulIntersections": meaningful,
        "assessment": [
            "The p78 lower graphic is real scan-visible text outside the 3D map's article-body layer.",
            "Literal horizontal mirroring sends the graphic to the lower-right p76 art/corridor area.",
            "Under the current scan it does not create a narrow text-unit selector; it is a provenance/orientation layer unless a physical/source transform changes the overlap.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# P78 Graphic Pull-Quote Reflection Audit",
        "",
        "Scope: treat the lower page-78 brush/pull-quote as scan-visible graphic text outside the 3D map text layer, then mirror it onto page 76. No key derivation was run.",
        "",
        f"- Graphic text: `{GRAPHIC_TEXT}`",
        f"- p78 graphic box: `{result['p78GraphicBox']}`",
        f"- reflected p76 box: `{result['reflectedBoxOnP76']}`",
        f"- component count: `{len(comps)}`",
        f"- crop: `{CROP}`",
        f"- overlay: `{OVERLAY}`",
        "",
        "## Intersections With Page-76 Highlight Units",
        "",
    ]
    for item in meaningful:
        lines.append(
            f"- `{item['id']}` {item['kind']} `{item['label']}`: "
            f"bboxOverlapVsTarget=`{item['bboxOverlapVsTarget']}`, "
            f"maskPixels=`{item['reflectedMaskPixelsInsideTarget']}`, "
            f"maskDensity=`{item['reflectedMaskDensityInsideTarget']}`"
        )
    if not meaningful:
        lines.append("- No intersections.")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- This confirms a missing visual/text layer: the lower p78 graphic repeats the `economy of love... hate and war` line, but it is not captured as exact 3D-map article text.",
            "- Mirroring the graphic's dark pixels onto p76 puts them over the lower-right page-76 art/corridor zone, not into a clean single word/letter target.",
            "- The strongest overlap is broad-area context, not a precise selector. Keep this as orientation/provenance evidence tied to the `FUCK`/X/brush system unless a physical scan or explicit rule says how to use the graphic.",
            "- Next best move: if the Canva `FUCK ALL SHITCOINS` alignment is reopened with higher-resolution evidence, include this p78 graphic layer as a first-class visual object rather than treating it as normal article text.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(OUT_MD)
    print(OUT_JSON)
    print(OVERLAY)


if __name__ == "__main__":
    main()
