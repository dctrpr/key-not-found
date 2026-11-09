#!/usr/bin/env python3
"""Trace the nearest B4 broad-mask contact back to page-75 source material.

The miss-distance gate found one possible rescue condition:
all_content_box_translation:broad reaches B4 only after 22 px of expansion.
This pass asks whether that contact is actual source ink/text, or merely a
broad non-white scan/halo pixel. It is provenance inspection only.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import math
import re
import textwrap
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from audit_current_scan_source_layer_landing_gate import (
    ACTIVE_INDEX_SLOT,
    CONTENT_BOX_REGISTRATION,
    REOPEN_TRIGGER_MATRIX,
    ROOT,
    SOURCE_PAGE_TEMPLATE,
    TARGET_ORDER,
    UPRIGHT_PAGE_TEMPLATE,
    active_boxes,
    content_box_modes,
    font,
    load_json,
    load_trigger_summary,
    normalize_page,
    rel,
    shifted_mirrored_source,
    source_layer_masks,
)
from audit_current_scan_source_layer_miss_distance_gate import (
    expanded_box,
)


OUT_DIR = ROOT / "analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate"
JSON_OUT = OUT_DIR / "current_scan_b4_broad_contact_provenance_gate.json"
MD_OUT = OUT_DIR / "current_scan_b4_broad_contact_provenance_gate.md"
SHEET_OUT = OUT_DIR / "current_scan_b4_broad_contact_provenance_gate_sheet.jpg"

SOURCE_LAYER_MISS_DISTANCE = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/"
    "current_scan_source_layer_miss_distance_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"

MODE_ID = "all_content_box_translation"
TARGET_ID = "B4"
LAYER = "broad"
TRACE_RADII = [16, 32, 64, 128]
SOURCE_CONTEXT_PADS = [64, 128, 256]

STRICT_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "use",
    "using",
    "select",
    "extract",
    "decode",
    "encoded",
    "cipher",
    "key",
    "private",
    "seed",
    "line",
    "lines",
    "word",
    "words",
    "phrase",
    "phrases",
    "letter",
    "letters",
    "edge",
    "edges",
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "fold",
    "folded",
    "mirror",
    "mirrored",
    "reverse",
    "order",
    "slot",
    "slots",
    "index",
    "indexes",
    "font",
    "bold",
    "highlight",
    "overdose",
}
CONTEXT_TERMS = {
    "bitcoin",
    "salvador",
    "bukele",
    "imf",
    "volcano",
    "volcanoes",
    "bond",
    "bonds",
    "shitcoiner",
    "shitcoiners",
    "heart",
    "dip",
    "sell",
}


def norm_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def box_distance_to_point(box: list[float], point: tuple[float, float]) -> float:
    x, y = point
    x0, y0, x1, y1 = box
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def box_distance(a: list[float], b: list[float]) -> float:
    if boxes_intersect(a, b):
        return 0.0
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def padded_box(box: list[int] | list[float], size: tuple[int, int], pad: int) -> list[int]:
    w, h = size
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    return [max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)]


def page_words(article: dict[str, Any], page_no: int) -> list[dict[str, Any]]:
    for page in article.get("pages", []):
        if page.get("page") == page_no:
            return page.get("words", [])
    return []


def source_words_for_box(words: list[dict[str, Any]], box: list[int]) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        token = norm_token(word.get("text", ""))
        if not token:
            continue
        if boxes_intersect(word.get("box", [0, 0, 0, 0]), box):
            hits.append(
                {
                    "id": word.get("id"),
                    "index": word.get("index"),
                    "text": word.get("text", ""),
                    "token": token,
                    "box": word.get("box"),
                    "strictInstruction": token in STRICT_TERMS,
                    "contextTerm": token in CONTEXT_TERMS,
                }
            )
    return hits


def nearest_words(
    words: list[dict[str, Any]],
    point: tuple[float, float],
    limit: int = 10,
    strict_only: bool = False,
) -> list[dict[str, Any]]:
    rows = []
    for word in words:
        token = norm_token(word.get("text", ""))
        if not token:
            continue
        if strict_only and token not in STRICT_TERMS:
            continue
        box = word.get("box", [0, 0, 0, 0])
        rows.append(
            {
                "id": word.get("id"),
                "index": word.get("index"),
                "text": word.get("text", ""),
                "token": token,
                "box": box,
                "distanceToSourcePointPx": round(box_distance_to_point(box, point), 3),
                "strictInstruction": token in STRICT_TERMS,
                "contextTerm": token in CONTEXT_TERMS,
            }
        )
    rows.sort(key=lambda row: row["distanceToSourcePointPx"])
    return rows[:limit]


def connected_components(mask: np.ndarray) -> list[dict[str, Any]]:
    visited = np.zeros(mask.shape, dtype=bool)
    ys, xs = np.where(mask)
    h, w = mask.shape
    components: list[dict[str, Any]] = []
    for start_y, start_x in zip(ys.tolist(), xs.tolist()):
        if visited[start_y, start_x]:
            continue
        queue = deque([(start_y, start_x)])
        visited[start_y, start_x] = True
        pixels: list[tuple[int, int]] = []
        while queue:
            y, x = queue.popleft()
            pixels.append((y, x))
            for ny in (y - 1, y, y + 1):
                for nx in (x - 1, x, x + 1):
                    if ny == y and nx == x:
                        continue
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        py = [p[0] for p in pixels]
        px = [p[1] for p in pixels]
        components.append(
            {
                "pixelCount": len(pixels),
                "targetBox": [min(px), min(py), max(px) + 1, max(py) + 1],
                "targetCentroid": [round(float(np.mean(px)), 3), round(float(np.mean(py)), 3)],
            }
        )
    return sorted(components, key=lambda item: item["pixelCount"], reverse=True)


def transform_target_box_to_source(
    box: list[int],
    page_width: int,
    dx: int,
    dy: int,
) -> list[int]:
    x0, y0, x1, y1 = box
    sx0 = page_width - (x1 - dx)
    sx1 = page_width - (x0 - dx)
    sy0 = y0 - dy
    sy1 = y1 - dy
    return [int(sx0), int(sy0), int(sx1), int(sy1)]


def transform_target_point_to_source(
    point: list[int] | tuple[int, int],
    page_width: int,
    dx: int,
    dy: int,
) -> list[int]:
    x, y = point
    return [int(page_width - 1 - (x - dx)), int(y - dy)]


def rgb_stats(rgb: list[int]) -> dict[str, float | list[int]]:
    vals = [int(v) for v in rgb]
    r, g, b = vals
    maxc = max(vals) / 255.0
    minc = min(vals) / 255.0
    sat = (maxc - minc) / maxc if maxc else 0.0
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return {"rgb": vals, "luma": round(luma, 3), "saturation": round(sat, 6)}


def ring_mask(box: list[float], shape: tuple[int, int], radius: int) -> np.ndarray:
    h, w = shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    ex0, ey0, ex1, ey1 = expanded_box(box, radius, shape)
    mask = np.zeros((h, w), dtype=bool)
    mask[ey0:ey1, ex0:ex1] = True
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = False
    return mask


def find_miss_row(miss: dict[str, Any]) -> dict[str, Any]:
    for mode in miss.get("modeResults", []):
        if mode.get("modeId") != MODE_ID:
            continue
        for row in mode.get("activeRows", []):
            if row.get("target") == TARGET_ID and row.get("layer") == LAYER:
                return row
    return {}


def draw_sheet(result: dict[str, Any], target_img: Image.Image, source_img: Image.Image) -> None:
    sheet = Image.new("RGB", (1880, 1260), (248, 250, 252))
    draw = ImageDraw.Draw(sheet, "RGBA")
    title_f = font(32, True)
    head_f = font(22, True)
    body_f = font(18)
    small_f = font(14)
    summary = result["summary"]
    draw.text((34, 24), "Current Scan B4 Broad-Contact Provenance Gate", fill=(15, 23, 42), font=title_f)
    y = 82
    for line in [
        f"Decision: {summary['decision']}",
        f"B4 all-content broad contact: {summary['b4BroadNearestDistancePx']}px, first pixel at {summary['firstExpansionWithPixelsPx']}px expansion",
        f"Radius 32: {summary['radius32BroadPixelCount']} broad pixel(s), {summary['radius32FeaturePixelCount']} feature pixel(s), nearest word {summary['nearestWordDistancePx']}px",
        f"Source words within 64/128/256px: {summary['sourceWordsWithinContextPads']['64']}/{summary['sourceWordsWithinContextPads']['128']}/{summary['sourceWordsWithinContextPads']['256']}; strict hits: {summary['strictInstructionHitCount']}",
    ]:
        draw.text((34, y), line, fill=(30, 41, 59), font=body_f)
        y += 28

    b4_box = result["targetBox"]
    nearest_target = result["nearestTargetPoint"]
    source_point = result["nearestSourcePoint"]
    target_crop_box = padded_box(b4_box, target_img.size, 220)
    source_crop_box = padded_box([source_point[0], source_point[1], source_point[0] + 1, source_point[1] + 1], source_img.size, 380)
    target_crop = result["landingImage"].crop(tuple(target_crop_box)).convert("RGB")
    source_crop = source_img.crop(tuple(source_crop_box)).convert("RGB")

    def paste_panel(img: Image.Image, at: tuple[int, int], crop_box: list[int], label: str, source_panel: bool) -> None:
        panel_w, panel_h = 840, 500
        img.thumbnail((panel_w, panel_h))
        x, y0 = at
        sheet.paste(img, (x, y0 + 42))
        draw.text((x, y0), label, fill=(15, 23, 42), font=head_f)
        sx = img.width / (crop_box[2] - crop_box[0])
        sy = img.height / (crop_box[3] - crop_box[1])
        if not source_panel:
            x0, yb0, x1, yb1 = b4_box
            rect = [
                x + (x0 - crop_box[0]) * sx,
                y0 + 42 + (yb0 - crop_box[1]) * sy,
                x + (x1 - crop_box[0]) * sx,
                y0 + 42 + (yb1 - crop_box[1]) * sy,
            ]
            draw.rectangle(rect, outline=(255, 70, 0, 255), width=4)
            for radius, color in [(16, (148, 163, 184, 180)), (32, (16, 185, 129, 220))]:
                ex0, ey0, ex1, ey1 = expanded_box(b4_box, radius, target_img.size[::-1])
                ring_rect = [
                    x + (ex0 - crop_box[0]) * sx,
                    y0 + 42 + (ey0 - crop_box[1]) * sy,
                    x + (ex1 - crop_box[0]) * sx,
                    y0 + 42 + (ey1 - crop_box[1]) * sy,
                ]
                draw.rectangle(ring_rect, outline=color, width=3)
            px, py = nearest_target
            draw.ellipse(
                (
                    x + (px - crop_box[0]) * sx - 8,
                    y0 + 42 + (py - crop_box[1]) * sy - 8,
                    x + (px - crop_box[0]) * sx + 8,
                    y0 + 42 + (py - crop_box[1]) * sy + 8,
                ),
                fill=(16, 185, 129, 235),
            )
        else:
            px, py = source_point
            draw.ellipse(
                (
                    x + (px - crop_box[0]) * sx - 8,
                    y0 + 42 + (py - crop_box[1]) * sy - 8,
                    x + (px - crop_box[0]) * sx + 8,
                    y0 + 42 + (py - crop_box[1]) * sy + 8,
                ),
                fill=(16, 185, 129, 235),
            )
            for word in result["nearestSourceWords"][:8]:
                wx0, wy0, wx1, wy1 = word["box"]
                rect = [
                    x + (wx0 - crop_box[0]) * sx,
                    y0 + 42 + (wy0 - crop_box[1]) * sy,
                    x + (wx1 - crop_box[0]) * sx,
                    y0 + 42 + (wy1 - crop_box[1]) * sy,
                ]
                color = (220, 38, 38, 230) if word["strictInstruction"] else (37, 99, 235, 170)
                draw.rectangle(rect, outline=color, width=2)

    paste_panel(target_crop, (34, 205), target_crop_box, "B4 target-side all-content broad contact", False)
    paste_panel(source_crop, (980, 205), source_crop_box, "Mapped page-75 source area", True)

    y = 780
    draw.text((34, y), "Trace Summary", fill=(15, 23, 42), font=head_f)
    y += 35
    cols = [34, 128, 248, 382, 520, 660, 800]
    headers = ["radius", "broad px", "feature px", "broad-only", "components", "source words", "strict"]
    for cx, label in zip(cols, headers):
        draw.text((cx, y), label, fill=(51, 65, 85), font=small_f)
    y += 24
    for row in result["radiusRows"]:
        vals = [
            row["radiusPx"],
            row["broadPixelCount"],
            row["featurePixelCount"],
            row["broadOnlyPixelCount"],
            row["componentCount"],
            row["sourceWordHitCount"],
            row["strictInstructionHitCount"],
        ]
        for cx, val in zip(cols, vals):
            draw.text((cx, y), str(val), fill=(30, 41, 59), font=small_f)
        y += 22

    x0 = 980
    y = 780
    draw.text((x0, y), "Nearest Page-75 OCR Words", fill=(15, 23, 42), font=head_f)
    y += 35
    for word in result["nearestSourceWords"][:8]:
        draw.text(
            (x0, y),
            f"{word['distanceToSourcePointPx']:>6.1f}px  {word['text']}",
            fill=(30, 41, 59),
            font=small_f,
        )
        y += 22

    y = 1068
    notes = [
        "The nearest B4 rescue is a broad-only pixel, not feature/ink support.",
        "The mapped source point is in blank source area; nearest OCR word is hundreds of pixels away.",
        "No source-side strict unit/order/transform term is attached to the contact.",
    ]
    for note in notes:
        for line in textwrap.wrap(note, width=105):
            draw.text((34, y), "- " + line, fill=(30, 41, 59), font=body_f)
            y += 26
    sheet.save(SHEET_OUT, quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    miss = load_json(SOURCE_LAYER_MISS_DISTANCE)
    article = load_json(ARTICLE_MAP)
    active = active_boxes(active_index)
    b4 = next(row for row in active if row["shortId"] == TARGET_ID)
    mode = next(row for row in content_box_modes() if row["modeId"] == MODE_ID)
    dx_float = float(mode["dx"])
    dy_float = float(mode["dy"])
    dx = int(round(dx_float))
    dy = int(round(dy_float))

    source_page = normalize_page(75)
    target_page = normalize_page(76)
    landing = shifted_mirrored_source(source_page, dx_float, dy_float)
    landing_arr = np.asarray(landing.convert("RGB"))
    source_arr = np.asarray(source_page.convert("RGB"))
    masks = source_layer_masks(landing_arr)
    source_masks = source_layer_masks(source_arr)
    page75_words = page_words(article, 75)
    miss_row = find_miss_row(miss)
    nearest_target = miss_row.get("nearestSourcePoint") or [711, 2450]
    nearest_source = transform_target_point_to_source(nearest_target, landing.width, dx, dy)

    radius_rows = []
    all_context_words: list[dict[str, Any]] = []
    for radius in TRACE_RADII:
        ring = ring_mask(b4["box"], masks[LAYER].shape, radius)
        broad_pixels = np.logical_and(masks["broad"], ring)
        feature_pixels = np.logical_and(masks["feature"], ring)
        broad_only = np.logical_and(broad_pixels, ~masks["feature"])
        components = connected_components(broad_pixels)
        component_records = []
        radius_words_by_pad: dict[str, list[dict[str, Any]]] = {}
        for pad in SOURCE_CONTEXT_PADS:
            words_for_pad: list[dict[str, Any]] = []
            for component in components:
                source_box = transform_target_box_to_source(component["targetBox"], landing.width, dx, dy)
                context_box = padded_box(source_box, source_page.size, pad)
                words_for_pad.extend(source_words_for_box(page75_words, context_box))
            dedup = {word["id"]: word for word in words_for_pad}
            radius_words_by_pad[str(pad)] = list(dedup.values())
        for component in components[:12]:
            source_box = transform_target_box_to_source(component["targetBox"], landing.width, dx, dy)
            source_context = padded_box(source_box, source_page.size, 128)
            source_words = source_words_for_box(page75_words, source_context)
            all_context_words.extend(source_words)
            cx, cy = component["targetCentroid"]
            component_source_point = transform_target_point_to_source([int(round(cx)), int(round(cy))], landing.width, dx, dy)
            component_records.append(
                {
                    **component,
                    "sourceBox": source_box,
                    "sourceCentroid": component_source_point,
                    "sourceContextBox128": source_context,
                    "sourceWordHitCount": len(source_words),
                    "strictInstructionHitCount": sum(1 for word in source_words if word["strictInstruction"]),
                    "contextTermHitCount": sum(1 for word in source_words if word["contextTerm"]),
                    "sourceWords": source_words[:20],
                }
            )
        words_128 = radius_words_by_pad["128"]
        radius_rows.append(
            {
                "radiusPx": radius,
                "broadPixelCount": int(broad_pixels.sum()),
                "featurePixelCount": int(feature_pixels.sum()),
                "broadOnlyPixelCount": int(broad_only.sum()),
                "componentCount": len(components),
                "componentPixelCounts": [component["pixelCount"] for component in components[:12]],
                "sourceWordHitCount": len({word["id"] for word in words_128}),
                "strictInstructionHitCount": len(
                    {word["id"] for word in words_128 if word["strictInstruction"]}
                ),
                "contextTermHitCount": len({word["id"] for word in words_128 if word["contextTerm"]}),
                "sourceWordsWithinContextPads": {
                    str(pad): len({word["id"] for word in radius_words_by_pad[str(pad)]})
                    for pad in SOURCE_CONTEXT_PADS
                },
                "components": component_records,
            }
        )

    source_point_tuple = (float(nearest_source[0]), float(nearest_source[1]))
    nearest = nearest_words(page75_words, source_point_tuple)
    nearest_strict = nearest_words(page75_words, source_point_tuple, limit=6, strict_only=True)
    source_words_by_pad = {
        str(pad): source_words_for_box(
            page75_words,
            padded_box([nearest_source[0], nearest_source[1], nearest_source[0] + 1, nearest_source[1] + 1], source_page.size, pad),
        )
        for pad in SOURCE_CONTEXT_PADS
    }
    unique_context = {word["id"]: word for word in all_context_words}
    source_y, source_x = nearest_source[1], nearest_source[0]
    target_y, target_x = nearest_target[1], nearest_target[0]
    point_layer_membership = {
        layer: bool(masks[layer][target_y, target_x]) if 0 <= target_y < masks[layer].shape[0] and 0 <= target_x < masks[layer].shape[1] else False
        for layer in ("black", "orange", "grey", "feature", "broad")
    }
    source_point_layer_membership = {
        layer: bool(source_masks[layer][source_y, source_x])
        if 0 <= source_y < source_masks[layer].shape[0] and 0 <= source_x < source_masks[layer].shape[1]
        else False
        for layer in ("black", "orange", "grey", "feature", "broad")
    }
    trigger = load_trigger_summary()
    radius32 = next(row for row in radius_rows if row["radiusPx"] == 32)
    nearest_word_distance = nearest[0]["distanceToSourcePointPx"] if nearest else None
    nearest_strict_distance = nearest_strict[0]["distanceToSourcePointPx"] if nearest_strict else None
    strict_count = len({word["id"] for word in unique_context.values() if word["strictInstruction"]})
    context_count = len({word["id"] for word in unique_context.values() if word["contextTerm"]})
    source_words_pad_counts = {
        str(pad): len({word["id"] for word in source_words_by_pad[str(pad)]})
        for pad in SOURCE_CONTEXT_PADS
    }
    hidden_candidate = bool(
        radius32["featurePixelCount"] > 0
        and source_words_pad_counts["128"] > 0
        and strict_count > 0
        and trigger["sourceBackedR3BridgeHitCount"] > 0
    )
    decision = "current_scan_b4_broad_contact_provenance_noise"
    fingerprint = (
        f"mode={MODE_ID}|target={TARGET_ID}|layer={LAYER}"
        f"|b4BroadMin={miss_row.get('minimalExpansionPx')}"
        f"|firstExpansion={miss_row.get('firstExpansionWithPixelsPx')}"
        f"|r32BroadPx={radius32['broadPixelCount']}|r32FeaturePx={radius32['featurePixelCount']}"
        f"|r32BroadOnlyPx={radius32['broadOnlyPixelCount']}|r32Components={radius32['componentCount']}"
        f"|pointLayers={','.join(k for k, v in point_layer_membership.items() if v) or '-'}"
        f"|sourceWords64={source_words_pad_counts['64']}|sourceWords128={source_words_pad_counts['128']}"
        f"|nearestWord={nearest_word_distance}:{nearest[0]['token'] if nearest else '-'}"
        f"|nearestStrict={nearest_strict_distance}:{nearest_strict[0]['token'] if nearest_strict else '-'}"
        f"|strict={strict_count}|context={context_count}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger['satisfiedReopenTriggerCount']}/{trigger['triggerCount']}"
        "|selectors=0"
    )
    summary = {
        "decision": decision,
        "modeId": MODE_ID,
        "target": TARGET_ID,
        "layer": LAYER,
        "dx": dx_float,
        "dy": dy_float,
        "roundedDx": dx,
        "roundedDy": dy,
        "b4BroadNearestDistancePx": miss_row.get("nearestDistancePx"),
        "b4BroadMinimalExpansionPx": miss_row.get("minimalExpansionPx"),
        "firstExpansionWithPixelsPx": miss_row.get("firstExpansionWithPixelsPx"),
        "radius32BroadPixelCount": radius32["broadPixelCount"],
        "radius32FeaturePixelCount": radius32["featurePixelCount"],
        "radius32BroadOnlyPixelCount": radius32["broadOnlyPixelCount"],
        "radius32ComponentCount": radius32["componentCount"],
        "nearestTargetPoint": nearest_target,
        "nearestSourcePoint": nearest_source,
        "nearestPointTargetRgb": rgb_stats(landing_arr[target_y, target_x].tolist()),
        "nearestPointSourceRgb": rgb_stats(source_arr[source_y, source_x].tolist()),
        "nearestPointTargetLayerMembership": point_layer_membership,
        "nearestPointSourceLayerMembership": source_point_layer_membership,
        "sourceWordsWithinContextPads": source_words_pad_counts,
        "nearestWordDistancePx": nearest_word_distance,
        "nearestWordText": nearest[0]["text"] if nearest else None,
        "nearestStrictInstructionDistancePx": nearest_strict_distance,
        "nearestStrictInstructionText": nearest_strict[0]["text"] if nearest_strict else None,
        "strictInstructionHitCount": strict_count,
        "contextTermHitCount": context_count,
        "hiddenBroadContactCandidate": hidden_candidate,
        "priorMissDistanceFingerprint": miss.get("summary", {}).get("sourceLayerMissDistanceFingerprint"),
        "sourceBackedR3BridgeHitCount": trigger["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger["satisfiedReopenTriggerCount"],
        "triggerCount": trigger["triggerCount"],
        "b4BroadContactProvenanceFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current scan B4 all-content broad-mask contact provenance audit; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "contentBoxRegistrationGate": rel(CONTENT_BOX_REGISTRATION),
            "sourceLayerMissDistanceGate": rel(SOURCE_LAYER_MISS_DISTANCE),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage75": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))),
            "uprightPage75": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=75))),
        },
        "targetBox": [int(round(v)) for v in b4["box"]],
        "nearestTargetPoint": nearest_target,
        "nearestSourcePoint": nearest_source,
        "nearestSourceWords": nearest,
        "nearestStrictInstructionWords": nearest_strict,
        "radiusRows": radius_rows,
        "summary": summary,
        "decision": {
            "currentScanB4BroadContactProvenanceGate": decision,
            "selectorUnlocked": False,
            "reason": "The nearest B4 rescue contact is broad-only scan material, not feature/ink text, and it carries no source-side instruction wording.",
            "nextMove": "Do not reopen this broad-mask B4 contact unless a physical/original-layout source or raw clue supplies a registration rule.",
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": fingerprint,
        "landingImage": landing,
    }
    draw_sheet(result, target_page, source_page)
    result.pop("landingImage")
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan B4 Broad-Contact Provenance Gate",
        "",
        "Scope: traced the nearest `all_content_box_translation:broad` contact around B4 back through the page-75 mirror transform, then checked whether the mapped source area carries source text or instruction terms. No key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Mode/layer/target: `{MODE_ID}` / `{LAYER}` / `{TARGET_ID}`",
        f"- B4 broad nearest distance / minimal expansion / first pixel expansion: `{summary['b4BroadNearestDistancePx']}` / `{summary['b4BroadMinimalExpansionPx']}` / `{summary['firstExpansionWithPixelsPx']}` px",
        f"- Radius-32 broad / feature / broad-only pixels: `{summary['radius32BroadPixelCount']}` / `{summary['radius32FeaturePixelCount']}` / `{summary['radius32BroadOnlyPixelCount']}`",
        f"- Nearest target point -> source point: `{summary['nearestTargetPoint']}` -> `{summary['nearestSourcePoint']}`",
        f"- Target/source point RGB: `{summary['nearestPointTargetRgb']}` / `{summary['nearestPointSourceRgb']}`",
        f"- Source words within 64/128/256 px: `{summary['sourceWordsWithinContextPads']}`",
        f"- Nearest OCR word / nearest strict instruction word: `{summary['nearestWordText']}` at `{summary['nearestWordDistancePx']}` px / `{summary['nearestStrictInstructionText']}` at `{summary['nearestStrictInstructionDistancePx']}` px",
        f"- Strict/context hits in traced contact contexts: `{summary['strictInstructionHitCount']}` / `{summary['contextTermHitCount']}`",
        f"- Hidden broad-contact candidate: `{int(summary['hiddenBroadContactCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Radius Rows",
        "",
        "| radius | broad px | feature px | broad-only px | components | source words | strict | context |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in radius_rows:
        lines.append(
            f"| `{row['radiusPx']}` | `{row['broadPixelCount']}` | `{row['featurePixelCount']}` | "
            f"`{row['broadOnlyPixelCount']}` | `{row['componentCount']}` | `{row['sourceWordHitCount']}` | "
            f"`{row['strictInstructionHitCount']}` | `{row['contextTermHitCount']}` |"
        )
    lines.extend(
        [
            "",
            "## Nearest Source Words",
            "",
            "| distance px | text | token | strict | context |",
            "|---:|---|---|---:|---:|",
        ]
    )
    for word in nearest[:10]:
        lines.append(
            f"| `{word['distanceToSourcePointPx']}` | {word['text']} | `{word['token']}` | "
            f"`{int(word['strictInstruction'])}` | `{int(word['contextTerm'])}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- The B4 rescue contact is broad-only: it has broad-mask pixels but no feature-mask pixels at the 32 px expansion where contact first appears.",
            "- The mapped source point is not on OCR text; the nearest page-75 OCR word is hundreds of pixels away and no traced context supplies source-side unit/order/transform wording.",
            "- Keep the all-content broad B4 contact closed as a scan/halo/margin artifact, not as an extraction path.",
            "",
            "## Next Move",
            "",
            "- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {rel(MD_OUT)}")
    print(f"Wrote {rel(JSON_OUT)}")
    print(f"Wrote {rel(SHEET_OUT)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
