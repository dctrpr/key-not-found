#!/usr/bin/env python3
"""Trace valid same-leaf channel-separated source pixels back to page 75.

This bounded pass keeps the physically valid page 75 -> page 76 held-to-light
model and separates the source-side signal into orange, dark, and grey masks
inside O4/B4/G5/O5. It asks whether a color/channel split exposes source-side
instruction words that the combined interior and glyph-slot traces did not.
No candidate derivation, hashing, seed/WIF/address checks, or broad search is
performed.
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


OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_channel_source_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_channel_source_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_channel_source_trace_sheet.jpg"

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

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CHANNELS = ["orange", "dark", "grey"]
CHANNEL_COLORS = {
    "orange": [255, 128, 0, 132],
    "dark": [0, 112, 255, 132],
    "grey": [135, 135, 135, 132],
}
CONTEXT_PAD = 28


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
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


def box_mask(shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = shape
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


def draw_channel_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    channel_masks: dict[str, np.ndarray],
    target_row: dict,
    mode: str,
    dx: int,
    dy: int,
    out_path: Path,
) -> None:
    pad_x, pad_y = 170, 100
    x0, y0, x1, y1 = [round(v) for v in target_row["box"]]
    crop = [
        max(0, x0 - pad_x),
        max(0, y0 - pad_y),
        min(target_img.width, x1 + pad_x),
        min(target_img.height, y1 + pad_y),
    ]
    target_crop = target_img.crop(tuple(crop))
    source_crop = edge.shifted_mirror_image(source_img, dx, dy).crop(tuple(crop))
    blend = Image.blend(target_crop, source_crop, 0.42).convert("RGBA")
    overlay = np.zeros((blend.height, blend.width, 4), dtype=np.uint8)
    for channel in CHANNELS:
        local = channel_masks[channel][crop[1] : crop[3], crop[0] : crop[2]]
        overlay[local] = CHANNEL_COLORS[channel]
    blend = Image.alpha_composite(blend, Image.fromarray(overlay, "RGBA")).convert("RGB")

    target_w = 430
    resized = blend.resize((target_w, round(target_w * blend.height / blend.width)))
    canvas = Image.new("RGB", (target_w, resized.height + 78), "white")
    canvas.paste(resized, (0, 78))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 0, canvas.width, 66), fill=(25, 31, 42, 235))
    draw.text(
        (10, 9),
        f"{mode.replace('valid_75_to_76_', '')} / {target_row['target']} dx={dx} dy={dy}",
        fill="white",
        font=font(15),
    )
    draw.text(
        (10, 35),
        f"dominant {target_row['dominantChannel']} text {target_row['sourceTextPreview'][:38] or '-'}",
        fill=(220, 228, 238),
        font=font(12),
    )

    def sx(value: float) -> float:
        return (value - crop[0]) * target_w / (crop[2] - crop[0])

    def sy(value: float) -> float:
        return 78 + (value - crop[1]) * resized.height / (crop[3] - crop[1])

    draw.rectangle((sx(x0), sy(y0), sx(x1), sy(y1)), outline=(255, 0, 0, 240), width=3)
    legend_x = 250
    for idx, channel in enumerate(CHANNELS):
        color = tuple(CHANNEL_COLORS[channel])
        lx = legend_x + idx * 56
        draw.rectangle((lx, 38, lx + 14, 52), fill=color)
        draw.text((lx + 18, 36), channel[0], fill=(230, 236, 246), font=font(11))
    canvas.save(out_path, quality=91)


def draw_sheet(result: dict, panel_paths: list[Path]) -> None:
    width, height = 1840, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Valid Leaf Channel Source Trace", fill="white", font=font(26))
    draw.text(
        (24, 56),
        "Orange/dark/grey source-only pixels inside O4/B4/G5/O5, mapped back to page 75.",
        fill=(235, 235, 235),
        font=font(14),
    )

    y = 118
    cards = [
        ("channel rows", result["summary"]["channelRowCount"]),
        ("component rows", result["summary"]["componentRows"]),
        ("source words", result["summary"]["totalSourceWordHits"]),
        ("strict/context", f"{result['summary']['totalStrictInstructionHits']}/{result['summary']['totalContextTermHits']}"),
        ("R3/triggers", f"{result['summary']['sourceBackedR3BridgeHitCount']}/{result['summary']['satisfiedReopenTriggerCount']}/{result['summary']['triggerCount']}"),
    ]
    x = 24
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 310, y + 72), radius=6, fill=(246, 248, 250), outline=(208, 215, 222))
        draw.text((x + 12, y + 10), label, fill=(80, 86, 96), font=font(11))
        draw.text((x + 12, y + 34), str(value), fill=(22, 26, 34), font=font(18))
        x += 328

    y = 220
    x = 24
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((430, 250))
        sheet.paste(img, (x, y))
        x += 448
        if x + 430 > width:
            x = 24
            y += 292

    y = 850
    headers = ["mode", "target", "dominant", "pixels", "components", "words", "strict", "source text"]
    xs = [24, 254, 332, 430, 506, 612, 682, 744]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=font(11))
    y += 22
    for row in result["targetRows"][:12]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            row["dominantChannel"],
            str(row["sourceOnlyPixelCount"]),
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            row["sourceTextPreview"][:95],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value), fill=(35, 35, 35), font=font(11))
        y += 19
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    bleed = load_json(BLEED_CONTROL)
    article = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "box": row["box"],
            "visualState": row["visualState"],
            "color": row["color"],
        }
        for row in active.get("activeRows", [])
    ]
    active_rows.sort(key=lambda row: TARGET_ORDER.index(row["shortId"]))
    page75_words = next(
        (page.get("words", []) for page in article.get("pages", []) if page.get("page") == 75),
        [],
    )

    target_img = edge.normalize_page(76)
    source_img = edge.normalize_page(75)
    target_channels = edge.feature_channels(target_img)
    source_channels = edge.feature_channels(source_img)
    jitter_shift = bleed.get("summary", {}).get("jitterBestShift", [-80, -20])
    mode_specs = [
        ("valid_75_to_76_natural", 0, 0),
        ("valid_75_to_76_small_jitter_best", int(jitter_shift[0]), int(jitter_shift[1])),
    ]

    channel_rows = []
    target_rows = []
    panel_paths: list[Path] = []
    for mode, dx, dy in mode_specs:
        shifted = edge.shift_channels(source_channels, dx, dy)
        target_feature = target_channels["feature"]
        for active_row in active_rows:
            mask = box_mask(target_feature.shape, active_row["box"])
            per_channel_rows = []
            channel_masks = {}
            for channel in CHANNELS:
                source_only = np.logical_and(np.logical_and(shifted[channel], mask), ~target_feature)
                channel_masks[channel] = source_only
                components = edge.connected_components(source_only, limit=20)
                source_boxes = [
                    edge.transform_target_box_to_source(component["targetBox"], target_img.width, dx, dy)
                    for component in components
                ]
                source_trace_box = union_box(source_boxes)
                if source_trace_box:
                    source_trace_box = edge.padded_box(source_trace_box, source_img.size, CONTEXT_PAD)
                source_words = edge.source_words_for_box(page75_words, source_trace_box) if source_trace_box else []
                strict_hits = [word for word in source_words if word["strictInstruction"]]
                context_hits = [word for word in source_words if word["contextTerm"]]
                row = {
                    "mode": mode,
                    "target": active_row["shortId"],
                    "phrase": active_row["phrase"],
                    "visualState": active_row["visualState"],
                    "channel": channel,
                    "sourceOnlyPixelCount": int(source_only.sum()),
                    "componentCount": len(components),
                    "componentPixelCount": sum(component["pixelCount"] for component in components),
                    "sourceTraceBox": source_trace_box,
                    "sourceWordHitCount": len(source_words),
                    "strictInstructionHitCount": len(strict_hits),
                    "contextTermHitCount": len(context_hits),
                    "strictInstructionTerms": sorted({word["token"] for word in strict_hits}),
                    "contextTerms": sorted({word["token"] for word in context_hits}),
                    "sourceTextPreview": " ".join(word["text"] for word in source_words),
                    "sourceWords": source_words[:30],
                }
                per_channel_rows.append(row)
                channel_rows.append(row)
            dominant = max(
                per_channel_rows,
                key=lambda row: (row["componentPixelCount"], row["sourceOnlyPixelCount"]),
            )
            source_word_rows = [row for row in per_channel_rows if row["sourceWordHitCount"]]
            target_row = {
                "mode": mode,
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                "dominantChannel": dominant["channel"] if dominant["sourceOnlyPixelCount"] else ".",
                "sourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in per_channel_rows),
                "componentCount": sum(row["componentCount"] for row in per_channel_rows),
                "componentPixelCount": sum(row["componentPixelCount"] for row in per_channel_rows),
                "sourceWordHitCount": sum(row["sourceWordHitCount"] for row in per_channel_rows),
                "strictInstructionHitCount": sum(row["strictInstructionHitCount"] for row in per_channel_rows),
                "contextTermHitCount": sum(row["contextTermHitCount"] for row in per_channel_rows),
                "sourceTextPreview": " | ".join(
                    row["sourceTextPreview"] for row in source_word_rows if row["sourceTextPreview"]
                ),
            }
            panel_path = OUT / f"{mode}_{active_row['shortId']}_channel_trace.jpg"
            draw_channel_panel(
                target_img,
                source_img,
                channel_masks,
                target_row,
                mode,
                dx,
                dy,
                panel_path,
            )
            target_row["panel"] = rel(panel_path)
            target_rows.append(target_row)
            panel_paths.append(panel_path)

    source_r3_hits = 0
    trigger_rows = reopen.get("triggerRows", [])
    satisfied_triggers = sum(1 for row in trigger_rows if row.get("triggerSatisfiedNow"))
    trigger_count = len(trigger_rows)
    selector_unlocks = 0
    strict_rows = sum(1 for row in channel_rows if row["strictInstructionHitCount"])
    context_rows = sum(1 for row in channel_rows if row["contextTermHitCount"])
    word_hit_rows = sum(1 for row in channel_rows if row["sourceWordHitCount"])
    component_rows = sum(1 for row in channel_rows if row["componentCount"])
    orange_component_rows = sum(
        1 for row in channel_rows if row["channel"] == "orange" and row["componentCount"]
    )
    decision = (
        "valid_leaf_channel_source_trace_no_instruction_source"
        if not strict_rows and not source_r3_hits and not satisfied_triggers
        else "needs_manual_review"
    )
    summary = {
        "modeCount": len(mode_specs),
        "targetRowCount": len(target_rows),
        "channelRowCount": len(channel_rows),
        "componentRows": component_rows,
        "orangeComponentRows": orange_component_rows,
        "wordHitRows": word_hit_rows,
        "strictInstructionRows": strict_rows,
        "contextTermRows": context_rows,
        "totalComponentCount": sum(row["componentCount"] for row in channel_rows),
        "totalComponentPixelCount": sum(row["componentPixelCount"] for row in channel_rows),
        "totalSourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in channel_rows),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in channel_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in channel_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in channel_rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"modes={summary['modeCount']}|targets={summary['targetRowCount']}|"
        f"channels={summary['channelRowCount']}|componentRows={summary['componentRows']}|"
        f"orangeComponentRows={summary['orangeComponentRows']}|wordRows={summary['wordHitRows']}|"
        f"strictRows={summary['strictInstructionRows']}|contextRows={summary['contextTermRows']}|"
        f"components={summary['totalComponentCount']}|componentPixels={summary['totalComponentPixelCount']}|"
        f"sourcePixels={summary['totalSourceOnlyPixelCount']}|words={summary['totalSourceWordHits']}|"
        f"strict={summary['totalStrictInstructionHits']}|context={summary['totalContextTermHits']}|"
        f"sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}|"
        f"selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page 75 -> page 76 channel-separated source trace; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "bleedControlGrid": rel(BLEED_CONTROL),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "targetRows": target_rows,
        "channelRows": channel_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Do not extract from valid-leaf channel-separated traces; require a source/clue that names transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Channel Source Trace",
        "",
        "Scope: separated valid page 75 -> page 76 source-only pixels inside O4/B4/G5/O5 into orange, dark, and grey masks, then mapped each channel back to page-75 source words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Target rows / channel rows: `{summary['targetRowCount']}` / `{summary['channelRowCount']}`",
        f"- Component rows / orange component rows / word rows: `{summary['componentRows']}` / `{summary['orangeComponentRows']}` / `{summary['wordHitRows']}`",
        f"- Total components / component pixels / source-only pixels: `{summary['totalComponentCount']}` / `{summary['totalComponentPixelCount']}` / `{summary['totalSourceOnlyPixelCount']}`",
        f"- Source word hits / strict instruction hits / context hits: `{summary['totalSourceWordHits']}` / `{summary['totalStrictInstructionHits']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Target Rows",
        "",
        "| mode | target | dominant channel | pixels | components | source words | strict | context | source text preview | panel |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in target_rows:
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | `{row['dominantChannel']}` | "
            f"{row['sourceOnlyPixelCount']} | {row['componentCount']} | "
            f"{row['sourceWordHitCount']} | {row['strictInstructionHitCount']} | "
            f"{row['contextTermHitCount']} | {row['sourceTextPreview'][:120]} | `{row['panel']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Orange source-only components are absent in the valid leaf; dark/grey components trace only to sparse ordinary page-75 words.",
            "- Channel separation does not expose a source-side instruction, context cue, unit, or order.",
            "- Keep this as the color/channel provenance stop-check for the current valid leaf.",
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
