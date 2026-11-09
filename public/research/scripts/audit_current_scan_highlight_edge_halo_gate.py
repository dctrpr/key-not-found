#!/usr/bin/env python3
"""Audit current page-76 scan highlight edge/halo behavior.

This bounded pass checks whether orange/black edge halos around O4/B4/G5/O5 or
projected OVERDOSE slots form a shared directional/color carrier against shifted
controls. It is a scan-artifact/source-quality gate, not extraction.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_highlight_edge_halo_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_highlight_edge_halo_gate.json"
OUT_MD = OUT / "current_scan_highlight_edge_halo_gate.md"
OUT_SHEET = OUT / "current_scan_highlight_edge_halo_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUTER_PADS = [4, 8, 16, 32]
INNER_STRIPS = [4, 8, 16]
SIGNATURE_PADS = [8, 16]
EDGE_NAMES = ["top", "right", "bottom", "left"]
OUTLIER_Z = 3.0


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


def clamp_box(box: list[float], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [
        max(0.0, min(float(width), x0)),
        max(0.0, min(float(height), y0)),
        max(0.0, min(float(width), x1)),
        max(0.0, min(float(height), y1)),
    ]


def int_box(box: list[float], width: int, height: int) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = clamp_box(box, width, height)
    ix0 = max(0, min(width, int(round(x0))))
    iy0 = max(0, min(height, int(round(y0))))
    ix1 = max(0, min(width, int(round(x1))))
    iy1 = max(0, min(height, int(round(y1))))
    return ix0, iy0, ix1, iy1


def crop_rgb(page: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        return np.zeros((0, 0, 3), dtype=np.uint8)
    return page[y0:y1, x0:x1, :]


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
                "shortId": f"slot{slot['index']}_{slot['letter']}",
                "phrase": f"C9 projected OVERDOSE slot {slot['letter']}",
                "visualState": "N",
                "kind": "overdose_slot",
                "box": [float(slot["left"]), float(frame[1]), float(slot["right"]), float(frame[3])],
            }
        )
    return rows


def shifted_control_boxes(active_boxes: list[dict[str, Any]], size: tuple[int, int]) -> list[dict[str, Any]]:
    width, height = size
    rows: list[dict[str, Any]] = []
    for box in active_boxes:
        x0, y0, x1, y1 = box["box"]
        for dy in [-292, -146, 146, 292]:
            shifted = clamp_box([x0, y0 + dy, x1, y1 + dy], width, height)
            if shifted[3] > shifted[1] and shifted[2] > shifted[0]:
                rows.append(
                    {
                        "shortId": f"{box['shortId']}_dy{dy:+d}",
                        "phrase": f"{box['shortId']} shifted {dy:+d}px",
                        "visualState": "control",
                        "kind": "shifted_control",
                        "box": shifted,
                    }
                )
    return rows


def rgb_masks(rgb: np.ndarray) -> dict[str, np.ndarray]:
    if rgb.size == 0:
        empty = np.zeros(rgb.shape[:2], dtype=bool)
        return {"orange": empty, "black": empty, "ink": empty}

    arr = rgb.astype(np.float32) / 255.0
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    maxc = np.max(arr, axis=2)
    minc = np.min(arr, axis=2)
    delta = maxc - minc
    sat = np.where(maxc > 1e-6, delta / np.maximum(maxc, 1e-6), 0.0)

    hue = np.zeros_like(maxc)
    red = (maxc == r) & (delta > 1e-6)
    green = (maxc == g) & (delta > 1e-6)
    blue = (maxc == b) & (delta > 1e-6)
    hue[red] = ((g[red] - b[red]) / delta[red]) % 6.0
    hue[green] = ((b[green] - r[green]) / delta[green]) + 2.0
    hue[blue] = ((r[blue] - g[blue]) / delta[blue]) + 4.0
    hue *= 60.0

    rgb_simple_orange = (
        (rgb[:, :, 0] > 115)
        & (rgb[:, :, 1] > 55)
        & (rgb[:, :, 2] < 165)
        & (rgb[:, :, 0].astype(np.int16) - rgb[:, :, 2].astype(np.int16) > 32)
        & (rgb[:, :, 1].astype(np.float32) > rgb[:, :, 2].astype(np.float32) * 1.04)
    )
    hsv_orange = (
        (hue >= 12.0)
        & (hue <= 58.0)
        & (sat >= 0.16)
        & (maxc >= 0.28)
        & (g >= b * 1.02)
    )
    orange = rgb_simple_orange | hsv_orange
    black = maxc <= 0.42
    ink = orange | black
    return {"orange": orange, "black": black, "ink": ink}


def mask_ratios(rgb: np.ndarray) -> dict[str, float | int]:
    pixels = int(rgb.shape[0] * rgb.shape[1]) if rgb.ndim == 3 else 0
    if pixels == 0:
        return {
            "pixels": 0,
            "orangeRatio": 0.0,
            "blackRatio": 0.0,
            "inkRatio": 0.0,
            "meanR": 0.0,
            "meanG": 0.0,
            "meanB": 0.0,
        }
    masks = rgb_masks(rgb)
    means = rgb.reshape(-1, 3).mean(axis=0)
    return {
        "pixels": pixels,
        "orangeRatio": round(float(masks["orange"].mean()), 6),
        "blackRatio": round(float(masks["black"].mean()), 6),
        "inkRatio": round(float(masks["ink"].mean()), 6),
        "meanR": round(float(means[0]), 6),
        "meanG": round(float(means[1]), 6),
        "meanB": round(float(means[2]), 6),
    }


def combine_crops(crops: list[np.ndarray]) -> np.ndarray:
    good = [crop.reshape(-1, 3) for crop in crops if crop.size]
    if not good:
        return np.zeros((0, 0, 3), dtype=np.uint8)
    joined = np.vstack(good)
    return joined.reshape(1, joined.shape[0], 3)


def edge_boxes(box: tuple[int, int, int, int], pad: int, width: int, height: int) -> dict[str, tuple[int, int, int, int]]:
    x0, y0, x1, y1 = box
    return {
        "top": int_box([x0 - pad, y0 - pad, x1 + pad, y0], width, height),
        "right": int_box([x1, y0, x1 + pad, y1], width, height),
        "bottom": int_box([x0 - pad, y1, x1 + pad, y1 + pad], width, height),
        "left": int_box([x0 - pad, y0, x0, y1], width, height),
    }


def inner_boxes(box: tuple[int, int, int, int], strip: int, width: int, height: int) -> dict[str, tuple[int, int, int, int]]:
    x0, y0, x1, y1 = box
    strip = max(1, min(strip, max(1, (x1 - x0) // 2), max(1, (y1 - y0) // 2)))
    return {
        "top": int_box([x0, y0, x1, y0 + strip], width, height),
        "right": int_box([x1 - strip, y0, x1, y1], width, height),
        "bottom": int_box([x0, y1 - strip, x1, y1], width, height),
        "left": int_box([x0, y0, x0 + strip, y1], width, height),
    }


def edge_measurements(
    page: np.ndarray,
    boxes: dict[str, tuple[int, int, int, int]],
) -> dict[str, Any]:
    edge_rows: dict[str, dict[str, float | int]] = {}
    crops = []
    for edge in EDGE_NAMES:
        crop = crop_rgb(page, boxes[edge])
        crops.append(crop)
        edge_rows[edge] = mask_ratios(crop)
    combined = mask_ratios(combine_crops(crops))
    for color in ["orange", "black", "ink"]:
        values = [float(edge_rows[edge][f"{color}Ratio"]) for edge in EDGE_NAMES]
        combined[f"{color}TopMinusBottom"] = round(values[0] - values[2], 6)
        combined[f"{color}RightMinusLeft"] = round(values[1] - values[3], 6)
        combined[f"{color}EdgeSpread"] = round(max(values) - min(values), 6)
        max_index = int(np.argmax(values))
        combined[f"{color}DominantEdge"] = EDGE_NAMES[max_index]
        combined[f"{color}DominantEdgeRatio"] = round(values[max_index], 6)
    return {"combined": combined, "edges": edge_rows}


def ratio_bin(value: float, scale: int = 20) -> int:
    return int(round(max(0.0, min(1.0, value)) * scale))


def collect_features(row: dict[str, Any]) -> dict[str, float]:
    features: dict[str, float] = {}
    for item in row["outerRings"]:
        pad = item["pad"]
        combined = item["combined"]
        for color in ["orange", "black", "ink"]:
            for metric in [
                f"{color}Ratio",
                f"{color}DominantEdgeRatio",
                f"{color}EdgeSpread",
                f"{color}TopMinusBottom",
                f"{color}RightMinusLeft",
            ]:
                features[f"outer_p{pad}_{metric}"] = float(combined[metric])
            for edge in EDGE_NAMES:
                features[f"outer_p{pad}_{color}_{edge}Ratio"] = float(
                    item["edges"][edge][f"{color}Ratio"]
                )
    for item in row["innerStrips"]:
        strip = item["strip"]
        combined = item["combined"]
        for color in ["orange", "black", "ink"]:
            for metric in [
                f"{color}Ratio",
                f"{color}DominantEdgeRatio",
                f"{color}EdgeSpread",
                f"{color}TopMinusBottom",
                f"{color}RightMinusLeft",
            ]:
                features[f"inner_s{strip}_{metric}"] = float(combined[metric])
            for edge in EDGE_NAMES:
                features[f"inner_s{strip}_{color}_{edge}Ratio"] = float(
                    item["edges"][edge][f"{color}Ratio"]
                )
    return features


def halo_signature(row: dict[str, Any]) -> str:
    parts = []
    for item in row["outerRings"]:
        if item["pad"] not in SIGNATURE_PADS:
            continue
        combined = item["combined"]
        orange = float(combined["orangeRatio"])
        black = float(combined["blackRatio"])
        if orange >= black:
            color = "O"
            edge = str(combined["orangeDominantEdge"])[0].upper()
            value = orange
            spread = float(combined["orangeEdgeSpread"])
        else:
            color = "K"
            edge = str(combined["blackDominantEdge"])[0].upper()
            value = black
            spread = float(combined["blackEdgeSpread"])
        parts.append(f"p{item['pad']}={color}{edge}{ratio_bin(value)}s{ratio_bin(spread)}")
    return "|".join(parts)


def edge_bias_signature(row: dict[str, Any]) -> str:
    parts = []
    for item in row["outerRings"]:
        if item["pad"] not in SIGNATURE_PADS:
            continue
        combined = item["combined"]
        edge = str(combined["inkDominantEdge"])[0].upper()
        value = float(combined["inkDominantEdgeRatio"])
        spread = float(combined["inkEdgeSpread"])
        parts.append(f"p{item['pad']}=I{edge}{ratio_bin(value)}s{ratio_bin(spread)}")
    return "|".join(parts)


def inspect_region(page: np.ndarray, row: dict[str, Any]) -> dict[str, Any]:
    height, width = page.shape[:2]
    box = int_box(row["box"], width, height)
    outer_rings = []
    for pad in OUTER_PADS:
        boxes = edge_boxes(box, pad, width, height)
        outer_rings.append({"pad": pad, **edge_measurements(page, boxes)})
    inner_strips = []
    for strip in INNER_STRIPS:
        boxes = inner_boxes(box, strip, width, height)
        inner_strips.append({"strip": strip, **edge_measurements(page, boxes)})
    core = mask_ratios(crop_rgb(page, box))
    x0, y0, x1, y1 = row["box"]
    inspected = {
        **row,
        "width": round(float(x1 - x0), 6),
        "height": round(float(y1 - y0), 6),
        "coreColor": core,
        "outerRings": outer_rings,
        "innerStrips": inner_strips,
    }
    inspected["haloSignature"] = halo_signature(inspected)
    inspected["edgeBiasSignature"] = edge_bias_signature(inspected)
    inspected["featureValues"] = collect_features(inspected)
    return inspected


def control_stats(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    controls = [row for row in rows if row["kind"] == "shifted_control"]
    keys = sorted({key for row in controls for key in row["featureValues"]})
    stats: dict[str, dict[str, float]] = {}
    for key in keys:
        arr = np.asarray([float(row["featureValues"].get(key, 0.0)) for row in controls])
        stats[key] = {"mean": float(arr.mean()) if arr.size else 0.0, "std": float(arr.std()) if arr.size else 0.0}
    return stats


def zscore(value: float, stats: dict[str, float]) -> float:
    if stats["std"] < 1e-9:
        return 0.0
    return float((value - stats["mean"]) / stats["std"])


def annotate_outliers(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    stats = control_stats(rows)
    for row in rows:
        strongest_outer = {"feature": None, "absZ": 0.0, "value": None}
        strongest_inner = {"feature": None, "absZ": 0.0, "value": None}
        strongest_any = {"feature": None, "absZ": 0.0, "value": None}
        outer_z_values: list[float] = []
        inner_z_values: list[float] = []
        any_z_values: list[float] = []
        for key, value in row["featureValues"].items():
            abs_z = abs(zscore(float(value), stats.get(key, {"mean": 0.0, "std": 0.0})))
            any_z_values.append(abs_z)
            if key.startswith("outer_"):
                outer_z_values.append(abs_z)
                if abs_z > float(strongest_outer["absZ"]):
                    strongest_outer = {
                        "feature": key,
                        "absZ": round(abs_z, 6),
                        "value": round(float(value), 6),
                    }
            elif key.startswith("inner_"):
                inner_z_values.append(abs_z)
                if abs_z > float(strongest_inner["absZ"]):
                    strongest_inner = {
                        "feature": key,
                        "absZ": round(abs_z, 6),
                        "value": round(float(value), 6),
                    }
            if abs_z > float(strongest_any["absZ"]):
                strongest_any = {
                    "feature": key,
                    "absZ": round(abs_z, 6),
                    "value": round(float(value), 6),
                }
        row["maxOuterHaloAbsZ"] = round(max(outer_z_values), 6) if outer_z_values else 0.0
        row["maxInnerEdgeAbsZ"] = round(max(inner_z_values), 6) if inner_z_values else 0.0
        row["maxAnyEdgeAbsZ"] = round(max(any_z_values), 6) if any_z_values else 0.0
        row["outerHaloOutlier"] = bool(row["maxOuterHaloAbsZ"] >= OUTLIER_Z)
        row["innerEdgeOutlier"] = bool(row["maxInnerEdgeAbsZ"] >= OUTLIER_Z)
        row["anyEdgeOutlier"] = bool(row["maxAnyEdgeAbsZ"] >= OUTLIER_Z)
        row["strongestOuterHaloZ"] = strongest_outer
        row["strongestInnerEdgeZ"] = strongest_inner
        row["strongestAnyEdgeZ"] = strongest_any
        row["maxHaloAbsZ"] = row["maxOuterHaloAbsZ"]
        row["haloOutlier"] = row["outerHaloOutlier"]
        row["strongestHaloZ"] = strongest_outer
    return stats


def draw_ring_overlay(draw: ImageDraw.ImageDraw, box: list[float], scale: tuple[float, float], label: str, color: tuple[int, int, int, int]) -> None:
    sx, sy = scale
    x0, y0, x1, y1 = box
    rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
    draw.rectangle(rect, outline=color, width=3)
    pad = 16
    outer = [(x0 - pad) * sx, (y0 - pad) * sy, (x1 + pad) * sx, (y1 + pad) * sy]
    draw.rectangle(outer, outline=(color[0], color[1], color[2], 90), width=2)
    draw.text((rect[0], max(0, rect[1] - 16)), label, fill=(255, 0, 0, 255))


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1880, 1300), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1880, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan Highlight Edge-Halo Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 target edge rings checked for orange/black directional halo behavior against controls and C9 OVERDOSE slots.",
        fill=(235, 235, 235),
        font=small,
    )

    preview = image.resize((720, round(720 * image.height / image.width)))
    pdraw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height
    for row in rows:
        if row["kind"] not in {"active", "overdose_slot"}:
            continue
        color = (255, 128, 0, 230) if row["kind"] == "active" else (30, 90, 255, 170)
        draw_ring_overlay(pdraw, row["box"], (sx, sy), row["shortId"], color)
    sheet.paste(preview, (24, 120))

    x0 = 780
    y = 120
    draw.text((x0, y), "Strongest edge-halo rows", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "halo sig", "edge sig", "maxZ", "feature", "value"]
    xs = [x0, x0 + 112, x0 + 245, x0 + 500, x0 + 750, x0 + 820, x0 + 1030]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    sort_rows = sorted(rows, key=lambda item: item["maxHaloAbsZ"], reverse=True)
    for row in sort_rows[:30]:
        strongest = row["strongestHaloZ"]
        vals = [
            row["kind"][:14],
            row["shortId"][:16],
            row["haloSignature"][:32],
            row["edgeBiasSignature"][:32],
            f"{row['maxHaloAbsZ']:.2f}",
            str(strongest["feature"])[:28],
            f"{float(strongest['value'] or 0.0):.3f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    draw.text((780, 760), "Summary", fill=(70, 70, 70), font=small)
    summary_lines = [
        f"Active/control/slots: {summary['activeBoxCount']} / {summary['shiftedControlBoxCount']} / {summary['overdoseSlotBoxCount']}",
        f"Active halo outliers: {summary['activeHaloOutlierCount']} ({','.join(summary['activeHaloOutlierIds'])})",
        f"All four active halo outlier: {int(summary['allFourActiveHaloOutlier'])}",
        f"Common halo signature: {summary['activeCommonHaloSignature'] or 'mixed'}",
        f"Common edge-bias signature: {summary['activeCommonEdgeBiasSignature'] or 'mixed'}",
        f"Control/slot halo matches: {summary['controlCommonHaloSignatureMatchCount']} / {summary['overdoseSlotCommonHaloSignatureMatchCount']}",
        f"Shared carrier / hidden candidate: {int(summary['sharedActiveHaloCarrier'])} / {int(summary['hiddenHaloCandidate'])}",
        f"Max active/control/slot halo Z: {summary['maxActiveHaloAbsZ']:.2f} / {summary['maxControlHaloAbsZ']:.2f} / {summary['maxOverdoseSlotHaloAbsZ']:.2f}",
        f"Source R3/triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]
    for idx, line in enumerate(summary_lines):
        draw.text((780, 794 + idx * 22), line, fill=(35, 35, 35), font=small)

    active_rows = [row for row in rows if row["kind"] == "active"]
    thumb_rows = active_rows + [row for row in sort_rows if row["kind"] != "active"][:4]
    tx = 780
    ty = 1012
    draw.text((tx, ty - 24), "Active crops and strongest control/slot rows", fill=(70, 70, 70), font=small)
    for i, row in enumerate(thumb_rows[:8]):
        crop = image.crop(tuple(round(v) for v in row["box"])).convert("RGB").resize((220, 74))
        cx = tx + (i % 4) * 250
        cy = ty + (i // 4) * 132
        sheet.paste(crop, (cx, cy))
        draw.rectangle((cx, cy, cx + 220, cy + 74), outline=(35, 35, 35), width=1)
        draw.text(
            (cx, cy + 80),
            f"{row['shortId']} haloZ {row['maxHaloAbsZ']:.2f}",
            fill=(35, 35, 35),
            font=tiny,
        )
        draw.text((cx, cy + 96), row["edgeBiasSignature"][:28], fill=(35, 35, 35), font=tiny)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")
    page = np.asarray(image, dtype=np.uint8)

    active_boxes = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "visualState": row["visualState"],
            "kind": "active",
            "box": row["box"],
        }
        for row in active_index.get("activeRows", [])
    ]
    controls = shifted_control_boxes(active_boxes, image.size)
    slots = c9_slot_boxes(c9)
    rows = [inspect_region(page, row) for row in active_boxes + controls + slots]
    stats = annotate_outliers(rows)

    active_rows = [row for row in rows if row["kind"] == "active"]
    control_rows = [row for row in rows if row["kind"] == "shifted_control"]
    slot_rows = [row for row in rows if row["kind"] == "overdose_slot"]
    active_halo_outliers = [row["shortId"] for row in active_rows if row["haloOutlier"]]
    all_four_halo = len(active_halo_outliers) == len(active_rows)
    halo_signatures = [row["haloSignature"] for row in active_rows]
    edge_bias_signatures = [row["edgeBiasSignature"] for row in active_rows]
    active_common_halo = halo_signatures[0] if len(set(halo_signatures)) == 1 else None
    active_common_edge_bias = (
        edge_bias_signatures[0] if len(set(edge_bias_signatures)) == 1 else None
    )
    control_common_matches = (
        sum(1 for row in control_rows if row["haloSignature"] == active_common_halo)
        if active_common_halo
        else 0
    )
    slot_common_matches = (
        sum(1 for row in slot_rows if row["haloSignature"] == active_common_halo)
        if active_common_halo
        else 0
    )
    control_edge_matches = (
        sum(1 for row in control_rows if row["edgeBiasSignature"] == active_common_edge_bias)
        if active_common_edge_bias
        else 0
    )
    slot_edge_matches = (
        sum(1 for row in slot_rows if row["edgeBiasSignature"] == active_common_edge_bias)
        if active_common_edge_bias
        else 0
    )
    max_active_z = max(float(row["maxHaloAbsZ"]) for row in active_rows)
    max_control_z = max(float(row["maxHaloAbsZ"]) for row in control_rows)
    max_slot_z = max(float(row["maxHaloAbsZ"]) for row in slot_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    shared_active_carrier = bool(all_four_halo and (active_common_halo or active_common_edge_bias))
    hidden_candidate = bool(
        shared_active_carrier
        and (not active_common_halo or (control_common_matches == 0 and slot_common_matches == 0))
        and (not active_common_edge_bias or (control_edge_matches == 0 and slot_edge_matches == 0))
        and source_r3 > 0
    )

    fingerprint = (
        f"active={len(active_rows)}|controls={len(control_rows)}|slots={len(slot_rows)}"
        f"|outerPads={','.join(map(str, OUTER_PADS))}|innerStrips={','.join(map(str, INNER_STRIPS))}"
        f"|activeHaloOutliers={len(active_halo_outliers)}|allFourHalo={int(all_four_halo)}"
        f"|sharedCarrier={int(shared_active_carrier)}|hiddenCandidate={int(hidden_candidate)}"
        f"|commonHalo={active_common_halo or 'mixed'}|commonEdge={active_common_edge_bias or 'mixed'}"
        f"|controlHaloCommon={control_common_matches}|slotHaloCommon={slot_common_matches}"
        f"|controlEdgeCommon={control_edge_matches}|slotEdgeCommon={slot_edge_matches}"
        f"|maxHaloZ={max_active_z:.2f}/{max_control_z:.2f}/{max_slot_z:.2f}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_rows),
        "shiftedControlBoxCount": len(control_rows),
        "overdoseSlotBoxCount": len(slot_rows),
        "outerPadsChecked": OUTER_PADS,
        "innerStripsChecked": INNER_STRIPS,
        "signaturePads": SIGNATURE_PADS,
        "outlierAbsZThreshold": OUTLIER_Z,
        "activeHaloOutlierCount": len(active_halo_outliers),
        "activeHaloOutlierIds": active_halo_outliers,
        "allFourActiveHaloOutlier": all_four_halo,
        "activeHaloSignatures": halo_signatures,
        "activeEdgeBiasSignatures": edge_bias_signatures,
        "activeCommonHaloSignature": active_common_halo,
        "activeCommonEdgeBiasSignature": active_common_edge_bias,
        "controlCommonHaloSignatureMatchCount": control_common_matches,
        "overdoseSlotCommonHaloSignatureMatchCount": slot_common_matches,
        "controlCommonEdgeBiasSignatureMatchCount": control_edge_matches,
        "overdoseSlotCommonEdgeBiasSignatureMatchCount": slot_edge_matches,
        "sharedActiveHaloCarrier": shared_active_carrier,
        "hiddenHaloCandidate": hidden_candidate,
        "maxActiveHaloAbsZ": round(max_active_z, 6),
        "maxControlHaloAbsZ": round(max_control_z, 6),
        "maxOverdoseSlotHaloAbsZ": round(max_slot_z, 6),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "highlightEdgeHaloFingerprint": fingerprint,
    }
    draw_sheet(image, rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 scan highlight edge-halo gate over active boxes, shifted controls, and projected OVERDOSE slots; no extraction or candidate generation",
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "controlStats": stats,
        "regionRows": rows,
        "decision": {
            "currentScanHighlightEdgeHaloGate": "current_scan_highlight_edge_halo_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Edge/halo color measurements show visible target-highlight behavior, but the "
                "active color-sensitive halo signatures and ink edge-bias signatures are mixed "
                "or control-matched and still have no source-backed R3 unit/order/transform cue."
            ),
            "nextMove": (
                "Do not pursue current-scan highlight halo tuning as a selector. Continue with "
                "original-layout/physical source validation or raw clue wording that names the "
                "missing unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Highlight Edge-Halo Gate",
        "",
        "Scope: inspected orange/black edge-halo behavior around current page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots. This is a scan/source-quality gate, not extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/control/OVERDOSE-slot boxes: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Outer pads checked: `{OUTER_PADS}`",
        f"- Inner strips checked: `{INNER_STRIPS}`",
        f"- Outlier abs-z threshold against shifted controls: `{OUTLIER_Z}`",
        f"- Active edge-halo outlier rows: `{len(active_halo_outliers)}` (`{','.join(active_halo_outliers)}`)",
        f"- All-four active edge-halo outlier: `{int(all_four_halo)}`",
        f"- Active common color-sensitive halo signature: `{active_common_halo or 'mixed'}`",
        f"- Active common ink edge-bias signature: `{active_common_edge_bias or 'mixed'}`",
        f"- Matching controls / OVERDOSE slots for common halo signature: `{control_common_matches}` / `{slot_common_matches}`",
        f"- Matching controls / OVERDOSE slots for common edge-bias signature: `{control_edge_matches}` / `{slot_edge_matches}`",
        f"- Shared active halo carrier / hidden halo candidate: `{int(shared_active_carrier)}` / `{int(hidden_candidate)}`",
        f"- Max active/control/OVERDOSE halo abs-z: `{max_active_z:.2f}` / `{max_control_z:.2f}` / `{max_slot_z:.2f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | halo signature | edge-bias signature | outlier | max z | strongest feature | value |",
        "|---|---|---|---|---:|---:|---|---:|",
    ]
    for row in sorted(rows, key=lambda item: item["maxHaloAbsZ"], reverse=True):
        strongest = row["strongestHaloZ"]
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | `{row['haloSignature']}` | `{row['edgeBiasSignature']}` | {int(row['haloOutlier'])} | {float(row['maxHaloAbsZ']):.2f} | `{strongest['feature']}` | `{float(strongest['value'] or 0.0):.3f}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_highlight_edge_halo_no_selector`",
            "- The active boxes show expected visible orange/black highlight-edge behavior, but there is no shared all-four halo carrier.",
            "- Color-sensitive halo signatures and ink edge-bias signatures are mixed or control-matched, and no source-backed unit/order/transform clue is present.",
            "",
            "## Next Move",
            "",
            "- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanHighlightEdgeHaloGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
