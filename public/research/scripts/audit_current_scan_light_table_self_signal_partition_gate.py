#!/usr/bin/env python3
"""Partition valid held-to-light signal into source-supported vs target-only.

The current scan's valid 75->76 average blend can make all four page-76 active
boxes visually pop, but prior gates showed the same view lacks all-four source
ink. This bounded pass measures whether that visual pop is actually carried by
the mirrored back page, or mostly by page-76 self-signal against a light source.
It also measures projected OVERDOSE slots as geometry controls.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_light_table_self_signal_partition_gate.json"
OUT_MD = OUT / "current_scan_light_table_self_signal_partition_gate.md"
OUT_SHEET = OUT / "current_scan_light_table_self_signal_partition_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
B4_SELF_SIGNAL = ROOT / (
    "analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/"
    "current_scan_b4_self_signal_guardrail.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]
SOURCE_INK_LUMA_THRESHOLD = 238.0
TARGET_INK_LUMA_THRESHOLD = 238.0
AVERAGE_ALPHA = 0.70
TARGET_ONLY_DOMINANCE = 0.75
SOURCE_SUPPORTED_DOMINANCE = 0.50


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def normalize_page(page: int) -> Image.Image:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    if source_path.exists():
        source = Image.open(source_path).convert("RGB")
        upright = Image.open(upright_path).convert("RGB")
        sample_size = (318, 408)
        source_sample = source.resize(sample_size)
        upright_sample = upright.resize(sample_size)
        same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
        rot_diff = sum(
            ImageStat.Stat(
                ImageChops.difference(source_sample.rotate(180), upright_sample)
            ).mean
        )
        return source.rotate(180) if rot_diff < same_diff else source
    return Image.open(upright_path).convert("RGB")


def shifted_mirrored_source(page: Image.Image, dx: int = 0, dy: int = 0) -> Image.Image:
    mirrored = ImageOps.mirror(page)
    canvas = Image.new("RGB", page.size, "white")
    canvas.paste(mirrored, (dx, dy))
    return canvas


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def crop_arr(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return arr[y0:y1, x0:x1, :]


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def box_area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def iou(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    inter = box_area([x0, y0, x1, y1])
    union = box_area(a) + box_area(b) - inter
    return inter / union if union else 0.0


def shifted_box(box: list[float], dy: float, page_size: tuple[int, int]) -> list[float] | None:
    w, h = page_size
    shifted = [box[0], box[1] + dy, box[2], box[3] + dy]
    if shifted[0] < 0 or shifted[1] < 0 or shifted[2] > w or shifted[3] > h:
        return None
    return shifted


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") in TARGET_ORDER:
            rows.append(
                {
                    "id": row["id"],
                    "shortId": row["shortId"],
                    "phrase": row["phrase"],
                    "kind": "active",
                    "visualState": row["visualState"],
                    "pageLine": int(row["pageLine"]),
                    "box": [float(v) for v in row["box"]],
                }
            )
    rows.sort(key=lambda row: TARGET_ORDER.index(row["shortId"]))
    return rows


def estimated_line_pitch(rows: list[dict[str, Any]]) -> float:
    pitches: list[float] = []
    for i, left in enumerate(rows):
        for right in rows[i + 1 :]:
            line_gap = right["pageLine"] - left["pageLine"]
            if line_gap:
                cy_left = (left["box"][1] + left["box"][3]) / 2
                cy_right = (right["box"][1] + right["box"][3]) / 2
                pitches.append((cy_right - cy_left) / line_gap)
    return float(median(pitches)) if pitches else 73.5


def line_shift_controls(active: list[dict[str, Any]], page_size: tuple[int, int], pitch: float) -> list[dict[str, Any]]:
    active_boxes_only = [row["box"] for row in active]
    rows: list[dict[str, Any]] = []
    for row in active:
        for offset in CONTROL_LINE_OFFSETS:
            box = shifted_box(row["box"], offset * pitch, page_size)
            if box is None or any(iou(box, active_box) > 0.08 for active_box in active_boxes_only):
                continue
            rows.append(
                {
                    "id": f"{row['shortId']}_line_{offset:+d}",
                    "shortId": f"{row['shortId']}{offset:+d}",
                    "sourceTarget": row["shortId"],
                    "phrase": f"{row['shortId']} shifted {offset:+d} lines",
                    "kind": "line_shift_control",
                    "visualState": "control",
                    "pageLine": row["pageLine"] + offset,
                    "box": box,
                }
            )
    return rows


def overdose_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])]
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "id": f"overdose_slot_{slot['index']}_{slot['letter']}",
                "shortId": f"slot_{slot['letter']}{slot['index']}",
                "phrase": f"OVERDOSE slot {slot['letter']}",
                "kind": "overdose_slot",
                "visualState": "slot",
                "slotIndex": int(slot["index"]),
                "slotLetter": str(slot["letter"]),
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return rows


def average_blend(target_arr: np.ndarray, source_arr: np.ndarray) -> np.ndarray:
    return np.clip(
        (1.0 - AVERAGE_ALPHA) * target_arr.astype(np.float32)
        + AVERAGE_ALPHA * source_arr.astype(np.float32),
        0,
        255,
    ).astype(np.uint8)


def measure_region(
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    blend_arr: np.ndarray,
    source_ink_mask: np.ndarray,
    target_ink_mask: np.ndarray,
    row: dict[str, Any],
) -> dict[str, Any]:
    box = row["box"]
    target_crop = crop_arr(target_arr, box)
    source_crop = crop_arr(source_arr, box)
    blend_crop = crop_arr(blend_arr, box)
    source_ink = crop_bool(source_ink_mask, box)
    target_ink = crop_bool(target_ink_mask, box)
    if target_crop.size == 0:
        return {**row, "averageDelta": 0.0, "sourceInkRatio": 0.0}

    delta = np.abs(luma(target_crop) - luma(blend_crop))
    total_delta = float(delta.sum())
    source_supported = source_ink
    target_only = target_ink & ~source_ink
    white_source = ~source_ink
    source_supported_delta = float(delta[source_supported].sum()) if source_supported.any() else 0.0
    target_only_delta = float(delta[target_only].sum()) if target_only.any() else 0.0
    white_source_delta = float(delta[white_source].sum()) if white_source.any() else 0.0
    source_only_delta = float(delta[source_ink & ~target_ink].sum()) if (source_ink & ~target_ink).any() else 0.0
    overlap_delta = float(delta[source_ink & target_ink].sum()) if (source_ink & target_ink).any() else 0.0
    source_supported_delta_mean = float((delta * source_ink).mean())
    target_only_delta_mean = float((delta * target_only).mean())
    return {
        **row,
        "averageDelta": round(float(delta.mean()), 6),
        "sourceInkRatio": round(float(source_ink.mean()), 6),
        "targetInkRatio": round(float(target_ink.mean()), 6),
        "sourceSupportedDeltaMean": round(source_supported_delta_mean, 6),
        "targetOnlyDeltaMean": round(target_only_delta_mean, 6),
        "sourceSupportedDeltaShare": round(source_supported_delta / total_delta, 6) if total_delta else 0.0,
        "targetOnlyDeltaShare": round(target_only_delta / total_delta, 6) if total_delta else 0.0,
        "whiteSourceDeltaShare": round(white_source_delta / total_delta, 6) if total_delta else 0.0,
        "sourceOnlyDeltaShare": round(source_only_delta / total_delta, 6) if total_delta else 0.0,
        "sourceTargetOverlapDeltaShare": round(overlap_delta / total_delta, 6) if total_delta else 0.0,
        "targetOnlyDominant": bool(total_delta and target_only_delta / total_delta >= TARGET_ONLY_DOMINANCE),
        "sourceSupportedDominant": bool(total_delta and source_supported_delta / total_delta >= SOURCE_SUPPORTED_DOMINANCE),
    }


def percentile(values: list[float], pct: float) -> float:
    return float(np.percentile(values, pct)) if values else 0.0


def summarize(rows: list[dict[str, Any]], triggers: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    active = [row for row in rows if row["kind"] == "active"]
    controls = [row for row in rows if row["kind"] == "line_shift_control"]
    slots = [row for row in rows if row["kind"] == "overdose_slot"]
    control_source_mean_p95 = percentile([float(row["sourceSupportedDeltaMean"]) for row in controls], 95)
    control_source_share_p95 = percentile([float(row["sourceSupportedDeltaShare"]) for row in controls], 95)
    slot_source_mean_p95 = percentile([float(row["sourceSupportedDeltaMean"]) for row in slots], 95)
    active_above_control_mean = sum(
        1 for row in active if float(row["sourceSupportedDeltaMean"]) > control_source_mean_p95
    )
    active_above_control_share = sum(
        1 for row in active if float(row["sourceSupportedDeltaShare"]) > control_source_share_p95
    )
    source_r3 = int(triggers.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(triggers.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(triggers.get("summary", {}).get("triggerCount") or 0)
    all_active_target_only = all(row["targetOnlyDominant"] for row in active)
    all_active_source_supported = all(row["sourceSupportedDominant"] for row in active)
    selector = bool(
        source_r3 > 0
        and all_active_source_supported
        and active_above_control_mean == len(active)
        and not all_active_target_only
    )
    active_target_only_shares = [float(row["targetOnlyDeltaShare"]) for row in active]
    active_source_shares = [float(row["sourceSupportedDeltaShare"]) for row in active]
    fingerprint = (
        f"active={len(active)}|controls={len(controls)}|slots={len(slots)}|alpha={AVERAGE_ALPHA:.2f}|"
        f"activeTargetOnlyDominant={sum(1 for row in active if row['targetOnlyDominant'])}/{len(active)}|"
        f"activeSourceDominant={sum(1 for row in active if row['sourceSupportedDominant'])}/{len(active)}|"
        f"activeSrcMeanAboveCtlP95={active_above_control_mean}/{len(active)}|"
        f"activeSrcShareAboveCtlP95={active_above_control_share}/{len(active)}|"
        f"activeMinTargetOnly={min(active_target_only_shares):.4f}|"
        f"activeMaxSourceShare={max(active_source_shares):.4f}|"
        f"slotSrcMeanP95={slot_source_mean_p95:.4f}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={int(selector)}"
    )
    return {
        "scenarioId": "valid_75_to_76_natural_average",
        "sourcePage": 75,
        "targetPage": 76,
        "alpha": AVERAGE_ALPHA,
        "activeCount": len(active),
        "controlCount": len(controls),
        "overdoseSlotCount": len(slots),
        "activeTargetOnlyDominantCount": sum(1 for row in active if row["targetOnlyDominant"]),
        "activeSourceSupportedDominantCount": sum(1 for row in active if row["sourceSupportedDominant"]),
        "controlTargetOnlyDominantCount": sum(1 for row in controls if row["targetOnlyDominant"]),
        "overdoseSlotTargetOnlyDominantCount": sum(1 for row in slots if row["targetOnlyDominant"]),
        "activeSourceSupportedMeanAboveControlP95Count": active_above_control_mean,
        "activeSourceSupportedShareAboveControlP95Count": active_above_control_share,
        "activeMinTargetOnlyDeltaShare": round(min(active_target_only_shares), 6),
        "activeMaxSourceSupportedDeltaShare": round(max(active_source_shares), 6),
        "activeMeanTargetOnlyDeltaShare": round(float(np.mean(active_target_only_shares)), 6),
        "activeMeanSourceSupportedDeltaShare": round(float(np.mean(active_source_shares)), 6),
        "controlSourceSupportedDeltaMeanP95": round(control_source_mean_p95, 6),
        "controlSourceSupportedDeltaShareP95": round(control_source_share_p95, 6),
        "overdoseSlotSourceSupportedDeltaMeanP95": round(slot_source_mean_p95, 6),
        "selfSignalSelectorCandidate": selector,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "priorB4SelfSignalFingerprint": prior.get("summary", {}).get("b4SelfSignalFingerprint"),
        "lightTableSelfSignalPartitionFingerprint": fingerprint,
    }


def draw_sheet(
    target: Image.Image,
    source: Image.Image,
    blend: Image.Image,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    preview_w = 360
    preview_h = round(preview_w * target.height / target.width)
    sheet = Image.new("RGB", (1500, 1120), (248, 248, 244))
    draw = ImageDraw.Draw(sheet)
    title = font(24, True)
    small = font(13)
    tiny = font(11)
    draw.rectangle((0, 0, 1500, 92), fill=(28, 32, 39))
    draw.text((22, 16), "Light-Table Self-Signal Partition Gate", fill="white", font=title)
    draw.text(
        (22, 50),
        summary["lightTableSelfSignalPartitionFingerprint"],
        fill=(230, 230, 230),
        font=tiny,
    )

    panels = [("page 76 target", target), ("mirrored page 75 source", source), ("average blend", blend)]
    x = 22
    active = [row for row in rows if row["kind"] == "active"]
    slots = [row for row in rows if row["kind"] == "overdose_slot"]
    for label, image in panels:
        preview = image.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
        panel_draw = ImageDraw.Draw(preview, "RGBA")
        sx = preview_w / image.width
        sy = preview_h / image.height
        for slot in slots:
            x0, y0, x1, y1 = slot["box"]
            panel_draw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=(90, 130, 230, 130), width=1)
        for row in active:
            x0, y0, x1, y1 = row["box"]
            color = (255, 130, 0, 255) if row["visualState"] == "Y" else (0, 0, 0, 255)
            panel_draw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=color, width=3)
            panel_draw.text((x0 * sx, max(0, y0 * sy - 15)), row["shortId"], fill=(255, 0, 0, 255))
        sheet.paste(preview, (x, 112))
        draw.text((x, 96), label, fill=(30, 30, 30), font=small)
        x += preview_w + 24

    y = 112 + preview_h + 34
    draw.text((22, y), "Active boxes", fill=(30, 30, 30), font=font(16, True))
    y += 26
    headers = ["id", "target-only", "source-supported", "source mean", "avg delta", "source ink"]
    xs = [22, 112, 230, 380, 505, 620]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 18
    for row in active:
        values = [
            row["shortId"],
            row["targetOnlyDeltaShare"],
            row["sourceSupportedDeltaShare"],
            row["sourceSupportedDeltaMean"],
            row["averageDelta"],
            row["sourceInkRatio"],
        ]
        for xpos, value in zip(xs, values):
            draw.text((xpos, y), str(value), fill=(25, 25, 25), font=tiny)
        y += 18

    y += 22
    draw.text((22, y), "OVERDOSE slot controls", fill=(30, 30, 30), font=font(16, True))
    y += 26
    slot_headers = ["slot", "target-only", "source-supported", "source mean", "avg delta"]
    slot_xs = [22, 112, 230, 380, 505]
    for xpos, header in zip(slot_xs, slot_headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 18
    for row in slots:
        values = [
            f"{row['slotLetter']}{row['slotIndex']}",
            row["targetOnlyDeltaShare"],
            row["sourceSupportedDeltaShare"],
            row["sourceSupportedDeltaMean"],
            row["averageDelta"],
        ]
        for xpos, value in zip(slot_xs, values):
            draw.text((xpos, y), str(value), fill=(25, 25, 25), font=tiny)
        y += 18
    sheet.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current Scan Light-Table Self-Signal Partition Gate",
        "",
        "Scope: valid page `75 -> 76` held-to-light average blend only. The mirrored page-75 source layer is separated from page-76 target-only ink, with line-shift controls and projected OVERDOSE slots included. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active / line-shift controls / OVERDOSE slots: `{summary['activeCount']}` / `{summary['controlCount']}` / `{summary['overdoseSlotCount']}`",
        f"- Active target-only dominant rows: `{summary['activeTargetOnlyDominantCount']}/{summary['activeCount']}`",
        f"- Active source-supported dominant rows: `{summary['activeSourceSupportedDominantCount']}/{summary['activeCount']}`",
        f"- Active source-supported mean above control p95 rows: `{summary['activeSourceSupportedMeanAboveControlP95Count']}/{summary['activeCount']}`",
        f"- Active source-supported share above control p95 rows: `{summary['activeSourceSupportedShareAboveControlP95Count']}/{summary['activeCount']}`",
        f"- Active min target-only delta share: `{summary['activeMinTargetOnlyDeltaShare']}`",
        f"- Active max source-supported delta share: `{summary['activeMaxSourceSupportedDeltaShare']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['lightTableSelfSignalPartitionFingerprint']}`",
        "",
        "## Active Rows",
        "",
        "| id | target-only share | source-supported share | source-supported mean | avg delta | source ink |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["rows"]:
        if row["kind"] != "active":
            continue
        lines.append(
            f"| `{row['shortId']}` | `{row['targetOnlyDeltaShare']}` | `{row['sourceSupportedDeltaShare']}` | `{row['sourceSupportedDeltaMean']}` | `{row['averageDelta']}` | `{row['sourceInkRatio']}` |"
        )
    lines.extend(
        [
            "",
            "## OVERDOSE Slot Controls",
            "",
            "| slot | target-only share | source-supported share | source-supported mean | avg delta |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in result["rows"]:
        if row["kind"] != "overdose_slot":
            continue
        lines.append(
            f"| `{row['slotLetter']}{row['slotIndex']}` | `{row['targetOnlyDeltaShare']}` | `{row['sourceSupportedDeltaShare']}` | `{row['sourceSupportedDeltaMean']}` | `{row['averageDelta']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`.",
            f"- Reason: {result['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    triggers = load_json(REOPEN_TRIGGER_MATRIX)
    prior = load_json(B4_SELF_SIGNAL)
    active = active_boxes(active_index)
    target_img = normalize_page(76)
    source_img = shifted_mirrored_source(normalize_page(75), 0, 0)
    target_arr = np.asarray(target_img.convert("RGB"))
    source_arr = np.asarray(source_img.convert("RGB"))
    blend_arr = average_blend(target_arr, source_arr)
    source_ink_mask = luma(source_arr) < SOURCE_INK_LUMA_THRESHOLD
    target_ink_mask = luma(target_arr) < TARGET_INK_LUMA_THRESHOLD
    pitch = estimated_line_pitch(active)
    controls = line_shift_controls(active, target_img.size, pitch)
    slots = overdose_slot_boxes(c9)
    inspected = active + controls + slots
    rows = [
        measure_region(target_arr, source_arr, blend_arr, source_ink_mask, target_ink_mask, row)
        for row in inspected
    ]
    summary = summarize(rows, triggers, prior)

    decision = "light_table_visual_pop_is_target_self_signal"
    reason = (
        "The valid 75->76 average blend is dominated by page-76 target-only ink across all active boxes; "
        "no active row is source-supported-dominant, and source-backed R3 remains absent."
    )
    next_move = (
        "Stop treating the attractive valid light-table blend as source evidence. Continue only with a new "
        "physical/original-layout source or raw clue wording that supplies a real source layer, unit, and order."
    )
    if summary["selfSignalSelectorCandidate"]:
        decision = "light_table_source_supported_partition_requires_review"
        reason = "A source-backed all-active source-supported condition appeared; review manually before extraction."
        next_move = "Inspect the source-supported layer against the source-reopen requirements."

    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "valid 75->76 light-table self-signal partition; no extraction, candidates, hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "b4SelfSignalGuardrail": rel(B4_SELF_SIGNAL),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))),
            "targetPage": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=76))),
            "alpha": AVERAGE_ALPHA,
            "sourceInkLumaThreshold": SOURCE_INK_LUMA_THRESHOLD,
            "targetInkLumaThreshold": TARGET_INK_LUMA_THRESHOLD,
        },
        "rows": rows,
        "summary": summary,
        "decision": decision,
        "reason": reason,
        "nextMove": next_move,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(target_img, source_img, Image.fromarray(blend_arr), rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(summary["lightTableSelfSignalPartitionFingerprint"])


if __name__ == "__main__":
    main()
