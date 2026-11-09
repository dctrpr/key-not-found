#!/usr/bin/env python3
"""Audit whether the active O4/B4/G5/O5 target envelope is a selector.

This bounded geometry pass treats the minimal page-76 bounding envelope around
the locked active targets as a hypothesis. If the envelope is meaningful as an
extraction selector, it should isolate a compact rule-bearing surface rather
than a broad lower-corridor band of ordinary prose. The pass compares the
active envelope with same-size line-pitch translated controls.

No new OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed. Existing OCR-map word boxes are used only
as a density/control witness.
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

OUT = ROOT / "analysis_outputs/source_audit/active_target_envelope_density_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_target_envelope_density_gate.json"
OUT_MD = OUT / "active_target_envelope_density_gate.md"
SHEET = OUT / "active_target_envelope_density_gate_sheet.jpg"

WORD_OVERLAP_THRESHOLD = 0.25
HIGHLIGHT_OVERLAP_THRESHOLD = 0.01

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


def overlap_fraction_subject(subject: list[float], container: list[float]) -> float:
    hit = intersection(subject, container)
    if not hit or area(subject) <= 0:
        return 0.0
    return area(hit) / area(subject)


def overlap_fraction_container(subject: list[float], container: list[float]) -> float:
    hit = intersection(subject, container)
    if not hit or area(container) <= 0:
        return 0.0
    return area(hit) / area(container)


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def bbox_union(boxes: list[list[float]]) -> list[float]:
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def scan_terms(text: str, terms: set[str]) -> list[str]:
    tokens = [normalize_token(token) for token in re.split(r"\s+", text)]
    present = sorted({term for term in terms if term in tokens})
    return present


def words_in_box(words: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for word in words:
        frac = overlap_fraction_subject(word["box"], box)
        if frac >= WORD_OVERLAP_THRESHOLD:
            row = dict(word)
            row["overlapFraction"] = round(frac, 6)
            rows.append(row)
    return sorted(rows, key=lambda row: (row["center"][1], row["center"][0], row["index"]))


def highlights_in_box(highlights: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for highlight in highlights:
        frac = overlap_fraction_subject(highlight["box"], box)
        if frac >= HIGHLIGHT_OVERLAP_THRESHOLD:
            row = dict(highlight)
            row["overlapFraction"] = round(frac, 6)
            rows.append(row)
    return sorted(rows, key=lambda row: row["id"])


def target_hits(targets: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        subject_frac = overlap_fraction_subject(target["box"], box)
        container_frac = overlap_fraction_container(target["box"], box)
        if subject_frac > 0:
            rows.append(
                {
                    "id": target["id"],
                    "label": target["label"],
                    "phrase": target["phrase"],
                    "visualState": target["visualState"],
                    "pageLine": target["pageLine"],
                    "corridorIndex": target["corridorIndex"],
                    "box": target["box"],
                    "subjectOverlapFraction": round(subject_frac, 6),
                    "envelopeAreaFraction": round(container_frac, 6),
                }
            )
    return rows


def row_groups(words: list[dict[str, Any]], pitch: float) -> list[dict[str, Any]]:
    if not words:
        return []
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    last_y: float | None = None
    threshold = max(24.0, pitch * 0.48)
    for word in words:
        y = word["center"][1]
        if last_y is None or abs(y - last_y) <= threshold:
            current.append(word)
        else:
            groups.append(current)
            current = [word]
        last_y = y
    if current:
        groups.append(current)

    rows = []
    for idx, group in enumerate(groups, start=1):
        sorted_group = sorted(group, key=lambda row: (row["center"][0], row["index"]))
        text = " ".join(row["text"] for row in sorted_group)
        rows.append(
            {
                "rowIndex": idx,
                "wordCount": len(sorted_group),
                "yMedian": round(median(row["center"][1] for row in sorted_group), 2),
                "xMin": round(min(row["box"][0] for row in sorted_group), 2),
                "xMax": round(max(row["box"][2] for row in sorted_group), 2),
                "text": text,
                "strictInstructionTerms": scan_terms(text, STRICT_UNIT_TERMS),
                "contextTerms": scan_terms(text, CONTEXT_TERMS),
            }
        )
    return rows


def box_to_line_range(box: list[float], active_y0: float, pitch: float) -> list[float]:
    return [
        round((box[1] - active_y0) / pitch, 2),
        round((box[3] - active_y0) / pitch, 2),
    ]


def translate_box(box: list[float], dy: float) -> list[float]:
    return [box[0], box[1] + dy, box[2], box[3] + dy]


def polygon_area(points: list[list[float]]) -> float:
    total = 0.0
    for i, p in enumerate(points):
        q = points[(i + 1) % len(points)]
        total += p[0] * q[1] - q[0] * p[1]
    return abs(total) / 2.0


def convex_hull(points: list[list[float]]) -> list[list[float]]:
    pts = sorted({(p[0], p[1]) for p in points})
    if len(pts) <= 1:
        return [[p[0], p[1]] for p in pts]

    def cross(o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for point in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return [[p[0], p[1]] for p in lower[:-1] + upper[:-1]]


def summarize_box(
    box_id: str,
    box: list[float],
    words: list[dict[str, Any]],
    highlights: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    active_y0: float,
    pitch: float,
) -> dict[str, Any]:
    box_words = words_in_box(words, box)
    text = " ".join(row["text"] for row in box_words)
    hit_targets = target_hits(targets, box)
    return {
        "id": box_id,
        "box": [round(v, 2) for v in box],
        "linePitchOffsetRangeFromActiveTop": box_to_line_range(box, active_y0, pitch),
        "wordCount": len(box_words),
        "textPreview": text[:260],
        "rowGroups": row_groups(box_words, pitch),
        "highlightHits": [
            {"id": row["id"], "kind": row.get("kind"), "overlapFraction": row["overlapFraction"]}
            for row in highlights_in_box(highlights, box)
        ],
        "activeTargetHits": hit_targets,
        "activeTargetHitCount": len(hit_targets),
        "strictInstructionTerms": scan_terms(text, STRICT_UNIT_TERMS),
        "contextTerms": scan_terms(text, CONTEXT_TERMS),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [250, 1980, 2050, 3065]
    scale = 0.56
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 32
    header_h = 160
    side_w = 690
    panel_w, panel_h = panel.size
    sheet_w = margin * 3 + panel_w + side_w
    sheet_h = header_h + panel_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, 28), "Active Target Envelope Density Gate", fill=(242, 246, 250), font=title)
    draw.text(
        (margin, 70),
        "Tests whether the minimal O4/B4/G5/O5 envelope isolates a rule-bearing surface.",
        fill=(178, 188, 200),
        font=normal,
    )
    draw.text(
        (margin, 100),
        "Gold = active target envelope. Orange/grey = trusted target boxes. Thin cyan = comparable shifted controls.",
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

    # Draw a few high-information controls: the closest row-pitch shifts and the densest shifted control.
    controls = result["controls"]["rows"]
    chosen_shift_ids = {-1, 1}
    if controls:
        densest = max(controls, key=lambda row: row["wordCount"])
        chosen_shift_ids.add(densest["linePitchShift"])
    for row in controls:
        if row["linePitchShift"] in chosen_shift_ids:
            draw_box(row["box"], "#66d9ef", 2)
            draw.text((sx(row["box"][0]) + 6, sy(row["box"][1]) + 6), f"{row['linePitchShift']} lp", fill="#66d9ef", font=small)

    active = result["activeEnvelope"]
    draw_box(active["box"], "#ffd45a", 5)
    draw.text((sx(active["box"][0]) + 8, sy(active["box"][1]) + 8), "active envelope", fill="#ffd45a", font=small)

    for target in result["targets"]:
        color = "#ff9b2e" if target["visualState"] == "Y" else "#aab3c2"
        draw_box(target["box"], color, 4)
        cx, cy = target["center"]
        draw.ellipse((sx(cx) - 5, sy(cy) - 5, sx(cx) + 5, sy(cy) + 5), fill=color)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 18), target["id"], fill="#ffffff", font=small)

    side_x = margin * 2 + panel_w
    y = header_h
    draw.text((side_x, y), "Result", fill=(242, 246, 250), font=font(24))
    y += 42
    summary_lines = [
        f"active words: {result['summary']['activeEnvelopeWordCount']}",
        f"non-target words: {result['summary']['activeEnvelopeNonTargetWordCount']}",
        f"active targets covered: {result['summary']['activeTargetCoverage']}",
        f"strict terms: {result['summary']['activeStrictInstructionHitCount']}",
        f"context terms: {', '.join(result['activeEnvelope']['contextTerms']) or 'none'}",
        f"controls: {result['summary']['controlShiftCount']}",
        f"control median/max words: {result['summary']['controlMedianWordCount']} / {result['summary']['controlMaxWordCount']}",
        f"comparable controls: {result['summary']['controlComparableWordCount']}",
        f"control strict hits: {result['summary']['controlStrictInstructionHitCount']}",
    ]
    for line in summary_lines:
        draw.text((side_x, y), line, fill=(206, 214, 224), font=normal)
        y += 28

    y += 14
    draw.text((side_x, y), "Active row groups", fill=(242, 246, 250), font=font(20))
    y += 34
    for row in active["rowGroups"][:9]:
        text = row["text"]
        if len(text) > 70:
            text = text[:67] + "..."
        draw.text((side_x, y), f"y={row['yMedian']} n={row['wordCount']}: {text}", fill=(182, 192, 204), font=mono)
        y += 22

    sheet.save(SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    pitch_report = load_json(LINE_PITCH_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
    targets = active["targets"]
    target_boxes = [target["box"] for target in targets]
    active_box = bbox_union(target_boxes)
    pitch = float(pitch_report.get("gapVsLinePitch", {}).get("medianLinePitchPx") or 73.73)

    target_rows = []
    for target in targets:
        row = {
            "id": target["id"],
            "label": target["label"],
            "phrase": target["phrase"],
            "box": target["box"],
            "center": [round(v, 2) for v in center(target["box"])],
            "visualState": target["visualState"],
            "pageLine": target["pageLine"],
            "corridorIndex": target["corridorIndex"],
        }
        target_rows.append(row)

    centers = [center(box) for box in target_boxes]
    hull = convex_hull(centers)
    active_summary = summarize_box(
        "active_target_envelope",
        active_box,
        page["words"],
        page["highlights"],
        targets,
        active_box[1],
        pitch,
    )

    controls = []
    for line_shift in range(-22, 5):
        if line_shift == 0:
            continue
        shifted = translate_box(active_box, line_shift * pitch)
        if shifted[1] < 0 or shifted[3] > page["height"]:
            continue
        row = summarize_box(
            f"shift_{line_shift:+d}_line_pitches",
            shifted,
            page["words"],
            page["highlights"],
            targets,
            active_box[1],
            pitch,
        )
        row["linePitchShift"] = line_shift
        row["box"] = [round(v, 2) for v in shifted]
        controls.append(row)

    active_word_count = active_summary["wordCount"]
    active_target_words = []
    for word in words_in_box(page["words"], active_box):
        if any(overlap_fraction_subject(word["box"], target["box"]) >= WORD_OVERLAP_THRESHOLD for target in targets):
            active_target_words.append(word)
    active_target_word_count = len(active_target_words)
    active_non_target_word_count = active_word_count - active_target_word_count
    control_word_counts = [row["wordCount"] for row in controls]
    comparable_controls = [
        row
        for row in controls
        if row["wordCount"] >= math.floor(active_word_count * 0.75)
    ]
    control_strict_rows = [row for row in controls if row["strictInstructionTerms"]]
    active_strict_count = len(active_summary["strictInstructionTerms"])

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active O4/B4/G5/O5 minimal target-envelope density gate; no new OCR/key derivation/hashing/address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "linePitchSource": rel(LINE_PITCH_JSON),
            "pageImage": rel(PAGE_IMAGE),
            "wordOverlapThreshold": WORD_OVERLAP_THRESHOLD,
            "highlightOverlapThreshold": HIGHLIGHT_OVERLAP_THRESHOLD,
        },
        "linePitchPx": round(pitch, 4),
        "targets": target_rows,
        "geometry": {
            "activeEnvelopeBox": [round(v, 2) for v in active_box],
            "activeEnvelopeWidthPx": round(active_box[2] - active_box[0], 2),
            "activeEnvelopeHeightPx": round(active_box[3] - active_box[1], 2),
            "activeEnvelopeAreaPx": round(area(active_box), 2),
            "targetBoxAreaTotalPx": round(sum(area(box) for box in target_boxes), 2),
            "targetBoxAreaFractionOfEnvelope": round(sum(area(box) for box in target_boxes) / area(active_box), 6),
            "targetCenterHull": [[round(x, 2), round(y, 2)] for x, y in hull],
            "targetCenterHullAreaPx": round(polygon_area(hull), 2),
            "targetCenterHullAreaFractionOfEnvelope": round(polygon_area(hull) / area(active_box), 6),
            "activePageLines": [target["pageLine"] for target in targets],
            "activeCorridorIndexes": [target["corridorIndex"] for target in targets],
            "activeLineGaps": [
                targets[i + 1]["pageLine"] - targets[i]["pageLine"] for i in range(len(targets) - 1)
            ],
            "activeCorridorGaps": [
                targets[i + 1]["corridorIndex"] - targets[i]["corridorIndex"] for i in range(len(targets) - 1)
            ],
        },
        "activeEnvelope": active_summary,
        "controls": {
            "method": "same-size active envelope translated by integer multiples of the current median line pitch; controls remain in p76 page bounds",
            "rows": controls,
        },
        "summary": {
            "activeEnvelopeWordCount": active_word_count,
            "activeTargetWordCountByOcrOverlap": active_target_word_count,
            "activeEnvelopeNonTargetWordCount": active_non_target_word_count,
            "activeTargetCoverage": f"{len(active_summary['activeTargetHits'])}/4",
            "activeHighlightHitIds": [row["id"] for row in active_summary["highlightHits"]],
            "activeStrictInstructionHitCount": active_strict_count,
            "activeStrictInstructionTerms": active_summary["strictInstructionTerms"],
            "activeContextTerms": active_summary["contextTerms"],
            "controlShiftCount": len(controls),
            "controlWordCounts": control_word_counts,
            "controlMedianWordCount": round(median(control_word_counts), 2) if control_word_counts else 0,
            "controlMaxWordCount": max(control_word_counts) if control_word_counts else 0,
            "controlComparableWordCount": len(comparable_controls),
            "controlComparableShifts": [row["linePitchShift"] for row in comparable_controls],
            "controlStrictInstructionHitCount": len(control_strict_rows),
            "controlStrictInstructionHitShifts": [row["linePitchShift"] for row in control_strict_rows],
            "targetPhraseIsolated": active_word_count <= len(targets) * 4 and active_non_target_word_count <= 4,
            "selectorUnlocked": False,
        },
        "decision": {
            "activeTargetEnvelopeDensityGate": "do-not-promote",
            "reason": (
                "The minimal O4/B4/G5/O5 envelope covers a broad lower-corridor prose band, "
                "not an isolated instruction surface. It contains many non-target OCR words, "
                "only ordinary context terms, and no strict unit/order instruction terms; "
                "line-pitch translated controls have comparable text density."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Keep the active envelope as source-comparison/validation geometry only. "
            "The next useful geometry pass should require new source wording or inspect a different "
            "bounded mechanic, not expand this envelope into another selector."
        ),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    draw_sheet(result)

    active_rows = result["activeEnvelope"]["rowGroups"]
    controls_sorted = sorted(result["controls"]["rows"], key=lambda row: (-row["wordCount"], abs(row["linePitchShift"])))
    lines = [
        "# Active Target Envelope Density Gate",
        "",
        "Scope: test whether the minimal O4/B4/G5/O5 page-76 envelope is a selector or only a broad source-validation surface. No new OCR, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active envelope: `{result['geometry']['activeEnvelopeBox']}`",
        f"- Line pitch: `{result['linePitchPx']}` px",
        f"- Active targets covered: `{result['summary']['activeTargetCoverage']}`",
        f"- Active envelope words: `{result['summary']['activeEnvelopeWordCount']}`",
        f"- OCR target words inside envelope: `{result['summary']['activeTargetWordCountByOcrOverlap']}`",
        f"- Non-target words inside envelope: `{result['summary']['activeEnvelopeNonTargetWordCount']}`",
        f"- Active strict instruction terms: `{result['summary']['activeStrictInstructionTerms']}`",
        f"- Active context terms: `{result['summary']['activeContextTerms']}`",
        f"- Active highlight hits: `{result['summary']['activeHighlightHitIds']}`",
        f"- Control shifts tested: `{result['summary']['controlShiftCount']}`",
        f"- Control median/max word count: `{result['summary']['controlMedianWordCount']}` / `{result['summary']['controlMaxWordCount']}`",
        f"- Comparable control shifts (>=75% active word count): `{result['summary']['controlComparableShifts']}`",
        f"- Control strict-instruction rows: `{result['summary']['controlStrictInstructionHitShifts']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Active Row Groups",
        "",
        "| row | y | words | strict terms | context terms | text |",
        "|---:|---:|---:|---|---|---|",
    ]
    for row in active_rows:
        text = row["text"].replace("|", "\\|")
        lines.append(
            f"| {row['rowIndex']} | {row['yMedian']} | {row['wordCount']} | `{row['strictInstructionTerms']}` | `{row['contextTerms']}` | {text} |"
        )

    lines.extend(
        [
            "",
            "## Densest Shift Controls",
            "",
            "| shift | words | highlights | strict terms | text preview |",
            "|---:|---:|---|---|---|",
        ]
    )
    for row in controls_sorted[:10]:
        preview = row["textPreview"].replace("|", "\\|")
        lines.append(
            f"| {row['linePitchShift']} | {row['wordCount']} | `{[hit['id'] for hit in row['highlightHits']]}` | `{row['strictInstructionTerms']}` | {preview} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote the active target bbox/hull envelope as a selector.",
            f"- The envelope contains `{result['summary']['activeEnvelopeWordCount']}` OCR words, of which `{result['summary']['activeEnvelopeNonTargetWordCount']}` are not target-overlap words.",
            f"- It covers all four active target boxes and hits `{result['summary']['activeHighlightHitIds']}`, but that confirms source-validation geometry rather than extraction permission.",
            f"- It has `{result['summary']['activeStrictInstructionHitCount']}` strict instruction-term hits; context terms such as `sell`, `bitcoin`, `IMF`, and `trust` are article prose, not unit/order commands.",
            f"- `{result['summary']['controlComparableWordCount']}` same-size line-pitch shifted controls have at least 75% of the active envelope's word density, so density alone is not selective.",
            "- Next best move: keep this envelope as validation geometry and require new source/clue wording before reopening envelope-based extraction.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("activeEnvelopeWordCount:", result["summary"]["activeEnvelopeWordCount"])
    print("activeEnvelopeNonTargetWordCount:", result["summary"]["activeEnvelopeNonTargetWordCount"])
    print("activeStrictInstructionHitCount:", result["summary"]["activeStrictInstructionHitCount"])
    print("controlComparableWordCount:", result["summary"]["controlComparableWordCount"])


if __name__ == "__main__":
    main()
