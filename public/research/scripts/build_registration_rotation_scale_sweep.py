#!/usr/bin/env python3
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from build_registration_workbench import CROP, PAGE_H, PAGE_W, feature_mask, load_page, score_masks
from highres_reflection_extract import ensure_highres_sources


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs" / "source_audit"
OUT.mkdir(parents=True, exist_ok=True)

REPORT_MD = OUT / "registration_rotation_scale_76_79.md"
CONTACT = OUT / "registration_rotation_scale_76_79_contact_sheet.jpg"
BEST = OUT / "registration_rotation_scale_76_79_best_overlay.jpg"
MASK = OUT / "registration_rotation_scale_76_79_best_masks.jpg"

SCALE_FACTOR = 0.25


def scaled_crop():
    return tuple(int(round(v * SCALE_FACTOR)) for v in CROP)


def affine_inverse_coeffs(size, dx, dy, angle_deg, scale):
    # Forward transform, source -> destination:
    # dest = T(dx,dy) * C * R(angle) * S(scale) * C^-1 * src.
    # PIL expects destination -> source coefficients.
    w, h = size
    cx, cy = w / 2, h / 2
    theta = math.radians(angle_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    inv_s = 1.0 / scale
    # source = C * S^-1 * R^-1 * C^-1 * T(-dx,-dy) * dest
    a = inv_s * cos_t
    b = inv_s * sin_t
    d = -inv_s * sin_t
    e = inv_s * cos_t
    c = cx - a * (cx + dx) - b * (cy + dy)
    f = cy - d * (cx + dx) - e * (cy + dy)
    return (a, b, c, d, e, f)


def transform_image(img, dx, dy, angle_deg, scale):
    coeffs = affine_inverse_coeffs(img.size, dx, dy, angle_deg, scale)
    return img.transform(img.size, Image.Transform.AFFINE, coeffs, resample=Image.Resampling.BICUBIC, fillcolor="white")


def crop_mask(mask):
    x1, y1, x2, y2 = scaled_crop()
    return mask[y1:y2, x1:x2]


def make_preview(base, transformed, label, score):
    crop = scaled_crop()
    b = base.crop(crop)
    t = transformed.crop(crop)
    blend = Image.blend(b, t, 0.48)
    preview = Image.new("RGB", (b.width, b.height + 52), "white")
    preview.paste(blend, (0, 0))
    draw = ImageDraw.Draw(preview)
    draw.rectangle((0, b.height, preview.width, preview.height), fill=(245, 245, 245))
    draw.text((8, b.height + 8), f"{label} bal={score['balanced']:.4f} jac={score['jaccard']:.4f}", fill=(20, 20, 20))
    return preview


def make_mask_preview(base_mask, overlay_mask):
    x1, y1, x2, y2 = scaled_crop()
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
    size = (int(PAGE_W * SCALE_FACTOR), int(PAGE_H * SCALE_FACTOR))
    page76 = load_page(76).resize(size)
    page79 = load_page(79).resize(size).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    base_crop_mask = crop_mask(feature_mask(page76))

    trials = []
    base_dx = -20 * SCALE_FACTOR
    base_dy = 240 * SCALE_FACTOR
    for angle in [-3, -2, -1, 0, 1, 2, 3]:
        for scale in [0.96, 0.98, 1.00, 1.02, 1.04]:
            for dx_extra in [-40, -20, 0, 20, 40]:
                for dy_extra in [-40, -20, 0, 20, 40]:
                    dx = base_dx + dx_extra * SCALE_FACTOR
                    dy = base_dy + dy_extra * SCALE_FACTOR
                    transformed = transform_image(page79, dx, dy, angle, scale)
                    score = score_masks(base_crop_mask, crop_mask(feature_mask(transformed)))
                    trials.append({
                        "dx": round(dx / SCALE_FACTOR, 2),
                        "dy": round(dy / SCALE_FACTOR, 2),
                        "angleDeg": angle,
                        "scale": scale,
                        **score,
                    })
    trials.sort(key=lambda item: (item["balanced"], item["jaccard"], item["overBase"]), reverse=True)
    top = trials[:12]

    previews = []
    for item in top:
        transformed = transform_image(
            page79,
            item["dx"] * SCALE_FACTOR,
            item["dy"] * SCALE_FACTOR,
            item["angleDeg"],
            item["scale"],
        )
        previews.append(make_preview(page76, transformed, f"dx={item['dx']} dy={item['dy']} a={item['angleDeg']} s={item['scale']}", item))

    cols = 3
    cell_w = max(p.width for p in previews)
    cell_h = max(p.height for p in previews)
    rows = (len(previews) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    for idx, preview in enumerate(previews):
        sheet.paste(preview, ((idx % cols) * cell_w, (idx // cols) * cell_h))
    sheet.save(CONTACT, quality=92)

    best = top[0]
    best_transformed = transform_image(
        page79,
        best["dx"] * SCALE_FACTOR,
        best["dy"] * SCALE_FACTOR,
        best["angleDeg"],
        best["scale"],
    )
    crop = scaled_crop()
    Image.blend(page76.crop(crop), best_transformed.crop(crop), 0.48).save(BEST, quality=94)
    make_mask_preview(feature_mask(page76), feature_mask(best_transformed)).save(MASK, quality=94)

    translation_baseline = min(
        trials,
        key=lambda item: abs(item["dx"] + 20) + abs(item["dy"] - 240) + abs(item["angleDeg"]) + abs(item["scale"] - 1),
    )

    lines = [
        "# Registration Rotation/Scale Sweep 76/79",
        "",
        "Scope: small rotation/scale/translation sweep around the best simple translation from the 76/79 workbench.",
        "This is still a visual-registration diagnostic, not a key search.",
        "",
        f"- Working scale: `{SCALE_FACTOR}`",
        f"- Full-resolution crop region represented: `{CROP}`",
        f"- Search center: `dx=-20`, `dy=240`, `angle=0`, `scale=1.0`",
        f"- Contact sheet: `{CONTACT}`",
        f"- Best overlay crop: `{BEST}`",
        f"- Best mask preview: `{MASK}`",
        "",
        "## Top Scores",
        "",
    ]
    for item in top:
        lines.append(
            f"- dx={item['dx']} dy={item['dy']} angle={item['angleDeg']} scale={item['scale']:.2f} "
            f"balanced={item['balanced']:.5f} jaccard={item['jaccard']:.5f} "
            f"overBase={item['overBase']:.5f} overOverlay={item['overOverlay']:.5f}"
        )
    lines.extend(["", "## Assessment", ""])
    lines.append(
        f"- Translation baseline in this local grid: balanced={translation_baseline['balanced']:.5f}, "
        f"jaccard={translation_baseline['jaccard']:.5f}."
    )
    lines.append(
        f"- Best local transform: dx={best['dx']}, dy={best['dy']}, angle={best['angleDeg']}, scale={best['scale']:.2f}, "
        f"balanced={best['balanced']:.5f}."
    )
    improvement = best["balanced"] / max(1e-9, translation_baseline["balanced"])
    lines.append(f"- Improvement over translation baseline: {improvement:.3f}x.")
    if improvement > 1.10:
        lines.append("- Rotation/scale materially improves feature overlap; use the best transform for the next visual inspection pass.")
    else:
        lines.append("- Rotation/scale does not materially improve the translation-only workbench. Further extraction should use manual correspondences or local warping, not global affine tuning.")
    lines.append("- No key material is produced by this pass.")
    REPORT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_MD}")
    print(f"wrote {CONTACT}")
    print(f"wrote {BEST}")
    print(f"wrote {MASK}")


if __name__ == "__main__":
    main()
