#!/usr/bin/env python3
"""Control-test page-76 highlight fold axes against the full highlight population.

This bounded geometry pass asks whether the locked O4/B4/G5/O5 quartet is
selected by a simple horizontal, vertical, or point-reflection axis when the
axis is chosen from the full page-76 highlight population. It does not perform
OCR, extraction, hashing, key derivation, seed/WIF checks, address checks, or
broad candidate generation.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BENCH_JSON = (
    ROOT
    / "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
ACTIVE_JSON = (
    ROOT
    / "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
PITCH_JSON = ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_highlight_fold_axis_population_gate.json"
OUT_MD = OUT / "page76_highlight_fold_axis_population_gate.md"
OUT_SHEET = OUT / "page76_highlight_fold_axis_population_gate_sheet.jpg"

STRICT_TERMS = re.compile(
    r"\b(read|take|first|last|letter|letters|word|words|line|lines|order|key|seed|private|wif|phrase)\b",
    re.I,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


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


def reflect(point: tuple[float, float], mode: str, axis_x: float | None, axis_y: float | None) -> tuple[float, float]:
    x, y = point
    if mode == "vertical":
        assert axis_x is not None
        return (2.0 * axis_x - x, y)
    if mode == "horizontal":
        assert axis_y is not None
        return (x, 2.0 * axis_y - y)
    assert axis_x is not None and axis_y is not None
    return (2.0 * axis_x - x, 2.0 * axis_y - y)


def build_population(bench: dict[str, Any], active: dict[str, Any]) -> list[dict[str, Any]]:
    # The benchmark file has useful page-76 controls, but its older G4/G5 boxes
    # are not the active-trusted B4/G5 geometry. Replace active rows with the
    # crop-completion authority and keep O1/O2/O3/G1/G2/G3 as controls.
    population: list[dict[str, Any]] = []
    for row in bench["targets"]:
        if row["id"] in {"O4", "G4", "G5", "O5"}:
            continue
        box = [float(v) for v in row["box"]]
        population.append(
            {
                "id": row["id"],
                "label": row["label"],
                "kind": row["kind"],
                "box": box,
                "center": center(box),
                "active": False,
                "authority": "page76_all_source_highlight_mirror_benchmark",
            }
        )

    active_ids = {
        "buying_dip": "O4",
        "one_billion": "B4",
        "volcano_bonds": "G5",
        "shitcoiner_heart": "O5",
    }
    for row in active["targets"]:
        box = [float(v) for v in row["box"]]
        population.append(
            {
                "id": active_ids[row["id"]],
                "label": row["phrase"],
                "kind": "orange" if row["visualState"] == "Y" else "black",
                "box": box,
                "center": center(box),
                "active": True,
                "pageLine": row.get("pageLine"),
                "corridorIndex": row.get("corridorIndex"),
                "visualState": row.get("visualState"),
                "authority": "page76_active_target_crop_completion",
            }
        )
    return population


def axis_candidates(population: list[dict[str, Any]], page_size: tuple[int, int]) -> list[dict[str, Any]]:
    axes: list[dict[str, Any]] = []
    for i, a in enumerate(population):
        for b in population[i + 1 :]:
            mx = (a["center"][0] + b["center"][0]) / 2.0
            my = (a["center"][1] + b["center"][1]) / 2.0
            axes.extend(
                [
                    {"mode": "vertical", "axisX": mx, "axisY": None, "source": [a["id"], b["id"]]},
                    {"mode": "horizontal", "axisX": None, "axisY": my, "source": [a["id"], b["id"]]},
                    {"mode": "point", "axisX": mx, "axisY": my, "source": [a["id"], b["id"]]},
                ]
            )

    width, height = page_size
    xs = [v for row in population if row["active"] for v in (row["box"][0], row["box"][2])]
    ys = [v for row in population if row["active"] for v in (row["box"][1], row["box"][3])]
    active_axis_x = (min(xs) + max(xs)) / 2.0
    active_axis_y = (min(ys) + max(ys)) / 2.0
    axes.extend(
        [
            {"mode": "vertical", "axisX": width / 2.0, "axisY": None, "source": ["page_center"]},
            {"mode": "horizontal", "axisX": None, "axisY": height / 2.0, "source": ["page_center"]},
            {"mode": "point", "axisX": width / 2.0, "axisY": height / 2.0, "source": ["page_center"]},
            {"mode": "vertical", "axisX": active_axis_x, "axisY": None, "source": ["active_bbox_center"]},
            {"mode": "horizontal", "axisX": None, "axisY": active_axis_y, "source": ["active_bbox_center"]},
            {"mode": "point", "axisX": active_axis_x, "axisY": active_axis_y, "source": ["active_bbox_center"]},
        ]
    )
    return axes


def evaluate_axis(axis: dict[str, Any], population: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    active_rows = [row for row in population if row["active"]]
    hits = []
    for row in active_rows:
        reflected = reflect(row["center"], axis["mode"], axis["axisX"], axis["axisY"])
        nearest = min(population, key=lambda item: distance(item["center"], reflected))
        dist = distance(nearest["center"], reflected)
        if dist <= threshold:
            hits.append(
                {
                    "from": row["id"],
                    "to": nearest["id"],
                    "distancePx": round(dist, 2),
                    "toActive": bool(nearest["active"]),
                    "reflectedCenter": [round(reflected[0], 2), round(reflected[1], 2)],
                }
            )

    active_hits = [hit for hit in hits if hit["toActive"]]
    active_ids = {row["id"] for row in active_rows}
    source_active = set(axis["source"]).issubset(active_ids)
    reciprocal_source_hits = source_active and axis["mode"] == "point" and {
        (hit["from"], hit["to"]) for hit in active_hits
    } == {(axis["source"][0], axis["source"][1]), (axis["source"][1], axis["source"][0])}
    labels = " ".join(row["label"] for row in population if row["id"] in axis["source"])
    return {
        "mode": axis["mode"],
        "axisX": round(axis["axisX"], 2) if axis["axisX"] is not None else None,
        "axisY": round(axis["axisY"], 2) if axis["axisY"] is not None else None,
        "source": axis["source"],
        "hits": hits,
        "activeHitCount": len(active_hits),
        "allHitCount": len(hits),
        "isTautologicalActivePairPointAxis": reciprocal_source_hits,
        "strictInstructionHit": bool(STRICT_TERMS.search(labels)),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [220, 260, 2320, 3060]
    scale = 0.36
    panel = page.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 30
    header_h = 150
    side_w = 720
    sheet = Image.new("RGB", (margin * 3 + panel.width + side_w, header_h + panel.height + margin), (13, 16, 21))
    draw = ImageDraw.Draw(sheet)
    title_font = font(28)
    normal = font(16)
    small = font(13)
    mono = font(13)

    draw.text((margin, 26), "Page 76 Highlight Fold-Axis Population Gate", fill=(240, 244, 248), font=title_font)
    draw.text(
        (margin, 66),
        "Enumerates horizontal, vertical, and point-reflection axes from all page-76 highlight targets.",
        fill=(180, 190, 202),
        font=normal,
    )
    draw.text(
        (margin, 94),
        "Orange/gray outlines are control highlights; thick white centers mark locked O4/B4/G5/O5.",
        fill=(180, 190, 202),
        font=small,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(x: float) -> float:
        return margin + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return header_h + (y - crop[1]) * scale

    for row in result["population"]:
        box = row["box"]
        color = "#ff9b2e" if row["kind"] == "orange" else "#9aa4b2"
        width = 4 if row["active"] else 2
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)
        cx, cy = row["center"]
        r = 5 if row["active"] else 3
        draw.ellipse((sx(cx) - r, sy(cy) - r, sx(cx) + r, sy(cy) + r), fill="#ffffff")
        draw.text((sx(box[0]), sy(box[1]) - 15), row["id"], fill="#ffffff", font=small)

    # Draw only representative non-tautological axes with hits; all-four/three-plus
    # axes are absent, which is the point of the gate.
    representative = result["representativeAxes"][:5]
    axis_colors = ["#55d6ff", "#ffcf5a", "#d88cff", "#6ef3a5", "#ff8fa3"]
    for axis, color in zip(representative, axis_colors):
        if axis["mode"] == "vertical" and axis["axisX"] is not None:
            draw.line((sx(axis["axisX"]), sy(crop[1]), sx(axis["axisX"]), sy(crop[3])), fill=color, width=2)
        elif axis["mode"] == "horizontal" and axis["axisY"] is not None:
            draw.line((sx(crop[0]), sy(axis["axisY"]), sx(crop[2]), sy(axis["axisY"])), fill=color, width=2)
        elif axis["mode"] == "point" and axis["axisX"] is not None and axis["axisY"] is not None:
            draw.ellipse((sx(axis["axisX"]) - 7, sy(axis["axisY"]) - 7, sx(axis["axisX"]) + 7, sy(axis["axisY"]) + 7), outline=color, width=3)

    x0 = margin * 2 + panel.width
    y = header_h
    summary = result["summary"]
    lines = [
        "Summary",
        f"population: {summary['populationCount']} targets",
        f"axis candidates: {summary['axisCandidateCount']}",
        f"axes with active re-hit: {summary['axesWithAnyActiveHit']}",
        f"all-four active axes: {summary['allFourActiveAxisCount']}",
        f"three-plus active axes: {summary['threePlusActiveAxisCount']}",
        f"two-active axes: {summary['twoActiveAxisCount']}",
        f"non-tautological two-active: {summary['nonTautologicalTwoActiveAxisCount']}",
        f"max non-tautological active hits: {summary['maxNonTautologicalActiveHits']}",
        f"strict instruction hits: {summary['strictInstructionAxisHits']}",
        "",
        "Representative non-tautological hits",
    ]
    for line in lines:
        draw.text((x0, y), line, fill=(240, 244, 248) if line == "Summary" else (190, 199, 210), font=normal if line == "Summary" else mono)
        y += 24
    for axis in representative[:8]:
        label = f"{axis['mode']} {axis['source']} -> {axis['hits'][:2]}"
        draw.text((x0, y), label[:88], fill=(190, 199, 210), font=mono)
        y += 22
    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    bench = load_json(BENCH_JSON)
    active = load_json(ACTIVE_JSON)
    pitch = load_json(PITCH_JSON)["linePitch"]["median"]
    page_size = Image.open(PAGE_IMAGE).size
    population = build_population(bench, active)
    axes = axis_candidates(population, page_size)
    evaluated = [evaluate_axis(axis, population, pitch) for axis in axes]
    with_hits = [row for row in evaluated if row["allHitCount"] > 0]
    with_hits.sort(
        key=lambda row: (
            -row["activeHitCount"],
            row["isTautologicalActivePairPointAxis"],
            -row["allHitCount"],
            row["mode"],
            row["source"],
        )
    )
    non_taut = [row for row in with_hits if not row["isTautologicalActivePairPointAxis"]]
    two_active = [row for row in with_hits if row["activeHitCount"] == 2]
    three_plus = [row for row in with_hits if row["activeHitCount"] >= 3]
    all_four = [row for row in with_hits if row["activeHitCount"] == 4]
    summary = {
        "linePitchPx": round(pitch, 2),
        "populationCount": len(population),
        "activeTargetCount": sum(1 for row in population if row["active"]),
        "axisCandidateCount": len(axes),
        "axesWithAnyActiveHit": len(with_hits),
        "allFourActiveAxisCount": len(all_four),
        "threePlusActiveAxisCount": len(three_plus),
        "twoActiveAxisCount": len(two_active),
        "tautologicalTwoActivePointAxisCount": sum(1 for row in two_active if row["isTautologicalActivePairPointAxis"]),
        "nonTautologicalTwoActiveAxisCount": sum(1 for row in two_active if not row["isTautologicalActivePairPointAxis"]),
        "maxNonTautologicalActiveHits": max([row["activeHitCount"] for row in non_taut] or [0]),
        "strictInstructionAxisHits": sum(1 for row in evaluated if row["strictInstructionHit"]),
        "selectorUnlocked": False,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 highlight fold-axis population gate; no OCR, extraction, hashing, or key derivation",
        "inputs": {
            "allSourceHighlightMirrorBenchmark": rel(BENCH_JSON),
            "activeTargetCropCompletion": rel(ACTIVE_JSON),
            "linePitch": rel(PITCH_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "population": [
            {
                **row,
                "center": [round(row["center"][0], 2), round(row["center"][1], 2)],
            }
            for row in population
        ],
        "summary": summary,
        "topAxes": with_hits[:20],
        "representativeAxes": non_taut[:12],
        "assessment": [
            "No horizontal, vertical, or point-reflection axis from the page-76 highlight population re-hits all four locked active targets.",
            "No tested axis re-hits three locked active targets.",
            "The only two-active hits are tautological point axes generated from the same two active target centers.",
            "Non-tautological axes re-hit at most one active target, usually as a near self-hit, and do not provide a unit/order rule.",
        ],
        "decision": {
            "page76HighlightFoldAxisPopulationGate": "population_fold_axes_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Keep page-76 fold/mirror axes as source-validation context only unless a new source/clue names a specific axis, fold operation, or reading unit/order.",
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md = [
        "# Page 76 Highlight Fold-Axis Population Gate",
        "",
        "Scope: enumerate horizontal, vertical, and point-reflection axes from the full page-76 highlight population, then test whether any single axis re-hits the locked O4/B4/G5/O5 quartet. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Line pitch threshold: `{summary['linePitchPx']} px`.",
        f"- Population targets: `{summary['populationCount']}` (`{summary['activeTargetCount']}` active).",
        f"- Axis candidates tested: `{summary['axisCandidateCount']}`.",
        f"- Axes with any active re-hit: `{summary['axesWithAnyActiveHit']}`.",
        f"- All-four active axes: `{summary['allFourActiveAxisCount']}`.",
        f"- Three-plus active axes: `{summary['threePlusActiveAxisCount']}`.",
        f"- Two-active axes: `{summary['twoActiveAxisCount']}`.",
        f"- Tautological two-active point axes: `{summary['tautologicalTwoActivePointAxisCount']}`.",
        f"- Non-tautological two-active axes: `{summary['nonTautologicalTwoActiveAxisCount']}`.",
        f"- Max non-tautological active hits: `{summary['maxNonTautologicalActiveHits']}`.",
        f"- Strict instruction axis hits: `{summary['strictInstructionAxisHits']}`.",
        "",
        "## Top Active-Rehit Axes",
        "",
    ]
    for row in with_hits[:10]:
        hits = ", ".join(f"{hit['from']}->{hit['to']}({hit['distancePx']})" for hit in row["hits"])
        taut = " tautological" if row["isTautologicalActivePairPointAxis"] else ""
        md.append(
            f"- `{row['mode']}` source `{row['source']}` axisX `{row['axisX']}` axisY `{row['axisY']}`: active hits `{row['activeHitCount']}`, all hits `{row['allHitCount']}`{taut}; {hits}"
        )
    md.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote page-76 highlight-population fold axes as a selector.",
            "- No single simple fold/mirror axis recovers all four active targets or even three active targets.",
            "- The only two-active results are tautological point axes chosen from the same two active target centers.",
            "- Reopen only if a new source/clue names a specific axis, fold operation, or reading unit/order.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
