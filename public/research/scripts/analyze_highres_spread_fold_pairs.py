#!/usr/bin/env python3
"""High-res physical spread/fold audit.

Even pages are left pages and odd pages are right pages. Folding a right page
onto the left across the spine maps local x -> W - x, and the same is true in
reverse. This script tests the true facing spreads available in the article:
76/77 and 78/79.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from highres_reflection_extract import ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
MANUAL_ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
MANUAL_GREY = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
OUT_JSON = OUT / "highres_spread_fold_pairs.json"
OUT_MD = OUT / "highres_spread_fold_pairs.md"
OUT_IMG = OUT / "highres_spread_fold_pairs_contact_sheet.jpg"


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def intersection(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    return None if x2 <= x1 or y2 <= y1 else (x1, y1, x2, y2)


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def hflip_box(box, width):
    x1, y1, x2, y2 = box
    return (width - x2, y1, width - x1, y2)


def labels_for_orange(page):
    with MANUAL_ORANGE.open() as f:
        data = json.load(f)
    prefix = f"p{page}_orange_"
    numbered = []
    for key, text in data["visualOrangeBoxes"].items():
        if key.startswith(prefix) and not text.startswith("["):
            numbered.append((int(key.rsplit("_", 1)[1]), text))
    return [text for _, text in sorted(numbered)]


def orange_items(page):
    labels = labels_for_orange(page)
    boxes, _ = orange_boxes(page)
    items = []
    for i, box in enumerate(boxes, 1):
        items.append(
            {
                "kind": "orange",
                "page": page,
                "index": i,
                "box": tuple(int(v) for v in box),
                "label": labels[i - 1] if i - 1 < len(labels) else f"orange {i}",
            }
        )
    return items


def grey_items(page):
    with MANUAL_GREY.open() as f:
        data = json.load(f)
    rows = [r for r in data["rows"] if r["page"] == page]
    rows.sort(key=lambda r: r["id"])
    items = []
    for i, row in enumerate(rows, 1):
        items.append(
            {
                "kind": "grey",
                "page": page,
                "index": i,
                "box": tuple(int(round(v)) for v in row["highresBox"]),
                "label": row["expected"],
            }
        )
    return items


def draw_pair_panel(target_page, source_page, targets, reflected_sources, edges):
    img = upright_image(target_page).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for t in targets:
        color = (255, 85, 0, 255) if t["kind"] == "orange" else (0, 210, 230, 255)
        prefix = "O" if t["kind"] == "orange" else "G"
        draw.rectangle(t["box"], outline=color, width=5)
        draw.text((t["box"][0], max(0, t["box"][1] - 24)), f"{prefix}{t['index']}", fill=color)
    for s in reflected_sources:
        draw.rectangle(s["reflectedBox"], outline=(190, 0, 255, 210), width=4)
        draw.text((s["reflectedBox"][0], max(0, s["reflectedBox"][1] - 20)), f"{source_page}:{s['index']}", fill=(190, 0, 255, 255))
    for e in edges:
        draw.rectangle(e["intersection"], outline=(20, 255, 20, 255), width=4)

    combined = Image.alpha_composite(img, overlay).convert("RGB")
    # Crop to content-ish center for a readable contact sheet.
    combined.thumbnail((900, 1150), Image.Resampling.LANCZOS)
    return combined


def audit_direction(source_page, target_page):
    width = upright_image(source_page).width
    sources = []
    for item in orange_items(source_page):
        reflected = dict(item)
        reflected["sourceBox"] = reflected.pop("box")
        reflected["reflectedBox"] = hflip_box(reflected["sourceBox"], width)
        sources.append(reflected)

    targets = orange_items(target_page) + grey_items(target_page)
    edges = []
    for src in sources:
        for tgt in targets:
            inter = intersection(src["reflectedBox"], tgt["box"])
            if not inter:
                continue
            ia = area(inter)
            if ia <= 0:
                continue
            ca = center(src["reflectedBox"])
            cb = center(tgt["box"])
            edge = {
                "sourcePage": source_page,
                "targetPage": target_page,
                "sourceIndex": src["index"],
                "sourceLabel": src["label"],
                "targetKind": tgt["kind"],
                "targetIndex": tgt["index"],
                "targetLabel": tgt["label"],
                "intersection": inter,
                "overlapArea": ia,
                "overlapVsSource": round(ia / area(src["reflectedBox"]), 5),
                "overlapVsTarget": round(ia / area(tgt["box"]), 5),
                "centerDistance": round(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5, 2),
            }
            if edge["overlapVsSource"] >= 0.01 or edge["overlapVsTarget"] >= 0.01:
                edges.append(edge)

    edges.sort(key=lambda e: (e["targetKind"], e["targetIndex"], -max(e["overlapVsSource"], e["overlapVsTarget"])))
    return {
        "sourcePage": source_page,
        "targetPage": target_page,
        "sourceCount": len(sources),
        "targetCount": len(targets),
        "meaningfulEdges": edges,
        "targetPattern": "".join(("O" if e["targetKind"] == "orange" else "G") + str(e["targetIndex"]) for e in edges),
        "panel": draw_pair_panel(target_page, source_page, targets, sources, edges),
    }


def main():
    ensure_highres_sources()
    directions = [(77, 76), (76, 77), (79, 78), (78, 79)]
    reports = [audit_direction(src, tgt) for src, tgt in directions]

    panel_w = max(r["panel"].width for r in reports)
    panel_h = max(r["panel"].height for r in reports)
    sheet = Image.new("RGB", (panel_w * 2, panel_h * 2), "white")
    for i, r in enumerate(reports):
        panel = r["panel"]
        x = (i % 2) * panel_w
        y = (i // 2) * panel_h
        sheet.paste(panel, (x, y))
    sheet.save(OUT_IMG, quality=92)

    result = {
        "source": "high-res magazine spread geometry",
        "contactSheet": str(OUT_IMG),
        "directions": [
            {k: v for k, v in r.items() if k != "panel"}
            for r in reports
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# High-Res Spread Fold Pairs",
        "",
        "Scope: true facing-spread geometry on high-res magazine pages. Tests 76/77 and 78/79 by reflecting orange highlights across the spine onto the opposite page's orange and grey/black highlights.",
        "",
        f"- Contact sheet: `{OUT_IMG}`",
        "",
        "## Results",
        "",
    ]
    for r in reports:
        lines.append(
            f"### {r['sourcePage']} -> {r['targetPage']}"
        )
        lines.append(f"- source orange boxes: {r['sourceCount']}")
        lines.append(f"- target highlight boxes: {r['targetCount']}")
        lines.append(f"- meaningful intersections: {len(r['meaningfulEdges'])}")
        lines.append(f"- target pattern: `{r['targetPattern']}`")
        if r["meaningfulEdges"]:
            for e in r["meaningfulEdges"]:
                lines.append(
                    f"- p{e['sourcePage']} box {e['sourceIndex']} `{e['sourceLabel']}` -> "
                    f"p{e['targetPage']} {e['targetKind']} {e['targetIndex']} `{e['targetLabel']}` "
                    f"(source={e['overlapVsSource']:.3f}, target={e['overlapVsTarget']:.3f}, dist={e['centerDistance']:.1f})"
                )
        lines.append("")

    lines.extend(
        [
            "## Assessment",
            "",
            "- True high-res facing-spread folds do not produce a clean one-to-one selector across the available article spreads.",
            "- Any hits should be treated as regional/semantic evidence only unless a separate instruction tells us why that spread and direction should be chosen.",
            "- The page-76 corridor remains stronger than the spread-pair output, so the next move is not more generic spread folding. It is either a physical scan/alignment or one explicit mirror-writing read rule on the page-76 corridor.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
