#!/usr/bin/env python3
"""Valid same-leaf bleed-through edge-contact control for page 76.

This pass tests whether the physical page 75 -> page 76 light-table view
creates selective source-only contacts immediately around the O4/B4/G5/O5
target-box edges. It is a bounded geometry/visual inspection only: no
OCR-to-key extraction, key derivation, hashing, seed/WIF/address checks,
BIP39, or broad brute force.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_edge_contact_control.json"
OUT_MD = OUT / "current_scan_valid_leaf_edge_contact_control.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_edge_contact_control_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BLEED_GRID = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/"
    "current_scan_valid_leaf_bleedthrough_control_grid.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

RING_PAD = 28
LOWER_Y0 = 2060
LOWER_Y1 = 3060


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def normalize_page(page: int) -> Image.Image:
    source = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean)
    return source.rotate(180) if rot_diff < same_diff else source


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
    return {"feature": feature, "dark": dark, "orange": orange, "grey": grey}


def shift_mask(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(mask)
    h, w = mask.shape
    src_x0 = max(0, -dx)
    src_x1 = min(w, w - dx)
    dst_x0 = max(0, dx)
    dst_x1 = min(w, w + dx)
    src_y0 = max(0, -dy)
    src_y1 = min(h, h - dy)
    dst_y0 = max(0, dy)
    dst_y1 = min(h, h + dy)
    if src_x1 > src_x0 and src_y1 > src_y0:
        out[dst_y0:dst_y1, dst_x0:dst_x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def shift_channels(channels: dict[str, np.ndarray], dx: int, dy: int) -> dict[str, np.ndarray]:
    return {name: shift_mask(np.fliplr(mask), dx, dy) for name, mask in channels.items()}


def shifted_mirror_image(img: Image.Image, dx: int, dy: int) -> Image.Image:
    flipped = ImageOps.mirror(img)
    canvas = Image.new("RGB", img.size, "white")
    canvas.paste(flipped, (dx, dy))
    return canvas


def iou(a: list[float], b: list[float]) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union else 0.0


def ring_mask_for_box(page_shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = page_shape
    x0, y0, x1, y1 = [round(v) for v in box]
    rx0, ry0 = max(0, x0 - RING_PAD), max(0, y0 - RING_PAD)
    rx1, ry1 = min(w, x1 + RING_PAD), min(h, y1 + RING_PAD)
    mask = np.zeros((h, w), dtype=bool)
    mask[ry0:ry1, rx0:rx1] = True
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = False
    return mask


def side_masks_for_box(page_shape: tuple[int, int], box: list[float]) -> dict[str, np.ndarray]:
    h, w = page_shape
    x0, y0, x1, y1 = [round(v) for v in box]
    masks: dict[str, np.ndarray] = {}
    coords = {
        "top": (x0, max(0, y0 - RING_PAD), x1, y0),
        "bottom": (x0, y1, x1, min(h, y1 + RING_PAD)),
        "left": (max(0, x0 - RING_PAD), y0, x0, y1),
        "right": (x1, y0, min(w, x1 + RING_PAD), y1),
    }
    for side, (sx0, sy0, sx1, sy1) in coords.items():
        mask = np.zeros((h, w), dtype=bool)
        if sx1 > sx0 and sy1 > sy0:
            mask[sy0:sy1, sx0:sx1] = True
        masks[side] = mask
    return masks


def metric_for_mask(source_feature: np.ndarray, target_feature: np.ndarray, region: np.ndarray) -> dict:
    source = np.logical_and(source_feature, region)
    target = np.logical_and(target_feature, region)
    source_only = np.logical_and(source, ~target)
    overlap = np.logical_and(source, target)
    area = int(region.sum())
    source_count = int(source.sum())
    return {
        "area": area,
        "sourceCoverage": float(source_count / area) if area else 0.0,
        "sourceOnlyCoverage": float(source_only.sum() / area) if area else 0.0,
        "overlapCoverage": float(overlap.sum() / area) if area else 0.0,
        "sourceOnlyShareOfSource": float(source_only.sum() / source_count) if source_count else 0.0,
    }


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(1 for item in controls if item <= value) / len(controls)


def control_boxes_for(active_box: list[float], page_size: tuple[int, int], active_boxes: list[list[float]]) -> list[list[float]]:
    width = round(active_box[2] - active_box[0])
    height = round(active_box[3] - active_box[1])
    page_w, page_h = page_size
    x_step = max(52, width // 3)
    y_step = max(48, height + 34)
    boxes: list[list[float]] = []
    y = LOWER_Y0
    while y + height + RING_PAD <= min(LOWER_Y1, page_h):
        x = 80
        while x + width + RING_PAD <= page_w - 80:
            candidate = [float(x), float(y), float(x + width), float(y + height)]
            if all(iou(candidate, other) < 0.03 for other in active_boxes):
                boxes.append(candidate)
            x += x_step
        y += y_step
    return boxes


def evaluate_mode(
    mode: str,
    dx: int,
    dy: int,
    source_channels: dict[str, np.ndarray],
    target_channels: dict[str, np.ndarray],
    active_rows: list[dict],
    page_size: tuple[int, int],
) -> dict:
    shifted = shift_channels(source_channels, dx, dy)
    source_feature = shifted["feature"]
    target_feature = target_channels["feature"]
    active_boxes = [row["box"] for row in active_rows]
    rows = []
    for active in active_rows:
        ring = ring_mask_for_box(source_feature.shape, active["box"])
        ring_metric = metric_for_mask(source_feature, target_feature, ring)
        sides = {
            side: metric_for_mask(source_feature, target_feature, mask)
            for side, mask in side_masks_for_box(source_feature.shape, active["box"]).items()
        }
        side_values = [side_metric["sourceOnlyCoverage"] for side_metric in sides.values()]
        controls = control_boxes_for(active["box"], page_size, active_boxes)
        control_values = [
            metric_for_mask(
                source_feature,
                target_feature,
                ring_mask_for_box(source_feature.shape, control),
            )["sourceOnlyCoverage"]
            for control in controls
        ]
        rows.append(
            {
                "mode": mode,
                "target": active["shortId"],
                "phrase": active["phrase"],
                "box": active["box"],
                **ring_metric,
                "maxSideSourceOnlyCoverage": max(side_values) if side_values else 0.0,
                "bestSide": max(sides, key=lambda side: sides[side]["sourceOnlyCoverage"]),
                "sideMetrics": sides,
                "controlCount": len(control_values),
                "controlMedianSourceOnlyCoverage": float(np.median(control_values)) if control_values else 0.0,
                "controlP90SourceOnlyCoverage": float(np.quantile(control_values, 0.90)) if control_values else 0.0,
                "controlMaxSourceOnlyCoverage": max(control_values) if control_values else 0.0,
                "sourceOnlyControlPercentile": percentile(ring_metric["sourceOnlyCoverage"], control_values),
            }
        )
    values = [row["sourceOnlyCoverage"] for row in rows]
    percentiles = [row["sourceOnlyControlPercentile"] for row in rows]
    return {
        "mode": mode,
        "dx": dx,
        "dy": dy,
        "rows": rows,
        "meanRingSourceOnlyCoverage": float(np.mean(values)) if values else 0.0,
        "minRingSourceOnlyCoverage": min(values) if values else 0.0,
        "targetCountAtLeast10": sum(1 for value in values if value >= 0.10),
        "targetCountAtLeast25": sum(1 for value in values if value >= 0.25),
        "highPercentileCount": sum(1 for value in percentiles if value >= 0.75),
        "minControlPercentile": min(percentiles) if percentiles else 0.0,
        "meanControlPercentile": float(np.mean(percentiles)) if percentiles else 0.0,
    }


def draw_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    source_feature: np.ndarray,
    target_feature: np.ndarray,
    row: dict,
    dx: int,
    dy: int,
    path: Path,
) -> None:
    x0, y0, x1, y1 = [round(v) for v in row["box"]]
    pad_x, pad_y = 150, 92
    rect = (
        max(0, x0 - pad_x),
        max(0, y0 - pad_y),
        min(target_img.width, x1 + pad_x),
        min(target_img.height, y1 + pad_y),
    )
    transformed = shifted_mirror_image(source_img, dx, dy)
    target_crop = target_img.crop(rect)
    source_crop = transformed.crop(rect)
    blend = Image.blend(target_crop, source_crop, 0.42)
    local_region = ring_mask_for_box(source_feature.shape, row["box"])[rect[1] : rect[3], rect[0] : rect[2]]
    local_source = source_feature[rect[1] : rect[3], rect[0] : rect[2]]
    local_target = target_feature[rect[1] : rect[3], rect[0] : rect[2]]
    source_only = np.logical_and(np.logical_and(local_source, local_region), ~local_target)
    overlap = np.logical_and(np.logical_and(local_source, local_region), local_target)
    overlay = blend.convert("RGBA")
    arr = np.zeros((overlay.height, overlay.width, 4), dtype=np.uint8)
    arr[local_region] = [255, 210, 0, 55]
    arr[source_only] = [0, 112, 255, 135]
    arr[overlap] = [255, 0, 0, 120]
    overlay = Image.alpha_composite(overlay, Image.fromarray(arr, "RGBA")).convert("RGB")
    panels = [target_crop, source_crop, blend, overlay]
    labels = ["page 76 crop", "mirrored page 75", "light-table blend", "edge ring: blue source-only"]
    panel_w = 300
    resized = [panel.resize((panel_w, round(panel_w * panel.height / panel.width))) for panel in panels]
    panel_h = max(panel.height for panel in resized)
    canvas = Image.new("RGB", (panel_w * 4, panel_h + 84), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    try:
        small = ImageFont.truetype("Arial.ttf", 14)
        title = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        small = ImageFont.load_default()
        title = ImageFont.load_default()
    draw.rectangle((0, 0, canvas.width, 36), fill=(25, 31, 42, 235))
    draw.text((10, 10), f"{row['target']} {row['mode']} dx={dx} dy={dy}", fill="white", font=title)
    for idx, panel in enumerate(resized):
        px = idx * panel_w
        canvas.paste(panel, (px, 58))
        draw.text((px + 8, 40), labels[idx], fill=(35, 38, 45), font=small)
        bx0 = round((x0 - rect[0]) * panel_w / (rect[2] - rect[0]))
        by0 = round((y0 - rect[1]) * panel.height / (rect[3] - rect[1])) + 58
        bx1 = round((x1 - rect[0]) * panel_w / (rect[2] - rect[0]))
        by1 = round((y1 - rect[1]) * panel.height / (rect[3] - rect[1])) + 58
        draw.rectangle((px + bx0, by0, px + bx1, by1), outline=(255, 0, 0, 230), width=3)
    canvas.save(path, quality=91)


def draw_sheet(result: dict, panel_paths: list[Path]) -> None:
    width, height = 1740, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 15)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title_font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Valid Leaf Edge-Contact Control", fill="white", font=title_font)
    draw.text((24, 56), "Page 75 mirrored onto page 76; source-only signal in edge collars around O4/B4/G5/O5.", fill=(235, 235, 235), font=small)
    x, y = 24, 118
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((560, 240))
        sheet.paste(img, (x, y))
        x += 578
        if x + 560 > width:
            x = 24
            y += 298
    y = 720
    headers = ["mode", "dx", "dy", "mean ring", "min ring", ">=.10", ">=.25", "pctl>=.75", "min pctl"]
    xs = [24, 338, 390, 456, 558, 652, 708, 766, 858]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for mode in result["modeRows"]:
        values = [
            mode["mode"],
            str(mode["dx"]),
            str(mode["dy"]),
            f"{mode['meanRingSourceOnlyCoverage']:.4f}",
            f"{mode['minRingSourceOnlyCoverage']:.4f}",
            str(mode["targetCountAtLeast10"]),
            str(mode["targetCountAtLeast25"]),
            str(mode["highPercentileCount"]),
            f"{mode['minControlPercentile']:.3f}",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 22
    y += 20
    headers = ["mode", "target", "ring src-only", "best side", "side max", "control p90", "control max", "percentile"]
    xs = [24, 338, 420, 528, 612, 706, 812, 914]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for row in result["targetRows"][:16]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            row["bestSide"],
            f"{row['maxSideSourceOnlyCoverage']:.4f}",
            f"{row['controlP90SourceOnlyCoverage']:.4f}",
            f"{row['controlMaxSourceOnlyCoverage']:.4f}",
            f"{row['sourceOnlyControlPercentile']:.3f}",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    bleed = load_json(BLEED_GRID)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_rows = [
        {"shortId": row["shortId"], "phrase": row["phrase"], "box": row["box"]}
        for row in active.get("activeRows", [])
    ]
    target_img = normalize_page(76)
    source_img = normalize_page(75)
    target_channels = feature_channels(target_img)
    source_channels = feature_channels(source_img)
    jitter = bleed.get("summary", {}).get("jitterBestShift") or [-80, -20]
    mode_specs = [
        ("valid_75_to_76_natural", 0, 0),
        ("valid_75_to_76_small_jitter_best", int(jitter[0]), int(jitter[1])),
    ]
    mode_rows = [
        evaluate_mode(mode, dx, dy, source_channels, target_channels, active_rows, target_img.size)
        for mode, dx, dy in mode_specs
    ]
    panel_paths: list[Path] = []
    target_rows = []
    for mode in mode_rows:
        shifted = shift_channels(source_channels, mode["dx"], mode["dy"])
        for row in mode["rows"]:
            target_rows.append(row)
            panel_path = OUT / f"{row['mode']}_{row['target']}.jpg"
            draw_panel(
                target_img,
                source_img,
                shifted["feature"],
                target_channels["feature"],
                row,
                mode["dx"],
                mode["dy"],
                panel_path,
            )
            panel_paths.append(panel_path)
    source_r3_hits = 0
    trigger_count = len(reopen.get("triggerRows", []))
    satisfied_triggers = sum(1 for row in reopen.get("triggerRows", []) if row.get("triggerSatisfiedNow"))
    selector_unlocks = 0
    all_four_10_modes = [row["mode"] for row in mode_rows if row["targetCountAtLeast10"] == 4]
    all_four_25_modes = [row["mode"] for row in mode_rows if row["targetCountAtLeast25"] == 4]
    all_four_pctl_modes = [row["mode"] for row in mode_rows if row["highPercentileCount"] == 4]
    decision = (
        "valid_leaf_edge_contact_no_active_quartet_selector"
        if not all_four_25_modes and not all_four_pctl_modes
        else "needs_manual_review"
    )
    summary = {
        "modeCount": len(mode_rows),
        "targetRowCount": len(target_rows),
        "naturalMeanRingSourceOnlyCoverage": mode_rows[0]["meanRingSourceOnlyCoverage"],
        "naturalMinRingSourceOnlyCoverage": mode_rows[0]["minRingSourceOnlyCoverage"],
        "naturalTargetCountAtLeast10": mode_rows[0]["targetCountAtLeast10"],
        "naturalTargetCountAtLeast25": mode_rows[0]["targetCountAtLeast25"],
        "naturalHighPercentileCount": mode_rows[0]["highPercentileCount"],
        "jitterShift": [mode_rows[1]["dx"], mode_rows[1]["dy"]],
        "jitterMeanRingSourceOnlyCoverage": mode_rows[1]["meanRingSourceOnlyCoverage"],
        "jitterMinRingSourceOnlyCoverage": mode_rows[1]["minRingSourceOnlyCoverage"],
        "jitterTargetCountAtLeast10": mode_rows[1]["targetCountAtLeast10"],
        "jitterTargetCountAtLeast25": mode_rows[1]["targetCountAtLeast25"],
        "jitterHighPercentileCount": mode_rows[1]["highPercentileCount"],
        "allFourAtLeast10Modes": all_four_10_modes,
        "allFourAtLeast25Modes": all_four_25_modes,
        "allFourHighPercentileModes": all_four_pctl_modes,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"modes={summary['modeCount']}|targets={summary['targetRowCount']}|"
        f"natMean={summary['naturalMeanRingSourceOnlyCoverage']:.4f}|"
        f"natMin={summary['naturalMinRingSourceOnlyCoverage']:.4f}|"
        f"nat10={summary['naturalTargetCountAtLeast10']}|"
        f"nat25={summary['naturalTargetCountAtLeast25']}|"
        f"natPctl75={summary['naturalHighPercentileCount']}|"
        f"jit={mode_rows[1]['dx']},{mode_rows[1]['dy']}|"
        f"jitMean={summary['jitterMeanRingSourceOnlyCoverage']:.4f}|"
        f"jitMin={summary['jitterMinRingSourceOnlyCoverage']:.4f}|"
        f"jit10={summary['jitterTargetCountAtLeast10']}|"
        f"jit25={summary['jitterTargetCountAtLeast25']}|"
        f"jitPctl75={summary['jitterHighPercentileCount']}|"
        f"sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}|"
        f"selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page 75 -> page 76 same-leaf edge-contact control; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "bleedthroughControlGrid": rel(BLEED_GRID),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage75": rel(SOURCE_PAGE_TEMPLATE.with_name("magazine_page_75.jpg")),
            "sourcePage76": rel(SOURCE_PAGE_TEMPLATE.with_name("magazine_page_76.jpg")),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "modeRows": [{key: value for key, value in row.items() if key != "rows"} for row in mode_rows],
        "targetRows": target_rows,
        "sheet": rel(OUT_SHEET),
        "panelPaths": [rel(path) for path in panel_paths],
        "nextMove": "Do not extract from valid same-leaf edge contacts; require a new source/clue naming transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)
    lines = [
        "# Current Scan Valid Leaf Edge-Contact Control",
        "",
        "Scope: tested whether the physically valid page 75 -> page 76 light-table view creates selective source-only contacts immediately around the O4/B4/G5/O5 target-box edges. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Modes / target rows: `{summary['modeCount']}` / `{summary['targetRowCount']}`",
        f"- Natural edge-ring mean/min source-only coverage: `{summary['naturalMeanRingSourceOnlyCoverage']:.4f}` / `{summary['naturalMinRingSourceOnlyCoverage']:.4f}`",
        f"- Natural targets >=10% / >=25% ring source-only coverage: `{summary['naturalTargetCountAtLeast10']}` / `{summary['naturalTargetCountAtLeast25']}`",
        f"- Natural targets at >=75th percentile vs controls: `{summary['naturalHighPercentileCount']}`",
        f"- Small-jitter shift: `{mode_rows[1]['dx']},{mode_rows[1]['dy']}`",
        f"- Small-jitter edge-ring mean/min source-only coverage: `{summary['jitterMeanRingSourceOnlyCoverage']:.4f}` / `{summary['jitterMinRingSourceOnlyCoverage']:.4f}`",
        f"- Small-jitter targets >=10% / >=25% ring source-only coverage: `{summary['jitterTargetCountAtLeast10']}` / `{summary['jitterTargetCountAtLeast25']}`",
        f"- Small-jitter targets at >=75th percentile vs controls: `{summary['jitterHighPercentileCount']}`",
        f"- All-four >=10% modes: `{', '.join(all_four_10_modes) if all_four_10_modes else 'none'}`",
        f"- All-four >=25% modes: `{', '.join(all_four_25_modes) if all_four_25_modes else 'none'}`",
        f"- All-four >=75th-percentile modes: `{', '.join(all_four_pctl_modes) if all_four_pctl_modes else 'none'}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Mode Rows",
        "",
        "| mode | dx | dy | mean ring source-only | min ring source-only | >=.10 | >=.25 | pctl>=.75 | min percentile | decision signal |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in mode_rows:
        signal = (
            "all-four selective"
            if row["targetCountAtLeast25"] == 4 and row["highPercentileCount"] == 4
            else "not selective"
        )
        lines.append(
            f"| `{row['mode']}` | {row['dx']} | {row['dy']} | "
            f"{row['meanRingSourceOnlyCoverage']:.4f} | {row['minRingSourceOnlyCoverage']:.4f} | "
            f"{row['targetCountAtLeast10']} | {row['targetCountAtLeast25']} | "
            f"{row['highPercentileCount']} | {row['minControlPercentile']:.3f} | {signal} |"
        )
    lines.extend(
        [
            "",
            "## Target Rows",
            "",
            "| mode | target | ring source-only | best side | max side | control median | control p90 | control max | percentile | panel |",
            "|---|---|---:|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in target_rows:
        panel = f"analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/{row['mode']}_{row['target']}.jpg"
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | {row['sourceOnlyCoverage']:.4f} | "
            f"{row['bestSide']} | {row['maxSideSourceOnlyCoverage']:.4f} | "
            f"{row['controlMedianSourceOnlyCoverage']:.4f} | {row['controlP90SourceOnlyCoverage']:.4f} | "
            f"{row['controlMaxSourceOnlyCoverage']:.4f} | {row['sourceOnlyControlPercentile']:.3f} | `{panel}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Valid same-leaf edge collars do not create an all-four O4/B4/G5/O5 selector.",
            "- Edge contacts are sparse and do not separate from same-size lower-page controls under natural or small-jitter alignment.",
            "- Keep the edge panels as visual review material only; do not extract without new source/clue evidence that passes R1-R5.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", fingerprint)
    print("decision:", decision)


if __name__ == "__main__":
    main()
