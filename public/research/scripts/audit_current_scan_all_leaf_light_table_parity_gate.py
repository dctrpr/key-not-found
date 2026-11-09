#!/usr/bin/env python3
"""Check all valid current-scan leaf pairs under natural held-to-light parity.

This bounded pass uses the existing PDF/source page images only. It normalizes
pages to readable/upright coordinates, horizontally mirrors each odd back page
over its even target page, and compares the same active boxes and OVERDOSE slot
columns across 75->76, 77->78, and 79->80.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_all_leaf_light_table_parity_gate.json"
OUT_MD = OUT / "current_scan_all_leaf_light_table_parity_gate.md"
OUT_SHEET = OUT / "current_scan_all_leaf_light_table_parity_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
VALID_LEAF_SOURCE_INK = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/"
    "current_scan_valid_leaf_source_ink_landing_gate.json"
)
ALL_LEAF_IMPOSITION = ROOT / (
    "analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate/"
    "current_pdf_all_leaf_imposition_consistency_gate.json"
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
    source = Image.open(source_path).convert("RGB")
    upright = Image.open(upright_path).convert("RGB")
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


def feature_channels(img: Image.Image) -> dict[str, np.ndarray]:
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
    return {
        "ink": ink,
        "feature": feature,
        "dark": dark,
        "orange": orange,
        "grey": grey,
    }


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


def overdose_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [])]
    projections = c9.get("projections", [])
    if len(frame) != 4 or not projections:
        return []
    slots = projections[0].get("slots", [])
    rows = []
    for slot in slots:
        rows.append(
            {
                "id": f"slot_{slot['index']}_{slot['letter']}",
                "slotIndex": int(slot["index"]),
                "letter": slot["letter"],
                "box": [
                    float(slot["left"]),
                    frame[1],
                    float(slot["right"]),
                    frame[3],
                ],
            }
        )
    return rows


def measure_region(channels: dict[str, np.ndarray], box: list[float]) -> dict[str, Any]:
    pixel_count = int(crop_bool(channels["ink"], box).size)
    metrics: dict[str, Any] = {"box": [round(float(v), 3) for v in box], "pixelCount": pixel_count}
    for name in ["ink", "feature", "dark", "orange", "grey"]:
        crop = crop_bool(channels[name], box)
        count = int(crop.sum())
        ratio = count / pixel_count if pixel_count else 0.0
        metrics[f"source{name.title()}PixelCount"] = count
        metrics[f"source{name.title()}Ratio"] = round(float(ratio), 6)
    return metrics


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(values, q)) if values else 0.0


def save_pair_overlay(
    pair_id: str,
    source_page: int,
    target_page: int,
    target: Image.Image,
    mirrored_source: Image.Image,
    active: list[dict[str, Any]],
    slots: list[dict[str, Any]],
) -> Path:
    blend = Image.blend(target.convert("RGB"), mirrored_source.convert("RGB"), 0.42)
    out_w = 620
    out_h = round(out_w * blend.height / blend.width)
    preview = blend.resize((out_w, out_h))
    draw = ImageDraw.Draw(preview, "RGBA")
    sx = out_w / blend.width
    sy = out_h / blend.height
    for slot in slots:
        x0, y0, x1, y1 = [v for v in slot["box"]]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        draw.rectangle(rect, outline=(15, 90, 180, 120), width=1)
        draw.text((rect[0] + 3, rect[1] + 4), slot["letter"], fill=(15, 90, 180, 190), font=font(12))
    for row in active:
        color = (255, 130, 0, 240) if row["visualState"] == "Y" else (25, 25, 25, 240)
        x0, y0, x1, y1 = [v for v in row["box"]]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        draw.rectangle(rect, outline=color, width=3)
        draw.rectangle((rect[0], max(0, rect[1] - 20), rect[0] + 44, rect[1]), fill=(255, 255, 255, 210))
        draw.text((rect[0] + 3, max(0, rect[1] - 18)), row["shortId"], fill=color, font=font(13))
    draw.rectangle((0, 0, out_w, 38), fill=(20, 27, 38, 210))
    draw.text(
        (10, 10),
        f"{pair_id}: mirrored p{source_page} over p{target_page}, no shift",
        fill=(255, 255, 255, 255),
        font=font(15),
    )
    path = OUT / f"{pair_id}_natural_light_table_overlay.jpg"
    preview.convert("RGB").save(path, quality=92)
    return path


def draw_sheet(
    overlay_paths: list[Path],
    active_pair_rows: list[dict[str, Any]],
    active_comparisons: list[dict[str, Any]],
    slot_summary: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    sheet = Image.new("RGB", (1900, 1360), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 1900, 104), fill=(24, 31, 42))
    draw.text((24, 16), "All-Leaf Light-Table Parity Gate", fill="white", font=font(25))
    draw.text(
        (24, 54),
        "Natural odd-page mirror over even target for 75->76, 77->78, 79->80. Same active boxes and OVERDOSE slots are used as parity controls.",
        fill=(235, 235, 235),
        font=font(14),
    )
    draw.text(
        (1220, 20),
        f"active ink/feature outliers: {summary['page76ActiveInkOutlierCount']}/{summary['page76ActiveFeatureOutlierCount']}",
        fill=(235, 235, 235),
        font=font(14),
    )
    draw.text(
        (1220, 50),
        f"all-four ink/feature: {int(summary['allFourPage76InkOutlier'])}/{int(summary['allFourPage76FeatureOutlier'])}",
        fill=(235, 235, 235),
        font=font(14),
    )

    x = 24
    for path in overlay_paths:
        img = Image.open(path).convert("RGB").resize((430, 552))
        sheet.paste(img, (x, 132))
        x += 458

    y = 730
    draw.text((24, y), "Same-coordinate active boxes across valid leaf pairs", fill=(30, 34, 40), font=font(14))
    y += 24
    headers = ["pair", "target", "O4 ink", "B4 ink", "G5 ink", "O5 ink", "O4 feat", "B4 feat", "G5 feat", "O5 feat"]
    xs = [24, 180, 260, 350, 440, 530, 640, 730, 820, 910]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for pair_id, _, target_page in VALID_PAIRS:
        pair_rows = [row for row in active_pair_rows if row["pairId"] == pair_id]
        by_target = {row["target"]: row for row in pair_rows}
        values = [pair_id, str(target_page)]
        values.extend(f"{by_target[t]['sourceInkRatio']:.4f}" for t in TARGET_ORDER)
        values.extend(f"{by_target[t]['sourceFeatureRatio']:.4f}" for t in TARGET_ORDER)
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(25, 28, 34), font=font(11))
        y += 20

    y += 28
    draw.text((24, y), "Page-76 active-vs-control parity", fill=(30, 34, 40), font=font(14))
    y += 24
    headers = ["target", "p76 ink", "other max", "line p95", "ink out", "p76 feat", "other max", "line p95", "feat out"]
    xs = [24, 100, 188, 282, 374, 470, 564, 658, 754]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for row in active_comparisons:
        values = [
            row["target"],
            f"{row['page76InkRatio']:.4f}",
            f"{row['otherLeafInkMax']:.4f}",
            f"{row['lineControlInkP95']:.4f}",
            str(int(row["page76InkOutlier"])),
            f"{row['page76FeatureRatio']:.4f}",
            f"{row['otherLeafFeatureMax']:.4f}",
            f"{row['lineControlFeatureP95']:.4f}",
            str(int(row["page76FeatureOutlier"])),
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(25, 28, 34), font=font(11))
        y += 20

    y += 28
    notes = [
        f"OVERDOSE page-76 slot ink/feature outliers: {slot_summary['page76SlotInkOutlierCount']}/{slot_summary['page76SlotFeatureOutlierCount']}.",
        f"Line-shift controls across all leaves: {summary['lineShiftControlRegionCount']}; slot rows: {summary['slotRegionCount']}.",
        "Selector stays locked because page 76 does not produce an all-four active outlier under natural all-leaf parity, and source-backed R3 remains zero.",
    ]
    for note in notes:
        draw.text((24, y), "- " + note, fill=(25, 28, 34), font=font(14))
        y += 24
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    prior_valid_leaf = load_json(VALID_LEAF_SOURCE_INK)
    prior_imposition = load_json(ALL_LEAF_IMPOSITION)

    active = active_boxes(active_index)
    page_size = normalize_page(76).size
    pitch = estimated_line_pitch(active)
    controls = control_boxes(active, page_size, pitch)
    slots = overdose_slot_boxes(c9)

    overlay_paths: list[Path] = []
    region_rows: list[dict[str, Any]] = []
    for pair_id, source_page, target_page in VALID_PAIRS:
        target = normalize_page(target_page)
        source = normalize_page(source_page)
        mirrored_source = ImageOps.mirror(source)
        channels = feature_channels(mirrored_source)
        overlay_paths.append(
            save_pair_overlay(pair_id, source_page, target_page, target, mirrored_source, active, slots)
        )
        for row in active:
            region_rows.append(
                {
                    "pairId": pair_id,
                    "sourcePage": source_page,
                    "targetPage": target_page,
                    "role": "active_same_coordinate",
                    "target": row["shortId"],
                    "phrase": row["phrase"],
                    "visualState": row["visualState"],
                    **measure_region(channels, row["box"]),
                }
            )
        for control in controls:
            region_rows.append(
                {
                    "pairId": pair_id,
                    "sourcePage": source_page,
                    "targetPage": target_page,
                    "role": "line_shift_control",
                    "controlId": control["id"],
                    "sourceTarget": control["sourceTarget"],
                    "lineOffset": control["lineOffset"],
                    **measure_region(channels, control["box"]),
                }
            )
        for slot in slots:
            region_rows.append(
                {
                    "pairId": pair_id,
                    "sourcePage": source_page,
                    "targetPage": target_page,
                    "role": "overdose_slot",
                    "slotId": slot["id"],
                    "slotIndex": slot["slotIndex"],
                    "letter": slot["letter"],
                    **measure_region(channels, slot["box"]),
                }
            )

    active_rows = [row for row in region_rows if row["role"] == "active_same_coordinate"]
    control_rows = [row for row in region_rows if row["role"] == "line_shift_control"]
    slot_rows = [row for row in region_rows if row["role"] == "overdose_slot"]

    active_comparisons: list[dict[str, Any]] = []
    for target in TARGET_ORDER:
        page76_row = next(
            row for row in active_rows if row["target"] == target and row["targetPage"] == 76
        )
        other_rows = [row for row in active_rows if row["target"] == target and row["targetPage"] != 76]
        matched_controls = [row for row in control_rows if row["sourceTarget"] == target]
        line_ink_p95 = percentile([float(row["sourceInkRatio"]) for row in matched_controls], 95)
        line_feature_p95 = percentile([float(row["sourceFeatureRatio"]) for row in matched_controls], 95)
        other_ink_max = max([float(row["sourceInkRatio"]) for row in other_rows] or [0.0])
        other_feature_max = max([float(row["sourceFeatureRatio"]) for row in other_rows] or [0.0])
        page76_ink = float(page76_row["sourceInkRatio"])
        page76_feature = float(page76_row["sourceFeatureRatio"])
        active_comparisons.append(
            {
                "target": target,
                "phrase": page76_row["phrase"],
                "page76InkRatio": round(page76_ink, 6),
                "otherLeafInkMax": round(other_ink_max, 6),
                "lineControlInkP95": round(line_ink_p95, 6),
                "lineControlInkGePage76Count": sum(
                    1 for row in matched_controls if float(row["sourceInkRatio"]) >= page76_ink
                ),
                "page76InkOutlier": page76_ink > max(other_ink_max, line_ink_p95),
                "page76FeatureRatio": round(page76_feature, 6),
                "otherLeafFeatureMax": round(other_feature_max, 6),
                "lineControlFeatureP95": round(line_feature_p95, 6),
                "lineControlFeatureGePage76Count": sum(
                    1 for row in matched_controls if float(row["sourceFeatureRatio"]) >= page76_feature
                ),
                "page76FeatureOutlier": page76_feature > max(other_feature_max, line_feature_p95),
            }
        )

    slot_comparisons: list[dict[str, Any]] = []
    for slot in slots:
        page76_row = next(
            row for row in slot_rows if row["slotId"] == slot["id"] and row["targetPage"] == 76
        )
        other_rows = [row for row in slot_rows if row["slotId"] == slot["id"] and row["targetPage"] != 76]
        other_ink_max = max([float(row["sourceInkRatio"]) for row in other_rows] or [0.0])
        other_feature_max = max([float(row["sourceFeatureRatio"]) for row in other_rows] or [0.0])
        page76_ink = float(page76_row["sourceInkRatio"])
        page76_feature = float(page76_row["sourceFeatureRatio"])
        slot_comparisons.append(
            {
                "slotId": slot["id"],
                "slotIndex": slot["slotIndex"],
                "letter": slot["letter"],
                "page76InkRatio": round(page76_ink, 6),
                "otherLeafInkMax": round(other_ink_max, 6),
                "page76InkOutlier": page76_ink > other_ink_max,
                "page76FeatureRatio": round(page76_feature, 6),
                "otherLeafFeatureMax": round(other_feature_max, 6),
                "page76FeatureOutlier": page76_feature > other_feature_max,
            }
        )

    active_ink_outliers = sum(1 for row in active_comparisons if row["page76InkOutlier"])
    active_feature_outliers = sum(1 for row in active_comparisons if row["page76FeatureOutlier"])
    slot_ink_outliers = sum(1 for row in slot_comparisons if row["page76InkOutlier"])
    slot_feature_outliers = sum(1 for row in slot_comparisons if row["page76FeatureOutlier"])
    all_four_ink = active_ink_outliers == len(TARGET_ORDER)
    all_four_feature = active_feature_outliers == len(TARGET_ORDER)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    selector_count = 0
    hidden_candidate = bool(all_four_ink and all_four_feature and source_r3 > 0)

    fingerprint = (
        f"pairs={len(VALID_PAIRS)}|activeRows={len(active_rows)}|slots={len(slot_rows)}|"
        f"controls={len(control_rows)}|p76ActiveInkOutliers={active_ink_outliers}|"
        f"p76ActiveFeatureOutliers={active_feature_outliers}|all4Ink={int(all_four_ink)}|"
        f"all4Feature={int(all_four_feature)}|slotInkOutliers={slot_ink_outliers}|"
        f"slotFeatureOutliers={slot_feature_outliers}|hiddenCandidate={int(hidden_candidate)}|"
        f"sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors={selector_count}"
    )

    slot_summary = {
        "page76SlotInkOutlierCount": slot_ink_outliers,
        "page76SlotFeatureOutlierCount": slot_feature_outliers,
        "slotComparisonCount": len(slot_comparisons),
    }
    summary = {
        "validLeafPairCount": len(VALID_PAIRS),
        "activeRegionCount": len(active_rows),
        "page76ActiveRegionCount": len(TARGET_ORDER),
        "lineShiftControlRegionCount": len(control_rows),
        "slotRegionCount": len(slot_rows),
        "page76SlotRegionCount": len(slots),
        "estimatedLinePitchPx": round(pitch, 6),
        "sourceInkLumaThreshold": INK_LUMA_THRESHOLD,
        "page76ActiveInkOutlierCount": active_ink_outliers,
        "page76ActiveFeatureOutlierCount": active_feature_outliers,
        "allFourPage76InkOutlier": all_four_ink,
        "allFourPage76FeatureOutlier": all_four_feature,
        "page76SlotInkOutlierCount": slot_ink_outliers,
        "page76SlotFeatureOutlierCount": slot_feature_outliers,
        "hiddenAllLeafLightTableCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "allLeafLightTableParityFingerprint": fingerprint,
        "priorValidLeafSourceInkFingerprint": prior_valid_leaf.get("fingerprint"),
        "priorAllLeafImpositionFingerprint": prior_imposition.get("fingerprint"),
    }

    draw_sheet(overlay_paths, active_rows, active_comparisons, slot_summary, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current-scan all valid leaf held-to-light parity gate; no extraction or candidate generation",
        "inputs": {
            "sourceImages": "analysis_outputs/source_images/magazine_page_75..80.jpg",
            "readableReference": "analysis_outputs/3d_article_map/page_75..80_upright.jpg",
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT),
            "validLeafSourceInkLandingGate": rel(VALID_LEAF_SOURCE_INK),
            "allLeafImpositionConsistencyGate": rel(ALL_LEAF_IMPOSITION),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "orientation": "PDF-extracted source_images are rotated 180 degrees into readable/upright coordinates, then odd source pages are horizontally mirrored over even target pages with dx=0, dy=0.",
        "validPairs": [
            {"pairId": pair_id, "sourcePage": source_page, "targetPage": target_page, "dx": 0, "dy": 0}
            for pair_id, source_page, target_page in VALID_PAIRS
        ],
        "activeBoxes": active,
        "lineShiftControls": controls,
        "overdoseSlotBoxes": slots,
        "activeRows": active_rows,
        "lineShiftControlRows": control_rows,
        "overdoseSlotRows": slot_rows,
        "activeComparisons": active_comparisons,
        "slotComparisons": slot_comparisons,
        "summary": summary,
        "decision": {
            "currentScanAllLeafLightTableParityGate": "current_scan_all_leaf_light_table_parity_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Natural all-leaf held-to-light parity does not make the page-76 active quartet "
                "an all-four outlier. Same-coordinate neighboring leaf pairs and matched line-shift "
                "controls absorb the apparent source-layer behavior."
            ),
            "nextMove": (
                "Stop treating the current scan's natural held-to-light overlay as a selector unless "
                "a new physical/original-layout source or raw clue supplies the missing unit/order."
            ),
        },
        "overlays": [rel(path) for path in overlay_paths],
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan All-Leaf Light-Table Parity Gate",
        "",
        "Scope: compared natural held-to-light overlays for valid current-scan leaf pairs `75->76`, `77->78`, and `79->80`. Each odd source page was normalized to readable/upright coordinates, horizontally mirrored, and overlaid on its even target page with no translation search. The same O4/B4/G5/O5 boxes, matched line-shift controls, and C9/OVERDOSE slot columns were measured. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Valid leaf pairs: `{len(VALID_PAIRS)}`",
        f"- Active same-coordinate rows / line-shift controls / OVERDOSE slot rows: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Page-76 active ink / feature outliers: `{active_ink_outliers}` / `{active_feature_outliers}`",
        f"- All-four page-76 active ink / feature outlier: `{int(all_four_ink)}` / `{int(all_four_feature)}`",
        f"- Page-76 OVERDOSE slot ink / feature outliers: `{slot_ink_outliers}` / `{slot_feature_outliers}`",
        f"- Hidden all-leaf light-table candidate: `{int(hidden_candidate)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Active Same-Coordinate Rows",
        "",
        "| pair | target page | target | source ink | source feature | dark | orange | grey |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in active_rows:
        lines.append(
            f"| `{row['pairId']}` | {row['targetPage']} | `{row['target']}` | {row['sourceInkRatio']:.6f} | {row['sourceFeatureRatio']:.6f} | {row['sourceDarkRatio']:.6f} | {row['sourceOrangeRatio']:.6f} | {row['sourceGreyRatio']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Page-76 Active Parity Comparison",
            "",
            "| target | p76 ink | other-leaf ink max | line-control ink p95 | ink outlier | p76 feature | other-leaf feature max | line-control feature p95 | feature outlier |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in active_comparisons:
        lines.append(
            f"| `{row['target']}` | {row['page76InkRatio']:.6f} | {row['otherLeafInkMax']:.6f} | {row['lineControlInkP95']:.6f} | {int(row['page76InkOutlier'])} | {row['page76FeatureRatio']:.6f} | {row['otherLeafFeatureMax']:.6f} | {row['lineControlFeatureP95']:.6f} | {int(row['page76FeatureOutlier'])} |"
        )
    lines.extend(
        [
            "",
            "## OVERDOSE Slot Parity",
            "",
            "| slot | letter | p76 ink | other-leaf ink max | ink outlier | p76 feature | other-leaf feature max | feature outlier |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in slot_comparisons:
        lines.append(
            f"| `{row['slotIndex']}` | `{row['letter']}` | {row['page76InkRatio']:.6f} | {row['otherLeafInkMax']:.6f} | {int(row['page76InkOutlier'])} | {row['page76FeatureRatio']:.6f} | {row['otherLeafFeatureMax']:.6f} | {int(row['page76FeatureOutlier'])} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_all_leaf_light_table_parity_no_selector`",
            "- Natural all-leaf held-to-light parity does not make O4/B4/G5/O5 an all-four page-76 outlier.",
            "- The current scan remains useful as a source-review witness, but it still does not provide a source-backed unit/order rule.",
            "",
            "## Next Move",
            "",
            "- Continue only with physical/original-layout source validation or raw clue wording that names a unit, order, or transform.",
            "- Do not run more current-scan held-to-light extraction variants without new source evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanAllLeafLightTableParityGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
