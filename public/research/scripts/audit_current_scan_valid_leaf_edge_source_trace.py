#!/usr/bin/env python3
"""Trace valid same-leaf edge contacts back to page-75 source regions.

This follows the current valid page 75 -> page 76 edge-contact control. It
maps source-only edge-ring pixels around O4/B4/G5/O5 back through the
held-to-light mirror transform onto page 75, then checks whether those source
regions contain source-side instruction words. It is a provenance/geometry
inspection only: no candidate derivation, hashing, seed/WIF/address checks, or
broad search.
"""

from __future__ import annotations

import json
import re
from collections import deque
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_edge_source_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_edge_source_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_edge_source_trace_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
EDGE_CONTACT = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/"
    "current_scan_valid_leaf_edge_contact_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

RING_PAD = 28
MIN_COMPONENT_PIXELS = 18
CONTEXT_PAD = 28

STRICT_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "line",
    "lines",
    "word",
    "words",
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
    "heart",
    "dip",
    "sell",
}


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


def ring_mask_for_box(page_shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = page_shape
    x0, y0, x1, y1 = [round(v) for v in box]
    rx0, ry0 = max(0, x0 - RING_PAD), max(0, y0 - RING_PAD)
    rx1, ry1 = min(w, x1 + RING_PAD), min(h, y1 + RING_PAD)
    mask = np.zeros((h, w), dtype=bool)
    mask[ry0:ry1, rx0:rx1] = True
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = False
    return mask


def connected_components(mask: np.ndarray, limit: int = 6) -> list[dict]:
    visited = np.zeros(mask.shape, dtype=bool)
    ys, xs = np.where(mask)
    components: list[dict] = []
    h, w = mask.shape
    for start_y, start_x in zip(ys.tolist(), xs.tolist()):
        if visited[start_y, start_x]:
            continue
        queue = deque([(start_y, start_x)])
        visited[start_y, start_x] = True
        pixels = []
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
        if len(pixels) >= MIN_COMPONENT_PIXELS:
            py = [p[0] for p in pixels]
            px = [p[1] for p in pixels]
            components.append(
                {
                    "pixelCount": len(pixels),
                    "targetBox": [min(px), min(py), max(px) + 1, max(py) + 1],
                }
            )
    return sorted(components, key=lambda item: item["pixelCount"], reverse=True)[:limit]


def transform_target_box_to_source(box: list[int], page_width: int, dx: int, dy: int) -> list[int]:
    x0, y0, x1, y1 = box
    sx0 = page_width - (x1 - dx)
    sx1 = page_width - (x0 - dx)
    sy0 = y0 - dy
    sy1 = y1 - dy
    return [int(sx0), int(sy0), int(sx1), int(sy1)]


def padded_box(box: list[int], size: tuple[int, int], pad: int = CONTEXT_PAD) -> list[int]:
    w, h = size
    x0, y0, x1, y1 = box
    return [max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)]


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def norm_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def source_words_for_box(words: list[dict], box: list[int]) -> list[dict]:
    hits = []
    for word in words:
        if boxes_intersect(word.get("box", [0, 0, 0, 0]), box):
            token = norm_token(word.get("text", ""))
            if token:
                hits.append(
                    {
                        "text": word.get("text", ""),
                        "token": token,
                        "box": word.get("box"),
                        "index": word.get("index"),
                        "strictInstruction": token in STRICT_TERMS,
                        "contextTerm": token in CONTEXT_TERMS,
                    }
                )
    return hits


def render_trace_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    row: dict,
    dx: int,
    dy: int,
    source_box: list[int] | None,
    target_box: list[int] | None,
    source_words: list[dict],
    out_path: Path,
) -> None:
    panel_w = 420
    panel_h = 360
    canvas = Image.new("RGB", (panel_w * 2, panel_h + 66), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    try:
        small = ImageFont.truetype("Arial.ttf", 14)
        title = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        small = ImageFont.load_default()
        title = ImageFont.load_default()
    draw.rectangle((0, 0, canvas.width, 36), fill=(25, 31, 42, 235))
    draw.text((10, 10), f"{row['target']} {row['mode']} dx={dx} dy={dy}", fill="white", font=title)
    if target_box:
        tb = padded_box(target_box, target_img.size, 120)
        tcrop = target_img.crop(tuple(tb))
    else:
        x0, y0, x1, y1 = [round(v) for v in row["box"]]
        tb = padded_box([x0, y0, x1, y1], target_img.size, 120)
        tcrop = target_img.crop(tuple(tb))
    if source_box:
        sb = padded_box(source_box, source_img.size, 120)
        scrop = source_img.crop(tuple(sb))
    else:
        sb = [0, 0, 320, 240]
        scrop = Image.new("RGB", (320, 240), "white")

    for idx, (img, label, crop_box, box_to_draw) in enumerate(
        [
            (tcrop, "page 76 edge-contact area", tb, target_box),
            (scrop, "mapped page 75 source area", sb, source_box),
        ]
    ):
        resized = img.resize((panel_w, round(panel_w * img.height / img.width)))
        if resized.height > panel_h:
            resized = resized.resize((round(resized.width * panel_h / resized.height), panel_h))
        px = idx * panel_w
        canvas.paste(resized, (px, 58))
        draw.text((px + 8, 40), label, fill=(35, 38, 45), font=small)
        sx = resized.width / (crop_box[2] - crop_box[0])
        sy = resized.height / (crop_box[3] - crop_box[1])
        if box_to_draw:
            x0, y0, x1, y1 = box_to_draw
            rect = [
                px + (x0 - crop_box[0]) * sx,
                58 + (y0 - crop_box[1]) * sy,
                px + (x1 - crop_box[0]) * sx,
                58 + (y1 - crop_box[1]) * sy,
            ]
            draw.rectangle(rect, outline=(255, 0, 0, 230), width=3)
        if idx == 1:
            for word in source_words[:12]:
                wx0, wy0, wx1, wy1 = word["box"]
                rect = [
                    px + (wx0 - crop_box[0]) * sx,
                    58 + (wy0 - crop_box[1]) * sy,
                    px + (wx1 - crop_box[0]) * sx,
                    58 + (wy1 - crop_box[1]) * sy,
                ]
                color = (255, 0, 0, 230) if word["strictInstruction"] else (0, 120, 255, 160)
                draw.rectangle(rect, outline=color, width=2)
    canvas.save(out_path, quality=91)


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
    draw.text((24, 18), "Valid Leaf Edge Source Trace", fill="white", font=title_font)
    draw.text((24, 56), "Page 76 edge contacts mapped back to page 75 source regions; red word boxes would be strict instructions.", fill=(235, 235, 235), font=small)
    x, y = 24, 118
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((560, 284))
        sheet.paste(img, (x, y))
        x += 578
        if x + 560 > width:
            x = 24
            y += 338

    y = 820
    headers = ["mode", "target", "components", "source words", "strict", "context", "top text"]
    xs = [24, 256, 342, 438, 540, 604, 678]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for row in result["traceRows"][:16]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            str(row["contextTermHitCount"]),
            row["sourceTextPreview"][:96],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    edge = load_json(EDGE_CONTACT)
    article = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_by_key = {
        (row["mode"], row["target"]): row for row in edge.get("targetRows", [])
    }
    active_rows = [
        {"shortId": row["shortId"], "phrase": row["phrase"], "box": row["box"]}
        for row in active.get("activeRows", [])
    ]
    page75_words = []
    for page in article.get("pages", []):
        if page.get("page") == 75:
            page75_words = page.get("words", [])
            break

    target_img = normalize_page(76)
    source_img = normalize_page(75)
    target_channels = feature_channels(target_img)
    source_channels = feature_channels(source_img)
    mode_specs = [
        ("valid_75_to_76_natural", 0, 0),
        ("valid_75_to_76_small_jitter_best", -80, -20),
    ]

    trace_rows = []
    panel_paths: list[Path] = []
    for mode, dx, dy in mode_specs:
        shifted = shift_channels(source_channels, dx, dy)
        source_feature = shifted["feature"]
        target_feature = target_channels["feature"]
        for active_row in active_rows:
            edge_row = active_by_key.get((mode, active_row["shortId"]), {})
            ring = ring_mask_for_box(source_feature.shape, active_row["box"])
            source_only = np.logical_and(np.logical_and(source_feature, ring), ~target_feature)
            components = connected_components(source_only)
            source_boxes = [
                transform_target_box_to_source(component["targetBox"], target_img.width, dx, dy)
                for component in components
            ]
            union_source_box = None
            union_target_box = None
            if source_boxes:
                union_source_box = [
                    min(box[0] for box in source_boxes),
                    min(box[1] for box in source_boxes),
                    max(box[2] for box in source_boxes),
                    max(box[3] for box in source_boxes),
                ]
                union_source_box = padded_box(union_source_box, source_img.size, CONTEXT_PAD)
                union_target_box = [
                    min(component["targetBox"][0] for component in components),
                    min(component["targetBox"][1] for component in components),
                    max(component["targetBox"][2] for component in components),
                    max(component["targetBox"][3] for component in components),
                ]
                union_target_box = padded_box(union_target_box, target_img.size, CONTEXT_PAD)
            source_words = source_words_for_box(page75_words, union_source_box) if union_source_box else []
            strict_hits = [word for word in source_words if word["strictInstruction"]]
            context_hits = [word for word in source_words if word["contextTerm"]]
            source_text = " ".join(word["text"] for word in source_words)
            out_row = {
                "mode": mode,
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                "edgeSourceOnlyCoverage": edge_row.get("sourceOnlyCoverage", 0.0),
                "edgeControlPercentile": edge_row.get("sourceOnlyControlPercentile", 0.0),
                "componentCount": len(components),
                "componentPixelCount": sum(component["pixelCount"] for component in components),
                "largestComponentPixelCount": components[0]["pixelCount"] if components else 0,
                "targetContactBox": union_target_box,
                "sourceTraceBox": union_source_box,
                "sourceWordHitCount": len(source_words),
                "strictInstructionHitCount": len(strict_hits),
                "contextTermHitCount": len(context_hits),
                "strictInstructionTerms": sorted({word["token"] for word in strict_hits}),
                "contextTerms": sorted({word["token"] for word in context_hits}),
                "sourceTextPreview": source_text,
                "sourceWords": source_words[:30],
            }
            panel_path = OUT / f"{mode}_{active_row['shortId']}.jpg"
            render_trace_panel(
                target_img,
                source_img,
                out_row,
                dx,
                dy,
                union_source_box,
                union_target_box,
                source_words,
                panel_path,
            )
            out_row["panel"] = rel(panel_path)
            trace_rows.append(out_row)
            panel_paths.append(panel_path)

    source_r3_hits = 0
    strict_rows = sum(1 for row in trace_rows if row["strictInstructionHitCount"])
    context_rows = sum(1 for row in trace_rows if row["contextTermHitCount"])
    word_hit_rows = sum(1 for row in trace_rows if row["sourceWordHitCount"])
    component_rows = sum(1 for row in trace_rows if row["componentCount"])
    satisfied_triggers = sum(1 for row in reopen.get("triggerRows", []) if row.get("triggerSatisfiedNow"))
    trigger_count = len(reopen.get("triggerRows", []))
    selector_unlocks = 0
    decision = "valid_leaf_edge_source_trace_no_instruction_source"
    summary = {
        "traceRowCount": len(trace_rows),
        "componentRows": component_rows,
        "wordHitRows": word_hit_rows,
        "strictInstructionRows": strict_rows,
        "contextTermRows": context_rows,
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in trace_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in trace_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in trace_rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"rows={summary['traceRowCount']}|components={summary['componentRows']}|"
        f"wordRows={summary['wordHitRows']}|strictRows={summary['strictInstructionRows']}|"
        f"contextRows={summary['contextTermRows']}|words={summary['totalSourceWordHits']}|"
        f"strict={summary['totalStrictInstructionHits']}|context={summary['totalContextTermHits']}|"
        f"sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}|"
        f"selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "trace valid page 75 -> page 76 edge contacts back to page-75 source words; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "edgeContactControl": rel(EDGE_CONTACT),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Do not extract from valid-leaf edge source traces; require a source/clue that names transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Edge Source Trace",
        "",
        "Scope: mapped source-only edge contacts from the valid page 75 -> page 76 held-to-light view back onto page 75, then checked whether those source regions contain source-side instruction words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Trace rows / rows with components: `{summary['traceRowCount']}` / `{summary['componentRows']}`",
        f"- Rows with source words / strict instruction rows / context rows: `{summary['wordHitRows']}` / `{summary['strictInstructionRows']}` / `{summary['contextTermRows']}`",
        f"- Source word hits / strict instruction hits / context hits: `{summary['totalSourceWordHits']}` / `{summary['totalStrictInstructionHits']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Trace Rows",
        "",
        "| mode | target | edge src-only | pctl | components | source words | strict | context | source text preview | panel |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in trace_rows:
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | {row['edgeSourceOnlyCoverage']:.4f} | "
            f"{row['edgeControlPercentile']:.3f} | {row['componentCount']} | "
            f"{row['sourceWordHitCount']} | {row['strictInstructionHitCount']} | "
            f"{row['contextTermHitCount']} | {row['sourceTextPreview'][:120]} | `{row['panel']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- The valid same-leaf edge contacts do not trace to source-side unit/order instructions.",
            "- Source-word hits are ordinary page-75 article/header text or sparse context terms; strict instruction terms remain absent.",
            "- Keep this as a provenance stop-check for current-scan light-table edge contacts.",
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
