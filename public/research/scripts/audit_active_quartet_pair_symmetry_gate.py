#!/usr/bin/env python3
"""Test whether the active OBBO/YKKY quartet supplies a fold-pair symmetry rule.

This bounded geometry pass treats the locked active targets as two natural
pairs: outer orange O4/O5 and inner black B4/G5. It checks whether those pairs
share a clean horizontal, vertical, or point-reflection axis, and whether their
pair midpoints register to the p78 OVERDOSE same-layout/current-mirror frames.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
P78_SOURCE_JSON = ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json"
SCORING_JSON = ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/active_quartet_pair_symmetry_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_quartet_pair_symmetry_gate.json"
OUT_MD = OUT / "active_quartet_pair_symmetry_gate.md"
SHEET = OUT / "active_quartet_pair_symmetry_gate_sheet.jpg"


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


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def dist(a: list[float], b: list[float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def midpoint(a: list[float], b: list[float]) -> list[float]:
    return [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]


def round_box(box: list[float]) -> list[float]:
    return [round(v, 2) for v in box]


def pair_metrics(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ca = a["center"]
    cb = b["center"]
    mid = midpoint(ca, cb)
    return {
        "pair": [a["id"], b["id"]],
        "labels": [a["label"], b["label"]],
        "colors": [a["visualState"], b["visualState"]],
        "centers": [ca, cb],
        "midpoint": [round(mid[0], 2), round(mid[1], 2)],
        "dxAbsPx": round(abs(ca[0] - cb[0]), 2),
        "dyAbsPx": round(abs(ca[1] - cb[1]), 2),
        "distancePx": round(dist(ca, cb), 2),
        "lineGap": abs(a["pageLine"] - b["pageLine"]),
        "corridorGap": abs(a["corridorIndex"] - b["corridorIndex"]),
    }


def axis_hypothesis(name: str, pairs: list[dict[str, Any]], line_pitch: float) -> dict[str, Any]:
    horizontal_pair_axes = [sum(c[1] for c in pair["centers"]) / 2.0 for pair in pairs]
    horizontal_x_errors = [abs(pair["centers"][0][0] - pair["centers"][1][0]) for pair in pairs]
    vertical_pair_axes = [sum(c[0] for c in pair["centers"]) / 2.0 for pair in pairs]
    vertical_y_errors = [abs(pair["centers"][0][1] - pair["centers"][1][1]) for pair in pairs]
    point_midpoints = [pair["midpoint"] for pair in pairs]
    point_mid_spread = dist(point_midpoints[0], point_midpoints[1])

    horizontal_axis_spread = abs(horizontal_pair_axes[0] - horizontal_pair_axes[1])
    vertical_axis_spread = abs(vertical_pair_axes[0] - vertical_pair_axes[1])
    horizontal_max_error = max(horizontal_x_errors + [horizontal_axis_spread])
    vertical_max_error = max(vertical_y_errors + [vertical_axis_spread])
    point_max_error = max(point_mid_spread, 0.0)

    threshold = line_pitch
    return {
        "name": name,
        "pairs": pairs,
        "horizontalFold": {
            "pairAxesY": [round(v, 2) for v in horizontal_pair_axes],
            "pairAxisSpreadPx": round(horizontal_axis_spread, 2),
            "xMismatchPx": [round(v, 2) for v in horizontal_x_errors],
            "maxErrorPx": round(horizontal_max_error, 2),
            "passesOneLinePitch": horizontal_max_error <= threshold,
        },
        "verticalFold": {
            "pairAxesX": [round(v, 2) for v in vertical_pair_axes],
            "pairAxisSpreadPx": round(vertical_axis_spread, 2),
            "yMismatchPx": [round(v, 2) for v in vertical_y_errors],
            "maxErrorPx": round(vertical_max_error, 2),
            "passesOneLinePitch": vertical_max_error <= threshold,
        },
        "pointReflection": {
            "pairMidpoints": point_midpoints,
            "midpointSpreadPx": round(point_mid_spread, 2),
            "passesOneLinePitch": point_max_error <= threshold,
        },
    }


def frame_center(frame: list[float]) -> list[float]:
    return [(frame[0] + frame[2]) / 2.0, (frame[1] + frame[3]) / 2.0]


def frame_relation(name: str, frame: list[float], pair_rows: list[dict[str, Any]], line_pitch: float) -> dict[str, Any]:
    fc = frame_center(frame)
    rows = []
    for pair in pair_rows:
        mid = pair["midpoint"]
        rows.append(
            {
                "pair": pair["pair"],
                "midpoint": mid,
                "dxToFrameCenterPx": round(abs(mid[0] - fc[0]), 2),
                "dyToFrameCenterPx": round(abs(mid[1] - fc[1]), 2),
                "distanceToFrameCenterPx": round(dist(mid, fc), 2),
                "withinOneLinePitch2d": dist(mid, fc) <= line_pitch,
            }
        )
    best = min(rows, key=lambda row: row["distanceToFrameCenterPx"])
    return {
        "name": name,
        "frame": round_box(frame),
        "frameCenter": [round(fc[0], 2), round(fc[1], 2)],
        "pairRows": rows,
        "bestPair": best,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [220, 2050, 2060, 3060]
    scale = 0.56
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 34
    header_h = 154
    panel_w, panel_h = panel.size
    side_w = 660
    sheet_w = margin * 3 + panel_w + side_w
    sheet_h = header_h + panel_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, 28), "Active Quartet Pair Symmetry Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 70),
        "Tests whether the palindromic OBBO/YKKY target order gives a fold or mirror pair rule.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 98),
        "Blue = p78 current mirror frame. Cyan = p78 same-layout frame. Orange lines pair O4/O5 and B4/G5.",
        fill=(176, 186, 198),
        font=small,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    def draw_box(box: list[float], color: str, width: int = 3) -> None:
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)

    draw_box(result["frames"]["sameLayoutFrame"], "#55d6ff", 3)
    draw_box(result["frames"]["currentMirrorFrame"], "#4f7dff", 3)

    target_color = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for row in result["targets"]:
        draw_box(row["box"], target_color.get(row["visualState"], "#ffffff"), 4)
        cx, cy = row["center"]
        draw.ellipse((sx(cx) - 5, sy(cy) - 5, sx(cx) + 5, sy(cy) + 5), fill="#ffffff")
        draw.text((sx(row["box"][0]), sy(row["box"][1]) - 18), row["id"], fill="#ffffff", font=small)

    for pair in result["primaryPairing"]["pairs"]:
        a, b = pair["centers"]
        draw.line((sx(a[0]), sy(a[1]), sx(b[0]), sy(b[1])), fill="#ffb25b", width=3)
        mx, my = pair["midpoint"]
        draw.ellipse((sx(mx) - 6, sy(my) - 6, sx(mx) + 6, sy(my) + 6), outline="#ffb25b", width=3)

    # Show the horizontal candidate axes for the two natural pairs.
    for y in result["primaryPairing"]["horizontalFold"]["pairAxesY"]:
        draw.line((sx(crop[0]), sy(y), sx(crop[2]), sy(y)), fill="#ffb25b", width=1)

    x0 = margin * 2 + panel_w
    y = header_h
    draw.text((x0, y), "Result", fill=(238, 243, 248), font=normal)
    y += 34
    decision = result["decision"]
    chips = [
        ("selector", decision["selectorUnlocked"]),
        ("best axis", decision["bestAxis"]),
        ("best frame relation", decision["bestFrameRelation"]),
        ("line pitch px", result["linePitchPx"]),
    ]
    for label, value in chips:
        draw.rectangle((x0, y, x0 + side_w, y + 48), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x0 + 12, y + 7), label, fill=(129, 143, 158), font=small)
        draw.text((x0 + 180, y + 7), str(value), fill=(232, 239, 246), font=mono)
        y += 58

    y += 16
    draw.text((x0, y), "Symmetry Errors", fill=(238, 243, 248), font=normal)
    y += 34
    rows = [
        ("horizontal fold max", result["primaryPairing"]["horizontalFold"]["maxErrorPx"]),
        ("vertical fold max", result["primaryPairing"]["verticalFold"]["maxErrorPx"]),
        ("point midpoint spread", result["primaryPairing"]["pointReflection"]["midpointSpreadPx"]),
        ("same-layout best 2D", result["frameRelations"][0]["bestPair"]["distanceToFrameCenterPx"]),
        ("current-mirror best 2D", result["frameRelations"][1]["bestPair"]["distanceToFrameCenterPx"]),
    ]
    for label, value in rows:
        draw.text((x0 + 10, y), f"{label}: {value}px", fill=(202, 211, 221), font=mono)
        y += 24

    y += 18
    draw.text((x0, y), "Interpretation", fill=(238, 243, 248), font=normal)
    y += 32
    notes = [
        "Outer orange and inner black pairs do not share a clean fold axis.",
        "B4/G5 midpoint nearly matches same-layout frame X, but misses in Y.",
        "The current mirror frame does not center either color pair cleanly.",
        "This keeps OBBO/YKKY as target validation, not extraction permission.",
    ]
    for note in notes:
        draw.text((x0 + 10, y), note, fill=(202, 211, 221), font=small)
        y += 24

    sheet.save(SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    p78_source = load_json(P78_SOURCE_JSON)
    scoring = load_json(SCORING_JSON)
    page76 = next(page for page in article["pages"] if page["page"] == 76)
    line_pitch = float(scoring.get("numericBenchmarks", {}).get("p77NearMiss", {}).get("medianLinePitchPx", 73.73))

    targets = []
    for row in active["targets"]:
        item = dict(row)
        item["center"] = [round(v, 2) for v in center(row["box"])]
        targets.append(item)
    by_id = {row["id"]: row for row in targets}

    primary_pairs = [
        pair_metrics(by_id["buying_dip"], by_id["shitcoiner_heart"]),
        pair_metrics(by_id["one_billion"], by_id["volcano_bonds"]),
    ]
    primary = axis_hypothesis("outer_orange_inner_black", primary_pairs, line_pitch)

    alternate_pairs = [
        pair_metrics(by_id["buying_dip"], by_id["one_billion"]),
        pair_metrics(by_id["volcano_bonds"], by_id["shitcoiner_heart"]),
    ]
    alternate = axis_hypothesis("top_neighbor_pairs_control", alternate_pairs, line_pitch)

    same_layout_frame = list(map(float, p78_source["sourceGraphic"]["box"]))
    current_mirror_frame = list(map(float, scoring["numericBenchmarks"]["p78Frame"]["currentFrame"]))
    frame_relations = [
        frame_relation("same_layout_p78_source_slot", same_layout_frame, primary_pairs, line_pitch),
        frame_relation("current_p78_to_p76_mirror_frame", current_mirror_frame, primary_pairs, line_pitch),
    ]

    best_axis = min(
        [
            ("horizontal_fold", primary["horizontalFold"]["maxErrorPx"]),
            ("vertical_fold", primary["verticalFold"]["maxErrorPx"]),
            ("point_reflection", primary["pointReflection"]["midpointSpreadPx"]),
        ],
        key=lambda row: row[1],
    )
    best_frame = min(
        [
            (rel["name"], rel["bestPair"]["distanceToFrameCenterPx"])
            for rel in frame_relations
        ],
        key=lambda row: row[1],
    )
    selector_unlocked = (
        primary["horizontalFold"]["passesOneLinePitch"]
        or primary["verticalFold"]["passesOneLinePitch"]
        or primary["pointReflection"]["passesOneLinePitch"]
        or any(rel["bestPair"]["withinOneLinePitch2d"] for rel in frame_relations)
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active OBBO/YKKY pair-symmetry gate; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "p78SourceInstructionSurface": rel(P78_SOURCE_JSON),
            "futureSourceScoringRubric": rel(SCORING_JSON),
        },
        "page": {"page": 76, "width": page76["width"], "height": page76["height"]},
        "linePitchPx": round(line_pitch, 2),
        "targets": [
            {
                "id": row["id"],
                "label": row["label"],
                "phrase": row["phrase"],
                "box": round_box(row["box"]),
                "center": row["center"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "visualState": row["visualState"],
            }
            for row in targets
        ],
        "frames": {
            "sameLayoutFrame": round_box(same_layout_frame),
            "currentMirrorFrame": round_box(current_mirror_frame),
        },
        "primaryPairing": primary,
        "alternatePairingControl": alternate,
        "frameRelations": frame_relations,
        "summary": {
            "colorPattern": active["summary"]["activeColorPattern"],
            "visualStatePattern": active["summary"]["activeVisualStateOrder"],
            "pageLines": active["summary"]["pageLines"],
            "corridorIndexes": active["summary"]["corridorIndexes"],
            "primaryHorizontalMaxErrorPx": primary["horizontalFold"]["maxErrorPx"],
            "primaryVerticalMaxErrorPx": primary["verticalFold"]["maxErrorPx"],
            "primaryPointMidpointSpreadPx": primary["pointReflection"]["midpointSpreadPx"],
            "bestFrameRelationName": best_frame[0],
            "bestFrameRelationDistancePx": round(best_frame[1], 2),
            "selectorUnlocked": selector_unlocked,
        },
        "decision": {
            "activeQuartetPairSymmetry": "closed_current_scan",
            "bestAxis": f"{best_axis[0]} {round(best_axis[1], 2)}px",
            "bestFrameRelation": f"{best_frame[0]} {round(best_frame[1], 2)}px",
            "selectorUnlocked": selector_unlocked,
            "nextMove": "Keep OBBO/YKKY pair symmetry as a visual validation check only; reopen only if source wording names color-pair folding, pair midpoints, or an axis.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Quartet Pair Symmetry Gate",
        "",
        "Scope: test whether the locked page-76 `OBBO` / `YKKY` quartet supplies a fold-pair, mirror-pair, or p78-frame midpoint rule. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active pattern: `{result['summary']['colorPattern']}` / `{result['summary']['visualStatePattern']}`",
        f"- Active line order: `{result['summary']['pageLines']}`",
        f"- Active corridor order: `{result['summary']['corridorIndexes']}`",
        f"- One-line tolerance benchmark: `{result['linePitchPx']} px`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Natural Color Pair Test",
        "",
        "| test | value | pass within one line pitch? |",
        "|---|---:|---|",
        f"| horizontal fold max error | `{primary['horizontalFold']['maxErrorPx']} px` | `{primary['horizontalFold']['passesOneLinePitch']}` |",
        f"| vertical fold max error | `{primary['verticalFold']['maxErrorPx']} px` | `{primary['verticalFold']['passesOneLinePitch']}` |",
        f"| point-reflection midpoint spread | `{primary['pointReflection']['midpointSpreadPx']} px` | `{primary['pointReflection']['passesOneLinePitch']}` |",
        "",
        "Natural pairs:",
    ]
    for pair in primary_pairs:
        lines.append(
            f"- `{pair['pair'][0]}` <-> `{pair['pair'][1]}` midpoint `{pair['midpoint']}`, dx `{pair['dxAbsPx']} px`, dy `{pair['dyAbsPx']} px`, line gap `{pair['lineGap']}`, corridor gap `{pair['corridorGap']}`."
        )
    lines.extend(["", "## P78 Frame Relation", "", "| frame | best pair | 2D distance to frame center | within one line pitch? |", "|---|---|---:|---|"])
    for relation in frame_relations:
        best = relation["bestPair"]
        lines.append(
            f"| `{relation['name']}` | `{best['pair'][0]}` <-> `{best['pair'][1]}` | `{best['distanceToFrameCenterPx']} px` | `{best['withinOneLinePitch2d']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The palindromic `OBBO` / `YKKY` color-state order does not create a clean current-scan fold axis.",
            "- The black B4/G5 midpoint nearly matches the p78 same-layout frame in X, but misses the frame center by more than two line pitches in 2D; this supports same-slot validation only.",
            "- The current p78->p76 mirror frame does not center either color pair cleanly.",
            "- No selector was unlocked. Reopen only if source wording names color-pair folding, pair midpoints, or an axis.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("selectorUnlocked:", selector_unlocked)
    print("bestAxis:", result["decision"]["bestAxis"])
    print("bestFrameRelation:", result["decision"]["bestFrameRelation"])


if __name__ == "__main__":
    main()
