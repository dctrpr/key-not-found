#!/usr/bin/env python3
"""Check whether valid-leaf held-to-light residue is visually readable.

This bounded pass reuses the current scan/PDF page images and the established
75 -> 76 same-leaf mirror model. It asks whether source-only residue inside the
locked O4/B4/G5/O5 active boxes forms substantial letter-like components, or
whether the residue remains fragmentary/target-overlap noise.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_scan_valid_leaf_edge_source_trace as edge  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_held_to_light_component_readability_gate.json"
OUT_MD = OUT / "current_scan_held_to_light_component_readability_gate.md"
OUT_SHEET = OUT / "current_scan_held_to_light_component_readability_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BLEED_CONTROL = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/"
    "current_scan_valid_leaf_bleedthrough_control_grid.json"
)
CROP_LIGHT_TABLE = ROOT / (
    "analysis_outputs/source_audit/current_scan_crop_light_table_targets/"
    "current_scan_crop_light_table_targets.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGETS = ["O4", "B4", "G5", "O5"]
MIN_LETTERLIKE_COMPONENTS_FOR_ROW = 2
MIN_COMPONENT_AREA = 18
STRICT_TERMS = edge.STRICT_TERMS
CONTEXT_TERMS = edge.CONTEXT_TERMS


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


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


def norm_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def page_words(article_map: dict[str, Any], page: int) -> list[dict[str, Any]]:
    for page_row in article_map.get("pages", []):
        if int(page_row.get("page", -1)) == page:
            return page_row.get("words", [])
    return []


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in active_index.get("activeRows", []) if row.get("shortId") in TARGETS]
    return sorted(rows, key=lambda row: TARGETS.index(row["shortId"]))


def box_mask(shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = shape
    x0, y0, x1, y1 = [round(value) for value in box]
    mask = np.zeros((h, w), dtype=bool)
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = True
    return mask


def boxes_intersect(left: list[float], right: list[float]) -> bool:
    return max(left[0], right[0]) < min(left[2], right[2]) and max(left[1], right[1]) < min(
        left[3], right[3]
    )


def source_words_for_box(words: list[dict[str, Any]], box: list[int] | None) -> list[dict[str, Any]]:
    if not box:
        return []
    hits = []
    for word in words:
        word_box = word.get("box", [0, 0, 0, 0])
        if not boxes_intersect(word_box, box):
            continue
        token = norm_token(str(word.get("text", "")))
        if not token:
            continue
        hits.append(
            {
                "text": word.get("text", ""),
                "token": token,
                "box": word_box,
                "index": word.get("index"),
                "strictInstruction": token in STRICT_TERMS,
                "contextTerm": token in CONTEXT_TERMS,
            }
        )
    return hits


def union_box(boxes: list[list[int]]) -> list[int] | None:
    if not boxes:
        return None
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def component_shape(component: dict[str, Any]) -> dict[str, Any]:
    x0, y0, x1, y1 = component["targetBox"]
    width = x1 - x0
    height = y1 - y0
    area = int(component["pixelCount"])
    bbox_area = max(1, width * height)
    fill_ratio = area / bbox_area
    aspect = width / max(1, height)
    letterlike = (
        area >= MIN_COMPONENT_AREA
        and 3 <= width <= 120
        and 8 <= height <= 90
        and 0.08 <= aspect <= 8.0
        and 0.04 <= fill_ratio <= 0.88
    )
    return {
        "pixelCount": area,
        "widthPx": width,
        "heightPx": height,
        "fillRatio": round(fill_ratio, 6),
        "aspectRatio": round(aspect, 6),
        "letterlike": letterlike,
    }


def component_rows(local_mask: np.ndarray, offset_x: int, offset_y: int) -> list[dict[str, Any]]:
    components = edge.connected_components(local_mask, limit=10)
    rows = []
    for component in components:
        local_box = component["targetBox"]
        target_box = [
            local_box[0] + offset_x,
            local_box[1] + offset_y,
            local_box[2] + offset_x,
            local_box[3] + offset_y,
        ]
        shaped = {"targetBox": target_box, **component_shape({**component, "targetBox": target_box})}
        rows.append(shaped)
    return rows


def mode_definitions(bleed_control: dict[str, Any], crop_light_table: dict[str, Any]) -> list[dict[str, Any]]:
    jitter = bleed_control.get("summary", {}).get("jitterBestShift") or [-80, -20]
    forced = next(
        (
            row
            for row in crop_light_table.get("scenarios", [])
            if row.get("scenarioId") == "valid_75_to_76_forced_best"
        ),
        {},
    )
    return [
        {
            "mode": "valid_75_to_76_natural",
            "sourcePage": 75,
            "targetPage": 76,
            "dx": 0,
            "dy": 0,
            "physicalClass": "valid same leaf natural",
        },
        {
            "mode": "valid_75_to_76_small_jitter_best",
            "sourcePage": 75,
            "targetPage": 76,
            "dx": int(jitter[0]),
            "dy": int(jitter[1]),
            "physicalClass": "valid same leaf small-jitter control",
        },
        {
            "mode": "valid_75_to_76_forced_best",
            "sourcePage": 75,
            "targetPage": 76,
            "dx": int(forced.get("dx", -220)),
            "dy": int(forced.get("dy", 200)),
            "physicalClass": "valid same leaf forced-boundary guardrail",
        },
    ]


def inspect_mode(
    mode: dict[str, Any],
    target_img: Image.Image,
    source_img: Image.Image,
    target_channels: dict[str, np.ndarray],
    source_words: list[dict[str, Any]],
    active: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_channels = edge.shift_channels(edge.feature_channels(source_img), mode["dx"], mode["dy"])
    source_feature = source_channels["feature"]
    target_feature = target_channels["feature"]
    source_only = source_feature & ~target_feature
    rows = []
    for target in active:
        box = [float(value) for value in target["box"]]
        x0, y0, x1, y1 = [round(value) for value in box]
        box_area = max(1, (x1 - x0) * (y1 - y0))
        local_source = source_feature[y0:y1, x0:x1]
        local_target = target_feature[y0:y1, x0:x1]
        local_source_only = source_only[y0:y1, x0:x1]
        components = component_rows(local_source_only, x0, y0)
        letterlike_components = [row for row in components if row["letterlike"]]
        component_source_boxes = [
            edge.transform_target_box_to_source(component["targetBox"], target_img.width, mode["dx"], mode["dy"])
            for component in letterlike_components
        ]
        source_trace_box = union_box(component_source_boxes)
        source_words = source_words_for_box(source_words, source_trace_box)
        source_text = " ".join(word["text"] for word in source_words[:12])
        row = {
            "mode": mode["mode"],
            "physicalClass": mode["physicalClass"],
            "sourcePage": mode["sourcePage"],
            "targetPage": mode["targetPage"],
            "dx": mode["dx"],
            "dy": mode["dy"],
            "target": target["shortId"],
            "phrase": target["phrase"],
            "visualState": target.get("visualState"),
            "color": target.get("color"),
            "box": box,
            "sourceCoverage": round(float(local_source.mean()) if local_source.size else 0.0, 9),
            "targetCoverage": round(float(local_target.mean()) if local_target.size else 0.0, 9),
            "sourceOnlyCoverage": round(float(local_source_only.mean()) if local_source_only.size else 0.0, 9),
            "sourceOnlyPixelCount": int(local_source_only.sum()),
            "componentCount": len(components),
            "letterlikeComponentCount": len(letterlike_components),
            "largestComponentPixelCount": max([row["pixelCount"] for row in components] or [0]),
            "largestLetterlikePixelCount": max([row["pixelCount"] for row in letterlike_components] or [0]),
            "componentPixelCount": int(sum(row["pixelCount"] for row in components)),
            "letterlikePixelCount": int(sum(row["pixelCount"] for row in letterlike_components)),
            "letterlikeShareOfBox": round(
                sum(row["pixelCount"] for row in letterlike_components) / box_area, 9
            ),
            "components": components,
            "letterlikeComponents": letterlike_components,
            "componentSourceBoxes": component_source_boxes,
            "sourceTraceBox": source_trace_box,
            "sourceWordHitCount": len(source_words),
            "strictInstructionHitCount": sum(1 for word in source_words if word["strictInstruction"]),
            "contextTermHitCount": sum(1 for word in source_words if word["contextTerm"]),
            "strictInstructionTerms": sorted(
                {word["token"] for word in source_words if word["strictInstruction"]}
            ),
            "contextTerms": sorted({word["token"] for word in source_words if word["contextTerm"]}),
            "sourceTextPreview": source_text,
            "sourceWords": source_words,
            "readableComponentCandidate": len(letterlike_components)
            >= MIN_LETTERLIKE_COMPONENTS_FOR_ROW,
        }
        rows.append(row)
    return rows


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
    px, py = paste_xy
    x0, y0, x1, y1 = rect
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


def padded_box(box: list[int] | list[float], size: tuple[int, int], pad_x: int = 120, pad_y: int = 86) -> list[int]:
    w, h = size
    x0, y0, x1, y1 = [round(value) for value in box]
    return [max(0, x0 - pad_x), max(0, y0 - pad_y), min(w, x1 + pad_x), min(h, y1 + pad_y)]


def fit_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    resized = img.resize((target_w, max(1, round(target_w * img.height / img.width))))
    if resized.height > target_h:
        resized = resized.resize((max(1, round(resized.width * target_h / resized.height)), target_h))
    return resized


def render_panel(
    target_img: Image.Image,
    source_img: Image.Image,
    row: dict[str, Any],
    out_path: Path,
) -> None:
    panel_w = 360
    panel_h = 250
    top_h = 62
    canvas = Image.new("RGB", (panel_w * 3, panel_h + top_h + 22), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    title_font = safe_font(15)
    small_font = safe_font(12)

    draw.rectangle((0, 0, canvas.width, 38), fill=(25, 31, 42, 235))
    draw.text(
        (10, 10),
        f"{row['mode']} {row['target']} components={row['letterlikeComponentCount']} strict={row['strictInstructionHitCount']}",
        fill="white",
        font=title_font,
    )
    target_box = [round(value) for value in row["box"]]
    target_crop_box = padded_box(target_box, target_img.size)
    transformed_source = edge.shifted_mirror_image(source_img, row["dx"], row["dy"])
    source_trace_box = row.get("sourceTraceBox")
    source_crop_box = (
        edge.padded_box(source_trace_box, source_img.size, 90) if source_trace_box else None
    )

    target_crop = target_img.crop(tuple(target_crop_box))
    source_crop = transformed_source.crop(tuple(target_crop_box))
    blend = Image.blend(target_crop, source_crop, 0.42)
    overlay = blend.convert("RGBA")
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    for component in row["letterlikeComponents"]:
        draw_scaled_rect(
            overlay_draw,
            component["targetBox"],
            target_crop_box,
            (0, 0),
            overlay.size,
            (0, 116, 255, 220),
            2,
        )
    blend = overlay.convert("RGB")
    if source_crop_box:
        source_panel = source_img.crop(tuple(source_crop_box))
    else:
        source_panel = Image.new("RGB", (panel_w, panel_h), "white")
        ImageDraw.Draw(source_panel).text((24, 104), "no mapped component", fill=(80, 80, 80), font=small_font)

    panels = [
        (target_crop, "page 76 target", target_crop_box),
        (blend, "source residue overlay", target_crop_box),
        (source_panel, "mapped page 75 source", source_crop_box),
    ]
    for idx, (img, label, crop_box) in enumerate(panels):
        resized = fit_crop(img, panel_w, panel_h)
        px = idx * panel_w
        py = top_h
        canvas.paste(resized, (px, py))
        draw.text((px + 8, 44), label, fill=(35, 38, 45), font=small_font)
        if crop_box:
            if idx in {0, 1}:
                draw_scaled_rect(draw, target_box, crop_box, (px, py), resized.size, (255, 0, 0, 230), 2)
                for component in row["letterlikeComponents"]:
                    draw_scaled_rect(
                        draw,
                        component["targetBox"],
                        crop_box,
                        (px, py),
                        resized.size,
                        (0, 116, 255, 230),
                        2,
                    )
            else:
                if source_trace_box:
                    draw_scaled_rect(draw, source_trace_box, crop_box, (px, py), resized.size, (255, 0, 0, 230), 2)
                for source_box in row["componentSourceBoxes"]:
                    draw_scaled_rect(draw, source_box, crop_box, (px, py), resized.size, (255, 140, 0, 210), 2)
                for word in row["sourceWords"][:12]:
                    color = (255, 0, 0, 235) if word["strictInstruction"] else (0, 120, 255, 170)
                    draw_scaled_rect(draw, word["box"], crop_box, (px, py), resized.size, color, 2)
    canvas.save(out_path, quality=91)


def draw_sheet(result: dict[str, Any], panel_paths: list[Path]) -> None:
    width, height = 1840, 1320
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = safe_font(25)
    small_font = safe_font(15)
    tiny_font = safe_font(12)

    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Held-To-Light Component Readability Gate", fill="white", font=title_font)
    draw.text(
        (24, 56),
        (
            f"modes {result['summary']['modeCount']} | rows {result['summary']['targetRowCount']} | "
            f"natural readable rows {result['summary']['naturalReadableRowCount']} | "
            f"all-four readable modes {result['summary']['allFourReadableModeCount']} | "
            f"strict rows {result['summary']['strictInstructionRowCount']} | selectors 0"
        ),
        fill=(235, 235, 235),
        font=small_font,
    )

    x, y = 24, 120
    for path in panel_paths[:6]:
        panel = Image.open(path).convert("RGB").resize((560, 174))
        img.paste(panel, (x, y))
        x += 592
        if x + 560 > width:
            x = 24
            y += 222

    y = 600
    headers = [
        "mode",
        "target",
        "src-only",
        "components",
        "letterlike",
        "largest",
        "source words",
        "strict",
        "preview",
    ]
    xs = [24, 300, 382, 470, 570, 670, 755, 860, 930]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny_font)
    y += 22
    for idx, row in enumerate(result["targetRows"]):
        fill = (248, 249, 252) if idx % 2 == 0 else (238, 242, 247)
        if row["readableComponentCandidate"]:
            fill = (255, 246, 225)
        if row["strictInstructionHitCount"]:
            fill = (255, 230, 230)
        draw.rectangle((18, y - 4, width - 18, y + 36), fill=fill)
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            str(row["componentCount"]),
            str(row["letterlikeComponentCount"]),
            str(row["largestLetterlikePixelCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            row["sourceTextPreview"][:92],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(30, 30, 30), font=tiny_font)
        y += 40
    img.save(OUT_SHEET, quality=92)


def summarize_mode(rows: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    mode_rows = [row for row in rows if row["mode"] == mode]
    readable_rows = [
        row for row in mode_rows if row["letterlikeComponentCount"] >= MIN_LETTERLIKE_COMPONENTS_FOR_ROW
    ]
    return {
        "mode": mode,
        "rowCount": len(mode_rows),
        "sourceOnlyPixelCount": int(sum(row["sourceOnlyPixelCount"] for row in mode_rows)),
        "componentRows": sum(1 for row in mode_rows if row["componentCount"]),
        "letterlikeRows": sum(1 for row in mode_rows if row["letterlikeComponentCount"]),
        "readableRowCount": len(readable_rows),
        "minLetterlikeComponentCount": min([row["letterlikeComponentCount"] for row in mode_rows] or [0]),
        "maxLetterlikeComponentCount": max([row["letterlikeComponentCount"] for row in mode_rows] or [0]),
        "allFourReadable": len(readable_rows) == len(TARGETS),
        "strictInstructionRows": sum(1 for row in mode_rows if row["strictInstructionHitCount"]),
        "contextTermRows": sum(1 for row in mode_rows if row["contextTermHitCount"]),
        "sourceWordRows": sum(1 for row in mode_rows if row["sourceWordHitCount"]),
    }


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Held-To-Light Component Readability Gate",
        "",
        "Scope: bounded current-scan/PDF held-to-light component-readability inspection. No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Modes checked: `{summary['modeCount']}`",
        f"- Target rows checked: `{summary['targetRowCount']}`",
        f"- Natural valid-leaf readable rows: `{summary['naturalReadableRowCount']}`",
        f"- All-four readable modes: `{summary['allFourReadableModeCount']}`",
        f"- Strict instruction rows: `{summary['strictInstructionRowCount']}`",
        f"- Hidden readability candidates: `{summary['hiddenReadabilityCandidateCount']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['componentReadabilityFingerprint']}`",
        "",
        "## Mode Summary",
        "",
        "| mode | source-only pixels | component rows | letterlike rows | readable rows | all-four readable | strict rows | source-word rows |",
        "|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for row in result["modeRows"]:
        lines.append(
            f"| `{row['mode']}` | `{row['sourceOnlyPixelCount']}` | `{row['componentRows']}` | "
            f"`{row['letterlikeRows']}` | `{row['readableRowCount']}` | `{row['allFourReadable']}` | "
            f"`{row['strictInstructionRows']}` | `{row['sourceWordRows']}` |"
        )
    lines.extend(
        [
            "",
            "## Target Rows",
            "",
            "| mode | target | source-only coverage | components | letterlike | largest letterlike | source words | strict | preview |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in result["targetRows"]:
        preview = row["sourceTextPreview"].replace("|", "/")
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | `{row['sourceOnlyCoverage']}` | "
            f"`{row['componentCount']}` | `{row['letterlikeComponentCount']}` | "
            f"`{row['largestLetterlikePixelCount']}` | `{row['sourceWordHitCount']}` | "
            f"`{row['strictInstructionHitCount']}` | {preview} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['currentScanHeldToLightComponentReadabilityGate']}.",
            f"- Reason: {result['decision']['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    bleed_control = load_json(BLEED_CONTROL)
    crop_light_table = load_json(CROP_LIGHT_TABLE)
    article_map = load_json(ARTICLE_MAP)
    reopen_trigger = load_json(REOPEN_TRIGGER_MATRIX)

    target_img = edge.normalize_page(76)
    source_img = edge.normalize_page(75)
    target_channels = edge.feature_channels(target_img)
    source_words = page_words(article_map, 75)
    active = active_rows(active_index)
    modes = mode_definitions(bleed_control, crop_light_table)

    target_rows: list[dict[str, Any]] = []
    for mode in modes:
        target_rows.extend(
            inspect_mode(mode, target_img, source_img, target_channels, source_words, active)
        )

    panel_paths = []
    for row in target_rows:
        out_path = OUT / f"{row['mode']}_{row['target']}_component_readability.jpg"
        render_panel(target_img, source_img, row, out_path)
        row["panel"] = rel(out_path)
        panel_paths.append(out_path)

    mode_rows = [summarize_mode(target_rows, mode["mode"]) for mode in modes]
    readable_modes = [row for row in mode_rows if row["allFourReadable"]]

    reopen_summary = reopen_trigger.get("summary", {})
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(reopen_summary.get("triggerCount", 0) or 0)
    strict_instruction_rows = sum(1 for row in target_rows if row["strictInstructionHitCount"])
    hidden_candidates = [
        row
        for row in mode_rows
        if row["allFourReadable"] and row["strictInstructionRows"] > 0 and source_r3 > 0
    ]
    natural = next(row for row in mode_rows if row["mode"] == "valid_75_to_76_natural")
    forced = next(row for row in mode_rows if row["mode"] == "valid_75_to_76_forced_best")
    fingerprint = (
        f"modes={len(modes)}|rows={len(target_rows)}|"
        f"naturalReadable={natural['readableRowCount']}|"
        f"forcedReadable={forced['readableRowCount']}|"
        f"allFourReadable={len(readable_modes)}|strictRows={strict_instruction_rows}|"
        f"hiddenCandidate={len(hidden_candidates)}|sourceR3={source_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "modeCount": len(modes),
        "targetRowCount": len(target_rows),
        "naturalReadableRowCount": natural["readableRowCount"],
        "forcedReadableRowCount": forced["readableRowCount"],
        "allFourReadableModeCount": len(readable_modes),
        "strictInstructionRowCount": strict_instruction_rows,
        "sourceWordRowCount": sum(1 for row in target_rows if row["sourceWordHitCount"]),
        "contextTermRowCount": sum(1 for row in target_rows if row["contextTermHitCount"]),
        "hiddenReadabilityCandidateCount": len(hidden_candidates),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "componentReadabilityFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current scan held-to-light component-readability gate; no key derivation, "
            "hashing, WIF, seed, address, BIP39, or broad brute force"
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "bleedthroughControlGrid": rel(BLEED_CONTROL),
            "cropLightTableTargets": rel(CROP_LIGHT_TABLE),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "modes": modes,
            "componentMinimumPixelArea": MIN_COMPONENT_AREA,
            "readableRowThreshold": f">={MIN_LETTERLIKE_COMPONENTS_FOR_ROW} letterlike components",
            "candidateRequirement": "all four active boxes readable plus strict/source-backed R3 instruction",
        },
        "modeRows": mode_rows,
        "targetRows": target_rows,
        "summary": summary,
        "decision": {
            "currentScanHeldToLightComponentReadabilityGate": (
                "current_scan_held_to_light_components_not_readable_selector"
            ),
            "selectorUnlocked": False,
            "reason": (
                "The physically valid natural 75->76 view has no readable active quartet, "
                "and even the forced same-leaf guardrail does not make all four active boxes "
                "readable or produce strict instruction text. Any mapped words remain ordinary "
                "page-75 prose/context without source-backed R3 permission."
            ),
        },
        "nextMove": (
            "Do not treat held-to-light residue as readable source text under the current scan. "
            "Further local work should inspect a different source/provenance surface, or wait for "
            "a true physical/original-layout source or raw clue that names the unit/order/transform."
        ),
        "sheet": rel(OUT_SHEET),
        "panels": [rel(path) for path in panel_paths],
    }
    draw_sheet(result, panel_paths)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint {fingerprint}")


if __name__ == "__main__":
    main()
