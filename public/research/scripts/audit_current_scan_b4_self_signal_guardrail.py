#!/usr/bin/env python3
"""Separate valid-leaf source ink from page-76 self-signal at B4.

The previous held-to-light blend pass showed an all-four visual pop under an
average blend, while the valid-leaf source-ink landing pass showed B4 has zero
source ink. This bounded pass explains that conflict by decomposing the
average-blend delta into source-supported pixels versus target-only pixels.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_b4_self_signal_guardrail.json"
OUT_MD = OUT / "current_scan_b4_self_signal_guardrail.md"
OUT_SHEET = OUT / "current_scan_b4_self_signal_guardrail_sheet.jpg"
OUT_OVERLAY = OUT / "b4_self_signal_delta_overlay.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
SOURCE_INK_LANDING = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/"
    "current_scan_valid_leaf_source_ink_landing_gate.json"
)
LIGHT_TABLE_BLEND_MODE = ROOT / (
    "analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/"
    "current_scan_light_table_blend_mode_gate.json"
)
JITTER_RESCUE = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/"
    "current_scan_valid_leaf_jitter_source_ink_rescue_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]
SOURCE_INK_LUMA_THRESHOLD = 238.0
TARGET_INK_LUMA_THRESHOLD = 238.0
AVERAGE_ALPHA = 0.70


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def normalize_page(page: int) -> Image.Image:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    if source_path.exists():
        source = Image.open(source_path).convert("RGB")
        upright = Image.open(upright_path).convert("RGB")
        sample_size = (318, 408)
        source_sample = source.resize(sample_size)
        upright_sample = upright.resize(sample_size)
        same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
        rot_diff = sum(
            ImageStat.Stat(
                ImageChops.difference(source_sample.rotate(180), upright_sample)
            ).mean
        )
        return source.rotate(180) if rot_diff < same_diff else source
    return Image.open(upright_path).convert("RGB")


def shifted_mirrored_source(page: Image.Image, dx: int, dy: int) -> Image.Image:
    mirrored = ImageOps.mirror(page)
    canvas = Image.new("RGB", page.size, "white")
    canvas.paste(mirrored, (dx, dy))
    return canvas


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def crop_arr(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return arr[y0:y1, x0:x1, :]


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def box_area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def iou(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    inter = box_area([x0, y0, x1, y1])
    union = box_area(a) + box_area(b) - inter
    return inter / union if union else 0.0


def shifted_box(box: list[float], dy: float, page_size: tuple[int, int]) -> list[float] | None:
    w, h = page_size
    shifted = [box[0], box[1] + dy, box[2], box[3] + dy]
    if shifted[0] < 0 or shifted[1] < 0 or shifted[2] > w or shifted[3] > h:
        return None
    return shifted


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") in TARGET_ORDER:
            rows.append(
                {
                    "id": row["id"],
                    "shortId": row["shortId"],
                    "phrase": row["phrase"],
                    "visualState": row["visualState"],
                    "pageLine": int(row["pageLine"]),
                    "box": [float(v) for v in row["box"]],
                }
            )
    rows.sort(key=lambda item: TARGET_ORDER.index(item["shortId"]))
    return rows


def estimated_line_pitch(rows: list[dict[str, Any]]) -> float:
    pitches: list[float] = []
    for i, left in enumerate(rows):
        for right in rows[i + 1 :]:
            line_gap = right["pageLine"] - left["pageLine"]
            if line_gap:
                cy_left = (left["box"][1] + left["box"][3]) / 2
                cy_right = (right["box"][1] + right["box"][3]) / 2
                pitches.append((cy_right - cy_left) / line_gap)
    return float(median(pitches)) if pitches else 73.5


def build_control_boxes(
    rows: list[dict[str, Any]],
    page_size: tuple[int, int],
    line_pitch: float,
) -> list[dict[str, Any]]:
    active_bounds = [row["box"] for row in rows]
    controls: list[dict[str, Any]] = []
    for row in rows:
        for offset in CONTROL_LINE_OFFSETS:
            box = shifted_box(row["box"], offset * line_pitch, page_size)
            if box is None:
                continue
            if any(iou(box, active_box) > 0.08 for active_box in active_bounds):
                continue
            controls.append(
                {
                    "id": f"{row['shortId']}_line_{offset:+d}",
                    "sourceTarget": row["shortId"],
                    "lineOffset": offset,
                    "box": box,
                }
            )
    return controls


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    lo = int(np.floor(rank))
    hi = int(np.ceil(rank))
    if lo == hi:
        return float(ordered[lo])
    frac = rank - lo
    return float(ordered[lo] * (1 - frac) + ordered[hi] * frac)


def average_blend(target_arr: np.ndarray, source_arr: np.ndarray) -> np.ndarray:
    t = target_arr.astype(np.float32)
    s = source_arr.astype(np.float32)
    return np.clip((1.0 - AVERAGE_ALPHA) * t + AVERAGE_ALPHA * s, 0, 255).astype(np.uint8)


def measure_region(
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    blend_arr: np.ndarray,
    box: list[float],
) -> dict[str, float]:
    target_crop = crop_arr(target_arr, box)
    source_crop = crop_arr(source_arr, box)
    blend_crop = crop_arr(blend_arr, box)
    if target_crop.size == 0:
        return {
            "averageDelta": 0.0,
            "targetInkRatio": 0.0,
            "targetDarkRatio": 0.0,
            "sourceInkRatio": 0.0,
            "sourceSupportedDeltaShare": 0.0,
            "targetOnlyDeltaShare": 0.0,
            "whiteSourceDeltaShare": 0.0,
        }
    target_luma = luma(target_crop)
    source_luma = luma(source_crop)
    source_ink = source_luma < SOURCE_INK_LUMA_THRESHOLD
    target_ink = target_luma < TARGET_INK_LUMA_THRESHOLD
    target_dark = target_luma < 150.0
    delta = np.abs(target_crop.astype(np.int16) - blend_crop.astype(np.int16)).mean(axis=2)
    delta_sum = float(delta.sum())
    if delta_sum:
        source_supported_delta_share = float(delta[source_ink].sum() / delta_sum)
        target_only_delta_share = float(delta[target_ink & ~source_ink].sum() / delta_sum)
        white_source_delta_share = float(delta[~source_ink].sum() / delta_sum)
    else:
        source_supported_delta_share = 0.0
        target_only_delta_share = 0.0
        white_source_delta_share = 0.0
    return {
        "averageDelta": round(float(delta.mean()), 6),
        "targetInkRatio": round(float(target_ink.mean()), 6),
        "targetDarkRatio": round(float(target_dark.mean()), 6),
        "sourceInkRatio": round(float(source_ink.mean()), 6),
        "sourceSupportedDeltaShare": round(source_supported_delta_share, 6),
        "targetOnlyDeltaShare": round(target_only_delta_share, 6),
        "whiteSourceDeltaShare": round(white_source_delta_share, 6),
    }


def make_overlay(
    target: Image.Image,
    source_ink_mask: np.ndarray,
    target_ink_mask: np.ndarray,
    active: list[dict[str, Any]],
) -> None:
    overlay = target.convert("RGBA")
    rgba = Image.new("RGBA", target.size, (0, 0, 0, 0))
    arr = np.asarray(rgba).copy()
    target_only = target_ink_mask & ~source_ink_mask
    arr[target_only] = [255, 0, 0, 75]
    arr[source_ink_mask] = [0, 90, 255, 95]
    combined = Image.alpha_composite(overlay, Image.fromarray(arr, "RGBA"))
    draw = ImageDraw.Draw(combined, "RGBA")
    for row in active:
        color = (255, 135, 0, 255) if row["visualState"] == "Y" else (15, 15, 15, 255)
        draw.rectangle(row["box"], outline=color, width=6)
        draw.text(
            (row["box"][0], max(0, row["box"][1] - 28)),
            row["shortId"],
            fill=(255, 0, 0, 255),
            font=font(26),
        )
    combined.convert("RGB").save(OUT_OVERLAY, quality=92)


def panel_for_row(
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    blend_arr: np.ndarray,
    source_ink_mask: np.ndarray,
    target_ink_mask: np.ndarray,
    row: dict[str, Any],
    metrics: dict[str, float],
) -> Image.Image:
    pad = 42
    x0, y0, x1, y1 = [int(round(v)) for v in row["box"]]
    crop_box = [x0 - pad, y0 - pad, x1 + pad, y1 + pad]
    target_crop = Image.fromarray(crop_arr(target_arr, crop_box))
    source_crop = Image.fromarray(crop_arr(source_arr, crop_box))
    blend_crop = Image.fromarray(crop_arr(blend_arr, crop_box))
    source_mask = crop_bool(source_ink_mask, crop_box)
    target_mask = crop_bool(target_ink_mask, crop_box)
    target_only = target_mask & ~source_mask
    overlay = target_crop.convert("RGBA")
    mask_img = Image.new("RGBA", target_crop.size, (0, 0, 0, 0))
    mask_arr = np.asarray(mask_img).copy()
    mask_arr[target_only] = [255, 0, 0, 105]
    mask_arr[source_mask] = [0, 90, 255, 115]
    overlay = Image.alpha_composite(overlay, Image.fromarray(mask_arr, "RGBA")).convert("RGB")

    w, h = 330, 125
    panel = Image.new("RGB", (w, h * 4 + 108), "white")
    draw = ImageDraw.Draw(panel)
    title = (
        f"{row['shortId']} {row['phrase']} | src {metrics['sourceInkRatio']:.4f} "
        f"| target-only delta {metrics['targetOnlyDeltaShare']:.2f}"
    )
    draw.text((10, 8), title[:78], fill="black", font=font(15))
    for idx, (label, image) in enumerate(
        [
            ("target p76", target_crop),
            ("mirrored p75 source", source_crop),
            ("average blend 0.70", blend_crop),
            ("red target-only / blue source", overlay),
        ]
    ):
        y = 40 + idx * h
        draw.text((10, y), label, fill="black", font=font(14))
        panel.paste(image.resize((w - 20, h - 22)), (10, y + 18))
    return panel


def make_sheet(
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    blend_arr: np.ndarray,
    source_ink_mask: np.ndarray,
    target_ink_mask: np.ndarray,
    active_rows: list[dict[str, Any]],
    active_metrics: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    panels = []
    metrics_by_id = {row["shortId"]: row for row in active_metrics}
    for row in active_rows:
        panels.append(
            panel_for_row(
                target_arr,
                source_arr,
                blend_arr,
                source_ink_mask,
                target_ink_mask,
                row,
                metrics_by_id[row["shortId"]],
            )
        )
    sheet = Image.new("RGB", (1380, 1290), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 20), "B4 self-signal guardrail: valid 75->76 average blend decomposition", fill="black", font=font(28))
    draw.text(
        (24, 58),
        f"Fingerprint: {summary['b4SelfSignalFingerprint']}",
        fill="black",
        font=font(15),
    )
    for idx, panel in enumerate(panels):
        x = 24 + (idx % 4) * 338
        y = 100
        sheet.paste(panel, (x, y))
    legend_y = 735
    draw.text((24, legend_y), "Legend", fill="black", font=font(22))
    draw.rectangle([24, legend_y + 34, 54, legend_y + 64], fill=(255, 0, 0))
    draw.text((66, legend_y + 36), "red = page-76 target ink with no page-75 source ink", fill="black", font=font(18))
    draw.rectangle([24, legend_y + 74, 54, legend_y + 104], fill=(0, 90, 255))
    draw.text((66, legend_y + 76), "blue = physical page-75 source ink landing", fill="black", font=font(18))
    draw.text(
        (24, legend_y + 130),
        f"B4: sourceInk={summary['b4SourceInkRatio']:.4f}, targetOnlyDeltaShare={summary['b4TargetOnlyDeltaShare']:.4f}, "
        f"sourceSupportedDeltaShare={summary['b4SourceSupportedDeltaShare']:.4f}, deltaAboveControlP95={summary['b4DeltaAboveMatchedControlP95']:.4f}",
        fill="black",
        font=font(18),
    )
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    source_landing = load_json(SOURCE_INK_LANDING)
    blend_gate = load_json(LIGHT_TABLE_BLEND_MODE)
    jitter_gate = load_json(JITTER_RESCUE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)

    scenario = source_landing.get("scenario", {})
    source_page = int(scenario.get("sourcePage", 75))
    target_page = int(scenario.get("targetPage", 76))
    dx = int(scenario.get("dx", 0))
    dy = int(scenario.get("dy", 0))

    target = normalize_page(target_page)
    source_page_img = normalize_page(source_page)
    source = shifted_mirrored_source(source_page_img, dx, dy)
    target_arr = np.asarray(target).copy()
    source_arr = np.asarray(source).copy()
    blend_arr = average_blend(target_arr, source_arr)

    source_ink_mask = luma(source_arr) < SOURCE_INK_LUMA_THRESHOLD
    target_ink_mask = luma(target_arr) < TARGET_INK_LUMA_THRESHOLD
    active = active_boxes(active_index)
    line_pitch = estimated_line_pitch(active)
    controls = build_control_boxes(active, target.size, line_pitch)

    active_metric_rows: list[dict[str, Any]] = []
    for row in active:
        metric = measure_region(target_arr, source_arr, blend_arr, row["box"])
        active_metric_rows.append({**row, **metric})

    control_metric_rows: list[dict[str, Any]] = []
    for row in controls:
        metric = measure_region(target_arr, source_arr, blend_arr, row["box"])
        control_metric_rows.append({**row, **metric})

    control_p95_by_target = {
        short_id: round(
            percentile(
                [
                    row["averageDelta"]
                    for row in control_metric_rows
                    if row["sourceTarget"] == short_id
                ],
                0.95,
            ),
            6,
        )
        for short_id in TARGET_ORDER
    }
    for row in active_metric_rows:
        p95 = control_p95_by_target.get(row["shortId"], 0.0)
        row["matchedControlP95AverageDelta"] = p95
        row["deltaAboveMatchedControlP95"] = round(row["averageDelta"] - p95, 6)
        row["sourceSupportedOutlier"] = (
            row["sourceInkRatio"] >= 0.05 and row["deltaAboveMatchedControlP95"] > 0
        )
        row["zeroSourceSelfSignal"] = (
            row["sourceInkRatio"] < 0.01
            and row["targetOnlyDeltaShare"] >= 0.95
            and row["deltaAboveMatchedControlP95"] > 0
        )

    b4 = next(row for row in active_metric_rows if row["shortId"] == "B4")
    source_supported_outliers = [
        row["shortId"] for row in active_metric_rows if row["sourceSupportedOutlier"]
    ]
    zero_source_self_signal_targets = [
        row["shortId"] for row in active_metric_rows if row["zeroSourceSelfSignal"]
    ]
    all_four_source_supported_outlier = len(source_supported_outliers) == 4
    source_r3 = trigger_matrix.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    satisfied = trigger_matrix.get("summary", {}).get("satisfiedTriggerCount", 0)
    triggers = trigger_matrix.get("summary", {}).get("triggerCount", 9)

    fingerprint = (
        f"scenario=valid_75_to_76_natural|alpha={AVERAGE_ALPHA:.2f}|targets=4|"
        f"controls={len(controls)}|B4src={b4['sourceInkRatio']:.4f}|"
        f"B4targetOnly={b4['targetOnlyDeltaShare']:.4f}|"
        f"B4srcDelta={b4['sourceSupportedDeltaShare']:.4f}|"
        f"B4dCtl={b4['deltaAboveMatchedControlP95']:.2f}|"
        f"srcOutliers={len(source_supported_outliers)}/4|"
        f"selfZero={','.join(zero_source_self_signal_targets) or 'none'}|"
        f"all4Src={int(all_four_source_supported_outlier)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{triggers}|selectors=0"
    )

    summary = {
        "scenarioId": "valid_75_to_76_natural",
        "sourcePage": source_page,
        "targetPage": target_page,
        "heldToLightMode": "natural_hflip",
        "dx": dx,
        "dy": dy,
        "blendMode": "average",
        "alpha": AVERAGE_ALPHA,
        "targetCount": len(active),
        "controlBoxCount": len(controls),
        "estimatedLinePitchPx": round(line_pitch, 6),
        "sourceInkLumaThreshold": SOURCE_INK_LUMA_THRESHOLD,
        "targetInkLumaThreshold": TARGET_INK_LUMA_THRESHOLD,
        "sourceSupportedOutlierTargets": source_supported_outliers,
        "zeroSourceSelfSignalTargets": zero_source_self_signal_targets,
        "allFourSourceSupportedOutlier": all_four_source_supported_outlier,
        "b4SourceInkRatio": b4["sourceInkRatio"],
        "b4TargetInkRatio": b4["targetInkRatio"],
        "b4TargetDarkRatio": b4["targetDarkRatio"],
        "b4AverageDelta": b4["averageDelta"],
        "b4MatchedControlP95AverageDelta": b4["matchedControlP95AverageDelta"],
        "b4DeltaAboveMatchedControlP95": b4["deltaAboveMatchedControlP95"],
        "b4TargetOnlyDeltaShare": b4["targetOnlyDeltaShare"],
        "b4WhiteSourceDeltaShare": b4["whiteSourceDeltaShare"],
        "b4SourceSupportedDeltaShare": b4["sourceSupportedDeltaShare"],
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": triggers,
        "selectorUnlocked": False,
        "b4SelfSignalFingerprint": fingerprint,
        "priorSourceInkLandingFingerprint": source_landing.get("fingerprint"),
        "priorBlendModeFingerprint": blend_gate.get("fingerprint"),
        "priorJitterRescueFingerprint": jitter_gate.get("fingerprint"),
    }

    make_overlay(target, source_ink_mask, target_ink_mask, active)
    make_sheet(
        target_arr,
        source_arr,
        blend_arr,
        source_ink_mask,
        target_ink_mask,
        active,
        active_metric_rows,
        summary,
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page-75-to-76 average-blend B4 self-signal guardrail; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "sourceInkLanding": rel(SOURCE_INK_LANDING),
            "lightTableBlendMode": rel(LIGHT_TABLE_BLEND_MODE),
            "jitterRescue": rel(JITTER_RESCUE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "activeMetricRows": active_metric_rows,
        "controlMetricRows": control_metric_rows,
        "controlP95ByTarget": control_p95_by_target,
        "decision": {
            "currentScanB4SelfSignalGuardrail": "current_scan_b4_self_signal_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "B4's average-blend pop is target-only: no valid page-75 source ink lands in B4, "
                "and its blend delta is carried by page-76 black target ink against a white/blank source area. "
                "This explains the visual all-four blend without promoting it as physical back-page evidence."
            ),
            "nextMove": (
                "Stop treating B4 average-blend contrast as a source carrier. Continue only with true "
                "original-layout/physical source comparison or raw clue wording that supplies transform, unit, and order."
            ),
        },
        "overlay": rel(OUT_OVERLAY),
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan B4 Self-Signal Guardrail",
        "",
        "Scope: decomposed the valid page-75-to-76 held-to-light average blend into source-supported pixels versus page-76 target-only pixels. This checks whether B4's visual pop is a real back-page source carrier. No key derivation, OCR-to-key extraction, seed/WIF/address checks, hashes, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "- Scenario: `valid_75_to_76_natural`, mirrored page `75` over page `76`, `dx=0`, `dy=0`",
        f"- Blend checked: `average@{AVERAGE_ALPHA:.2f}`",
        f"- Active targets / controls: `{len(active)}` / `{len(controls)}`",
        f"- Source-supported outlier targets: `{','.join(source_supported_outliers) or '-'}`",
        f"- Zero-source self-signal targets: `{','.join(zero_source_self_signal_targets) or '-'}`",
        f"- All-four source-supported outlier: `{all_four_source_supported_outlier}`",
        f"- B4 source-ink ratio: `{b4['sourceInkRatio']:.6f}`",
        f"- B4 target-ink ratio: `{b4['targetInkRatio']:.6f}`",
        f"- B4 average-blend delta: `{b4['averageDelta']:.6f}`",
        f"- B4 matched-control p95 delta: `{b4['matchedControlP95AverageDelta']:.6f}`",
        f"- B4 delta above matched control p95: `{b4['deltaAboveMatchedControlP95']:.6f}`",
        f"- B4 target-only delta share: `{b4['targetOnlyDeltaShare']:.6f}`",
        f"- B4 source-supported delta share: `{b4['sourceSupportedDeltaShare']:.6f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied}/{triggers}`",
        f"- Overlay: `{rel(OUT_OVERLAY)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Active Rows",
        "",
        "| target | phrase | source ink | target ink | avg delta | control p95 | delta over p95 | target-only delta share | source-supported delta share | verdict |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in active_metric_rows:
        verdict = (
            "zero-source self-signal"
            if row["zeroSourceSelfSignal"]
            else "source-supported outlier"
            if row["sourceSupportedOutlier"]
            else "not source-supported selector"
        )
        lines.append(
            f"| `{row['shortId']}` | {row['phrase']} | `{row['sourceInkRatio']:.6f}` | "
            f"`{row['targetInkRatio']:.6f}` | `{row['averageDelta']:.6f}` | "
            f"`{row['matchedControlP95AverageDelta']:.6f}` | `{row['deltaAboveMatchedControlP95']:.6f}` | "
            f"`{row['targetOnlyDeltaShare']:.6f}` | `{row['sourceSupportedDeltaShare']:.6f}` | {verdict} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_b4_self_signal_no_selector`",
            "- B4 has zero valid page-75 source ink but still produces a strong average-blend delta because the page-76 black target phrase is blended against a blank/white source area.",
            "- This explains why the all-four average-blend view can look tempting while still failing as physical back-page evidence.",
            "- Do not use B4 average-blend contrast, or the all-four average-blend visual pop, as a selector without a new source/clue that supplies transform, unit, and order.",
            "",
            "## Next Move",
            "",
            "- Stop varying current-scan light-table blend, opacity, and small registration jitter for B4.",
            "- Best next direction remains original-layout/physical source acquisition or raw clue wording scored against R1-R5 and the source-acquisition packet.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"wrote {OUT_OVERLAY}")
    print("fingerprint:", fingerprint)


if __name__ == "__main__":
    main()
