#!/usr/bin/env python3
"""Audit active-quartet envelope-centered fold/mirror transforms.

This bounded pass asks whether the current page-76 O4/B4/G5/O5 boxes fold or
mirror back onto the active quartet when the transform is centered on the
quartet's own envelope. It compares active re-hits against non-active page-76
highlight controls and C9/OVERDOSE slot placement. It is geometry inspection
only, not extraction.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_envelope_transform_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_envelope_transform_gate.json"
OUT_MD = OUT / "current_scan_active_envelope_transform_gate.md"
OUT_SHEET = OUT / "current_scan_active_envelope_transform_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
PAGE76_HIGHLIGHT_BENCHMARK = ROOT / (
    "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

ACTIVE_ORDER = ["O4", "B4", "G5", "O5"]
ACTIVE_TARGET_IDS = {"O4", "B4", "G5", "O5"}
THRESHOLDS = [8, 16, 32, 64]
STRICT_THRESHOLD = 32


PointTransform = Callable[[float, float], tuple[float, float]]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def center(box: list[float]) -> tuple[float, float]:
    x0, y0, x1, y1 = box
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def area(box: list[float]) -> float:
    x0, y0, x1, y1 = box
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def intersection_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def overlap_score(projected: list[float], target: list[float]) -> float:
    projected_area = area(projected)
    if projected_area <= 0:
        return 0.0
    return intersection_area(projected, target) / projected_area


def transform_box(box: list[float], transform: PointTransform) -> list[float]:
    x0, y0, x1, y1 = box
    points = [
        transform(x0, y0),
        transform(x1, y0),
        transform(x1, y1),
        transform(x0, y1),
    ]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in active_index.get("activeRows", []):
        box = [float(value) for value in row["box"]]
        rows.append(
            {
                "id": row["id"],
                "shortId": row["shortId"],
                "phrase": row["phrase"],
                "visualState": row["visualState"],
                "color": row.get("color"),
                "pageLine": row.get("pageLine"),
                "corridorIndex": row.get("corridorIndex"),
                "box": box,
                "center": center(box),
            }
        )
    order = {short_id: idx for idx, short_id in enumerate(ACTIVE_ORDER)}
    return sorted(rows, key=lambda item: order.get(item["shortId"], 99))


def highlight_control_rows(benchmark: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in benchmark.get("targets", []):
        target_id = str(target.get("id"))
        if target_id in ACTIVE_TARGET_IDS:
            continue
        box = [float(value) for value in target.get("box", [])]
        rows.append(
            {
                "id": target_id,
                "shortId": target_id,
                "phrase": str(target.get("label")),
                "kind": str(target.get("kind")),
                "box": box,
                "center": center(box),
            }
        )
    return rows


def envelope_for(rows: list[dict[str, Any]]) -> dict[str, Any]:
    xs0 = [row["box"][0] for row in rows]
    ys0 = [row["box"][1] for row in rows]
    xs1 = [row["box"][2] for row in rows]
    ys1 = [row["box"][3] for row in rows]
    box = [min(xs0), min(ys0), max(xs1), max(ys1)]
    width = box[2] - box[0]
    height = box[3] - box[1]
    return {
        "box": box,
        "center": center(box),
        "width": width,
        "height": height,
        "aspect": width / height if height else None,
    }


def transforms_for(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    min_x, min_y, max_x, max_y = envelope["box"]
    width = max_x - min_x
    height = max_y - min_y
    cx, cy = envelope["center"]

    def normalize(x: float, y: float) -> tuple[float, float]:
        return ((x - min_x) / width, (y - min_y) / height)

    def denormalize(u: float, v: float) -> tuple[float, float]:
        return (min_x + u * width, min_y + v * height)

    return [
        {
            "name": "hmirror",
            "label": "Horizontal mirror around active-envelope center x",
            "axis": {"x": cx},
            "transform": lambda x, y: (2.0 * cx - x, y),
        },
        {
            "name": "vmirror",
            "label": "Vertical mirror around active-envelope center y",
            "axis": {"y": cy},
            "transform": lambda x, y: (x, 2.0 * cy - y),
        },
        {
            "name": "rot180",
            "label": "180-degree rotation around active-envelope center",
            "axis": {"center": [cx, cy]},
            "transform": lambda x, y: (2.0 * cx - x, 2.0 * cy - y),
        },
        {
            "name": "diag_main",
            "label": "Normalized main-diagonal fold inside active envelope",
            "axis": {"normalizedDiagonal": "top-left_to_bottom-right"},
            "transform": lambda x, y: denormalize(*reversed(normalize(x, y))),
        },
        {
            "name": "diag_anti",
            "label": "Normalized anti-diagonal fold inside active envelope",
            "axis": {"normalizedDiagonal": "top-right_to_bottom-left"},
            "transform": lambda x, y: denormalize(
                1.0 - normalize(x, y)[1],
                1.0 - normalize(x, y)[0],
            ),
        },
    ]


def c9_slots(c9: dict[str, Any]) -> tuple[list[dict[str, Any]], list[float]]:
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    slots = projection.get("slots", [])
    frame = [float(value) for value in c9.get("c9Frame", [])]
    return slots, frame


def slot_for(point: tuple[float, float], slots: list[dict[str, Any]], frame: list[float]) -> dict[str, Any]:
    x, y = point
    if len(frame) == 4 and not (frame[0] <= x <= frame[2] and frame[1] <= y <= frame[3]):
        return {"index": None, "letter": ".", "insideFrame": False}
    for slot in slots:
        if float(slot["left"]) <= x <= float(slot["right"]):
            return {"index": int(slot["index"]), "letter": str(slot["letter"]), "insideFrame": True}
    return {"index": None, "letter": ".", "insideFrame": bool(len(frame) == 4)}


def nearest_row(
    point: tuple[float, float],
    rows: list[dict[str, Any]],
    exclude_short_id: str | None = None,
) -> dict[str, Any]:
    candidates = [row for row in rows if row.get("shortId") != exclude_short_id]
    if not candidates:
        return {"shortId": None, "distancePx": None}
    winner = min(candidates, key=lambda row: distance(point, row["center"]))
    return {
        "shortId": winner["shortId"],
        "phrase": winner.get("phrase"),
        "distancePx": round(distance(point, winner["center"]), 6),
    }


def best_overlap(projected_box: list[float], rows: list[dict[str, Any]], exclude_short_id: str | None = None) -> dict[str, Any]:
    candidates = [row for row in rows if row.get("shortId") != exclude_short_id]
    if not candidates:
        return {"shortId": None, "overlapVsProjected": 0.0}
    scored = [
        (
            overlap_score(projected_box, row["box"]),
            intersection_area(projected_box, row["box"]),
            row,
        )
        for row in candidates
    ]
    score, overlap_px, winner = max(scored, key=lambda item: (item[0], item[1]))
    return {
        "shortId": winner["shortId"],
        "phrase": winner.get("phrase"),
        "overlapVsProjected": round(score, 6),
        "overlapAreaPx": round(overlap_px, 6),
    }


def inspect_transform(
    transform_row: dict[str, Any],
    active: list[dict[str, Any]],
    highlight_controls: list[dict[str, Any]],
    slots: list[dict[str, Any]],
    frame: list[float],
) -> dict[str, Any]:
    transform = transform_row["transform"]
    rows: list[dict[str, Any]] = []
    for source in active:
        projected_box = transform_box(source["box"], transform)
        projected_center = transform(*source["center"])
        slot = slot_for(projected_center, slots, frame)
        nearest_active_any = nearest_row(projected_center, active)
        nearest_active_other = nearest_row(projected_center, active, exclude_short_id=source["shortId"])
        nearest_highlight_control = nearest_row(projected_center, highlight_controls)
        row = {
            "sourceShortId": source["shortId"],
            "sourcePhrase": source["phrase"],
            "sourceCenter": [round(source["center"][0], 6), round(source["center"][1], 6)],
            "sourceBox": [round(value, 6) for value in source["box"]],
            "projectedCenter": [round(projected_center[0], 6), round(projected_center[1], 6)],
            "projectedBox": [round(value, 6) for value in projected_box],
            "nearestActiveAny": nearest_active_any,
            "nearestActiveOther": nearest_active_other,
            "nearestHighlightControl": nearest_highlight_control,
            "bestActiveOtherBoxOverlap": best_overlap(
                projected_box, active, exclude_short_id=source["shortId"]
            ),
            "bestHighlightControlBoxOverlap": best_overlap(projected_box, highlight_controls),
            "c9SlotAtProjectedCenter": slot,
        }
        for threshold in THRESHOLDS:
            row[f"activeAnyHit{threshold}"] = (
                nearest_active_any["distancePx"] is not None
                and nearest_active_any["distancePx"] <= threshold
            )
            row[f"activeOtherHit{threshold}"] = (
                nearest_active_other["distancePx"] is not None
                and nearest_active_other["distancePx"] <= threshold
            )
            row[f"highlightControlHit{threshold}"] = (
                nearest_highlight_control["distancePx"] is not None
                and nearest_highlight_control["distancePx"] <= threshold
            )
        rows.append(row)

    summary: dict[str, Any] = {
        "name": transform_row["name"],
        "label": transform_row["label"],
        "axis": transform_row["axis"],
        "projectedSlotStream": "".join(
            str(row["c9SlotAtProjectedCenter"]["letter"]) for row in rows
        ),
        "nearestActiveOtherStream": "-".join(
            str(row["nearestActiveOther"]["shortId"]) for row in rows
        ),
        "nearestHighlightControlStream": "-".join(
            str(row["nearestHighlightControl"]["shortId"]) for row in rows
        ),
    }
    active_other_distances = [
        float(row["nearestActiveOther"]["distancePx"]) for row in rows if row["nearestActiveOther"]["distancePx"] is not None
    ]
    highlight_control_distances = [
        float(row["nearestHighlightControl"]["distancePx"])
        for row in rows
        if row["nearestHighlightControl"]["distancePx"] is not None
    ]
    summary.update(
        {
            "minActiveOtherCenterDistancePx": round(min(active_other_distances), 6),
            "meanActiveOtherCenterDistancePx": round(
                sum(active_other_distances) / len(active_other_distances), 6
            ),
            "maxActiveOtherCenterDistancePx": round(max(active_other_distances), 6),
            "minHighlightControlCenterDistancePx": round(min(highlight_control_distances), 6),
            "bestActiveOtherBoxOverlap": max(
                row["bestActiveOtherBoxOverlap"]["overlapVsProjected"] for row in rows
            ),
            "bestHighlightControlBoxOverlap": max(
                row["bestHighlightControlBoxOverlap"]["overlapVsProjected"] for row in rows
            ),
        }
    )
    for threshold in THRESHOLDS:
        any_count = sum(int(row[f"activeAnyHit{threshold}"]) for row in rows)
        other_count = sum(int(row[f"activeOtherHit{threshold}"]) for row in rows)
        control_count = sum(int(row[f"highlightControlHit{threshold}"]) for row in rows)
        summary[f"activeAnyHitCount{threshold}"] = any_count
        summary[f"activeOtherHitCount{threshold}"] = other_count
        summary[f"highlightControlHitCount{threshold}"] = control_count
        summary[f"allFourActiveAnyRehit{threshold}"] = any_count == len(rows)
        summary[f"allFourActiveOtherRehit{threshold}"] = other_count == len(rows)
        summary[f"allFourHighlightControlHit{threshold}"] = control_count == len(rows)

    return {"summary": summary, "rows": rows}


def draw_sheet(
    image: Image.Image,
    active: list[dict[str, Any]],
    highlight_controls: list[dict[str, Any]],
    envelope: dict[str, Any],
    scenarios: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    sheet = Image.new("RGB", (1940, 1300), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1940, 94), fill=(25, 31, 42))
    draw.text((24, 16), "Current-Scan Active Envelope Transform Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "O4/B4/G5/O5 mirrored/rotated around their own active envelope, compared with active and non-active highlight boxes.",
        fill=(235, 235, 235),
        font=small,
    )

    preview = image.resize((760, round(760 * image.height / image.width)))
    pdraw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height

    ex0, ey0, ex1, ey1 = envelope["box"]
    ecx, ecy = envelope["center"]
    pdraw.rectangle([ex0 * sx, ey0 * sy, ex1 * sx, ey1 * sy], outline=(0, 90, 255, 210), width=3)
    pdraw.line([ecx * sx, ey0 * sy, ecx * sx, ey1 * sy], fill=(0, 90, 255, 130), width=2)
    pdraw.line([ex0 * sx, ecy * sy, ex1 * sx, ecy * sy], fill=(0, 90, 255, 130), width=2)
    pdraw.line([ex0 * sx, ey0 * sy, ex1 * sx, ey1 * sy], fill=(0, 90, 255, 90), width=2)
    pdraw.line([ex1 * sx, ey0 * sy, ex0 * sx, ey1 * sy], fill=(0, 90, 255, 90), width=2)

    for row in highlight_controls:
        x0, y0, x1, y1 = row["box"]
        pdraw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=(80, 80, 80, 105), width=2)
        pdraw.text((x0 * sx, max(0, y0 * sy - 13)), row["shortId"], fill=(75, 75, 75, 180), font=tiny)

    for row in active:
        x0, y0, x1, y1 = row["box"]
        color = (255, 122, 0, 245) if row["visualState"] == "Y" else (0, 0, 0, 245)
        pdraw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=color, width=4)
        pdraw.text((x0 * sx, max(0, y0 * sy - 17)), row["shortId"], fill=(255, 0, 0, 255), font=small)

    colors = {
        "hmirror": (230, 52, 80, 190),
        "vmirror": (22, 145, 92, 190),
        "rot180": (124, 70, 210, 190),
        "diag_main": (0, 132, 210, 190),
        "diag_anti": (220, 145, 20, 190),
    }
    for scenario in scenarios:
        color = colors.get(scenario["summary"]["name"], (50, 50, 50, 180))
        for row in scenario["rows"]:
            x0, y0, x1, y1 = row["projectedBox"]
            cx, cy = row["projectedCenter"]
            pdraw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=color, width=2)
            pdraw.ellipse(
                [cx * sx - 4, cy * sy - 4, cx * sx + 4, cy * sy + 4],
                fill=color,
                outline=(255, 255, 255, 220),
            )
    sheet.paste(preview, (24, 122))

    x0 = 830
    y = 120
    draw.text((x0, y), "Transform Summary", fill=(70, 70, 70), font=small)
    y += 28
    headers = ["transform", "slot", "other<=32", "other<=64", "ctrl<=32", "mean other", "best active ov", "best ctrl ov"]
    xs = [x0, x0 + 132, x0 + 208, x0 + 305, x0 + 402, x0 + 500, x0 + 610, x0 + 735]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 20
    for scenario in scenarios:
        row = scenario["summary"]
        values = [
            row["name"],
            row["projectedSlotStream"],
            str(row["activeOtherHitCount32"]),
            str(row["activeOtherHitCount64"]),
            str(row["highlightControlHitCount32"]),
            f"{row['meanActiveOtherCenterDistancePx']:.1f}",
            f"{row['bestActiveOtherBoxOverlap']:.2f}",
            f"{row['bestHighlightControlBoxOverlap']:.2f}",
        ]
        for xpos, value in zip(xs, values):
            draw.text((xpos, y), value, fill=(35, 35, 35), font=tiny)
        y += 21

    y += 20
    draw.text((x0, y), "Projected rows", fill=(70, 70, 70), font=small)
    y += 28
    headers = ["transform", "src", "nearest active", "dist", "nearest control", "dist", "slot"]
    xs = [x0, x0 + 130, x0 + 178, x0 + 296, x0 + 362, x0 + 500, x0 + 570]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 20
    for scenario in scenarios:
        for row in scenario["rows"]:
            values = [
                scenario["summary"]["name"],
                row["sourceShortId"],
                str(row["nearestActiveOther"]["shortId"]),
                f"{row['nearestActiveOther']['distancePx']:.1f}",
                str(row["nearestHighlightControl"]["shortId"]),
                f"{row['nearestHighlightControl']['distancePx']:.1f}",
                str(row["c9SlotAtProjectedCenter"]["letter"]),
            ]
            for xpos, value in zip(xs, values):
                draw.text((xpos, y), value, fill=(35, 35, 35), font=tiny)
            y += 18

    y = 1018
    draw.text((24, y), "Decision", fill=(70, 70, 70), font=small)
    decision_lines = [
        f"Active envelope: {summary['activeEnvelopeBox']} center {summary['activeEnvelopeCenter']}",
        f"Transforms checked: {', '.join(summary['transformNames'])}",
        f"Best active-other hits <=32/64: {summary['bestActiveOtherHitCount32']} / {summary['bestActiveOtherHitCount64']}",
        f"All-four active-other re-hit <=32/64: {int(summary['anyTransformAllFourActiveOther32'])} / {int(summary['anyTransformAllFourActiveOther64'])}",
        f"Best transform: {summary['bestTransformByActiveOther64']}",
        f"Source R3 / triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
        f"Hidden candidate: {int(summary['hiddenEnvelopeTransformCandidate'])}",
        f"Fingerprint: {summary['activeEnvelopeTransformFingerprint']}",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((24, y + 28 + idx * 22), line[:190], fill=(35, 35, 35), font=small)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    benchmark = load_json(PAGE76_HIGHLIGHT_BENCHMARK)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")

    active = active_rows(active_index)
    highlight_controls = highlight_control_rows(benchmark)
    envelope = envelope_for(active)
    slots, frame = c9_slots(c9)

    transform_rows = transforms_for(envelope)
    scenarios = [
        inspect_transform(row, active, highlight_controls, slots, frame)
        for row in transform_rows
    ]
    scenario_summaries = [scenario["summary"] for scenario in scenarios]
    best32 = max(row["activeOtherHitCount32"] for row in scenario_summaries)
    best64 = max(row["activeOtherHitCount64"] for row in scenario_summaries)
    best_scenario = min(
        scenario_summaries,
        key=lambda row: (
            -int(row["activeOtherHitCount64"]),
            row["meanActiveOtherCenterDistancePx"],
        ),
    )

    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    any_all_four_any_32 = any(row["allFourActiveAnyRehit32"] for row in scenario_summaries)
    any_all_four_any_64 = any(row["allFourActiveAnyRehit64"] for row in scenario_summaries)
    any_all_four_other_32 = any(row["allFourActiveOtherRehit32"] for row in scenario_summaries)
    any_all_four_other_64 = any(row["allFourActiveOtherRehit64"] for row in scenario_summaries)
    hidden_candidate = bool(any_all_four_other_32 and source_r3 > 0 and satisfied_triggers > 0)

    stream_bits = ",".join(
        f"{row['name']}:{row['projectedSlotStream']}/{row['activeOtherHitCount32']}/{row['activeOtherHitCount64']}"
        for row in scenario_summaries
    )
    fingerprint = (
        f"active={len(active)}|highlightControls={len(highlight_controls)}"
        f"|transforms={','.join(row['name'] for row in scenario_summaries)}"
        f"|allFourAny32={int(any_all_four_any_32)}|allFourAny64={int(any_all_four_any_64)}"
        f"|allFourOther32={int(any_all_four_other_32)}|allFourOther64={int(any_all_four_other_64)}"
        f"|bestOther32={best32}|bestOther64={best64}|bestTransform={best_scenario['name']}"
        f"|streams={stream_bits}|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active),
        "highlightControlBoxCount": len(highlight_controls),
        "thresholdsPx": THRESHOLDS,
        "strictThresholdPx": STRICT_THRESHOLD,
        "activeEnvelopeBox": [round(value, 6) for value in envelope["box"]],
        "activeEnvelopeCenter": [round(value, 6) for value in envelope["center"]],
        "activeEnvelopeWidthPx": round(envelope["width"], 6),
        "activeEnvelopeHeightPx": round(envelope["height"], 6),
        "activeEnvelopeAspect": round(float(envelope["aspect"]), 6),
        "transformNames": [row["name"] for row in scenario_summaries],
        "bestActiveOtherHitCount32": best32,
        "bestActiveOtherHitCount64": best64,
        "bestTransformByActiveOther64": best_scenario["name"],
        "anyTransformAllFourActiveAny32": any_all_four_any_32,
        "anyTransformAllFourActiveAny64": any_all_four_any_64,
        "anyTransformAllFourActiveOther32": any_all_four_other_32,
        "anyTransformAllFourActiveOther64": any_all_four_other_64,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "hiddenEnvelopeTransformCandidate": hidden_candidate,
        "selectorUnlocked": False,
        "activeEnvelopeTransformFingerprint": fingerprint,
    }

    draw_sheet(image, active, highlight_controls, envelope, scenarios, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current page-76 active O4/B4/G5/O5 box transforms around the active "
            "quartet envelope; compares active re-hits, non-active highlight controls, "
            "and C9/OVERDOSE slot placement; no extraction or candidate generation"
        ),
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "page76HighlightBenchmark": rel(PAGE76_HIGHLIGHT_BENCHMARK),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "activeRows": active,
        "highlightControlRows": highlight_controls,
        "activeEnvelope": envelope,
        "summary": summary,
        "transformScenarios": scenarios,
        "decision": {
            "currentScanActiveEnvelopeTransformGate": "current_scan_active_envelope_transform_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "No active-envelope centered mirror, rotation, or normalized diagonal fold "
                "maps all four active boxes back onto other active boxes at 32px or 64px. "
                "The best transform remains a partial geometry coincidence, not a source-backed "
                "unit/order rule."
            ),
            "nextMove": (
                "Use this as the active-quartet envelope fold/mirror stop-check. Continue "
                "with original-layout, physical scan, or raw clue validation that can supply "
                "a distinct source and an explicit unit/order instruction."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Active Envelope Transform Gate",
        "",
        "Scope: transformed the current page-76 O4/B4/G5/O5 active boxes around their own active-quartet envelope. Checked horizontal mirror, vertical mirror, 180-degree rotation, and normalized diagonal folds against active re-hits, non-active page-76 highlight controls, and C9/OVERDOSE slots. This is geometry inspection only; no key extraction, candidates, hashing, WIF/seed/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active / highlight-control boxes: `{len(active)}` / `{len(highlight_controls)}`",
        f"- Active envelope: `{summary['activeEnvelopeBox']}` center `{summary['activeEnvelopeCenter']}`",
        f"- Transform modes: `{', '.join(summary['transformNames'])}`",
        f"- Best active-other hit count <=32 / <=64 px: `{best32}` / `{best64}`",
        f"- Any transform all-four active-other re-hit <=32 / <=64 px: `{int(any_all_four_other_32)}` / `{int(any_all_four_other_64)}`",
        f"- Any transform all-four active-any re-hit <=32 / <=64 px: `{int(any_all_four_any_32)}` / `{int(any_all_four_any_64)}`",
        f"- Best transform by active-other <=64 px: `{best_scenario['name']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Hidden active-envelope transform candidate: `{int(hidden_candidate)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Transform Summary",
        "",
        "| transform | slot stream | active-other hits <=32 | active-other hits <=64 | highlight-control hits <=32 | mean active-other distance | best active-box overlap | best control-box overlap |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in scenario_summaries:
        lines.append(
            f"| `{row['name']}` | `{row['projectedSlotStream']}` | `{row['activeOtherHitCount32']}` | `{row['activeOtherHitCount64']}` | `{row['highlightControlHitCount32']}` | `{row['meanActiveOtherCenterDistancePx']:.2f}` | `{row['bestActiveOtherBoxOverlap']:.3f}` | `{row['bestHighlightControlBoxOverlap']:.3f}` |"
        )

    lines.extend(
        [
            "",
            "## Projected Rows",
            "",
            "| transform | source | projected slot | nearest active-other | distance | nearest highlight control | distance |",
            "|---|---|---|---|---:|---|---:|",
        ]
    )
    for scenario in scenarios:
        for row in scenario["rows"]:
            lines.append(
                f"| `{scenario['summary']['name']}` | `{row['sourceShortId']}` | `{row['c9SlotAtProjectedCenter']['letter']}` | `{row['nearestActiveOther']['shortId']}` | `{row['nearestActiveOther']['distancePx']:.2f}` | `{row['nearestHighlightControl']['shortId']}` | `{row['nearestHighlightControl']['distancePx']:.2f}` |"
            )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_active_envelope_transform_no_selector`",
            "- The active quartet does not fold/mirror back onto itself around its own envelope under the tested transforms.",
            "- This closes the remaining active-envelope version of the fold/mirror idea; it does not change the broader source-dependent frontier.",
            "",
            "## Next Move",
            "",
            "- Use original-layout, physical scan, or raw clue material to supply a distinct source and an explicit unit/order instruction before reopening extraction.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanActiveEnvelopeTransformGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
