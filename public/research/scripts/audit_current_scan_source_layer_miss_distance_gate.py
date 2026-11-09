#!/usr/bin/env python3
"""Audit held-to-light source-layer miss distances.

This bounded pass follows the source-layer landing gate. It asks whether B4 is
empty because page-75 source material narrowly misses the active box, or whether
the current scan geometry leaves B4 materially unsupported.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import math
import textwrap
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from audit_current_scan_source_layer_landing_gate import (
    ACTIVE_INDEX_SLOT,
    B4_SELF_SIGNAL,
    CONTENT_BOX_REGISTRATION,
    LAYER_ORDER,
    REOPEN_TRIGGER_MATRIX,
    ROOT,
    SOURCE_INK_LANDING,
    SOURCE_PAGE_TEMPLATE,
    SUPPORT_THRESHOLD,
    TARGET_ORDER,
    UPRIGHT_PAGE_TEMPLATE,
    WEAK_SUPPORT_THRESHOLD,
    active_boxes,
    build_control_boxes,
    content_box_modes,
    crop_bool,
    estimated_line_pitch,
    font,
    load_json,
    load_trigger_summary,
    normalize_page,
    rel,
    shifted_mirrored_source,
    source_layer_masks,
)


OUT_DIR = ROOT / "analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate"
JSON_OUT = OUT_DIR / "current_scan_source_layer_miss_distance_gate.json"
MD_OUT = OUT_DIR / "current_scan_source_layer_miss_distance_gate.md"
SHEET_OUT = OUT_DIR / "current_scan_source_layer_miss_distance_gate_sheet.jpg"

SOURCE_LAYER_LANDING = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_source_layer_landing_gate/"
    "current_scan_source_layer_landing_gate.json"
)

EXPANSION_RADII = [4, 8, 16, 32, 64, 128]
SEARCH_MARGIN_PX = 260
TINY_MISS_PX = 16


def clamp_int_box(box: list[float], shape: tuple[int, int]) -> list[int]:
    h, w = shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return [x0, y0, x1, y1]


def clipped_area(box: list[float], shape: tuple[int, int]) -> int:
    x0, y0, x1, y1 = clamp_int_box(box, shape)
    return max(0, x1 - x0) * max(0, y1 - y0)


def expanded_box(box: list[float], pad: int, shape: tuple[int, int]) -> list[int]:
    h, w = shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    return [
        max(0, x0 - pad),
        max(0, y0 - pad),
        min(w, x1 + pad),
        min(h, y1 + pad),
    ]


def side_for_point(x: int, y: int, box: list[int]) -> str:
    x0, y0, x1, y1 = box
    right = x1 - 1
    bottom = y1 - 1
    if x0 <= x <= right and y0 <= y <= bottom:
        return "inside"
    vertical = "top" if y < y0 else "bottom" if y > bottom else ""
    horizontal = "left" if x < x0 else "right" if x > right else ""
    if vertical and horizontal:
        return f"{vertical}_{horizontal}"
    return vertical or horizontal or "outside"


def nearest_source(mask: np.ndarray, box: list[float]) -> dict[str, Any]:
    h, w = mask.shape
    x0, y0, x1, y1 = clamp_int_box(box, mask.shape)
    region = mask[y0:y1, x0:x1]
    inside_count = int(region.sum())
    if inside_count:
        ys, xs = np.nonzero(region)
        px = int(xs[0] + x0)
        py = int(ys[0] + y0)
        return {
            "nearestDistancePx": 0.0,
            "minimalExpansionPx": 0,
            "nearestSide": "inside",
            "nearestSourcePoint": [px, py],
            "searchMarginPx": SEARCH_MARGIN_PX,
            "noSourcePixelsWithinSearch": False,
        }

    sx0 = max(0, x0 - SEARCH_MARGIN_PX)
    sx1 = min(w, x1 + SEARCH_MARGIN_PX)
    sy0 = max(0, y0 - SEARCH_MARGIN_PX)
    sy1 = min(h, y1 + SEARCH_MARGIN_PX)
    local = mask[sy0:sy1, sx0:sx1]
    ys, xs = np.nonzero(local)
    if len(xs) == 0:
        return {
            "nearestDistancePx": None,
            "minimalExpansionPx": None,
            "nearestSide": f">{SEARCH_MARGIN_PX}px",
            "nearestSourcePoint": None,
            "searchMarginPx": SEARCH_MARGIN_PX,
            "noSourcePixelsWithinSearch": True,
        }

    abs_x = xs.astype(np.int32) + sx0
    abs_y = ys.astype(np.int32) + sy0
    dx = np.maximum(np.maximum(x0 - abs_x, abs_x - (x1 - 1)), 0)
    dy = np.maximum(np.maximum(y0 - abs_y, abs_y - (y1 - 1)), 0)
    dist2 = dx.astype(np.float64) ** 2 + dy.astype(np.float64) ** 2
    idx = int(np.argmin(dist2))
    distance = float(math.sqrt(float(dist2[idx])))
    px = int(abs_x[idx])
    py = int(abs_y[idx])
    return {
        "nearestDistancePx": round(distance, 3),
        "minimalExpansionPx": int(math.ceil(distance)),
        "nearestSide": side_for_point(px, py, [x0, y0, x1, y1]),
        "nearestSourcePoint": [px, py],
        "searchMarginPx": SEARCH_MARGIN_PX,
        "noSourcePixelsWithinSearch": False,
    }


def expansion_rows(mask: np.ndarray, box: list[float], inside_count: int) -> list[dict[str, Any]]:
    rows = []
    original_area = clipped_area(box, mask.shape)
    for pad in EXPANSION_RADII:
        x0, y0, x1, y1 = expanded_box(box, pad, mask.shape)
        expanded = mask[y0:y1, x0:x1]
        expanded_count = int(expanded.sum())
        expanded_area = max(0, x1 - x0) * max(0, y1 - y0)
        ring_area = max(0, expanded_area - original_area)
        ring_count = max(0, expanded_count - inside_count)
        rows.append(
            {
                "radiusPx": pad,
                "ringPixelCount": ring_count,
                "ringArea": ring_area,
                "ringRatio": round(ring_count / ring_area, 6) if ring_area else 0.0,
                "expandedPixelCount": expanded_count,
            }
        )
    return rows


def measure_box_distance(mask: np.ndarray, box: list[float]) -> dict[str, Any]:
    region = crop_bool(mask, box)
    pixel_count = int(region.size)
    inside_count = int(region.sum())
    ratio = inside_count / pixel_count if pixel_count else 0.0
    nearest = nearest_source(mask, box)
    rings = expansion_rows(mask, box, inside_count)
    first_expansion = 0 if inside_count else None
    if first_expansion is None:
        for row in rings:
            if row["ringPixelCount"] > 0:
                first_expansion = row["radiusPx"]
                break
    minimal = nearest["minimalExpansionPx"]
    return {
        "pixelCount": pixel_count,
        "layerPixelCount": inside_count,
        "layerRatio": round(ratio, 6),
        "weakSupported": ratio >= WEAK_SUPPORT_THRESHOLD,
        "sourceSupported": ratio >= SUPPORT_THRESHOLD,
        **nearest,
        "firstExpansionWithPixelsPx": first_expansion,
        "withinExpansionPx": {
            str(radius): bool(minimal is not None and minimal <= radius)
            for radius in EXPANSION_RADII
        },
        "expansionRings": rings,
    }


def layer_summary(active_rows: list[dict[str, Any]], mode_id: str, layer: str) -> dict[str, Any]:
    rows = [row for row in active_rows if row["layer"] == layer]
    by_target = {row["target"]: row for row in rows}
    inside_targets = [row["target"] for row in rows if row["layerPixelCount"] > 0]
    supported_targets = [row["target"] for row in rows if row["sourceSupported"]]
    weak_targets = [row["target"] for row in rows if row["weakSupported"]]
    within_counts = {
        str(radius): sum(1 for row in rows if row["withinExpansionPx"][str(radius)])
        for radius in EXPANSION_RADII
    }
    all_four_within = {key: count == 4 for key, count in within_counts.items()}
    expansions = [row["minimalExpansionPx"] for row in rows]
    all_four_max = None if any(value is None for value in expansions) else max(expansions)
    b4 = by_target["B4"]
    return {
        "modeId": mode_id,
        "layer": layer,
        "insideTargets": inside_targets,
        "insideCount": len(inside_targets),
        "supportedTargets": supported_targets,
        "weakSupportedTargets": weak_targets,
        "supportedCount": len(supported_targets),
        "weakSupportedCount": len(weak_targets),
        "allFourInside": len(inside_targets) == 4,
        "withinExpansionCounts": within_counts,
        "allFourWithinExpansionPx": all_four_within,
        "allFourMaxExpansionPx": all_four_max,
        "b4NearestDistancePx": b4["nearestDistancePx"],
        "b4MinimalExpansionPx": b4["minimalExpansionPx"],
        "b4FirstExpansionWithPixelsPx": b4["firstExpansionWithPixelsPx"],
        "b4NearestSide": b4["nearestSide"],
        "b4NoSourcePixelsWithinSearch": b4["noSourcePixelsWithinSearch"],
    }


def mode_rows(
    source_page: Image.Image,
    active: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    mode_id: str,
    dx: float,
    dy: float,
) -> dict[str, Any]:
    landing = shifted_mirrored_source(source_page, dx, dy)
    arr = np.asarray(landing.convert("RGB"))
    masks = source_layer_masks(arr)
    active_rows = []
    control_rows = []
    for layer in LAYER_ORDER:
        mask = masks[layer]
        for row in active:
            active_rows.append(
                {
                    "modeId": mode_id,
                    "layer": layer,
                    "target": row["shortId"],
                    "phrase": row["phrase"],
                    "visualState": row["visualState"],
                    **measure_box_distance(mask, row["box"]),
                }
            )
        for control in controls:
            control_rows.append(
                {
                    "modeId": mode_id,
                    "layer": layer,
                    "id": control["id"],
                    "sourceTarget": control["sourceTarget"],
                    "lineOffset": control["lineOffset"],
                    **measure_box_distance(mask, control["box"]),
                }
            )
    return {
        "modeId": mode_id,
        "dx": round(float(dx), 3),
        "dy": round(float(dy), 3),
        "activeRows": active_rows,
        "controlRows": control_rows,
        "layerSummaries": [layer_summary(active_rows, mode_id, layer) for layer in LAYER_ORDER],
        "landingImage": landing,
    }


def control_distance_summary(control_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for layer in LAYER_ORDER:
        for target in TARGET_ORDER:
            rows = [row for row in control_rows if row["layer"] == layer and row["sourceTarget"] == target]
            values = [row["minimalExpansionPx"] for row in rows if row["minimalExpansionPx"] is not None]
            summaries.append(
                {
                    "layer": layer,
                    "sourceTarget": target,
                    "controlRowCount": len(rows),
                    "knownDistanceCount": len(values),
                    "minMinimalExpansionPx": min(values) if values else None,
                    "medianMinimalExpansionPx": round(float(median(values)), 3) if values else None,
                    "within16Count": sum(1 for value in values if value <= TINY_MISS_PX),
                }
            )
    return summaries


def distance_token(value: int | float | None) -> str:
    if value is None:
        return f">{SEARCH_MARGIN_PX}"
    if isinstance(value, int):
        return str(value)
    return f"{value:.1f}"


def best_b4_layer(summaries: list[dict[str, Any]], layer_filter: str | None = None) -> dict[str, Any] | None:
    candidates = [
        row
        for row in summaries
        if (layer_filter is None or row["layer"] == layer_filter)
        and row["b4MinimalExpansionPx"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: (row["b4MinimalExpansionPx"], LAYER_ORDER.index(row["layer"])))


def best_all_four_layer(summaries: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [row for row in summaries if row["allFourMaxExpansionPx"] is not None]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda row: (
            row["allFourMaxExpansionPx"],
            -row["insideCount"],
            LAYER_ORDER.index(row["layer"]),
        ),
    )


def preview_panel(result: dict[str, Any], active: list[dict[str, Any]]) -> Image.Image:
    bbox = [
        min(row["box"][0] for row in active) - 160,
        min(row["box"][1] for row in active) - 160,
        max(row["box"][2] for row in active) + 160,
        max(row["box"][3] for row in active) + 160,
    ]
    crop = result["landingImage"].crop([int(round(v)) for v in bbox]).convert("RGB")
    draw = ImageDraw.Draw(crop, "RGBA")
    for row in active:
        box = [
            row["box"][0] - bbox[0],
            row["box"][1] - bbox[1],
            row["box"][2] - bbox[0],
            row["box"][3] - bbox[1],
        ]
        draw.rectangle(box, outline=(255, 70, 0, 255), width=4)
        draw.text((box[0], max(0, box[1] - 24)), row["shortId"], fill=(220, 20, 20, 255), font=font(20, True))
    colors = {"feature": (0, 112, 243, 255), "broad": (16, 185, 129, 255)}
    for layer, color in colors.items():
        b4_row = next(row for row in result["activeRows"] if row["layer"] == layer and row["target"] == "B4")
        point = b4_row["nearestSourcePoint"]
        if point:
            px = point[0] - bbox[0]
            py = point[1] - bbox[1]
            draw.ellipse((px - 9, py - 9, px + 9, py + 9), outline=color, width=5)
            draw.line((px, py, px + 45, py - 34), fill=color, width=4)
            draw.text(
                (px + 50, py - 46),
                f"{layer} {distance_token(b4_row['minimalExpansionPx'])}px",
                fill=color,
                font=font(18, True),
            )
    crop.thumbnail((490, 370))
    panel = Image.new("RGB", (540, 450), "white")
    panel.paste(crop, (24, 58))
    d = ImageDraw.Draw(panel)
    d.text((22, 16), f"{result['modeId']} dx={result['dx']}, dy={result['dy']}", fill=(15, 23, 42), font=font(18, True))
    return panel


def draw_sheet(mode_results: list[dict[str, Any]], active: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (2100, 1500), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title = font(34, True)
    header = font(22, True)
    body = font(19)
    small = font(15)
    draw.text((36, 26), "Current Scan Source-Layer Miss-Distance Gate", fill=(15, 23, 42), font=title)
    y = 84
    for line in [
        f"Decision: {summary['decision']}",
        f"B4 min expansion any/feature/broad: {distance_token(summary['b4MinExpansionAnyPx'])} / {distance_token(summary['b4MinExpansionFeaturePx'])} / {distance_token(summary['b4MinExpansionBroadPx'])} px",
        f"B4 tiny miss candidate <=16px: {int(summary['b4TinyMissCandidate'])} | all-four within 16px layer/modes: {summary['allFourWithinExpansionLayerModeCounts']['16']}",
        f"Best all-four expansion layer/mode: {summary['bestAllFourExpansionLayerMode']}",
    ]:
        draw.text((36, y), line, fill=(30, 41, 59), font=body)
        y += 30

    x = 36
    y = 215
    for result in mode_results:
        sheet.paste(preview_panel(result, active), (x, y))
        x += 565

    y = 720
    draw.text((36, y), "Nearest Expansion Needed by Mode and Layer", fill=(15, 23, 42), font=header)
    y += 34
    cols = [36, 300, 410, 525, 640, 755, 870, 990, 1110, 1235, 1360, 1485]
    labels = ["mode", "layer", "O4", "B4", "G5", "O5", "<=8", "<=16", "<=32", "<=64", "all4max", "B4 side"]
    for cx, label in zip(cols, labels):
        draw.text((cx, y), label, fill=(51, 65, 85), font=small)
    y += 24
    for result in mode_results:
        for layer in LAYER_ORDER:
            rows = [row for row in result["activeRows"] if row["layer"] == layer]
            by_target = {row["target"]: row for row in rows}
            layer_row = next(row for row in result["layerSummaries"] if row["layer"] == layer)
            vals = [
                result["modeId"].replace("_content_box_translation", "_content"),
                layer,
                distance_token(by_target["O4"]["minimalExpansionPx"]),
                distance_token(by_target["B4"]["minimalExpansionPx"]),
                distance_token(by_target["G5"]["minimalExpansionPx"]),
                distance_token(by_target["O5"]["minimalExpansionPx"]),
                str(layer_row["withinExpansionCounts"]["8"]),
                str(layer_row["withinExpansionCounts"]["16"]),
                str(layer_row["withinExpansionCounts"]["32"]),
                str(layer_row["withinExpansionCounts"]["64"]),
                distance_token(layer_row["allFourMaxExpansionPx"]),
                str(layer_row["b4NearestSide"])[:15],
            ]
            for cx, val in zip(cols, vals):
                draw.text((cx, y), str(val)[:28], fill=(30, 41, 59), font=small)
            y += 23
        y += 8

    x0 = 1535
    y = 720
    draw.text((x0, y), "Interpretation", fill=(15, 23, 42), font=header)
    y += 36
    notes = [
        "This pass measures distance to source material after B4 showed zero in-box pixels.",
        "A <=16px B4 distance would imply a tiny crop/threshold miss to review.",
        "A larger or missing distance keeps the current scan held-to-light path closed.",
        "All-four expansion counts guard against rescuing B4 by making every box too loose.",
    ]
    for note in notes:
        wrapped = textwrap.wrap(note, width=48)
        for idx, line in enumerate(wrapped):
            prefix = "- " if idx == 0 else "  "
            draw.text((x0 + 8, y), prefix + line, fill=(30, 41, 59), font=body)
            y += 28
        y += 4
    sheet.save(SHEET_OUT, quality=92)


def serializable_mode_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "modeId": result["modeId"],
        "dx": result["dx"],
        "dy": result["dy"],
        "activeRows": result["activeRows"],
        "controlRows": result["controlRows"],
        "controlDistanceSummaries": control_distance_summary(result["controlRows"]),
        "layerSummaries": result["layerSummaries"],
    }


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Source-Layer Miss-Distance Gate",
        "",
        "Scope: measured how far mirrored page-75 source-layer pixels sit from page-76 O4/B4/G5/O5 active boxes under natural, all-content, and lower-half content-box registration. This is source/geometry validation only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Modes checked: `{summary['modeCount']}`",
        f"- Layers checked: `{summary['layersChecked']}`",
        f"- Active distance rows: `{summary['activeDistanceRowCount']}`",
        f"- Control distance rows: `{summary['controlDistanceRowCount']}`",
        f"- B4 min expansion any / feature / broad: `{distance_token(summary['b4MinExpansionAnyPx'])}` / `{distance_token(summary['b4MinExpansionFeaturePx'])}` / `{distance_token(summary['b4MinExpansionBroadPx'])}` px",
        f"- B4 tiny miss candidate <= `{TINY_MISS_PX}` px: `{int(summary['b4TinyMissCandidate'])}`",
        f"- All-four within expansion layer/modes: `{summary['allFourWithinExpansionLayerModeCounts']}`",
        f"- Best all-four expansion layer/mode: `{summary['bestAllFourExpansionLayerMode']}`",
        f"- Hidden miss-distance candidate: `{int(summary['hiddenMissDistanceCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['sourceLayerMissDistanceFingerprint']}`",
        "",
        "## Distance Rows",
        "",
        "| mode | layer | O4 px | B4 px | G5 px | O5 px | <=8 | <=16 | <=32 | <=64 | all-four max px | B4 side |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for mode in result["modeResults"]:
        for layer in LAYER_ORDER:
            rows = [row for row in mode["activeRows"] if row["layer"] == layer]
            by_target = {row["target"]: row for row in rows}
            layer_row = next(row for row in mode["layerSummaries"] if row["layer"] == layer)
            lines.append(
                f"| `{mode['modeId']}` | `{layer}` | "
                f"`{distance_token(by_target['O4']['minimalExpansionPx'])}` | "
                f"`{distance_token(by_target['B4']['minimalExpansionPx'])}` | "
                f"`{distance_token(by_target['G5']['minimalExpansionPx'])}` | "
                f"`{distance_token(by_target['O5']['minimalExpansionPx'])}` | "
                f"`{layer_row['withinExpansionCounts']['8']}/4` | "
                f"`{layer_row['withinExpansionCounts']['16']}/4` | "
                f"`{layer_row['withinExpansionCounts']['32']}/4` | "
                f"`{layer_row['withinExpansionCounts']['64']}/4` | "
                f"`{distance_token(layer_row['allFourMaxExpansionPx'])}` | "
                f"`{layer_row['b4NearestSide']}` |"
            )
    if summary["b4TinyMissCandidate"]:
        decision_note = (
            f"B4 has at least one source layer within {TINY_MISS_PX}px, but this still does not unlock a selector "
            "unless the same layer/mode cleanly supports the active quartet and a source-backed rule names the expansion."
        )
    else:
        decision_note = (
            f"B4 has no source layer within the {TINY_MISS_PX}px tiny-miss band under the tested registrations, "
            "so the zero B4 landing is not a small crop or threshold miss."
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{summary['decision']}`",
            f"- {decision_note}",
            "- All-four small-expansion support remains absent at the selector thresholds, and source-backed R3 remains 0.",
            "",
            "## Next Move",
            "",
            "- Keep current-scan held-to-light closed except as source-review evidence. Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    active = active_boxes(active_index)
    source_page = normalize_page(75)
    controls = build_control_boxes(active, source_page.size, estimated_line_pitch(active))
    modes = content_box_modes()
    mode_results = [
        mode_rows(source_page, active, controls, mode["modeId"], mode["dx"], mode["dy"])
        for mode in modes
    ]
    all_summaries = [row for mode in mode_results for row in mode["layerSummaries"]]
    all_active_rows = [row for mode in mode_results for row in mode["activeRows"]]
    all_control_rows = [row for mode in mode_results for row in mode["controlRows"]]
    best_any = best_b4_layer(all_summaries)
    best_feature = best_b4_layer(all_summaries, "feature")
    best_broad = best_b4_layer(all_summaries, "broad")
    best_all_four = best_all_four_layer(all_summaries)
    within_counts = {
        str(radius): sum(1 for row in all_summaries if row["allFourWithinExpansionPx"][str(radius)])
        for radius in EXPANSION_RADII
    }
    trigger = load_trigger_summary()
    b4_min_any = best_any["b4MinimalExpansionPx"] if best_any else None
    b4_min_feature = best_feature["b4MinimalExpansionPx"] if best_feature else None
    b4_min_broad = best_broad["b4MinimalExpansionPx"] if best_broad else None
    b4_tiny = bool(b4_min_any is not None and b4_min_any <= TINY_MISS_PX)
    all_four_tiny = within_counts[str(TINY_MISS_PX)] > 0
    hidden_candidate = bool(b4_tiny and all_four_tiny and trigger["sourceBackedR3BridgeHitCount"] > 0)
    decision = (
        "current_scan_source_layer_miss_distance_tiny_b4_but_no_selector"
        if b4_tiny
        else "current_scan_source_layer_miss_distance_no_tiny_miss"
    )
    best_all_four_label = (
        f"{best_all_four['modeId']}:{best_all_four['layer']}:{best_all_four['allFourMaxExpansionPx']}px"
        if best_all_four
        else f">{SEARCH_MARGIN_PX}px"
    )
    b4_tokens = ",".join(
        f"{row['modeId']}:{row['layer']}:{distance_token(row['b4MinimalExpansionPx'])}"
        for row in all_summaries
    )
    fingerprint = (
        f"modes={len(modes)}|layers={','.join(LAYER_ORDER)}"
        f"|rows={len(all_active_rows)}|controls={len(all_control_rows)}"
        f"|b4MinAny={distance_token(b4_min_any)}|b4MinFeature={distance_token(b4_min_feature)}"
        f"|b4MinBroad={distance_token(b4_min_broad)}|b4Tiny={int(b4_tiny)}"
        f"|allFourWithin16={within_counts[str(TINY_MISS_PX)]}"
        f"|bestAllFour={best_all_four_label}|b4={b4_tokens}"
        f"|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger['satisfiedReopenTriggerCount']}/{trigger['triggerCount']}"
        "|selectors=0"
    )
    summary = {
        "decision": decision,
        "modeCount": len(modes),
        "layersChecked": LAYER_ORDER,
        "activeDistanceRowCount": len(all_active_rows),
        "controlDistanceRowCount": len(all_control_rows),
        "b4MinExpansionAnyPx": b4_min_any,
        "b4MinExpansionFeaturePx": b4_min_feature,
        "b4MinExpansionBroadPx": b4_min_broad,
        "b4BestLayerMode": f"{best_any['modeId']}:{best_any['layer']}" if best_any else None,
        "b4BestSide": best_any["b4NearestSide"] if best_any else f">{SEARCH_MARGIN_PX}px",
        "b4TinyMissCandidate": b4_tiny,
        "allFourWithinExpansionLayerModeCounts": within_counts,
        "bestAllFourExpansionLayerMode": best_all_four_label,
        "hiddenMissDistanceCandidate": hidden_candidate,
        "priorContentBoxRegistrationFingerprint": load_json(CONTENT_BOX_REGISTRATION)
        .get("summary", {})
        .get("contentBoxRegistrationFingerprint"),
        "priorSourceInkLandingFingerprint": load_json(SOURCE_INK_LANDING)
        .get("summary", {})
        .get("sourceInkLandingFingerprint"),
        "priorSourceLayerLandingFingerprint": load_json(SOURCE_LAYER_LANDING)
        .get("summary", {})
        .get("sourceLayerLandingFingerprint"),
        "priorB4SelfSignalFingerprint": load_json(B4_SELF_SIGNAL).get("fingerprint"),
        "sourceBackedR3BridgeHitCount": trigger["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger["satisfiedReopenTriggerCount"],
        "triggerCount": trigger["triggerCount"],
        "sourceLayerMissDistanceFingerprint": fingerprint,
    }

    draw_sheet(mode_results, active, summary)
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current scan held-to-light source-layer miss-distance audit; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "contentBoxRegistrationGate": rel(CONTENT_BOX_REGISTRATION),
            "sourceInkLandingGate": rel(SOURCE_INK_LANDING),
            "sourceLayerLandingGate": rel(SOURCE_LAYER_LANDING),
            "b4SelfSignalGuardrail": rel(B4_SELF_SIGNAL),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage75": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))),
            "uprightPage75": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=75))),
        },
        "modes": modes,
        "targetOrder": TARGET_ORDER,
        "layerOrder": LAYER_ORDER,
        "expansionRadiiPx": EXPANSION_RADII,
        "searchMarginPx": SEARCH_MARGIN_PX,
        "tinyMissPx": TINY_MISS_PX,
        "modeResults": [serializable_mode_result(row) for row in mode_results],
        "summary": summary,
        "decision": {
            "currentScanSourceLayerMissDistanceGate": summary["decision"],
            "selectorUnlocked": False,
            "reason": (
                "The pass measures the minimum source-layer expansion needed after B4 showed zero in-box "
                "source pixels. It does not supply a source-backed extraction rule."
            ),
            "nextMove": (
                "Do not reopen current-scan held-to-light unless a distinct physical/original-layout source "
                "or raw clue supplies a new registration rule."
            ),
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": fingerprint,
    }
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(MD_OUT)}")
    print(f"Wrote {rel(JSON_OUT)}")
    print(f"Wrote {rel(SHEET_OUT)}")
    print(f"Decision: {summary['decision']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
