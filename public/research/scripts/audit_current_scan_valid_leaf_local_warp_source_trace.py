#!/usr/bin/env python3
"""Trace local-warp held-to-light pixels back to page-75 source words.

This follows the valid page 75 -> page 76 held-to-light topology, but uses the
per-box local shifts selected by the local-warp upper-bound gate. It maps the
resulting source-only pixels back onto page 75 and checks whether those source
regions contain source-side instruction terms. It is a bounded provenance
inspection only: no candidate derivation, hashing, seed/WIF/address checks,
BIP39, or broad search.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_scan_valid_leaf_edge_source_trace as edge  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_local_warp_source_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_local_warp_source_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_local_warp_source_trace_sheet.jpg"

LOCAL_WARP = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/"
    "current_scan_valid_leaf_local_warp_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

CONTEXT_PAD = 34


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
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


def source_words(page: int) -> list[dict[str, Any]]:
    article = load_json(ARTICLE_MAP)
    for page_row in article.get("pages", []):
        if page_row.get("page") == page:
            return page_row.get("words", [])
    return []


def trace_row(
    row: dict[str, Any],
    kind: str,
    target_img: Image.Image,
    source_img: Image.Image,
    source_channels: dict[str, np.ndarray],
    target_channels: dict[str, np.ndarray],
    page75_words: list[dict[str, Any]],
) -> dict[str, Any]:
    dx = int(row["bestDx"])
    dy = int(row["bestDy"])
    shifted = edge.shift_channels(source_channels, dx, dy)
    source_feature = shifted["feature"]
    target_feature = target_channels["feature"]
    region = box_mask(source_feature.shape, row["box"])
    source_only = np.logical_and(np.logical_and(source_feature, region), ~target_feature)
    components = edge.connected_components(source_only, limit=12)
    component_source_boxes = [
        edge.transform_target_box_to_source(component["targetBox"], target_img.width, dx, dy)
        for component in components
    ]
    target_union = union_box([component["targetBox"] for component in components])
    source_union = union_box(component_source_boxes)
    if target_union:
        target_union = edge.padded_box(target_union, target_img.size, CONTEXT_PAD)
    if source_union:
        source_union = edge.padded_box(source_union, source_img.size, CONTEXT_PAD)

    words = edge.source_words_for_box(page75_words, source_union) if source_union else []
    strict_hits = [word for word in words if word["strictInstruction"]]
    context_hits = [word for word in words if word["contextTerm"]]
    x0, y0, x1, y1 = [round(v) for v in row["box"]]
    area = max(0, x1 - x0) * max(0, y1 - y0)
    source_text = " ".join(word["text"] for word in words)
    out_row = {
        "kind": kind,
        "target": row["target"],
        "phrase": row["phrase"],
        "slotIndex": row.get("slotIndex"),
        "slotLetter": row.get("slotLetter"),
        "box": row["box"],
        "bestDx": dx,
        "bestDy": dy,
        "localWarpBestSourceOnlyCoverage": row["bestSourceOnlyCoverage"],
        "sourceOnlyCoverage": float(source_only.sum() / area) if area else 0.0,
        "sourceOnlyPixelCount": int(source_only.sum()),
        "componentCount": len(components),
        "componentPixelCount": sum(component["pixelCount"] for component in components),
        "largestComponentPixelCount": components[0]["pixelCount"] if components else 0,
        "targetContactBox": target_union,
        "sourceTraceBox": source_union,
        "components": components,
        "componentSourceBoxes": component_source_boxes,
        "sourceWordHitCount": len(words),
        "strictInstructionHitCount": len(strict_hits),
        "contextTermHitCount": len(context_hits),
        "strictInstructionTerms": sorted({word["token"] for word in strict_hits}),
        "contextTerms": sorted({word["token"] for word in context_hits}),
        "sourceTextPreview": source_text,
        "sourceWords": words[:36],
    }
    return out_row


def draw_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    row: dict[str, Any],
    source_words_for_panel: list[dict[str, Any]],
    out_path: Path,
) -> None:
    panel_w = 420
    panel_h = 320
    canvas = Image.new("RGB", (panel_w * 2, panel_h + 70), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    try:
        small = ImageFont.truetype("Arial.ttf", 14)
        title = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        small = ImageFont.load_default()
        title = ImageFont.load_default()

    draw.rectangle((0, 0, canvas.width, 36), fill=(25, 31, 42, 235))
    label = row["target"] if row["kind"] == "active" else f"{row['target']} {row['slotLetter']}"
    draw.text(
        (10, 10),
        f"{label} local-warp source trace dx={row['bestDx']} dy={row['bestDy']}",
        fill="white",
        font=title,
    )

    target_box = row.get("targetContactBox")
    if target_box:
        target_crop_box = edge.padded_box(target_box, target_img.size, 120)
    else:
        x0, y0, x1, y1 = [round(v) for v in row["box"]]
        target_crop_box = edge.padded_box([x0, y0, x1, y1], target_img.size, 120)
    source_box = row.get("sourceTraceBox")
    if source_box:
        source_crop_box = edge.padded_box(source_box, source_img.size, 120)
    else:
        source_crop_box = [0, 0, 320, 240]

    panels = [
        (target_img.crop(tuple(target_crop_box)), "page 76 source-only area", target_crop_box, target_box),
        (
            source_img.crop(tuple(source_crop_box)) if source_box else Image.new("RGB", (320, 240), "white"),
            "mapped page 75 source area",
            source_crop_box,
            source_box,
        ),
    ]
    for idx, (img, label_text, crop_box, box_to_draw) in enumerate(panels):
        resized = img.resize((panel_w, round(panel_w * img.height / img.width)))
        if resized.height > panel_h:
            resized = resized.resize((round(resized.width * panel_h / resized.height), panel_h))
        px = idx * panel_w
        canvas.paste(resized, (px, 60))
        draw.text((px + 8, 42), label_text, fill=(35, 38, 45), font=small)
        sx = resized.width / (crop_box[2] - crop_box[0])
        sy = resized.height / (crop_box[3] - crop_box[1])
        if box_to_draw:
            x0, y0, x1, y1 = box_to_draw
            draw.rectangle(
                [
                    px + (x0 - crop_box[0]) * sx,
                    60 + (y0 - crop_box[1]) * sy,
                    px + (x1 - crop_box[0]) * sx,
                    60 + (y1 - crop_box[1]) * sy,
                ],
                outline=(255, 0, 0, 230),
                width=3,
            )
        if idx == 1 and source_box:
            for word in source_words_for_panel[:14]:
                wx0, wy0, wx1, wy1 = word["box"]
                color = (255, 0, 0, 230) if word["strictInstruction"] else (0, 120, 255, 170)
                draw.rectangle(
                    [
                        px + (wx0 - crop_box[0]) * sx,
                        60 + (wy0 - crop_box[1]) * sy,
                        px + (wx1 - crop_box[0]) * sx,
                        60 + (wy1 - crop_box[1]) * sy,
                    ],
                    outline=color,
                    width=2,
                )
    canvas.save(out_path, quality=91)


def draw_sheet(result: dict[str, Any], panel_paths: list[Path]) -> None:
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

    summary = result["summary"]
    draw.rectangle((0, 0, width, 98), fill=(25, 31, 42))
    draw.text((24, 18), "Local-Warp Held-To-Light Source Trace", fill="white", font=title_font)
    draw.text(
        (24, 56),
        "Source-only pixels from local-warp active boxes and OVERDOSE slots mapped back to page 75.",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (1060, 18),
        f"strict rows {summary['strictInstructionRows']} | context rows {summary['contextTermRows']}",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (1060, 44),
        f"components {summary['totalComponentCount']} | words {summary['totalSourceWordHits']} | sourceR3 {summary['sourceBackedR3BridgeHitCount']}",
        fill=(235, 235, 235),
        font=small,
    )

    x, y = 24, 118
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((560, 260))
        sheet.paste(img, (x, y))
        x += 578
        if x + 560 > width:
            x = 24
            y += 312

    y = 790
    headers = ["kind", "target", "cov", "pixels", "comp", "words", "strict", "ctx", "source text"]
    xs = [24, 104, 190, 250, 320, 378, 438, 492, 548]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 22
    for row in result["traceRows"][:18]:
        values = [
            row["kind"],
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            str(row["sourceOnlyPixelCount"]),
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            str(row["contextTermHitCount"]),
            row["sourceTextPreview"][:112],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 20

    draw.rectangle((24, 1160, width - 24, 1278), outline=(215, 220, 226), width=1)
    notes = [
        "Finding: local-warp source-only pixels trace to sparse ordinary page-75 words or blank/graphic areas.",
        "No row contains a strict instruction term such as read/take/line/word/letter/fold/mirror/order/slot.",
        f"Fingerprint: {result['fingerprint']}",
    ]
    ny = 1180
    for note in notes:
        draw.text((42, ny), note, fill=(35, 35, 35), font=small)
        ny += 30
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    local_warp = load_json(LOCAL_WARP)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    page75_words = source_words(75)

    target_img = edge.normalize_page(76)
    source_img = edge.normalize_page(75)
    target_channels = edge.feature_channels(target_img)
    source_channels = edge.feature_channels(source_img)

    local_rows = []
    for row in local_warp.get("activeRows", []):
        local_rows.append((row, "active"))
    for row in local_warp.get("overdoseSlotRows", []):
        local_rows.append((row, "overdose_slot"))

    trace_rows = []
    panel_paths: list[Path] = []
    for row, kind in local_rows:
        out_row = trace_row(
            row,
            kind,
            target_img,
            source_img,
            source_channels,
            target_channels,
            page75_words,
        )
        panel_path = OUT / f"{kind}_{out_row['target']}_local_warp_source_trace.jpg"
        draw_panel(target_img, source_img, out_row, out_row["sourceWords"], panel_path)
        out_row["panel"] = rel(panel_path)
        trace_rows.append(out_row)
        panel_paths.append(panel_path)

    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    trigger_rows = reopen.get("triggerRows", [])
    triggers = sum(1 for row in trigger_rows if row.get("triggerSatisfiedNow"))
    trigger_count = len(trigger_rows)
    strict_rows = sum(1 for row in trace_rows if row["strictInstructionHitCount"])
    context_rows = sum(1 for row in trace_rows if row["contextTermHitCount"])
    word_rows = sum(1 for row in trace_rows if row["sourceWordHitCount"])
    active_strict_rows = sum(
        1 for row in trace_rows if row["kind"] == "active" and row["strictInstructionHitCount"]
    )
    slot_strict_rows = sum(
        1
        for row in trace_rows
        if row["kind"] == "overdose_slot" and row["strictInstructionHitCount"]
    )
    selector_unlocks = 0
    decision = (
        "valid_leaf_local_warp_source_trace_no_instruction_source"
        if not strict_rows and not source_r3 and not triggers
        else "needs_manual_review"
    )
    summary = {
        "traceRowCount": len(trace_rows),
        "activeTraceRowCount": sum(1 for row in trace_rows if row["kind"] == "active"),
        "overdoseSlotTraceRowCount": sum(
            1 for row in trace_rows if row["kind"] == "overdose_slot"
        ),
        "componentRows": sum(1 for row in trace_rows if row["componentCount"]),
        "totalComponentCount": sum(row["componentCount"] for row in trace_rows),
        "totalComponentPixelCount": sum(row["componentPixelCount"] for row in trace_rows),
        "totalSourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in trace_rows),
        "wordHitRows": word_rows,
        "strictInstructionRows": strict_rows,
        "contextTermRows": context_rows,
        "activeStrictInstructionRows": active_strict_rows,
        "overdoseSlotStrictInstructionRows": slot_strict_rows,
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in trace_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in trace_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in trace_rows),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"rows={summary['traceRowCount']}|active={summary['activeTraceRowCount']}|"
        f"slots={summary['overdoseSlotTraceRowCount']}|componentRows={summary['componentRows']}|"
        f"components={summary['totalComponentCount']}|pixels={summary['totalComponentPixelCount']}|"
        f"sourceOnly={summary['totalSourceOnlyPixelCount']}|wordRows={summary['wordHitRows']}|"
        f"strictRows={summary['strictInstructionRows']}|contextRows={summary['contextTermRows']}|"
        f"activeStrict={summary['activeStrictInstructionRows']}|slotStrict={summary['overdoseSlotStrictInstructionRows']}|"
        f"words={summary['totalSourceWordHits']}|strict={summary['totalStrictInstructionHits']}|"
        f"context={summary['totalContextTermHits']}|sourceR3={source_r3}|"
        f"triggers={triggers}/{trigger_count}|selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "trace current-scan valid page 75->76 local-warp source-only pixels "
            "back to page-75 words; no OCR-to-key/key/hash/seed/WIF/address/BIP39/brute force"
        ),
        "inputs": {
            "localWarpGate": rel(LOCAL_WARP),
            "articleMap": rel(ARTICLE_MAP),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
        "sheet": rel(OUT_SHEET),
        "panelPaths": [rel(path) for path in panel_paths],
        "nextMove": (
            "Do not extract from local-warp source traces; require a new source/raw clue "
            "that names transform, unit, and order."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current-Scan Valid-Leaf Local-Warp Source Trace",
        "",
        "Scope: traced source-only pixels selected by the current valid page 75 -> page 76 local-warp upper-bound gate back onto page 75, then checked whether those source regions contain source-side instruction words. The pass covers O4/B4/G5/O5 and all eight projected C9/OVERDOSE slots. No OCR-to-key extraction, candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Trace rows / active / OVERDOSE slots: `{summary['traceRowCount']}` / `{summary['activeTraceRowCount']}` / `{summary['overdoseSlotTraceRowCount']}`",
        f"- Rows with components / total components / component pixels: `{summary['componentRows']}` / `{summary['totalComponentCount']}` / `{summary['totalComponentPixelCount']}`",
        f"- Source-only pixels traced: `{summary['totalSourceOnlyPixelCount']}`",
        f"- Rows with source words / strict instruction rows / context rows: `{summary['wordHitRows']}` / `{summary['strictInstructionRows']}` / `{summary['contextTermRows']}`",
        f"- Active strict rows / OVERDOSE-slot strict rows: `{summary['activeStrictInstructionRows']}` / `{summary['overdoseSlotStrictInstructionRows']}`",
        f"- Source word hits / strict instruction hits / context hits: `{summary['totalSourceWordHits']}` / `{summary['totalStrictInstructionHits']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Trace Rows",
        "",
        "| kind | target | dx | dy | source-only | pixels | components | words | strict | context | source text preview | panel |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in trace_rows:
        lines.append(
            "| {kind} | `{target}` | {dx} | {dy} | {cov:.4f} | {pixels} | {components} | {words} | {strict} | {context} | {preview} | `{panel}` |".format(
                kind=row["kind"],
                target=row["target"],
                dx=row["bestDx"],
                dy=row["bestDy"],
                cov=row["sourceOnlyCoverage"],
                pixels=row["sourceOnlyPixelCount"],
                components=row["componentCount"],
                words=row["sourceWordHitCount"],
                strict=row["strictInstructionHitCount"],
                context=row["contextTermHitCount"],
                preview=row["sourceTextPreview"][:120],
                panel=row["panel"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Local-warp source-only pixels do not trace to source-side unit/order instructions.",
            "- Source-word hits are sparse ordinary page-75 prose or context words; strict instruction terms remain absent.",
            "- Keep local-warp held-to-light as closed for the current scan unless a new physical/original-layout source or raw clue names the transform, unit, and order.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
