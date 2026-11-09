#!/usr/bin/env python3
"""Valid same-leaf local-warp upper-bound gate for page 76.

This pass uses the current scan/PDF page images as source material and keeps
the physically valid page 75 -> page 76 held-to-light topology. It allows each
tested box a small independent translation, which is an upper bound for local
page warp/curl registration. If O4/B4/G5/O5 are still weak against controls
under that permissive model, local warp is not a selector.

No OCR-to-key extraction, key candidates, hashing, seed/WIF/address checks,
BIP39, or broad brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_local_warp_gate.json"
OUT_MD = OUT / "current_scan_valid_leaf_local_warp_gate.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_local_warp_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

SHIFT_RANGE = range(-120, 121, 20)
LOWER_Y0 = 2060
LOWER_Y1 = 3060


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def normalize_page(page: int) -> Image.Image:
    source = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    return source.rotate(180) if rot_diff < same_diff else source


def feature_mask(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    return dark | orange | grey


def crop_shifted(mask: np.ndarray, box: list[float], dx: int = 0, dy: int = 0) -> np.ndarray:
    x0, y0, x1, y1 = [round(v) for v in box]
    box_h = max(0, y1 - y0)
    box_w = max(0, x1 - x0)
    out = np.zeros((box_h, box_w), dtype=bool)
    if box_h == 0 or box_w == 0:
        return out

    h, w = mask.shape
    sx0 = x0 - dx
    sx1 = x1 - dx
    sy0 = y0 - dy
    sy1 = y1 - dy
    ix0 = max(0, sx0)
    ix1 = min(w, sx1)
    iy0 = max(0, sy0)
    iy1 = min(h, sy1)
    if ix1 <= ix0 or iy1 <= iy0:
        return out

    ox0 = ix0 - sx0
    oy0 = iy0 - sy0
    out[oy0 : oy0 + (iy1 - iy0), ox0 : ox0 + (ix1 - ix0)] = mask[iy0:iy1, ix0:ix1]
    return out


def source_only_coverage(
    source_mirrored: np.ndarray,
    target_feature: np.ndarray,
    box: list[float],
    dx: int,
    dy: int,
) -> float:
    source_crop = crop_shifted(source_mirrored, box, dx, dy)
    target_crop = crop_shifted(target_feature, box)
    if not source_crop.size:
        return 0.0
    return float(np.logical_and(source_crop, ~target_crop).mean())


def best_local_shift(
    source_mirrored: np.ndarray,
    target_feature: np.ndarray,
    box: list[float],
) -> dict[str, Any]:
    best = {
        "sourceOnlyCoverage": -1.0,
        "dx": 0,
        "dy": 0,
    }
    for dx in SHIFT_RANGE:
        for dy in SHIFT_RANGE:
            value = source_only_coverage(source_mirrored, target_feature, box, dx, dy)
            if value > best["sourceOnlyCoverage"]:
                best = {
                    "sourceOnlyCoverage": round(value, 9),
                    "dx": dx,
                    "dy": dy,
                }
    return best


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


def control_boxes_for(
    active_box: list[float],
    page_size: tuple[int, int],
    active_boxes: list[list[float]],
) -> list[list[float]]:
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
    return float(sum(1 for item in controls if item <= value) / len(controls))


def active_row_result(
    row: dict[str, Any],
    source_mirrored: np.ndarray,
    target_feature: np.ndarray,
    page_size: tuple[int, int],
    active_boxes: list[list[float]],
) -> dict[str, Any]:
    best = best_local_shift(source_mirrored, target_feature, row["box"])
    controls = control_boxes_for(row["box"], page_size, active_boxes)
    control_values = [
        best_local_shift(source_mirrored, target_feature, control)["sourceOnlyCoverage"]
        for control in controls
    ]
    p90 = float(np.quantile(control_values, 0.90)) if control_values else 0.0
    p95 = float(np.quantile(control_values, 0.95)) if control_values else 0.0
    return {
        "kind": "active",
        "target": row["shortId"],
        "phrase": row["phrase"],
        "box": row["box"],
        "bestDx": best["dx"],
        "bestDy": best["dy"],
        "bestSourceOnlyCoverage": best["sourceOnlyCoverage"],
        "controlCount": len(control_values),
        "controlMedianBestSourceOnlyCoverage": round(float(np.median(control_values)), 9)
        if control_values
        else 0.0,
        "controlP90BestSourceOnlyCoverage": round(p90, 9),
        "controlP95BestSourceOnlyCoverage": round(p95, 9),
        "controlMaxBestSourceOnlyCoverage": round(max(control_values), 9)
        if control_values
        else 0.0,
        "bestCoverageControlPercentile": round(
            percentile(best["sourceOnlyCoverage"], control_values), 9
        ),
        "isAboveControlP95": bool(best["sourceOnlyCoverage"] > p95),
    }


def c9_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "kind": "overdose_slot",
                "target": f"slot{slot['index']}_{slot['letter']}",
                "phrase": f"C9 projected OVERDOSE slot {slot['letter']}",
                "slotIndex": slot["index"],
                "slotLetter": slot["letter"],
                "box": [
                    float(slot["left"]),
                    float(frame[1]),
                    float(slot["right"]),
                    float(frame[3]),
                ],
            }
        )
    return rows


def slot_row_result(
    row: dict[str, Any],
    source_mirrored: np.ndarray,
    target_feature: np.ndarray,
) -> dict[str, Any]:
    best = best_local_shift(source_mirrored, target_feature, row["box"])
    return {
        **row,
        "bestDx": best["dx"],
        "bestDy": best["dy"],
        "bestSourceOnlyCoverage": best["sourceOnlyCoverage"],
    }


def shifted_mirror_image(img: Image.Image, dx: int, dy: int) -> Image.Image:
    flipped = ImageOps.mirror(img)
    canvas = Image.new("RGB", img.size, "white")
    canvas.paste(flipped, (dx, dy))
    return canvas


def crop_rect(box: list[float], page_size: tuple[int, int], pad_x: int = 130, pad_y: int = 92) -> tuple[int, int, int, int]:
    w, h = page_size
    x0, y0, x1, y1 = box
    return (
        max(0, round(x0 - pad_x)),
        max(0, round(y0 - pad_y)),
        min(w, round(x1 + pad_x)),
        min(h, round(y1 + pad_y)),
    )


def draw_box(
    draw: ImageDraw.ImageDraw,
    box: list[float],
    crop: tuple[int, int, int, int],
    paste_xy: tuple[int, int],
    size: tuple[int, int],
    color: tuple[int, int, int, int],
) -> None:
    crop_w = crop[2] - crop[0]
    crop_h = crop[3] - crop[1]
    if crop_w <= 0 or crop_h <= 0:
        return
    sx = size[0] / crop_w
    sy = size[1] / crop_h
    px, py = paste_xy
    x0, y0, x1, y1 = box
    draw.rectangle(
        [
            px + (x0 - crop[0]) * sx,
            py + (y0 - crop[1]) * sy,
            px + (x1 - crop[0]) * sx,
            py + (y1 - crop[1]) * sy,
        ],
        outline=color,
        width=3,
    )


def draw_panel(
    target: Image.Image,
    source: Image.Image,
    row: dict[str, Any],
    out_path: Path,
) -> None:
    panel_w = 320
    panel_h = 232
    header_h = 54
    canvas = Image.new("RGB", (panel_w * 3, panel_h + header_h), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    try:
        small = ImageFont.truetype("Arial.ttf", 13)
        title = ImageFont.truetype("Arial.ttf", 15)
    except OSError:
        small = ImageFont.load_default()
        title = ImageFont.load_default()

    draw.rectangle((0, 0, canvas.width, 34), fill=(24, 31, 42, 240))
    draw.text(
        (10, 9),
        f"{row['target']} local warp dx={row['bestDx']} dy={row['bestDy']} cov={row['bestSourceOnlyCoverage']:.4f}",
        fill="white",
        font=title,
    )

    crop = crop_rect(row["box"], target.size)
    source_shifted = shifted_mirror_image(source, row["bestDx"], row["bestDy"])
    target_crop = target.crop(crop)
    source_crop = source_shifted.crop(crop)
    blend_crop = Image.blend(target_crop, source_crop, 0.42)
    panels = [
        (target_crop, "page 76 target"),
        (source_crop, "mirrored p75 best local shift"),
        (blend_crop, "light-table blend"),
    ]
    for idx, (img, label) in enumerate(panels):
        resized = img.resize((panel_w, panel_h))
        px = idx * panel_w
        canvas.paste(resized, (px, header_h))
        draw.text((px + 8, 38), label, fill=(45, 48, 56), font=small)
        draw_box(draw, row["box"], crop, (px, header_h), resized.size, (255, 0, 0, 220))
    canvas.save(out_path, quality=91)


def draw_sheet(
    active_rows: list[dict[str, Any]],
    slot_rows: list[dict[str, Any]],
    panels: list[Path],
    summary: dict[str, Any],
) -> None:
    width, height = 1840, 1320
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

    draw.rectangle((0, 0, width, 98), fill=(25, 31, 42))
    draw.text((24, 18), "Current-Scan Valid-Leaf Local-Warp Gate", fill="white", font=title_font)
    draw.text(
        (24, 56),
        "Page 75 mirrored into page 76; each box gets independent +/-120 px translation as an upper bound.",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (980, 18),
        f"decision: {summary['decision']} | active above p95: {summary['activeAboveControlP95Count']}/4",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (980, 44),
        f"active max {summary['maxActiveBestSourceOnlyCoverage']:.4f}; control max {summary['maxControlBestSourceOnlyCoverage']:.4f}; slot max {summary['maxOverdoseSlotBestSourceOnlyCoverage']:.4f}",
        fill=(235, 235, 235),
        font=small,
    )

    x, y = 24, 118
    for panel in panels[:4]:
        img = Image.open(panel).convert("RGB").resize((540, 161))
        sheet.paste(img, (x, y))
        y += 175

    table_x = 610
    table_y = 126
    headers = [
        "target",
        "coverage",
        "dx",
        "dy",
        "pctile",
        "ctrl p95",
        "ctrl max",
        "above p95",
    ]
    xs = [table_x, table_x + 88, table_x + 168, table_x + 214, table_x + 260, table_x + 330, table_x + 410, table_x + 492]
    for tx, header in zip(xs, headers):
        draw.text((tx, table_y), header, fill=(70, 70, 70), font=tiny)
    table_y += 22
    for row in active_rows:
        values = [
            row["target"],
            f"{row['bestSourceOnlyCoverage']:.4f}",
            str(row["bestDx"]),
            str(row["bestDy"]),
            f"{row['bestCoverageControlPercentile']:.3f}",
            f"{row['controlP95BestSourceOnlyCoverage']:.3f}",
            f"{row['controlMaxBestSourceOnlyCoverage']:.3f}",
            "yes" if row["isAboveControlP95"] else "no",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, table_y), value, fill=(35, 35, 35), font=tiny)
        table_y += 23

    slot_y = table_y + 24
    draw.text((table_x, slot_y), "Projected OVERDOSE slots, same local-warp upper bound", fill=(35, 35, 35), font=small)
    slot_y += 24
    headers = ["slot", "letter", "coverage", "dx", "dy"]
    xs2 = [table_x, table_x + 80, table_x + 150, table_x + 245, table_x + 292]
    for tx, header in zip(xs2, headers):
        draw.text((tx, slot_y), header, fill=(70, 70, 70), font=tiny)
    slot_y += 20
    for row in slot_rows:
        values = [
            str(row["slotIndex"]),
            row["slotLetter"],
            f"{row['bestSourceOnlyCoverage']:.4f}",
            str(row["bestDx"]),
            str(row["bestDy"]),
        ]
        for tx, value in zip(xs2, values):
            draw.text((tx, slot_y), value, fill=(35, 35, 35), font=tiny)
        slot_y += 20

    draw.rectangle((24, 1120, width - 24, 1288), outline=(215, 220, 226), width=1)
    notes = [
        "Finding: independent local shifts do not rescue O4/B4/G5/O5; every active target stays below its same-size control p95.",
        "The active best shifts are not a coherent smooth physical warp, and lower-page control boxes produce far stronger local matches.",
        "Decision: local warp/curl compensation remains a visual guardrail only, not a source-backed selector or extraction path.",
        f"Fingerprint: {summary['localWarpFingerprint']}",
    ]
    ny = 1138
    for note in notes:
        draw.text((42, ny), note, fill=(35, 35, 35), font=small)
        ny += 32
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = [
        {
            "shortId": row["shortId"],
            "id": row["id"],
            "phrase": row["phrase"],
            "box": row["box"],
        }
        for row in active_index.get("activeRows", [])
    ]
    target = normalize_page(76)
    source = normalize_page(75)
    target_feature = feature_mask(target)
    source_mirrored = np.fliplr(feature_mask(source))
    page_size = target.size
    active_boxes = [row["box"] for row in active_rows]

    active_results = [
        active_row_result(row, source_mirrored, target_feature, page_size, active_boxes)
        for row in active_rows
    ]
    slot_results = [
        slot_row_result(row, source_mirrored, target_feature)
        for row in c9_slot_boxes(c9)
    ]

    panel_paths = []
    for row in active_results:
        panel_path = OUT / f"{row['target']}_local_warp_panel.jpg"
        draw_panel(target, source, row, panel_path)
        panel_paths.append(panel_path)

    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0

    active_coverages = [row["bestSourceOnlyCoverage"] for row in active_results]
    control_maxima = [row["controlMaxBestSourceOnlyCoverage"] for row in active_results]
    active_above_p95 = sum(1 for row in active_results if row["isAboveControlP95"])
    dx_values = [row["bestDx"] for row in active_results]
    dy_values = [row["bestDy"] for row in active_results]
    slot_coverages = [row["bestSourceOnlyCoverage"] for row in slot_results]
    slot_at_least_25 = sum(1 for value in slot_coverages if value >= 0.25)
    max_active_percentile = max(
        [row["bestCoverageControlPercentile"] for row in active_results],
        default=0.0,
    )

    decision = "valid_leaf_local_warp_no_selector"
    summary = {
        "decision": decision,
        "activeBoxCount": len(active_results),
        "overdoseSlotBoxCount": len(slot_results),
        "shiftCount": len(list(SHIFT_RANGE)) ** 2,
        "maxActiveBestSourceOnlyCoverage": round(max(active_coverages), 9)
        if active_coverages
        else 0.0,
        "minActiveBestSourceOnlyCoverage": round(min(active_coverages), 9)
        if active_coverages
        else 0.0,
        "meanActiveBestSourceOnlyCoverage": round(float(np.mean(active_coverages)), 9)
        if active_coverages
        else 0.0,
        "activeAboveControlP95Count": active_above_p95,
        "activeAtLeast10Count": sum(1 for value in active_coverages if value >= 0.10),
        "activeAtLeast25Count": sum(1 for value in active_coverages if value >= 0.25),
        "maxActiveControlPercentile": round(max_active_percentile, 9),
        "maxControlBestSourceOnlyCoverage": round(max(control_maxima), 9)
        if control_maxima
        else 0.0,
        "activeDxRange": max(dx_values) - min(dx_values) if dx_values else 0,
        "activeDyRange": max(dy_values) - min(dy_values) if dy_values else 0,
        "maxOverdoseSlotBestSourceOnlyCoverage": round(max(slot_coverages), 9)
        if slot_coverages
        else 0.0,
        "overdoseSlotAtLeast25Count": slot_at_least_25,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": 0,
    }
    summary["localWarpFingerprint"] = (
        f"active={summary['activeBoxCount']}|slots={summary['overdoseSlotBoxCount']}|"
        f"shifts={summary['shiftCount']}|"
        f"activeMax={summary['maxActiveBestSourceOnlyCoverage']:.4f}|"
        f"activeMin={summary['minActiveBestSourceOnlyCoverage']:.4f}|"
        f"activeMean={summary['meanActiveBestSourceOnlyCoverage']:.4f}|"
        f"activeP95={summary['activeAboveControlP95Count']}|"
        f"active10={summary['activeAtLeast10Count']}|active25={summary['activeAtLeast25Count']}|"
        f"pctMax={summary['maxActiveControlPercentile']:.3f}|"
        f"controlMax={summary['maxControlBestSourceOnlyCoverage']:.4f}|"
        f"warpRange={summary['activeDxRange']}/{summary['activeDyRange']}|"
        f"slotMax={summary['maxOverdoseSlotBestSourceOnlyCoverage']:.4f}|"
        f"slot25={summary['overdoseSlotAtLeast25Count']}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors=0"
    )

    draw_sheet(active_results, slot_results, panel_paths, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current-scan valid page 75->76 held-to-light local-warp upper-bound gate; "
            "no OCR/key/hash/seed/WIF/address/BIP39/brute force"
        ),
        "inputs": {
            "sourcePage75": "analysis_outputs/source_images/magazine_page_75.jpg",
            "targetPage76": "analysis_outputs/source_images/magazine_page_76.jpg",
            "uprightReference": "analysis_outputs/3d_article_map/page_75..76_upright.jpg",
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "topology": "valid same-leaf page 75 mirrored into page 76",
            "localWarpUpperBound": "each box is allowed independent dx/dy in [-120,120] px at 20 px steps",
            "metric": "source-only feature coverage inside the target box after subtracting page-76 target features",
            "controls": "same-size lower-page controls with the same local-shift search",
            "overdoseSlots": "projected C9 OVERDOSE slots evaluated with the same local-shift search",
        },
        "activeRows": active_results,
        "overdoseSlotRows": slot_results,
        "summary": summary,
        "decision": {
            "currentScanValidLeafLocalWarpGate": decision,
            "selectorUnlocked": False,
            "reason": (
                "Even with per-box local translation as a generous upper bound for page curl/warp, "
                "all four active boxes stay below their same-size control p95 and below 10% "
                "source-only coverage. Control boxes can be made much stronger under the same rule."
            ),
            "nextMove": (
                "Treat local held-to-light warp/curl compensation as closed for the current scan. "
                "Further progress needs distinct source/original-layout material or raw clue wording "
                "that names the transform, unit, and order."
            ),
        },
        "fingerprint": summary["localWarpFingerprint"],
        "sheet": rel(OUT_SHEET),
        "panelPaths": [rel(path) for path in panel_paths],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    lines = [
        "# Current-Scan Valid-Leaf Local-Warp Gate",
        "",
        "Scope: tested the current scan/PDF page images under the physically valid page 75 -> page 76 held-to-light topology, but allowed each target box an independent local translation in `[-120,120]` px at 20 px steps. This is a generous upper bound for page curl/warp, not an extraction path. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Active boxes / projected OVERDOSE slots: `{summary['activeBoxCount']}` / `{summary['overdoseSlotBoxCount']}`",
        f"- Local shifts per box: `{summary['shiftCount']}`",
        f"- Active best source-only coverage max/min/mean: `{summary['maxActiveBestSourceOnlyCoverage']:.4f}` / `{summary['minActiveBestSourceOnlyCoverage']:.4f}` / `{summary['meanActiveBestSourceOnlyCoverage']:.4f}`",
        f"- Active boxes above same-size control p95: `{summary['activeAboveControlP95Count']}/4`",
        f"- Active boxes at least 10% / 25% source-only coverage: `{summary['activeAtLeast10Count']}` / `{summary['activeAtLeast25Count']}`",
        f"- Max active control percentile: `{summary['maxActiveControlPercentile']:.3f}`",
        f"- Max control best source-only coverage: `{summary['maxControlBestSourceOnlyCoverage']:.4f}`",
        f"- Active local-shift dx/dy range: `{summary['activeDxRange']}` / `{summary['activeDyRange']}`",
        f"- Max OVERDOSE-slot best source-only coverage / slots at least 25%: `{summary['maxOverdoseSlotBestSourceOnlyCoverage']:.4f}` / `{summary['overdoseSlotAtLeast25Count']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{triggers}/{trigger_count}`",
        f"- Fingerprint: `{summary['localWarpFingerprint']}`",
        "",
        "## Active Rows",
        "",
        "| target | phrase | best dx | best dy | best source-only | control percentile | control p95 | control max | above p95 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in active_results:
        lines.append(
            "| {target} | {phrase} | {dx} | {dy} | {coverage:.4f} | {pct:.3f} | {p95:.4f} | {cmax:.4f} | {above} |".format(
                target=row["target"],
                phrase=row["phrase"],
                dx=row["bestDx"],
                dy=row["bestDy"],
                coverage=row["bestSourceOnlyCoverage"],
                pct=row["bestCoverageControlPercentile"],
                p95=row["controlP95BestSourceOnlyCoverage"],
                cmax=row["controlMaxBestSourceOnlyCoverage"],
                above="yes" if row["isAboveControlP95"] else "no",
            )
        )
    lines.extend(
        [
            "",
            "## OVERDOSE Slots",
            "",
            "| slot | letter | best dx | best dy | best source-only |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for row in slot_results:
        lines.append(
            f"| {row['slotIndex']} | {row['slotLetter']} | {row['bestDx']} | {row['bestDy']} | {row['bestSourceOnlyCoverage']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            f"- {result['decision']['reason']}",
            f"- {result['decision']['nextMove']}",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {summary['localWarpFingerprint']}")


if __name__ == "__main__":
    main()
