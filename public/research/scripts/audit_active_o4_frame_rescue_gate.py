#!/usr/bin/env python3
"""Measure whether O4 is recovered by a clean p78-frame extension.

The same-layout p78 frame hits B4/G5/O5 but misses O4. The current mirror frame
mostly clips O5. This bounded geometry pass checks the combined left/right
frame envelope and asks whether O4 is recovered by a clean line-pitch extension,
while still treating the result as source-comparison evidence unless an
external/source instruction names this operation.

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
OUT = ROOT / "analysis_outputs/source_audit/active_o4_frame_rescue_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_o4_frame_rescue_gate.json"
OUT_MD = OUT / "active_o4_frame_rescue_gate.md"
SHEET = OUT / "active_o4_frame_rescue_gate_sheet.jpg"


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


def round_box(box: list[float]) -> list[float]:
    return [round(v, 2) for v in box]


def union_frame(a: list[float], b: list[float]) -> list[float]:
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def expansion_needed(frame: list[float], targets: list[dict[str, Any]]) -> dict[str, float]:
    min_x = min(t["box"][0] for t in targets)
    min_y = min(t["box"][1] for t in targets)
    max_x = max(t["box"][2] for t in targets)
    max_y = max(t["box"][3] for t in targets)
    return {
        "left": round(max(0.0, frame[0] - min_x), 2),
        "top": round(max(0.0, frame[1] - min_y), 2),
        "right": round(max(0.0, max_x - frame[2]), 2),
        "bottom": round(max(0.0, max_y - frame[3]), 2),
    }


def touch_expansion_needed(frame: list[float], targets: list[dict[str, Any]]) -> dict[str, float]:
    # Minimal expansion that gives non-zero overlap with each target.
    needs = {"left": 0.0, "top": 0.0, "right": 0.0, "bottom": 0.0}
    for target in targets:
        box = target["box"]
        if overlap_fraction(frame, box) > 0:
            continue
        dx_left = max(0.0, frame[0] - box[2])
        dx_right = max(0.0, box[0] - frame[2])
        dy_top = max(0.0, frame[1] - box[3])
        dy_bottom = max(0.0, box[1] - frame[3])
        # For an axis-aligned expansion, a target can require horizontal and/or vertical expansion.
        needs["left"] = max(needs["left"], dx_left)
        needs["right"] = max(needs["right"], dx_right)
        needs["top"] = max(needs["top"], dy_top)
        needs["bottom"] = max(needs["bottom"], dy_bottom)
    return {k: round(v, 2) for k, v in needs.items()}


def classify_frame(frame_id: str, frame: list[float], targets: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for target in targets:
        frac = overlap_fraction(frame, target["box"])
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "visualState": target["visualState"],
                "pageLine": target["pageLine"],
                "corridorIndex": target["corridorIndex"],
                "overlapVsTarget": round(frac, 6),
                "fullHit": frac >= 0.95,
                "partialHit": frac > 0,
            }
        )
    return {
        "id": frame_id,
        "frame": round_box(frame),
        "fullHitCount": sum(row["fullHit"] for row in rows),
        "partialHitCount": sum(row["partialHit"] for row in rows),
        "hitIds": [row["id"] for row in rows if row["partialHit"]],
        "fullHitIds": [row["id"] for row in rows if row["fullHit"]],
        "rows": rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [150, 2050, 2320, 3065]
    scale = 0.48
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 142
    footer_h = 260
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 22), "O4 Frame Rescue Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 60),
        "Checks whether the dual p78 frame envelope recovers O4 by a clean line-pitch extension.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 88),
        "Cyan = same-layout frame. Blue = current mirror frame. Yellow = dual-frame envelope extended upward by 3 line pitches.",
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

    frames = result["frames"]
    draw_box(frames["sameLayout"], "#55d6ff", 3)
    draw_box(frames["currentMirror"], "#4f7dff", 3)
    draw_box(frames["dualEnvelope"], "#91a2b8", 2)
    draw_box(frames["dualEnvelopeTopMinus3LinePitch"], "#ffe45c", 4)

    target_colors = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for target in result["targets"]:
        draw_box(target["box"], target_colors.get(target["visualState"], "#ffffff"), 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 16), target["id"], fill="#ffffff", font=small)

    # Show one-line and three-line offsets above the original top.
    top = frames["dualEnvelope"][1]
    for i in [1, 2, 3]:
        y = top - result["linePitchPx"] * i
        draw.line((sx(frames["dualEnvelope"][0]), sy(y), sx(frames["dualEnvelope"][2]), sy(y)), fill="#ffe45c", width=1)
        draw.text((sx(frames["dualEnvelope"][2]) - 92, sy(y) - 14), f"-{i} line", fill="#ffe45c", font=small)

    y = header_h + panel.size[1] + 22
    draw.text((margin, y), "Rescue Metrics", fill=(238, 243, 248), font=normal)
    y += 32
    rows = [
        ("line pitch", f"{result['linePitchPx']} px"),
        ("dual envelope full expansion", str(result["expansions"]["dualEnvelopeFull"])),
        ("dual envelope touch expansion", str(result["expansions"]["dualEnvelopeTouch"])),
        ("top full / line pitch", result["summary"]["dualEnvelopeFullTopInLinePitches"]),
        ("top touch / line pitch", result["summary"]["dualEnvelopeTouchTopInLinePitches"]),
        ("-3 line envelope hits", ",".join(result["summary"]["topMinus3LinePitchHitIds"])),
        ("-3 line full hits", ",".join(result["summary"]["topMinus3LinePitchFullHitIds"])),
    ]
    for label, value in rows:
        draw.text((margin, y), label, fill=(129, 143, 158), font=small)
        draw.text((margin + 260, y), str(value), fill=(202, 211, 221), font=mono)
        y += 24

    y += 8
    draw.text(
        (margin, y),
        "Result: -3 line-pitch top extension recovers O4/B4/G5 and clips O5, but still needs source wording to become a selector.",
        fill=(255, 219, 137),
        font=normal,
    )
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
    envelope_top_minus_3 = [envelope[0], envelope[1] - 3 * line_pitch, envelope[2], envelope[3]]
    envelope_full_rescue = [
        envelope[0],
        min(t["box"][1] for t in targets),
        envelope[2],
        max(t["box"][3] for t in targets),
    ]

    frames = {
        "sameLayout": same_layout,
        "currentMirror": current_mirror,
        "dualEnvelope": envelope,
        "dualEnvelopeTopMinus3LinePitch": envelope_top_minus_3,
        "dualEnvelopeFullRescue": envelope_full_rescue,
    }
    classifications = [classify_frame(name, frame, targets) for name, frame in frames.items()]
    expansions_full = {
        "sameLayoutFull": expansion_needed(same_layout, targets),
        "currentMirrorFull": expansion_needed(current_mirror, targets),
        "dualEnvelopeFull": expansion_needed(envelope, targets),
    }
    expansions_touch = {
        "sameLayoutTouch": touch_expansion_needed(same_layout, targets),
        "currentMirrorTouch": touch_expansion_needed(current_mirror, targets),
        "dualEnvelopeTouch": touch_expansion_needed(envelope, targets),
    }
    top_full = expansions_full["dualEnvelopeFull"]["top"]
    top_touch = expansions_touch["dualEnvelopeTouch"]["top"]
    top_minus_3 = next(row for row in classifications if row["id"] == "dualEnvelopeTopMinus3LinePitch")

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "O4 recovery test for p78 same-layout/current-mirror frame envelope; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "p78SourceInstructionSurface": rel(P78_SOURCE_JSON),
            "futureSourceScoringRubric": rel(SCORING_JSON),
        },
        "linePitchPx": round(line_pitch, 2),
        "frames": {k: [round(v, 2) for v in frame] for k, frame in frames.items()},
        "targets": [
            {
                "id": row["id"],
                "label": row["label"],
                "phrase": row["phrase"],
                "box": [round(v, 2) for v in row["box"]],
                "visualState": row["visualState"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
            }
            for row in targets
        ],
        "classifications": classifications,
        "expansions": {**expansions_full, **expansions_touch},
        "summary": {
            "dualEnvelopeOriginalHitIds": next(row for row in classifications if row["id"] == "dualEnvelope")["hitIds"],
            "dualEnvelopeFullTopExpansionPx": top_full,
            "dualEnvelopeFullBottomExpansionPx": expansions_full["dualEnvelopeFull"]["bottom"],
            "dualEnvelopeFullTopInLinePitches": round(top_full / line_pitch, 4),
            "dualEnvelopeTouchTopExpansionPx": top_touch,
            "dualEnvelopeTouchTopInLinePitches": round(top_touch / line_pitch, 4),
            "topMinus3LinePitchHitIds": top_minus_3["hitIds"],
            "topMinus3LinePitchFullHitIds": top_minus_3["fullHitIds"],
            "topMinus3LinePitchPartialHitCount": top_minus_3["partialHitCount"],
            "topMinus3LinePitchFullHitCount": top_minus_3["fullHitCount"],
            "selectorUnlocked": False,
        },
        "decision": {
            "activeO4FrameRescue": "source_comparison_benchmark_only",
            "selectorUnlocked": False,
            "nextMove": "Keep the 3-line O4 rescue as a future source/original-layout validation benchmark only; reopen extraction only if source wording names extending/reading above the frame or three-line frame offset.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active O4 Frame Rescue Gate",
        "",
        "Scope: test whether the combined p78 same-layout/current-mirror frame envelope recovers the missing O4 target by a clean line-pitch extension. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Line-pitch benchmark: `{result['linePitchPx']} px`",
        f"- Same-layout frame: `{result['frames']['sameLayout']}`",
        f"- Current-mirror frame: `{result['frames']['currentMirror']}`",
        f"- Dual-frame envelope: `{result['frames']['dualEnvelope']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Expansion Metrics",
        "",
        "| frame | full expansion needed | touch expansion needed |",
        "|---|---|---|",
        f"| same-layout | `{expansions_full['sameLayoutFull']}` | `{expansions_touch['sameLayoutTouch']}` |",
        f"| current mirror | `{expansions_full['currentMirrorFull']}` | `{expansions_touch['currentMirrorTouch']}` |",
        f"| dual envelope | `{expansions_full['dualEnvelopeFull']}` | `{expansions_touch['dualEnvelopeTouch']}` |",
        "",
        "## Frame Checks",
        "",
        "| frame | partial hits | full hits | hit ids | full-hit ids |",
        "|---|---:|---:|---|---|",
    ]
    for row in classifications:
        lines.append(
            f"| `{row['id']}` | `{row['partialHitCount']}` | `{row['fullHitCount']}` | `{', '.join(row['hitIds']) or '-'}` | `{', '.join(row['fullHitIds']) or '-'}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- The dual-frame envelope already covers B4/G5 and clips O5, but misses O4 vertically.",
            f"- Full O4 recovery from the dual envelope requires a top extension of `{top_full}px`, which is `{round(top_full / line_pitch, 4)}` line pitches.",
            f"- Extending the dual envelope upward by exactly three line pitches recovers O4/B4/G5 and still clips O5.",
            "- This is a clean source-comparison benchmark, not extraction permission: it uses the union of two frames plus an extra vertical extension, and no source wording currently names that operation.",
            "- Reopen only if source/original-layout wording names reading above the frame, extending the frame, or a three-line offset.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("dualEnvelopeFullTopExpansionPx:", top_full)
    print("dualEnvelopeFullTopInLinePitches:", round(top_full / line_pitch, 4))
    print("topMinus3LinePitchHitIds:", result["summary"]["topMinus3LinePitchHitIds"])
    print("selectorUnlocked:", False)


if __name__ == "__main__":
    main()
