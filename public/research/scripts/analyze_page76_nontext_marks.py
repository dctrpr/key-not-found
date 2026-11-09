#!/usr/bin/env python3
"""High-res non-text mark audit for page 76.

Tests whether page-79 pill fragments register to page-76 non-text X/brush marks
under a mirrored high-res geometry. This is a visual/geometry inspection only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from extract_visual_masks import connected_components, masks_for_page
from highres_reflection_extract import ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_nontext_marks.json"
OUT_MD = OUT / "page76_nontext_marks.md"
OUT_IMG = OUT / "page76_nontext_marks_overlay.jpg"


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def hflip_box(box, width):
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def page76_nontext_marks():
    img = upright_image(76)
    black = masks_for_page(img)["black"]
    comps = connected_components(black, min_area=350)
    marks = []
    for c in comps:
        box = c["box"]
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        a = area(box)
        # Focus on large brush/X marks and page-side marks, not individual text
        # glyphs. The x/y gates are based on the visually obvious non-text marks
        # in the high-res page-76 scan.
        if a < 3_500:
            continue
        if x1 < 1750 and y1 < 2300:
            continue
        if w < 35 or h < 35:
            continue
        marks.append(
            {
                "box": tuple(int(v) for v in box),
                "center": tuple(round(v, 2) for v in center(box)),
                "area": int(a),
                "width": int(w),
                "height": int(h),
            }
        )
    marks.sort(key=lambda m: (m["box"][1], m["box"][0]))
    for i, m in enumerate(marks, 1):
        m["index"] = i
    return marks


def page79_pill_fragments():
    boxes, size = orange_boxes(79)
    # In high-res source page 79, orange boxes 6-10 are the pill/graphic
    # fragments recorded in the manual highlight audit.
    pills = []
    for i, box in enumerate(boxes, 1):
        if i < 6:
            continue
        refl = hflip_box(box, size[0])
        pills.append(
            {
                "index": i,
                "sourceBox": tuple(int(v) for v in box),
                "reflectedBox": tuple(int(v) for v in refl),
                "reflectedCenter": tuple(round(v, 2) for v in center(refl)),
                "area": int(area(box)),
            }
        )
    return pills


def score_translation(pills, marks, dx, dy):
    if not pills or not marks:
        return {"mean": float("inf"), "max": float("inf"), "pairs": []}
    pairs = []
    for p in pills:
        pc = p["reflectedCenter"]
        shifted = (pc[0] + dx, pc[1] + dy)
        nearest = min(marks, key=lambda m: dist(shifted, m["center"]))
        d = dist(shifted, nearest["center"])
        pairs.append(
            {
                "pill": p["index"],
                "mark": nearest["index"],
                "distance": round(d, 2),
                "shiftedCenter": (round(shifted[0], 2), round(shifted[1], 2)),
            }
        )
    dists = [p["distance"] for p in pairs]
    return {"mean": round(float(np.mean(dists)), 2), "max": round(float(np.max(dists)), 2), "pairs": pairs}


def draw_overlay(img, pills, marks, best):
    out = img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for m in marks:
        draw.rectangle(m["box"], outline=(0, 220, 255, 255), width=6)
        draw.text((m["box"][0], max(0, m["box"][1] - 26)), f"M{m['index']}", fill=(0, 180, 220, 255))
    for p in pills:
        rb = p["reflectedBox"]
        shifted = (
            int(round(rb[0] + best["dx"])),
            int(round(rb[1] + best["dy"])),
            int(round(rb[2] + best["dx"])),
            int(round(rb[3] + best["dy"])),
        )
        draw.rectangle(rb, outline=(190, 0, 255, 130), width=4)
        draw.rectangle(shifted, outline=(255, 80, 0, 230), width=5)
        draw.text((shifted[0], max(0, shifted[1] - 22)), f"P{p['index']}", fill=(255, 80, 0, 255))
    Image.alpha_composite(out, overlay).convert("RGB").save(OUT_IMG, quality=94)


def main():
    ensure_highres_sources()
    img76 = upright_image(76)
    marks = page76_nontext_marks()
    pills = page79_pill_fragments()

    results = []
    for dx in range(-500, 501, 50):
        for dy in range(-500, 501, 50):
            score = score_translation(pills, marks, dx, dy)
            results.append({"dx": dx, "dy": dy, **score})
    results.sort(key=lambda r: (r["mean"], r["max"]))
    best = results[0] if results else {"dx": 0, "dy": 0, "mean": None, "max": None, "pairs": []}
    draw_overlay(img76, pills, marks, best)

    result = {
        "source": "high-res page 76 non-text marks vs mirrored high-res page 79 pill fragments",
        "overlay": str(OUT_IMG),
        "marks": marks,
        "pills": pills,
        "bestTranslation": best,
        "topTranslations": results[:12],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Page 76 Non-Text Marks",
        "",
        "Scope: high-res visual geometry only. Detect large non-text black marks on page 76 and test whether mirrored page-79 pill fragments register to them under simple translation.",
        "",
        f"- Overlay: `{OUT_IMG}`",
        "",
        "## Summary",
        "",
        f"- Page-76 non-text marks detected: {len(marks)}",
        f"- Page-79 pill fragments tested: {len(pills)}",
        f"- Best translation: dx={best['dx']} dy={best['dy']} mean={best['mean']} max={best['max']} px",
        "",
        "## Best Pairing",
        "",
    ]
    for pair in best["pairs"]:
        lines.append(
            f"- pill {pair['pill']} -> mark {pair['mark']} distance={pair['distance']} shiftedCenter={pair['shiftedCenter']}"
        )
    lines.extend(["", "## Marks", ""])
    for m in marks:
        lines.append(f"- mark {m['index']}: box={m['box']} center={m['center']} area={m['area']}")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The page-79 pill fragments do not register cleanly to page-76 X/brush marks under simple high-res mirror plus translation.",
            "- The best fit is still hundreds of pixels off on at least one fragment, so this is not a reliable anchor system.",
            "- The non-text marks are useful visual context, but they do not currently supply the missing selector.",
            "- Next best move: physical scan/photo alignment or manual line-level inspection of the page-76 corridor; avoid more generic affine/pill-anchor searches unless new anchor evidence appears.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
