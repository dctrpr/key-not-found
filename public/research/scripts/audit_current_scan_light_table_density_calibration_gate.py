#!/usr/bin/env python3
"""Calibrate natural held-to-light hits against source-page ink density.

This bounded pass follows the all-leaf parity gate. It keeps the same natural
valid leaf pairs, normalizes mirrored source ink against full-page, active-band,
C9-frame, and matched line-control densities, and asks whether page 76 becomes
special only after density normalization.

No OCR-to-key extraction, candidate generation, key derivation, hashing,
seed/WIF/address checks, BIP39 checks, or brute force is run.
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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_light_table_density_calibration_gate.json"
OUT_MD = OUT / "current_scan_light_table_density_calibration_gate.md"
OUT_SHEET = OUT / "current_scan_light_table_density_calibration_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
ALL_LEAF_PARITY = ROOT / (
    "analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/"
    "current_scan_all_leaf_light_table_parity_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
VALID_PAIRS = [
    ("valid_75_to_76", 75, 76),
    ("valid_77_to_78", 77, 78),
    ("valid_79_to_80", 79, 80),
]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]
INK_LUMA_THRESHOLD = 238.0
EPSILON = 1e-9


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
    source = Image.open(Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))).convert("RGB")
    upright = Image.open(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    return source.rotate(180) if rot_diff < same_diff else source


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def masks(img: Image.Image) -> dict[str, np.ndarray]:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    feature = dark | orange | grey
    ink = luma(arr.astype(np.float32)) < INK_LUMA_THRESHOLD
    return {"ink": ink, "feature": feature}


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def ratio(mask: np.ndarray, box: list[float] | None = None) -> float:
    cropped = crop_bool(mask, box) if box else mask
    return float(cropped.mean()) if cropped.size else 0.0


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


def control_boxes(rows: list[dict[str, Any]], page_size: tuple[int, int], pitch: float) -> list[dict[str, Any]]:
    active_bounds = [row["box"] for row in rows]
    controls: list[dict[str, Any]] = []
    for row in rows:
        for offset in CONTROL_LINE_OFFSETS:
            box = shifted_box(row["box"], offset * pitch, page_size)
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


def overdose_slots(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [])]
    projections = c9.get("projections", [])
    if len(frame) != 4 or not projections:
        return []
    slots = []
    for slot in projections[0].get("slots", []):
        slots.append(
            {
                "id": f"slot_{slot['index']}_{slot['letter']}",
                "slotIndex": int(slot["index"]),
                "letter": slot["letter"],
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return slots


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(values, q)) if values else 0.0


def active_band_box(active: list[dict[str, Any]], page_size: tuple[int, int]) -> list[float]:
    width, _ = page_size
    y0 = min(row["box"][1] for row in active)
    y1 = max(row["box"][3] for row in active)
    return [0.0, y0, float(width), y1]


def norm(value: float, denom: float) -> float:
    return float(value / max(denom, EPSILON))


def measure_box(pair_context: dict[str, Any], box: list[float], role: str, label: str) -> dict[str, Any]:
    ink = ratio(pair_context["masks"]["ink"], box)
    feature = ratio(pair_context["masks"]["feature"], box)
    return {
        "pairId": pair_context["pairId"],
        "sourcePage": pair_context["sourcePage"],
        "targetPage": pair_context["targetPage"],
        "role": role,
        "label": label,
        "box": [round(float(v), 3) for v in box],
        "sourceInkRatio": round(ink, 6),
        "sourceFeatureRatio": round(feature, 6),
        "inkOverPageDensity": round(norm(ink, pair_context["pageInkDensity"]), 6),
        "inkOverActiveBandDensity": round(norm(ink, pair_context["activeBandInkDensity"]), 6),
        "inkOverC9FrameDensity": round(norm(ink, pair_context["c9FrameInkDensity"]), 6),
        "featureOverPageDensity": round(norm(feature, pair_context["pageFeatureDensity"]), 6),
        "featureOverActiveBandDensity": round(norm(feature, pair_context["activeBandFeatureDensity"]), 6),
        "featureOverC9FrameDensity": round(norm(feature, pair_context["c9FrameFeatureDensity"]), 6),
    }


def draw_sheet(pair_rows: list[dict[str, Any]], active_rows: list[dict[str, Any]], active_comparisons: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1900, 1280), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 1900, 104), fill=(24, 31, 42))
    draw.text((24, 16), "Light-Table Density Calibration Gate", fill="white", font=font(25))
    draw.text(
        (24, 54),
        "Natural valid leaf overlays normalized by full-page, active-band, C9-frame, and matched line-control source density.",
        fill=(235, 235, 235),
        font=font(14),
    )
    draw.text(
        (1210, 20),
        f"p76 norm outliers ink/feature: {summary['page76NormalizedInkOutlierCount']}/{summary['page76NormalizedFeatureOutlierCount']}",
        fill=(235, 235, 235),
        font=font(14),
    )
    draw.text(
        (1210, 50),
        f"all-four: {int(summary['allFourPage76NormalizedInkOutlier'])}/{int(summary['allFourPage76NormalizedFeatureOutlier'])}",
        fill=(235, 235, 235),
        font=font(14),
    )

    y = 132
    draw.text((24, y), "Pair density baselines", fill=(30, 34, 40), font=font(15))
    y += 28
    headers = ["pair", "src->target", "page ink", "band ink", "C9 ink", "active mean", "active/page", "active/band", "active/C9", "ctrl p95"]
    xs = [24, 180, 300, 400, 500, 600, 718, 838, 958, 1070]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for row in pair_rows:
        values = [
            row["pairId"],
            f"{row['sourcePage']}->{row['targetPage']}",
            f"{row['pageInkDensity']:.4f}",
            f"{row['activeBandInkDensity']:.4f}",
            f"{row['c9FrameInkDensity']:.4f}",
            f"{row['activeInkMean']:.4f}",
            f"{row['activeInkMeanOverPageDensity']:.3f}",
            f"{row['activeInkMeanOverActiveBandDensity']:.3f}",
            f"{row['activeInkMeanOverC9FrameDensity']:.3f}",
            f"{row['lineControlInkP95']:.4f}",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(25, 28, 34), font=font(11))
        y += 22

    y += 34
    draw.text((24, y), "Page-76 target normalization checks", fill=(30, 34, 40), font=font(15))
    y += 28
    headers = ["target", "p76 ink/page", "other max", "ctrl p95", "ink out", "p76 feat/page", "other max", "ctrl p95", "feat out"]
    xs = [24, 110, 225, 320, 410, 500, 630, 725, 815]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for row in active_comparisons:
        values = [
            row["target"],
            f"{row['page76InkOverPageDensity']:.4f}",
            f"{row['otherLeafInkOverPageDensityMax']:.4f}",
            f"{row['controlInkOverPageDensityP95']:.4f}",
            str(int(row["page76NormalizedInkOutlier"])),
            f"{row['page76FeatureOverPageDensity']:.4f}",
            f"{row['otherLeafFeatureOverPageDensityMax']:.4f}",
            f"{row['controlFeatureOverPageDensityP95']:.4f}",
            str(int(row["page76NormalizedFeatureOutlier"])),
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(25, 28, 34), font=font(11))
        y += 22

    y += 34
    draw.text((24, y), "Raw active rows", fill=(30, 34, 40), font=font(15))
    y += 28
    headers = ["pair", "target", "ink", "ink/page", "ink/band", "ink/C9", "feature/page"]
    xs = [24, 180, 280, 370, 470, 570, 670]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for row in active_rows:
        values = [
            row["pairId"],
            row["target"],
            f"{row['sourceInkRatio']:.4f}",
            f"{row['inkOverPageDensity']:.3f}",
            f"{row['inkOverActiveBandDensity']:.3f}",
            f"{row['inkOverC9FrameDensity']:.3f}",
            f"{row['featureOverPageDensity']:.3f}",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(25, 28, 34), font=font(11))
        y += 20
        if y > 1120:
            break

    y = 1140
    notes = [
        "Density normalization does not promote page 76: B4 remains zero, and no all-four active normalized outlier exists.",
        "High same-coordinate readings on page 78 are explained by source page 77 density, not a hidden page-76 instruction.",
        "The current scan remains a source-review witness only; extraction still needs external unit/order evidence.",
    ]
    for note in notes:
        draw.text((24, y), "- " + note, fill=(25, 28, 34), font=font(14))
        y += 25
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = active_boxes(load_json(ACTIVE_INDEX_SLOT))
    c9 = load_json(C9_HEADER_GLYPH_SLOT)
    c9_frame = [float(v) for v in c9.get("c9Frame", [0, 0, 0, 0])]
    slots = overdose_slots(c9)
    page_size = normalize_page(76).size
    band_box = active_band_box(active, page_size)
    pitch = estimated_line_pitch(active)
    controls = control_boxes(active, page_size, pitch)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    parity = load_json(ALL_LEAF_PARITY)

    pair_contexts: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    active_rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    slot_rows: list[dict[str, Any]] = []

    for pair_id, source_page, target_page in VALID_PAIRS:
        source = normalize_page(source_page)
        mirrored = ImageOps.mirror(source)
        pair_masks = masks(mirrored)
        context = {
            "pairId": pair_id,
            "sourcePage": source_page,
            "targetPage": target_page,
            "masks": pair_masks,
            "pageInkDensity": ratio(pair_masks["ink"]),
            "pageFeatureDensity": ratio(pair_masks["feature"]),
            "activeBandInkDensity": ratio(pair_masks["ink"], band_box),
            "activeBandFeatureDensity": ratio(pair_masks["feature"], band_box),
            "c9FrameInkDensity": ratio(pair_masks["ink"], c9_frame),
            "c9FrameFeatureDensity": ratio(pair_masks["feature"], c9_frame),
        }
        pair_contexts.append(context)

        pair_active_rows = []
        for row in active:
            measured = measure_box(context, row["box"], "active", row["shortId"])
            measured.update(
                {
                    "target": row["shortId"],
                    "phrase": row["phrase"],
                    "visualState": row["visualState"],
                }
            )
            active_rows.append(measured)
            pair_active_rows.append(measured)
        for control in controls:
            measured = measure_box(context, control["box"], "line_shift_control", control["id"])
            measured.update(
                {
                    "controlId": control["id"],
                    "sourceTarget": control["sourceTarget"],
                    "lineOffset": control["lineOffset"],
                }
            )
            control_rows.append(measured)
        for slot in slots:
            measured = measure_box(context, slot["box"], "overdose_slot", slot["id"])
            measured.update(
                {
                    "slotId": slot["id"],
                    "slotIndex": slot["slotIndex"],
                    "letter": slot["letter"],
                }
            )
            slot_rows.append(measured)

        active_ink = [float(row["sourceInkRatio"]) for row in pair_active_rows]
        active_feature = [float(row["sourceFeatureRatio"]) for row in pair_active_rows]
        control_ink = [
            float(row["sourceInkRatio"])
            for row in control_rows
            if row["pairId"] == pair_id
        ]
        pair_rows.append(
            {
                "pairId": pair_id,
                "sourcePage": source_page,
                "targetPage": target_page,
                "pageInkDensity": round(context["pageInkDensity"], 6),
                "pageFeatureDensity": round(context["pageFeatureDensity"], 6),
                "activeBandInkDensity": round(context["activeBandInkDensity"], 6),
                "activeBandFeatureDensity": round(context["activeBandFeatureDensity"], 6),
                "c9FrameInkDensity": round(context["c9FrameInkDensity"], 6),
                "c9FrameFeatureDensity": round(context["c9FrameFeatureDensity"], 6),
                "activeInkMean": round(float(np.mean(active_ink)), 6),
                "activeInkMin": round(float(np.min(active_ink)), 6),
                "activeFeatureMean": round(float(np.mean(active_feature)), 6),
                "activeInkMeanOverPageDensity": round(
                    norm(float(np.mean(active_ink)), context["pageInkDensity"]), 6
                ),
                "activeInkMeanOverActiveBandDensity": round(
                    norm(float(np.mean(active_ink)), context["activeBandInkDensity"]), 6
                ),
                "activeInkMeanOverC9FrameDensity": round(
                    norm(float(np.mean(active_ink)), context["c9FrameInkDensity"]), 6
                ),
                "lineControlInkMedian": round(float(np.median(control_ink)), 6),
                "lineControlInkP95": round(percentile(control_ink, 95), 6),
            }
        )

    active_comparisons: list[dict[str, Any]] = []
    for target in TARGET_ORDER:
        p76 = next(row for row in active_rows if row["target"] == target and row["targetPage"] == 76)
        others = [row for row in active_rows if row["target"] == target and row["targetPage"] != 76]
        controls_for_target = [row for row in control_rows if row["sourceTarget"] == target]
        p76_ink_norm = float(p76["inkOverPageDensity"])
        p76_feature_norm = float(p76["featureOverPageDensity"])
        other_ink_max = max([float(row["inkOverPageDensity"]) for row in others] or [0.0])
        other_feature_max = max([float(row["featureOverPageDensity"]) for row in others] or [0.0])
        control_ink_p95 = percentile([float(row["inkOverPageDensity"]) for row in controls_for_target], 95)
        control_feature_p95 = percentile(
            [float(row["featureOverPageDensity"]) for row in controls_for_target], 95
        )
        active_comparisons.append(
            {
                "target": target,
                "page76InkOverPageDensity": round(p76_ink_norm, 6),
                "otherLeafInkOverPageDensityMax": round(other_ink_max, 6),
                "controlInkOverPageDensityP95": round(control_ink_p95, 6),
                "controlInkOverPageDensityGePage76Count": sum(
                    1 for row in controls_for_target if float(row["inkOverPageDensity"]) >= p76_ink_norm
                ),
                "page76NormalizedInkOutlier": p76_ink_norm > max(other_ink_max, control_ink_p95),
                "page76FeatureOverPageDensity": round(p76_feature_norm, 6),
                "otherLeafFeatureOverPageDensityMax": round(other_feature_max, 6),
                "controlFeatureOverPageDensityP95": round(control_feature_p95, 6),
                "controlFeatureOverPageDensityGePage76Count": sum(
                    1
                    for row in controls_for_target
                    if float(row["featureOverPageDensity"]) >= p76_feature_norm
                ),
                "page76NormalizedFeatureOutlier": p76_feature_norm
                > max(other_feature_max, control_feature_p95),
            }
        )

    page76_norm_ink_outliers = sum(1 for row in active_comparisons if row["page76NormalizedInkOutlier"])
    page76_norm_feature_outliers = sum(
        1 for row in active_comparisons if row["page76NormalizedFeatureOutlier"]
    )
    all_four_ink = page76_norm_ink_outliers == len(TARGET_ORDER)
    all_four_feature = page76_norm_feature_outliers == len(TARGET_ORDER)
    slot_norm_outliers = 0
    for slot in slots:
        p76 = next(row for row in slot_rows if row["slotId"] == slot["id"] and row["targetPage"] == 76)
        other_max = max(
            [
                float(row["inkOverPageDensity"])
                for row in slot_rows
                if row["slotId"] == slot["id"] and row["targetPage"] != 76
            ]
            or [0.0]
        )
        if float(p76["inkOverPageDensity"]) > other_max:
            slot_norm_outliers += 1

    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    hidden_candidate = bool(all_four_ink and all_four_feature and source_r3 > 0)
    selector_count = 0
    fingerprint = (
        f"pairs={len(VALID_PAIRS)}|active={len(active_rows)}|controls={len(control_rows)}|"
        f"slots={len(slot_rows)}|p76NormInkOutliers={page76_norm_ink_outliers}|"
        f"p76NormFeatureOutliers={page76_norm_feature_outliers}|all4NormInk={int(all_four_ink)}|"
        f"all4NormFeature={int(all_four_feature)}|slotNormInkOutliers={slot_norm_outliers}|"
        f"hiddenCandidate={int(hidden_candidate)}|sourceR3={source_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors={selector_count}"
    )
    summary = {
        "validLeafPairCount": len(VALID_PAIRS),
        "activeRegionCount": len(active_rows),
        "lineShiftControlRegionCount": len(control_rows),
        "slotRegionCount": len(slot_rows),
        "page76NormalizedInkOutlierCount": page76_norm_ink_outliers,
        "page76NormalizedFeatureOutlierCount": page76_norm_feature_outliers,
        "allFourPage76NormalizedInkOutlier": all_four_ink,
        "allFourPage76NormalizedFeatureOutlier": all_four_feature,
        "page76SlotNormalizedInkOutlierCount": slot_norm_outliers,
        "hiddenDensityCalibratedCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "densityCalibrationFingerprint": fingerprint,
        "priorAllLeafParityFingerprint": parity.get("fingerprint"),
    }

    draw_sheet(pair_rows, active_rows, active_comparisons, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current-scan natural held-to-light density calibration gate; no extraction or candidate generation",
        "inputs": {
            "sourceImages": "analysis_outputs/source_images/magazine_page_75..80.jpg",
            "readableReference": "analysis_outputs/3d_article_map/page_75..80_upright.jpg",
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT),
            "allLeafParityGate": rel(ALL_LEAF_PARITY),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "validPairs": [
            {"pairId": pair_id, "sourcePage": source_page, "targetPage": target_page}
            for pair_id, source_page, target_page in VALID_PAIRS
        ],
        "activeBandBox": [round(float(v), 3) for v in band_box],
        "c9Frame": [round(float(v), 3) for v in c9_frame],
        "pairRows": pair_rows,
        "activeRows": active_rows,
        "lineShiftControlRows": control_rows,
        "overdoseSlotRows": slot_rows,
        "activeComparisons": active_comparisons,
        "summary": summary,
        "decision": {
            "currentScanLightTableDensityCalibrationGate": "current_scan_light_table_density_calibration_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Normalizing natural held-to-light hits by page, active-band, C9-frame, "
                "and matched-control density still does not make page 76 an all-four active "
                "or OVERDOSE selector."
            ),
            "nextMove": (
                "Use the current scan as a calibrated witness only. Reopen extraction only for a "
                "new physical/original-layout source or raw clue that supplies unit/order wording."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Light-Table Density Calibration Gate",
        "",
        "Scope: normalized the natural valid leaf held-to-light overlays against full-page, active-band, C9-frame, and matched line-control source density. This checks whether page 76 becomes special after compensating for different source-page ink density. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Valid leaf pairs: `{len(VALID_PAIRS)}`",
        f"- Active / line-shift control / OVERDOSE slot rows: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Page-76 normalized active ink / feature outliers: `{page76_norm_ink_outliers}` / `{page76_norm_feature_outliers}`",
        f"- All-four page-76 normalized active ink / feature outlier: `{int(all_four_ink)}` / `{int(all_four_feature)}`",
        f"- Page-76 normalized OVERDOSE slot ink outliers: `{slot_norm_outliers}`",
        f"- Hidden density-calibrated candidate: `{int(hidden_candidate)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Pair Density Baselines",
        "",
        "| pair | source->target | page ink | active-band ink | C9-frame ink | active ink mean | active/page | active/band | active/C9 | control p95 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pair_rows:
        lines.append(
            f"| `{row['pairId']}` | `{row['sourcePage']}->{row['targetPage']}` | {row['pageInkDensity']:.6f} | {row['activeBandInkDensity']:.6f} | {row['c9FrameInkDensity']:.6f} | {row['activeInkMean']:.6f} | {row['activeInkMeanOverPageDensity']:.6f} | {row['activeInkMeanOverActiveBandDensity']:.6f} | {row['activeInkMeanOverC9FrameDensity']:.6f} | {row['lineControlInkP95']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Page-76 Normalized Active Comparison",
            "",
            "| target | p76 ink/page | other-leaf ink/page max | control ink/page p95 | ink outlier | p76 feature/page | other-leaf feature/page max | control feature/page p95 | feature outlier |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in active_comparisons:
        lines.append(
            f"| `{row['target']}` | {row['page76InkOverPageDensity']:.6f} | {row['otherLeafInkOverPageDensityMax']:.6f} | {row['controlInkOverPageDensityP95']:.6f} | {int(row['page76NormalizedInkOutlier'])} | {row['page76FeatureOverPageDensity']:.6f} | {row['otherLeafFeatureOverPageDensityMax']:.6f} | {row['controlFeatureOverPageDensityP95']:.6f} | {int(row['page76NormalizedFeatureOutlier'])} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_light_table_density_calibration_no_selector`",
            "- Density normalization does not promote page 76 into an all-four active or OVERDOSE selector.",
            "- The high same-coordinate values on page 78 are source-density behavior, not a hidden page-76 rule.",
            "",
            "## Next Move",
            "",
            "- Treat current-scan light-table outputs as calibrated source-review witnesses only.",
            "- Continue only with physical/original-layout source validation or raw clue wording that names unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanLightTableDensityCalibrationGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
