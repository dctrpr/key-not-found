#!/usr/bin/env python3
"""Broad non-font visual-order audit around the 76/79 color-inversion anchor.

The previous calibrated-anchor pass focused on the core line crop. This script
checks the entire horizontal band around that anchor, including margins that
were outside the earlier crop, after masking article text and known highlight
boxes. It asks whether any remaining marks provide an ordering cue.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from analyze_highres_page76_mirror_selector import hflip_box, intersection
from analyze_registered_76_79_selector import BEST_TRANSFORM, transform_box
from build_registration_rotation_scale_sweep import transform_image
from build_registration_workbench import feature_mask, load_page
from extract_visual_masks import connected_components, dilate, merge_close_boxes


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REGISTERED = ROOT / "analysis_outputs/source_audit/registered_76_79_selector.json"
OUT_MD = ROOT / "analysis_outputs/source_audit/anchor_margin_visual_order_audit.md"
OUT_JSON = ROOT / "analysis_outputs/source_audit/anchor_margin_visual_order_audit.json"
OUT_IMG = ROOT / "analysis_outputs/source_audit/anchor_margin_visual_order_audit.jpg"
OUT_CROP = ROOT / "analysis_outputs/source_audit/anchor_margin_visual_order_full_band.jpg"

PAGE_W = 2544
PAGE_H = 3264
BAND = (0, 560, PAGE_W, 1280)
PREVIOUS_CORE_CROP = (350, 650, 2200, 1050)
TEXT_PAD = 10
HIGHLIGHT_PAD = 18


def area(box) -> float:
    if box is None:
        return 0.0
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap(a, b) -> float:
    return area(intersection(a, b))


def expand_box(box, pad: int) -> tuple[int, int, int, int]:
    return (
        max(0, int(round(box[0] - pad))),
        max(0, int(round(box[1] - pad))),
        min(PAGE_W, int(round(box[2] + pad))),
        min(PAGE_H, int(round(box[3] + pad))),
    )


def draw_box(mask: np.ndarray, box, pad: int = 0, value: bool = True) -> None:
    x1, y1, x2, y2 = expand_box(box, pad)
    mask[y1:y2, x1:x2] = value


def crop_mask(mask: np.ndarray, crop=BAND) -> np.ndarray:
    x1, y1, x2, y2 = crop
    return mask[y1:y2, x1:x2]


def words_for_page(article_map: dict, page: int) -> list[dict]:
    for row in article_map["pages"]:
        if row["page"] == page:
            return row.get("words", [])
    raise ValueError(page)


def text_mask(article_map: dict, page: int, *, transformed_from_p79: bool = False) -> np.ndarray:
    mask = np.zeros((PAGE_H, PAGE_W), dtype=bool)
    for word in words_for_page(article_map, page):
        box = word["box"]
        if transformed_from_p79:
            box = transform_box(hflip_box(box, PAGE_W), PAGE_W, PAGE_H, BEST_TRANSFORM)
        draw_box(mask, box, TEXT_PAD, True)
    return mask


def highlight_mask(registered: dict, *, side: str) -> np.ndarray:
    mask = np.zeros((PAGE_H, PAGE_W), dtype=bool)
    if side == "p76":
        for item in registered["targetOrange"]:
            draw_box(mask, item["box"], HIGHLIGHT_PAD, True)
        for item in registered["targetGrey"]:
            draw_box(mask, item["box"], HIGHLIGHT_PAD, True)
    elif side == "p79_registered":
        for item in registered["registeredSources"]:
            draw_box(mask, item["mappedBox"], HIGHLIGHT_PAD, True)
    else:
        raise ValueError(side)
    return mask


def component_rows(mask: np.ndarray, *, min_area: int = 110) -> list[dict]:
    local = crop_mask(mask)
    comps = connected_components(local, min_area=min_area)
    boxes = merge_close_boxes(comps, y_gap=12, x_gap=18)
    rows = []
    for idx, box in enumerate(boxes, 1):
        x1, y1, x2, y2 = box
        page_box = [x1 + BAND[0], y1 + BAND[1], x2 + BAND[0], y2 + BAND[1]]
        w = x2 - x1
        h = y2 - y1
        center = [(page_box[0] + page_box[2]) / 2, (page_box[1] + page_box[3]) / 2]
        rows.append(
            {
                "index": idx,
                "boxPage": page_box,
                "area": int(local[y1:y2, x1:x2].sum()),
                "width": int(w),
                "height": int(h),
                "aspect": round(w / h, 3) if h else None,
                "center": [round(center[0], 1), round(center[1], 1)],
                "region": region_for(center[0], center[1]),
                "outsidePreviousCore": not bool(overlap(page_box, PREVIOUS_CORE_CROP)),
            }
        )
    rows.sort(key=lambda r: (r["boxPage"][1], r["boxPage"][0]))
    return rows


def region_for(x: float, y: float) -> str:
    if x < PREVIOUS_CORE_CROP[0]:
        return "left_margin"
    if x > PREVIOUS_CORE_CROP[2]:
        return "right_margin"
    if y < PREVIOUS_CORE_CROP[1]:
        return "above_core"
    if y > PREVIOUS_CORE_CROP[3]:
        return "below_core"
    return "core"


def summarize_regions(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for row in rows:
        stats = out.setdefault(row["region"], {"components": 0, "pixels": 0, "outsidePreviousCore": 0})
        stats["components"] += 1
        stats["pixels"] += row["area"]
        stats["outsidePreviousCore"] += int(row["outsidePreviousCore"])
    return out


def make_preview(base: Image.Image, overlay: Image.Image, base_marks: np.ndarray, overlay_marks: np.ndarray, registered: dict) -> None:
    x1, y1, x2, y2 = BAND
    band_blend = Image.blend(base.crop(BAND), overlay.crop(BAND), 0.42).convert("RGB")
    rgb = np.asarray(band_blend).copy()
    bm = crop_mask(base_marks)
    om = crop_mask(overlay_marks)
    rgb[bm] = [0, 80, 255]
    rgb[om] = [255, 115, 0]
    rgb[bm & om] = [255, 0, 190]
    out = Image.fromarray(rgb)
    draw = ImageDraw.Draw(out)

    # Previous core crop boundary.
    cx1, cy1, cx2, cy2 = PREVIOUS_CORE_CROP
    draw.rectangle((cx1 - x1, cy1 - y1, cx2 - x1, cy2 - y1), outline=(20, 20, 20), width=4)
    draw.text((12, 14), "Full anchor band: blue=p76 residual, orange=registered p79 residual, magenta=overlap", fill=(0, 0, 0))
    draw.text((cx1 - x1 + 10, cy1 - y1 + 10), "previous core crop", fill=(0, 0, 0))

    for item in registered["targetGrey"]:
        if item["index"] in {1, 2}:
            box = item["box"]
            draw.rectangle((box[0] - x1, box[1] - y1, box[2] - x1, box[3] - y1), outline=(0, 210, 255), width=3)
    for item in registered["registeredSources"]:
        if item["index"] == 1:
            box = item["mappedBox"]
            draw.rectangle((box[0] - x1, box[1] - y1, box[2] - x1, box[3] - y1), outline=(190, 0, 255), width=3)

    out.save(OUT_CROP, quality=94)
    scaled = out.resize((out.width, int(out.height * 1.0)), Image.Resampling.LANCZOS)
    scaled.save(OUT_IMG, quality=94)


def main() -> None:
    article_map = json.loads(ARTICLE_MAP.read_text())
    registered = json.loads(REGISTERED.read_text())
    base = load_page(76)
    overlay_raw = load_page(79).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    overlay = transform_image(
        overlay_raw,
        BEST_TRANSFORM["dx"],
        BEST_TRANSFORM["dy"],
        BEST_TRANSFORM["angleDeg"],
        BEST_TRANSFORM["scale"],
    )

    base_features = dilate(feature_mask(base), 3)
    overlay_features = dilate(feature_mask(overlay), 3)

    base_remove = text_mask(article_map, 76) | highlight_mask(registered, side="p76")
    overlay_remove = text_mask(article_map, 79, transformed_from_p79=True) | highlight_mask(registered, side="p79_registered")

    base_marks = base_features & ~base_remove
    overlay_marks = overlay_features & ~overlay_remove

    base_rows = component_rows(base_marks)
    overlay_rows = component_rows(overlay_marks)
    overlap_pixels = int((crop_mask(base_marks) & crop_mask(overlay_marks)).sum())
    outside_overlap_pixels = 0
    outside = np.ones(crop_mask(base_marks).shape, dtype=bool)
    px1, py1, px2, py2 = PREVIOUS_CORE_CROP
    bx1, by1, bx2, by2 = BAND
    outside[py1 - by1 : py2 - by1, px1 - bx1 : px2 - bx1] = False
    outside_overlap_pixels = int(((crop_mask(base_marks) & crop_mask(overlay_marks)) & outside).sum())

    make_preview(base, overlay, base_marks, overlay_marks, registered)

    result = {
        "scope": "full horizontal band around p79-yellow -> p76-black color-inversion anchor",
        "band": BAND,
        "previousCoreCrop": PREVIOUS_CORE_CROP,
        "transform": BEST_TRANSFORM,
        "preview": str(OUT_IMG),
        "fullBandPreview": str(OUT_CROP),
        "stats": {
            "p76ResidualPixels": int(crop_mask(base_marks).sum()),
            "registeredP79ResidualPixels": int(crop_mask(overlay_marks).sum()),
            "overlapPixels": overlap_pixels,
            "outsidePreviousCoreOverlapPixels": outside_overlap_pixels,
            "p76Components": len(base_rows),
            "registeredP79Components": len(overlay_rows),
            "p76RegionSummary": summarize_regions(base_rows),
            "registeredP79RegionSummary": summarize_regions(overlay_rows),
        },
        "p76Components": base_rows[:60],
        "registeredP79Components": overlay_rows[:60],
        "assessment": [
            "The broader band reveals extra components outside the earlier core crop, but they are margin/page furniture, scan edges, or transformed source-page residue.",
            "No repeated dots, arrows, pills, X marks, wire knots, or aligned component sequence appears adjacent to the p79-yellow -> p76-black anchor.",
            "The color-inversion anchor remains a registration/orientation clue, not a local visual ordering rule.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Anchor Margin Visual-Order Audit",
        "",
        "Scope: inspect the full horizontal band around the p79-yellow -> p76-black color-inversion anchor, including margins outside the previous core crop. Article text boxes and known highlight boxes are masked before component detection. No key derivation is run.",
        "",
        f"- Band: `{BAND}`",
        f"- Previous core crop: `{PREVIOUS_CORE_CROP}`",
        f"- Preview: `{OUT_IMG}`",
        "",
        "## Stats",
        "",
        f"- p76 residual pixels in band: `{result['stats']['p76ResidualPixels']}` across `{result['stats']['p76Components']}` components",
        f"- registered p79 residual pixels in band: `{result['stats']['registeredP79ResidualPixels']}` across `{result['stats']['registeredP79Components']}` components",
        f"- overlap pixels after masking: `{overlap_pixels}`",
        f"- overlap pixels outside previous core crop: `{outside_overlap_pixels}`",
        "",
        "## Region Summary",
        "",
        "- p76:",
    ]
    for region, stats in sorted(result["stats"]["p76RegionSummary"].items()):
        md.append(f"  - `{region}`: components={stats['components']} pixels={stats['pixels']} outsideCore={stats['outsidePreviousCore']}")
    md.append("- registered p79:")
    for region, stats in sorted(result["stats"]["registeredP79RegionSummary"].items()):
        md.append(f"  - `{region}`: components={stats['components']} pixels={stats['pixels']} outsideCore={stats['outsidePreviousCore']}")

    md.extend(["", "## Largest Components Outside Previous Core", "", "- p76:"])
    for row in sorted([r for r in base_rows if r["outsidePreviousCore"]], key=lambda r: r["area"], reverse=True)[:10]:
        md.append(
            f"  - region={row['region']} area={row['area']} box={row['boxPage']} size={row['width']}x{row['height']} aspect={row['aspect']}"
        )
    md.append("- registered p79:")
    for row in sorted([r for r in overlay_rows if r["outsidePreviousCore"]], key=lambda r: r["area"], reverse=True)[:10]:
        md.append(
            f"  - region={row['region']} area={row['area']} box={row['boxPage']} size={row['width']}x{row['height']} aspect={row['aspect']}"
        )

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The broader band does add margin components that the earlier crop could not see, but they behave like publication/page furniture, scan-edge residue, or transformed source-page residue.",
            "- There is no clear repeated non-font ordering system: no usable dot count, pill count, X sequence, wire-knot sequence, arrow, or one-to-one component alignment appears around the color-inversion anchor.",
            "- Close this as a local visual-order selector under the current high-res transform.",
            "- Next best move: either inspect lower page-76 visual marks as a separate system, or pause geometry until a better physical/source scan gives new evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"wrote {OUT_CROP}")


if __name__ == "__main__":
    main()
