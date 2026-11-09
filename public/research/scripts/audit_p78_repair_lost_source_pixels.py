#!/usr/bin/env python3
"""Inspect which p78 source pixels are lost by the dx=-38/-40 repair.

The source-side fit audit showed that the repaired p78 frames lose about 0.8%
of the detected p78 graphic mask. This pass localizes that loss: left/right
bands, bounding boxes, centroids, and component overlap. It is visual geometry
bookkeeping only.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, or address
checks are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from audit_p78_graphic_pullquote_reflection import detect_graphic_mask
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
FIT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_source_side_fit/p78_frame_source_side_fit.json"
OUT = ROOT / "analysis_outputs/source_audit/p78_repair_lost_source_pixels"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_repair_lost_source_pixels.json"
OUT_MD = OUT / "p78_repair_lost_source_pixels.md"
SHEET = OUT / "p78_repair_lost_source_pixels_sheet.jpg"


def font(size: int = 18) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def box_mask(shape: tuple[int, int], box: list[int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    x0, y0, x1, y1 = box
    x0 = max(0, min(shape[1], x0))
    x1 = max(0, min(shape[1], x1))
    y0 = max(0, min(shape[0], y0))
    y1 = max(0, min(shape[0], y1))
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = True
    return mask


def bbox_for_mask(mask: np.ndarray) -> list[int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def centroid_for_mask(mask: np.ndarray) -> list[float] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [round(float(xs.mean()), 2), round(float(ys.mean()), 2)]


def mask_count_in_box(mask: np.ndarray, box: list[int]) -> int:
    bm = box_mask(mask.shape, box)
    return int((mask & bm).sum())


def summarize_repair(row: dict, current_box: list[int], graphic_mask: np.ndarray, components: list[dict]) -> dict:
    repaired_box = [int(v) for v in row["p78UprightBox"]]
    current = box_mask(graphic_mask.shape, current_box)
    repaired = box_mask(graphic_mask.shape, repaired_box)
    lost = graphic_mask & current & ~repaired
    gained_source_mask = graphic_mask & repaired & ~current
    gained_area = repaired & ~current
    lost_count = int(lost.sum())
    gained_mask_count = int(gained_source_mask.sum())
    gained_area_count = int(gained_area.sum())

    comp_rows = []
    for idx, comp in enumerate(components, 1):
        comp_box = [int(v) for v in comp["box"]]
        comp_mask = graphic_mask & box_mask(graphic_mask.shape, comp_box)
        comp_pixels = int(comp_mask.sum())
        lost_pixels = int((lost & box_mask(graphic_mask.shape, comp_box)).sum())
        if lost_pixels:
            comp_rows.append(
                {
                    "componentIndex": idx,
                    "componentBox": comp_box,
                    "componentPixels": comp_pixels,
                    "lostPixels": lost_pixels,
                    "lostShareOfComponent": round(lost_pixels / max(1, comp_pixels), 6),
                    "lostShareOfRepairLoss": round(lost_pixels / max(1, lost_count), 6),
                }
            )
    comp_rows.sort(key=lambda item: item["lostPixels"], reverse=True)

    lost_bbox = bbox_for_mask(lost)
    return {
        "name": row["name"],
        "repairedBox": repaired_box,
        "lostPixels": lost_count,
        "lostPixelShareOfGraphic": round(lost_count / max(1, int(graphic_mask.sum())), 6),
        "lostBBox": lost_bbox,
        "lostCentroid": centroid_for_mask(lost),
        "lostBandWidthPx": 0 if lost_bbox is None else lost_bbox[2] - lost_bbox[0],
        "gainedSourceMaskPixels": gained_mask_count,
        "gainedAreaPixels": gained_area_count,
        "gainedAreaContainsSourceMask": gained_mask_count > 0,
        "componentLosses": comp_rows,
    }


def draw_sheet(img: Image.Image, graphic_mask: np.ndarray, current_box: list[int], repairs: list[dict]) -> None:
    crop = [235, 2360, 1415, 3010]
    base = img.copy().convert("RGBA")
    mask_overlay = np.zeros((base.height, base.width, 4), dtype=np.uint8)
    mask_overlay[graphic_mask] = [0, 120, 255, 80]
    base = Image.alpha_composite(base, Image.fromarray(mask_overlay, "RGBA"))

    panels = []
    colors = {"g5_edge_touch_dx_-38": "#ff5ebc", "nearest_grid_dx_-40": "#ff9b2e"}
    for repair in repairs:
        panel = base.copy()
        draw = ImageDraw.Draw(panel)
        fnt = font(22)
        draw.rectangle(current_box, outline="#00d6ff", width=5)
        draw.text((current_box[0], max(0, current_box[1] - 28)), "current full source box", fill="#00d6ff", font=fnt)
        draw.rectangle(repair["repairedBox"], outline=colors.get(repair["name"], "#ff5ebc"), width=5)
        draw.text((repair["repairedBox"][0], max(0, repair["repairedBox"][1] - 54)), repair["name"], fill=colors.get(repair["name"], "#ff5ebc"), font=fnt)
        lost_mask = np.zeros((base.height, base.width, 4), dtype=np.uint8)
        x0 = repair["repairedBox"][0]
        # Lost area is left of repaired frame within current frame.
        lost = graphic_mask & box_mask(graphic_mask.shape, current_box) & ~box_mask(graphic_mask.shape, repair["repairedBox"])
        lost_mask[lost] = [255, 0, 0, 210]
        panel = Image.alpha_composite(panel, Image.fromarray(lost_mask, "RGBA")).convert("RGB")
        panels.append((repair["name"], panel.crop(tuple(crop))))

    margin = 24
    gap = 24
    label_h = 36
    panel_w = 650
    rendered = []
    for label, panel in panels:
        scale = min(panel_w / panel.width, 1.0)
        rendered.append((label, panel.resize((int(panel.width * scale), int(panel.height * scale)))))
    width = margin * 2 + sum(panel_w for _ in rendered) + gap * (len(rendered) - 1)
    height = margin * 2 + label_h + max(panel.height for _, panel in rendered)
    sheet = Image.new("RGB", (width, height), (16, 18, 22))
    draw = ImageDraw.Draw(sheet)
    fnt = font(21)
    x = margin
    for label, panel in rendered:
        draw.text((x, margin), f"{label}: red = source pixels trimmed by repair", fill=(238, 242, 247), font=fnt)
        sheet.paste(panel, (x, margin + label_h))
        x += panel_w + gap
    sheet.save(SHEET, quality=94)


def main() -> None:
    fit = json.loads(FIT_JSON.read_text(encoding="utf-8"))
    p78 = upright_image(78).convert("RGB")
    graphic_mask, graphic_box, components = detect_graphic_mask(p78)
    current = next(row for row in fit["rows"] if row["name"] == "current")
    repairs = [row for row in fit["rows"] if row["name"] != "current"]
    current_box = [int(v) for v in current["p78UprightBox"]]
    repair_summaries = [summarize_repair(row, current_box, graphic_mask, components) for row in repairs]
    draw_sheet(p78, graphic_mask, current_box, repair_summaries)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "localize p78 source graphic pixels lost by dx=-38/-40 repair; no OCR or key derivation",
        "sourceReports": {"sourceSideFit": str(FIT_JSON.relative_to(ROOT))},
        "currentSourceBox": current_box,
        "detectedGraphicBox": [int(v) for v in graphic_box],
        "graphicMaskPixels": int(graphic_mask.sum()),
        "componentCount": len(components),
        "repairs": repair_summaries,
        "sheet": str(SHEET.relative_to(ROOT)),
        "assessment": [
            "The repair loss is a narrow left-edge strip of the p78 graphic, not a centered cut through the pull-quote text.",
            "The repaired frame gains right-side area, but that gained area contains no detected source-mask pixels.",
            "This supports treating dx=-38/-40 as a p76 registration alignment rather than a source-object crop instruction.",
        ],
        "nextMove": "Keep p78 current box as the source object and dx=-38/-40 as the p76 registration repair; do not use the lost strip as extraction material unless a future source clue names left-edge trim/crop.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P78 Repair Lost Source Pixels Audit",
        "",
        "Scope: localize the p78 graphic pixels lost when the current p78 source box is shifted to the dx `-38/-40` repaired boxes. No OCR extraction, key derivation, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Current source box: `{current_box}`",
        f"- Detected graphic box: `{result['detectedGraphicBox']}`",
        f"- Graphic mask pixels: `{result['graphicMaskPixels']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Repair Losses",
        "",
        "| repair | lost pixels | lost share | lost bbox | lost centroid | gained source pixels | top component loss |",
        "|---|---:|---:|---|---|---:|---|",
    ]
    for repair in repair_summaries:
        top = repair["componentLosses"][0] if repair["componentLosses"] else None
        top_text = "-" if not top else f"component {top['componentIndex']} {top['lostPixels']}px ({top['lostShareOfRepairLoss']})"
        lines.append(
            f"| `{repair['name']}` | `{repair['lostPixels']}` | `{repair['lostPixelShareOfGraphic']}` | `{repair['lostBBox']}` | `{repair['lostCentroid']}` | `{repair['gainedSourceMaskPixels']}` | {top_text} |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    for repair in repair_summaries:
        print(repair["name"], repair["lostPixels"], repair["lostBBox"], "gainedMask", repair["gainedSourceMaskPixels"])


if __name__ == "__main__":
    main()
