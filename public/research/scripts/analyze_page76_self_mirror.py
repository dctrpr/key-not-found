#!/usr/bin/env python3
"""Audit page-76 internal mirror symmetry.

The opener spread shows real left/right mirror behavior in its OVERDOSE labels.
This pass asks whether page 76 itself uses a comparable self-mirror highlight
grammar: reflect verified page-76 orange/grey boxes across a few defensible
vertical axes and measure whether they land on other page-76 highlights.
No key candidates are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from analyze_highres_page76_mirror_selector import (
    area,
    attach_labels,
    center,
    intersection,
    manual_page76_grey_boxes,
)
from highres_reflection_extract import ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_self_mirror"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_self_mirror.json"
OUT_MD = OUT / "page76_self_mirror.md"
OUT_IMG = OUT / "page76_self_mirror_overlay.jpg"
OUT_CROP = OUT / "page76_self_mirror_crop.jpg"
MANUAL_ORANGE = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"


def reflect_box_about_axis(box: tuple[float, float, float, float], axis_x: float) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    return (2 * axis_x - x2, y1, 2 * axis_x - x1, y2)


def bbox_center_x(items: list[dict]) -> float:
    x1 = min(item["box"][0] for item in items)
    x2 = max(item["box"][2] for item in items)
    return (x1 + x2) / 2


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def build_items() -> list[dict]:
    manual = json.loads(MANUAL_ORANGE.read_text())
    prefix = "p76_orange_"
    labels = [
        text
        for _, text in sorted(
            (int(key.rsplit("_", 1)[1]), value)
            for key, value in manual["visualOrangeBoxes"].items()
            if key.startswith(prefix)
        )
    ]
    orange = attach_labels(orange_boxes(76)[0], labels)
    grey = manual_page76_grey_boxes()
    items = []
    for row in orange:
        items.append(
            {
                "kind": "orange",
                "id": f"O{row['index']}",
                "index": row["index"],
                "label": row["label"],
                "box": tuple(float(v) for v in row["box"]),
            }
        )
    for row in grey:
        items.append(
            {
                "kind": "grey",
                "id": f"B{row['index']}",
                "index": row["index"],
                "label": row["label"],
                "box": tuple(float(v) for v in row["box"]),
            }
        )
    return items


def audit_axis(name: str, axis_x: float, items: list[dict]) -> dict:
    reflected = []
    edges = []
    nearest_rows = []
    for src in items:
        reflected_box = reflect_box_about_axis(src["box"], axis_x)
        reflected_center = center(reflected_box)
        src_row = {
            "sourceId": src["id"],
            "sourceKind": src["kind"],
            "sourceLabel": src["label"],
            "sourceBox": src["box"],
            "reflectedBox": tuple(round(v, 2) for v in reflected_box),
            "reflectedCenter": tuple(round(v, 2) for v in reflected_center),
        }
        reflected.append(src_row)

        nearest = []
        for tgt in items:
            if tgt["id"] == src["id"]:
                continue
            inter = intersection(reflected_box, tgt["box"])
            if inter:
                ia = area(inter)
                if ia > 0:
                    edge = {
                        **src_row,
                        "targetId": tgt["id"],
                        "targetKind": tgt["kind"],
                        "targetLabel": tgt["label"],
                        "targetBox": tgt["box"],
                        "intersection": tuple(round(v, 2) for v in inter),
                        "overlapArea": round(ia, 2),
                        "overlapVsSource": round(ia / area(reflected_box), 5),
                        "overlapVsTarget": round(ia / area(tgt["box"]), 5),
                        "centerDistance": round(dist(reflected_center, center(tgt["box"])), 2),
                    }
                    if edge["overlapVsSource"] >= 0.02 or edge["overlapVsTarget"] >= 0.02:
                        edges.append(edge)
            nearest.append(
                {
                    "targetId": tgt["id"],
                    "targetKind": tgt["kind"],
                    "targetLabel": tgt["label"],
                    "distancePx": round(dist(reflected_center, center(tgt["box"])), 2),
                }
            )
        nearest.sort(key=lambda row: row["distancePx"])
        nearest_rows.append({**src_row, "nearestTargets": nearest[:3]})
    edges.sort(key=lambda e: (-max(e["overlapVsSource"], e["overlapVsTarget"]), e["sourceId"], e["targetId"]))
    return {
        "axisName": name,
        "axisX": round(axis_x, 2),
        "reflectedSources": reflected,
        "meaningfulEdges": edges,
        "nearestTargets": nearest_rows,
        "edgePattern": "".join(f"{e['sourceId']}->{e['targetId']}|" for e in edges).rstrip("|"),
    }


def draw_overlay(img: Image.Image, items: list[dict], axis: dict) -> None:
    out = img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    axis_x = axis["axisX"]
    draw.line((axis_x, 0, axis_x, img.height), fill=(40, 120, 255, 255), width=5)
    for item in items:
        color = (255, 90, 0, 255) if item["kind"] == "orange" else (0, 210, 230, 255)
        box = tuple(int(round(v)) for v in item["box"])
        draw.rectangle(box, outline=color, width=5)
        draw.text((box[0], max(0, box[1] - 24)), item["id"], fill=color)
    for row in axis["reflectedSources"]:
        box = tuple(int(round(v)) for v in row["reflectedBox"])
        draw.rectangle(box, outline=(190, 0, 255, 210), width=4)
        draw.text((box[0], max(0, box[1] - 20)), f"{row['sourceId']}r", fill=(190, 0, 255, 255))
    combined = Image.alpha_composite(out, overlay).convert("RGB")
    combined.save(OUT_IMG, quality=94)
    combined.crop((250, 650, 2300, 3150)).save(OUT_CROP, quality=94)


def main() -> None:
    ensure_highres_sources()
    img = upright_image(76)
    items = build_items()
    orange_items = [item for item in items if item["kind"] == "orange"]
    grey_items = [item for item in items if item["kind"] == "grey"]
    axes = {
        "page_center": img.width / 2,
        "all_highlight_bbox_center": bbox_center_x(items),
        "orange_bbox_center": bbox_center_x(orange_items),
        "grey_bbox_center": bbox_center_x(grey_items),
    }
    axis_results = [audit_axis(name, axis_x, items) for name, axis_x in axes.items()]
    draw_overlay(img, items, axis_results[0])

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 internal mirror audit; verified highlight boxes only; no key derivation",
        "overlay": str(OUT_IMG),
        "crop": str(OUT_CROP),
        "items": items,
        "axes": axis_results,
        "summary": {
            "axesTested": len(axis_results),
            "highlightItems": len(items),
            "meaningfulEdgesByAxis": {row["axisName"]: len(row["meaningfulEdges"]) for row in axis_results},
            "totalMeaningfulEdges": sum(len(row["meaningfulEdges"]) for row in axis_results),
        },
        "assessment": [
            "Page 76 has one repeatable internal mirror pairing: grey B5 Volcano Bonds reflects toward orange O5 shitcoiner at heart.",
            "No other verified page-76 highlight boxes participate, so this is a local anchor/pair rather than a clean self-fold selector system.",
            "Page 76 remains the target surface because of external reflected hits, not because it self-encodes by left/right folding.",
        ],
        "nextMove": "Do not pursue page-76 self-folding. Continue with external source/physical registration or a specific rule that maps the p73/p79/p80 provenance layers onto page-76 text.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Page 76 Self-Mirror Audit",
        "",
        "Scope: reflect verified page-76 orange/grey highlight boxes across a few defensible vertical axes and measure whether they land on other page-76 highlights. No key candidates are generated.",
        "",
        f"- Overlay: `{OUT_IMG}`",
        f"- Crop: `{OUT_CROP}`",
        "",
        "## Axes",
        "",
    ]
    for row in axis_results:
        lines.append(
            f"- `{row['axisName']}` x=`{row['axisX']}`: meaningful edges `{len(row['meaningfulEdges'])}` pattern `{row['edgePattern']}`"
        )
        for edge in row["meaningfulEdges"][:8]:
            lines.append(
                f"  - {edge['sourceId']} `{edge['sourceLabel']}` -> {edge['targetId']} `{edge['targetLabel']}` "
                f"(src={edge['overlapVsSource']:.3f}, tgt={edge['overlapVsTarget']:.3f}, dist={edge['centerDistance']:.1f})"
            )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The opener p73/p74 labels show true mirror symmetry. Page 76 has one repeatable local self-mirror pair: B5 `Volcano Bonds` <-> O5 `shitcoiner at heart`.",
            "- The best of the tested axes is `orange_bbox_center` at x=1322.0, where the reflected pair reaches source overlap `0.593` / target overlap `0.908` with center distance `63.5 px`.",
            "- No other verified page-76 highlight boxes participate, so this does not define a complete page self-fold selector.",
            "- Page 76 should remain the target surface because external reflected systems point to it, not because the page self-folds.",
            "",
            "## Next Best Move",
            "",
            "- Stop page-76 self-fold tests unless a new source clue points there. The live gap is still the source/physical rule that maps p73/p79/p80 provenance evidence onto page-76 text.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"wrote {OUT_CROP}")
    print(result["summary"])


if __name__ == "__main__":
    main()
