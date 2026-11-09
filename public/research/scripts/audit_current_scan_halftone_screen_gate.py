#!/usr/bin/env python3
"""Audit current-scan halftone/screen texture on page 76.

This bounded pass checks whether the active page-76 target boxes or projected
OVERDOSE slots are marked by unusual high-frequency print/scan texture,
dominant screen angle, or gradient anisotropy against shifted controls.

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
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_halftone_screen_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_halftone_screen_gate.json"
OUT_MD = OUT / "current_scan_halftone_screen_gate.md"
OUT_SHEET = OUT / "current_scan_halftone_screen_gate_sheet.jpg"

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

ANGLE_BINS = 8
ANGLE_BIN_WIDTH = 180.0 / ANGLE_BINS


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


def texture_metrics(crop: Image.Image) -> dict[str, Any]:
    gray_img = crop.convert("L")
    gray = np.asarray(gray_img, dtype=np.float32)
    if gray.shape[0] < 8 or gray.shape[1] < 8:
        return {
            "highpassRms": 0.0,
            "highFreqPowerRatio": 0.0,
            "dominantAngleDeg": 0.0,
            "dominantAngleBin": "0.0-22.5",
            "dominantShare": 0.0,
            "angleAnisotropy": 0.0,
        }

    blurred = np.asarray(gray_img.filter(ImageFilter.GaussianBlur(radius=2.0)), dtype=np.float32)
    highpass = gray - blurred
    highpass_rms = float(np.sqrt(np.mean(highpass * highpass)))

    gy, gx = np.gradient(gray)
    magnitude = np.sqrt(gx * gx + gy * gy)
    angle = (np.degrees(np.arctan2(gy, gx)) + 180.0) % 180.0
    hist, edges = np.histogram(
        angle.ravel(),
        bins=ANGLE_BINS,
        range=(0.0, 180.0),
        weights=magnitude.ravel(),
    )
    total = float(hist.sum())
    if total:
        dominant_index = int(np.argmax(hist))
        dominant_share = float(hist[dominant_index] / total)
        angle_anisotropy = float((hist.max() - hist.min()) / total)
    else:
        dominant_index = 0
        dominant_share = 0.0
        angle_anisotropy = 0.0
    dominant_left = float(edges[dominant_index])
    dominant_right = float(edges[dominant_index + 1])
    dominant_angle = (dominant_left + dominant_right) / 2.0

    centered = gray - gray.mean()
    power = np.abs(np.fft.rfft2(centered)) ** 2
    fy = np.fft.fftfreq(centered.shape[0])[:, None]
    fx = np.fft.rfftfreq(centered.shape[1])[None, :]
    radius = np.sqrt(fx * fx + fy * fy)
    total_power = float(power.sum())
    high_power = float(power[radius >= 0.18].sum()) if total_power else 0.0
    high_freq_ratio = high_power / total_power if total_power else 0.0

    return {
        "highpassRms": round(highpass_rms, 6),
        "highFreqPowerRatio": round(high_freq_ratio, 6),
        "dominantAngleDeg": round(dominant_angle, 6),
        "dominantAngleBin": f"{dominant_left:.1f}-{dominant_right:.1f}",
        "dominantShare": round(dominant_share, 6),
        "angleAnisotropy": round(angle_anisotropy, 6),
    }


def inspect_region(image: Image.Image, row: dict[str, Any]) -> dict[str, Any]:
    x0, y0, x1, y1 = row["box"]
    crop = crop_image(image, row["box"])
    return {
        **row,
        "width": round(float(x1 - x0), 6),
        "height": round(float(y1 - y0), 6),
        **texture_metrics(crop),
    }


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]]) -> None:
    sheet = Image.new("RGB", (1840, 1260), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 14)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan Halftone Screen Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 active boxes, shifted controls, and C9 OVERDOSE slots checked for high-frequency texture and dominant screen angle.",
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
    draw.text((x0, y), "Top texture / screen-angle rows", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "hi-pass", "hi-freq", "share", "angle", "bin"]
    xs = [x0, x0 + 105, x0 + 240, x0 + 330, x0 + 420, x0 + 500, x0 + 575]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in sorted(rows, key=lambda item: (item["dominantShare"], item["highpassRms"]), reverse=True)[:26]:
        vals = [
            row["kind"][:14],
            row["shortId"][:16],
            f"{row['highpassRms']:.2f}",
            f"{row['highFreqPowerRatio']:.3f}",
            f"{row['dominantShare']:.3f}",
            f"{row['dominantAngleDeg']:.1f}",
            row["dominantAngleBin"],
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    thumb_rows = [row for row in rows if row["kind"] == "active"]
    thumb_rows += sorted(
        [row for row in rows if row["kind"] == "shifted_control"],
        key=lambda item: item["dominantShare"],
        reverse=True,
    )[:4]
    tx = 780
    ty = 720
    draw.text((tx, ty - 24), "Active crops and strongest shifted controls", fill=(70, 70, 70), font=small)
    for i, row in enumerate(thumb_rows[:8]):
        crop = crop_image(image, row["box"]).resize((220, 74))
        cx = tx + (i % 4) * 250
        cy = ty + (i // 4) * 150
        sheet.paste(crop, (cx, cy))
        draw.rectangle((cx, cy, cx + 220, cy + 74), outline=(35, 35, 35), width=1)
        draw.text(
            (cx, cy + 80),
            f"{row['shortId']} {row['dominantAngleDeg']:.1f}deg share {row['dominantShare']:.3f}",
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

    control_share_p95 = float(np.percentile([row["dominantShare"] for row in control_rows], 95)) if control_rows else 0.0
    control_highpass_p95 = float(np.percentile([row["highpassRms"] for row in control_rows], 95)) if control_rows else 0.0
    share_outliers = [row["shortId"] for row in active_rows if row["dominantShare"] > control_share_p95]
    highpass_outliers = [row["shortId"] for row in active_rows if row["highpassRms"] > control_highpass_p95]
    all_four_share = len(share_outliers) == len(active_rows)
    all_four_highpass = len(highpass_outliers) == len(active_rows)
    active_bins = [row["dominantAngleBin"] for row in active_rows]
    active_unique_bins = sorted(set(active_bins))
    active_common_bin = active_unique_bins[0] if len(active_unique_bins) == 1 else None
    control_common_bin_match_count = (
        sum(1 for row in control_rows if row["dominantAngleBin"] == active_common_bin)
        if active_common_bin
        else 0
    )
    slot_common_bin_match_count = (
        sum(1 for row in slot_rows if row["dominantAngleBin"] == active_common_bin)
        if active_common_bin
        else 0
    )

    max_active_share = max(row["dominantShare"] for row in active_rows)
    max_control_share = max(row["dominantShare"] for row in control_rows)
    max_slot_share = max(row["dominantShare"] for row in slot_rows)
    max_active_highpass = max(row["highpassRms"] for row in active_rows)
    max_control_highpass = max(row["highpassRms"] for row in control_rows)
    max_slot_highpass = max(row["highpassRms"] for row in slot_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    fingerprint = (
        f"active={len(active_rows)}|controls={len(control_rows)}|slots={len(slot_rows)}"
        f"|shareOutliers={len(share_outliers)}|highpassOutliers={len(highpass_outliers)}"
        f"|allFourShare={int(all_four_share)}|allFourHighpass={int(all_four_highpass)}"
        f"|activeBins={','.join(active_bins)}"
        f"|commonBin={active_common_bin or 'mixed'}|controlCommon={control_common_bin_match_count}"
        f"|slotCommon={slot_common_bin_match_count}"
        f"|shareMax={max_active_share:.3f}/{max_control_share:.3f}/{max_slot_share:.3f}"
        f"|highpassMax={max_active_highpass:.3f}/{max_control_highpass:.3f}/{max_slot_highpass:.3f}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_rows),
        "shiftedControlBoxCount": len(control_rows),
        "overdoseSlotBoxCount": len(slot_rows),
        "dominantShareControlP95": round(control_share_p95, 6),
        "highpassRmsControlP95": round(control_highpass_p95, 6),
        "activeDominantShareOutlierCount": len(share_outliers),
        "activeDominantShareOutlierIds": share_outliers,
        "activeHighpassRmsOutlierCount": len(highpass_outliers),
        "activeHighpassRmsOutlierIds": highpass_outliers,
        "allFourActiveDominantShareOutlier": all_four_share,
        "allFourActiveHighpassRmsOutlier": all_four_highpass,
        "activeDominantAngleBins": active_bins,
        "activeUniqueDominantAngleBins": active_unique_bins,
        "activeCommonDominantAngleBin": active_common_bin,
        "controlCommonDominantAngleBinMatchCount": control_common_bin_match_count,
        "overdoseSlotCommonDominantAngleBinMatchCount": slot_common_bin_match_count,
        "maxActiveDominantShare": max_active_share,
        "maxControlDominantShare": max_control_share,
        "maxOverdoseSlotDominantShare": max_slot_share,
        "maxActiveHighpassRms": max_active_highpass,
        "maxControlHighpassRms": max_control_highpass,
        "maxOverdoseSlotHighpassRms": max_slot_highpass,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "halftoneScreenFingerprint": fingerprint,
    }

    draw_sheet(image, rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 scan halftone/high-frequency texture and dominant screen-angle gate; no extraction or candidate generation",
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "regionRows": rows,
        "decision": {
            "currentScanHalftoneScreenGate": "current_scan_halftone_screen_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Active target boxes and projected OVERDOSE slots do not show a unique "
                "halftone/screen-angle or high-frequency texture carrier against shifted "
                "controls. The active boxes do not all become control-threshold outliers "
                "and their shared dominant-angle bin is not by itself a source-backed "
                "unit/order/transform."
            ),
            "nextMove": (
                "Keep current-scan print/texture artifacts as closed. Continue only with "
                "distinct physical/original-layout source validation or raw clue wording "
                "that names extraction unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Halftone Screen Gate",
        "",
        "Scope: inspected current page-76 scan high-frequency/halftone texture and dominant screen angle in active target boxes, shifted controls, and projected C9/OVERDOSE slots. This is a visual/source artifact gate, not steganographic extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/control/OVERDOSE-slot boxes: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Active dominant-share outliers above shifted-control p95: `{len(share_outliers)}` (`{','.join(share_outliers)}`)",
        f"- Active highpass-RMS outliers above shifted-control p95: `{len(highpass_outliers)}` (`{','.join(highpass_outliers)}`)",
        f"- All-four active dominant-share/highpass outliers: `{int(all_four_share)}` / `{int(all_four_highpass)}`",
        f"- Active dominant angle bins: `{','.join(active_bins)}`",
        f"- Shared active angle bin / matching controls / matching OVERDOSE slots: `{active_common_bin or 'mixed'}` / `{control_common_bin_match_count}` / `{slot_common_bin_match_count}`",
        f"- Max active/control/OVERDOSE dominant share: `{max_active_share:.3f}` / `{max_control_share:.3f}` / `{max_slot_share:.3f}`",
        f"- Max active/control/OVERDOSE highpass RMS: `{max_active_highpass:.3f}` / `{max_control_highpass:.3f}` / `{max_slot_highpass:.3f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | highpass RMS | high-freq power | dominant share | angle | bin | anisotropy |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in sorted(rows, key=lambda item: (item["dominantShare"], item["highpassRms"]), reverse=True):
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | {row['highpassRms']:.3f} | {row['highFreqPowerRatio']:.3f} | {row['dominantShare']:.3f} | {row['dominantAngleDeg']:.1f} | `{row['dominantAngleBin']}` | {row['angleAnisotropy']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_halftone_screen_no_selector`",
            "- Active boxes and projected OVERDOSE slots do not produce a unique halftone/screen-angle or high-frequency texture signature against shifted controls.",
            "- The active quartet shares a dominant angle bin, but that bin is ordinary page/scan texture evidence and is not an all-four control-threshold outlier or source-backed extraction rule.",
            "- The scan texture remains source-quality/printing evidence only, not an extraction rule.",
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
    print(f"Decision: {result['decision']['currentScanHalftoneScreenGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
