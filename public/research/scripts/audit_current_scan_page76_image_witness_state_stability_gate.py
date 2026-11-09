#!/usr/bin/env python3
"""Check page-76 active-box stability across local image witnesses.

This bounded pass does not generate key material or try extraction. It scans
local full-page image witnesses, identifies exact page-76 matches against the
current upright reference, normalizes orientation, then remeasures the exact
O4/B4/G5/O5 boxes for visual-state stability.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_page76_image_witness_state_stability_gate.json"
OUT_MD = OUT / "current_scan_page76_image_witness_state_stability_gate.md"
OUT_SHEET = OUT / "current_scan_page76_image_witness_state_stability_gate_sheet.jpg"

REFERENCE_PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_SLOTS = ROOT / (
    "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_STATE_STREAM = "YKKY"
TARGET_COLOR_STREAM = "OBBO"
TARGET_SLOT_STREAM = "OVED"
PAGE_ASPECT = 2544 / 3264
SAMPLE_SIZE = (318, 408)
EXACT_PAGE76_MAD_THRESHOLD = 1.0
NEAR_PAGE76_MAD_THRESHOLD = 30.0


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def image_candidates() -> list[Path]:
    paths: list[Path] = []
    for pattern in ["*.jpg", "*.jpeg", "*.png"]:
        paths.extend(ROOT.glob(pattern))
    paths.extend((ROOT / "analysis_outputs/source_images").glob("*.jpg"))
    paths.extend((ROOT / "analysis_outputs/3d_article_map").glob("page_*_upright.jpg"))
    unique = sorted({path.resolve() for path in paths})
    return [path for path in unique if path.exists()]


def mean_abs_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return round(float(sum(ImageStat.Stat(diff).mean) / 3.0), 6)


def best_orientation(candidate: Image.Image, reference_sample: Image.Image) -> dict[str, Any]:
    normal = candidate.convert("RGB").resize(SAMPLE_SIZE)
    rotated = candidate.rotate(180).convert("RGB").resize(SAMPLE_SIZE)
    normal_mad = mean_abs_diff(reference_sample, normal)
    rotated_mad = mean_abs_diff(reference_sample, rotated)
    if rotated_mad < normal_mad:
        return {"orientation": "rot180_to_upright", "mad": rotated_mad}
    return {"orientation": "already_upright", "mad": normal_mad}


def normalize_candidate(candidate: Image.Image, orientation: str, size: tuple[int, int]) -> Image.Image:
    image = candidate.rotate(180) if orientation == "rot180_to_upright" else candidate
    return image.convert("RGB").resize(size)


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def slot_for_x(slots: list[dict[str, Any]], x: float) -> dict[str, Any]:
    for slot in slots:
        if float(slot["left"]) <= x < float(slot["right"]):
            return {"index": int(slot["index"]), "letter": str(slot["letter"])}
    nearest = min(
        slots,
        key=lambda slot: min(abs(x - float(slot["left"])), abs(x - float(slot["right"]))),
    )
    return {"index": int(nearest["index"]), "letter": str(nearest["letter"])}


def crop_box(image: Image.Image, box: list[float]) -> Image.Image:
    rounded = [int(round(value)) for value in box]
    return image.crop(rounded)


def crop_metrics(crop: Image.Image, reference_crop: Image.Image) -> dict[str, Any]:
    arr = np.asarray(crop.convert("RGB"), dtype=np.float32)
    ref = np.asarray(reference_crop.convert("RGB"), dtype=np.float32)
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    blue = arr[:, :, 2]
    luma = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    orange_mask = (
        (red > 145)
        & (green > 80)
        & (green < 230)
        & (blue < 170)
        & (red > green + 10)
        & (green > blue + 10)
    )
    dark_mask = luma < 110
    orange_fraction = float(orange_mask.mean())
    dark_fraction = float(dark_mask.mean())
    mean_rgb = arr.reshape(-1, 3).mean(axis=0)
    if orange_fraction >= 0.20:
        observed_state = "Y"
        observed_color = "O"
    elif dark_fraction >= 0.20:
        observed_state = "K"
        observed_color = "B"
    else:
        observed_state = "N"
        observed_color = "N"
    return {
        "orangeFraction": round(orange_fraction, 6),
        "darkFraction": round(dark_fraction, 6),
        "meanRgb": [round(float(value), 3) for value in mean_rgb],
        "meanLuma": round(float(luma.mean()), 6),
        "observedState": observed_state,
        "observedColor": observed_color,
        "meanAbsDiffVsReferenceCrop": round(float(np.abs(arr - ref).mean()), 6),
    }


def active_rows(active_index: dict[str, Any], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") not in TARGET_ORDER:
            continue
        box = [float(value) for value in row["box"]]
        cx, cy = center(box)
        slot = slot_for_x(slots, cx)
        rows.append(
            {
                "shortId": row["shortId"],
                "phrase": row.get("phrase", ""),
                "box": box,
                "centerX": round(cx, 3),
                "centerY": round(cy, 3),
                "expectedState": row.get("visualState"),
                "expectedColor": "O" if row.get("color") == "orange" else "B",
                "slotIndex": slot["index"],
                "slotLetter": slot["letter"],
            }
        )
    return sorted(rows, key=lambda row: TARGET_ORDER.index(row["shortId"]))


def classify_record(record: dict[str, Any]) -> str:
    if record["page76Mad"] <= EXACT_PAGE76_MAD_THRESHOLD:
        return "exact_page76_witness"
    if record["page76Mad"] <= NEAR_PAGE76_MAD_THRESHOLD:
        return "near_page76_control"
    return "not_page76"


def measure_witness(
    path: Path,
    reference: Image.Image,
    reference_sample: Image.Image,
    rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    try:
        image = Image.open(path).convert("RGB")
    except OSError:
        return None
    width, height = image.size
    if min(width, height) < 1000:
        return None
    aspect = width / height
    if abs(aspect - PAGE_ASPECT) > 0.08:
        return None

    orientation = best_orientation(image, reference_sample)
    normalized = normalize_candidate(image, orientation["orientation"], reference.size)
    target_rows = []
    for row in rows:
        crop = crop_box(normalized, row["box"])
        reference_crop = crop_box(reference, row["box"])
        metrics = crop_metrics(crop, reference_crop)
        target_rows.append({**row, **metrics})

    state_stream = "".join(row["observedState"] for row in target_rows)
    color_stream = "".join(row["observedColor"] for row in target_rows)
    slot_stream = "".join(row["slotLetter"] for row in target_rows)
    max_crop_diff = max(row["meanAbsDiffVsReferenceCrop"] for row in target_rows)
    mean_crop_diff = mean(row["meanAbsDiffVsReferenceCrop"] for row in target_rows)
    record = {
        "path": rel(path),
        "size": [width, height],
        "orientationToUpright": orientation["orientation"],
        "page76Mad": orientation["mad"],
        "targetRows": target_rows,
        "stateStream": state_stream,
        "colorStream": color_stream,
        "slotStream": slot_stream,
        "matchesActiveStateStream": state_stream == TARGET_STATE_STREAM,
        "matchesActiveColorStream": color_stream == TARGET_COLOR_STREAM,
        "matchesActiveSlotStream": slot_stream == TARGET_SLOT_STREAM,
        "maxActiveCropMeanAbsDiff": round(max_crop_diff, 6),
        "meanActiveCropMeanAbsDiff": round(mean_crop_diff, 6),
    }
    record["classification"] = classify_record(record)
    record["stableExactActiveWitness"] = (
        record["classification"] == "exact_page76_witness"
        and record["matchesActiveStateStream"]
        and record["matchesActiveColorStream"]
        and record["matchesActiveSlotStream"]
    )
    return record


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


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width, height = 1900, 980
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = font(26)
    small_font = font(16)
    tiny_font = font(13)

    draw.rectangle((0, 0, width, 96), fill=(28, 32, 38))
    draw.text((24, 18), "Current Scan Page-76 Image Witness State Stability", fill="white", font=title_font)
    draw.text(
        (24, 58),
        (
            f"checked {summary['candidateImageCount']} full-page images | exact p76 "
            f"{summary['exactPage76WitnessCount']} | stable exact {summary['stableExactWitnessCount']} | "
            f"fingerprint {summary['page76ImageWitnessStateFingerprint']}"
        ),
        fill=(230, 230, 230),
        font=tiny_font,
    )

    y = 124
    draw.text((24, y), "Best page-76 image witnesses and controls", fill=(40, 40, 40), font=small_font)
    y += 30
    headers = ["path", "class", "orient", "MAD", "state", "color", "slot", "max crop diff"]
    xs = [24, 590, 820, 1030, 1130, 1230, 1330, 1430]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny_font)
    y += 24
    for idx, record in enumerate(records[:18]):
        if record["classification"] == "exact_page76_witness":
            fill = (238, 249, 239)
        elif record["classification"] == "near_page76_control":
            fill = (252, 247, 238)
        else:
            fill = (248, 249, 252) if idx % 2 == 0 else (238, 242, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), record["path"][:70], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[1], y), record["classification"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[2], y), record["orientationToUpright"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[3], y), f"{record['page76Mad']:.3f}", fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[4], y), record["stateStream"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[5], y), record["colorStream"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[6], y), record["slotStream"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[7], y), f"{record['maxActiveCropMeanAbsDiff']:.3f}", fill=(30, 30, 30), font=tiny_font)
        y += 44

    img.save(OUT_SHEET, quality=92)


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Page-76 Image Witness State Stability Gate",
        "",
        "Scope: bounded current-scan/PDF image-witness stability control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Full-page image candidates checked: `{summary['candidateImageCount']}`",
        f"- Exact page-76 witnesses: `{summary['exactPage76WitnessCount']}`",
        f"- Stable exact witnesses: `{summary['stableExactWitnessCount']}`",
        f"- Near page-76 controls: `{summary['nearPage76ControlCount']}`",
        f"- Hidden changed-state witness candidates: `{summary['hiddenChangedStateWitnessCandidateCount']}`",
        f"- Exact witness max active-crop diff: `{summary['exactWitnessMaxActiveCropMeanAbsDiff']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['page76ImageWitnessStateFingerprint']}`",
        "",
        "## Witness Rows",
        "",
        "| path | class | orientation | MAD | state | color | slot | max crop diff |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for record in result["witnessRows"]:
        if record["classification"] == "not_page76" and record["page76Mad"] > 60:
            continue
        lines.append(
            f"| `{record['path']}` | `{record['classification']}` | `{record['orientationToUpright']}` | "
            f"`{record['page76Mad']}` | `{record['stateStream']}` | `{record['colorStream']}` | "
            f"`{record['slotStream']}` | `{record['maxActiveCropMeanAbsDiff']}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['currentScanPage76ImageWitnessStateStabilityGate']}.",
            f"- Reason: {result['decision']['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reference = Image.open(REFERENCE_PAGE76).convert("RGB")
    reference_sample = reference.resize(SAMPLE_SIZE)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9_slots = load_json(C9_SLOTS)
    reopen_trigger = load_json(REOPEN_TRIGGER_MATRIX)
    rows = active_rows(active_index, c9_slots.get("slots", []))

    records = []
    for path in image_candidates():
        record = measure_witness(path, reference, reference_sample, rows)
        if record:
            records.append(record)
    records.sort(key=lambda row: row["page76Mad"])

    exact = [row for row in records if row["classification"] == "exact_page76_witness"]
    near = [row for row in records if row["classification"] == "near_page76_control"]
    stable_exact = [row for row in exact if row["stableExactActiveWitness"]]
    hidden_changed = [row for row in exact if not row["stableExactActiveWitness"]]
    exact_max_diff = max((row["maxActiveCropMeanAbsDiff"] for row in exact), default=0.0)

    reopen_summary = reopen_trigger.get("summary", {})
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(reopen_summary.get("triggerCount", 0) or 0)
    selector_unlocked = False
    exact_paths = ",".join(row["path"] for row in exact)
    fingerprint = (
        f"images={len(records)}|exact={len(exact)}|stableExact={len(stable_exact)}|"
        f"near={len(near)}|hiddenChanged={len(hidden_changed)}|"
        f"exactMaxDiff={exact_max_diff:.3f}|sourceR3={source_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "candidateImageCount": len(records),
        "exactPage76WitnessCount": len(exact),
        "stableExactWitnessCount": len(stable_exact),
        "nearPage76ControlCount": len(near),
        "hiddenChangedStateWitnessCandidateCount": len(hidden_changed),
        "exactPage76WitnessPaths": exact_paths,
        "targetStateStream": TARGET_STATE_STREAM,
        "targetColorStream": TARGET_COLOR_STREAM,
        "targetSlotStream": TARGET_SLOT_STREAM,
        "exactWitnessMaxActiveCropMeanAbsDiff": round(exact_max_diff, 6),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
        "page76ImageWitnessStateFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current scan page-76 image witness state stability control; no key derivation, "
            "hashing, WIF, seed, address, or broad brute force"
        ),
        "inputs": {
            "referencePage76": rel(REFERENCE_PAGE76),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9Slots": rel(C9_SLOTS),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "candidateImages": "root full-page images plus analysis_outputs/source_images and 3d_article_map upright pages",
            "page76Identification": "sample mean absolute difference against upright page 76; normal vs 180-degree rotation",
            "exactPage76Threshold": EXACT_PAGE76_MAD_THRESHOLD,
            "nearControlThreshold": NEAR_PAGE76_MAD_THRESHOLD,
            "stateClassification": "orange fraction >= 0.20 => Y/O; otherwise dark fraction >= 0.20 => K/B",
        },
        "witnessRows": records,
        "summary": summary,
        "decision": {
            "currentScanPage76ImageWitnessStateStabilityGate": (
                "current_page76_image_witnesses_are_stable_raster_duplicates"
            ),
            "reason": (
                "All exact page-76 image witnesses preserve the active YKKY/OBBO/OVED "
                "state and slot streams after orientation normalization. No local image "
                "witness changes active-box state or supplies source-backed R3 wording."
            ),
            "selectorUnlocked": selector_unlocked,
        },
        "nextMove": (
            "Keep exact page-76 image witnesses as duplicate raster validation only; "
            "reopen source review only for a distinct physical/original-layout asset or "
            "raw clue wording that satisfies a source-reopen trigger."
        ),
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(records, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint {fingerprint}")


if __name__ == "__main__":
    main()
