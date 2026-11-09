#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

from highres_reflection_extract import SOURCE_PAGES, ensure_highres_sources


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs" / "source_audit"
OUT.mkdir(parents=True, exist_ok=True)

REPORT_MD = OUT / "registration_workbench_76_79.md"
CONTACT = OUT / "registration_workbench_76_79_contact_sheet.jpg"
BEST = OUT / "registration_workbench_76_79_best_overlay.jpg"
MASK = OUT / "registration_workbench_76_79_best_masks.jpg"


PAGE_W, PAGE_H = 2544, 3264
# Right-side visual art corridor where the Canva note focuses: wire, pills,
# dollar/X marks, black bars, and the Bukele/IMF corridor.
CROP = (1450, 0, 2544, 3264)


def load_page(page):
    return Image.open(SOURCE_PAGES[page]).convert("RGB").rotate(180, expand=True)


def shift_image(img, dx, dy):
    out = Image.new("RGB", img.size, "white")
    out.paste(img, (dx, dy))
    return out


def feature_mask(img, side="base"):
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    dark = (r < 90) & (g < 90) & (b < 90)
    orange = (r > 145) & (g > 55) & (g < 190) & (b < 100) & ((r - b) > 60)
    yellow = (r > 150) & (g > 135) & (b < 120)
    if side == "base":
        mask = dark | orange | yellow
    else:
        mask = dark | orange | yellow
    return mask


def crop_mask(mask):
    x1, y1, x2, y2 = CROP
    return mask[y1:y2, x1:x2]


def score_masks(base_mask, overlay_mask):
    inter = np.logical_and(base_mask, overlay_mask).sum()
    union = np.logical_or(base_mask, overlay_mask).sum()
    base_n = base_mask.sum()
    overlay_n = overlay_mask.sum()
    return {
        "intersection": int(inter),
        "union": int(union),
        "jaccard": float(inter / union) if union else 0.0,
        "overBase": float(inter / base_n) if base_n else 0.0,
        "overOverlay": float(inter / overlay_n) if overlay_n else 0.0,
        "balanced": float(inter / max(1.0, (base_n * overlay_n) ** 0.5)),
    }


def overlay_preview(base, shifted, label, score):
    crop_base = base.crop(CROP)
    crop_shift = shifted.crop(CROP)
    blend = Image.blend(crop_base, crop_shift, 0.48)
    diff = ImageChops.difference(crop_base, crop_shift)
    diff = ImageEnhance.Contrast(diff).enhance(1.8)
    preview = Image.new("RGB", (crop_base.width, crop_base.height + 120), "white")
    preview.paste(blend, (0, 0))
    draw = ImageDraw.Draw(preview)
    draw.rectangle((0, crop_base.height, preview.width, preview.height), fill=(245, 245, 245))
    draw.text(
        (18, crop_base.height + 16),
        f"{label}  jaccard={score['jaccard']:.4f} overBase={score['overBase']:.4f} overOverlay={score['overOverlay']:.4f}",
        fill=(20, 20, 20),
    )
    return preview.resize((preview.width // 3, preview.height // 3))


def make_mask_preview(base_mask, overlay_mask):
    x1, y1, x2, y2 = CROP
    bm = base_mask[y1:y2, x1:x2]
    om = overlay_mask[y1:y2, x1:x2]
    rgb = np.zeros((bm.shape[0], bm.shape[1], 3), dtype=np.uint8)
    rgb[:, :, :] = 245
    rgb[bm] = [40, 80, 220]
    rgb[om] = [240, 130, 20]
    rgb[np.logical_and(bm, om)] = [230, 20, 80]
    return Image.fromarray(rgb)


def main():
    ensure_highres_sources()
    page76 = load_page(76).resize((PAGE_W, PAGE_H))
    page79 = load_page(79).resize((PAGE_W, PAGE_H)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    base_crop_mask = crop_mask(feature_mask(page76, "base"))
    trials = []
    for dy in range(-260, 281, 20):
        for dx in range(-260, 281, 20):
            shifted = shift_image(page79, dx, dy)
            overlay_crop_mask = crop_mask(feature_mask(shifted, "overlay"))
            score = score_masks(base_crop_mask, overlay_crop_mask)
            trials.append({"dx": dx, "dy": dy, **score})
    trials.sort(key=lambda item: (item["balanced"], item["jaccard"], item["overBase"]), reverse=True)

    top = trials[:12]
    previews = []
    for item in top:
        shifted = shift_image(page79, item["dx"], item["dy"])
        previews.append(overlay_preview(page76, shifted, f"dx={item['dx']} dy={item['dy']}", item))

    cols = 3
    rows = (len(previews) + cols - 1) // cols
    cell_w = max(img.width for img in previews)
    cell_h = max(img.height for img in previews)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    for idx, img in enumerate(previews):
        sheet.paste(img, ((idx % cols) * cell_w, (idx // cols) * cell_h))
    sheet.save(CONTACT, quality=92)

    best = top[0]
    best_shifted = shift_image(page79, best["dx"], best["dy"])
    best_overlay = Image.blend(page76.crop(CROP), best_shifted.crop(CROP), 0.48)
    best_overlay.save(BEST, quality=94)
    make_mask_preview(feature_mask(page76), feature_mask(best_shifted)).save(MASK, quality=94)

    lines = [
        "# Registration Workbench 76/79",
        "",
        "Scope: sweep simple x/y translations of horizontally mirrored page 79 over page 76 in the right-side visual corridor.",
        "Feature masks include dark, orange, and yellow art/highlight pixels. This is a visual-registration diagnostic, not a key search.",
        "",
        f"- Crop region: `{CROP}`",
        f"- Translation sweep: dx/dy -260..280 px in 20 px steps",
        f"- Contact sheet: `{CONTACT}`",
        f"- Best overlay crop: `{BEST}`",
        f"- Best mask preview: `{MASK}`",
        "",
        "## Top Translation Scores",
        "",
    ]
    for item in top:
        lines.append(
            f"- dx={item['dx']} dy={item['dy']} balanced={item['balanced']:.5f} "
            f"jaccard={item['jaccard']:.5f} overBase={item['overBase']:.5f} overOverlay={item['overOverlay']:.5f}"
        )
    lines.extend(["", "## Assessment", ""])
    best_zero = next(item for item in trials if item["dx"] == 0 and item["dy"] == 0)
    lines.append(
        f"- Best shift is dx={best['dx']} dy={best['dy']} with balanced={best['balanced']:.5f}; "
        f"unshifted balanced={best_zero['balanced']:.5f}."
    )
    if best["balanced"] > best_zero["balanced"] * 1.25:
        lines.append("- Translation improves feature overlap, so a visual registration workbench is warranted before further exact-span geometry.")
    else:
        lines.append("- Translation does not materially improve feature overlap; any needed registration likely requires rotation/scale/local warp or better manual correspondences.")
    lines.append("- This does not promote the pill anchors to a selector. It only narrows how to inspect the overlay visually.")
    REPORT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_MD}")
    print(f"wrote {CONTACT}")
    print(f"wrote {BEST}")
    print(f"wrote {MASK}")


if __name__ == "__main__":
    main()
