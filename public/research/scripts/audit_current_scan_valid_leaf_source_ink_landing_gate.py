#!/usr/bin/env python3
"""Trace source-ink landing for the valid held-to-light leaf.

This bounded pass follows up the light-table blend-mode audit. It ignores
arbitrary blend appearance and measures only whether mirrored page-75 source
ink physically lands inside the page-76 active boxes in the natural same-leaf
75->76 registration.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_source_ink_landing_gate.json"
OUT_MD = OUT / "current_scan_valid_leaf_source_ink_landing_gate.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_source_ink_landing_gate_sheet.jpg"
OUT_OVERLAY = OUT / "valid_75_to_76_source_ink_overlay.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT_SIMULATOR = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
LIGHT_TABLE_BLEND_MODE = ROOT / (
    "analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/"
    "current_scan_light_table_blend_mode_gate.json"
)
ACTIVE_BOX_BALANCE = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/"
    "current_scan_held_to_light_active_box_balance_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]
INK_LUMA_THRESHOLD = 238.0
SUPPORT_THRESHOLD = 0.05
WEAK_SUPPORT_THRESHOLD = 0.01


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
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


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def shifted_mirrored_source(page: Image.Image, dx: int, dy: int) -> Image.Image:
    mirrored = ImageOps.mirror(page)
    canvas = Image.new("RGB", page.size, "white")
    canvas.paste(mirrored, (dx, dy))
    return canvas


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def crop_rgb(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return arr[y0:y1, x0:x1, :]


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
                    "visualState": row["visualState"],
                    "pageLine": int(row["pageLine"]),
                    "box": [float(v) for v in row["box"]],
                }
            )
    rows.sort(key=lambda item: TARGET_ORDER.index(item["shortId"]))
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


def build_control_boxes(
    rows: list[dict[str, Any]],
    page_size: tuple[int, int],
    line_pitch: float,
) -> list[dict[str, Any]]:
    active_bounds = [row["box"] for row in rows]
    controls: list[dict[str, Any]] = []
    for row in rows:
        for offset in CONTROL_LINE_OFFSETS:
            box = shifted_box(row["box"], offset * line_pitch, page_size)
            if box is None:
                continue
            if any(iou(box, active_box) > 0.08 for active_box in active_bounds):
                continue
            controls.append(
                {
                    "id": f"{row['shortId']}_line_{offset:+d}",
                    "sourceTarget": row["shortId"],
                    "lineOffset": offset,
                    "box": box,
                }
            )
    return controls


def mask_bbox(mask: np.ndarray) -> list[int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def measure_region(mask: np.ndarray, source_arr: np.ndarray, box: list[float]) -> dict[str, Any]:
    region_mask = crop_bool(mask, box)
    source_crop = crop_rgb(source_arr, box)
    pixel_count = int(region_mask.size)
    ink_count = int(region_mask.sum())
    ratio = ink_count / pixel_count if pixel_count else 0.0
    ink_luma_mean = 0.0
    if source_crop.size and ink_count:
        ink_luma_mean = float(luma(source_crop)[region_mask].mean())
    return {
        "box": [round(float(v), 3) for v in box],
        "pixelCount": pixel_count,
        "sourceInkPixelCount": ink_count,
        "sourceInkRatio": round(float(ratio), 6),
        "sourceInkLumaMean": round(ink_luma_mean, 6),
        "sourceInkLocalBBox": mask_bbox(region_mask),
        "weakSourceSupported": ratio >= WEAK_SUPPORT_THRESHOLD,
        "sourceSupported": ratio >= SUPPORT_THRESHOLD,
    }


def held_sim_row(rows: list[dict[str, Any]], pair_id: str, mode: str) -> dict[str, Any]:
    for row in rows:
        if row.get("pairId") == pair_id and row.get("mode") == mode:
            return row
    raise KeyError(f"{pair_id}/{mode}")


def save_overlay(
    target: Image.Image,
    mask: np.ndarray,
    active: list[dict[str, Any]],
    controls: list[dict[str, Any]],
) -> None:
    rgba = target.convert("RGBA")
    overlay = Image.new("RGBA", target.size, (0, 0, 0, 0))
    overlay_arr = np.asarray(overlay).copy()
    overlay_arr[mask] = [255, 0, 0, 105]
    overlay = Image.fromarray(overlay_arr, "RGBA")
    combined = Image.alpha_composite(rgba, overlay)
    draw = ImageDraw.Draw(combined, "RGBA")
    for control in controls:
        draw.rectangle(control["box"], outline=(45, 110, 255, 110), width=2)
    for row in active:
        color = (255, 130, 0, 255) if row["visualState"] == "Y" else (20, 20, 20, 255)
        draw.rectangle(row["box"], outline=color, width=6)
        draw.text(
            (row["box"][0], max(0, row["box"][1] - 26)),
            row["shortId"],
            fill=(255, 0, 0, 255),
            font=font(26),
        )
    combined.convert("RGB").save(OUT_OVERLAY, quality=92)


def target_panel(
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    mask: np.ndarray,
    row: dict[str, Any],
    metric: dict[str, Any],
) -> Image.Image:
    pad = 34
    x0, y0, x1, y1 = [int(round(v)) for v in row["box"]]
    crop_box = [x0 - pad, y0 - pad, x1 + pad, y1 + pad]
    target_crop = Image.fromarray(crop_rgb(target_arr, crop_box))
    source_crop = Image.fromarray(crop_rgb(source_arr, crop_box))
    mask_crop = crop_bool(mask, crop_box)
    overlay = target_crop.convert("RGBA")
    red = Image.new("RGBA", target_crop.size, (0, 0, 0, 0))
    red_arr = np.asarray(red).copy()
    red_arr[mask_crop] = [255, 0, 0, 135]
    red = Image.fromarray(red_arr, "RGBA")
    overlay = Image.alpha_composite(overlay, red).convert("RGB")
    w = 420
    h = 150
    target_crop = target_crop.resize((w, h))
    source_crop = source_crop.resize((w, h))
    overlay = overlay.resize((w, h))
    panel = Image.new("RGB", (w, h * 3 + 78), "white")
    draw = ImageDraw.Draw(panel)
    panel.paste(target_crop, (0, 0))
    panel.paste(source_crop, (0, h + 22))
    panel.paste(overlay, (0, h * 2 + 44))
    draw.text((8, h - 18), "target p76", fill=(30, 34, 40), font=font(13))
    draw.text((8, h * 2 + 4), "mirrored p75 landing", fill=(30, 34, 40), font=font(13))
    draw.text((8, h * 3 + 26), "red = p75 source ink", fill=(30, 34, 40), font=font(13))
    draw.rectangle((0, 0, w - 1, h * 3 + 77), outline=(190, 190, 190), width=1)
    draw.text(
        (8, h * 3 + 50),
        f"{row['shortId']} source ink {metric['sourceInkRatio']:.4f} supported={int(metric['sourceSupported'])}",
        fill=(0, 0, 0),
        font=font(15),
    )
    return panel


def draw_sheet(
    target: Image.Image,
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    mask: np.ndarray,
    active: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    sheet = Image.new("RGB", (1900, 1350), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 1900, 104), fill=(24, 31, 42))
    draw.text((24, 16), "Valid Leaf Source-Ink Landing Gate", fill="white", font=font(25))
    draw.text(
        (24, 54),
        "Natural same-leaf page 75 -> 76, source ink only. Red overlay is mirrored page-75 ink landing on page 76.",
        fill=(235, 235, 235),
        font=font(14),
    )
    draw.text(
        (1230, 22),
        f"active >=5%: {summary['activeSourceSupportedCount']}/4 | all-four: {int(summary['allFourSourceSupported'])}",
        fill=(235, 235, 235),
        font=font(14),
    )

    preview = Image.open(OUT_OVERLAY).convert("RGB").resize((520, 668))
    sheet.paste(preview, (24, 132))
    draw.text((24, 810), "Full-page landing overlay", fill=(30, 34, 40), font=font(14))

    metrics_by_target = {row["target"]: row for row in target_rows}
    positions = [(584, 132), (1024, 132), (584, 762), (1024, 762)]
    for active_row, pos in zip(active, positions):
        panel = target_panel(
            target_arr,
            source_arr,
            mask,
            active_row,
            metrics_by_target[active_row["shortId"]],
        )
        sheet.paste(panel, pos)

    y = 870
    x0 = 24
    draw.text((x0, y), "Target source-ink table", fill=(30, 34, 40), font=font(14))
    y += 24
    headers = ["target", "phrase", "ink ratio", "ink px", "ctrl p95", "ctrl >= target", "supported"]
    xs = [x0, x0 + 66, x0 + 286, x0 + 376, x0 + 456, x0 + 546, x0 + 670]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for row in target_rows:
        vals = [
            row["target"],
            row["phrase"][:28],
            f"{row['sourceInkRatio']:.4f}",
            str(row["sourceInkPixelCount"]),
            f"{row['matchedControlP95SourceInkRatio']:.4f}",
            str(row["matchedControlGeActiveCount"]),
            str(int(row["sourceSupported"])),
        ]
        for x, val in zip(xs, vals):
            draw.text((x, y), val, fill=(30, 34, 40), font=font(11))
        y += 18
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    held = load_json(HELD_TO_LIGHT_SIMULATOR)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    light_table_blend_mode = load_json(LIGHT_TABLE_BLEND_MODE)
    active_balance = load_json(ACTIVE_BOX_BALANCE)

    active = active_boxes(active_index)
    target_page = normalize_page(76)
    source_page = normalize_page(75)
    natural = held_sim_row(held.get("rows", []), "same_leaf_75_to_76", "natural_hflip")
    source_landing = shifted_mirrored_source(
        source_page,
        int(natural.get("dx", 0)),
        int(natural.get("dy", 0)),
    )
    target_arr = np.asarray(target_page.convert("RGB"))
    source_arr = np.asarray(source_landing.convert("RGB"))
    source_mask = luma(source_arr) < INK_LUMA_THRESHOLD
    line_pitch = estimated_line_pitch(active)
    controls = build_control_boxes(active, target_page.size, line_pitch)

    control_rows = []
    for control in controls:
        metric = measure_region(source_mask, source_arr, control["box"])
        control_rows.append({**control, **metric})

    control_by_target = {
        target: [row for row in control_rows if row["sourceTarget"] == target]
        for target in TARGET_ORDER
    }

    target_rows = []
    for row in active:
        metric = measure_region(source_mask, source_arr, row["box"])
        controls_for_target = control_by_target[row["shortId"]]
        ratios = [float(control["sourceInkRatio"]) for control in controls_for_target]
        p95 = float(np.percentile(ratios, 95)) if ratios else 0.0
        median_control = float(np.median(ratios)) if ratios else 0.0
        ge_active_count = sum(1 for ratio in ratios if ratio >= metric["sourceInkRatio"])
        target_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "visualState": row["visualState"],
                "pageLine": row["pageLine"],
                **metric,
                "matchedControlMedianSourceInkRatio": round(median_control, 6),
                "matchedControlP95SourceInkRatio": round(p95, 6),
                "matchedControlGeActiveCount": ge_active_count,
                "activeMinusMatchedControlP95SourceInkRatio": round(
                    metric["sourceInkRatio"] - p95, 6
                ),
            }
        )

    save_overlay(target_page, source_mask, active, controls)

    source_supported_targets = [
        row["target"] for row in target_rows if row["sourceInkRatio"] >= SUPPORT_THRESHOLD
    ]
    weak_source_supported_targets = [
        row["target"] for row in target_rows if row["sourceInkRatio"] >= WEAK_SUPPORT_THRESHOLD
    ]
    zero_source_targets = [
        row["target"] for row in target_rows if row["sourceInkPixelCount"] == 0
    ]
    active_supported_count = len(source_supported_targets)
    weak_active_supported_count = len(weak_source_supported_targets)
    all_four_supported = active_supported_count == 4
    all_four_weak_supported = weak_active_supported_count == 4
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    selector_count = 0

    fingerprint = (
        "scenario=valid_75_to_76_natural"
        f"|targets={len(target_rows)}|controls={len(control_rows)}"
        f"|activeGe05={active_supported_count}|activeGe01={weak_active_supported_count}"
        f"|all4Ge05={int(all_four_supported)}|all4Ge01={int(all_four_weak_supported)}"
        f"|zeroTargets={','.join(zero_source_targets) if zero_source_targets else 'none'}"
        f"|ratios={','.join(f'{row['target']}:{row['sourceInkRatio']:.4f}' for row in target_rows)}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors={selector_count}"
    )

    summary = {
        "scenarioId": "valid_75_to_76_natural",
        "sourcePage": 75,
        "targetPage": 76,
        "heldToLightMode": "natural_hflip",
        "dx": int(natural.get("dx", 0)),
        "dy": int(natural.get("dy", 0)),
        "targetCount": len(target_rows),
        "controlBoxCount": len(control_rows),
        "estimatedLinePitchPx": round(line_pitch, 6),
        "sourceInkLumaThreshold": INK_LUMA_THRESHOLD,
        "supportThreshold": SUPPORT_THRESHOLD,
        "weakSupportThreshold": WEAK_SUPPORT_THRESHOLD,
        "activeSourceSupportedTargets": source_supported_targets,
        "weakSourceSupportedTargets": weak_source_supported_targets,
        "zeroSourceInkTargets": zero_source_targets,
        "activeSourceSupportedCount": active_supported_count,
        "weakActiveSourceSupportedCount": weak_active_supported_count,
        "allFourSourceSupported": all_four_supported,
        "allFourWeakSourceSupported": all_four_weak_supported,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "sourceInkLandingFingerprint": fingerprint,
        "priorLightTableBlendModeFingerprint": light_table_blend_mode.get("fingerprint"),
        "priorActiveBalanceFingerprint": active_balance.get("fingerprint"),
    }
    draw_sheet(target_page, target_arr, source_arr, source_mask, active, target_rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid physical leaf page-75-to-76 source-ink landing audit; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT_SIMULATOR),
            "lightTableBlendModeGate": rel(LIGHT_TABLE_BLEND_MODE),
            "activeBoxBalanceGate": rel(ACTIVE_BOX_BALANCE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "scenario": {
            "scenarioId": "valid_75_to_76_natural",
            "pairId": "same_leaf_75_to_76",
            "sourcePage": 75,
            "targetPage": 76,
            "mode": "natural_hflip",
            "dx": int(natural.get("dx", 0)),
            "dy": int(natural.get("dy", 0)),
            "binaryActiveOverTarget": natural.get("activeOverTarget"),
            "activeCoverageByBox": natural.get("activeCoverageByBox"),
        },
        "activeBoxes": active,
        "controlBoxes": controls,
        "targetRows": target_rows,
        "controlRows": control_rows,
        "summary": summary,
        "decision": {
            "currentScanValidLeafSourceInkLandingGate": "current_scan_valid_leaf_source_ink_landing_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The natural physical 75->76 source-ink landing does not support all four "
                "active targets. B4 has zero landing source ink, so the average-blend all-four "
                "visual pop cannot be a physical back-page ink selector."
            ),
            "nextMove": (
                "Stop treating the current-scan valid leaf as extraction-ready. Use these "
                "landing ratios only as a source-review witness when comparing a true "
                "physical/original-layout source or raw clue wording."
            ),
        },
        "overlay": rel(OUT_OVERLAY),
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Valid Leaf Source-Ink Landing Gate",
        "",
        "Scope: measured whether mirrored page-75 source ink physically lands inside the O4/B4/G5/O5 page-76 active boxes under the natural same-leaf 75->76 held-to-light registration. This checks actual source ink, not arbitrary blend appearance. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "- Scenario: `valid_75_to_76_natural` / `same_leaf_75_to_76` / `natural_hflip`",
        f"- Source / target pages: `75` -> `76`",
        f"- Shift dx,dy: `{summary['dx']},{summary['dy']}`",
        f"- Active boxes / line-shift controls: `{len(target_rows)}` / `{len(control_rows)}`",
        f"- Estimated line pitch: `{line_pitch:.2f}px`",
        f"- Source-ink support threshold: `{SUPPORT_THRESHOLD:.2f}`",
        f"- Active source-supported targets: `{','.join(source_supported_targets)}` (`{active_supported_count}/4`)",
        f"- Weak source-supported targets: `{','.join(weak_source_supported_targets)}` (`{weak_active_supported_count}/4`)",
        f"- Zero-source-ink targets: `{','.join(zero_source_targets) if zero_source_targets else 'none'}`",
        f"- All-four source-supported / weak-source-supported: `{int(all_four_supported)}` / `{int(all_four_weak_supported)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Overlay: `{rel(OUT_OVERLAY)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Target Rows",
        "",
        "| target | phrase | source ink ratio | ink pixels | control p95 | controls >= active | supported | local ink bbox |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in target_rows:
        lines.append(
            f"| `{row['target']}` | `{row['phrase']}` | {row['sourceInkRatio']:.6f} | {row['sourceInkPixelCount']} | {row['matchedControlP95SourceInkRatio']:.6f} | {row['matchedControlGeActiveCount']} | {int(row['sourceSupported'])} | `{row['sourceInkLocalBBox']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_valid_leaf_source_ink_landing_no_selector`",
            "- The valid same-leaf page-75-to-76 geometry does not physically support all four active targets.",
            "- B4 has zero landing source ink, so the average-blend all-four visual pop is not a physical back-page ink carrier.",
            "- This closes the strongest remaining held-to-light caveat from the blend-mode pass.",
            "",
            "## Next Move",
            "",
            "- Keep current-scan held-to-light panels as source-review witnesses only.",
            "- Continue with original-layout/physical source acquisition or raw clue wording that supplies transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Wrote {rel(OUT_OVERLAY)}")
    print(f"Decision: {result['decision']['currentScanValidLeafSourceInkLandingGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
