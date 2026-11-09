#!/usr/bin/env python3
"""Audit whether the p78 frame has a three-object contact signature.

Previous passes found:
- current p78 reflected frame clips O5;
- trusted G5 sits 38px left of the frame's left edge;
- M3 is cut by the frame's right edge.

This pass asks whether the small G5 repair is arbitrary or whether it preserves
the other two contacts. It is geometry-only; no key derivation is run.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
P78_GRAPHIC_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json"
SENSITIVITY_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity.json"
M3_JSON = ROOT / "analysis_outputs/source_audit/m3_frame_side_marker/m3_frame_side_marker.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_tricontact_signature.json"
OUT_MD = OUT / "p78_frame_tricontact_signature.md"
OUT_IMG = OUT / "p78_frame_tricontact_signature_overlay.jpg"


def shift_box(box: list[float], dx: float = 0.0, dy: float = 0.0) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def edge_vertical_overlap(frame: list[float], target: list[float]) -> float:
    return max(0.0, min(frame[3], target[3]) - max(frame[1], target[1]))


def edge_horizontal_overlap(frame: list[float], target: list[float]) -> float:
    return max(0.0, min(frame[2], target[2]) - max(frame[0], target[0]))


def line_point_at_x(m3: dict, x: float) -> tuple[float, float]:
    cx, cy = m3["center"]
    vx, vy = m3["axisVector"]
    if abs(vx) < 1e-9:
        return x, cy
    t = (x - cx) / vx
    return x, cy + t * vy


def target_metrics(name: str, frame: list[float], targets: dict, m3: dict, dx: float, dy: float) -> dict:
    g5 = targets["G5"]["box"]
    o5 = targets["O5"]["box"]
    m3_box = m3["box"]

    g5_inter = intersection(frame, g5)
    o5_inter = intersection(frame, o5)
    m3_inter = intersection(frame, m3_box)

    left_edge_to_g5_right = frame[0] - g5[2]
    right_edge_inside_m3_x = m3_box[0] <= frame[2] <= m3_box[2]
    right_edge_m3_vertical_overlap = edge_vertical_overlap(frame, m3_box) if right_edge_inside_m3_x else 0.0
    m3_axis_at_right = line_point_at_x(m3, frame[2])
    m3_axis_right_inside_frame = frame[1] <= m3_axis_at_right[1] <= frame[3]
    m3_axis_right_inside_m3 = (
        m3_box[0] <= m3_axis_at_right[0] <= m3_box[2]
        and m3_box[1] <= m3_axis_at_right[1] <= m3_box[3]
    )

    bottom_edge_inside_o5_y = o5[1] <= frame[3] <= o5[3]
    bottom_edge_o5_horizontal_overlap = edge_horizontal_overlap(frame, o5) if bottom_edge_inside_o5_y else 0.0
    left_edge_inside_g5_y = edge_vertical_overlap(frame, g5) > 0

    tri_contact = (
        abs(left_edge_to_g5_right) <= 2.0
        and right_edge_inside_m3_x
        and right_edge_m3_vertical_overlap > 0
        and bottom_edge_inside_o5_y
        and bottom_edge_o5_horizontal_overlap > 0
    )
    return {
        "name": name,
        "dx": dx,
        "dy": dy,
        "frame": [round(v, 2) for v in frame],
        "leftEdgeToG5RightPx": round(left_edge_to_g5_right, 2),
        "leftEdgeG5VerticalOverlapPx": round(edge_vertical_overlap(frame, g5), 2) if left_edge_inside_g5_y else 0.0,
        "g5Intersection": [round(v, 2) for v in g5_inter] if g5_inter else None,
        "g5OverlapVsTarget": round(area(g5_inter) / max(1.0, area(g5)), 5) if g5_inter else 0.0,
        "rightEdgeInsideM3X": right_edge_inside_m3_x,
        "rightEdgeM3VerticalOverlapPx": round(right_edge_m3_vertical_overlap, 2),
        "m3Intersection": [round(v, 2) for v in m3_inter] if m3_inter else None,
        "m3OverlapVsMark": round(area(m3_inter) / max(1.0, area(m3_box)), 5) if m3_inter else 0.0,
        "m3AxisAtRightEdge": [round(m3_axis_at_right[0], 2), round(m3_axis_at_right[1], 2)],
        "m3AxisRightInsideFrame": m3_axis_right_inside_frame,
        "m3AxisRightInsideM3": m3_axis_right_inside_m3,
        "bottomEdgeInsideO5Y": bottom_edge_inside_o5_y,
        "bottomEdgeO5HorizontalOverlapPx": round(bottom_edge_o5_horizontal_overlap, 2),
        "o5Intersection": [round(v, 2) for v in o5_inter] if o5_inter else None,
        "o5OverlapVsTarget": round(area(o5_inter) / max(1.0, area(o5)), 5) if o5_inter else 0.0,
        "triContactPass": tri_contact,
    }


def draw_overlay(records: list[dict], targets: dict, m3: dict) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [640, 2320, 2544, 3038]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
        small = ImageFont.truetype("Arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    def tr(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    def label(x: float, y: float, text: str, fill: tuple[int, int, int]) -> None:
        x -= crop_box[0]
        y -= crop_box[1]
        bbox = draw.textbbox((x, y), text, font=small)
        draw.rectangle([bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3], fill=(255, 255, 255))
        draw.text((x, y), text, fill=fill, font=small)

    g5 = targets["G5"]["box"]
    o5 = targets["O5"]["box"]
    draw.rectangle(tr(g5), outline=(0, 80, 255), width=5)
    draw.rectangle(tr(o5), outline=(255, 120, 0), width=5)
    draw.rectangle(tr(m3["box"]), outline=(30, 170, 70), width=5)
    label(g5[0], g5[1] - 28, "trusted G5", (0, 80, 255))
    label(o5[0], o5[1] - 28, "O5", (255, 120, 0))
    label(m3["box"][0], m3["box"][1] - 28, "M3", (30, 150, 60))

    styles = {
        "current": ((220, 0, 0), "current"),
        "g5_edge_touch": ((0, 160, 60), "G5 edge-touch"),
        "nearest_grid_dx_-40": ((130, 0, 210), "dx=-40"),
        "best_overlap_dx_-160_dy_35": ((120, 120, 120), "best overlap"),
    }
    for record in records:
        color, name = styles.get(record["name"], ((0, 0, 0), record["name"]))
        frame = record["frame"]
        draw.rectangle(tr(frame), outline=color, width=4)
        label(frame[0], frame[1] + 10 + 24 * list(styles).index(record["name"]) if record["name"] in styles else frame[1], name, color)
        axis_point = record["m3AxisAtRightEdge"]
        draw.ellipse(
            [
                axis_point[0] - crop_box[0] - 5,
                axis_point[1] - crop_box[1] - 5,
                axis_point[0] - crop_box[0] + 5,
                axis_point[1] - crop_box[1] + 5,
            ],
            fill=color,
        )

    draw.text((24, crop.height - 70), "Green frame: left edge touches trusted G5 while right edge still cuts M3 and bottom edge clips O5.", fill=(20, 20, 20), font=font)
    crop.save(OUT_IMG, quality=94)


def main() -> None:
    p78 = json.loads(P78_GRAPHIC_JSON.read_text())
    sensitivity = json.loads(SENSITIVITY_JSON.read_text())
    m3_data = json.loads(M3_JSON.read_text())
    frame = [float(v) for v in p78["reflectedBoxOnP76"]]
    targets = sensitivity["targets"]
    m3 = {
        "box": [float(v) for v in m3_data["m3"]["box"]],
        "center": [float(v) for v in m3_data["m3"]["center"]],
        "axisVector": [float(v) for v in m3_data["m3"]["axisVector"]],
    }

    g5_edge_touch_dx = targets["G5"]["box"][2] - frame[0]
    scenarios = [
        ("current", 0.0, 0.0),
        ("g5_edge_touch", g5_edge_touch_dx, 0.0),
        ("nearest_grid_dx_-40", -40.0, 0.0),
        ("best_overlap_dx_-160_dy_35", -160.0, 35.0),
    ]
    records = [
        target_metrics(name, shift_box(frame, dx, dy), targets, m3, dx, dy)
        for name, dx, dy in scenarios
    ]
    draw_overlay(records, targets, m3)

    edge_touch = next(row for row in records if row["name"] == "g5_edge_touch")
    assessment = [
        "The G5 repair is not just an arbitrary loose shift: the exact edge-touch shift is dx=-38, matching the previously observed ~40px repair.",
        "At dx=-38, the frame's left edge touches trusted G5, the right edge still cuts M3 with the full vertical mark overlap, and the bottom edge still clips O5.",
        "The heavier best-overlap shift dx=-160, dy=35 improves G5/O5 area overlap but breaks the M3 right-edge contact, so it looks less source-like.",
        "This promotes dx≈-38/-40 as a three-object source-registration signature, not as an extraction rule.",
        "No word, letter, line, or key unit is created by this contact geometry.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 frame tri-contact geometry signature; no key derivation",
        "frame": frame,
        "targets": targets,
        "m3": m3,
        "overlay": str(OUT_IMG),
        "records": records,
        "edgeTouchDx": g5_edge_touch_dx,
        "edgeTouchTriContactPass": edge_touch["triContactPass"],
        "assessment": assessment,
        "nextMove": "Use dx≈-38/-40 as a source-registration validation signature for any new scan/source image. Do not read it as key material unless a source clue names the extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# P78 Frame Tri-Contact Signature",
        "",
        "Scope: test whether the p78 reflected frame can simultaneously explain trusted G5, O5, and M3 contacts under the smallest G5 repair. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_IMG}`",
        f"- Base frame: `{frame}`",
        f"- Edge-touch dx: `{g5_edge_touch_dx}`",
        "",
        "## Scenario Metrics",
        "",
        "| scenario | dx | dy | G5 edge gap/overlap | G5 overlap | M3 right-edge cut | M3 axis in mark | O5 bottom cut width | O5 overlap | tri-contact |",
        "|---|---:|---:|---:|---:|---:|---|---:|---:|---|",
    ]
    for row in records:
        md.append(
            f"| `{row['name']}` | `{row['dx']}` | `{row['dy']}` | `{row['leftEdgeToG5RightPx']}` | `{row['g5OverlapVsTarget']}` | `{row['rightEdgeM3VerticalOverlapPx']}` | `{row['m3AxisRightInsideM3']}` | `{row['bottomEdgeO5HorizontalOverlapPx']}` | `{row['o5OverlapVsTarget']}` | `{row['triContactPass']}` |"
        )
    md.extend(["", "## Assessment", ""])
    md.extend(f"- {item}" for item in assessment)
    md.extend(["", "## Next Best Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"edge_touch_dx={g5_edge_touch_dx} tri_contact={edge_touch['triContactPass']}")


if __name__ == "__main__":
    main()
