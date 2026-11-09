#!/usr/bin/env python3
"""Check whether C9 frame internal target geometry supplies an order rule.

The C9 frame covers O4/B4/G5/O5, but the previous page-control pass showed the
frame is broad and horizontally mirror-invariant. This bounded pass inspects
only the four active target boxes inside that frame: edge contacts,
centerlines, diagonals, normalized positions, and mirrored-pair relationships.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
C9_JSON = ROOT / "analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json"
YK_UNIT_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate.json"
ORDER_TRAP_JSON = ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/c9_frame_internal_geometry_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_frame_internal_geometry_gate.json"
OUT_MD = OUT / "c9_frame_internal_geometry_gate.md"
SHEET = OUT / "c9_frame_internal_geometry_gate_sheet.jpg"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def line_coeff(p1: tuple[float, float], p2: tuple[float, float]) -> tuple[float, float, float]:
    x1, y1 = p1
    x2, y2 = p2
    return y1 - y2, x2 - x1, x1 * y2 - x2 * y1


def line_distance(point: tuple[float, float], coeff: tuple[float, float, float]) -> float:
    a, b, c = coeff
    x, y = point
    return abs(a * x + b * y + c) / math.hypot(a, b)


def rounded_box(box: list[float]) -> list[float]:
    return [round(float(v), 2) for v in box]


def target_metrics(frame: list[float], target: dict[str, Any]) -> dict[str, Any]:
    x0, y0, x1, y1 = frame
    w = x1 - x0
    h = y1 - y0
    fx, fy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tlbr = line_coeff((x0, y0), (x1, y1))
    trbl = line_coeff((x1, y0), (x0, y1))
    box = [float(v) for v in target["box"]]
    cx, cy = center(box)
    box_edge_gaps = {
        "left": box[0] - x0,
        "right": x1 - box[2],
        "top": box[1] - y0,
        "bottom": y1 - box[3],
    }
    center_edge_gaps = {
        "left": cx - x0,
        "right": x1 - cx,
        "top": cy - y0,
        "bottom": y1 - cy,
    }
    nearest_box_edge = min(box_edge_gaps.items(), key=lambda kv: abs(kv[1]))
    return {
        "id": target["id"],
        "shortId": target["shortId"],
        "label": target["label"],
        "visualState": target["visualState"],
        "pageLine": target["pageLine"],
        "corridorIndex": target["corridorIndex"],
        "box": rounded_box(box),
        "center": [round(cx, 2), round(cy, 2)],
        "normalizedCenter": [round((cx - x0) / w, 6), round((cy - y0) / h, 6)],
        "boxEdgeGapsPx": {k: round(v, 2) for k, v in box_edge_gaps.items()},
        "centerEdgeGapsPx": {k: round(v, 2) for k, v in center_edge_gaps.items()},
        "nearestBoxEdge": nearest_box_edge[0],
        "nearestBoxEdgeGapPx": round(nearest_box_edge[1], 2),
        "centerlineDistancesPx": {
            "verticalCenterline": round(abs(cx - fx), 2),
            "horizontalCenterline": round(abs(cy - fy), 2),
        },
        "diagonalDistancesPx": {
            "topLeftToBottomRight": round(line_distance((cx, cy), tlbr), 2),
            "topRightToBottomLeft": round(line_distance((cx, cy), trbl), 2),
        },
    }


def pair_metrics(frame: list[float], targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    x0, y0, x1, y1 = frame
    fx, fy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rows = []
    for i, a in enumerate(targets):
        for b in targets[i + 1 :]:
            ac = center([float(v) for v in a["box"]])
            bc = center([float(v) for v in b["box"]])
            midpoint = ((ac[0] + bc[0]) / 2.0, (ac[1] + bc[1]) / 2.0)
            x_mirror_delta = math.hypot((2 * fx - ac[0]) - bc[0], ac[1] - bc[1])
            y_mirror_delta = math.hypot(ac[0] - bc[0], (2 * fy - ac[1]) - bc[1])
            point_delta = math.hypot((2 * fx - ac[0]) - bc[0], (2 * fy - ac[1]) - bc[1])
            rows.append(
                {
                    "pair": f"{a['shortId']}-{b['shortId']}",
                    "targetIds": [a["id"], b["id"]],
                    "midpoint": [round(midpoint[0], 2), round(midpoint[1], 2)],
                    "midpointDeltaFromFrameCenterPx": [round(midpoint[0] - fx, 2), round(midpoint[1] - fy, 2)],
                    "midpointDistanceFromFrameCenterPx": round(math.hypot(midpoint[0] - fx, midpoint[1] - fy), 2),
                    "xMirrorPairDeltaPx": round(x_mirror_delta, 2),
                    "yMirrorPairDeltaPx": round(y_mirror_delta, 2),
                    "pointReflectionPairDeltaPx": round(point_delta, 2),
                }
            )
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    crop = [180, 2070, 2315, 3065]
    scale = 0.46
    panel = Image.open(PAGE_IMAGE).convert("RGB").crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 28
    header_h = 128
    footer_h = 408
    sheet = Image.new("RGB", (margin * 2 + panel.size[0], header_h + panel.size[1] + footer_h + margin), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(15)
    small = font(12)
    mono = font(13)

    draw.text((margin, 20), "C9 Frame Internal Geometry Gate", fill=(240, 244, 248), font=title)
    draw.text((margin, 58), "Tests only O4/B4/G5/O5 positions inside the C9 frame: edges, centerlines, diagonals, mirror pairs.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 84), "Blue = C9 frame/axes. Orange/grey = active target boxes. Numbers are group/vertical order.", fill=(178, 188, 199), font=small)

    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    x0, y0, x1, y1 = result["c9Frame"]
    fx, fy = result["frameCenter"]
    draw.rectangle([sx(x0), sy(y0), sx(x1), sy(y1)], outline="#55d6ff", width=3)
    draw.line([sx(fx), sy(y0), sx(fx), sy(y1)], fill="#38bdf8", width=2)
    draw.line([sx(x0), sy(fy), sx(x1), sy(fy)], fill="#38bdf8", width=2)
    draw.line([sx(x0), sy(y0), sx(x1), sy(y1)], fill="#2dd4bf", width=2)
    draw.line([sx(x1), sy(y0), sx(x0), sy(y1)], fill="#2dd4bf", width=2)

    colors = {"Y": "#ff9b2e", "K": "#aab4c2"}
    for idx, row in enumerate(result["targetMetrics"], start=1):
        box = row["box"]
        color = colors[row["visualState"]]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=4)
        draw.ellipse([sx(box[0]) - 12, sy(box[1]) - 19, sx(box[0]) + 12, sy(box[1]) + 5], fill="#e0f2fe")
        draw.text((sx(box[0]) - 4, sy(box[1]) - 18), str(idx), fill="#06101d", font=small)
        draw.text((sx(box[0]), max(header_h, sy(box[1]) - 34)), row["shortId"], fill=color, font=small)

    y = header_h + panel.size[1] + 22
    draw.text((margin, y), "Gate Summary", fill=(238, 243, 248), font=normal)
    y += 28
    notes = [
        f"Strict edge contacts <=4px: {result['summary']['strictEdgeContactCount']} ({', '.join(result['summary']['strictEdgeContactLabels']) or 'none'}).",
        f"Centerline/diagonal center hits <=25px: {result['summary']['axisOrDiagonalCenterHitCount']}.",
        f"Mirror-pair hits <=25px: {result['summary']['mirrorPairHitCount']}.",
        f"Closest pair midpoint to frame center: {result['summary']['closestPairToFrameCenter']['pair']} at {result['summary']['closestPairToFrameCenter']['midpointDistanceFromFrameCenterPx']}px.",
        "Result: internal geometry adds an O4 top-edge coincidence but no usable fold/mirror/order rule.",
    ]
    for note in notes:
        draw.text((margin, y), note[:132], fill=(255, 219, 137), font=normal)
        y += 25

    y += 10
    draw.text((margin, y), "Target Normalized Centers", fill=(238, 243, 248), font=normal)
    y += 26
    for row in result["targetMetrics"]:
        draw.text(
            (margin, y),
            f"{row['shortId']} {row['normalizedCenter']} nearest edge {row['nearestBoxEdge']} {row['nearestBoxEdgeGapPx']}px",
            fill="#c6d1df",
            font=mono,
        )
        y += 21

    SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHEET, quality=94)


def main() -> None:
    c9 = load_json(C9_JSON)
    yk_unit = load_json(YK_UNIT_JSON)
    order_trap = load_json(ORDER_TRAP_JSON)
    frame = [float(v) for v in c9["c9Frame"]]
    x0, y0, x1, y1 = frame
    frame_center = [(x0 + x1) / 2.0, (y0 + y1) / 2.0]
    targets = c9["activeTargets"]
    target_rows = [target_metrics(frame, target) for target in targets]
    pair_rows = pair_metrics(frame, targets)

    edge_contacts = [
        row
        for row in target_rows
        if min(abs(v) for v in row["boxEdgeGapsPx"].values()) <= 4.0
    ]
    axis_hits = []
    for row in target_rows:
        for name, value in row["centerlineDistancesPx"].items():
            if value <= 25.0:
                axis_hits.append({"target": row["shortId"], "kind": name, "distancePx": value})
        for name, value in row["diagonalDistancesPx"].items():
            if value <= 25.0:
                axis_hits.append({"target": row["shortId"], "kind": name, "distancePx": value})

    mirror_pair_hits = [
        row
        for row in pair_rows
        if min(row["xMirrorPairDeltaPx"], row["yMirrorPairDeltaPx"], row["pointReflectionPairDeltaPx"]) <= 25.0
    ]
    closest_pair = min(pair_rows, key=lambda row: row["midpointDistanceFromFrameCenterPx"])

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 frame internal target geometry gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "c9FramePageControl": rel(C9_JSON),
            "ykUnitOrderGate": rel(YK_UNIT_JSON),
            "activeOrderOrientationTrap": rel(ORDER_TRAP_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "c9Frame": rounded_box(frame),
        "frameCenter": [round(frame_center[0], 2), round(frame_center[1], 2)],
        "frameSize": [round(x1 - x0, 2), round(y1 - y0, 2)],
        "targetMetrics": target_rows,
        "pairMetrics": pair_rows,
        "summary": {
            "strictEdgeContactThresholdPx": 4.0,
            "axisOrDiagonalThresholdPx": 25.0,
            "mirrorPairThresholdPx": 25.0,
            "strictEdgeContactCount": len(edge_contacts),
            "strictEdgeContactLabels": [f"{row['shortId']}:{row['nearestBoxEdge']}={row['nearestBoxEdgeGapPx']}px" for row in edge_contacts],
            "axisOrDiagonalCenterHitCount": len(axis_hits),
            "axisOrDiagonalCenterHits": axis_hits,
            "mirrorPairHitCount": len(mirror_pair_hits),
            "mirrorPairHits": mirror_pair_hits,
            "closestPairToFrameCenter": closest_pair,
            "groupOrderTargetIds": yk_unit.get("summary", {}).get("groupOrderTargetIds"),
            "leftToRightTargetIds": yk_unit.get("summary", {}).get("leftToRightTargetIds"),
            "lineOrder": yk_unit.get("summary", {}).get("pageLines"),
            "corridorOrder": yk_unit.get("summary", {}).get("corridorIndexes"),
            "obboOrientationIsPalindromic": order_trap.get("summary", {}).get("colorPatternIsPalindrome"),
            "ykkyOrientationIsPalindromic": order_trap.get("summary", {}).get("visualStatePatternIsPalindrome"),
            "selectorUnlocked": False,
        },
        "assessment": [
            "Only O4 has a strict edge coincidence: its top edge is effectively the C9 frame top edge.",
            "That contact is not independent extraction permission because the C9 frame was already derived as the active-quartet full-coverage envelope.",
            "No active target center sits on a C9 centerline or diagonal within 25 px.",
            "No active pair forms a horizontal, vertical, or point-reflection mirror pair within 25 px.",
            "Internal C9 geometry therefore does not resolve the group-order versus left-to-right order conflict.",
        ],
        "decision": {
            "c9FrameInternalGeometryGate": "closed_for_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep C9 as source-validation geometry only. Reopen extraction only if a new source/clue independently names a frame edge, centerline, diagonal, or target-order operation.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Frame Internal Geometry Gate",
        "",
        "Scope: inspect only O4/B4/G5/O5 positions inside the C9 frame: edge contacts, centerlines, diagonals, normalized positions, and mirror-pair relations. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- C9 frame: `{result['c9Frame']}`",
        f"- Frame center: `{result['frameCenter']}`",
        f"- Frame size: `{result['frameSize']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Target Geometry",
        "",
        "| target | visual | line/corridor | normalized center | nearest frame edge | centerline distances | diagonal distances |",
        "|---|---|---:|---|---|---|---|",
    ]
    for row in target_rows:
        lines.append(
            f"| `{row['shortId']} {row['label']}` | `{row['visualState']}` | `L{row['pageLine']}/C{row['corridorIndex']}` | `{row['normalizedCenter']}` | `{row['nearestBoxEdge']} {row['nearestBoxEdgeGapPx']}px` | `{row['centerlineDistancesPx']}` | `{row['diagonalDistancesPx']}` |"
        )

    lines.extend(
        [
            "",
            "## Pair Symmetry",
            "",
            "| pair | midpoint delta from frame center | midpoint distance | x-mirror delta | y-mirror delta | point-reflection delta |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in pair_rows:
        lines.append(
            f"| `{row['pair']}` | `{row['midpointDeltaFromFrameCenterPx']}` | `{row['midpointDistanceFromFrameCenterPx']}` | `{row['xMirrorPairDeltaPx']}` | `{row['yMirrorPairDeltaPx']}` | `{row['pointReflectionPairDeltaPx']}` |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Strict edge contacts <=4 px: `{result['summary']['strictEdgeContactCount']}` (`{', '.join(result['summary']['strictEdgeContactLabels']) or 'none'}`).",
            f"- Centerline/diagonal center hits <=25 px: `{result['summary']['axisOrDiagonalCenterHitCount']}`.",
            f"- Mirror-pair hits <=25 px: `{result['summary']['mirrorPairHitCount']}`.",
            f"- Closest pair midpoint to frame center: `{closest_pair['pair']}` at `{closest_pair['midpointDistanceFromFrameCenterPx']} px`.",
            f"- Group/vertical order remains `{result['summary']['groupOrderTargetIds']}`; left-to-right order remains `{result['summary']['leftToRightTargetIds']}`.",
            "",
            "## Assessment",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote internal C9 edge/axis/diagonal/pair geometry as a selector.",
            "- O4 top-edge coincidence is useful as a future source-registration check, but it is not independent extraction permission.",
            "- Keep C9 as source-validation geometry only. Reopen extraction only if a new source/clue names frame edge, centerline, diagonal, or target-order operation.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
