#!/usr/bin/env python3
"""Audit non-text visual marks near the calibrated 76/79 anchor."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from analyze_highres_page76_mirror_selector import area, hflip_box, intersection
from analyze_registered_76_79_selector import BEST_TRANSFORM, transform_box
from build_registration_rotation_scale_sweep import transform_image
from build_registration_workbench import feature_mask, load_page
from extract_visual_masks import connected_components, dilate, merge_close_boxes


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REGISTERED = ROOT / "analysis_outputs/source_audit/registered_76_79_selector.json"
CANVA = ROOT / "analysis_outputs/external_clues/canva_source_inspection.md"
OUT_MD = ROOT / "analysis_outputs/source_audit/calibrated_anchor_visual_marks.md"
OUT_JSON = ROOT / "analysis_outputs/source_audit/calibrated_anchor_visual_marks.json"
OUT_IMG = ROOT / "analysis_outputs/source_audit/calibrated_anchor_visual_marks.jpg"

PAGE_W = 2544
PAGE_H = 3264
CROP = (350, 650, 2200, 1050)
PAD = 8


def overlap_area(a, b) -> float:
    inter = intersection(a, b)
    return area(inter) if inter else 0.0


def expand_box(box, pad=PAD):
    return (
        max(0, int(round(box[0] - pad))),
        max(0, int(round(box[1] - pad))),
        min(PAGE_W, int(round(box[2] + pad))),
        min(PAGE_H, int(round(box[3] + pad))),
    )


def draw_box_on_mask(mask: np.ndarray, box, value: bool = True) -> None:
    x1, y1, x2, y2 = expand_box(box)
    mask[y1:y2, x1:x2] = value


def words_for_page(article_map: dict, page: int) -> list[dict]:
    for row in article_map["pages"]:
        if row["page"] == page:
            return row.get("words", [])
    raise ValueError(page)


def page_text_mask(article_map: dict, page: int, *, transformed_from_p79: bool = False) -> np.ndarray:
    mask = np.zeros((PAGE_H, PAGE_W), dtype=bool)
    for word in words_for_page(article_map, page):
        box = word["box"]
        if transformed_from_p79:
            box = transform_box(hflip_box(box, PAGE_W), PAGE_W, PAGE_H, BEST_TRANSFORM)
        draw_box_on_mask(mask, box, True)
    return mask


def known_anchor_mask(registered: dict) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    base_mask = np.zeros((PAGE_H, PAGE_W), dtype=bool)
    overlay_mask = np.zeros((PAGE_H, PAGE_W), dtype=bool)
    known = []
    for item in registered["targetGrey"]:
        if item["index"] in {1, 2}:
            draw_box_on_mask(base_mask, item["box"], True)
            known.append({"side": "p76", "label": f"B{item['index']} {item['label']}", "box": item["box"]})
    for item in registered["registeredSources"]:
        if item["index"] == 1:
            draw_box_on_mask(overlay_mask, item["mappedBox"], True)
            known.append({"side": "p79_registered", "label": item["label"], "box": item["mappedBox"]})
    return base_mask, overlay_mask, known


def crop_mask(mask: np.ndarray) -> np.ndarray:
    x1, y1, x2, y2 = CROP
    return mask[y1:y2, x1:x2]


def component_summary(mask: np.ndarray, *, min_area=120) -> list[dict]:
    comps = connected_components(mask, min_area=min_area)
    boxes = merge_close_boxes(comps, y_gap=10, x_gap=14)
    rows = []
    for idx, box in enumerate(boxes, 1):
        x1, y1, x2, y2 = box
        rows.append(
            {
                "index": idx,
                "boxLocal": [x1, y1, x2, y2],
                "boxPage": [x1 + CROP[0], y1 + CROP[1], x2 + CROP[0], y2 + CROP[1]],
                "area": int(mask[y1:y2, x1:x2].sum()),
                "width": int(x2 - x1),
                "height": int(y2 - y1),
            }
        )
    rows.sort(key=lambda r: (r["boxLocal"][1], r["boxLocal"][0]))
    return rows


def mask_stats(mask: np.ndarray) -> dict:
    return {"pixels": int(mask.sum()), "components": len(component_summary(mask))}


def make_preview(base_img: Image.Image, overlay_img: Image.Image, base_extra: np.ndarray, overlay_extra: np.ndarray, base_residual: np.ndarray, overlay_residual: np.ndarray) -> None:
    x1, y1, x2, y2 = CROP
    blend = Image.blend(base_img.crop(CROP), overlay_img.crop(CROP), 0.45).convert("RGB")
    rgb = np.array(blend)
    # Residual highlight/text-free marks: faint blue/orange. Extra after known anchor removal: strong.
    br = crop_mask(base_residual)
    orr = crop_mask(overlay_residual)
    be = crop_mask(base_extra)
    oe = crop_mask(overlay_extra)
    rgb[br] = (90, 130, 230)
    rgb[orr] = (240, 150, 50)
    rgb[br & orr] = (230, 50, 170)
    rgb[be] = (0, 70, 255)
    rgb[oe] = (255, 105, 0)
    rgb[be & oe] = (255, 0, 180)
    out = Image.fromarray(rgb)
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, x2 - x1 - 1, y2 - y1 - 1), outline=(20, 20, 20), width=2)
    draw.text((10, 10), "Blue=p76 residual, orange=registered p79 residual, magenta=overlap", fill=(0, 0, 0))
    out.save(OUT_IMG, quality=94)


def main() -> None:
    article_map = json.loads(ARTICLE_MAP.read_text())
    registered = json.loads(REGISTERED.read_text())
    base = load_page(76)
    overlay_raw = load_page(79).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    overlay = transform_image(overlay_raw, BEST_TRANSFORM["dx"], BEST_TRANSFORM["dy"], BEST_TRANSFORM["angleDeg"], BEST_TRANSFORM["scale"])

    base_feature = feature_mask(base)
    overlay_feature = feature_mask(overlay)
    # Smooth only slightly to merge the highlight fields but preserve standalone marks.
    base_feature = dilate(base_feature, 3)
    overlay_feature = dilate(overlay_feature, 3)

    base_text = page_text_mask(article_map, 76)
    overlay_text = page_text_mask(article_map, 79, transformed_from_p79=True)
    known_base, known_overlay, known_items = known_anchor_mask(registered)

    base_residual = base_feature & ~base_text
    overlay_residual = overlay_feature & ~overlay_text
    base_extra = base_residual & ~known_base
    overlay_extra = overlay_residual & ~known_overlay

    base_residual_crop = crop_mask(base_residual)
    overlay_residual_crop = crop_mask(overlay_residual)
    base_extra_crop = crop_mask(base_extra)
    overlay_extra_crop = crop_mask(overlay_extra)

    residual_overlap = base_residual_crop & overlay_residual_crop
    extra_overlap = base_extra_crop & overlay_extra_crop

    base_extra_components = component_summary(base_extra_crop)
    overlay_extra_components = component_summary(overlay_extra_crop)

    make_preview(base, overlay, base_extra, overlay_extra, base_residual, overlay_residual)

    result = {
        "source": "high-res p76 plus registered mirrored p79; OCR word boxes used only to mask text regions",
        "canvaInspection": str(CANVA),
        "crop": CROP,
        "transform": BEST_TRANSFORM,
        "knownAnchorItems": known_items,
        "stats": {
            "baseResidual": mask_stats(base_residual_crop),
            "overlayResidual": mask_stats(overlay_residual_crop),
            "residualOverlapPixels": int(residual_overlap.sum()),
            "baseExtraAfterKnownAnchorRemoval": mask_stats(base_extra_crop),
            "overlayExtraAfterKnownAnchorRemoval": mask_stats(overlay_extra_crop),
            "extraOverlapPixels": int(extra_overlap.sum()),
        },
        "baseExtraComponents": base_extra_components[:20],
        "overlayExtraComponents": overlay_extra_components[:20],
        "preview": str(OUT_IMG),
        "assessment": [
            "The calibrated crop is dominated by the known p79 orange highlight / p76 grey highlight line anchor.",
            "After masking OCR text boxes and the known anchor boxes, remaining components are small/noisy edge fragments rather than clear pills, wire knots, X marks, or ordering symbols.",
            "The local calibrated anchor provides a registration check, but no separate visual ordering cue is visible in this immediate crop.",
            "The missing ordering/instruction clue is more likely outside the calibrated anchor crop or in a source/physical clue, not in local residual marks beside the line pair.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Calibrated Anchor Visual-Marks Audit",
        "",
        "Scope: inspect the immediate crop around the unique registered 76/79 anchor for non-text visual marks that could provide the missing ordering cue. The script masks OCR word boxes and then separately removes the known aligned highlight boxes. No key derivation was run.",
        "",
        f"- Crop: `{CROP}`",
        f"- Transform: dx={BEST_TRANSFORM['dx']}, dy={BEST_TRANSFORM['dy']}, angle={BEST_TRANSFORM['angleDeg']}, scale={BEST_TRANSFORM['scale']}",
        f"- Preview: `{OUT_IMG}`",
        "",
        "## Known Anchor Removed",
        "",
    ]
    for item in known_items:
        md.append(f"- {item['side']}: `{item['label']}` box=`{item['box']}`")
    md.extend(["", "## Mask Statistics", ""])
    stats = result["stats"]
    md.append(f"- p76 residual after text masking: {stats['baseResidual']['pixels']} px, {stats['baseResidual']['components']} components")
    md.append(f"- registered p79 residual after text masking: {stats['overlayResidual']['pixels']} px, {stats['overlayResidual']['components']} components")
    md.append(f"- residual overlap before known-anchor removal: {stats['residualOverlapPixels']} px")
    md.append(f"- p76 extra after known-anchor removal: {stats['baseExtraAfterKnownAnchorRemoval']['pixels']} px, {stats['baseExtraAfterKnownAnchorRemoval']['components']} components")
    md.append(f"- registered p79 extra after known-anchor removal: {stats['overlayExtraAfterKnownAnchorRemoval']['pixels']} px, {stats['overlayExtraAfterKnownAnchorRemoval']['components']} components")
    md.append(f"- extra overlap after known-anchor removal: {stats['extraOverlapPixels']} px")
    md.extend(["", "## Largest Extra Components", ""])
    md.append("- p76 extra components:")
    for comp in sorted(base_extra_components, key=lambda c: c["area"], reverse=True)[:8]:
        md.append(f"  - area={comp['area']} box={comp['boxPage']} size={comp['width']}x{comp['height']}")
    md.append("- registered p79 extra components:")
    for comp in sorted(overlay_extra_components, key=lambda c: c["area"], reverse=True)[:8]:
        md.append(f"  - area={comp['area']} box={comp['boxPage']} size={comp['width']}x{comp['height']}")
    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The immediate calibrated anchor crop is dominated by the known p79 orange highlight / p76 grey highlight alignment.",
            "- After removing text boxes and the known aligned highlight boxes, the remaining marks are edge fragments/noise rather than clear pills, wire knots, X marks, or ordering symbols.",
            "- This means the unique anchor is useful for calibration but does not itself contain a visible local ordering cue.",
            "- Next best move: inspect the broader page-76/page-79 visual system outside this crop, especially the Canva-mentioned `XX`/barbed-wire/`SHIT`/`FUCK ALL SHITCOINS` alignment, or acquire a higher-resolution physical/source overlay.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
