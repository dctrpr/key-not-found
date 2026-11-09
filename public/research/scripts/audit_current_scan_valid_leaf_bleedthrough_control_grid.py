#!/usr/bin/env python3
"""Valid same-leaf bleed-through control grid for page 76.

This pass uses the current PDF/scan page images as source material and tests
the physically valid page 75 -> page 76 held-to-light model. It measures
source-only bleed-through signal inside O4/B4/G5/O5 and ranks those boxes
against same-size lower-page control boxes. It does not derive candidates,
hash, OCR-to-key, seed, WIF, address, or run any broad search.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_bleedthrough_control_grid.json"
OUT_MD = OUT / "current_scan_valid_leaf_bleedthrough_control_grid.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_bleedthrough_control_grid_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

SMALL_JITTER_RANGE = range(-80, 81, 20)
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


def box_slices(box: list[float]) -> tuple[slice, slice]:
    x0, y0, x1, y1 = [round(v) for v in box]
    return slice(y0, y1), slice(x0, x1)


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


def box_stats(
    source_channels: dict[str, np.ndarray],
    target_channels: dict[str, np.ndarray],
    box: list[float],
) -> dict:
    y_slice, x_slice = box_slices(box)
    source = source_channels["feature"][y_slice, x_slice]
    target = target_channels["feature"][y_slice, x_slice]
    source_only = np.logical_and(source, ~target)
    overlap = np.logical_and(source, target)
    area = source.size
    source_count = int(source.sum())
    if source_count:
        orange_share = float(np.logical_and(source_channels["orange"][y_slice, x_slice], source).sum() / source_count)
        dark_share = float(np.logical_and(source_channels["dark"][y_slice, x_slice], source).sum() / source_count)
        grey_share = float(np.logical_and(source_channels["grey"][y_slice, x_slice], source).sum() / source_count)
    else:
        orange_share = dark_share = grey_share = 0.0
    return {
        "sourceCoverage": float(source.mean()) if area else 0.0,
        "targetCoverage": float(target.mean()) if area else 0.0,
        "sourceOnlyCoverage": float(source_only.mean()) if area else 0.0,
        "sourceTargetOverlapCoverage": float(overlap.mean()) if area else 0.0,
        "sourceOnlyShareOfSource": float(source_only.sum() / source_count) if source_count else 0.0,
        "orangeShareOfSource": orange_share,
        "darkShareOfSource": dark_share,
        "greyShareOfSource": grey_share,
    }


def control_boxes_for(active_box: list[float], page_size: tuple[int, int], active_boxes: list[list[float]]) -> list[list[float]]:
    width = round(active_box[2] - active_box[0])
    height = round(active_box[3] - active_box[1])
    page_w, page_h = page_size
    x_step = max(48, width // 3)
    y_step = max(34, height + 22)
    boxes: list[list[float]] = []
    y = LOWER_Y0
    while y + height <= min(LOWER_Y1, page_h):
        x = 80
        while x + width <= page_w - 80:
            candidate = [float(x), float(y), float(x + width), float(y + height)]
            if all(iou(candidate, other) < 0.03 for other in active_boxes):
                boxes.append(candidate)
            x += x_step
        y += y_step
    return boxes


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(1 for item in controls if item <= value) / len(controls)


def dominant_source_label(row: dict) -> str:
    if row.get("sourceCoverage", 0.0) <= 0:
        return "none"
    return max(
        ["orangeShareOfSource", "darkShareOfSource", "greyShareOfSource"],
        key=lambda key: row[key],
    ).replace("ShareOfSource", "")


def evaluate_mode(
    mode_id: str,
    dx: int,
    dy: int,
    source_channels_75: dict[str, np.ndarray],
    target_channels_76: dict[str, np.ndarray],
    active_rows: list[dict],
    page_size: tuple[int, int],
) -> dict:
    source_shifted = shift_channels(source_channels_75, dx, dy)
    active_boxes = [row["box"] for row in active_rows]
    rows = []
    control_counts = []
    source_only_values = []
    percentiles = []
    for row in active_rows:
        stats = box_stats(source_shifted, target_channels_76, row["box"])
        controls = control_boxes_for(row["box"], page_size, active_boxes)
        control_values = [
            box_stats(source_shifted, target_channels_76, control)["sourceOnlyCoverage"]
            for control in controls
        ]
        active_percentile = percentile(stats["sourceOnlyCoverage"], control_values)
        rows.append(
            {
                "mode": mode_id,
                "target": row["shortId"],
                "phrase": row["phrase"],
                "box": row["box"],
                **stats,
                "controlCount": len(control_values),
                "controlMedianSourceOnlyCoverage": float(np.median(control_values)) if control_values else 0.0,
                "controlP90SourceOnlyCoverage": float(np.quantile(control_values, 0.90)) if control_values else 0.0,
                "controlMaxSourceOnlyCoverage": max(control_values) if control_values else 0.0,
                "sourceOnlyControlPercentile": active_percentile,
            }
        )
        control_counts.append(len(control_values))
        source_only_values.append(stats["sourceOnlyCoverage"])
        percentiles.append(active_percentile)
    all_above_10 = sum(1 for value in source_only_values if value >= 0.10)
    all_above_25 = sum(1 for value in source_only_values if value >= 0.25)
    high_percentile_count = sum(1 for value in percentiles if value >= 0.75)
    return {
        "mode": mode_id,
        "dx": dx,
        "dy": dy,
        "rows": rows,
        "meanSourceOnlyCoverage": float(np.mean(source_only_values)) if source_only_values else 0.0,
        "minSourceOnlyCoverage": min(source_only_values) if source_only_values else 0.0,
        "allFourAtLeast10": all_above_10 == 4,
        "allFourAtLeast25": all_above_25 == 4,
        "targetCountAtLeast10": all_above_10,
        "targetCountAtLeast25": all_above_25,
        "highPercentileCount": high_percentile_count,
        "minControlPercentile": min(percentiles) if percentiles else 0.0,
        "meanControlPercentile": float(np.mean(percentiles)) if percentiles else 0.0,
        "controlCounts": control_counts,
    }


def choose_small_jitter(
    source_channels_75: dict[str, np.ndarray],
    target_channels_76: dict[str, np.ndarray],
    active_rows: list[dict],
    page_size: tuple[int, int],
) -> dict:
    best = None
    for dx in SMALL_JITTER_RANGE:
        for dy in SMALL_JITTER_RANGE:
            result = evaluate_mode(
                "valid_75_to_76_small_jitter_best",
                dx,
                dy,
                source_channels_75,
                target_channels_76,
                active_rows,
                page_size,
            )
            score = (
                result["targetCountAtLeast10"],
                result["highPercentileCount"],
                result["meanSourceOnlyCoverage"],
                result["minSourceOnlyCoverage"],
            )
            if best is None or score > best["score"]:
                best = {"score": score, "result": result}
    return best["result"]


def crop_panel(
    target_img: Image.Image,
    source_img_75: Image.Image,
    source_channels: dict[str, np.ndarray],
    target_channels: dict[str, np.ndarray],
    row: dict,
    dx: int,
    dy: int,
    path: Path,
) -> None:
    pad_x, pad_y = 160, 95
    x0, y0, x1, y1 = [round(v) for v in row["box"]]
    rect = (
        max(0, x0 - pad_x),
        max(0, y0 - pad_y),
        min(target_img.width, x1 + pad_x),
        min(target_img.height, y1 + pad_y),
    )
    source_transformed = shifted_mirror_image(source_img_75, dx, dy)
    target_crop = target_img.crop(rect)
    source_crop = source_transformed.crop(rect)
    blend = Image.blend(target_crop, source_crop, 0.42)

    shifted_channels = shift_channels(source_channels, dx, dy)
    source = shifted_channels["feature"][rect[1] : rect[3], rect[0] : rect[2]]
    target = target_channels["feature"][rect[1] : rect[3], rect[0] : rect[2]]
    source_only = np.logical_and(source, ~target)
    overlay = blend.convert("RGBA")
    overlay_layer = np.zeros((overlay.height, overlay.width, 4), dtype=np.uint8)
    overlay_layer[source_only] = [0, 112, 255, 115]
    overlay_layer[np.logical_and(source, target)] = [255, 0, 0, 120]
    overlay = Image.alpha_composite(overlay, Image.fromarray(overlay_layer, "RGBA")).convert("RGB")

    panels = [target_crop, source_crop, blend, overlay]
    labels = ["page 76", "mirrored page 75", "light-table blend", "blue source-only / red overlap"]
    target_w = 300
    resized = []
    for panel in panels:
        resized.append(panel.resize((target_w, round(target_w * panel.height / panel.width))))
    panel_h = max(img.height for img in resized)
    canvas = Image.new("RGB", (target_w * 4, panel_h + 84), "white")
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
        px = idx * target_w
        canvas.paste(panel, (px, 58))
        draw.text((px + 8, 40), labels[idx], fill=(35, 38, 45), font=small)
        bx0 = round((x0 - rect[0]) * target_w / (rect[2] - rect[0]))
        by0 = round((y0 - rect[1]) * panel.height / (rect[3] - rect[1])) + 58
        bx1 = round((x1 - rect[0]) * target_w / (rect[2] - rect[0]))
        by1 = round((y1 - rect[1]) * panel.height / (rect[3] - rect[1])) + 58
        draw.rectangle((px + bx0, by0, px + bx1, by1), outline=(255, 0, 0, 230), width=3)
    canvas.save(path, quality=91)


def draw_sheet(result: dict, panel_paths: list[Path]) -> None:
    thumb_w = 560
    thumb_h = 240
    width = 1740
    height = 1320
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
    draw.text((24, 18), "Valid Same-Leaf Bleed-Through Control Grid", fill="white", font=title_font)
    draw.text(
        (24, 56),
        "Page 75 mirrored onto page 76; source-only signal ranked against same-size lower-page controls.",
        fill=(235, 235, 235),
        font=small,
    )
    x, y = 24, 118
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        sheet.paste(img, (x, y))
        x += thumb_w + 18
        if x + thumb_w > width:
            x = 24
            y += thumb_h + 58

    y = 720
    headers = ["mode", "dx", "dy", "mean src-only", "min src-only", ">=.10", ">=.25", "pctl>=.75", "min pctl"]
    xs = [24, 338, 390, 456, 584, 704, 762, 820, 910]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for mode in result["modeRows"]:
        values = [
            mode["mode"],
            str(mode["dx"]),
            str(mode["dy"]),
            f"{mode['meanSourceOnlyCoverage']:.4f}",
            f"{mode['minSourceOnlyCoverage']:.4f}",
            str(mode["targetCountAtLeast10"]),
            str(mode["targetCountAtLeast25"]),
            str(mode["highPercentileCount"]),
            f"{mode['minControlPercentile']:.3f}",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 22

    y += 20
    headers = ["mode", "target", "src-only", "control med", "control p90", "control max", "percentile", "dominant"]
    xs = [24, 338, 420, 506, 608, 706, 806, 906]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for row in result["targetRows"][:16]:
        dominant = dominant_source_label(row)
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            f"{row['controlMedianSourceOnlyCoverage']:.4f}",
            f"{row['controlP90SourceOnlyCoverage']:.4f}",
            f"{row['controlMaxSourceOnlyCoverage']:.4f}",
            f"{row['sourceOnlyControlPercentile']:.3f}",
            dominant,
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_rows = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "box": row["box"],
        }
        for row in active.get("activeRows", [])
    ]
    target_img_76 = normalize_page(76)
    source_img_75 = normalize_page(75)
    target_channels_76 = feature_channels(target_img_76)
    source_channels_75 = feature_channels(source_img_75)

    natural = evaluate_mode(
        "valid_75_to_76_natural",
        0,
        0,
        source_channels_75,
        target_channels_76,
        active_rows,
        target_img_76.size,
    )
    jitter = choose_small_jitter(
        source_channels_75,
        target_channels_76,
        active_rows,
        target_img_76.size,
    )
    mode_rows = [natural, jitter]
    target_rows = []
    panel_paths = []
    for mode in mode_rows:
        for row in mode["rows"]:
            target_rows.append(row)
            panel_path = OUT / f"{row['mode']}_{row['target']}.jpg"
            crop_panel(
                target_img_76,
                source_img_75,
                source_channels_75,
                target_channels_76,
                row,
                mode["dx"],
                mode["dy"],
                panel_path,
            )
            panel_paths.append(panel_path)

    source_r3_hits = 0
    trigger_rows = reopen.get("triggerRows", [])
    satisfied_triggers = sum(1 for row in trigger_rows if row.get("triggerSatisfiedNow"))
    trigger_count = len(trigger_rows)
    selector_unlocks = 0

    all_four_10_modes = [row["mode"] for row in mode_rows if row["allFourAtLeast10"]]
    all_four_25_modes = [row["mode"] for row in mode_rows if row["allFourAtLeast25"]]
    all_four_high_percentile_modes = [row["mode"] for row in mode_rows if row["highPercentileCount"] == 4]
    decision = (
        "valid_leaf_bleedthrough_no_active_quartet_selector"
        if not all_four_25_modes and not all_four_high_percentile_modes
        else "needs_manual_review"
    )

    summary = {
        "modeCount": len(mode_rows),
        "targetRowCount": len(target_rows),
        "naturalMeanSourceOnlyCoverage": natural["meanSourceOnlyCoverage"],
        "naturalMinSourceOnlyCoverage": natural["minSourceOnlyCoverage"],
        "naturalTargetCountAtLeast10": natural["targetCountAtLeast10"],
        "naturalTargetCountAtLeast25": natural["targetCountAtLeast25"],
        "naturalHighPercentileCount": natural["highPercentileCount"],
        "jitterBestShift": [jitter["dx"], jitter["dy"]],
        "jitterMeanSourceOnlyCoverage": jitter["meanSourceOnlyCoverage"],
        "jitterMinSourceOnlyCoverage": jitter["minSourceOnlyCoverage"],
        "jitterTargetCountAtLeast10": jitter["targetCountAtLeast10"],
        "jitterTargetCountAtLeast25": jitter["targetCountAtLeast25"],
        "jitterHighPercentileCount": jitter["highPercentileCount"],
        "allFourAtLeast10Modes": all_four_10_modes,
        "allFourAtLeast25Modes": all_four_25_modes,
        "allFourHighPercentileModes": all_four_high_percentile_modes,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"modes={summary['modeCount']}|targets={summary['targetRowCount']}|"
        f"natMean={summary['naturalMeanSourceOnlyCoverage']:.4f}|"
        f"natMin={summary['naturalMinSourceOnlyCoverage']:.4f}|"
        f"nat10={summary['naturalTargetCountAtLeast10']}|"
        f"nat25={summary['naturalTargetCountAtLeast25']}|"
        f"natPctl75={summary['naturalHighPercentileCount']}|"
        f"jit={jitter['dx']},{jitter['dy']}|"
        f"jitMean={summary['jitterMeanSourceOnlyCoverage']:.4f}|"
        f"jitMin={summary['jitterMinSourceOnlyCoverage']:.4f}|"
        f"jit10={summary['jitterTargetCountAtLeast10']}|"
        f"jit25={summary['jitterTargetCountAtLeast25']}|"
        f"jitPctl75={summary['jitterHighPercentileCount']}|"
        f"sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}|"
        f"selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page 75 -> page 76 same-leaf bleed-through control grid; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage75": rel(SOURCE_PAGE_TEMPLATE.with_name("magazine_page_75.jpg")),
            "sourcePage76": rel(SOURCE_PAGE_TEMPLATE.with_name("magazine_page_76.jpg")),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "modeRows": [
            {key: value for key, value in row.items() if key != "rows"}
            for row in mode_rows
        ],
        "targetRows": target_rows,
        "sheet": rel(OUT_SHEET),
        "panelPaths": [rel(path) for path in panel_paths],
        "nextMove": (
            "Do not extract from current held-to-light bleed-through. Reopen only with a materially new "
            "physical/original-layout source or raw clue that names a unit/order and beats same-size controls."
        ),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Bleed-Through Control Grid",
        "",
        "Scope: tested the physically valid page 75 -> page 76 held-to-light model from the current scan/PDF. Page 75 was mirrored onto page 76, then source-only signal inside O4/B4/G5/O5 was ranked against same-size lower-page control boxes. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Modes / target rows: `{summary['modeCount']}` / `{summary['targetRowCount']}`",
        f"- Natural 75->76 mean/min source-only coverage: `{summary['naturalMeanSourceOnlyCoverage']:.4f}` / `{summary['naturalMinSourceOnlyCoverage']:.4f}`",
        f"- Natural targets >=10% / >=25% source-only coverage: `{summary['naturalTargetCountAtLeast10']}` / `{summary['naturalTargetCountAtLeast25']}`",
        f"- Natural targets at >=75th percentile vs controls: `{summary['naturalHighPercentileCount']}`",
        f"- Small-jitter best shift: `{jitter['dx']},{jitter['dy']}`",
        f"- Small-jitter mean/min source-only coverage: `{summary['jitterMeanSourceOnlyCoverage']:.4f}` / `{summary['jitterMinSourceOnlyCoverage']:.4f}`",
        f"- Small-jitter targets >=10% / >=25% source-only coverage: `{summary['jitterTargetCountAtLeast10']}` / `{summary['jitterTargetCountAtLeast25']}`",
        f"- Small-jitter targets at >=75th percentile vs controls: `{summary['jitterHighPercentileCount']}`",
        f"- All-four >=10% modes: `{', '.join(all_four_10_modes) if all_four_10_modes else 'none'}`",
        f"- All-four >=25% modes: `{', '.join(all_four_25_modes) if all_four_25_modes else 'none'}`",
        f"- All-four >=75th-percentile modes: `{', '.join(all_four_high_percentile_modes) if all_four_high_percentile_modes else 'none'}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Mode Rows",
        "",
        "| mode | dx | dy | mean source-only | min source-only | >=.10 | >=.25 | pctl>=.75 | min percentile | decision signal |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in mode_rows:
        signal = (
            "all-four selective"
            if row["allFourAtLeast25"] and row["highPercentileCount"] == 4
            else "not selective"
        )
        lines.append(
            f"| `{row['mode']}` | {row['dx']} | {row['dy']} | "
            f"{row['meanSourceOnlyCoverage']:.4f} | {row['minSourceOnlyCoverage']:.4f} | "
            f"{row['targetCountAtLeast10']} | {row['targetCountAtLeast25']} | "
            f"{row['highPercentileCount']} | {row['minControlPercentile']:.3f} | {signal} |"
        )
    lines.extend(
        [
            "",
            "## Target Rows",
            "",
            "| mode | target | source-only | control median | control p90 | control max | percentile | dominant source | panel |",
            "|---|---|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in target_rows:
        dominant = dominant_source_label(row)
        panel = f"analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/{row['mode']}_{row['target']}.jpg"
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | {row['sourceOnlyCoverage']:.4f} | "
            f"{row['controlMedianSourceOnlyCoverage']:.4f} | {row['controlP90SourceOnlyCoverage']:.4f} | "
            f"{row['controlMaxSourceOnlyCoverage']:.4f} | {row['sourceOnlyControlPercentile']:.3f} | "
            f"{dominant} | `{panel}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Natural valid same-leaf bleed-through does not create an all-four O4/B4/G5/O5 source-only selector.",
            "- The small-jitter best shift is still a bounded alignment search and does not produce all-four >=25% coverage or all-four high-percentile control separation.",
            "- Treat the current light-table view as visual review material only; do not extract from it without new source/clue evidence that passes R1-R5.",
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
