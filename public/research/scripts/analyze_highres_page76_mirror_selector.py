#!/usr/bin/env python3
"""High-res-only mirror selector audit for page 76.

This avoids OCR PDF geometry completely. It reflects high-res orange highlight
boxes from pages 78 and 79 onto the high-res page-76 image, then measures their
intersections with high-res page-76 orange and black/grey highlight boxes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from extract_visual_masks import connected_components, dilate, masks_for_page, merge_close_boxes
from highres_reflection_extract import SOURCE_PAGES, ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "highres_page76_mirror_selector.json"
OUT_MD = OUT / "highres_page76_mirror_selector.md"
OUT_IMG = OUT / "highres_page76_mirror_selector_overlay.jpg"
MANUAL_GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"

PAGE76_ORANGE_LABELS = [
    "Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.",
    "by the rancid catnip of fiat money.",
    "buying the dip.",
    "shitcoiner at heart.",
]

PAGE76_GREY_LABELS = [
    "Gotta be this way. Forty years of dumb post-1971 fiat money nonsense",
    "nonsense",
    "It's a stun gun to the genitals.",
    "$1 billion",
    "Volcano Bonds",
]

PAGE78_ORANGE_LABELS = [
    "The numbers don't lie.",
    "America left $85 BILLION worth of hate toys in Afghanistan,",
    "$2 trillion fiat cuck-bucks.",
    "the game-theorized Bitcoin protocol,",
]

PAGE79_ORANGE_LABELS = [
    "infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold",
    "That's right, Bitcoin will take all the energy.",
    "all the energy.",
    "Everyone will live their own experience in the rabbit hole.",
    "We are getting our souls back and our minds.",
    "pill fragment 1",
    "pill fragment 2",
    "pill fragment 3",
    "pill fragment 4",
    "pill fragment 5",
]


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def intersection(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def hflip_box(box, width):
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def black_boxes_highres(page: int):
    img = upright_image(page)
    mask = masks_for_page(img)["black"]
    comp_mask = dilate(mask, 19)
    comps = connected_components(comp_mask, min_area=120)
    boxes = merge_close_boxes(comps, y_gap=22, x_gap=34)
    filtered = []
    for box in boxes:
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        fill = mask[y1:y2, x1:x2].mean()
        # Keep highlight bars, not ordinary bold text or page-edge artifacts.
        if width < 130 or height < 22:
            continue
        if width > img.width * 0.95 or height > img.height * 0.25:
            continue
        if fill < 0.12:
            continue
        filtered.append(box)
    return filtered, img.size


def manual_page76_grey_boxes():
    with MANUAL_GREY.open() as f:
        data = json.load(f)
    rows = [r for r in data["rows"] if r["page"] == 76]
    rows.sort(key=lambda r: r["id"])
    out = []
    for i, row in enumerate(rows, 1):
        box = tuple(int(round(v)) for v in row["highresBox"])
        out.append(
            {
                "index": i,
                "box": box,
                "label": row["expected"],
                "id": row["id"],
            }
        )
    return out


def attach_labels(boxes, labels):
    return [
        {
            "index": i + 1,
            "box": tuple(int(v) for v in box),
            "label": labels[i] if i < len(labels) else f"box {i + 1}",
        }
        for i, box in enumerate(boxes)
    ]


def draw_overlay(target_img, target_orange, target_black, reflected):
    out = target_img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for item in target_orange:
        draw.rectangle(item["box"], outline=(255, 70, 0, 255), width=6)
        draw.text((item["box"][0], max(0, item["box"][1] - 26)), f"O{item['index']}", fill=(255, 70, 0, 255))
    for item in target_black:
        draw.rectangle(item["box"], outline=(0, 220, 255, 255), width=6)
        draw.text((item["box"][0], max(0, item["box"][1] - 26)), f"B{item['index']}", fill=(0, 170, 220, 255))
    for item in reflected:
        color = (30, 80, 255, 190) if item["sourcePage"] == 78 else (190, 0, 255, 190)
        draw.rectangle(item["reflectedBox"], outline=color, width=5)
        draw.text(
            (item["reflectedBox"][0], max(0, item["reflectedBox"][1] - 20)),
            f"{item['sourcePage']}:{item['index']}",
            fill=color,
        )

    combined = Image.alpha_composite(out, overlay).convert("RGB")
    combined.save(OUT_IMG, quality=94)


def main() -> None:
    ensure_highres_sources()
    target_img = upright_image(76)
    target_orange = attach_labels(orange_boxes(76)[0], PAGE76_ORANGE_LABELS)
    # Use manual high-res grey boxes. Automatic black detection catches large X
    # artwork and merges unrelated rows, so it is diagnostic only.
    target_black = manual_page76_grey_boxes()

    reflected = []
    for source_page, labels in [(78, PAGE78_ORANGE_LABELS), (79, PAGE79_ORANGE_LABELS)]:
        boxes, size = orange_boxes(source_page)
        for item in attach_labels(boxes, labels):
            item["sourcePage"] = source_page
            item["sourceBox"] = item.pop("box")
            item["reflectedBox"] = hflip_box(item["sourceBox"], size[0])
            reflected.append(item)

    edges = []
    for src in reflected:
        for color, targets in [("orange", target_orange), ("black", target_black)]:
            for tgt in targets:
                inter = intersection(src["reflectedBox"], tgt["box"])
                if not inter:
                    continue
                ia = area(inter)
                if ia <= 0:
                    continue
                ca = center(src["reflectedBox"])
                cb = center(tgt["box"])
                edges.append(
                    {
                        "sourcePage": src["sourcePage"],
                        "sourceIndex": src["index"],
                        "sourceLabel": src["label"],
                        "sourceBox": src["sourceBox"],
                        "reflectedBox": src["reflectedBox"],
                        "targetColor": color,
                        "targetIndex": tgt["index"],
                        "targetLabel": tgt["label"],
                        "targetBox": tgt["box"],
                        "overlapArea": ia,
                        "overlapVsSource": round(ia / area(src["reflectedBox"]), 5),
                        "overlapVsTarget": round(ia / area(tgt["box"]), 5),
                        "centerDistance": round(float(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5), 2),
                    }
                )

    meaningful = [
        e
        for e in edges
        if e["overlapVsSource"] >= 0.01 or e["overlapVsTarget"] >= 0.01
    ]
    meaningful.sort(key=lambda e: (e["targetColor"], e["targetIndex"], -max(e["overlapVsSource"], e["overlapVsTarget"])))

    draw_overlay(target_img, target_orange, target_black, reflected)

    result = {
        "source": "high-res magazine images only",
        "overlay": str(OUT_IMG),
        "targetOrange": target_orange,
        "targetGrey": target_black,
        "reflectedSources": reflected,
        "edges": edges,
        "meaningfulEdges": meaningful,
        "summary": {
            "targetOrangeBoxes": len(target_orange),
            "targetGreyBoxes": len(target_black),
            "reflectedSourceBoxes": len(reflected),
            "allEdges": len(edges),
            "meaningfulEdges": len(meaningful),
            "targetHitPattern": "".join(
                ("O" if e["targetColor"] == "orange" else "B") + str(e["targetIndex"]) for e in meaningful
            ),
            "sourcePagePattern": "".join(str(e["sourcePage"]) for e in meaningful),
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# High-Res Page 76 Mirror Selector",
        "",
        "Scope: high-res magazine geometry only. Reflect orange highlight boxes from pages 78 and 79 onto high-res page 76, then measure intersections with high-res page-76 orange and black/grey highlight boxes.",
        "",
        f"- Overlay: `{OUT_IMG}`",
        "",
        "## Summary",
        "",
        f"- Page-76 orange boxes: {len(target_orange)}",
        f"- Page-76 manual grey/black text boxes: {len(target_black)}",
        f"- Reflected source boxes from p78/p79: {len(reflected)}",
        f"- Raw intersections: {len(edges)}",
        f"- Meaningful intersections: {len(meaningful)}",
        f"- Meaningful target pattern: `{result['summary']['targetHitPattern']}`",
        f"- Meaningful source-page pattern: `{result['summary']['sourcePagePattern']}`",
        "",
        "## Meaningful Intersections",
        "",
    ]
    if meaningful:
        for e in meaningful:
            lines.append(
                f"- p{e['sourcePage']} box {e['sourceIndex']} `{e['sourceLabel']}` -> "
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
            "- Direct high-res horizontal mirroring from pages 78/79 onto page 76 does not create a clean one-to-one selector across the page-76 highlighted phrases.",
            "- The useful signal remains regional: page-76 lower/middle highlighted areas are plausible targets, but simple high-res page-center hflip alone is not the final rule.",
            "- Next best move: use the high-res overlay as the base for a constrained manual mirror-writing rule, likely adding fold/spine translation or physical spread positioning rather than raw page-center hflip.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
