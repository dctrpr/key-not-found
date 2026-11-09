#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from build_registration_rotation_scale_sweep import transform_image
from build_registration_workbench import PAGE_H, PAGE_W, feature_mask, load_page
from highres_reflection_extract import ensure_highres_sources


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs" / "source_audit"
OUT.mkdir(parents=True, exist_ok=True)

REPORT_MD = OUT / "manual_correspondence_sheet_76_79.md"
SHEET = OUT / "manual_correspondence_sheet_76_79.jpg"

BEST = {"dx": 20, "dy": 240, "angle": 2, "scale": 1.02}

REGIONS = [
    ("wire_open_heart", (1450, 120, 2544, 820)),
    ("fiat_nonsense", (1450, 760, 2544, 1450)),
    ("el_salvador_imf", (1450, 1450, 2544, 2350)),
    ("pills_dollar_marks", (1450, 2280, 2544, 3264)),
]


def draw_grid(img, region, label):
    out = img.convert("RGB")
    draw = ImageDraw.Draw(out)
    w, h = out.size
    for x in range(0, w + 1, 100):
        draw.line((x, 0, x, h), fill=(210, 80, 80), width=1)
        draw.text((x + 3, 4), str(region[0] + x), fill=(160, 40, 40))
    for y in range(0, h + 1, 100):
        draw.line((0, y, w, y), fill=(210, 80, 80), width=1)
        draw.text((4, y + 3), str(region[1] + y), fill=(160, 40, 40))
    draw.rectangle((0, 0, w - 1, h - 1), outline=(30, 30, 30), width=3)
    draw.rectangle((0, h - 42, w, h), fill=(255, 255, 255))
    draw.text((12, h - 32), label, fill=(10, 10, 10))
    return out


def mask_preview(base_crop, transformed_crop):
    bm = feature_mask(base_crop)
    tm = feature_mask(transformed_crop)
    rgb = np.zeros((bm.shape[0], bm.shape[1], 3), dtype=np.uint8)
    rgb[:, :, :] = 245
    rgb[bm] = [40, 80, 220]
    rgb[tm] = [240, 130, 20]
    rgb[np.logical_and(bm, tm)] = [230, 20, 80]
    return Image.fromarray(rgb)


def panelize(region_name, region, page76, page79_transformed):
    base = page76.crop(region)
    transformed = page79_transformed.crop(region)
    blend = Image.blend(base, transformed, 0.48)
    mask = mask_preview(base, transformed)
    panels = [
        draw_grid(base, region, f"{region_name} | page76"),
        draw_grid(transformed, region, f"{region_name} | mirrored p79 transformed"),
        draw_grid(blend, region, f"{region_name} | blend"),
        draw_grid(mask, region, f"{region_name} | mask blue=76 orange=79 pink=overlap"),
    ]
    max_w = 500
    resized = []
    for panel in panels:
        ratio = max_w / panel.width
        resized.append(panel.resize((max_w, int(panel.height * ratio))))
    return resized


def main():
    ensure_highres_sources()
    page76 = load_page(76).resize((PAGE_W, PAGE_H))
    page79 = load_page(79).resize((PAGE_W, PAGE_H)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    transformed = transform_image(page79, BEST["dx"], BEST["dy"], BEST["angle"], BEST["scale"])

    rows = [panelize(name, region, page76, transformed) for name, region in REGIONS]
    cell_w = max(panel.width for row in rows for panel in row)
    cell_h = max(panel.height for row in rows for panel in row)
    sheet = Image.new("RGB", (4 * cell_w, len(rows) * cell_h), "white")
    for y, row in enumerate(rows):
        for x, panel in enumerate(row):
            sheet.paste(panel, (x * cell_w, y * cell_h))
    sheet.save(SHEET, quality=92)

    lines = [
        "# Manual Correspondence Sheet 76/79",
        "",
        "Scope: create a visual inspection sheet for manually marking true correspondences between page 76 and mirrored/transformed page 79.",
        "This does not extract or check key material.",
        "",
        f"- Transform used: dx={BEST['dx']}, dy={BEST['dy']}, angle={BEST['angle']}deg, scale={BEST['scale']}",
        f"- Sheet: `{SHEET}`",
        "",
        "## Regions",
        "",
    ]
    for name, region in REGIONS:
        lines.append(f"- `{name}`: `{region}`")
    lines.extend(["", "## How To Use", ""])
    lines.append("- Look for points that are the same physical mark in the page76 panel and the transformed page79 panel.")
    lines.append("- Good candidates should be visible in the blend and pink in the mask panel.")
    lines.append("- Avoid using repeated body text as correspondence points because it creates false alignments.")
    lines.append("- Candidate manual points should come from wire knots/crossings, pill tips, dollar/X strokes, or hard edges of black bars/highlights.")
    lines.extend(["", "## Assessment", ""])
    lines.append("- This artifact turns the current best global transform into a practical manual-marking view.")
    lines.append("- If no 4+ non-text correspondences are obvious here, the 76/79 visual system should remain orientation evidence rather than letter-level geometry.")
    REPORT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_MD}")
    print(f"wrote {SHEET}")


if __name__ == "__main__":
    main()
