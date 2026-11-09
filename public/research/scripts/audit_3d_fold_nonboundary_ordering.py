#!/usr/bin/env python3
"""Inspect whether the 3D fold layout creates a non-boundary ordering cue."""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "3d_article_map" / "fold_nonboundary_ordering"

MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ANCHORS_JSON = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
VIEWER_JS = ROOT / "analysis_outputs/3d_article_map/viewer.js"

PAGE_SCALE = 0.22
FOLD_POSITIONS = {
    75: [-280.0, 320.0, -130.0, 0.42],
    79: [280.0, 320.0, -130.0, -0.42],
    76: [-280.0, -380.0, 130.0, 0.42],
    78: [280.0, -380.0, 130.0, -0.42],
    77: [0.0, -20.0, 330.0, 0.0],
    80: [610.0, -20.0, 420.0, -0.2],
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def box_center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def overlap_area(a: list[float], b: list[float]) -> float:
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    return max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)


def page_local(page: dict[str, Any], x: float, y: float, z: float = 0.0) -> tuple[float, float, float]:
    return ((x - page["width"] / 2) * PAGE_SCALE, (page["height"] / 2 - y) * PAGE_SCALE, z)


def page_world(page: dict[str, Any], x: float, y: float, z: float = 0.0) -> tuple[float, float, float]:
    px, py, pz, rot_y = FOLD_POSITIONS[page["page"]]
    lx, ly, lz = page_local(page, x, y, z)
    cos_t = math.cos(rot_y)
    sin_t = math.sin(rot_y)
    wx = px + cos_t * lx + sin_t * lz
    wy = py + ly
    wz = pz - sin_t * lx + cos_t * lz
    return (round(wx, 2), round(wy, 2), round(wz, 2))


def dist3(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return round(math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3))), 2)


def draw_plan(page_map: dict[int, dict[str, Any]], anchors: list[dict[str, Any]], original_pills: list[dict[str, Any]]) -> str:
    width, height = 1500, 1000
    image = Image.new("RGB", (width, height), "#101216")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
        small = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    xs = [v[0] for v in FOLD_POSITIONS.values()]
    zs = [v[2] for v in FOLD_POSITIONS.values()]
    min_x, max_x = min(xs) - 260, max(xs) + 260
    min_z, max_z = min(zs) - 180, max(zs) + 180

    def project(world: tuple[float, float, float]) -> tuple[float, float]:
        x, _y, z = world
        sx = 80 + (x - min_x) / (max_x - min_x) * (width - 160)
        sy = height - (80 + (z - min_z) / (max_z - min_z) * (height - 160))
        return (sx, sy)

    for page_no, page in page_map.items():
        px, _py, pz, rot = FOLD_POSITIONS[page_no]
        w = page["width"] * PAGE_SCALE
        h = page["height"] * PAGE_SCALE
        corners_local = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
        cos_t = math.cos(rot)
        sin_t = math.sin(rot)
        corners = []
        for lx, ly, lz in corners_local:
            wx = px + cos_t * lx + sin_t * lz
            wz = pz - sin_t * lx + cos_t * lz
            corners.append(project((wx, 0, wz)))
        draw.polygon(corners, fill=(40, 48, 60, 180), outline=(120, 140, 165, 255))
        cx, cy = project((px, 0, pz))
        draw.text((cx - 18, cy - 12), str(page_no), fill=(240, 247, 250, 255), font=font)

    for a in anchors:
        sx, sy = project(tuple(a["world"]))
        color = (255, 155, 46, 255) if a["color"] == "orange" else (240, 240, 240, 255)
        draw.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=color)
        draw.text((sx + 9, sy - 8), a["id"], fill=color, font=small)

    for pill in original_pills:
        sx, sy = project(tuple(pill["world"]))
        draw.rectangle([sx - 5, sy - 5, sx + 5, sy + 5], fill=(255, 80, 180, 255))
        draw.text((sx + 7, sy - 7), pill["id"].replace("p79_", "").replace("_original", ""), fill=(255, 80, 180, 255), font=small)

    out = OUT_DIR / "fold_nonboundary_ordering_plan.jpg"
    image.save(out, quality=92)
    return str(out.relative_to(ROOT))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_json(MAP_JSON)
    anchor_data = load_json(ANCHORS_JSON)
    page_map = {page["page"]: page for page in data["pages"]}

    active_ids = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]
    anchors = []
    for anchor in anchor_data["anchors"]:
        if anchor["id"] in active_ids:
            cx, cy = box_center(anchor["box"])
            world = page_world(page_map[76], cx, cy)
            anchors.append(
                {
                    "id": anchor["id"],
                    "label": anchor["label"],
                    "color": anchor["color"],
                    "box": anchor["box"],
                    "center": [round(cx, 2), round(cy, 2)],
                    "world": list(world),
                }
            )
    anchors.sort(key=lambda item: active_ids.index(item["id"]))

    orders = {
        "page76VisualTopToBottom": [a["id"] for a in sorted(anchors, key=lambda item: item["center"][1])],
        "foldDepthFrontToBackZLowToHigh": [a["id"] for a in sorted(anchors, key=lambda item: item["world"][2])],
        "foldXLeftToRight": [a["id"] for a in sorted(anchors, key=lambda item: item["world"][0])],
    }

    pair_symmetry = [
        {"pair": [75, 79], "sameFoldRow": True, "sameFoldDepth": True, "rotations": [FOLD_POSITIONS[75][3], FOLD_POSITIONS[79][3]]},
        {"pair": [76, 78], "sameFoldRow": True, "sameFoldDepth": True, "rotations": [FOLD_POSITIONS[76][3], FOLD_POSITIONS[78][3]]},
        {"pair": [79, 76], "sameFoldRow": False, "sameFoldDepth": False, "rotations": [FOLD_POSITIONS[79][3], FOLD_POSITIONS[76][3]]},
    ]

    # Original p79 pills in fold space: used only as orientation markers, not selectors.
    original_pills = []
    for item in data["anchors"]:
        if item["page"] == 79 and item["id"].endswith("_original"):
            world = page_world(page_map[79], item["point"][0], item["point"][1], 42)
            original_pills.append({"id": item["id"], "point": item["point"], "world": list(world)})

    # Check whether reflection rectangles that previously selected page-76 text become
    # visually close to the active anchors in the 3D fold display itself.
    reflection_rows = []
    for reflection in data["reflections"]:
        if reflection["target"] != 76:
            continue
        target_center = box_center(reflection["targetBox"])
        target_world = page_world(page_map[76], target_center[0], target_center[1], 22)
        source_center = box_center(reflection["sourceBox"])
        source_world = page_world(page_map[reflection["source"]], source_center[0], source_center[1], 22)
        best_anchor = None
        for anchor in anchors:
            area = overlap_area(reflection["targetBox"], anchor["box"])
            distance = dist3(target_world, tuple(anchor["world"]))
            candidate = {"anchor": anchor["id"], "overlapArea": round(area, 2), "targetWorldDistance": distance}
            if best_anchor is None or (candidate["overlapArea"], -candidate["targetWorldDistance"]) > (
                best_anchor["overlapArea"],
                -best_anchor["targetWorldDistance"],
            ):
                best_anchor = candidate
        reflection_rows.append(
            {
                "id": reflection["id"],
                "source": reflection["source"],
                "target": reflection["target"],
                "textPreview": (reflection.get("text") or reflection.get("chars") or "")[:90],
                "sourceWorld": list(source_world),
                "targetWorld": list(target_world),
                "sourceToTargetFoldDistance": dist3(source_world, target_world),
                "bestActiveAnchor": best_anchor,
            }
        )

    close_reflections = [
        row
        for row in reflection_rows
        if row["bestActiveAnchor"] and (row["bestActiveAnchor"]["overlapArea"] > 0 or row["bestActiveAnchor"]["targetWorldDistance"] <= 90)
    ]
    close_reflections.sort(
        key=lambda row: (
            -row["bestActiveAnchor"]["overlapArea"],
            row["bestActiveAnchor"]["targetWorldDistance"],
            row["sourceToTargetFoldDistance"],
        )
    )

    overlay = draw_plan(page_map, anchors, original_pills)

    assessment = [
        "The viewer's fold layout itself pairs pages 75/79 and 76/78 as symmetric rows; page 79 and page 76 are diagonal in the fold display, not a direct folded pair.",
        "Within page 76, the active O-B-B-O anchors keep ordinary page order top-to-bottom. The alternative depth ordering is just a yaw artifact of the page-76 plane, not an independent clue.",
        "Original p79 pill markers sit on the top-row p79 plane in the fold layout; their mirrored copies on page 76 are already an overlay hypothesis, not a new fold-view order.",
        "Reflected rectangles that land near the active lower corridor remain far apart from their source rectangles in fold-world distance; the 3D fold view does not create a new physical contact or ordering cue.",
        "This keeps the 3D fold view useful as orientation/provenance evidence only. A new selector must come from source/physical instruction, not another fold-display order.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D fold non-boundary ordering audit; no text extraction/key derivation",
        "sources": {
            "mapData": str(MAP_JSON.relative_to(ROOT)),
            "anchorData": str(ANCHORS_JSON.relative_to(ROOT)),
            "viewer": str(VIEWER_JS.relative_to(ROOT)),
        },
        "foldPositionsFromViewer": FOLD_POSITIONS,
        "overlay": overlay,
        "activeAnchors": anchors,
        "orders": orders,
        "pairSymmetry": pair_symmetry,
        "originalP79Pills": original_pills,
        "closeReflectionRows": close_reflections[:12],
        "assessment": assessment,
        "decision": "Do not promote 3D fold display ordering to extraction evidence; it is an orientation view.",
        "nextMove": "Stop deriving selectors from display geometry; the next bounded pass should audit source/provenance clues for an explicit extraction instruction or compare physical/source images if available.",
    }

    (OUT_DIR / "fold_nonboundary_ordering.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# 3D Fold Non-Boundary Ordering",
        "",
        "Scope: inspect whether the 3D fold view reveals an ordering cue that is not just box boundaries. No text extraction, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{overlay}`",
        "",
        "## Fold Pairing From Viewer",
        "",
        "| pair | same row | same depth | rotations |",
        "|---|---|---|---|",
    ]
    for row in pair_symmetry:
        lines.append(f"| `{row['pair']}` | `{row['sameFoldRow']}` | `{row['sameFoldDepth']}` | `{row['rotations']}` |")

    lines.extend(["", "## Active Anchor World Positions", "", "| id | label | color | page center | fold world xyz |", "|---|---|---|---|---|"])
    for anchor in anchors:
        lines.append(f"| `{anchor['id']}` | `{anchor['label']}` | `{anchor['color']}` | `{anchor['center']}` | `{anchor['world']}` |")

    lines.extend(["", "## Orders Checked", ""])
    for name, order in orders.items():
        lines.append(f"- `{name}`: `{' -> '.join(order)}`")

    lines.extend(["", "## Reflection Rows Near Active Anchors", "", "| reflection | source | preview | best anchor | overlap | target distance | source-target fold distance |", "|---|---:|---|---|---:|---:|---:|"])
    if close_reflections:
        for row in close_reflections[:12]:
            best = row["bestActiveAnchor"]
            lines.append(
                f"| `{row['id']}` | `{row['source']}` | `{row['textPreview']}` | `{best['anchor']}` | `{best['overlapArea']}` | `{best['targetWorldDistance']}` | `{row['sourceToTargetFoldDistance']}` |"
            )
    else:
        lines.append("| - | - | - | - | - | - | - |")

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {result['decision']}", f"- Next move: {result['nextMove']}", ""])
    (OUT_DIR / "fold_nonboundary_ordering.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
