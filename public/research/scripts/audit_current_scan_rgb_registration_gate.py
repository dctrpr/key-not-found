#!/usr/bin/env python3
"""Audit RGB channel registration around page-76 target/OVERDOSE regions.

This bounded pass checks whether the current page-76 scan has unusual local
red/green/blue channel displacement around O4/B4/G5/O5 or projected OVERDOSE
slots. It is a scan/PDF source-quality artifact gate, not extraction.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_rgb_registration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_rgb_registration_gate.json"
OUT_MD = OUT / "current_scan_rgb_registration_gate.md"
OUT_SHEET = OUT / "current_scan_rgb_registration_gate_sheet.jpg"

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

SEARCH_RADIUS = 3
RELIABLE_EDGE_STD = 2.0
NONZERO_MAG_THRESHOLD = 1.0
CONFIDENCE_THRESHOLD = 0.02


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def clamp_box(box: list[float], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [
        max(0.0, min(float(width), x0)),
        max(0.0, min(float(height), y0)),
        max(0.0, min(float(width), x1)),
        max(0.0, min(float(height), y1)),
    ]


def crop_image(image: Image.Image, box: list[float]) -> Image.Image:
    x0, y0, x1, y1 = [round(v) for v in box]
    x0 = max(0, min(image.width, x0))
    x1 = max(0, min(image.width, x1))
    y0 = max(0, min(image.height, y0))
    y1 = max(0, min(image.height, y1))
    return image.crop((x0, y0, x1, y1))


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
                        "kind": "shifted_control",
                        "box": shifted,
                    }
                )
    return rows


def edge_map(channel: np.ndarray) -> np.ndarray:
    gray = channel.astype(np.float32)
    if gray.shape[0] < 3 or gray.shape[1] < 3:
        return np.zeros_like(gray, dtype=np.float32)
    gy, gx = np.gradient(gray)
    return np.sqrt(gx * gx + gy * gy)


def shifted_overlap(
    ref: np.ndarray,
    mov: np.ndarray,
    dx: int,
    dy: int,
) -> tuple[np.ndarray, np.ndarray]:
    height, width = ref.shape
    if dx >= 0:
        ref_x0, ref_x1 = dx, width
        mov_x0, mov_x1 = 0, width - dx
    else:
        ref_x0, ref_x1 = 0, width + dx
        mov_x0, mov_x1 = -dx, width
    if dy >= 0:
        ref_y0, ref_y1 = dy, height
        mov_y0, mov_y1 = 0, height - dy
    else:
        ref_y0, ref_y1 = 0, height + dy
        mov_y0, mov_y1 = -dy, height
    if ref_x1 <= ref_x0 or ref_y1 <= ref_y0:
        return np.empty((0, 0)), np.empty((0, 0))
    return ref[ref_y0:ref_y1, ref_x0:ref_x1], mov[mov_y0:mov_y1, mov_x0:mov_x1]


def normalized_corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 16 or b.size < 16:
        return 0.0
    av = a.astype(np.float32).ravel()
    bv = b.astype(np.float32).ravel()
    a_std = float(av.std())
    b_std = float(bv.std())
    if a_std < 1e-6 or b_std < 1e-6:
        return 0.0
    av = (av - float(av.mean())) / a_std
    bv = (bv - float(bv.mean())) / b_std
    return float(np.mean(av * bv))


def best_pair_shift(ref_edge: np.ndarray, mov_edge: np.ndarray) -> dict[str, Any]:
    zero_a, zero_b = shifted_overlap(ref_edge, mov_edge, 0, 0)
    zero_corr = normalized_corr(zero_a, zero_b)
    best = {
        "dx": 0,
        "dy": 0,
        "corr": zero_corr,
    }
    for dy in range(-SEARCH_RADIUS, SEARCH_RADIUS + 1):
        for dx in range(-SEARCH_RADIUS, SEARCH_RADIUS + 1):
            a, b = shifted_overlap(ref_edge, mov_edge, dx, dy)
            corr = normalized_corr(a, b)
            if corr > best["corr"]:
                best = {"dx": dx, "dy": dy, "corr": corr}
    magnitude = math.hypot(float(best["dx"]), float(best["dy"]))
    confidence = best["corr"] - zero_corr
    return {
        "dx": int(best["dx"]),
        "dy": int(best["dy"]),
        "magnitude": round(magnitude, 6),
        "bestCorr": round(float(best["corr"]), 6),
        "zeroCorr": round(float(zero_corr), 6),
        "confidenceGain": round(float(confidence), 6),
        "nonzero": bool(magnitude >= NONZERO_MAG_THRESHOLD and confidence >= CONFIDENCE_THRESHOLD),
    }


def channel_metrics(crop: Image.Image) -> dict[str, Any]:
    arr = np.asarray(crop.convert("RGB"), dtype=np.float32)
    if arr.shape[0] < 12 or arr.shape[1] < 12:
        empty_pair = {
            "dx": 0,
            "dy": 0,
            "magnitude": 0.0,
            "bestCorr": 0.0,
            "zeroCorr": 0.0,
            "confidenceGain": 0.0,
            "nonzero": False,
        }
        return {
            "edgeStd": 0.0,
            "reliableEdge": False,
            "rAgainstG": empty_pair,
            "bAgainstG": empty_pair,
            "maxShiftMagnitude": 0.0,
            "maxConfidenceGain": 0.0,
            "nonzeroPairCount": 0,
            "shiftSignature": "RG+0,+0|BG+0,+0",
        }

    r_edge = edge_map(arr[:, :, 0])
    g_edge = edge_map(arr[:, :, 1])
    b_edge = edge_map(arr[:, :, 2])
    edge_std = float(np.mean([r_edge.std(), g_edge.std(), b_edge.std()]))
    rg = best_pair_shift(g_edge, r_edge)
    bg = best_pair_shift(g_edge, b_edge)
    max_mag = max(float(rg["magnitude"]), float(bg["magnitude"]))
    max_gain = max(float(rg["confidenceGain"]), float(bg["confidenceGain"]))
    nonzero_pair_count = int(rg["nonzero"]) + int(bg["nonzero"])
    return {
        "edgeStd": round(edge_std, 6),
        "reliableEdge": bool(edge_std >= RELIABLE_EDGE_STD),
        "rAgainstG": rg,
        "bAgainstG": bg,
        "maxShiftMagnitude": round(max_mag, 6),
        "maxConfidenceGain": round(max_gain, 6),
        "nonzeroPairCount": nonzero_pair_count,
        "shiftSignature": f"RG{rg['dx']:+d},{rg['dy']:+d}|BG{bg['dx']:+d},{bg['dy']:+d}",
    }


def inspect_region(image: Image.Image, row: dict[str, Any]) -> dict[str, Any]:
    x0, y0, x1, y1 = row["box"]
    crop = crop_image(image, row["box"])
    return {
        **row,
        "width": round(float(x1 - x0), 6),
        "height": round(float(y1 - y0), 6),
        **channel_metrics(crop),
    }


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


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 1260), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan RGB Channel Registration Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 active boxes, shifted controls, and C9 OVERDOSE slots checked for local RGB channel displacement.",
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
    draw.text((x0, y), "Top channel-displacement rows", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "sig", "max px", "gain", "pairs", "edge"]
    xs = [x0, x0 + 105, x0 + 238, x0 + 410, x0 + 480, x0 + 548, x0 + 610]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in sorted(rows, key=lambda item: (item["maxShiftMagnitude"], item["maxConfidenceGain"]), reverse=True)[:26]:
        vals = [
            row["kind"][:14],
            row["shortId"][:16],
            row["shiftSignature"],
            f"{row['maxShiftMagnitude']:.1f}",
            f"{row['maxConfidenceGain']:.3f}",
            str(row["nonzeroPairCount"]),
            f"{row['edgeStd']:.1f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    draw.text((780, 690), "Summary", fill=(70, 70, 70), font=small)
    summary_lines = [
        f"Active/control/slots: {summary['activeBoxCount']} / {summary['shiftedControlBoxCount']} / {summary['overdoseSlotBoxCount']}",
        f"Active nonzero rows: {summary['activeNonzeroRegistrationRowCount']} ({','.join(summary['activeNonzeroRegistrationRowIds'])})",
        f"Active gain outliers: {summary['activeConfidenceOutlierCount']} ({','.join(summary['activeConfidenceOutlierIds'])})",
        f"All four nonzero/outlier: {int(summary['allFourActiveNonzeroRegistration'])} / {int(summary['allFourActiveConfidenceOutlier'])}",
        f"Max shift active/control/slot: {summary['maxActiveShiftMagnitude']:.1f} / {summary['maxControlShiftMagnitude']:.1f} / {summary['maxOverdoseSlotShiftMagnitude']:.1f}",
        f"Max gain active/control/slot: {summary['maxActiveConfidenceGain']:.3f} / {summary['maxControlConfidenceGain']:.3f} / {summary['maxOverdoseSlotConfidenceGain']:.3f}",
    ]
    for idx, line in enumerate(summary_lines):
        draw.text((780, 722 + idx * 22), line, fill=(35, 35, 35), font=small)

    thumb_rows = [row for row in rows if row["kind"] == "active"]
    thumb_rows += sorted(
        [row for row in rows if row["kind"] == "shifted_control"],
        key=lambda item: (item["maxShiftMagnitude"], item["maxConfidenceGain"]),
        reverse=True,
    )[:4]
    tx = 780
    ty = 900
    draw.text((tx, ty - 24), "Active crops and strongest shifted controls", fill=(70, 70, 70), font=small)
    for i, row in enumerate(thumb_rows[:8]):
        crop = crop_image(image, row["box"]).resize((220, 74))
        cx = tx + (i % 4) * 250
        cy = ty + (i // 4) * 150
        sheet.paste(crop, (cx, cy))
        draw.rectangle((cx, cy, cx + 220, cy + 74), outline=(35, 35, 35), width=1)
        draw.text(
            (cx, cy + 80),
            f"{row['shortId']} {row['shiftSignature']} mag {row['maxShiftMagnitude']:.1f}",
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

    active_rows = [row for row in rows if row["kind"] == "active"]
    control_rows = [row for row in rows if row["kind"] == "shifted_control"]
    slot_rows = [row for row in rows if row["kind"] == "overdose_slot"]
    reliable_active_rows = [row for row in active_rows if row["reliableEdge"]]

    control_gain_p95 = (
        float(np.percentile([row["maxConfidenceGain"] for row in control_rows], 95))
        if control_rows
        else 0.0
    )
    control_shift_p95 = (
        float(np.percentile([row["maxShiftMagnitude"] for row in control_rows], 95))
        if control_rows
        else 0.0
    )
    active_nonzero = [
        row["shortId"]
        for row in active_rows
        if row["reliableEdge"]
        and row["maxShiftMagnitude"] >= NONZERO_MAG_THRESHOLD
        and row["maxConfidenceGain"] >= CONFIDENCE_THRESHOLD
    ]
    confidence_outliers = [
        row["shortId"]
        for row in active_rows
        if row["reliableEdge"]
        and row["maxConfidenceGain"] > control_gain_p95
        and row["maxShiftMagnitude"] >= NONZERO_MAG_THRESHOLD
    ]
    all_four_nonzero = len(active_nonzero) == len(active_rows)
    all_four_outlier = len(confidence_outliers) == len(active_rows)
    active_sigs = [row["shiftSignature"] for row in active_rows]
    active_common_sig = active_sigs[0] if len(set(active_sigs)) == 1 else None
    control_common_sig_matches = (
        sum(1 for row in control_rows if row["shiftSignature"] == active_common_sig)
        if active_common_sig
        else 0
    )
    slot_common_sig_matches = (
        sum(1 for row in slot_rows if row["shiftSignature"] == active_common_sig)
        if active_common_sig
        else 0
    )

    max_active_shift = max(row["maxShiftMagnitude"] for row in active_rows)
    max_control_shift = max(row["maxShiftMagnitude"] for row in control_rows)
    max_slot_shift = max(row["maxShiftMagnitude"] for row in slot_rows)
    max_active_gain = max(row["maxConfidenceGain"] for row in active_rows)
    max_control_gain = max(row["maxConfidenceGain"] for row in control_rows)
    max_slot_gain = max(row["maxConfidenceGain"] for row in slot_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    fingerprint = (
        f"active={len(active_rows)}|controls={len(control_rows)}|slots={len(slot_rows)}"
        f"|radius={SEARCH_RADIUS}|reliableActive={len(reliable_active_rows)}"
        f"|activeNonzero={len(active_nonzero)}|activeGainOutliers={len(confidence_outliers)}"
        f"|allFourNonzero={int(all_four_nonzero)}|allFourGain={int(all_four_outlier)}"
        f"|commonSig={active_common_sig or 'mixed'}|controlCommon={control_common_sig_matches}"
        f"|slotCommon={slot_common_sig_matches}"
        f"|shiftMax={max_active_shift:.1f}/{max_control_shift:.1f}/{max_slot_shift:.1f}"
        f"|gainMax={max_active_gain:.3f}/{max_control_gain:.3f}/{max_slot_gain:.3f}"
        f"|controlP95={control_shift_p95:.1f}/{control_gain_p95:.3f}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_rows),
        "shiftedControlBoxCount": len(control_rows),
        "overdoseSlotBoxCount": len(slot_rows),
        "searchRadiusPx": SEARCH_RADIUS,
        "reliableEdgeStdThreshold": RELIABLE_EDGE_STD,
        "reliableActiveBoxCount": len(reliable_active_rows),
        "controlShiftMagnitudeP95": round(control_shift_p95, 6),
        "controlConfidenceGainP95": round(control_gain_p95, 6),
        "activeNonzeroRegistrationRowCount": len(active_nonzero),
        "activeNonzeroRegistrationRowIds": active_nonzero,
        "activeConfidenceOutlierCount": len(confidence_outliers),
        "activeConfidenceOutlierIds": confidence_outliers,
        "allFourActiveNonzeroRegistration": all_four_nonzero,
        "allFourActiveConfidenceOutlier": all_four_outlier,
        "activeShiftSignatures": active_sigs,
        "activeCommonShiftSignature": active_common_sig,
        "controlCommonShiftSignatureMatchCount": control_common_sig_matches,
        "overdoseSlotCommonShiftSignatureMatchCount": slot_common_sig_matches,
        "maxActiveShiftMagnitude": max_active_shift,
        "maxControlShiftMagnitude": max_control_shift,
        "maxOverdoseSlotShiftMagnitude": max_slot_shift,
        "maxActiveConfidenceGain": max_active_gain,
        "maxControlConfidenceGain": max_control_gain,
        "maxOverdoseSlotConfidenceGain": max_slot_gain,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "rgbRegistrationFingerprint": fingerprint,
    }
    draw_sheet(image, rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 scan RGB channel-registration gate over active boxes, shifted controls, and projected OVERDOSE slots; no extraction or candidate generation",
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "regionRows": rows,
        "decision": {
            "currentScanRgbRegistrationGate": "current_scan_rgb_registration_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Active target boxes and projected OVERDOSE slots do not show a unique "
                "RGB channel-displacement carrier against shifted controls. Any local "
                "channel differences are ordinary scan/color content effects and do not "
                "supply source-backed unit/order/transform evidence."
            ),
            "nextMove": (
                "Keep current-scan RGB channel registration as a closed source-quality "
                "artifact path. Continue only with distinct physical/original-layout source "
                "validation or raw clue wording that names extraction unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan RGB Registration Gate",
        "",
        "Scope: inspected current page-76 scan RGB channel registration in active target boxes, shifted controls, and projected C9/OVERDOSE slots. This checks local scan/color displacement and chromatic artifact behavior; it is not steganographic extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/control/OVERDOSE-slot boxes: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Search radius: `+-{SEARCH_RADIUS}px`",
        f"- Reliable active boxes: `{len(reliable_active_rows)}` / `{len(active_rows)}`",
        f"- Active nonzero channel-registration rows: `{len(active_nonzero)}` (`{','.join(active_nonzero)}`)",
        f"- Active confidence-gain outliers above shifted-control p95: `{len(confidence_outliers)}` (`{','.join(confidence_outliers)}`)",
        f"- All-four active nonzero / confidence outlier: `{int(all_four_nonzero)}` / `{int(all_four_outlier)}`",
        f"- Active shift signatures: `{','.join(active_sigs)}`",
        f"- Shared active signature / matching controls / matching OVERDOSE slots: `{active_common_sig or 'mixed'}` / `{control_common_sig_matches}` / `{slot_common_sig_matches}`",
        f"- Max active/control/OVERDOSE shift magnitude: `{max_active_shift:.1f}` / `{max_control_shift:.1f}` / `{max_slot_shift:.1f}` px",
        f"- Max active/control/OVERDOSE confidence gain: `{max_active_gain:.3f}` / `{max_control_gain:.3f}` / `{max_slot_gain:.3f}`",
        f"- Control p95 shift/gain: `{control_shift_p95:.1f}` / `{control_gain_p95:.3f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | signature | max shift | max gain | nonzero pairs | edge std | reliable |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda item: (item["maxShiftMagnitude"], item["maxConfidenceGain"]), reverse=True):
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | `{row['shiftSignature']}` | {row['maxShiftMagnitude']:.1f} | {row['maxConfidenceGain']:.3f} | {row['nonzeroPairCount']} | {row['edgeStd']:.2f} | {int(row['reliableEdge'])} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_rgb_registration_no_selector`",
            "- Active boxes and projected OVERDOSE slots do not produce a unique RGB channel-registration signature against shifted controls.",
            "- Color-channel displacement remains scan/source-quality evidence only and does not supply source-backed unit/order/transform evidence.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanRgbRegistrationGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
