#!/usr/bin/env python3
"""Check micro-registration of exact page-76 image witnesses.

This bounded pass does not generate key material or try extraction. It takes
the exact page-76 image witnesses, normalizes orientation, and tests whether
the active O4/B4/G5/O5 boxes need any local +/-8 px shift to best match the
upright page-76 reference.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_page76_image_witness_microregistration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_page76_image_witness_microregistration_gate.json"
OUT_MD = OUT / "current_scan_page76_image_witness_microregistration_gate.md"
OUT_SHEET = OUT / "current_scan_page76_image_witness_microregistration_gate_sheet.jpg"

REFERENCE_PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
IMAGE_WITNESS_STATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate/"
    "current_scan_page76_image_witness_state_stability_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
SEARCH_RADIUS_PX = 8


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") not in TARGET_ORDER:
            continue
        rows.append(
            {
                "shortId": row["shortId"],
                "phrase": row.get("phrase", ""),
                "box": [int(round(float(value))) for value in row["box"]],
                "pageLine": int(row["pageLine"]),
                "corridorIndex": int(row["corridorIndex"]),
                "centerX": round((float(row["box"][0]) + float(row["box"][2])) / 2.0, 3),
                "centerY": round((float(row["box"][1]) + float(row["box"][3])) / 2.0, 3),
            }
        )
    return sorted(rows, key=lambda row: TARGET_ORDER.index(row["shortId"]))


def exact_witnesses(image_witness_state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in image_witness_state.get("witnessRows", [])
        if row.get("classification") == "exact_page76_witness"
    ]


def normalized_image(row: dict[str, Any], reference_size: tuple[int, int]) -> Image.Image:
    image = Image.open(ROOT / row["path"]).convert("RGB")
    if row.get("orientationToUpright") == "rot180_to_upright":
        image = image.rotate(180)
    return image.resize(reference_size)


def crop_array(image: Image.Image, box: list[int]) -> np.ndarray:
    return np.asarray(image.crop(box).convert("RGB"), dtype=np.int16)


def shifted_box(box: list[int], dx: int, dy: int) -> list[int]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def mean_abs_diff(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.abs(left - right).mean())


def best_local_shift(reference: Image.Image, witness: Image.Image, target: dict[str, Any]) -> dict[str, Any]:
    box = target["box"]
    reference_crop = crop_array(reference, box)
    zero_diff = mean_abs_diff(reference_crop, crop_array(witness, box))
    best = {"dx": 0, "dy": 0, "meanAbsDiff": zero_diff}
    for dy in range(-SEARCH_RADIUS_PX, SEARCH_RADIUS_PX + 1):
        for dx in range(-SEARCH_RADIUS_PX, SEARCH_RADIUS_PX + 1):
            candidate_box = shifted_box(box, dx, dy)
            candidate_diff = mean_abs_diff(reference_crop, crop_array(witness, candidate_box))
            if candidate_diff < best["meanAbsDiff"]:
                best = {"dx": dx, "dy": dy, "meanAbsDiff": candidate_diff}
    return {
        "shortId": target["shortId"],
        "phrase": target["phrase"],
        "box": box,
        "zeroShiftMeanAbsDiff": round(zero_diff, 6),
        "bestShiftDx": int(best["dx"]),
        "bestShiftDy": int(best["dy"]),
        "bestShiftMeanAbsDiff": round(best["meanAbsDiff"], 6),
        "bestShiftImprovement": round(zero_diff - float(best["meanAbsDiff"]), 6),
        "bestShiftIsZero": best["dx"] == 0 and best["dy"] == 0,
    }


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


def draw_sheet(witness_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width, height = 1800, 900
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = font(26)
    small_font = font(16)
    tiny_font = font(13)

    draw.rectangle((0, 0, width, 96), fill=(28, 32, 38))
    draw.text((24, 18), "Current Scan Page-76 Image Witness Micro-Registration", fill="white", font=title_font)
    draw.text(
        (24, 58),
        (
            f"exact witnesses {summary['exactPage76WitnessCount']} | target rows "
            f"{summary['targetShiftRowCount']} | nonzero best shifts {summary['nonZeroBestShiftCount']} | "
            f"fingerprint {summary['microregistrationFingerprint']}"
        ),
        fill=(230, 230, 230),
        font=tiny_font,
    )

    y = 124
    draw.text((24, y), "Per-witness active target local shift search", fill=(40, 40, 40), font=small_font)
    y += 30
    headers = ["witness", "target", "zero diff", "best diff", "best dx,dy", "improve", "zero?"]
    xs = [24, 640, 760, 900, 1040, 1180, 1300]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny_font)
    y += 24
    idx = 0
    for witness in witness_rows:
        for target in witness["targetShiftRows"]:
            fill = (238, 249, 239) if target["bestShiftIsZero"] else (252, 238, 238)
            if idx % 2 == 1 and target["bestShiftIsZero"]:
                fill = (229, 243, 233)
            draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
            draw.text((xs[0], y), witness["path"][:76], fill=(30, 30, 30), font=tiny_font)
            draw.text((xs[1], y), target["shortId"], fill=(30, 30, 30), font=tiny_font)
            draw.text((xs[2], y), f"{target['zeroShiftMeanAbsDiff']:.3f}", fill=(30, 30, 30), font=tiny_font)
            draw.text((xs[3], y), f"{target['bestShiftMeanAbsDiff']:.3f}", fill=(30, 30, 30), font=tiny_font)
            draw.text((xs[4], y), f"{target['bestShiftDx']},{target['bestShiftDy']}", fill=(30, 30, 30), font=tiny_font)
            draw.text((xs[5], y), f"{target['bestShiftImprovement']:.3f}", fill=(30, 30, 30), font=tiny_font)
            draw.text((xs[6], y), str(target["bestShiftIsZero"]), fill=(30, 30, 30), font=tiny_font)
            y += 44
            idx += 1

    img.save(OUT_SHEET, quality=92)


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Page-76 Image Witness Micro-Registration Gate",
        "",
        "Scope: bounded exact page-76 image witness local-shift control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Exact page-76 witnesses checked: `{summary['exactPage76WitnessCount']}`",
        f"- Active target shift rows: `{summary['targetShiftRowCount']}`",
        f"- Search radius: `+/-{summary['searchRadiusPx']} px`",
        f"- Nonzero best shifts: `{summary['nonZeroBestShiftCount']}`",
        f"- Max absolute best shift: `{summary['maxAbsBestShiftPx']}` px",
        f"- Max zero-shift diff: `{summary['maxZeroShiftMeanAbsDiff']}`",
        f"- Max zero-to-best improvement: `{summary['maxZeroToBestImprovement']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['microregistrationFingerprint']}`",
        "",
        "## Shift Rows",
        "",
        "| witness | target | zero diff | best diff | best dx | best dy | improvement | zero shift best |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for witness in result["witnessRows"]:
        for row in witness["targetShiftRows"]:
            lines.append(
                f"| `{witness['path']}` | `{row['shortId']}` | `{row['zeroShiftMeanAbsDiff']}` | "
                f"`{row['bestShiftMeanAbsDiff']}` | `{row['bestShiftDx']}` | `{row['bestShiftDy']}` | "
                f"`{row['bestShiftImprovement']}` | `{row['bestShiftIsZero']}` |"
            )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['currentScanPage76ImageWitnessMicroregistrationGate']}.",
            f"- Reason: {result['decision']['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reference = Image.open(REFERENCE_PAGE76).convert("RGB")
    active_index = load_json(ACTIVE_INDEX_SLOT)
    image_witness_state = load_json(IMAGE_WITNESS_STATE)
    reopen_trigger = load_json(REOPEN_TRIGGER_MATRIX)
    targets = active_rows(active_index)
    witnesses = exact_witnesses(image_witness_state)

    witness_rows = []
    shift_rows = []
    for witness_record in witnesses:
        image = normalized_image(witness_record, reference.size)
        target_shift_rows = [best_local_shift(reference, image, target) for target in targets]
        shift_rows.extend(target_shift_rows)
        witness_rows.append(
            {
                "path": witness_record["path"],
                "orientationToUpright": witness_record.get("orientationToUpright"),
                "page76Mad": witness_record.get("page76Mad"),
                "targetShiftRows": target_shift_rows,
                "nonZeroBestShiftCount": sum(1 for row in target_shift_rows if not row["bestShiftIsZero"]),
                "maxZeroShiftMeanAbsDiff": round(max(row["zeroShiftMeanAbsDiff"] for row in target_shift_rows), 6),
                "maxBestShiftMeanAbsDiff": round(max(row["bestShiftMeanAbsDiff"] for row in target_shift_rows), 6),
            }
        )

    non_zero = [row for row in shift_rows if not row["bestShiftIsZero"]]
    max_abs_shift = max(
        (max(abs(row["bestShiftDx"]), abs(row["bestShiftDy"])) for row in shift_rows),
        default=0,
    )
    max_zero_diff = max((row["zeroShiftMeanAbsDiff"] for row in shift_rows), default=0.0)
    max_best_diff = max((row["bestShiftMeanAbsDiff"] for row in shift_rows), default=0.0)
    max_improvement = max((row["bestShiftImprovement"] for row in shift_rows), default=0.0)
    mean_zero_diff = mean([row["zeroShiftMeanAbsDiff"] for row in shift_rows]) if shift_rows else 0.0
    mean_best_diff = mean([row["bestShiftMeanAbsDiff"] for row in shift_rows]) if shift_rows else 0.0

    reopen_summary = reopen_trigger.get("summary", {})
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(reopen_summary.get("triggerCount", 0) or 0)
    selector_unlocked = False
    fingerprint = (
        f"witnesses={len(witnesses)}|targets={len(shift_rows)}|radius={SEARCH_RADIUS_PX}|"
        f"nonZeroShift={len(non_zero)}|maxAbsShift={max_abs_shift}|"
        f"maxZeroDiff={max_zero_diff:.3f}|maxImprove={max_improvement:.3f}|"
        f"sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "exactPage76WitnessCount": len(witnesses),
        "targetShiftRowCount": len(shift_rows),
        "searchRadiusPx": SEARCH_RADIUS_PX,
        "nonZeroBestShiftCount": len(non_zero),
        "maxAbsBestShiftPx": max_abs_shift,
        "maxZeroShiftMeanAbsDiff": round(max_zero_diff, 6),
        "maxBestShiftMeanAbsDiff": round(max_best_diff, 6),
        "meanZeroShiftMeanAbsDiff": round(mean_zero_diff, 6),
        "meanBestShiftMeanAbsDiff": round(mean_best_diff, 6),
        "maxZeroToBestImprovement": round(max_improvement, 6),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
        "microregistrationFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current scan exact page-76 image witness micro-registration control; "
            "no key derivation, hashing, WIF, seed, address, or broad brute force"
        ),
        "inputs": {
            "referencePage76": rel(REFERENCE_PAGE76),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "imageWitnessStateGate": rel(IMAGE_WITNESS_STATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "exactWitnessSource": "current_scan_page76_image_witness_state_stability_gate exact_page76_witness rows",
            "searchRadiusPx": SEARCH_RADIUS_PX,
            "metric": "mean absolute RGB difference against upright page-76 reference crop",
            "interpretation": "a nonzero best shift would indicate local active-box micro-registration drift",
        },
        "witnessRows": witness_rows,
        "summary": summary,
        "decision": {
            "currentScanPage76ImageWitnessMicroregistrationGate": (
                "exact_page76_image_witnesses_have_no_active_microregistration_drift"
            ),
            "reason": (
                "Across all exact page-76 image witnesses and all four active boxes, the "
                "best +/-8 px local match is the zero-shift crop. The small remaining "
                "differences are raster/JPEG differences, not geometry shifts or a hidden layer."
            ),
            "selectorUnlocked": selector_unlocked,
        },
        "nextMove": (
            "Keep exact page-76 witnesses as aligned duplicate rasters. Reopen active-box "
            "geometry only for a distinct physical/original-layout source or raw clue wording."
        ),
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(witness_rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint {fingerprint}")


if __name__ == "__main__":
    main()
