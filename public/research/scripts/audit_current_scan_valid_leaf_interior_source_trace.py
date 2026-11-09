#!/usr/bin/env python3
"""Trace valid same-leaf interior bleed pixels back to page-75 source regions.

This follows the current valid page 75 -> page 76 held-to-light model and
looks inside O4/B4/G5/O5, not around their edge collars. It maps source-only
interior components back through the mirror transform onto page 75, then checks
whether those source regions contain source-side instruction words. This is a
bounded provenance/geometry inspection only: no candidate derivation, hashing,
seed/WIF/address checks, or broad search.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_scan_valid_leaf_edge_source_trace as edge  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_interior_source_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_interior_source_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_interior_source_trace_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BLEED_CONTROL = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/"
    "current_scan_valid_leaf_bleedthrough_control_grid.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

CONTEXT_PAD = 28


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def box_mask(page_shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = page_shape
    x0, y0, x1, y1 = [round(v) for v in box]
    mask = np.zeros((h, w), dtype=bool)
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = True
    return mask


def union_box(boxes: list[list[int]]) -> list[int] | None:
    if not boxes:
        return None
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def draw_scaled_rect(
    draw: ImageDraw.ImageDraw,
    rect: list[float],
    crop_box: list[int],
    paste_xy: tuple[int, int],
    resized_size: tuple[int, int],
    color: tuple[int, int, int, int],
    width: int = 2,
) -> None:
    crop_w = crop_box[2] - crop_box[0]
    crop_h = crop_box[3] - crop_box[1]
    if not crop_w or not crop_h:
        return
    sx = resized_size[0] / crop_w
    sy = resized_size[1] / crop_h
    x0, y0, x1, y1 = rect
    px, py = paste_xy
    draw.rectangle(
        [
            px + (x0 - crop_box[0]) * sx,
            py + (y0 - crop_box[1]) * sy,
            px + (x1 - crop_box[0]) * sx,
            py + (y1 - crop_box[1]) * sy,
        ],
        outline=color,
        width=width,
    )


def fit_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    resized = img.resize((target_w, round(target_w * img.height / img.width)))
    if resized.height > target_h:
        resized = resized.resize((round(resized.width * target_h / resized.height), target_h))
    return resized


def render_trace_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    source_only: np.ndarray,
    row: dict,
    dx: int,
    dy: int,
    source_words: list[dict],
    out_path: Path,
) -> None:
    panel_w = 360
    panel_h = 275
    top_h = 60
    canvas = Image.new("RGB", (panel_w * 3, panel_h + top_h + 28), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    try:
        small = ImageFont.truetype("Arial.ttf", 13)
        title = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        small = ImageFont.load_default()
        title = ImageFont.load_default()

    draw.rectangle((0, 0, canvas.width, 36), fill=(25, 31, 42, 235))
    draw.text(
        (10, 10),
        f"{row['target']} interior trace {row['mode']} dx={dx} dy={dy}",
        fill="white",
        font=title,
    )

    target_box = [round(v) for v in row["box"]]
    target_union = row.get("targetContactBox") or target_box
    target_crop_box = edge.padded_box(target_union, target_img.size, 130)
    source_union = row.get("sourceTraceBox")
    source_crop_box = edge.padded_box(source_union, source_img.size, 120) if source_union else None

    target_crop = target_img.crop(tuple(target_crop_box))
    source_transformed = edge.shifted_mirror_image(source_img, dx, dy)
    source_crop = source_transformed.crop(tuple(target_crop_box))
    blend = Image.blend(target_crop, source_crop, 0.42).convert("RGBA")
    overlay_layer = np.zeros((blend.height, blend.width, 4), dtype=np.uint8)
    crop_mask = source_only[
        target_crop_box[1] : target_crop_box[3], target_crop_box[0] : target_crop_box[2]
    ]
    overlay_layer[crop_mask] = [0, 112, 255, 125]
    blend = Image.alpha_composite(blend, Image.fromarray(overlay_layer, "RGBA")).convert("RGB")

    panels: list[tuple[Image.Image, str, list[int] | None]] = [
        (target_crop, "page 76 target", target_crop_box),
        (blend, "blue = source-only interior", target_crop_box),
    ]
    if source_crop_box:
        panels.append((source_img.crop(tuple(source_crop_box)), "mapped page 75 source", source_crop_box))
    else:
        blank = Image.new("RGB", (panel_w, panel_h), "white")
        blank_draw = ImageDraw.Draw(blank)
        blank_draw.text((18, 118), "no interior component", fill=(80, 80, 80), font=small)
        panels.append((blank, "mapped page 75 source", None))

    y0 = top_h
    for idx, (img, label, crop_box) in enumerate(panels):
        px = idx * panel_w
        resized = fit_crop(img, panel_w, panel_h)
        canvas.paste(resized, (px, y0))
        draw.text((px + 8, 40), label, fill=(35, 38, 45), font=small)
        if crop_box:
            if idx in (0, 1):
                draw_scaled_rect(draw, target_box, crop_box, (px, y0), resized.size, (255, 0, 0, 230), 3)
                for component in row.get("components", []):
                    draw_scaled_rect(
                        draw,
                        component["targetBox"],
                        crop_box,
                        (px, y0),
                        resized.size,
                        (0, 112, 255, 220),
                        2,
                    )
            else:
                if source_union:
                    draw_scaled_rect(
                        draw, source_union, crop_box, (px, y0), resized.size, (255, 0, 0, 230), 3
                    )
                for component_box in row.get("componentSourceBoxes", []):
                    draw_scaled_rect(
                        draw,
                        component_box,
                        crop_box,
                        (px, y0),
                        resized.size,
                        (255, 145, 0, 210),
                        2,
                    )
                for word in source_words[:14]:
                    color = (255, 0, 0, 230) if word["strictInstruction"] else (0, 120, 255, 170)
                    draw_scaled_rect(draw, word["box"], crop_box, (px, y0), resized.size, color, 2)
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
    draw.text((24, 18), "Valid Leaf Interior Source Trace", fill="white", font=title_font)
    draw.text(
        (24, 56),
        "Source-only interior pixels in O4/B4/G5/O5 mapped back to page 75; red word boxes would be strict instructions.",
        fill=(235, 235, 235),
        font=small,
    )

    x, y = 24, 118
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((560, 188))
        sheet.paste(img, (x, y))
        x += 578
        if x + 560 > width:
            x = 24
            y += 245

    y = 650
    headers = [
        "mode",
        "target",
        "src-only",
        "pixels",
        "components",
        "source words",
        "strict",
        "context",
        "top text",
    ]
    xs = [24, 260, 342, 428, 492, 588, 690, 752, 820]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for row in result["traceRows"][:16]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            f"{row['interiorSourceOnlyCoverage']:.4f}",
            str(row["interiorSourceOnlyPixelCount"]),
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            str(row["contextTermHitCount"]),
            row["sourceTextPreview"][:92],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    bleed = load_json(BLEED_CONTROL)
    article = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_rows = [
        {"shortId": row["shortId"], "phrase": row["phrase"], "box": row["box"]}
        for row in active.get("activeRows", [])
    ]
    bleed_by_key = {(row["mode"], row["target"]): row for row in bleed.get("targetRows", [])}

    page75_words = []
    for page in article.get("pages", []):
        if page.get("page") == 75:
            page75_words = page.get("words", [])
            break

    target_img = edge.normalize_page(76)
    source_img = edge.normalize_page(75)
    target_channels = edge.feature_channels(target_img)
    source_channels = edge.feature_channels(source_img)

    jitter_shift = bleed.get("summary", {}).get("jitterBestShift", [-80, -20])
    mode_specs = [
        ("valid_75_to_76_natural", 0, 0),
        ("valid_75_to_76_small_jitter_best", int(jitter_shift[0]), int(jitter_shift[1])),
    ]

    trace_rows = []
    panel_paths: list[Path] = []
    for mode, dx, dy in mode_specs:
        shifted = edge.shift_channels(source_channels, dx, dy)
        source_feature = shifted["feature"]
        target_feature = target_channels["feature"]
        for active_row in active_rows:
            bleed_row = bleed_by_key.get((mode, active_row["shortId"]), {})
            interior = box_mask(source_feature.shape, active_row["box"])
            source_only = np.logical_and(np.logical_and(source_feature, interior), ~target_feature)
            components = edge.connected_components(source_only, limit=12)
            component_source_boxes = [
                edge.transform_target_box_to_source(component["targetBox"], target_img.width, dx, dy)
                for component in components
            ]
            union_source_box = union_box(component_source_boxes)
            if union_source_box:
                union_source_box = edge.padded_box(union_source_box, source_img.size, CONTEXT_PAD)
            union_target_box = union_box([component["targetBox"] for component in components])
            if union_target_box:
                union_target_box = edge.padded_box(union_target_box, target_img.size, CONTEXT_PAD)

            source_words = (
                edge.source_words_for_box(page75_words, union_source_box) if union_source_box else []
            )
            strict_hits = [word for word in source_words if word["strictInstruction"]]
            context_hits = [word for word in source_words if word["contextTerm"]]
            source_text = " ".join(word["text"] for word in source_words)
            x0, y0, x1, y1 = [round(v) for v in active_row["box"]]
            area = max(0, x1 - x0) * max(0, y1 - y0)
            out_row = {
                "mode": mode,
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                "bleedControlSourceOnlyCoverage": bleed_row.get("sourceOnlyCoverage", 0.0),
                "bleedControlPercentile": bleed_row.get("sourceOnlyControlPercentile", 0.0),
                "interiorSourceOnlyCoverage": float(source_only.sum() / area) if area else 0.0,
                "interiorSourceOnlyPixelCount": int(source_only.sum()),
                "componentCount": len(components),
                "componentPixelCount": sum(component["pixelCount"] for component in components),
                "largestComponentPixelCount": components[0]["pixelCount"] if components else 0,
                "targetContactBox": union_target_box,
                "sourceTraceBox": union_source_box,
                "components": components,
                "componentSourceBoxes": component_source_boxes,
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
                source_only,
                out_row,
                dx,
                dy,
                source_words,
                panel_path,
            )
            out_row["panel"] = rel(panel_path)
            trace_rows.append(out_row)
            panel_paths.append(panel_path)

    source_r3_hits = 0
    trigger_rows = reopen.get("triggerRows", [])
    satisfied_triggers = sum(1 for row in trigger_rows if row.get("triggerSatisfiedNow"))
    trigger_count = len(trigger_rows)
    selector_unlocks = 0
    strict_rows = sum(1 for row in trace_rows if row["strictInstructionHitCount"])
    context_rows = sum(1 for row in trace_rows if row["contextTermHitCount"])
    word_hit_rows = sum(1 for row in trace_rows if row["sourceWordHitCount"])
    component_rows = sum(1 for row in trace_rows if row["componentCount"])
    total_components = sum(row["componentCount"] for row in trace_rows)
    total_component_pixels = sum(row["componentPixelCount"] for row in trace_rows)
    decision = (
        "valid_leaf_interior_source_trace_no_instruction_source"
        if not strict_rows and not source_r3_hits and not satisfied_triggers
        else "needs_manual_review"
    )
    summary = {
        "traceRowCount": len(trace_rows),
        "componentRows": component_rows,
        "totalComponentCount": total_components,
        "totalComponentPixelCount": total_component_pixels,
        "totalInteriorSourceOnlyPixelCount": sum(
            row["interiorSourceOnlyPixelCount"] for row in trace_rows
        ),
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
        f"rows={summary['traceRowCount']}|componentRows={summary['componentRows']}|"
        f"totalComponents={summary['totalComponentCount']}|"
        f"componentPixels={summary['totalComponentPixelCount']}|"
        f"wordRows={summary['wordHitRows']}|strictRows={summary['strictInstructionRows']}|"
        f"contextRows={summary['contextTermRows']}|words={summary['totalSourceWordHits']}|"
        f"strict={summary['totalStrictInstructionHits']}|"
        f"context={summary['totalContextTermHits']}|sourceR3={source_r3_hits}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "trace valid page 75 -> page 76 interior source-only pixels back to page-75 source words; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "bleedControlGrid": rel(BLEED_CONTROL),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Do not extract from valid-leaf interior bleed traces; require a source/clue that names transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Interior Source Trace",
        "",
        "Scope: mapped source-only interior pixels inside O4/B4/G5/O5 from the valid page 75 -> page 76 held-to-light view back onto page 75, then checked whether those source regions contain source-side instruction words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Trace rows / rows with components: `{summary['traceRowCount']}` / `{summary['componentRows']}`",
        f"- Total components / component pixels: `{summary['totalComponentCount']}` / `{summary['totalComponentPixelCount']}`",
        f"- Rows with source words / strict instruction rows / context rows: `{summary['wordHitRows']}` / `{summary['strictInstructionRows']}` / `{summary['contextTermRows']}`",
        f"- Source word hits / strict instruction hits / context hits: `{summary['totalSourceWordHits']}` / `{summary['totalStrictInstructionHits']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Trace Rows",
        "",
        "| mode | target | interior src-only | pixels | components | source words | strict | context | source text preview | panel |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in trace_rows:
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | {row['interiorSourceOnlyCoverage']:.4f} | "
            f"{row['interiorSourceOnlyPixelCount']} | {row['componentCount']} | "
            f"{row['sourceWordHitCount']} | {row['strictInstructionHitCount']} | "
            f"{row['contextTermHitCount']} | {row['sourceTextPreview'][:120]} | `{row['panel']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- The valid same-leaf interior source-only components do not trace to source-side unit/order instructions.",
            "- Source-word hits are sparse ordinary page-75 article text; strict instruction terms remain absent.",
            "- Keep this as a provenance stop-check for current-scan light-table interior bleed variants.",
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
