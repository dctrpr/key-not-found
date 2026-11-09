#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from build_registration_workbench import PAGE_H, PAGE_W, feature_mask, load_page, score_masks
from highres_reflection_extract import ensure_highres_sources


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs" / "source_audit"
OUT.mkdir(parents=True, exist_ok=True)

REPORT_MD = OUT / "leaf_hold_to_light_sheet.md"
SHEET = OUT / "leaf_hold_to_light_sheet.jpg"

LEAF_PAIRS = [(75, 76), (77, 78), (79, 80)]


def mask_preview(base, overlay):
    bm = feature_mask(base)
    om = feature_mask(overlay)
    rgb = np.zeros((bm.shape[0], bm.shape[1], 3), dtype=np.uint8)
    rgb[:, :, :] = 245
    rgb[bm] = [40, 80, 220]
    rgb[om] = [240, 130, 20]
    rgb[np.logical_and(bm, om)] = [230, 20, 80]
    return Image.fromarray(rgb), score_masks(bm, om)


def highlight_mask(img):
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    orange = (r > 145) & (g > 55) & (g < 190) & (b < 110) & ((r - b) > 55)
    yellow = (r > 150) & (g > 135) & (b < 130)
    return orange | yellow


def draw_label(img, label):
    out = img.convert("RGB")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, out.width, 42), fill=(255, 255, 255))
    draw.text((12, 12), label, fill=(10, 10, 10))
    return out


def make_panel(base_page, back_page, view_label):
    base = load_page(base_page).resize((PAGE_W, PAGE_H))
    back = load_page(back_page).resize((PAGE_W, PAGE_H)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    blend = Image.blend(base, back, 0.48)
    mask, score = mask_preview(base, back)
    highlight_score = score_masks(highlight_mask(base), highlight_mask(back))
    panels = [
        draw_label(base, f"{view_label}: base p{base_page}"),
        draw_label(back, f"{view_label}: hflip p{back_page}"),
        draw_label(blend, f"{view_label}: blend"),
        draw_label(mask, f"{view_label}: mask blue=base orange=back pink=overlap"),
    ]
    max_w = 360
    resized = []
    for panel in panels:
        ratio = max_w / panel.width
        resized.append(panel.resize((max_w, int(panel.height * ratio))))
    return resized, score, highlight_score


def main():
    ensure_highres_sources()
    rows = []
    scores = []
    for odd, even in LEAF_PAIRS:
        for base, back in [(odd, even), (even, odd)]:
            view_label = f"{base}_view_{back}_through"
            panels, score, highlight_score = make_panel(base, back, view_label)
            rows.append(panels)
            scores.append({
                "view": view_label,
                "base": base,
                "back": back,
                **score,
                "highlightBalanced": highlight_score["balanced"],
                "highlightJaccard": highlight_score["jaccard"],
                "highlightOverBase": highlight_score["overBase"],
                "highlightOverBack": highlight_score["overOverlay"],
            })

    cell_w = max(panel.width for row in rows for panel in row)
    cell_h = max(panel.height for row in rows for panel in row)
    sheet = Image.new("RGB", (4 * cell_w, len(rows) * cell_h), "white")
    for y, row in enumerate(rows):
        for x, panel in enumerate(row):
            sheet.paste(panel, (x * cell_w, y * cell_h))
    sheet.save(SHEET, quality=92)

    scores.sort(key=lambda item: (item["balanced"], item["jaccard"]), reverse=True)
    lines = [
        "# Leaf Hold-To-Light Sheet",
        "",
        "Scope: inspect physical front/back leaves by overlaying each page with the horizontally mirrored page on the back side.",
        "This is a visual geometry pass only; it does not generate key candidates.",
        "",
        f"- Sheet: `{SHEET}`",
        "",
        "## Scores",
        "",
    ]
    for item in scores:
        lines.append(
            f"- {item['view']}: balanced={item['balanced']:.5f} jaccard={item['jaccard']:.5f} "
            f"overBase={item['overBase']:.5f} overBack={item['overOverlay']:.5f} "
            f"highlightBalanced={item['highlightBalanced']:.5f} highlightJaccard={item['highlightJaccard']:.5f}"
        )
    lines.extend(["", "## Assessment", ""])
    top = scores[0]
    lines.append(f"- Strongest feature-overlap view is `{top['view']}` with balanced={top['balanced']:.5f}.")
    top_highlight = max(scores, key=lambda item: (item["highlightBalanced"], item["highlightJaccard"]))
    lines.append(f"- Strongest highlight-only view is `{top_highlight['view']}` with highlightBalanced={top_highlight['highlightBalanced']:.5f}.")
    lines.append("- Full feature scores include text/background/art pixels; highlight-only scores are better for checking literal highlighted-mask correspondence.")
    lines.append("- Use this sheet to decide whether a physical leaf pair has cleaner correspondence than the 76/79 art overlay.")
    lines.append("- If no leaf pair shows clean non-text correspondence, the missing selector is probably not a direct hold-to-light affine overlay.")
    REPORT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_MD}")
    print(f"wrote {SHEET}")


if __name__ == "__main__":
    main()
