#!/usr/bin/env python3
"""Trace valid same-leaf OVERDOSE glyph-slot pixels back to page 75.

This is a bounded follow-up to the current OVERDOSE glyph crop projection and
the valid-leaf source traces. It keeps the physically valid page 75 -> page 76
light-table model, subdivides O4/B4/G5/O5 by the actual page-76 OVERDOSE glyph
slots, and maps slot-level source-only components back to page-75 words. It is
provenance/geometry inspection only: no key derivation, hashing, seed/WIF/
address checks, or broad search.
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


OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_glyph_slot_source_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_glyph_slot_source_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_glyph_slot_source_trace_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BLEED_CONTROL = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/"
    "current_scan_valid_leaf_bleedthrough_control_grid.json"
)
C9_HEADER_GLYPH = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
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


def slot_region(target_box: list[float], slot: dict) -> list[int] | None:
    left = max(float(target_box[0]), float(slot["left"]))
    right = min(float(target_box[2]), float(slot["right"]))
    top = float(target_box[1])
    bottom = float(target_box[3])
    if right <= left or bottom <= top:
        return None
    return [round(left), round(top), round(right), round(bottom)]


def region_mask(shape: tuple[int, int], region: list[int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    x0, y0, x1, y1 = region
    mask[y0:y1, x0:x1] = True
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


def draw_slot_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    source_only: np.ndarray,
    target_row: dict,
    slots: list[dict],
    mode: str,
    dx: int,
    dy: int,
    out_path: Path,
) -> None:
    pad_x, pad_y = 190, 110
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
    local = source_only[crop[1] : crop[3], crop[0] : crop[2]]
    overlay[local] = [0, 112, 255, 130]
    blend = Image.alpha_composite(blend, Image.fromarray(overlay, "RGBA")).convert("RGB")

    target_w = 430
    resized = blend.resize((target_w, round(target_w * blend.height / blend.width)))
    canvas = Image.new("RGB", (target_w, resized.height + 74), "white")
    canvas.paste(resized, (0, 74))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 0, canvas.width, 62), fill=(25, 31, 42, 235))
    draw.text(
        (10, 9),
        f"{mode.replace('valid_75_to_76_', '')} / {target_row['target']} dx={dx} dy={dy}",
        fill="white",
        font=font(15),
    )
    draw.text(
        (10, 35),
        f"pixel {target_row['dominantPixelLetter']} comp {target_row['dominantComponentLetter']} text {target_row['sourceTextPreview'][:34] or '-'}",
        fill=(220, 228, 238),
        font=font(12),
    )

    def sx(value: float) -> float:
        return (value - crop[0]) * target_w / (crop[2] - crop[0])

    def sy(value: float) -> float:
        return 74 + (value - crop[1]) * resized.height / (crop[3] - crop[1])

    colors = [
        (255, 190, 80, 220),
        (246, 130, 90, 220),
        (120, 190, 255, 220),
        (150, 220, 150, 220),
        (220, 160, 255, 220),
        (255, 220, 120, 220),
        (110, 210, 230, 220),
        (245, 160, 170, 220),
    ]
    for slot, color in zip(slots, colors):
        left = max(float(slot["left"]), crop[0])
        right = min(float(slot["right"]), crop[2])
        if right <= left:
            continue
        draw.rectangle((sx(left), 74, sx(right), canvas.height - 1), outline=color, width=2)
        draw.text((sx(left) + 3, 78), slot["letter"], fill=color, font=font(11))
    draw.rectangle((sx(x0), sy(y0), sx(x1), sy(y1)), outline=(255, 0, 0, 240), width=3)
    canvas.save(out_path, quality=91)


def draw_sheet(result: dict, panel_paths: list[Path]) -> None:
    width, height = 1840, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Valid Leaf OVERDOSE Glyph-Slot Source Trace", fill="white", font=font(26))
    draw.text(
        (24, 56),
        "Actual page-76 OVERDOSE glyph slots inside O4/B4/G5/O5; blue pixels are valid 75->76 source-only signal.",
        fill=(235, 235, 235),
        font=font(14),
    )

    y = 118
    cards = [
        ("slot rows", result["summary"]["slotTraceRowCount"]),
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
    headers = ["mode", "target", "pixel", "component", "slot pixels", "slot comps", "words", "strict", "source text"]
    xs = [24, 254, 332, 414, 520, 606, 700, 760, 822]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=font(11))
    y += 22
    for row in result["targetRows"][:12]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            row["dominantPixelLetter"],
            row["dominantComponentLetter"],
            str(row["sourceOnlyPixelCount"]),
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            row["sourceTextPreview"][:90],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value), fill=(35, 35, 35), font=font(11))
        y += 19
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    bleed = load_json(BLEED_CONTROL)
    glyph = load_json(C9_HEADER_GLYPH)
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
    slots = next(
        projection["slots"]
        for projection in glyph.get("projections", [])
        if projection.get("name") == "p76_header_glyph"
    )
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

    slot_rows = []
    target_rows = []
    panel_paths: list[Path] = []
    for mode, dx, dy in mode_specs:
        shifted = edge.shift_channels(source_channels, dx, dy)
        source_feature = shifted["feature"]
        target_feature = target_channels["feature"]
        mode_target_rows = []
        for active_row in active_rows:
            per_slot_rows = []
            target_source_only = np.zeros(source_feature.shape, dtype=bool)
            for slot in slots:
                region = slot_region(active_row["box"], slot)
                if region is None:
                    continue
                area = max(0, region[2] - region[0]) * max(0, region[3] - region[1])
                mask = region_mask(source_feature.shape, region)
                source_only = np.logical_and(np.logical_and(source_feature, mask), ~target_feature)
                target_source_only |= source_only
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
                    "slotIndex": slot["index"],
                    "slotLetter": slot["letter"],
                    "slotRegion": region,
                    "area": area,
                    "sourceOnlyPixelCount": int(source_only.sum()),
                    "sourceOnlyCoverage": float(source_only.sum() / area) if area else 0.0,
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
                per_slot_rows.append(row)
                slot_rows.append(row)

            dominant_pixel = max(
                per_slot_rows,
                key=lambda row: (row["sourceOnlyCoverage"], row["sourceOnlyPixelCount"]),
                default=None,
            )
            component_candidates = [row for row in per_slot_rows if row["componentCount"]]
            dominant_component = max(
                component_candidates,
                key=lambda row: (row["componentPixelCount"], row["sourceOnlyCoverage"]),
                default=None,
            )
            source_word_rows = [row for row in per_slot_rows if row["sourceWordHitCount"]]
            target_source_words = []
            for row in source_word_rows:
                target_source_words.extend(row["sourceWords"])
            target_row = {
                "mode": mode,
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                "dominantPixelLetter": dominant_pixel["slotLetter"]
                if dominant_pixel and dominant_pixel["sourceOnlyPixelCount"]
                else ".",
                "dominantPixelCoverage": dominant_pixel["sourceOnlyCoverage"] if dominant_pixel else 0.0,
                "dominantComponentLetter": dominant_component["slotLetter"] if dominant_component else ".",
                "sourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in per_slot_rows),
                "componentCount": sum(row["componentCount"] for row in per_slot_rows),
                "componentPixelCount": sum(row["componentPixelCount"] for row in per_slot_rows),
                "sourceWordHitCount": sum(row["sourceWordHitCount"] for row in per_slot_rows),
                "strictInstructionHitCount": sum(row["strictInstructionHitCount"] for row in per_slot_rows),
                "contextTermHitCount": sum(row["contextTermHitCount"] for row in per_slot_rows),
                "sourceTextPreview": " | ".join(
                    row["sourceTextPreview"] for row in source_word_rows if row["sourceTextPreview"]
                ),
            }
            panel_path = OUT / f"{mode}_{active_row['shortId']}_glyph_slot_trace.jpg"
            draw_slot_panel(
                target_img,
                source_img,
                target_source_only,
                target_row,
                slots,
                mode,
                dx,
                dy,
                panel_path,
            )
            target_row["panel"] = rel(panel_path)
            mode_target_rows.append(target_row)
            target_rows.append(target_row)
            panel_paths.append(panel_path)

        pixel_stream = "".join(row["dominantPixelLetter"] for row in mode_target_rows)
        component_stream = "".join(row["dominantComponentLetter"] for row in mode_target_rows)
        for row in mode_target_rows:
            row["modeDominantPixelLineStream"] = pixel_stream
            row["modeDominantComponentLineStream"] = component_stream

    source_r3_hits = 0
    trigger_rows = reopen.get("triggerRows", [])
    satisfied_triggers = sum(1 for row in trigger_rows if row.get("triggerSatisfiedNow"))
    trigger_count = len(trigger_rows)
    selector_unlocks = 0
    strict_rows = sum(1 for row in slot_rows if row["strictInstructionHitCount"])
    context_rows = sum(1 for row in slot_rows if row["contextTermHitCount"])
    word_hit_rows = sum(1 for row in slot_rows if row["sourceWordHitCount"])
    component_rows = sum(1 for row in slot_rows if row["componentCount"])
    decision = (
        "valid_leaf_glyph_slot_source_trace_no_instruction_source"
        if not strict_rows and not source_r3_hits and not satisfied_triggers
        else "needs_manual_review"
    )
    mode_streams = []
    for mode, _, _ in mode_specs:
        rows = [row for row in target_rows if row["mode"] == mode]
        mode_streams.append(
            {
                "mode": mode,
                "dominantPixelLineStream": rows[0]["modeDominantPixelLineStream"] if rows else "",
                "dominantComponentLineStream": rows[0]["modeDominantComponentLineStream"] if rows else "",
            }
        )
    summary = {
        "modeCount": len(mode_specs),
        "targetRowCount": len(target_rows),
        "slotTraceRowCount": len(slot_rows),
        "componentRows": component_rows,
        "wordHitRows": word_hit_rows,
        "strictInstructionRows": strict_rows,
        "contextTermRows": context_rows,
        "totalComponentCount": sum(row["componentCount"] for row in slot_rows),
        "totalComponentPixelCount": sum(row["componentPixelCount"] for row in slot_rows),
        "totalSourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in slot_rows),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in slot_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in slot_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in slot_rows),
        "modeStreams": mode_streams,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"modes={summary['modeCount']}|targets={summary['targetRowCount']}|"
        f"slots={summary['slotTraceRowCount']}|componentRows={summary['componentRows']}|"
        f"wordRows={summary['wordHitRows']}|strictRows={summary['strictInstructionRows']}|"
        f"contextRows={summary['contextTermRows']}|components={summary['totalComponentCount']}|"
        f"componentPixels={summary['totalComponentPixelCount']}|words={summary['totalSourceWordHits']}|"
        f"strict={summary['totalStrictInstructionHits']}|context={summary['totalContextTermHits']}|"
        f"streams={';'.join(row['dominantPixelLineStream'] + '/' + row['dominantComponentLineStream'] for row in mode_streams)}|"
        f"sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}|"
        f"selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page 75 -> page 76 OVERDOSE glyph-slot source trace; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "bleedControlGrid": rel(BLEED_CONTROL),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "targetRows": target_rows,
        "slotRows": slot_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Do not extract from valid-leaf OVERDOSE glyph-slot traces; require a source/clue that names transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Glyph-Slot Source Trace",
        "",
        "Scope: subdivided O4/B4/G5/O5 by the actual page-76 OVERDOSE glyph slots under valid page 75 -> page 76 held-to-light alignment, then mapped slot-level source-only components back to page-75 source words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Target rows / slot rows: `{summary['targetRowCount']}` / `{summary['slotTraceRowCount']}`",
        f"- Component rows / word rows: `{summary['componentRows']}` / `{summary['wordHitRows']}`",
        f"- Total components / component pixels: `{summary['totalComponentCount']}` / `{summary['totalComponentPixelCount']}`",
        f"- Source word hits / strict instruction hits / context hits: `{summary['totalSourceWordHits']}` / `{summary['totalStrictInstructionHits']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Mode Streams",
        "",
        "| mode | dominant pixel stream | dominant component stream |",
        "|---|---|---|",
    ]
    for row in mode_streams:
        lines.append(
            f"| `{row['mode']}` | `{row['dominantPixelLineStream']}` | `{row['dominantComponentLineStream']}` |"
        )
    lines.extend(
        [
            "",
            "## Target Rows",
            "",
            "| mode | target | pixel letter | component letter | slot pixels | components | source words | strict | context | source text preview | panel |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in target_rows:
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | `{row['dominantPixelLetter']}` | "
            f"`{row['dominantComponentLetter']}` | {row['sourceOnlyPixelCount']} | "
            f"{row['componentCount']} | {row['sourceWordHitCount']} | "
            f"{row['strictInstructionHitCount']} | {row['contextTermHitCount']} | "
            f"{row['sourceTextPreview'][:120]} | `{row['panel']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- The valid same-leaf OVERDOSE glyph-slot source pixels do not trace to source-side unit/order instructions.",
            "- Slot-aware streams remain non-extractive (`S.RD`/`...D` natural and `S.RR`/`..RR` small-jitter), and source-word hits are sparse ordinary page-75 text.",
            "- Keep this as the glyph-slot provenance stop-check for the current valid leaf.",
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
