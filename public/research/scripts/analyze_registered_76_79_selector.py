#!/usr/bin/env python3
"""Apply the best 76/79 visual registration and remeasure page-76 hits."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from analyze_highres_page76_mirror_selector import (
    PAGE76_ORANGE_LABELS,
    PAGE79_ORANGE_LABELS,
    area,
    attach_labels,
    center,
    hflip_box,
    intersection,
    manual_page76_grey_boxes,
)
from highres_reflection_extract import ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT_JSON = OUT / "registered_76_79_selector.json"
OUT_MD = OUT / "registered_76_79_selector.md"
OUT_IMG = OUT / "registered_76_79_selector_overlay.jpg"
OUT_CROP = OUT / "registered_76_79_selector_crop.jpg"

BEST_TRANSFORM = {
    "dx": 20.0,
    "dy": 240.0,
    "angleDeg": 2.0,
    "scale": 1.02,
    "source": "analysis_outputs/source_audit/registration_rotation_scale_76_79.md",
}


def transform_point(point: tuple[float, float], width: int, height: int, *, dx: float, dy: float, angle_deg: float, scale: float) -> tuple[float, float]:
    x, y = point
    cx, cy = width / 2, height / 2
    theta = math.radians(angle_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    x0 = (x - cx) * scale
    y0 = (y - cy) * scale
    xr = cos_t * x0 - sin_t * y0
    yr = sin_t * x0 + cos_t * y0
    return cx + xr + dx, cy + yr + dy


def transform_box(box: tuple[int, int, int, int], width: int, height: int, transform: dict) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    corners = [
        transform_point((x1, y1), width, height, dx=transform["dx"], dy=transform["dy"], angle_deg=transform["angleDeg"], scale=transform["scale"]),
        transform_point((x2, y1), width, height, dx=transform["dx"], dy=transform["dy"], angle_deg=transform["angleDeg"], scale=transform["scale"]),
        transform_point((x2, y2), width, height, dx=transform["dx"], dy=transform["dy"], angle_deg=transform["angleDeg"], scale=transform["scale"]),
        transform_point((x1, y2), width, height, dx=transform["dx"], dy=transform["dy"], angle_deg=transform["angleDeg"], scale=transform["scale"]),
    ]
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return (int(round(min(xs))), int(round(min(ys))), int(round(max(xs))), int(round(max(ys))))


def overlap_edges(sources: list[dict], targets: list[tuple[str, dict]]) -> list[dict]:
    edges = []
    for src in sources:
        for color, tgt in targets:
            inter = intersection(src["mappedBox"], tgt["box"])
            if not inter:
                continue
            ia = area(inter)
            if ia <= 0:
                continue
            ca = center(src["mappedBox"])
            cb = center(tgt["box"])
            edges.append(
                {
                    "sourceIndex": src["index"],
                    "sourceLabel": src["label"],
                    "sourceBox": src["sourceBox"],
                    "hflipBox": src["hflipBox"],
                    "mappedBox": src["mappedBox"],
                    "targetColor": color,
                    "targetIndex": tgt["index"],
                    "targetLabel": tgt["label"],
                    "targetBox": tgt["box"],
                    "overlapArea": ia,
                    "overlapVsSource": round(ia / area(src["mappedBox"]), 5),
                    "overlapVsTarget": round(ia / area(tgt["box"]), 5),
                    "centerDistance": round(float(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5), 2),
                }
            )
    edges.sort(key=lambda e: (e["targetColor"], e["targetIndex"], -max(e["overlapVsSource"], e["overlapVsTarget"])))
    return edges


def draw_overlay(target_img: Image.Image, target_orange: list[dict], target_grey: list[dict], registered_sources: list[dict]) -> None:
    out = target_img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for item in target_orange:
        draw.rectangle(item["box"], outline=(255, 80, 0, 255), width=6)
        draw.text((item["box"][0], max(0, item["box"][1] - 26)), f"O{item['index']}", fill=(255, 80, 0, 255))
    for item in target_grey:
        draw.rectangle(item["box"], outline=(0, 210, 255, 255), width=6)
        draw.text((item["box"][0], max(0, item["box"][1] - 26)), f"B{item['index']}", fill=(0, 170, 220, 255))
    for item in registered_sources:
        draw.rectangle(item["mappedBox"], outline=(180, 0, 255, 205), width=5)
        draw.text((item["mappedBox"][0], max(0, item["mappedBox"][1] - 22)), f"79:{item['index']}", fill=(180, 0, 255, 255))
    combined = Image.alpha_composite(out, overlay).convert("RGB")
    combined.save(OUT_IMG, quality=94)
    combined.crop((250, 250, 2300, 1700)).save(OUT_CROP, quality=94)


def edge_pattern(edges: list[dict]) -> str:
    return "".join(("O" if e["targetColor"] == "orange" else "B") + str(e["targetIndex"]) for e in edges)


def main() -> None:
    ensure_highres_sources()
    target_img = upright_image(76)
    width, height = target_img.size
    target_orange = attach_labels(orange_boxes(76)[0], PAGE76_ORANGE_LABELS)
    target_grey = manual_page76_grey_boxes()
    targets = [("orange", item) for item in target_orange] + [("black", item) for item in target_grey]

    p79_boxes, p79_size = orange_boxes(79)
    source_items = attach_labels(p79_boxes, PAGE79_ORANGE_LABELS)
    raw_sources = []
    registered_sources = []
    for item in source_items:
        hflipped = hflip_box(item["box"], p79_size[0])
        raw_sources.append(
            {
                "index": item["index"],
                "label": item["label"],
                "sourceBox": item["box"],
                "hflipBox": hflipped,
                "mappedBox": hflipped,
            }
        )
        registered_sources.append(
            {
                "index": item["index"],
                "label": item["label"],
                "sourceBox": item["box"],
                "hflipBox": hflipped,
                "mappedBox": transform_box(hflipped, width, height, BEST_TRANSFORM),
            }
        )

    raw_edges = overlap_edges(raw_sources, targets)
    registered_edges = overlap_edges(registered_sources, targets)
    meaningful = [
        e
        for e in registered_edges
        if e["overlapVsSource"] >= 0.01 or e["overlapVsTarget"] >= 0.01
    ]
    draw_overlay(target_img, target_orange, target_grey, registered_sources)

    result = {
        "source": "high-res magazine page 76/79 boxes only",
        "transform": BEST_TRANSFORM,
        "overlay": str(OUT_IMG),
        "crop": str(OUT_CROP),
        "targetOrange": target_orange,
        "targetGrey": target_grey,
        "rawSources": raw_sources,
        "registeredSources": registered_sources,
        "rawEdges": raw_edges,
        "registeredEdges": registered_edges,
        "meaningfulRegisteredEdges": meaningful,
        "summary": {
            "rawEdges": len(raw_edges),
            "registeredEdges": len(registered_edges),
            "meaningfulRegisteredEdges": len(meaningful),
            "rawPattern": edge_pattern(raw_edges),
            "registeredPattern": edge_pattern(meaningful),
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Registered 76/79 Selector Audit",
        "",
        "Scope: apply the best high-res 76/79 mirror registration transform to page-79 orange highlight boxes, then remeasure which page-76 orange/grey targets they hit. This is a visual-selector test, not key derivation.",
        "",
        f"- Transform source: `{BEST_TRANSFORM['source']}`",
        f"- Transform: dx={BEST_TRANSFORM['dx']}, dy={BEST_TRANSFORM['dy']}, angle={BEST_TRANSFORM['angleDeg']}, scale={BEST_TRANSFORM['scale']}",
        f"- Overlay: `{OUT_IMG}`",
        f"- Crop: `{OUT_CROP}`",
        "",
        "## Summary",
        "",
        f"- Raw p79 hflip intersections: {len(raw_edges)} pattern `{edge_pattern(raw_edges)}`",
        f"- Registered p79 intersections: {len(registered_edges)}",
        f"- Meaningful registered intersections: {len(meaningful)} pattern `{edge_pattern(meaningful)}`",
        "",
        "## Meaningful Registered Intersections",
        "",
    ]
    if meaningful:
        for e in meaningful:
            lines.append(
                f"- p79 box {e['sourceIndex']} `{e['sourceLabel']}` -> "
                f"p76 {e['targetColor']} {e['targetIndex']} `{e['targetLabel']}` "
                f"(source={e['overlapVsSource']:.3f}, target={e['overlapVsTarget']:.3f}, dist={e['centerDistance']:.1f})"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The improved visual registration changes the p79 hit pattern and gives one strong line-level alignment.",
            "- p79 box 1 (`infinitely more efficient...`) lands almost exactly on p76 grey box 1 (`Gotta be this way... post-1971 fiat money`): 77.0% of the target box is covered and the centers are only about 10 px apart.",
            "- The same source box also clips the p76 `nonsense` continuation, so this is probably a broad line/row alignment rather than a word- or character-level selector.",
            "- This promotes the transform as a useful orientation/registration clue, but it still does not provide a final extraction rule by itself.",
            "- Next best move: use this registered line pair as a local anchor and inspect whether nearby p79/p76 typography, highlights, or Typeka states produce a smaller readable rule around the page-76 corridor.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"wrote {OUT_CROP}")


if __name__ == "__main__":
    main()
