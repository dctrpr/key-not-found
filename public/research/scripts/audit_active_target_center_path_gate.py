#!/usr/bin/env python3
"""Audit whether active target-center connector paths act as selectors.

This bounded pass tests a tempting visual mechanic after the broad envelope was
closed: draw connector rails through the centers of O4/B4/G5/O5 and inspect
only the words/highlights touched by a narrow rail buffer. It checks active
line order plus a few obvious mirror/color alternatives and line-pitch shifted
controls for the primary path.

No new OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed. Existing OCR-map word boxes are used only
as geometry/density witnesses.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LINE_PITCH_JSON = ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/active_target_center_path_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_target_center_path_gate.json"
OUT_MD = OUT / "active_target_center_path_gate.md"
SHEET = OUT / "active_target_center_path_gate_sheet.jpg"

BUFFER_HALF_WIDTH_PX = 24.0
STRICT_UNIT_TERMS = {
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
}

CONTEXT_TERMS = {
    "bukele",
    "volcano",
    "bonds",
    "bitcoin",
    "imf",
    "loan",
    "sell",
    "billions",
    "trust",
    "shitcoiner",
    "heart",
}


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


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def scan_terms(text: str, terms: set[str]) -> list[str]:
    tokens = [normalize_token(token) for token in re.split(r"\s+", text)]
    return sorted({term for term in terms if term in tokens})


def dist_point_segment(point: list[float], start: list[float], end: list[float]) -> float:
    px, py = point
    ax, ay = start
    bx, by = end
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    x = ax + t * dx
    y = ay + t * dy
    return math.hypot(px - x, py - y)


def min_path_distance(point: list[float], points: list[list[float]]) -> float:
    if len(points) < 2:
        return math.inf
    return min(dist_point_segment(point, a, b) for a, b in zip(points, points[1:]))


def path_length(points: list[list[float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_fraction_subject(subject: list[float], container: list[float]) -> float:
    hit = intersection(subject, container)
    if not hit or area(subject) <= 0:
        return 0.0
    return area(hit) / area(subject)


def target_center_rows(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "phrase": target["phrase"],
                "box": [float(v) for v in target["box"]],
                "center": [round(v, 2) for v in center(target["box"])],
                "visualState": target["visualState"],
                "pageLine": target["pageLine"],
                "corridorIndex": target["corridorIndex"],
            }
        )
    return rows


def shifted_path(points: list[list[float]], dx: float = 0.0, dy: float = 0.0) -> list[list[float]]:
    return [[point[0] + dx, point[1] + dy] for point in points]


def words_near_path(words: list[dict[str, Any]], points: list[list[float]], buffer_px: float) -> list[dict[str, Any]]:
    rows = []
    for word in words:
        distance = min_path_distance(word["center"], points)
        if distance <= buffer_px:
            row = dict(word)
            row["pathDistancePx"] = round(distance, 2)
            rows.append(row)
    return sorted(rows, key=lambda row: (row["center"][1], row["center"][0], row["index"]))


def highlights_near_path(highlights: list[dict[str, Any]], points: list[list[float]], buffer_px: float) -> list[dict[str, Any]]:
    rows = []
    for highlight in highlights:
        distance = min_path_distance(center(highlight["box"]), points)
        if distance <= buffer_px:
            row = dict(highlight)
            row["centerDistancePx"] = round(distance, 2)
            rows.append(row)
    return sorted(rows, key=lambda row: row["id"])


def target_center_hits(targets: list[dict[str, Any]], points: list[list[float]], buffer_px: float) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        distance = min_path_distance(target["center"], points)
        if distance <= buffer_px:
            rows.append(
                {
                    "id": target["id"],
                    "label": target["label"],
                    "distancePx": round(distance, 2),
                    "visualState": target["visualState"],
                    "pageLine": target["pageLine"],
                    "corridorIndex": target["corridorIndex"],
                }
            )
    return rows


def summarize_path(
    path_id: str,
    order: list[dict[str, Any]],
    points: list[list[float]],
    words: list[dict[str, Any]],
    highlights: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    buffer_px: float,
) -> dict[str, Any]:
    near_words = words_near_path(words, points, buffer_px)
    text = " ".join(row["text"] for row in near_words)
    target_words = []
    for word in near_words:
        if any(overlap_fraction_subject(word["box"], target["box"]) >= 0.25 for target in targets):
            target_words.append(word)
    return {
        "id": path_id,
        "order": [row["id"] for row in order],
        "visualStateOrder": "".join(row["visualState"] for row in order),
        "pageLines": [row["pageLine"] for row in order],
        "corridorIndexes": [row["corridorIndex"] for row in order],
        "points": [[round(v, 2) for v in point] for point in points],
        "pathLengthPx": round(path_length(points), 2),
        "bufferHalfWidthPx": buffer_px,
        "wordCount": len(near_words),
        "targetOverlapWordCount": len(target_words),
        "nonTargetWordCount": len(near_words) - len(target_words),
        "text": text,
        "textPreview": text[:260],
        "words": [
            {
                "id": word["id"],
                "index": word["index"],
                "text": word["text"],
                "center": [round(v, 2) for v in word["center"]],
                "pathDistancePx": word["pathDistancePx"],
            }
            for word in near_words
        ],
        "highlightHits": [
            {
                "id": row["id"],
                "kind": row.get("kind"),
                "centerDistancePx": row["centerDistancePx"],
            }
            for row in highlights_near_path(highlights, points, buffer_px)
        ],
        "targetCenterHits": target_center_hits(targets, points, buffer_px),
        "strictInstructionTerms": scan_terms(text, STRICT_UNIT_TERMS),
        "contextTerms": scan_terms(text, CONTEXT_TERMS),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [250, 2070, 1900, 3045]
    scale = 0.62
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 32
    header_h = 160
    side_w = 670
    panel_w, panel_h = panel.size
    sheet_w = margin * 3 + panel_w + side_w
    sheet_h = header_h + panel_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, 28), "Active Target Center Path Gate", fill=(242, 246, 250), font=title)
    draw.text(
        (margin, 70),
        "Tests whether narrow connector rails through O4/B4/G5/O5 centers select instruction text.",
        fill=(178, 188, 200),
        font=normal,
    )
    draw.text(
        (margin, 100),
        "Gold = primary active line-order path. Cyan = shifted controls. Orange/grey = trusted target boxes.",
        fill=(178, 188, 200),
        font=small,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    def draw_box(box: list[float], color: str, width: int = 3) -> None:
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)

    controls = result["controls"]["primaryLineOrderShiftControls"]
    chosen_controls = {-1, 1}
    if controls:
        densest = max(controls, key=lambda row: row["wordCount"])
        chosen_controls.add(densest["linePitchShift"])
    for row in controls:
        if row["linePitchShift"] in chosen_controls:
            points = row["points"]
            draw.line([(sx(x), sy(y)) for x, y in points], fill="#65d9ef", width=2)
            draw.text((sx(points[0][0]) + 4, sy(points[0][1]) + 4), f"{row['linePitchShift']} lp", fill="#65d9ef", font=small)

    primary = result["pathVariants"][0]
    draw.line([(sx(x), sy(y)) for x, y in primary["points"]], fill="#ffd45a", width=6)
    for x, y in primary["points"]:
        draw.ellipse((sx(x) - 6, sy(y) - 6, sx(x) + 6, sy(y) + 6), fill="#ffd45a")

    for target in result["targets"]:
        color = "#ff9b2e" if target["visualState"] == "Y" else "#aab3c2"
        draw_box(target["box"], color, 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 18), target["id"], fill="#ffffff", font=small)

    # Mark selected word centers for the primary rail.
    for word in primary["words"]:
        x, y = word["center"]
        draw.ellipse((sx(x) - 3, sy(y) - 3, sx(x) + 3, sy(y) + 3), fill="#ffffff")

    side_x = margin * 2 + panel_w
    y = header_h
    draw.text((side_x, y), "Result", fill=(242, 246, 250), font=font(24))
    y += 42
    summary_lines = [
        f"buffer half-width: {result['summary']['bufferHalfWidthPx']} px",
        f"primary words: {result['summary']['primaryWordCount']}",
        f"primary non-target words: {result['summary']['primaryNonTargetWordCount']}",
        f"primary strict terms: {result['summary']['primaryStrictInstructionHitCount']}",
        f"variant strict terms: {result['summary']['variantStrictInstructionHitCount']}",
        f"control shifts: {result['summary']['controlShiftCount']}",
        f"control median/max words: {result['summary']['controlMedianWordCount']} / {result['summary']['controlMaxWordCount']}",
        f"comparable controls: {result['summary']['controlComparableWordCount']}",
        f"control strict terms: {result['summary']['controlStrictInstructionHitCount']}",
    ]
    for line in summary_lines:
        draw.text((side_x, y), line, fill=(206, 214, 224), font=normal)
        y += 28

    y += 14
    draw.text((side_x, y), "Primary rail words", fill=(242, 246, 250), font=font(20))
    y += 34
    for word in primary["words"][:14]:
        draw.text(
            (side_x, y),
            f"{word['index']:>3} d={word['pathDistancePx']:>4}: {word['text']}",
            fill=(182, 192, 204),
            font=mono,
        )
        y += 22

    sheet.save(SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    pitch_report = load_json(LINE_PITCH_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
    targets = target_center_rows(active["targets"])
    targets_by_id = {row["id"]: row for row in targets}
    pitch = float(pitch_report.get("gapVsLinePitch", {}).get("medianLinePitchPx") or 73.73)

    def by_ids(ids: list[str]) -> list[dict[str, Any]]:
        return [targets_by_id[item] for item in ids]

    line_order = sorted(targets, key=lambda row: (row["pageLine"], row["corridorIndex"]))
    x_order = sorted(targets, key=lambda row: row["center"][0])
    order_variants = [
        ("line_order_o4_b4_g5_o5", line_order),
        ("x_order_b4_g5_o5_o4", x_order),
        ("orange_then_black_mirror_pair_path", by_ids(["buying_dip", "shitcoiner_heart", "volcano_bonds", "one_billion"])),
        ("black_pair_then_orange_path", by_ids(["one_billion", "volcano_bonds", "buying_dip", "shitcoiner_heart"])),
    ]

    path_variants = []
    for path_id, order in order_variants:
        points = [row["center"] for row in order]
        path_variants.append(
            summarize_path(
                path_id,
                order,
                points,
                page["words"],
                page["highlights"],
                targets,
                BUFFER_HALF_WIDTH_PX,
            )
        )

    primary_points = path_variants[0]["points"]
    controls = []
    for line_shift in range(-10, 5):
        if line_shift == 0:
            continue
        points = shifted_path(primary_points, dy=line_shift * pitch)
        if min(point[1] for point in points) < 0 or max(point[1] for point in points) > page["height"]:
            continue
        control = summarize_path(
            f"line_order_shift_{line_shift:+d}_line_pitches",
            line_order,
            points,
            page["words"],
            page["highlights"],
            targets,
            BUFFER_HALF_WIDTH_PX,
        )
        control["linePitchShift"] = line_shift
        controls.append(control)

    primary = path_variants[0]
    control_word_counts = [row["wordCount"] for row in controls]
    comparable_controls = [
        row for row in controls if row["wordCount"] >= math.floor(primary["wordCount"] * 0.75)
    ]
    variant_strict_count = sum(1 for row in path_variants if row["strictInstructionTerms"])
    control_strict_rows = [row for row in controls if row["strictInstructionTerms"]]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active O4/B4/G5/O5 target-center connector path gate; no new OCR/key derivation/hashing/address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "linePitchSource": rel(LINE_PITCH_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "linePitchPx": round(pitch, 4),
        "targets": targets,
        "pathVariants": path_variants,
        "controls": {
            "method": "primary active line-order connector path translated by integer multiples of current median line pitch",
            "primaryLineOrderShiftControls": controls,
        },
        "summary": {
            "bufferHalfWidthPx": BUFFER_HALF_WIDTH_PX,
            "primaryOrder": primary["order"],
            "primaryVisualStateOrder": primary["visualStateOrder"],
            "primaryWordCount": primary["wordCount"],
            "primaryTargetOverlapWordCount": primary["targetOverlapWordCount"],
            "primaryNonTargetWordCount": primary["nonTargetWordCount"],
            "primaryText": primary["text"],
            "primaryStrictInstructionHitCount": len(primary["strictInstructionTerms"]),
            "primaryStrictInstructionTerms": primary["strictInstructionTerms"],
            "primaryContextTerms": primary["contextTerms"],
            "variantCount": len(path_variants),
            "variantWordCounts": {row["id"]: row["wordCount"] for row in path_variants},
            "variantStrictInstructionHitCount": variant_strict_count,
            "controlShiftCount": len(controls),
            "controlWordCounts": control_word_counts,
            "controlMedianWordCount": round(median(control_word_counts), 2) if control_word_counts else 0,
            "controlMaxWordCount": max(control_word_counts) if control_word_counts else 0,
            "controlComparableWordCount": len(comparable_controls),
            "controlComparableShifts": [row["linePitchShift"] for row in comparable_controls],
            "controlStrictInstructionHitCount": len(control_strict_rows),
            "controlStrictInstructionHitShifts": [row["linePitchShift"] for row in control_strict_rows],
            "selectorUnlocked": False,
        },
        "decision": {
            "activeTargetCenterPathGate": "do-not-promote",
            "reason": (
                "Narrow connector rails through the active target centers touch only sparse, corrupted/contextual OCR-map words, "
                "produce no strict unit/order instruction terms, and have same-line-pitch shifted controls with comparable or higher word density."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Keep active target-center paths as visual/source-comparison context only. Reopen only if a source/clue names a connector line, path, rail, or target-center operation plus a unit/order rule."
        ),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result)

    lines = [
        "# Active Target Center Path Gate",
        "",
        "Scope: test whether narrow connector paths through O4/B4/G5/O5 centers act as selectors. No new OCR, key derivation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Buffer half-width: `{BUFFER_HALF_WIDTH_PX}` px",
        f"- Line pitch: `{result['linePitchPx']}` px",
        f"- Primary path: `{result['summary']['primaryOrder']}`",
        f"- Primary path words: `{result['summary']['primaryWordCount']}`",
        f"- Primary non-target words: `{result['summary']['primaryNonTargetWordCount']}`",
        f"- Primary strict instruction terms: `{result['summary']['primaryStrictInstructionTerms']}`",
        f"- Primary context terms: `{result['summary']['primaryContextTerms']}`",
        f"- Variant strict-instruction path count: `{result['summary']['variantStrictInstructionHitCount']}`",
        f"- Shift controls tested: `{result['summary']['controlShiftCount']}`",
        f"- Control median/max word count: `{result['summary']['controlMedianWordCount']}` / `{result['summary']['controlMaxWordCount']}`",
        f"- Comparable shifted controls (>=75% primary word count): `{result['summary']['controlComparableShifts']}`",
        f"- Control strict instruction shifts: `{result['summary']['controlStrictInstructionHitShifts']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Path Variants",
        "",
        "| path | order | words | non-target | strict terms | context terms | text |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for row in path_variants:
        text = row["text"].replace("|", "\\|")
        lines.append(
            f"| `{row['id']}` | `{row['order']}` | {row['wordCount']} | {row['nonTargetWordCount']} | `{row['strictInstructionTerms']}` | `{row['contextTerms']}` | {text} |"
        )

    controls_sorted = sorted(controls, key=lambda row: (-row["wordCount"], abs(row["linePitchShift"])))
    lines.extend(
        [
            "",
            "## Densest Shift Controls",
            "",
            "| shift | words | strict terms | text preview |",
            "|---:|---:|---|---|",
        ]
    )
    for row in controls_sorted[:10]:
        preview = row["textPreview"].replace("|", "\\|")
        lines.append(
            f"| {row['linePitchShift']} | {row['wordCount']} | `{row['strictInstructionTerms']}` | {preview} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote active target-center connector paths as a selector.",
            f"- The primary path touches `{primary['wordCount']}` OCR-map words, `{primary['nonTargetWordCount']}` of them non-target words, and has `{len(primary['strictInstructionTerms'])}` strict instruction-term hits.",
            f"- The alternative target-center paths have `{variant_strict_count}` strict-instruction path hits across `{len(path_variants)}` variants.",
            f"- The shifted controls have median/max word counts `{result['summary']['controlMedianWordCount']}` / `{result['summary']['controlMaxWordCount']}` and `{len(control_strict_rows)}` strict-instruction rows.",
            "- Next best move: keep center paths as visual/source-validation context only unless a new source/clue names path/rail/connector geometry and a unit/order rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("primaryWordCount:", result["summary"]["primaryWordCount"])
    print("primaryNonTargetWordCount:", result["summary"]["primaryNonTargetWordCount"])
    print("primaryStrictInstructionHitCount:", result["summary"]["primaryStrictInstructionHitCount"])
    print("controlComparableWordCount:", result["summary"]["controlComparableWordCount"])


if __name__ == "__main__":
    main()
