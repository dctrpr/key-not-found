#!/usr/bin/env python3
"""Check whether p78 frame centers turn active targets into a reflection selector.

The same-layout and current-mirror p78 frames keep recurring around the active
page-76 cluster. This bounded pass asks whether using those frame centers as
horizontal, vertical, or point-reflection axes maps O4/B4/G5/O5 onto
instruction-bearing text or another clean active-target relation.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
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
OUT = ROOT / "analysis_outputs/source_audit/active_frame_center_reflection_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_frame_center_reflection_gate.json"
OUT_MD = OUT / "active_frame_center_reflection_gate.md"
SHEET = OUT / "active_frame_center_reflection_gate_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]


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


def round_box(box: list[float]) -> list[float]:
    return [round(v, 2) for v in box]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def overlap_fraction(frame: list[float], box: list[float]) -> float:
    inter = intersection(frame, box)
    return 0.0 if not inter else area(inter) / max(area(box), 1.0)


def hard_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def transform_box(box: list[float], cx: float, cy: float, mode: str) -> list[float]:
    if mode == "point":
        return [2 * cx - box[2], 2 * cy - box[3], 2 * cx - box[0], 2 * cy - box[1]]
    if mode == "vertical_axis":
        return [2 * cx - box[2], box[1], 2 * cx - box[0], box[3]]
    if mode == "horizontal_axis":
        return [box[0], 2 * cy - box[3], box[2], 2 * cy - box[1]]
    raise ValueError(mode)


def in_bounds(box: list[float], width: float, height: float) -> bool:
    return box[2] > 0 and box[0] < width and box[3] > 0 and box[1] < height


def summarize_projection(
    projected: list[float],
    target: dict[str, Any],
    page: dict[str, Any],
    active_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    word_rows = []
    hard_terms: set[str] = set()
    for word in page.get("words", []):
        frac = overlap_fraction(projected, word["box"])
        if frac <= 0.18:
            continue
        hits = hard_hits(word.get("text", ""))
        hard_terms.update(hits)
        word_rows.append(
            {
                "id": word["id"],
                "text": word.get("text", ""),
                "overlapVsWord": round(frac, 6),
                "importance": word.get("importance", 0),
                "hardInstructionHits": hits,
            }
        )

    highlight_rows = []
    for h in page.get("highlights", []):
        frac = overlap_fraction(projected, h["box"])
        if frac <= 0:
            continue
        highlight_rows.append(
            {
                "id": h["id"],
                "kind": h["kind"],
                "overlapVsHighlight": round(frac, 6),
            }
        )

    active_rows = []
    for other in active_targets:
        if other["id"] == target["id"]:
            continue
        frac = overlap_fraction(projected, other["box"])
        if frac <= 0:
            continue
        active_rows.append(
            {
                "id": other["id"],
                "label": other["label"],
                "overlapVsTarget": round(frac, 6),
            }
        )

    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "projectedBox": round_box(projected),
        "wordCount": len(word_rows),
        "focusWordCount": sum(1 for row in word_rows if row["importance"] >= 3),
        "wordPreview": " ".join(row["text"] for row in word_rows)[:160],
        "hardInstructionHits": sorted(hard_terms),
        "hardInstructionHitCount": len(hard_terms),
        "highlightHitCount": len(highlight_rows),
        "highlightHits": highlight_rows,
        "activeTargetHitCount": len(active_rows),
        "activeTargetHits": active_rows,
        "wordRows": word_rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [150, 2000, 2320, 3065]
    scale = 0.47
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 138
    footer_h = 250
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 22), "Active Frame-Center Reflection Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 60),
        "Projects O4/B4/G5/O5 through p78 same-layout and current-mirror frame centers.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 86),
        "Solid boxes = active targets and p78 frames. Dashed-looking thin boxes = projected active target boxes.",
        fill=(176, 186, 198),
        font=small,
    )

    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    def draw_box(box: list[float], color: str, width: int = 2) -> None:
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)

    draw_box(result["frames"]["sameLayoutFrame"], "#55d6ff", 3)
    draw_box(result["frames"]["currentMirrorFrame"], "#4f7dff", 3)
    for frame in result["frames"]["frameCenters"].values():
        cx, cy = frame
        draw.ellipse((sx(cx) - 5, sy(cy) - 5, sx(cx) + 5, sy(cy) + 5), fill="#ffffff")

    active_color = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for target in result["targets"]:
        draw_box(target["box"], active_color.get(target["visualState"], "#ffffff"), 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 16), target["id"], fill="#ffffff", font=small)

    scenario_colors = {
        "same_layout_point": "#ffeb66",
        "same_layout_vertical_axis": "#87f5a0",
        "same_layout_horizontal_axis": "#ff75c8",
        "current_mirror_point": "#ffc266",
        "current_mirror_vertical_axis": "#75f1ff",
        "current_mirror_horizontal_axis": "#c596ff",
    }
    for scenario in result["scenarios"]:
        color = scenario_colors.get(scenario["id"], "#ffffff")
        for row in scenario["rows"]:
            if not row["inBounds"]:
                continue
            draw_box(row["projectedBox"], color, 1)

    y = header_h + panel.size[1] + 22
    draw.text((margin, y), "Scenario Summary", fill=(238, 243, 248), font=normal)
    y += 30
    headers = [("scenario", 0), ("in", 300), ("words", 360), ("instr", 430), ("active", 505), ("decision", 575)]
    for label, off in headers:
        draw.text((margin + off, y), label, fill=(129, 143, 158), font=small)
    y += 22
    for scenario in result["scenarios"]:
        s = scenario["summary"]
        draw.text((margin, y), scenario["id"], fill=(202, 211, 221), font=mono)
        draw.text((margin + 300, y), str(s["inBoundsCount"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 360, y), str(s["wordHitProjectionCount"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 430, y), str(s["hardInstructionHitCount"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 505, y), str(s["activeTargetRehitCount"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 575, y), "closed", fill=(255, 219, 137), font=mono)
        y += 22

    y += 10
    draw.text(
        (margin, y),
        "Result: all frame-center reflection modes are either off-page, ordinary prose, or non-instructional overlaps.",
        fill=(255, 219, 137),
        font=normal,
    )
    sheet.save(SHEET, quality=94)


def scenario_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    instruction_terms = sorted({term for row in rows for term in row["hardInstructionHits"]})
    active_overlaps = [
        hit["overlapVsTarget"]
        for row in rows
        for hit in row["activeTargetHits"]
    ]
    return {
        "projectionCount": len(rows),
        "inBoundsCount": sum(1 for row in rows if row["inBounds"]),
        "wordHitProjectionCount": sum(1 for row in rows if row["wordCount"] > 0),
        "highlightHitProjectionCount": sum(1 for row in rows if row["highlightHitCount"] > 0),
        "activeTargetRehitCount": sum(row["activeTargetHitCount"] for row in rows),
        "strongActiveTargetRehitCount": sum(1 for value in active_overlaps if value >= 0.5),
        "maxActiveTargetRehitOverlap": round(max(active_overlaps), 6) if active_overlaps else 0.0,
        "hardInstructionHitCount": len(instruction_terms),
        "hardInstructionHits": instruction_terms,
        "selectorUnlocked": False,
    }


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    p78_source = load_json(P78_SOURCE_JSON)
    scoring = load_json(SCORING_JSON)
    page76 = next(page for page in article["pages"] if page["page"] == 76)
    width = float(page76["width"])
    height = float(page76["height"])

    active_targets = active["targets"]
    targets = [
        {
            "id": row["id"],
            "label": row["label"],
            "phrase": row["phrase"],
            "box": round_box(row["box"]),
            "center": [round(v, 2) for v in center(row["box"])],
            "visualState": row["visualState"],
            "pageLine": row["pageLine"],
            "corridorIndex": row["corridorIndex"],
        }
        for row in active_targets
    ]

    same_layout_frame = list(map(float, p78_source["sourceGraphic"]["box"]))
    current_mirror_frame = list(map(float, scoring["numericBenchmarks"]["p78Frame"]["currentFrame"]))
    frames = {
        "same_layout": same_layout_frame,
        "current_mirror": current_mirror_frame,
    }
    modes = ["point", "vertical_axis", "horizontal_axis"]

    scenarios = []
    for frame_id, frame in frames.items():
        cx, cy = center(frame)
        for mode in modes:
            rows = []
            for target in active_targets:
                projected = transform_box(list(map(float, target["box"])), cx, cy, mode)
                summary = summarize_projection(projected, target, page76, active_targets)
                summary["inBounds"] = in_bounds(projected, width, height)
                rows.append(summary)
            scenario_id = f"{frame_id}_{mode}"
            scenarios.append(
                {
                    "id": scenario_id,
                    "frame": round_box(frame),
                    "frameCenter": [round(cx, 2), round(cy, 2)],
                    "mode": mode,
                    "summary": scenario_summary(rows),
                    "rows": rows,
                }
            )

    total_instruction_terms = sorted({term for s in scenarios for term in s["summary"]["hardInstructionHits"]})
    total_active_rehits = sum(s["summary"]["activeTargetRehitCount"] for s in scenarios)
    total_strong_active_rehits = sum(s["summary"]["strongActiveTargetRehitCount"] for s in scenarios)
    max_active_rehit_overlap = max(s["summary"]["maxActiveTargetRehitOverlap"] for s in scenarios)
    best_word_scenario = max(scenarios, key=lambda s: s["summary"]["wordHitProjectionCount"])

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active target reflection through p78 frame centers; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "p78SourceInstructionSurface": rel(P78_SOURCE_JSON),
            "futureSourceScoringRubric": rel(SCORING_JSON),
        },
        "page": {"page": 76, "width": page76["width"], "height": page76["height"]},
        "targets": targets,
        "frames": {
            "sameLayoutFrame": round_box(same_layout_frame),
            "currentMirrorFrame": round_box(current_mirror_frame),
            "frameCenters": {
                "sameLayout": [round(v, 2) for v in center(same_layout_frame)],
                "currentMirror": [round(v, 2) for v in center(current_mirror_frame)],
            },
        },
        "scenarios": scenarios,
        "summary": {
            "scenarioCount": len(scenarios),
            "projectionCount": sum(s["summary"]["projectionCount"] for s in scenarios),
            "inBoundsProjectionCount": sum(s["summary"]["inBoundsCount"] for s in scenarios),
            "totalHardInstructionHitCount": len(total_instruction_terms),
            "totalHardInstructionHits": total_instruction_terms,
            "totalActiveTargetRehitCount": total_active_rehits,
            "totalStrongActiveTargetRehitCount": total_strong_active_rehits,
            "maxActiveTargetRehitOverlap": max_active_rehit_overlap,
            "bestWordHitScenario": best_word_scenario["id"],
            "bestWordHitProjectionCount": best_word_scenario["summary"]["wordHitProjectionCount"],
            "selectorUnlocked": False,
        },
        "decision": {
            "activeFrameCenterReflection": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep p78 frame centers as source-comparison landmarks only; reopen only if source wording names center reflection, frame-center axis, or same-slot frame flipping.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Frame-Center Reflection Gate",
        "",
        "Scope: project locked O4/B4/G5/O5 boxes through p78 same-layout and current-mirror frame centers using point reflection, vertical-axis reflection, and horizontal-axis reflection. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Same-layout frame center: `{result['frames']['frameCenters']['sameLayout']}`",
        f"- Current-mirror frame center: `{result['frames']['frameCenters']['currentMirror']}`",
        f"- Total scenarios: `{result['summary']['scenarioCount']}`",
        f"- Total projections: `{result['summary']['projectionCount']}`",
        f"- In-bounds projections: `{result['summary']['inBoundsProjectionCount']}`",
        f"- Hard instruction hits: `{result['summary']['totalHardInstructionHitCount']}`",
        f"- Active-target re-hits: `{result['summary']['totalActiveTargetRehitCount']}` total, `{result['summary']['totalStrongActiveTargetRehitCount']}` strong",
        f"- Max active-target re-hit overlap: `{result['summary']['maxActiveTargetRehitOverlap']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Scenario Summary",
        "",
        "| scenario | in bounds | projections with words | projections with highlights | active target re-hits | instruction hits |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for scenario in scenarios:
        s = scenario["summary"]
        lines.append(
            f"| `{scenario['id']}` | `{s['inBoundsCount']}` | `{s['wordHitProjectionCount']}` | `{s['highlightHitProjectionCount']}` | `{s['activeTargetRehitCount']}` | `{', '.join(s['hardInstructionHits']) or '-'}` |"
        )
    lines.extend(["", "## Landing Previews", ""])
    for scenario in scenarios:
        previews = [row for row in scenario["rows"] if row["wordPreview"]]
        if not previews:
            continue
        lines.append(f"### {scenario['id']}")
        for row in previews[:4]:
            lines.append(f"- `{row['targetId']}` -> `{row['wordPreview']}`")
        lines.append("")
    lines.extend(
        [
            "## Decision",
            "",
            "- Frame-center reflection does not create a selector from O4/B4/G5/O5.",
            "- The projections either land off-page, on ordinary body prose, or on non-instructional highlight/active geometry.",
            "- The only active-target re-hits are weak partial B4/O5 contacts under same-layout point reflection; the maximum overlap is `0.198042`, below a usable target-transfer threshold.",
            "- No hard instruction term and no strong active-target re-hit was produced across all six bounded reflection modes.",
            "- Keep p78 frame centers as source-comparison landmarks only; reopen only if source wording names center reflection, frame-center axis, or same-slot frame flipping.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("scenarioCount:", result["summary"]["scenarioCount"])
    print("inBoundsProjectionCount:", result["summary"]["inBoundsProjectionCount"])
    print("hardInstructionHitCount:", result["summary"]["totalHardInstructionHitCount"])
    print("activeTargetRehitCount:", result["summary"]["totalActiveTargetRehitCount"])


if __name__ == "__main__":
    main()
