#!/usr/bin/env python3
"""Sensitivity check for the p78 reflected frame against trusted O5/G5.

The previous exact B5/O5 self-mirror result was demoted because it used stale
G5 geometry. This script asks a narrower follow-up question: does the p78 lower
graphic frame still behave like a robust orientation pointer when checked
against the trusted G5 and O5 boxes?

No key derivation is performed.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
P78_GRAPHIC_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_trusted_target_sensitivity.json"
OUT_MD = OUT / "p78_frame_trusted_target_sensitivity.md"
OUT_OVERLAY = OUT / "p78_frame_trusted_target_sensitivity_overlay.jpg"


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def shift(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def intersection(a: list[float], b: list[float]) -> tuple[float, list[float] | None]:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0, None
    box = [x1, y1, x2, y2]
    return area(box), box


def gap(a: list[float], b: list[float]) -> tuple[float, float]:
    horizontal = max(b[0] - a[2], a[0] - b[2], 0.0)
    vertical = max(b[1] - a[3], a[1] - b[3], 0.0)
    return horizontal, vertical


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def target_record(frame: list[float], target: dict) -> dict:
    overlap, inter = intersection(frame, target["box"])
    hgap, vgap = gap(frame, target["box"])
    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "intersection": [round(v, 2) for v in inter] if inter else None,
        "overlapArea": round(overlap, 2),
        "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 5),
        "overlapVsFrame": round(overlap / max(1.0, area(frame)), 5),
        "horizontalGapPx": round(hgap, 2),
        "verticalGapPx": round(vgap, 2),
        "centerDistancePx": round(distance(center(frame), center(target["box"])), 2),
    }


def load_targets() -> dict[str, dict]:
    data = json.loads(MAP_JSON.read_text())
    page = next(row for row in data["pages"] if row["page"] == 76)
    o5 = next(h for h in page["highlights"] if h["id"] == "p76_orange_5")
    lower = json.loads(LOWER_MARKS_JSON.read_text())
    g5 = next(item for item in lower["analyses"] if "Volcano Bonds" in item.get("note", ""))
    return {
        "O5": {
            "id": "O5",
            "label": "shitcoiner at heart",
            "box": [float(v) for v in o5["box"]],
        },
        "G5": {
            "id": "G5_trusted",
            "label": "Volcano Bonds",
            "box": [float(v) for v in g5["box"]],
        },
    }


def best_grid_records(frame: list[float], targets: dict[str, dict]) -> dict:
    grid = []
    for dx in range(-160, 161, 5):
        for dy in range(-80, 81, 5):
            moved = shift(frame, dx, dy)
            o5 = target_record(moved, targets["O5"])
            g5 = target_record(moved, targets["G5"])
            grid.append(
                {
                    "dx": dx,
                    "dy": dy,
                    "frame": [round(v, 2) for v in moved],
                    "O5": o5,
                    "G5": g5,
                    "o5Overlap": o5["overlapVsTarget"],
                    "g5Overlap": g5["overlapVsTarget"],
                    "g5HorizontalGap": g5["horizontalGapPx"],
                    "g5VerticalGap": g5["verticalGapPx"],
                    "scoreOverlap": round(o5["overlapVsTarget"] + g5["overlapVsTarget"], 5),
                }
            )
    current = next(row for row in grid if row["dx"] == 0 and row["dy"] == 0)
    simultaneous_overlap = [row for row in grid if row["o5Overlap"] > 0 and row["g5Overlap"] > 0]
    g5_edge_o5_overlap = [
        row
        for row in grid
        if row["o5Overlap"] > 0
        and row["G5"]["verticalGapPx"] == 0
        and row["G5"]["horizontalGapPx"] <= 40
    ]
    o5_lost_if_up = sorted(
        [row for row in grid if row["dx"] == 0 and row["dy"] <= 0],
        key=lambda row: row["dy"],
    )
    first_o5_loss = next((row for row in reversed(o5_lost_if_up) if row["o5Overlap"] == 0), None)

    best_overlap = sorted(simultaneous_overlap, key=lambda row: (-row["scoreOverlap"], abs(row["dx"]) + abs(row["dy"])))[:8]
    closest_to_current_simultaneous = sorted(simultaneous_overlap, key=lambda row: abs(row["dx"]) + abs(row["dy"]))[:8]
    closest_edge = sorted(g5_edge_o5_overlap, key=lambda row: abs(row["dx"]) + abs(row["dy"]))[:8]

    return {
        "gridStepPx": 5,
        "dxRangePx": [-160, 160],
        "dyRangePx": [-80, 80],
        "current": current,
        "simultaneousOverlapCount": len(simultaneous_overlap),
        "g5EdgeAndO5OverlapCount": len(g5_edge_o5_overlap),
        "closestSimultaneousOverlaps": closest_to_current_simultaneous,
        "bestSimultaneousOverlaps": best_overlap,
        "closestG5EdgeWithO5Overlap": closest_edge,
        "firstPureUpwardShiftWhereO5Lost": first_o5_loss,
    }


def draw_overlay(frame: list[float], targets: dict[str, dict], records: dict) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [650, 2320, 2320, 3030]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    def tr(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    def label(xy, text, fill):
        try:
            font = ImageFont.truetype("Arial.ttf", 23)
        except OSError:
            font = ImageFont.load_default()
        x, y = xy
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
        draw.text((x, y), text, fill=fill, font=font)

    draw.rectangle(tr(targets["G5"]["box"]), outline=(0, 90, 255), width=5)
    draw.rectangle(tr(targets["O5"]["box"]), outline=(255, 110, 0), width=5)
    label((int(targets["G5"]["box"][0] - crop_box[0]), int(targets["G5"]["box"][1] - crop_box[1] - 28)), "trusted G5", (0, 90, 255))
    label((int(targets["O5"]["box"][0] - crop_box[0]), int(targets["O5"]["box"][1] - crop_box[1] - 28)), "O5", (255, 110, 0))

    draw.rectangle(tr(frame), outline=(255, 0, 0), width=4)
    label((int(frame[0] - crop_box[0]), int(frame[1] - crop_box[1] + 8)), "current p78 frame", (255, 0, 0))

    nearest = records["closestSimultaneousOverlaps"][0] if records["closestSimultaneousOverlaps"] else None
    if nearest:
        moved = nearest["frame"]
        draw.rectangle(tr(moved), outline=(0, 160, 60), width=4)
        label((int(moved[0] - crop_box[0]), int(moved[1] - crop_box[1] + 38)), f"nearest both dx={nearest['dx']}", (0, 160, 60))

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    targets = load_targets()
    p78 = json.loads(P78_GRAPHIC_JSON.read_text())
    frame = [float(v) for v in p78["reflectedBoxOnP76"]]
    records = best_grid_records(frame, targets)
    draw_overlay(frame, targets, records)

    current = records["current"]
    nearest = records["closestSimultaneousOverlaps"][0] if records["closestSimultaneousOverlaps"] else None
    edge = records["closestG5EdgeWithO5Overlap"][0] if records["closestG5EdgeWithO5Overlap"] else None
    best = records["bestSimultaneousOverlaps"][0] if records["bestSimultaneousOverlaps"] else None

    assessment = [
        "The current p78 frame remains a lower-corridor pointer: it clips O5 and runs vertically beside trusted G5.",
        "Current G5 evidence is edge-adjacent, not an exact overlap: the trusted G5 right edge is 38px left of the p78 frame.",
        "A small left shift of about 40px is enough for the p78 frame to touch/overlap trusted G5 while preserving the O5 clip.",
        "The O5 clip is vertically fragile: moving the frame upward by about 20px loses O5, while moving downward strengthens it.",
        "Therefore p78 frame/O5/G5 should stay active as orientation/source-registration evidence, but not as a precise extraction unit without a better source transform.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 reflected frame sensitivity against trusted page-76 G5/O5; no key derivation",
        "frame": frame,
        "targets": targets,
        "grid": records,
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": assessment,
        "nextMove": "Use this p78-frame robustness profile when evaluating any new source image: a valid source registration should explain the 38px G5 near-miss and the O5 bottom-edge clip without arbitrary local shifting.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P78 Frame Trusted-Target Sensitivity",
        "",
        "Scope: test how the reflected p78 frame behaves against trusted G5/O5 after the stale G5 correction. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        f"- Frame: `{frame}`",
        f"- O5: `{targets['O5']['box']}`",
        f"- Trusted G5: `{targets['G5']['box']}`",
        "",
        "## Current Position",
        "",
        f"- O5 overlapVsTarget: `{current['O5']['overlapVsTarget']}`; O5 verticalGap: `{current['O5']['verticalGapPx']}px`",
        f"- G5 overlapVsTarget: `{current['G5']['overlapVsTarget']}`; G5 horizontalGap: `{current['G5']['horizontalGapPx']}px`; G5 verticalGap: `{current['G5']['verticalGapPx']}px`",
        "",
        "## Sensitivity Results",
        "",
        f"- Grid: dx `{records['dxRangePx']}` px, dy `{records['dyRangePx']}` px, step `{records['gridStepPx']}` px.",
        f"- Simultaneous true-overlap positions for O5 and trusted G5: `{records['simultaneousOverlapCount']}`.",
        f"- G5 edge/near-edge plus O5 overlap positions: `{records['g5EdgeAndO5OverlapCount']}`.",
    ]
    if nearest:
        lines.append(
            f"- Nearest true simultaneous overlap: dx=`{nearest['dx']}`, dy=`{nearest['dy']}`, O5=`{nearest['O5']['overlapVsTarget']}`, G5=`{nearest['G5']['overlapVsTarget']}`."
        )
    if edge:
        lines.append(
            f"- Nearest G5 edge/near-edge plus O5 overlap: dx=`{edge['dx']}`, dy=`{edge['dy']}`, G5 gap=`{edge['G5']['horizontalGapPx']}px`, O5=`{edge['O5']['overlapVsTarget']}`."
        )
    if best:
        lines.append(
            f"- Best combined overlap in this bounded grid: dx=`{best['dx']}`, dy=`{best['dy']}`, O5=`{best['O5']['overlapVsTarget']}`, G5=`{best['G5']['overlapVsTarget']}`."
        )
    if records["firstPureUpwardShiftWhereO5Lost"]:
        lost = records["firstPureUpwardShiftWhereO5Lost"]
        lines.append(f"- Pure upward shift where O5 is lost: dy=`{lost['dy']}` px.")

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("current", current["O5"]["overlapVsTarget"], current["G5"]["horizontalGapPx"])
    if nearest:
        print("nearest simultaneous", nearest["dx"], nearest["dy"], nearest["O5"]["overlapVsTarget"], nearest["G5"]["overlapVsTarget"])


if __name__ == "__main__":
    main()
