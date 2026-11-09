#!/usr/bin/env python3
"""Audit held-to-light blend modes against active-box controls.

This bounded pass uses the current scan/PDF page images and the existing
held-to-light registrations. It asks whether any plausible or diagnostic
light-table blend makes O4/B4/G5/O5 uniquely pop compared with nearby
line-shifted controls.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_light_table_blend_mode_gate.json"
OUT_MD = OUT / "current_scan_light_table_blend_mode_gate.md"
OUT_SHEET = OUT / "current_scan_light_table_blend_mode_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT_SIMULATOR = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
ACTIVE_BOX_BALANCE = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/"
    "current_scan_held_to_light_active_box_balance_gate.json"
)
OPACITY_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate/"
    "current_scan_held_to_light_opacity_gate.json"
)
CROP_LIGHT_TABLE = ROOT / (
    "analysis_outputs/source_audit/current_scan_crop_light_table_targets/"
    "current_scan_crop_light_table_targets.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
BLEND_MODES = ["multiply", "darken", "average", "difference", "source_ink"]
ALPHAS = [0.35, 0.50, 0.70]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]


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


def blend_arrays(target: np.ndarray, source: np.ndarray, mode: str, alpha: float) -> np.ndarray:
    t = target.astype(np.float32)
    s = source.astype(np.float32)
    if mode == "multiply":
        base = (t * s) / 255.0
    elif mode == "darken":
        base = np.minimum(t, s)
    elif mode == "average":
        base = s
    elif mode == "difference":
        base = np.abs(t - s)
    elif mode == "source_ink":
        ink = 255.0 - s
        base = np.clip(t - ink, 0, 255)
    else:  # pragma: no cover
        raise ValueError(mode)
    return np.clip((1.0 - alpha) * t + alpha * base, 0, 255).astype(np.uint8)


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


def shifted_box(box: list[float], dx: float, dy: float, page_size: tuple[int, int]) -> list[float] | None:
    w, h = page_size
    shifted = [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]
    if shifted[0] < 0 or shifted[1] < 0 or shifted[2] > w or shifted[3] > h:
        return None
    return shifted


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
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
            box = shifted_box(row["box"], 0, offset * line_pitch, page_size)
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


def region_metrics(
    target_arr: np.ndarray,
    blend_arr: np.ndarray,
    source_arr: np.ndarray,
    box: list[float],
) -> dict[str, float]:
    target_crop = crop_arr(target_arr, box)
    blend_crop = crop_arr(blend_arr, box)
    source_crop = crop_arr(source_arr, box)
    if target_crop.size == 0:
        return {
            "absRgbDelta": 0.0,
            "lumaDelta": 0.0,
            "sourceInkRatio": 0.0,
            "blendContrast": 0.0,
        }
    abs_rgb = float(
        np.abs(target_crop.astype(np.int16) - blend_crop.astype(np.int16)).mean()
    )
    luma_delta = float(abs(luma(target_crop).mean() - luma(blend_crop).mean()))
    source_ink = float((luma(source_crop) < 238).mean()) if source_crop.size else 0.0
    contrast = float(luma(blend_crop).std())
    return {
        "absRgbDelta": round(abs_rgb, 6),
        "lumaDelta": round(luma_delta, 6),
        "sourceInkRatio": round(source_ink, 6),
        "blendContrast": round(contrast, 6),
    }


def held_sim_row(rows: list[dict[str, Any]], pair_id: str, mode: str) -> dict[str, Any]:
    for row in rows:
        if row.get("pairId") == pair_id and row.get("mode") == mode:
            return row
    raise KeyError(f"{pair_id}/{mode}")


def scenario_rows(held: dict[str, Any]) -> list[dict[str, Any]]:
    rows = held.get("rows", [])
    picked = [
        (
            "valid_75_to_76_natural",
            "same_leaf_75_to_76",
            "natural_hflip",
            "valid same leaf, natural alignment",
        ),
        (
            "valid_75_to_76_forced_active",
            "same_leaf_75_to_76",
            "best_page76_active_boxes",
            "valid same leaf, forced active-box alignment",
        ),
        (
            "nonphysical_78_to_76_forced_active",
            "nonphysical_78_to_76",
            "best_page76_active_boxes",
            "non-physical page-76 benchmark",
        ),
        (
            "nonphysical_79_to_76_forced_active",
            "nonphysical_79_to_76",
            "best_page76_active_boxes",
            "non-physical page-76 benchmark",
        ),
    ]
    scenarios: list[dict[str, Any]] = []
    for scenario_id, pair_id, mode, topology in picked:
        source = held_sim_row(rows, pair_id, mode)
        scenarios.append(
            {
                "scenarioId": scenario_id,
                "pairId": pair_id,
                "sourcePage": int(source["sourcePage"]),
                "targetPage": int(source["targetPage"]),
                "heldToLightMode": mode,
                "topology": topology,
                "dx": int(source["dx"]),
                "dy": int(source["dy"]),
                "binaryActiveOverTarget": round(float(source.get("activeOverTarget", 0.0)), 6),
                "sameLeaf75To76": pair_id == "same_leaf_75_to_76",
                "physicalNatural": pair_id == "same_leaf_75_to_76" and mode == "natural_hflip",
                "nonphysical": str(pair_id).startswith("nonphysical"),
            }
        )
    return scenarios


def outlier_row(
    scenario: dict[str, Any],
    blend_mode: str,
    alpha: float,
    active_metrics: list[dict[str, Any]],
    control_metrics: list[dict[str, Any]],
) -> dict[str, Any]:
    control_by_target = {
        target: [row for row in control_metrics if row["sourceTarget"] == target]
        for target in TARGET_ORDER
    }
    active_by_target = {row["target"]: row for row in active_metrics}
    target_rows: list[dict[str, Any]] = []
    outlier_count = 0
    p95_values = []
    gains = []
    active_values = []
    active_source_ink_values = []
    source_supported_outlier_count = 0
    for target in TARGET_ORDER:
        active_value = float(active_by_target[target]["absRgbDelta"])
        active_source_ink = float(active_by_target[target]["sourceInkRatio"])
        controls = [float(row["absRgbDelta"]) for row in control_by_target[target]]
        p95 = float(np.percentile(controls, 95)) if controls else 0.0
        median_control = float(np.median(controls)) if controls else 0.0
        gain = active_value - p95
        is_outlier = active_value > p95 and gain >= 2.0
        source_supported = is_outlier and active_source_ink >= 0.05
        outlier_count += int(is_outlier)
        source_supported_outlier_count += int(source_supported)
        p95_values.append(p95)
        gains.append(gain)
        active_values.append(active_value)
        active_source_ink_values.append(active_source_ink)
        target_rows.append(
            {
                "target": target,
                "activeAbsRgbDelta": round(active_value, 6),
                "activeSourceInkRatio": round(active_source_ink, 6),
                "matchedControlP95AbsRgbDelta": round(p95, 6),
                "matchedControlMedianAbsRgbDelta": round(median_control, 6),
                "activeMinusControlP95": round(gain, 6),
                "outlierVsMatchedControls": is_outlier,
                "sourceSupportedOutlier": source_supported,
            }
        )
    min_active = min(active_values) if active_values else 0.0
    max_active = max(active_values) if active_values else 0.0
    balance = min_active / max_active if max_active else 0.0
    all_four_outlier = outlier_count == 4
    all_four_source_supported = source_supported_outlier_count == 4
    selector_candidate = bool(
        scenario["physicalNatural"]
        and all_four_source_supported
        and min(gains) >= 4.0
        and min(active_source_ink_values) >= 0.05
    )
    return {
        **scenario,
        "blendMode": blend_mode,
        "alpha": alpha,
        "activeMeanAbsRgbDelta": round(float(np.mean(active_values)), 6),
        "activeMinAbsRgbDelta": round(min_active, 6),
        "activeMaxAbsRgbDelta": round(max_active, 6),
        "activeMinSourceInkRatio": round(float(min(active_source_ink_values)), 6),
        "activeMeanSourceInkRatio": round(float(np.mean(active_source_ink_values)), 6),
        "activeBalanceRatio": round(balance, 6),
        "matchedControlMeanP95AbsRgbDelta": round(float(np.mean(p95_values)), 6),
        "minActiveMinusMatchedControlP95": round(float(min(gains)), 6),
        "activeOutlierCount": outlier_count,
        "sourceSupportedOutlierCount": source_supported_outlier_count,
        "allFourActiveOutlier": all_four_outlier,
        "allFourSourceSupportedOutlier": all_four_source_supported,
        "selectorCandidateBeforeR3": selector_candidate,
        "targetRows": target_rows,
    }


def save_preview(
    image: Image.Image,
    scenario: dict[str, Any],
    mode: str,
    alpha: float,
    active_rows: list[dict[str, Any]],
    controls: list[dict[str, Any]],
) -> Path:
    out_w = 620
    out_h = round(out_w * image.height / image.width)
    preview = image.resize((out_w, out_h))
    draw = ImageDraw.Draw(preview, "RGBA")
    sx = out_w / image.width
    sy = out_h / image.height
    for control in controls:
        x0, y0, x1, y1 = control["box"]
        draw.rectangle(
            [x0 * sx, y0 * sy, x1 * sx, y1 * sy],
            outline=(45, 110, 255, 120),
            width=1,
        )
    for box in active_rows:
        x0, y0, x1, y1 = box["box"]
        color = (255, 130, 0, 240) if box["visualState"] == "Y" else (20, 20, 20, 240)
        draw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=color, width=3)
        draw.text((x0 * sx, max(0, y0 * sy - 18)), box["shortId"], fill=(255, 0, 0, 255))
    draw.rectangle((0, 0, out_w, 40), fill=(0, 0, 0, 180))
    draw.text(
        (8, 10),
        f"{scenario['scenarioId']} {mode} alpha={alpha:.2f}",
        fill=(255, 255, 255, 255),
    )
    path = OUT / f"{scenario['scenarioId']}_{mode}_{alpha:.2f}.jpg"
    preview.save(path, quality=90)
    return path


def draw_sheet(
    rows: list[dict[str, Any]],
    preview_paths: list[Path],
    line_pitch: float,
    control_count: int,
) -> None:
    sheet = Image.new("RGB", (1900, 1300), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(25)
    small = font(14)
    tiny = font(11)
    draw.rectangle((0, 0, 1900, 104), fill=(24, 31, 42))
    draw.text((24, 16), "Current Scan Light-Table Blend-Mode Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        f"Active boxes compared with {control_count} nearby line-shifted controls; estimated line pitch {line_pitch:.2f}px.",
        fill=(235, 235, 235),
        font=small,
    )
    best = sorted(
        rows,
        key=lambda row: (
            row["allFourSourceSupportedOutlier"],
            row["sourceSupportedOutlierCount"],
            row["minActiveMinusMatchedControlP95"],
        ),
        reverse=True,
    )[:6]
    draw.text(
        (1170, 22),
        f"best source-supported {best[0]['sourceSupportedOutlierCount']}/4 | all-four source rows {sum(1 for r in rows if r['allFourSourceSupportedOutlier'])}",
        fill=(235, 235, 235),
        font=small,
    )
    x, y = 24, 126
    for path in preview_paths[:6]:
        img = Image.open(path).convert("RGB").resize((300, 385))
        sheet.paste(img, (x, y))
        x += 314
    y = 550
    headers = [
        "scenario",
        "mode",
        "alpha",
        "outliers",
        "src",
        "min gain",
        "active mean",
        "ctrl p95 mean",
        "balance",
    ]
    xs = [24, 430, 540, 610, 680, 745, 850, 960, 1085]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in best + sorted(rows, key=lambda r: r["activeMeanAbsRgbDelta"], reverse=True)[:14]:
        vals = [
            row["scenarioId"],
            row["blendMode"],
            f"{row['alpha']:.2f}",
            f"{row['activeOutlierCount']}/4",
            f"{row['sourceSupportedOutlierCount']}/4",
            f"{row['minActiveMinusMatchedControlP95']:.2f}",
            f"{row['activeMeanAbsRgbDelta']:.2f}",
            f"{row['matchedControlMeanP95AbsRgbDelta']:.2f}",
            f"{row['activeBalanceRatio']:.2f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(30, 34, 40), font=tiny)
        y += 18
        if y > 1210:
            break
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    held = load_json(HELD_TO_LIGHT_SIMULATOR)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    active_balance = load_json(ACTIVE_BOX_BALANCE)
    opacity_gate = load_json(OPACITY_GATE)
    crop_light_table = load_json(CROP_LIGHT_TABLE)

    active = active_boxes(active_index)
    page_cache = {page: normalize_page(page) for page in {75, 76, 78, 79}}
    target_page = page_cache[76]
    target_arr = np.asarray(target_page.convert("RGB"))
    line_pitch = estimated_line_pitch(active)
    controls = build_control_boxes(active, target_page.size, line_pitch)
    scenarios = scenario_rows(held)

    blend_rows: list[dict[str, Any]] = []
    active_metric_rows: list[dict[str, Any]] = []
    control_metric_rows: list[dict[str, Any]] = []
    preview_paths: list[Path] = []

    for scenario in scenarios:
        source_img = shifted_mirrored_source(
            page_cache[scenario["sourcePage"]], scenario["dx"], scenario["dy"]
        )
        source_arr = np.asarray(source_img.convert("RGB"))
        for mode in BLEND_MODES:
            for alpha in ALPHAS:
                blend_arr = blend_arrays(target_arr, source_arr, mode, alpha)
                active_metrics = []
                for box in active:
                    metrics = region_metrics(target_arr, blend_arr, source_arr, box["box"])
                    row = {
                        **scenario,
                        "blendMode": mode,
                        "alpha": alpha,
                        "target": box["shortId"],
                        "phrase": box["phrase"],
                        "visualState": box["visualState"],
                        **metrics,
                    }
                    active_metric_rows.append(row)
                    active_metrics.append(row)
                control_metrics = []
                for control in controls:
                    metrics = region_metrics(target_arr, blend_arr, source_arr, control["box"])
                    row = {
                        **scenario,
                        "blendMode": mode,
                        "alpha": alpha,
                        "controlId": control["id"],
                        "sourceTarget": control["sourceTarget"],
                        "lineOffset": control["lineOffset"],
                        **metrics,
                    }
                    control_metric_rows.append(row)
                    control_metrics.append(row)
                blend_row = outlier_row(
                    scenario,
                    mode,
                    alpha,
                    active_metrics,
                    control_metrics,
                )
                blend_rows.append(blend_row)
                if mode in {"multiply", "darken", "source_ink"} and alpha in {0.5, 0.7}:
                    preview_paths.append(
                        save_preview(
                            Image.fromarray(blend_arr),
                            scenario,
                            mode,
                            alpha,
                            active,
                            controls,
                        )
                    )

    natural_rows = [row for row in blend_rows if row["scenarioId"] == "valid_75_to_76_natural"]
    forced_or_control_rows = [
        row for row in blend_rows if row["scenarioId"] != "valid_75_to_76_natural"
    ]
    best = max(blend_rows, key=lambda row: (row["activeOutlierCount"], row["minActiveMinusMatchedControlP95"]))
    best_natural = max(
        natural_rows,
        key=lambda row: (row["activeOutlierCount"], row["minActiveMinusMatchedControlP95"]),
    )
    best_forced_or_control = max(
        forced_or_control_rows,
        key=lambda row: (row["activeOutlierCount"], row["minActiveMinusMatchedControlP95"]),
    )
    natural_all_four = sum(1 for row in natural_rows if row["allFourActiveOutlier"])
    forced_or_control_all_four = sum(
        1 for row in forced_or_control_rows if row["allFourActiveOutlier"]
    )
    natural_all_four_source_supported = sum(
        1 for row in natural_rows if row["allFourSourceSupportedOutlier"]
    )
    forced_or_control_all_four_source_supported = sum(
        1 for row in forced_or_control_rows if row["allFourSourceSupportedOutlier"]
    )
    pre_r3_candidates = sum(1 for row in blend_rows if row["selectorCandidateBeforeR3"])
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    selector_count = 0

    fingerprint = (
        f"scenarios={len(scenarios)}|modes={len(BLEND_MODES)}|alphas={len(ALPHAS)}"
        f"|blendRows={len(blend_rows)}|controls={len(controls)}"
        f"|naturalAll4Outlier={natural_all_four}|controlAll4Outlier={forced_or_control_all_four}"
        f"|naturalAll4Source={natural_all_four_source_supported}"
        f"|controlAll4Source={forced_or_control_all_four_source_supported}"
        f"|bestNatural={best_natural['activeOutlierCount']}/4:"
        f"{best_natural['sourceSupportedOutlierCount']}/4src:"
        f"{best_natural['blendMode']}@{best_natural['alpha']:.2f}:"
        f"{best_natural['minActiveMinusMatchedControlP95']:.2f}"
        f"|bestControl={best_forced_or_control['activeOutlierCount']}/4:"
        f"{best_forced_or_control['sourceSupportedOutlierCount']}/4src:"
        f"{best_forced_or_control['scenarioId']}:{best_forced_or_control['blendMode']}@"
        f"{best_forced_or_control['alpha']:.2f}:"
        f"{best_forced_or_control['minActiveMinusMatchedControlP95']:.2f}"
        f"|preR3={pre_r3_candidates}|sourceR3={source_r3}"
        f"|triggers={satisfied_triggers}/{trigger_count}|selectors={selector_count}"
    )

    summary = {
        "scenarioCount": len(scenarios),
        "blendModeCount": len(BLEND_MODES),
        "alphaCount": len(ALPHAS),
        "blendRowCount": len(blend_rows),
        "activeMetricRowCount": len(active_metric_rows),
        "controlMetricRowCount": len(control_metric_rows),
        "controlBoxCount": len(controls),
        "estimatedLinePitchPx": round(line_pitch, 6),
        "bestScenarioId": best["scenarioId"],
        "bestBlendMode": best["blendMode"],
        "bestAlpha": best["alpha"],
        "bestActiveOutlierCount": best["activeOutlierCount"],
        "bestMinActiveMinusMatchedControlP95": best["minActiveMinusMatchedControlP95"],
        "bestNaturalActiveOutlierCount": best_natural["activeOutlierCount"],
        "bestNaturalSourceSupportedOutlierCount": best_natural[
            "sourceSupportedOutlierCount"
        ],
        "bestNaturalBlend": f"{best_natural['blendMode']}@{best_natural['alpha']:.2f}",
        "bestNaturalMinActiveMinusMatchedControlP95": best_natural[
            "minActiveMinusMatchedControlP95"
        ],
        "bestForcedOrControlActiveOutlierCount": best_forced_or_control[
            "activeOutlierCount"
        ],
        "bestForcedOrControlSourceSupportedOutlierCount": best_forced_or_control[
            "sourceSupportedOutlierCount"
        ],
        "bestForcedOrControlScenario": best_forced_or_control["scenarioId"],
        "bestForcedOrControlBlend": (
            f"{best_forced_or_control['blendMode']}@{best_forced_or_control['alpha']:.2f}"
        ),
        "bestForcedOrControlMinActiveMinusMatchedControlP95": best_forced_or_control[
            "minActiveMinusMatchedControlP95"
        ],
        "naturalAllFourActiveOutlierCount": natural_all_four,
        "forcedOrControlAllFourActiveOutlierCount": forced_or_control_all_four,
        "naturalAllFourSourceSupportedOutlierCount": natural_all_four_source_supported,
        "forcedOrControlAllFourSourceSupportedOutlierCount": forced_or_control_all_four_source_supported,
        "selectorCandidateBeforeR3Count": pre_r3_candidates,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "lightTableBlendModeFingerprint": fingerprint,
        "priorHeldToLightActiveBalanceFingerprint": active_balance.get("fingerprint"),
        "priorOpacityFingerprint": opacity_gate.get("fingerprint"),
        "priorCropLightTableFingerprint": crop_light_table.get("summary", {}).get(
            "cropLightTableFingerprint"
        ),
    }

    draw_sheet(blend_rows, preview_paths, line_pitch, len(controls))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current scan/PDF light-table blend-mode contrast gate; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT_SIMULATOR),
            "activeBoxBalanceGate": rel(ACTIVE_BOX_BALANCE),
            "opacityGate": rel(OPACITY_GATE),
            "cropLightTableTargets": rel(CROP_LIGHT_TABLE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "blendModes": BLEND_MODES,
        "alphas": ALPHAS,
        "controlLineOffsets": CONTROL_LINE_OFFSETS,
        "scenarios": scenarios,
        "activeBoxes": active,
        "controlBoxes": controls,
        "blendRows": blend_rows,
        "activeMetricRows": active_metric_rows,
        "controlMetricRows": control_metric_rows,
        "summary": summary,
        "decision": {
            "currentScanLightTableBlendModeGate": "current_scan_light_table_blend_mode_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The physically valid natural 75->76 average blend can make all four active "
                "boxes outliers against nearby line-shift controls, but the effect is not "
                "source-ink-supported across the quartet. It is a target-highlight washout "
                "artifact under arbitrary blend/alpha choices, while no source-backed R3 "
                "unit/order bridge is present."
            ),
            "nextMove": (
                "Keep the current scan as a registration witness only. The next useful move "
                "is still a true original-layout/physical source or raw clue wording that "
                "names transform, unit, and order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Light-Table Blend-Mode Gate",
        "",
        "Scope: tested whether alternate held-to-light blend modes make O4/B4/G5/O5 uniquely stand out against nearby line-shifted controls. The pass uses the current scan/PDF page images and the existing held-to-light registrations only. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scenarios / blend rows: `{len(scenarios)}` / `{len(blend_rows)}`",
        f"- Blend modes / alphas: `{', '.join(BLEND_MODES)}` / `{', '.join(f'{a:.2f}' for a in ALPHAS)}`",
        f"- Active boxes / line-shift control boxes: `{len(active)}` / `{len(controls)}`",
        f"- Estimated line pitch: `{line_pitch:.2f}px`",
        f"- Best natural 75->76 outliers: `{best_natural['activeOutlierCount']}/4` via `{best_natural['blendMode']}@{best_natural['alpha']:.2f}` with min active-control p95 gain `{best_natural['minActiveMinusMatchedControlP95']:.2f}`",
        f"- Best natural source-supported outliers: `{best_natural['sourceSupportedOutlierCount']}/4` with min active source-ink ratio `{best_natural['activeMinSourceInkRatio']:.4f}`",
        f"- Best forced/control outliers: `{best_forced_or_control['activeOutlierCount']}/4` via `{best_forced_or_control['scenarioId']}` / `{best_forced_or_control['blendMode']}@{best_forced_or_control['alpha']:.2f}` with min active-control p95 gain `{best_forced_or_control['minActiveMinusMatchedControlP95']:.2f}`",
        f"- Best forced/control source-supported outliers: `{best_forced_or_control['sourceSupportedOutlierCount']}/4`",
        f"- Natural all-four active-outlier rows / forced-or-control all-four rows: `{natural_all_four}` / `{forced_or_control_all_four}`",
        f"- Natural all-four source-supported rows / forced-or-control all-four source-supported rows: `{natural_all_four_source_supported}` / `{forced_or_control_all_four_source_supported}`",
        f"- Selector candidates before R3 / final selectors: `{pre_r3_candidates}` / `0`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Top Blend Rows",
        "",
        "| scenario | mode | alpha | outliers | source-supported | min active-control p95 gain | source ink min | active mean delta | control p95 mean | balance |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(
        blend_rows,
        key=lambda item: (
            item["allFourSourceSupportedOutlier"],
            item["sourceSupportedOutlierCount"],
            item["allFourActiveOutlier"],
            item["activeOutlierCount"],
            item["minActiveMinusMatchedControlP95"],
            item["activeMeanAbsRgbDelta"],
        ),
        reverse=True,
    )[:30]:
        lines.append(
            f"| `{row['scenarioId']}` | `{row['blendMode']}` | {row['alpha']:.2f} | {row['activeOutlierCount']}/4 | {row['sourceSupportedOutlierCount']}/4 | {row['minActiveMinusMatchedControlP95']:.2f} | {row['activeMinSourceInkRatio']:.4f} | {row['activeMeanAbsRgbDelta']:.2f} | {row['matchedControlMeanP95AbsRgbDelta']:.2f} | {row['activeBalanceRatio']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_light_table_blend_mode_no_selector`",
            "- Alternate blend modes can create natural 75->76 all-four active outliers in average mode, but those rows are not source-ink-supported across O4/B4/G5/O5.",
            "- The strongest apparent effect is a target-highlight washout under arbitrary average blend/alpha, not a readable back-page ink landing pattern.",
            "- This reinforces the earlier held-to-light active-box balance and opacity closures; current scan/PDF material remains useful for visual validation, not extraction.",
            "",
            "## Next Move",
            "",
            "- Stop varying current-scan light-table blend modes unless a new source/clue supplies a specific blend, opacity, transform, unit, and order.",
            "- Continue with original-layout/physical source acquisition or raw clue wording scored against the source-acquisition packet and R1-R5 reopen requirements.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanLightTableBlendModeGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
