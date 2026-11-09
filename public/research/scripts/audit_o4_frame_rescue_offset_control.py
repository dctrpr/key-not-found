#!/usr/bin/env python3
"""Control-test the O4 frame-rescue offset against nearby line-pitch offsets.

The previous pass found that the union of the p78 same-layout and current
mirror frames recovers O4 with a three-line top extension. This bounded pass
checks whether that is a unique selector or just the minimum integer line
offset in a family of larger frame extensions.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
P78_SOURCE_JSON = ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json"
SCORING_JSON = ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_offset_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "o4_frame_rescue_offset_control.json"
OUT_MD = OUT / "o4_frame_rescue_offset_control.md"
SHEET = OUT / "o4_frame_rescue_offset_control_sheet.jpg"


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


def union_frame(a: list[float], b: list[float]) -> list[float]:
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def classify_frame(frame: list[float], targets: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for target in targets:
        frac = overlap_fraction(frame, target["box"])
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "visualState": target["visualState"],
                "overlapVsTarget": round(frac, 6),
                "partialHit": frac > 0,
                "fullHit": frac >= 0.95,
            }
        )
    return {
        "partialHitCount": sum(row["partialHit"] for row in rows),
        "fullHitCount": sum(row["fullHit"] for row in rows),
        "hitIds": [row["id"] for row in rows if row["partialHit"]],
        "fullHitIds": [row["id"] for row in rows if row["fullHit"]],
        "rows": rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [150, 2050, 2320, 3065]
    scale = 0.45
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 140
    footer_h = 360
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 22), "O4 Frame Rescue Offset Control", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 60),
        "Controls the three-line top extension against nearby line-pitch offsets.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 88),
        "Grey = original dual envelope. Yellow = top-only offsets. Pink = 3-up/1-down full-coverage benchmark.",
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

    draw_box(result["dualEnvelope"], "#91a2b8", 3)
    for row in result["topOnlyRows"]:
        if row["topLineOffset"] in [1, 2, 3, 4]:
            draw_box(row["frame"], "#ffe45c" if row["topLineOffset"] == 3 else "#bda94c", 2 if row["topLineOffset"] == 3 else 1)
            draw.text((sx(row["frame"][2]) - 65, sy(row["frame"][1]) - 12), f"-{row['topLineOffset']}", fill="#ffe45c", font=small)
    draw_box(result["minimumFullCoverageFrame"], "#ff73c8", 4)

    colors = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for target in result["targets"]:
        draw_box(target["box"], colors.get(target["visualState"], "#ffffff"), 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 16), target["id"], fill="#ffffff", font=small)

    y = header_h + panel.size[1] + 22
    draw.text((margin, y), "Top-Only Offset Control", fill=(238, 243, 248), font=normal)
    y += 30
    headers = [("top lines", 0), ("partial", 100), ("full", 190), ("hit ids", 275), ("full ids", 610)]
    for label, off in headers:
        draw.text((margin + off, y), label, fill=(129, 143, 158), font=small)
    y += 22
    for row in result["topOnlyRows"]:
        draw.text((margin, y), str(row["topLineOffset"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 100, y), str(row["partialHitCount"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 190, y), str(row["fullHitCount"]), fill=(202, 211, 221), font=mono)
        draw.text((margin + 275, y), ",".join(row["hitIds"])[:42], fill=(202, 211, 221), font=mono)
        draw.text((margin + 610, y), ",".join(row["fullHitIds"])[:36], fill=(202, 211, 221), font=mono)
        y += 22

    y += 18
    draw.text((margin, y), "Decision", fill=(238, 243, 248), font=normal)
    y += 28
    notes = [
        f"Minimum integer top-only offset for all four partial hits: {result['summary']['minimumTopOnlyAllFourPartial']} lines.",
        f"Top-only all-four partial offsets: {result['summary']['topOnlyAllFourPartialOffsets']}.",
        f"Minimum full-coverage grid offset: top {result['summary']['minimumFullCoverageTopLines']} / bottom {result['summary']['minimumFullCoverageBottomLines']} lines.",
        "This remains a source-comparison benchmark because no clue names line-pitch frame extension.",
    ]
    for note in notes:
        draw.text((margin, y), note, fill=(255, 219, 137), font=normal)
        y += 24

    sheet.save(SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    p78_source = load_json(P78_SOURCE_JSON)
    scoring = load_json(SCORING_JSON)
    targets = active["targets"]
    line_pitch = float(scoring.get("numericBenchmarks", {}).get("p77NearMiss", {}).get("medianLinePitchPx", 73.73))

    same_layout = list(map(float, p78_source["sourceGraphic"]["box"]))
    current_mirror = list(map(float, scoring["numericBenchmarks"]["p78Frame"]["currentFrame"]))
    envelope = union_frame(same_layout, current_mirror)

    top_only_rows = []
    for top_lines in range(0, 7):
        frame = [envelope[0], envelope[1] - top_lines * line_pitch, envelope[2], envelope[3]]
        summary = classify_frame(frame, targets)
        top_only_rows.append(
            {
                "topLineOffset": top_lines,
                "frame": [round(v, 2) for v in frame],
                **summary,
            }
        )

    grid_rows = []
    for top_lines in range(0, 7):
        for bottom_lines in range(0, 4):
            frame = [
                envelope[0],
                envelope[1] - top_lines * line_pitch,
                envelope[2],
                envelope[3] + bottom_lines * line_pitch,
            ]
            summary = classify_frame(frame, targets)
            grid_rows.append(
                {
                    "topLineOffset": top_lines,
                    "bottomLineOffset": bottom_lines,
                    "frame": [round(v, 2) for v in frame],
                    **summary,
                }
            )

    all_four_partial = [row for row in top_only_rows if row["partialHitCount"] == 4]
    all_four_full = [row for row in grid_rows if row["fullHitCount"] == 4]
    min_partial = min((row["topLineOffset"] for row in all_four_partial), default=None)
    min_full = min(all_four_full, key=lambda row: (row["topLineOffset"] + row["bottomLineOffset"], row["topLineOffset"], row["bottomLineOffset"]))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "O4 frame-rescue line-offset control; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "p78SourceInstructionSurface": rel(P78_SOURCE_JSON),
            "futureSourceScoringRubric": rel(SCORING_JSON),
        },
        "linePitchPx": round(line_pitch, 2),
        "sameLayoutFrame": [round(v, 2) for v in same_layout],
        "currentMirrorFrame": [round(v, 2) for v in current_mirror],
        "dualEnvelope": [round(v, 2) for v in envelope],
        "targets": [
            {
                "id": row["id"],
                "label": row["label"],
                "box": [round(v, 2) for v in row["box"]],
                "visualState": row["visualState"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
            }
            for row in targets
        ],
        "topOnlyRows": top_only_rows,
        "gridRows": grid_rows,
        "minimumFullCoverageFrame": min_full["frame"],
        "summary": {
            "topOnlyOffsetCount": len(top_only_rows),
            "gridOffsetCount": len(grid_rows),
            "topOnlyAllFourPartialOffsets": [row["topLineOffset"] for row in all_four_partial],
            "topOnlyAllFourFullOffsets": [row["topLineOffset"] for row in top_only_rows if row["fullHitCount"] == 4],
            "minimumTopOnlyAllFourPartial": min_partial,
            "minimumFullCoverageTopLines": min_full["topLineOffset"],
            "minimumFullCoverageBottomLines": min_full["bottomLineOffset"],
            "minimumFullCoverageTotalLineExpansion": min_full["topLineOffset"] + min_full["bottomLineOffset"],
            "minimumFullCoverageHitIds": min_full["hitIds"],
            "minimumFullCoverageFullHitIds": min_full["fullHitIds"],
            "selectorUnlocked": False,
        },
        "decision": {
            "o4FrameRescueOffsetControl": "source_comparison_benchmark_only",
            "selectorUnlocked": False,
            "nextMove": "Keep 3-up and 3-up/1-down as future source-validation benchmarks only; reopen extraction only if source wording names line-pitch frame extension or above/below frame reading.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# O4 Frame Rescue Offset Control",
        "",
        "Scope: control-test the three-line O4 frame rescue against nearby line-pitch offsets. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Line-pitch benchmark: `{result['linePitchPx']} px`",
        f"- Dual-frame envelope: `{result['dualEnvelope']}`",
        f"- Top-only offsets checked: `{result['summary']['topOnlyOffsetCount']}`",
        f"- Top/bottom grid offsets checked: `{result['summary']['gridOffsetCount']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Top-Only Offset Control",
        "",
        "| top line offset | partial hits | full hits | hit ids | full-hit ids |",
        "|---:|---:|---:|---|---|",
    ]
    for row in top_only_rows:
        lines.append(
            f"| `{row['topLineOffset']}` | `{row['partialHitCount']}` | `{row['fullHitCount']}` | `{', '.join(row['hitIds']) or '-'}` | `{', '.join(row['fullHitIds']) or '-'}` |"
        )
    lines.extend(
        [
            "",
            "## Minimums",
            "",
            f"- Minimum integer top-only offset that touches all four active targets: `{min_partial}` line pitches.",
            f"- Top-only offsets that touch all four active targets: `{result['summary']['topOnlyAllFourPartialOffsets']}`.",
            f"- Top-only offsets that fully cover all four active targets: `{result['summary']['topOnlyAllFourFullOffsets']}`.",
            f"- Minimum top/bottom grid offset that fully covers all four active targets: top `{min_full['topLineOffset']}`, bottom `{min_full['bottomLineOffset']}`, total `{result['summary']['minimumFullCoverageTotalLineExpansion']}` line pitches.",
            "",
            "## Decision",
            "",
            "- The three-line top extension is the minimum integer top-only offset that recovers all four active targets.",
            "- It is not unique once larger top extensions are allowed, so it is not a standalone selector.",
            "- Full coverage of all four targets requires a `3-up / 1-down` line-pitch envelope.",
            "- Keep these as future source/original-layout validation benchmarks only; reopen extraction only if source wording names line-pitch frame extension or above/below frame reading.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("minimumTopOnlyAllFourPartial:", min_partial)
    print("topOnlyAllFourPartialOffsets:", result["summary"]["topOnlyAllFourPartialOffsets"])
    print("minimumFullCoverage:", (min_full["topLineOffset"], min_full["bottomLineOffset"]))
    print("selectorUnlocked:", False)


if __name__ == "__main__":
    main()
