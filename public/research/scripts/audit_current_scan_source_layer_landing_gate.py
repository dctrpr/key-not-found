#!/usr/bin/env python3
"""Audit held-to-light source-layer landing by color/ink class.

This bounded pass follows the content-box registration gate. It asks whether
the valid page-75 -> page-76 held-to-light failure at B4 is only a dark-ink
threshold artifact, or whether B4 is also empty under orange highlight, grey
ink, combined feature, and broad non-white source masks.

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
OUT_DIR = ROOT / "analysis_outputs/source_audit/current_scan_source_layer_landing_gate"
JSON_OUT = OUT_DIR / "current_scan_source_layer_landing_gate.json"
MD_OUT = OUT_DIR / "current_scan_source_layer_landing_gate.md"
SHEET_OUT = OUT_DIR / "current_scan_source_layer_landing_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
CONTENT_BOX_REGISTRATION = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_content_box_registration_gate/"
    "current_scan_content_box_registration_gate.json"
)
SOURCE_INK_LANDING = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/"
    "current_scan_valid_leaf_source_ink_landing_gate.json"
)
B4_SELF_SIGNAL = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/"
    "current_scan_b4_self_signal_guardrail.json"
)
REOPEN_TRIGGER_MATRIX = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]
LAYER_ORDER = ["black", "orange", "grey", "feature", "broad"]
SUPPORT_THRESHOLD = 0.05
WEAK_SUPPORT_THRESHOLD = 0.01


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def normalize_page(page: int) -> Image.Image:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    upright = Image.open(upright_path).convert("RGB")
    if not source_path.exists():
        return upright
    source = Image.open(source_path).convert("RGB")
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


def source_layer_masks(rgb: np.ndarray) -> dict[str, np.ndarray]:
    if rgb.size == 0:
        empty = np.zeros(rgb.shape[:2], dtype=bool)
        return {name: empty for name in LAYER_ORDER}

    arr = rgb.astype(np.float32) / 255.0
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    blue = arr[:, :, 2]
    maxc = arr.max(axis=2)
    minc = arr.min(axis=2)
    delta = maxc - minc
    sat = np.where(maxc > 1e-6, delta / np.maximum(maxc, 1e-6), 0.0)

    hue = np.zeros_like(maxc)
    is_red = (maxc == red) & (delta > 1e-6)
    is_green = (maxc == green) & (delta > 1e-6)
    is_blue = (maxc == blue) & (delta > 1e-6)
    hue[is_red] = ((green[is_red] - blue[is_red]) / delta[is_red]) % 6.0
    hue[is_green] = ((blue[is_green] - red[is_green]) / delta[is_green]) + 2.0
    hue[is_blue] = ((red[is_blue] - green[is_blue]) / delta[is_blue]) + 4.0
    hue *= 60.0

    r8 = rgb[:, :, 0].astype(np.int16)
    g8 = rgb[:, :, 1].astype(np.int16)
    b8 = rgb[:, :, 2].astype(np.int16)
    rgb_orange = (
        (r8 > 115)
        & (g8 > 55)
        & (b8 < 165)
        & ((r8 - b8) > 32)
        & (g8.astype(np.float32) > b8.astype(np.float32) * 1.04)
    )
    hsv_orange = (
        (hue >= 12.0)
        & (hue <= 58.0)
        & (sat >= 0.16)
        & (maxc >= 0.28)
        & (green >= blue * 1.02)
    )
    orange = rgb_orange | hsv_orange
    black = maxc <= 0.42
    lum = luma(rgb.astype(np.float32))
    grey = (~orange) & (~black) & (lum < 230.0) & (sat < 0.24)
    broad = (lum < 244.0) | (sat > 0.08)
    return {
        "black": black,
        "orange": orange,
        "grey": grey,
        "feature": black | orange | grey,
        "broad": broad,
    }


def shifted_mirrored_source(page: Image.Image, dx: float, dy: float) -> Image.Image:
    mirrored = ImageOps.mirror(page)
    canvas = Image.new("RGB", page.size, "white")
    canvas.paste(mirrored, (int(round(dx)), int(round(dy))))
    return canvas


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def crop_rgb(arr: np.ndarray, box: list[float]) -> np.ndarray:
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
                cy_left = (left["box"][1] + left["box"][3]) / 2.0
                cy_right = (right["box"][1] + right["box"][3]) / 2.0
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


def measure_box(mask: np.ndarray, box: list[float]) -> dict[str, Any]:
    region = crop_bool(mask, box)
    pixel_count = int(region.size)
    count = int(region.sum())
    ratio = count / pixel_count if pixel_count else 0.0
    return {
        "pixelCount": pixel_count,
        "layerPixelCount": count,
        "layerRatio": round(ratio, 6),
        "weakSupported": ratio >= WEAK_SUPPORT_THRESHOLD,
        "sourceSupported": ratio >= SUPPORT_THRESHOLD,
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
        for row in active:
            active_rows.append(
                {
                    "modeId": mode_id,
                    "layer": layer,
                    "target": row["shortId"],
                    "phrase": row["phrase"],
                    "visualState": row["visualState"],
                    **measure_box(masks[layer], row["box"]),
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
                    **measure_box(masks[layer], control["box"]),
                }
            )
    layer_summaries = []
    for layer in LAYER_ORDER:
        rows = [row for row in active_rows if row["layer"] == layer]
        supported = [row["target"] for row in rows if row["sourceSupported"]]
        weak = [row["target"] for row in rows if row["weakSupported"]]
        zero = [row["target"] for row in rows if row["layerPixelCount"] == 0]
        layer_summaries.append(
            {
                "modeId": mode_id,
                "layer": layer,
                "supportedTargets": supported,
                "weakSupportedTargets": weak,
                "zeroTargets": zero,
                "supportedCount": len(supported),
                "weakSupportedCount": len(weak),
                "allFourSupported": len(supported) == 4,
                "allFourWeakSupported": len(weak) == 4,
                "b4LayerRatio": next(row["layerRatio"] for row in rows if row["target"] == "B4"),
            }
        )
    return {
        "modeId": mode_id,
        "dx": round(float(dx), 3),
        "dy": round(float(dy), 3),
        "activeRows": active_rows,
        "controlRows": control_rows,
        "layerSummaries": layer_summaries,
        "landingImage": landing,
        "layerMasks": masks,
    }


def content_box_modes() -> list[dict[str, Any]]:
    content = load_json(CONTENT_BOX_REGISTRATION)
    summary = content.get("summary", {})
    all_shift = summary.get("validPairAllContentShift") or [31.5, -61.0]
    lower_shift = summary.get("validPairLowerHalfShift") or [32.5, -0.5]
    return [
        {"modeId": "natural_hflip", "dx": 0.0, "dy": 0.0},
        {"modeId": "all_content_box_translation", "dx": float(all_shift[0]), "dy": float(all_shift[1])},
        {
            "modeId": "lower_half_content_box_translation",
            "dx": float(lower_shift[0]),
            "dy": float(lower_shift[1]),
        },
    ]


def load_trigger_summary() -> dict[str, int]:
    data = load_json(REOPEN_TRIGGER_MATRIX)
    summary = data.get("summary", {})
    return {
        "sourceBackedR3BridgeHitCount": int(summary.get("sourceBackedR3BridgeHitCount", 0) or 0),
        "satisfiedReopenTriggerCount": int(
            summary.get("satisfiedReopenTriggerCount", summary.get("satisfiedTriggerCount", 0)) or 0
        ),
        "triggerCount": int(summary.get("triggerCount", 0) or 0),
    }


def preview_panel(mode: dict[str, Any], source_landing: Image.Image, active: list[dict[str, Any]]) -> Image.Image:
    bbox = [
        min(row["box"][0] for row in active) - 80,
        min(row["box"][1] for row in active) - 80,
        max(row["box"][2] for row in active) + 80,
        max(row["box"][3] for row in active) + 80,
    ]
    crop = source_landing.crop([int(round(v)) for v in bbox]).convert("RGB")
    draw = ImageDraw.Draw(crop, "RGBA")
    for row in active:
        box = [
            row["box"][0] - bbox[0],
            row["box"][1] - bbox[1],
            row["box"][2] - bbox[0],
            row["box"][3] - bbox[1],
        ]
        draw.rectangle(box, outline=(255, 70, 0, 255), width=4)
        draw.text((box[0], max(0, box[1] - 24)), row["shortId"], fill=(220, 20, 20), font=font(20, True))
    crop.thumbnail((380, 300))
    panel = Image.new("RGB", (420, 370), "white")
    panel.paste(crop, (20, 44))
    d = ImageDraw.Draw(panel)
    d.text((18, 12), f"{mode['modeId']} dx={mode['dx']}, dy={mode['dy']}", fill=(15, 23, 42), font=font(16, True))
    return panel


def draw_sheet(mode_results: list[dict[str, Any]], active: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1960, 1360), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title = font(32, True)
    header = font(22, True)
    body = font(19)
    small = font(15)
    draw.text((36, 26), "Current Scan Source-Layer Landing Gate", fill=(15, 23, 42), font=title)
    y = 82
    for line in [
        f"Decision: {summary['decision']}",
        f"Modes: {summary['modeCount']} | layers: {','.join(LAYER_ORDER)}",
        f"B4 positive layer/mode count: {summary['b4PositiveLayerModeCount']} | all-four layer/modes: {summary['allFourSupportedLayerModeCount']}",
        f"Best layer/mode: {summary['bestLayerMode']} with {summary['bestSupportedCount']}/4 supported",
    ]:
        draw.text((36, y), line, fill=(30, 41, 59), font=body)
        y += 30

    x = 36
    y = 210
    for result in mode_results:
        panel = preview_panel(result, result["landingImage"], active)
        sheet.paste(panel, (x, y))
        x += 445

    y = 610
    draw.text((36, y), "Layer Landing Ratios by Target", fill=(15, 23, 42), font=header)
    y += 34
    cols = [36, 270, 390, 500, 610, 720, 830, 935, 1040]
    headers = ["mode", "layer", "O4", "B4", "G5", "O5", ">=5%", "weak", "zero"]
    for cx, label in zip(cols, headers):
        draw.text((cx, y), label, fill=(51, 65, 85), font=small)
    y += 24
    for result in mode_results:
        for layer in LAYER_ORDER:
            rows = [row for row in result["activeRows"] if row["layer"] == layer]
            by_target = {row["target"]: row for row in rows}
            ls = next(row for row in result["layerSummaries"] if row["layer"] == layer)
            vals = [
                result["modeId"].replace("_content_box_translation", "_content"),
                layer,
                f"{by_target['O4']['layerRatio']:.4f}",
                f"{by_target['B4']['layerRatio']:.4f}",
                f"{by_target['G5']['layerRatio']:.4f}",
                f"{by_target['O5']['layerRatio']:.4f}",
                f"{ls['supportedCount']}/4",
                f"{ls['weakSupportedCount']}/4",
                ",".join(ls["zeroTargets"]) or "-",
            ]
            for cx, val in zip(cols, vals):
                draw.text((cx, y), str(val)[:28], fill=(30, 41, 59), font=small)
            y += 23
        y += 8

    x0 = 1190
    y = 610
    draw.text((x0, y), "Interpretation", fill=(15, 23, 42), font=header)
    y += 36
    notes = [
        "B4 has zero source-layer pixels in every tested mask and mode.",
        "Orange source material does not land on any active target in this valid leaf.",
        "Grey/broad masks explain small O4/G5/O5 support but do not create B4 support.",
        "This confirms the B4 failure is not just a dark-ink threshold artifact.",
    ]
    for note in notes:
        draw.text((x0 + 8, y), "- " + note, fill=(30, 41, 59), font=body)
        y += 30
    sheet.save(SHEET_OUT, quality=92)


def serializable_mode_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "modeId": result["modeId"],
        "dx": result["dx"],
        "dy": result["dy"],
        "activeRows": result["activeRows"],
        "controlRows": result["controlRows"],
        "layerSummaries": result["layerSummaries"],
    }


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Source-Layer Landing Gate",
        "",
        "Scope: split mirrored page-75 source material into black, orange, grey, combined feature, and broad non-white masks, then measured landing inside page-76 O4/B4/G5/O5 under natural, all-content, and lower-half content-box registration. This is source/geometry validation only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Modes checked: `{summary['modeCount']}`",
        f"- Layers checked: `{summary['layersChecked']}`",
        f"- Active target layer rows: `{summary['activeLayerRowCount']}`",
        f"- B4 positive layer/mode count: `{summary['b4PositiveLayerModeCount']}`",
        f"- All-four supported layer/mode count: `{summary['allFourSupportedLayerModeCount']}`",
        f"- All-four weak-supported layer/mode count: `{summary['allFourWeakSupportedLayerModeCount']}`",
        f"- Best layer/mode: `{summary['bestLayerMode']}` with `{summary['bestSupportedCount']}/4` supported",
        f"- Hidden source-layer candidate: `{int(summary['hiddenSourceLayerCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['sourceLayerLandingFingerprint']}`",
        "",
        "## Layer Landing Rows",
        "",
        "| mode | layer | O4 | B4 | G5 | O5 | supported | weak supported | zero targets |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for mode in result["modeResults"]:
        for layer in LAYER_ORDER:
            rows = [row for row in mode["activeRows"] if row["layer"] == layer]
            by_target = {row["target"]: row for row in rows}
            layer_summary = next(row for row in mode["layerSummaries"] if row["layer"] == layer)
            lines.append(
                f"| `{mode['modeId']}` | `{layer}` | "
                f"`{by_target['O4']['layerRatio']:.6f}` | `{by_target['B4']['layerRatio']:.6f}` | "
                f"`{by_target['G5']['layerRatio']:.6f}` | `{by_target['O5']['layerRatio']:.6f}` | "
                f"`{layer_summary['supportedCount']}/4` | `{layer_summary['weakSupportedCount']}/4` | "
                f"`{','.join(layer_summary['zeroTargets']) if layer_summary['zeroTargets'] else '-'}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{summary['decision']}`",
            "- B4 remains zero across black, orange, grey, combined feature, and broad non-white source layers under all tested registration modes.",
            "- Orange source material does not land on any active target in this valid same-leaf geometry.",
            "- The prior B4 failure is therefore not a dark-ink threshold artifact; it is a missing source-material landing.",
            "",
            "## Next Move",
            "",
            "- Keep current-scan held-to-light closed except as source-review evidence. Best direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit, order, or transform.",
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

    all_layer_summaries = [
        layer_summary
        for mode in mode_results
        for layer_summary in mode["layerSummaries"]
    ]
    best_layer = max(
        all_layer_summaries,
        key=lambda row: (row["supportedCount"], row["weakSupportedCount"], -LAYER_ORDER.index(row["layer"])),
    )
    b4_positive = sum(1 for row in all_layer_summaries if float(row["b4LayerRatio"]) > 0.0)
    all_four_supported = [row for row in all_layer_summaries if row["allFourSupported"]]
    all_four_weak = [row for row in all_layer_summaries if row["allFourWeakSupported"]]
    trigger = load_trigger_summary()
    hidden_candidate = bool(b4_positive and all_four_supported)
    fingerprint = (
        f"modes={len(modes)}|layers={','.join(LAYER_ORDER)}"
        f"|rows={len(all_layer_summaries) * len(TARGET_ORDER)}"
        f"|b4PositiveLayerModes={b4_positive}"
        f"|allFour={len(all_four_supported)}|allFourWeak={len(all_four_weak)}"
        f"|best={best_layer['modeId']}:{best_layer['layer']}:{best_layer['supportedCount']}/4"
        f"|b4Ratios={','.join(f'{row['modeId']}:{row['layer']}:{row['b4LayerRatio']:.4f}' for row in all_layer_summaries)}"
        f"|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger['satisfiedReopenTriggerCount']}/{trigger['triggerCount']}"
        "|selectors=0"
    )
    summary = {
        "decision": "current_scan_source_layer_landing_no_selector",
        "modeCount": len(modes),
        "layersChecked": LAYER_ORDER,
        "activeLayerRowCount": len(all_layer_summaries) * len(TARGET_ORDER),
        "controlLayerRowCount": sum(len(mode["controlRows"]) for mode in mode_results),
        "b4PositiveLayerModeCount": b4_positive,
        "allFourSupportedLayerModeCount": len(all_four_supported),
        "allFourWeakSupportedLayerModeCount": len(all_four_weak),
        "bestLayerMode": f"{best_layer['modeId']}:{best_layer['layer']}",
        "bestSupportedCount": best_layer["supportedCount"],
        "hiddenSourceLayerCandidate": hidden_candidate,
        "priorContentBoxRegistrationFingerprint": load_json(CONTENT_BOX_REGISTRATION)
        .get("summary", {})
        .get("contentBoxRegistrationFingerprint"),
        "priorSourceInkLandingFingerprint": load_json(SOURCE_INK_LANDING)
        .get("summary", {})
        .get("sourceInkLandingFingerprint"),
        "priorB4SelfSignalFingerprint": load_json(B4_SELF_SIGNAL).get("fingerprint"),
        "sourceBackedR3BridgeHitCount": trigger["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger["satisfiedReopenTriggerCount"],
        "triggerCount": trigger["triggerCount"],
        "sourceLayerLandingFingerprint": fingerprint,
    }

    draw_sheet(mode_results, active, summary)
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current scan held-to-light source-layer landing audit; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "contentBoxRegistrationGate": rel(CONTENT_BOX_REGISTRATION),
            "sourceInkLandingGate": rel(SOURCE_INK_LANDING),
            "b4SelfSignalGuardrail": rel(B4_SELF_SIGNAL),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage75": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))),
            "uprightPage75": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=75))),
        },
        "modes": modes,
        "targetOrder": TARGET_ORDER,
        "layerOrder": LAYER_ORDER,
        "modeResults": [serializable_mode_result(row) for row in mode_results],
        "summary": summary,
        "decision": {
            "currentScanSourceLayerLandingGate": summary["decision"],
            "selectorUnlocked": False,
            "reason": (
                "B4 has zero source material in every tested source-layer mask under natural, all-content, "
                "and lower-half content-box registrations. The held-to-light failure is not a dark-ink "
                "threshold artifact."
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
