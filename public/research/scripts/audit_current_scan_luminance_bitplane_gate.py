#!/usr/bin/env python3
"""Audit current page-76 scan luminance bit/threshold planes.

This bounded pass checks whether O4/B4/G5/O5 or projected OVERDOSE slots show
unique low-order luminance bit-plane or simple threshold-plane behavior against
shifted controls. It is a scan-artifact/source-quality gate, not extraction.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_luminance_bitplane_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_luminance_bitplane_gate.json"
OUT_MD = OUT / "current_scan_luminance_bitplane_gate.md"
OUT_SHEET = OUT / "current_scan_luminance_bitplane_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

LOW_BITS = [0, 1, 2, 3]
THRESHOLDS = [64, 96, 128, 160, 192]
OUTLIER_Z = 3.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def clamp_box(box: list[float], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [
        max(0.0, min(float(width), x0)),
        max(0.0, min(float(height), y0)),
        max(0.0, min(float(width), x1)),
        max(0.0, min(float(height), y1)),
    ]


def crop_array(image: Image.Image, box: list[float]) -> np.ndarray:
    x0, y0, x1, y1 = [round(v) for v in box]
    x0 = max(0, min(image.width, x0))
    x1 = max(0, min(image.width, x1))
    y0 = max(0, min(image.height, y0))
    y1 = max(0, min(image.height, y1))
    crop = image.crop((x0, y0, x1, y1)).convert("L")
    return np.asarray(crop, dtype=np.uint8)


def c9_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "shortId": f"slot{slot['index']}_{slot['letter']}",
                "phrase": f"C9 projected OVERDOSE slot {slot['letter']}",
                "visualState": "N",
                "kind": "overdose_slot",
                "box": [float(slot["left"]), float(frame[1]), float(slot["right"]), float(frame[3])],
            }
        )
    return rows


def shifted_control_boxes(active_boxes: list[dict[str, Any]], size: tuple[int, int]) -> list[dict[str, Any]]:
    width, height = size
    rows: list[dict[str, Any]] = []
    for box in active_boxes:
        x0, y0, x1, y1 = box["box"]
        for dy in [-292, -146, 146, 292]:
            shifted = clamp_box([x0, y0 + dy, x1, y1 + dy], width, height)
            if shifted[3] > shifted[1] and shifted[2] > shifted[0]:
                rows.append(
                    {
                        "shortId": f"{box['shortId']}_dy{dy:+d}",
                        "phrase": f"{box['shortId']} shifted {dy:+d}px",
                        "visualState": "control",
                        "kind": "shifted_control",
                        "box": shifted,
                    }
                )
    return rows


def binary_entropy(one_ratio: float) -> float:
    if one_ratio <= 0.0 or one_ratio >= 1.0:
        return 0.0
    return float(
        -one_ratio * math.log(one_ratio, 2)
        - (1.0 - one_ratio) * math.log(1.0 - one_ratio, 2)
    )


def transition_metrics(mask: np.ndarray) -> dict[str, float]:
    if mask.size == 0:
        return {"horizontal": 0.0, "vertical": 0.0}
    horizontal = float(np.mean(mask[:, 1:] != mask[:, :-1])) if mask.shape[1] > 1 else 0.0
    vertical = float(np.mean(mask[1:, :] != mask[:-1, :])) if mask.shape[0] > 1 else 0.0
    return {"horizontal": horizontal, "vertical": vertical}


def plane_metrics(gray: np.ndarray) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bit_rows: list[dict[str, Any]] = []
    threshold_rows: list[dict[str, Any]] = []
    for bit in LOW_BITS:
        mask = ((gray >> bit) & 1).astype(np.uint8)
        one_ratio = float(mask.mean()) if mask.size else 0.0
        transitions = transition_metrics(mask)
        bit_rows.append(
            {
                "bit": bit,
                "oneRatio": round(one_ratio, 6),
                "entropy": round(binary_entropy(one_ratio), 6),
                "horizontalTransition": round(transitions["horizontal"], 6),
                "verticalTransition": round(transitions["vertical"], 6),
            }
        )
    for threshold in THRESHOLDS:
        mask = (gray <= threshold).astype(np.uint8)
        dark_ratio = float(mask.mean()) if mask.size else 0.0
        transitions = transition_metrics(mask)
        threshold_rows.append(
            {
                "threshold": threshold,
                "darkRatio": round(dark_ratio, 6),
                "entropy": round(binary_entropy(dark_ratio), 6),
                "horizontalTransition": round(transitions["horizontal"], 6),
                "verticalTransition": round(transitions["vertical"], 6),
            }
        )
    return bit_rows, threshold_rows


def inspect_region(image: Image.Image, row: dict[str, Any]) -> dict[str, Any]:
    gray = crop_array(image, row["box"])
    bit_rows, threshold_rows = plane_metrics(gray)
    bit_signature = "|".join(f"b{item['bit']}={item['oneRatio']:.2f}" for item in bit_rows)
    threshold_signature = "|".join(
        f"t{item['threshold']}={item['darkRatio']:.2f}" for item in threshold_rows
    )
    x0, y0, x1, y1 = row["box"]
    return {
        **row,
        "width": round(float(x1 - x0), 6),
        "height": round(float(y1 - y0), 6),
        "meanLuminance": round(float(gray.mean()) if gray.size else 0.0, 6),
        "stdLuminance": round(float(gray.std()) if gray.size else 0.0, 6),
        "lowBitPlanes": bit_rows,
        "thresholdPlanes": threshold_rows,
        "lowBitSignature": bit_signature,
        "thresholdSignature": threshold_signature,
    }


def control_stats(rows: list[dict[str, Any]], path: list[str | int]) -> dict[str, float]:
    values = []
    for row in rows:
        item: Any = row
        for key in path:
            item = item[key]
        values.append(float(item))
    if not values:
        return {"mean": 0.0, "std": 0.0}
    arr = np.asarray(values, dtype=np.float64)
    return {"mean": float(arr.mean()), "std": float(arr.std())}


def zscore(value: float, stats: dict[str, float]) -> float:
    if stats["std"] < 1e-9:
        return 0.0
    return float((value - stats["mean"]) / stats["std"])


def annotate_outliers(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = [row for row in rows if row["kind"] == "shifted_control"]
    bit_density_stats = {
        bit: control_stats(controls, ["lowBitPlanes", idx, "oneRatio"])
        for idx, bit in enumerate(LOW_BITS)
    }
    bit_entropy_stats = {
        bit: control_stats(controls, ["lowBitPlanes", idx, "entropy"])
        for idx, bit in enumerate(LOW_BITS)
    }
    bit_htrans_stats = {
        bit: control_stats(controls, ["lowBitPlanes", idx, "horizontalTransition"])
        for idx, bit in enumerate(LOW_BITS)
    }
    bit_vtrans_stats = {
        bit: control_stats(controls, ["lowBitPlanes", idx, "verticalTransition"])
        for idx, bit in enumerate(LOW_BITS)
    }
    threshold_dark_stats = {
        threshold: control_stats(controls, ["thresholdPlanes", idx, "darkRatio"])
        for idx, threshold in enumerate(THRESHOLDS)
    }

    for row in rows:
        density_z = []
        entropy_z = []
        transition_z = []
        for idx, bit in enumerate(LOW_BITS):
            plane = row["lowBitPlanes"][idx]
            density_z.append(abs(zscore(float(plane["oneRatio"]), bit_density_stats[bit])))
            entropy_z.append(abs(zscore(float(plane["entropy"]), bit_entropy_stats[bit])))
            transition_z.append(
                max(
                    abs(zscore(float(plane["horizontalTransition"]), bit_htrans_stats[bit])),
                    abs(zscore(float(plane["verticalTransition"]), bit_vtrans_stats[bit])),
                )
            )
        threshold_z = []
        for idx, threshold in enumerate(THRESHOLDS):
            plane = row["thresholdPlanes"][idx]
            threshold_z.append(abs(zscore(float(plane["darkRatio"]), threshold_dark_stats[threshold])))
        row["maxLowBitDensityAbsZ"] = round(max(density_z), 6) if density_z else 0.0
        row["maxLowBitEntropyAbsZ"] = round(max(entropy_z), 6) if entropy_z else 0.0
        row["maxLowBitTransitionAbsZ"] = round(max(transition_z), 6) if transition_z else 0.0
        row["maxThresholdDarkRatioAbsZ"] = round(max(threshold_z), 6) if threshold_z else 0.0
        row["lowBitOutlier"] = bool(
            row["maxLowBitDensityAbsZ"] >= OUTLIER_Z
            or row["maxLowBitEntropyAbsZ"] >= OUTLIER_Z
            or row["maxLowBitTransitionAbsZ"] >= OUTLIER_Z
        )
        row["thresholdOutlier"] = bool(row["maxThresholdDarkRatioAbsZ"] >= OUTLIER_Z)

    return {
        "bitDensityStats": bit_density_stats,
        "bitEntropyStats": bit_entropy_stats,
        "bitHorizontalTransitionStats": bit_htrans_stats,
        "bitVerticalTransitionStats": bit_vtrans_stats,
        "thresholdDarkRatioStats": threshold_dark_stats,
    }


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 1260), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan Luminance Bitplane Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 active boxes, shifted controls, and C9 OVERDOSE slots checked for low-bit and threshold-plane anomalies.",
        fill=(235, 235, 235),
        font=small,
    )

    preview = image.resize((720, round(720 * image.height / image.width)))
    pdraw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height
    for row in rows:
        if row["kind"] not in {"active", "overdose_slot"}:
            continue
        x0, y0, x1, y1 = row["box"]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        color = (255, 128, 0, 230) if row["kind"] == "active" else (30, 90, 255, 170)
        pdraw.rectangle(rect, outline=color, width=3)
        pdraw.text((rect[0], max(0, rect[1] - 16)), row["shortId"], fill=(255, 0, 0, 255))
    sheet.paste(preview, (24, 120))

    x0 = 780
    y = 120
    draw.text((x0, y), "Strongest plane outlier rows", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "bit sig", "densZ", "entZ", "trZ", "thrZ"]
    xs = [x0, x0 + 110, x0 + 245, x0 + 500, x0 + 570, x0 + 640, x0 + 710]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    sort_rows = sorted(
        rows,
        key=lambda item: (
            item["maxLowBitDensityAbsZ"],
            item["maxLowBitEntropyAbsZ"],
            item["maxLowBitTransitionAbsZ"],
            item["maxThresholdDarkRatioAbsZ"],
        ),
        reverse=True,
    )
    for row in sort_rows[:28]:
        vals = [
            row["kind"][:14],
            row["shortId"][:16],
            row["lowBitSignature"][:34],
            f"{row['maxLowBitDensityAbsZ']:.2f}",
            f"{row['maxLowBitEntropyAbsZ']:.2f}",
            f"{row['maxLowBitTransitionAbsZ']:.2f}",
            f"{row['maxThresholdDarkRatioAbsZ']:.2f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    draw.text((780, 720), "Summary", fill=(70, 70, 70), font=small)
    summary_lines = [
        f"Active/control/slots: {summary['activeBoxCount']} / {summary['shiftedControlBoxCount']} / {summary['overdoseSlotBoxCount']}",
        f"Low-bit active outliers: {summary['activeLowBitOutlierCount']} ({','.join(summary['activeLowBitOutlierIds'])})",
        f"Threshold active outliers: {summary['activeThresholdOutlierCount']} ({','.join(summary['activeThresholdOutlierIds'])})",
        f"All four low-bit/threshold: {int(summary['allFourActiveLowBitOutlier'])} / {int(summary['allFourActiveThresholdOutlier'])}",
        f"Common low-bit sig: {summary['activeCommonLowBitSignature'] or 'mixed'}",
        f"Control/slot sig matches: {summary['controlCommonLowBitSignatureMatchCount']} / {summary['overdoseSlotCommonLowBitSignatureMatchCount']}",
        f"Max active/control/slot low-bit Z: {summary['maxActiveLowBitAbsZ']:.2f} / {summary['maxControlLowBitAbsZ']:.2f} / {summary['maxOverdoseSlotLowBitAbsZ']:.2f}",
        f"Source R3/triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]
    for idx, line in enumerate(summary_lines):
        draw.text((780, 754 + idx * 22), line, fill=(35, 35, 35), font=small)

    thumb_rows = [row for row in rows if row["kind"] == "active"]
    thumb_rows += sort_rows[:4]
    tx = 780
    ty = 960
    draw.text((tx, ty - 24), "Active crops and strongest plane rows", fill=(70, 70, 70), font=small)
    for i, row in enumerate(thumb_rows[:8]):
        crop = image.crop(tuple(round(v) for v in row["box"])).convert("RGB").resize((220, 74))
        cx = tx + (i % 4) * 250
        cy = ty + (i // 4) * 132
        sheet.paste(crop, (cx, cy))
        draw.rectangle((cx, cy, cx + 220, cy + 74), outline=(35, 35, 35), width=1)
        draw.text(
            (cx, cy + 80),
            f"{row['shortId']} bitZ {max(row['maxLowBitDensityAbsZ'], row['maxLowBitEntropyAbsZ'], row['maxLowBitTransitionAbsZ']):.2f}",
            fill=(35, 35, 35),
            font=tiny,
        )

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")

    active_boxes = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "visualState": row["visualState"],
            "kind": "active",
            "box": row["box"],
        }
        for row in active_index.get("activeRows", [])
    ]
    controls = shifted_control_boxes(active_boxes, image.size)
    slots = c9_slot_boxes(c9)
    rows = [inspect_region(image, row) for row in active_boxes + controls + slots]
    stats = annotate_outliers(rows)

    active_rows = [row for row in rows if row["kind"] == "active"]
    control_rows = [row for row in rows if row["kind"] == "shifted_control"]
    slot_rows = [row for row in rows if row["kind"] == "overdose_slot"]
    active_low_bit_outliers = [row["shortId"] for row in active_rows if row["lowBitOutlier"]]
    active_threshold_outliers = [row["shortId"] for row in active_rows if row["thresholdOutlier"]]
    all_four_low_bit = len(active_low_bit_outliers) == len(active_rows)
    all_four_threshold = len(active_threshold_outliers) == len(active_rows)
    active_low_bit_signatures = [row["lowBitSignature"] for row in active_rows]
    active_common_low_bit_signature = (
        active_low_bit_signatures[0] if len(set(active_low_bit_signatures)) == 1 else None
    )
    active_threshold_signatures = [row["thresholdSignature"] for row in active_rows]
    active_common_threshold_signature = (
        active_threshold_signatures[0] if len(set(active_threshold_signatures)) == 1 else None
    )
    control_common_low_bit_matches = (
        sum(1 for row in control_rows if row["lowBitSignature"] == active_common_low_bit_signature)
        if active_common_low_bit_signature
        else 0
    )
    slot_common_low_bit_matches = (
        sum(1 for row in slot_rows if row["lowBitSignature"] == active_common_low_bit_signature)
        if active_common_low_bit_signature
        else 0
    )

    def row_low_bit_abs_z(row: dict[str, Any]) -> float:
        return max(
            float(row["maxLowBitDensityAbsZ"]),
            float(row["maxLowBitEntropyAbsZ"]),
            float(row["maxLowBitTransitionAbsZ"]),
        )

    max_active_low_bit_z = max(row_low_bit_abs_z(row) for row in active_rows)
    max_control_low_bit_z = max(row_low_bit_abs_z(row) for row in control_rows)
    max_slot_low_bit_z = max(row_low_bit_abs_z(row) for row in slot_rows)
    max_active_threshold_z = max(float(row["maxThresholdDarkRatioAbsZ"]) for row in active_rows)
    max_control_threshold_z = max(float(row["maxThresholdDarkRatioAbsZ"]) for row in control_rows)
    max_slot_threshold_z = max(float(row["maxThresholdDarkRatioAbsZ"]) for row in slot_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    shared_active_low_bit_carrier = bool(all_four_low_bit and active_common_low_bit_signature)
    hidden_bitplane_candidate = bool(
        shared_active_low_bit_carrier
        and control_common_low_bit_matches == 0
        and slot_common_low_bit_matches == 0
        and source_r3 > 0
    )

    fingerprint = (
        f"active={len(active_rows)}|controls={len(control_rows)}|slots={len(slot_rows)}"
        f"|bits={','.join(map(str, LOW_BITS))}|thresholds={','.join(map(str, THRESHOLDS))}"
        f"|activeLowBitOutliers={len(active_low_bit_outliers)}"
        f"|activeThresholdOutliers={len(active_threshold_outliers)}"
        f"|allFourLowBit={int(all_four_low_bit)}|allFourThreshold={int(all_four_threshold)}"
        f"|sharedCarrier={int(shared_active_low_bit_carrier)}|hiddenCandidate={int(hidden_bitplane_candidate)}"
        f"|commonLowBit={active_common_low_bit_signature or 'mixed'}"
        f"|controlCommon={control_common_low_bit_matches}|slotCommon={slot_common_low_bit_matches}"
        f"|maxLowBitZ={max_active_low_bit_z:.2f}/{max_control_low_bit_z:.2f}/{max_slot_low_bit_z:.2f}"
        f"|maxThresholdZ={max_active_threshold_z:.2f}/{max_control_threshold_z:.2f}/{max_slot_threshold_z:.2f}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_rows),
        "shiftedControlBoxCount": len(control_rows),
        "overdoseSlotBoxCount": len(slot_rows),
        "lowBitPlanesChecked": LOW_BITS,
        "thresholdPlanesChecked": THRESHOLDS,
        "outlierAbsZThreshold": OUTLIER_Z,
        "activeLowBitOutlierCount": len(active_low_bit_outliers),
        "activeLowBitOutlierIds": active_low_bit_outliers,
        "activeThresholdOutlierCount": len(active_threshold_outliers),
        "activeThresholdOutlierIds": active_threshold_outliers,
        "allFourActiveLowBitOutlier": all_four_low_bit,
        "allFourActiveThresholdOutlier": all_four_threshold,
        "activeLowBitSignatures": active_low_bit_signatures,
        "activeCommonLowBitSignature": active_common_low_bit_signature,
        "activeThresholdSignatures": active_threshold_signatures,
        "activeCommonThresholdSignature": active_common_threshold_signature,
        "controlCommonLowBitSignatureMatchCount": control_common_low_bit_matches,
        "overdoseSlotCommonLowBitSignatureMatchCount": slot_common_low_bit_matches,
        "sharedActiveLowBitCarrier": shared_active_low_bit_carrier,
        "hiddenBitplaneCandidate": hidden_bitplane_candidate,
        "maxActiveLowBitAbsZ": round(max_active_low_bit_z, 6),
        "maxControlLowBitAbsZ": round(max_control_low_bit_z, 6),
        "maxOverdoseSlotLowBitAbsZ": round(max_slot_low_bit_z, 6),
        "maxActiveThresholdAbsZ": round(max_active_threshold_z, 6),
        "maxControlThresholdAbsZ": round(max_control_threshold_z, 6),
        "maxOverdoseSlotThresholdAbsZ": round(max_slot_threshold_z, 6),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "luminanceBitplaneFingerprint": fingerprint,
    }
    draw_sheet(image, rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 scan luminance bit/threshold-plane gate over active boxes, shifted controls, and projected OVERDOSE slots; no extraction or candidate generation",
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "controlStats": stats,
        "regionRows": rows,
        "decision": {
            "currentScanLuminanceBitplaneGate": "current_scan_luminance_bitplane_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Low-order luminance bit planes and simple threshold planes show active-box "
                "contrast, but the active low-bit signatures are mixed and do not form a shared "
                "carrier. Threshold-plane contrast is visible ink/highlight behavior, and no "
                "source-backed R3 unit/order/transform cue licenses this as a selector."
            ),
            "nextMove": (
                "Do not pursue current-scan low-bit or threshold-plane tuning. Continue with "
                "original-layout/physical source validation or raw clue wording that names the "
                "missing unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Luminance Bitplane Gate",
        "",
        "Scope: inspected low-order luminance bit planes and simple threshold masks in current page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots. This is a scan/source-quality gate, not extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/control/OVERDOSE-slot boxes: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Low-bit planes checked: `{LOW_BITS}`",
        f"- Threshold planes checked: `{THRESHOLDS}`",
        f"- Outlier abs-z threshold against shifted controls: `{OUTLIER_Z}`",
        f"- Active low-bit outlier rows: `{len(active_low_bit_outliers)}` (`{','.join(active_low_bit_outliers)}`)",
        f"- Active threshold-plane outlier rows: `{len(active_threshold_outliers)}` (`{','.join(active_threshold_outliers)}`)",
        f"- All-four active low-bit / threshold-plane outlier: `{int(all_four_low_bit)}` / `{int(all_four_threshold)}`",
        f"- Active common low-bit signature: `{active_common_low_bit_signature or 'mixed'}`",
        f"- Matching controls / OVERDOSE slots for common low-bit signature: `{control_common_low_bit_matches}` / `{slot_common_low_bit_matches}`",
        f"- Shared active low-bit carrier / hidden bitplane candidate: `{int(shared_active_low_bit_carrier)}` / `{int(hidden_bitplane_candidate)}`",
        f"- Max active/control/OVERDOSE low-bit abs-z: `{max_active_low_bit_z:.2f}` / `{max_control_low_bit_z:.2f}` / `{max_slot_low_bit_z:.2f}`",
        f"- Max active/control/OVERDOSE threshold abs-z: `{max_active_threshold_z:.2f}` / `{max_control_threshold_z:.2f}` / `{max_slot_threshold_z:.2f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | low-bit signature | threshold signature | low-bit outlier | threshold outlier | max bit z | max threshold z |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in sorted(
        rows,
        key=lambda item: (
            row_low_bit_abs_z(item),
            float(item["maxThresholdDarkRatioAbsZ"]),
        ),
        reverse=True,
    ):
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | `{row['lowBitSignature']}` | `{row['thresholdSignature']}` | {int(row['lowBitOutlier'])} | {int(row['thresholdOutlier'])} | {row_low_bit_abs_z(row):.2f} | {float(row['maxThresholdDarkRatioAbsZ']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_luminance_bitplane_no_selector`",
            "- The active boxes do stand out in low-bit and threshold-plane metrics, but their low-bit signatures are mixed, not a shared all-four carrier.",
            "- Threshold-plane contrast is visible ink/highlight behavior and still has no source-backed unit/order/transform clue.",
            "",
            "## Next Move",
            "",
            "- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanLuminanceBitplaneGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
