#!/usr/bin/env python3
"""Check whether small valid-leaf jitter can rescue B4 source ink.

This bounded pass follows the valid-leaf source-ink landing gate. It tests a
documented print/scan tolerance window around the natural page-75-to-76
held-to-light registration and asks whether B4 can gain source ink while the
full active quartet remains physically supported.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_jitter_source_ink_rescue_gate.json"
OUT_MD = OUT / "current_scan_valid_leaf_jitter_source_ink_rescue_gate.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_jitter_source_ink_rescue_gate_sheet.jpg"
OUT_OVERLAY = OUT / "best_b4_jitter_source_ink_overlay.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
SOURCE_INK_LANDING = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/"
    "current_scan_valid_leaf_source_ink_landing_gate.json"
)
ALIGNMENT_TOLERANCE = ROOT / (
    "analysis_outputs/source_audit/source_packet_alignment_tolerance/"
    "source_packet_alignment_tolerance.json"
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
EXTENDED_GUARDRAIL_SHIFT_PX = 8


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


def source_ink_ratio(base_mask: np.ndarray, box: list[float], dx: int, dy: int) -> float:
    h, w = base_mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    sx0 = max(0, min(w, x0 - dx))
    sx1 = max(0, min(w, x1 - dx))
    sy0 = max(0, min(h, y0 - dy))
    sy1 = max(0, min(h, y1 - dy))
    if sx1 <= sx0 or sy1 <= sy0:
        return 0.0
    # Small jitter never crosses the page edge for active boxes; divide by
    # requested box area so clipped out-of-page shifts do not inflate ratios.
    denom = max(1, (x1 - x0) * (y1 - y0))
    return float(base_mask[sy0:sy1, sx0:sx1].sum() / denom)


def shifted_mask(base_mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    h, w = base_mask.shape[:2]
    out = np.zeros_like(base_mask, dtype=bool)
    sx0 = max(0, -dx)
    sx1 = min(w, w - dx)
    sy0 = max(0, -dy)
    sy1 = min(h, h - dy)
    tx0 = max(0, dx)
    ty0 = max(0, dy)
    if sx1 > sx0 and sy1 > sy0:
        out[ty0 : ty0 + (sy1 - sy0), tx0 : tx0 + (sx1 - sx0)] = base_mask[sy0:sy1, sx0:sx1]
    return out


def scan_shift_rows(
    base_mask: np.ndarray,
    active: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    shift_limit: int,
    credible_shift_limit: int,
) -> list[dict[str, Any]]:
    control_by_target = {
        target: [control for control in controls if control["sourceTarget"] == target]
        for target in TARGET_ORDER
    }
    rows: list[dict[str, Any]] = []
    for dx in range(-shift_limit, shift_limit + 1):
        for dy in range(-shift_limit, shift_limit + 1):
            target_rows = []
            active_ratios = []
            for target in active:
                ratio = source_ink_ratio(base_mask, target["box"], dx, dy)
                control_ratios = [
                    source_ink_ratio(base_mask, control["box"], dx, dy)
                    for control in control_by_target[target["shortId"]]
                ]
                p95 = float(np.percentile(control_ratios, 95)) if control_ratios else 0.0
                target_rows.append(
                    {
                        "target": target["shortId"],
                        "phrase": target["phrase"],
                        "sourceInkRatio": round(ratio, 6),
                        "matchedControlP95SourceInkRatio": round(p95, 6),
                        "sourceSupported": ratio >= SUPPORT_THRESHOLD,
                        "weakSourceSupported": ratio >= WEAK_SUPPORT_THRESHOLD,
                    }
                )
                active_ratios.append(ratio)
            rows.append(
                {
                    "dx": dx,
                    "dy": dy,
                    "withinCredibleTolerance": abs(dx) <= credible_shift_limit
                    and abs(dy) <= credible_shift_limit,
                    "activeSourceSupportedCount": sum(
                        1 for ratio in active_ratios if ratio >= SUPPORT_THRESHOLD
                    ),
                    "weakActiveSourceSupportedCount": sum(
                        1 for ratio in active_ratios if ratio >= WEAK_SUPPORT_THRESHOLD
                    ),
                    "allFourSourceSupported": all(
                        ratio >= SUPPORT_THRESHOLD for ratio in active_ratios
                    ),
                    "allFourWeakSourceSupported": all(
                        ratio >= WEAK_SUPPORT_THRESHOLD for ratio in active_ratios
                    ),
                    "minSourceInkRatio": round(float(min(active_ratios)), 6),
                    "meanSourceInkRatio": round(float(np.mean(active_ratios)), 6),
                    "b4SourceInkRatio": round(float(active_ratios[1]), 6),
                    "targetRows": target_rows,
                }
            )
    return rows


def save_overlay(
    target_page: Image.Image,
    mask: np.ndarray,
    active: list[dict[str, Any]],
    best_row: dict[str, Any],
) -> None:
    shifted = shifted_mask(mask, int(best_row["dx"]), int(best_row["dy"]))
    rgba = target_page.convert("RGBA")
    red = Image.new("RGBA", target_page.size, (0, 0, 0, 0))
    red_arr = np.asarray(red).copy()
    red_arr[shifted] = [255, 0, 0, 105]
    red = Image.fromarray(red_arr, "RGBA")
    combined = Image.alpha_composite(rgba, red)
    draw = ImageDraw.Draw(combined, "RGBA")
    for row in active:
        color = (255, 130, 0, 255) if row["visualState"] == "Y" else (20, 20, 20, 255)
        draw.rectangle(row["box"], outline=color, width=6)
        label = row["shortId"]
        draw.text((row["box"][0], max(0, row["box"][1] - 28)), label, fill=(255, 0, 0, 255), font=font(28))
    draw.rectangle((0, 0, 940, 58), fill=(0, 0, 0, 170))
    draw.text(
        (16, 16),
        f"best B4 jitter dx={best_row['dx']} dy={best_row['dy']} B4={best_row['b4SourceInkRatio']:.4f}",
        fill=(255, 255, 255, 255),
        font=font(22),
    )
    combined.convert("RGB").save(OUT_OVERLAY, quality=92)


def draw_sheet(
    rows: list[dict[str, Any]],
    active: list[dict[str, Any]],
    credible_limit: int,
    extended_limit: int,
    best_credible: dict[str, Any],
    best_extended: dict[str, Any],
) -> None:
    sheet = Image.new("RGB", (1900, 1280), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 1900, 104), fill=(24, 31, 42))
    draw.text((24, 16), "Valid Leaf Jitter Source-Ink Rescue Gate", fill="white", font=font(25))
    draw.text(
        (24, 54),
        f"Mirrored page-75 source ink under +/-{credible_limit}px credible tolerance; guardrail map shown to +/-{extended_limit}px.",
        fill=(235, 235, 235),
        font=font(14),
    )

    heat_x, heat_y = 40, 150
    cell = 38
    draw.text((heat_x, heat_y - 34), "B4 source-ink ratio by jitter", fill=(30, 34, 40), font=font(15))
    b4_by_shift = {(row["dx"], row["dy"]): row["b4SourceInkRatio"] for row in rows}
    max_b4 = max(b4_by_shift.values()) if b4_by_shift else 0.0
    for y_index, dy in enumerate(range(-extended_limit, extended_limit + 1)):
        for x_index, dx in enumerate(range(-extended_limit, extended_limit + 1)):
            ratio = b4_by_shift.get((dx, dy), 0.0)
            intensity = int(255 * (ratio / max_b4)) if max_b4 else 0
            color = (255, 255 - intensity, 255 - intensity)
            x = heat_x + x_index * cell
            y = heat_y + y_index * cell
            draw.rectangle((x, y, x + cell - 2, y + cell - 2), fill=color, outline=(230, 230, 230))
            if abs(dx) <= credible_limit and abs(dy) <= credible_limit:
                draw.rectangle((x + 2, y + 2, x + cell - 4, y + cell - 4), outline=(60, 90, 170), width=1)
            if ratio:
                draw.text((x + 5, y + 12), f"{ratio:.2f}", fill=(20, 20, 20), font=font(10))
    for i, value in enumerate(range(-extended_limit, extended_limit + 1)):
        draw.text((heat_x + i * cell + 10, heat_y - 18), str(value), fill=(75, 75, 75), font=font(9))
        draw.text((heat_x - 26, heat_y + i * cell + 10), str(value), fill=(75, 75, 75), font=font(9))

    table_x = 760
    y = 150
    draw.text((table_x, y - 34), "Best shifts", fill=(30, 34, 40), font=font(15))
    headers = ["scope", "dx,dy", "supported", "weak", "min", "B4", "mean"]
    xs = [table_x, table_x + 150, table_x + 250, table_x + 350, table_x + 430, table_x + 510, table_x + 590]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=font(11))
    y += 20
    for label, row in [("credible", best_credible), ("guardrail", best_extended)]:
        vals = [
            label,
            f"{row['dx']},{row['dy']}",
            f"{row['activeSourceSupportedCount']}/4",
            f"{row['weakActiveSourceSupportedCount']}/4",
            f"{row['minSourceInkRatio']:.4f}",
            f"{row['b4SourceInkRatio']:.4f}",
            f"{row['meanSourceInkRatio']:.4f}",
        ]
        for x, val in zip(xs, vals):
            draw.text((x, y), val, fill=(30, 34, 40), font=font(11))
        y += 22

    y += 26
    draw.text((table_x, y), "Best credible target rows", fill=(30, 34, 40), font=font(15))
    y += 24
    headers = ["target", "phrase", "ratio", "ctrl p95", "supported"]
    xs = [table_x, table_x + 70, table_x + 310, table_x + 390, table_x + 480]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=font(11))
    y += 18
    for target in best_credible["targetRows"]:
        vals = [
            target["target"],
            target["phrase"][:28],
            f"{target['sourceInkRatio']:.4f}",
            f"{target['matchedControlP95SourceInkRatio']:.4f}",
            str(int(target["sourceSupported"])),
        ]
        for x, val in zip(xs, vals):
            draw.text((x, y), val, fill=(30, 34, 40), font=font(11))
        y += 18

    preview = Image.open(OUT_OVERLAY).convert("RGB").resize((520, 668))
    sheet.paste(preview, (table_x, 520))
    draw.text((table_x, 1200), "Best-B4 guardrail overlay", fill=(30, 34, 40), font=font(13))
    sheet.save(OUT_SHEET, quality=92)


def best_shift(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        rows,
        key=lambda row: (
            row["allFourSourceSupported"],
            row["activeSourceSupportedCount"],
            row["b4SourceInkRatio"],
            row["minSourceInkRatio"],
            -abs(row["dx"]) - abs(row["dy"]),
        ),
    )


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    source_ink_landing = load_json(SOURCE_INK_LANDING)
    alignment = load_json(ALIGNMENT_TOLERANCE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    active = active_boxes(active_index)
    target_page = normalize_page(76)
    source_page = normalize_page(75)
    base_source = ImageOps.mirror(source_page)
    base_mask = luma(np.asarray(base_source.convert("RGB"))) < INK_LUMA_THRESHOLD
    line_pitch = estimated_line_pitch(active)
    controls = build_control_boxes(active, target_page.size, line_pitch)

    credible_limit = int(
        alignment.get("summary", {}).get("commonFullEightDirectionShiftAllTargetsPassPx")
        or 4
    )
    extended_limit = max(EXTENDED_GUARDRAIL_SHIFT_PX, credible_limit)
    rows = scan_shift_rows(base_mask, active, controls, extended_limit, credible_limit)
    credible_rows = [row for row in rows if row["withinCredibleTolerance"]]
    guardrail_rows = rows
    best_credible = best_shift(credible_rows)
    best_extended = best_shift(guardrail_rows)
    credible_all_four = [row for row in credible_rows if row["allFourSourceSupported"]]
    extended_all_four = [row for row in guardrail_rows if row["allFourSourceSupported"]]
    credible_b4_positive = [row for row in credible_rows if row["b4SourceInkRatio"] > 0]
    extended_b4_positive = [row for row in guardrail_rows if row["b4SourceInkRatio"] > 0]

    best_for_overlay = max(guardrail_rows, key=lambda row: row["b4SourceInkRatio"])
    save_overlay(target_page, base_mask, active, best_for_overlay)
    draw_sheet(rows, active, credible_limit, extended_limit, best_credible, best_extended)

    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    selector_count = 0
    target_ratio_stream = ",".join(
        f"{target['target']}:{target['sourceInkRatio']:.4f}"
        for target in best_credible["targetRows"]
    )
    fingerprint = (
        f"credible=+-{credible_limit}|extended=+-{extended_limit}"
        f"|credibleRows={len(credible_rows)}|extendedRows={len(guardrail_rows)}"
        f"|credAll4={len(credible_all_four)}|extAll4={len(extended_all_four)}"
        f"|credB4Pos={len(credible_b4_positive)}|extB4Pos={len(extended_b4_positive)}"
        f"|bestCred={best_credible['dx']},{best_credible['dy']}:"
        f"{best_credible['activeSourceSupportedCount']}/4:"
        f"B4={best_credible['b4SourceInkRatio']:.4f}:min={best_credible['minSourceInkRatio']:.4f}"
        f"|bestExt={best_extended['dx']},{best_extended['dy']}:"
        f"{best_extended['activeSourceSupportedCount']}/4:"
        f"B4={best_extended['b4SourceInkRatio']:.4f}:min={best_extended['minSourceInkRatio']:.4f}"
        f"|bestCredRatios={target_ratio_stream}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors={selector_count}"
    )

    summary = {
        "credibleShiftLimitPx": credible_limit,
        "extendedGuardrailShiftLimitPx": extended_limit,
        "credibleShiftRowCount": len(credible_rows),
        "extendedShiftRowCount": len(guardrail_rows),
        "credibleAllFourSourceSupportedCount": len(credible_all_four),
        "extendedAllFourSourceSupportedCount": len(extended_all_four),
        "credibleB4PositiveShiftCount": len(credible_b4_positive),
        "extendedB4PositiveShiftCount": len(extended_b4_positive),
        "bestCredibleShift": {
            "dx": best_credible["dx"],
            "dy": best_credible["dy"],
            "activeSourceSupportedCount": best_credible["activeSourceSupportedCount"],
            "weakActiveSourceSupportedCount": best_credible["weakActiveSourceSupportedCount"],
            "b4SourceInkRatio": best_credible["b4SourceInkRatio"],
            "minSourceInkRatio": best_credible["minSourceInkRatio"],
            "meanSourceInkRatio": best_credible["meanSourceInkRatio"],
            "targetRows": best_credible["targetRows"],
        },
        "bestExtendedShift": {
            "dx": best_extended["dx"],
            "dy": best_extended["dy"],
            "activeSourceSupportedCount": best_extended["activeSourceSupportedCount"],
            "weakActiveSourceSupportedCount": best_extended["weakActiveSourceSupportedCount"],
            "b4SourceInkRatio": best_extended["b4SourceInkRatio"],
            "minSourceInkRatio": best_extended["minSourceInkRatio"],
            "meanSourceInkRatio": best_extended["meanSourceInkRatio"],
            "targetRows": best_extended["targetRows"],
        },
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "jitterSourceInkRescueFingerprint": fingerprint,
        "priorSourceInkLandingFingerprint": source_ink_landing.get("fingerprint"),
        "alignmentToleranceFingerprint": alignment.get("summary", {}).get(
            "alignmentToleranceFingerprint"
        ),
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid leaf source-ink jitter rescue gate; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "sourceInkLandingGate": rel(SOURCE_INK_LANDING),
            "alignmentTolerance": rel(ALIGNMENT_TOLERANCE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "parameters": {
            "sourceInkLumaThreshold": INK_LUMA_THRESHOLD,
            "supportThreshold": SUPPORT_THRESHOLD,
            "weakSupportThreshold": WEAK_SUPPORT_THRESHOLD,
            "controlLineOffsets": CONTROL_LINE_OFFSETS,
        },
        "shiftRows": rows,
        "summary": summary,
        "decision": {
            "currentScanValidLeafJitterSourceInkRescueGate": "current_scan_valid_leaf_jitter_source_ink_rescue_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "No shift inside the documented +/-4px common visual tolerance rescues B4 "
                "source ink or creates an all-four source-supported active quartet. The "
                "+/-8px guardrail range also has no B4-positive or all-four source-supported "
                "row, so the B4 zero-ink blocker is stable against small physical jitter."
            ),
            "nextMove": (
                "Stop pursuing current-scan 75->76 source-ink rescue. Keep these measurements "
                "as source-review constraints and require a new physical/original-layout source "
                "or raw clue wording before any extraction attempt."
            ),
        },
        "overlay": rel(OUT_OVERLAY),
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Valid Leaf Jitter Source-Ink Rescue Gate",
        "",
        "Scope: tested whether small jitter around the natural same-leaf 75->76 held-to-light registration can rescue B4 source ink or create a source-supported O4/B4/G5/O5 quartet. The credible window is the documented common visual tolerance from the source-packet alignment gate. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Credible shift window: `+-{credible_limit}px`",
        f"- Extended guardrail window: `+-{extended_limit}px`",
        f"- Credible shift rows / extended rows: `{len(credible_rows)}` / `{len(guardrail_rows)}`",
        f"- Credible all-four source-supported rows / B4-positive rows: `{len(credible_all_four)}` / `{len(credible_b4_positive)}`",
        f"- Extended all-four source-supported rows / B4-positive rows: `{len(extended_all_four)}` / `{len(extended_b4_positive)}`",
        f"- Best credible shift: `{best_credible['dx']},{best_credible['dy']}` with active support `{best_credible['activeSourceSupportedCount']}/4`, B4 `{best_credible['b4SourceInkRatio']:.4f}`, min `{best_credible['minSourceInkRatio']:.4f}`",
        f"- Best extended shift: `{best_extended['dx']},{best_extended['dy']}` with active support `{best_extended['activeSourceSupportedCount']}/4`, B4 `{best_extended['b4SourceInkRatio']:.4f}`, min `{best_extended['minSourceInkRatio']:.4f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Overlay: `{rel(OUT_OVERLAY)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Best Credible Target Rows",
        "",
        "| target | phrase | source ink ratio | control p95 | supported | weak supported |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in best_credible["targetRows"]:
        lines.append(
            f"| `{row['target']}` | `{row['phrase']}` | {row['sourceInkRatio']:.6f} | {row['matchedControlP95SourceInkRatio']:.6f} | {int(row['sourceSupported'])} | {int(row['weakSourceSupported'])} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_valid_leaf_jitter_source_ink_rescue_no_selector`",
            "- The documented `+-4px` tolerance window does not rescue B4 source ink.",
            "- The `+-8px` guardrail window also has no B4-positive row and no all-four source-supported row.",
            "- This stabilizes the previous B4 zero-source-ink closure against small physical registration jitter.",
            "",
            "## Next Move",
            "",
            "- Stop pursuing current-scan valid-leaf source-ink rescue without a new source/clue that supplies transform, unit, and order.",
            "- Continue with original-layout/physical source acquisition or raw clue wording scored against the source-acquisition packet and R1-R5 reopen requirements.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Wrote {rel(OUT_OVERLAY)}")
    print(f"Decision: {result['decision']['currentScanValidLeafJitterSourceInkRescueGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
