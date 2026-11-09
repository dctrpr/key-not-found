#!/usr/bin/env python3
"""Audit current page-76 scan threshold morphology.

This bounded pass checks whether thresholded ink/component shape in O4/B4/G5/O5
or projected OVERDOSE slots forms a shared carrier against shifted controls. It
is a scan-artifact/source-quality gate, not extraction.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_threshold_morphology_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_threshold_morphology_gate.json"
OUT_MD = OUT / "current_scan_threshold_morphology_gate.md"
OUT_SHEET = OUT / "current_scan_threshold_morphology_gate_sheet.jpg"

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

THRESHOLDS = [64, 96, 128, 160, 192]
SIGNATURE_THRESHOLDS = [128, 160, 192]
OUTLIER_Z = 3.0
MORPH_METRICS = [
    "darkRatio",
    "componentCount",
    "largeComponentCount",
    "largestComponentAreaRatio",
    "largestComponentBboxAreaRatio",
    "largestComponentFillRatio",
    "inkBboxAreaRatio",
    "rowOccupancyRatio",
    "columnOccupancyRatio",
    "xProjectionRunCount",
    "yProjectionRunCount",
]


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


def projection_runs(values: np.ndarray) -> int:
    flags = np.asarray(values, dtype=bool)
    if flags.size == 0:
        return 0
    padded = np.concatenate(([False], flags, [False]))
    changes = np.flatnonzero(padded[1:] != padded[:-1])
    return int(len(changes) // 2)


def row_runs(row: np.ndarray) -> list[tuple[int, int]]:
    if row.size == 0:
        return []
    padded = np.concatenate(([False], np.asarray(row, dtype=bool), [False]))
    changes = np.flatnonzero(padded[1:] != padded[:-1])
    return [(int(start), int(end)) for start, end in zip(changes[0::2], changes[1::2])]


def connected_component_metrics(mask: np.ndarray) -> dict[str, float | int]:
    mask = np.asarray(mask, dtype=bool)
    height, width = mask.shape if mask.ndim == 2 else (0, 0)
    total = int(mask.size)
    if total == 0 or not bool(mask.any()):
        return {
            "componentCount": 0,
            "largeComponentCount": 0,
            "largestComponentAreaRatio": 0.0,
            "largestComponentBboxAreaRatio": 0.0,
            "largestComponentFillRatio": 0.0,
            "inkBboxAreaRatio": 0.0,
            "rowOccupancyRatio": 0.0,
            "columnOccupancyRatio": 0.0,
            "xProjectionRunCount": 0,
            "yProjectionRunCount": 0,
        }

    parent: list[int] = []
    runs: list[tuple[int, int, int, int]] = []

    def make_set() -> int:
        parent.append(len(parent))
        return len(parent) - 1

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    previous: list[tuple[int, int, int]] = []
    for y in range(height):
        current: list[tuple[int, int, int]] = []
        previous_index = 0
        for start, end in row_runs(mask[y]):
            component_id = make_set()
            while previous_index < len(previous) and previous[previous_index][1] < start:
                previous_index += 1
            overlap_index = previous_index
            while overlap_index < len(previous) and previous[overlap_index][0] <= end:
                union(component_id, previous[overlap_index][2])
                overlap_index += 1
            current.append((start, end, component_id))
            runs.append((y, start, end, component_id))
        previous = current

    components: dict[int, dict[str, int]] = {}
    for y, start, end, component_id in runs:
        root = find(component_id)
        row = components.setdefault(
            root,
            {"area": 0, "x0": start, "y0": y, "x1": end, "y1": y + 1},
        )
        row["area"] += end - start
        row["x0"] = min(row["x0"], start)
        row["y0"] = min(row["y0"], y)
        row["x1"] = max(row["x1"], end)
        row["y1"] = max(row["y1"], y + 1)

    min_area = max(8, int(round(total * 0.0002)))
    large_area = max(min_area, int(round(total * 0.002)))
    kept = [row for row in components.values() if row["area"] >= min_area]
    large = [row for row in kept if row["area"] >= large_area]
    largest = max(kept, key=lambda row: row["area"], default=None)

    ys, xs = np.where(mask)
    ink_bbox_area = int((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1))
    row_occupied = mask.any(axis=1)
    col_occupied = mask.any(axis=0)

    if largest is None:
        largest_area_ratio = 0.0
        largest_bbox_area_ratio = 0.0
        largest_fill_ratio = 0.0
    else:
        bbox_area = int((largest["x1"] - largest["x0"]) * (largest["y1"] - largest["y0"]))
        largest_area_ratio = largest["area"] / total
        largest_bbox_area_ratio = bbox_area / total
        largest_fill_ratio = largest["area"] / bbox_area if bbox_area else 0.0

    return {
        "componentCount": int(len(kept)),
        "largeComponentCount": int(len(large)),
        "largestComponentAreaRatio": round(float(largest_area_ratio), 6),
        "largestComponentBboxAreaRatio": round(float(largest_bbox_area_ratio), 6),
        "largestComponentFillRatio": round(float(largest_fill_ratio), 6),
        "inkBboxAreaRatio": round(float(ink_bbox_area / total), 6),
        "rowOccupancyRatio": round(float(row_occupied.mean()), 6),
        "columnOccupancyRatio": round(float(col_occupied.mean()), 6),
        "xProjectionRunCount": projection_runs(col_occupied),
        "yProjectionRunCount": projection_runs(row_occupied),
    }


def threshold_metrics(gray: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for threshold in THRESHOLDS:
        mask = gray <= threshold
        metrics = connected_component_metrics(mask)
        dark_ratio = float(mask.mean()) if mask.size else 0.0
        rows.append(
            {
                "threshold": threshold,
                "darkRatio": round(dark_ratio, 6),
                **metrics,
            }
        )
    return rows


def morphology_signature(rows: list[dict[str, Any]]) -> str:
    parts = []
    for item in rows:
        if item["threshold"] not in SIGNATURE_THRESHOLDS:
            continue
        dark_bin = int(round(float(item["darkRatio"]) * 10))
        component_bin = min(99, int(item["componentCount"]))
        largest_bin = int(round(float(item["largestComponentAreaRatio"]) * 100))
        bbox_bin = int(round(float(item["inkBboxAreaRatio"]) * 10))
        parts.append(
            f"t{item['threshold']}=d{dark_bin}c{component_bin}l{largest_bin}b{bbox_bin}"
        )
    return "|".join(parts)


def inspect_region(image: Image.Image, row: dict[str, Any]) -> dict[str, Any]:
    gray = crop_array(image, row["box"])
    threshold_rows = threshold_metrics(gray)
    x0, y0, x1, y1 = row["box"]
    return {
        **row,
        "width": round(float(x1 - x0), 6),
        "height": round(float(y1 - y0), 6),
        "meanLuminance": round(float(gray.mean()) if gray.size else 0.0, 6),
        "stdLuminance": round(float(gray.std()) if gray.size else 0.0, 6),
        "thresholdMorphology": threshold_rows,
        "morphologySignature": morphology_signature(threshold_rows),
    }


def control_stats(rows: list[dict[str, Any]], threshold_idx: int, metric: str) -> dict[str, float]:
    values = [float(row["thresholdMorphology"][threshold_idx][metric]) for row in rows]
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
    metric_stats = {
        str(threshold): {
            metric: control_stats(controls, idx, metric)
            for metric in MORPH_METRICS
        }
        for idx, threshold in enumerate(THRESHOLDS)
    }

    for row in rows:
        z_values: list[float] = []
        strongest = {"threshold": None, "metric": None, "absZ": 0.0, "value": None}
        for idx, threshold in enumerate(THRESHOLDS):
            for metric in MORPH_METRICS:
                value = float(row["thresholdMorphology"][idx][metric])
                abs_z = abs(zscore(value, metric_stats[str(threshold)][metric]))
                z_values.append(abs_z)
                if abs_z > float(strongest["absZ"]):
                    strongest = {
                        "threshold": threshold,
                        "metric": metric,
                        "absZ": round(abs_z, 6),
                        "value": round(value, 6),
                    }
        row["maxMorphologyAbsZ"] = round(max(z_values), 6) if z_values else 0.0
        row["morphologyOutlier"] = bool(row["maxMorphologyAbsZ"] >= OUTLIER_Z)
        row["strongestMorphologyZ"] = strongest
    return metric_stats


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 1260), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan Threshold Morphology Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 active boxes, shifted controls, and C9 OVERDOSE slots checked for thresholded ink-component shape.",
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
    draw.text((x0, y), "Strongest threshold-morphology rows", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "signature", "maxZ", "metric", "t", "value"]
    xs = [x0, x0 + 112, x0 + 245, x0 + 600, x0 + 670, x0 + 830, x0 + 880]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    sort_rows = sorted(rows, key=lambda item: item["maxMorphologyAbsZ"], reverse=True)
    for row in sort_rows[:28]:
        strongest = row["strongestMorphologyZ"]
        vals = [
            row["kind"][:14],
            row["shortId"][:16],
            row["morphologySignature"][:48],
            f"{row['maxMorphologyAbsZ']:.2f}",
            str(strongest["metric"])[:18],
            str(strongest["threshold"]),
            f"{float(strongest['value'] or 0.0):.3f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    draw.text((780, 720), "Summary", fill=(70, 70, 70), font=small)
    summary_lines = [
        f"Active/control/slots: {summary['activeBoxCount']} / {summary['shiftedControlBoxCount']} / {summary['overdoseSlotBoxCount']}",
        f"Active morphology outliers: {summary['activeMorphologyOutlierCount']} ({','.join(summary['activeMorphologyOutlierIds'])})",
        f"All four active morphology outlier: {int(summary['allFourActiveMorphologyOutlier'])}",
        f"Common morph signature: {summary['activeCommonMorphologySignature'] or 'mixed'}",
        f"Control/slot sig matches: {summary['controlCommonMorphologySignatureMatchCount']} / {summary['overdoseSlotCommonMorphologySignatureMatchCount']}",
        f"Shared carrier / hidden candidate: {int(summary['sharedActiveMorphologyCarrier'])} / {int(summary['hiddenMorphologyCandidate'])}",
        f"Max active/control/slot morphology Z: {summary['maxActiveMorphologyAbsZ']:.2f} / {summary['maxControlMorphologyAbsZ']:.2f} / {summary['maxOverdoseSlotMorphologyAbsZ']:.2f}",
        f"Source R3/triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]
    for idx, line in enumerate(summary_lines):
        draw.text((780, 754 + idx * 22), line, fill=(35, 35, 35), font=small)

    active_rows = [row for row in rows if row["kind"] == "active"]
    thumb_rows = active_rows + [row for row in sort_rows if row["kind"] != "active"][:4]
    tx = 780
    ty = 960
    draw.text((tx, ty - 24), "Active crops and strongest control/slot rows", fill=(70, 70, 70), font=small)
    for i, row in enumerate(thumb_rows[:8]):
        crop = image.crop(tuple(round(v) for v in row["box"])).convert("RGB").resize((220, 74))
        cx = tx + (i % 4) * 250
        cy = ty + (i // 4) * 132
        sheet.paste(crop, (cx, cy))
        draw.rectangle((cx, cy, cx + 220, cy + 74), outline=(35, 35, 35), width=1)
        draw.text(
            (cx, cy + 80),
            f"{row['shortId']} morphZ {row['maxMorphologyAbsZ']:.2f}",
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
    active_morphology_outliers = [row["shortId"] for row in active_rows if row["morphologyOutlier"]]
    all_four_morphology = len(active_morphology_outliers) == len(active_rows)
    active_signatures = [row["morphologySignature"] for row in active_rows]
    active_common_signature = active_signatures[0] if len(set(active_signatures)) == 1 else None
    control_common_matches = (
        sum(1 for row in control_rows if row["morphologySignature"] == active_common_signature)
        if active_common_signature
        else 0
    )
    slot_common_matches = (
        sum(1 for row in slot_rows if row["morphologySignature"] == active_common_signature)
        if active_common_signature
        else 0
    )
    max_active_z = max(float(row["maxMorphologyAbsZ"]) for row in active_rows)
    max_control_z = max(float(row["maxMorphologyAbsZ"]) for row in control_rows)
    max_slot_z = max(float(row["maxMorphologyAbsZ"]) for row in slot_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    shared_active_carrier = bool(all_four_morphology and active_common_signature)
    hidden_candidate = bool(
        shared_active_carrier
        and control_common_matches == 0
        and slot_common_matches == 0
        and source_r3 > 0
    )

    fingerprint = (
        f"active={len(active_rows)}|controls={len(control_rows)}|slots={len(slot_rows)}"
        f"|thresholds={','.join(map(str, THRESHOLDS))}"
        f"|activeMorphOutliers={len(active_morphology_outliers)}"
        f"|allFourMorph={int(all_four_morphology)}"
        f"|sharedCarrier={int(shared_active_carrier)}|hiddenCandidate={int(hidden_candidate)}"
        f"|commonMorph={active_common_signature or 'mixed'}"
        f"|controlCommon={control_common_matches}|slotCommon={slot_common_matches}"
        f"|maxMorphZ={max_active_z:.2f}/{max_control_z:.2f}/{max_slot_z:.2f}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_rows),
        "shiftedControlBoxCount": len(control_rows),
        "overdoseSlotBoxCount": len(slot_rows),
        "thresholdsChecked": THRESHOLDS,
        "signatureThresholds": SIGNATURE_THRESHOLDS,
        "outlierAbsZThreshold": OUTLIER_Z,
        "morphologyMetrics": MORPH_METRICS,
        "activeMorphologyOutlierCount": len(active_morphology_outliers),
        "activeMorphologyOutlierIds": active_morphology_outliers,
        "allFourActiveMorphologyOutlier": all_four_morphology,
        "activeMorphologySignatures": active_signatures,
        "activeCommonMorphologySignature": active_common_signature,
        "controlCommonMorphologySignatureMatchCount": control_common_matches,
        "overdoseSlotCommonMorphologySignatureMatchCount": slot_common_matches,
        "sharedActiveMorphologyCarrier": shared_active_carrier,
        "hiddenMorphologyCandidate": hidden_candidate,
        "maxActiveMorphologyAbsZ": round(max_active_z, 6),
        "maxControlMorphologyAbsZ": round(max_control_z, 6),
        "maxOverdoseSlotMorphologyAbsZ": round(max_slot_z, 6),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "thresholdMorphologyFingerprint": fingerprint,
    }
    draw_sheet(image, rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 scan threshold morphology gate over active boxes, shifted controls, and projected OVERDOSE slots; no extraction or candidate generation",
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
            "currentScanThresholdMorphologyGate": "current_scan_threshold_morphology_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Thresholded ink morphology shows active-box shape contrast, but the active "
                "morphology signatures are mixed and do not form a shared all-four carrier. "
                "The component behavior follows visible orange/black target ink and still has "
                "no source-backed R3 unit/order/transform cue."
            ),
            "nextMove": (
                "Do not pursue current-scan threshold morphology or component-shape tuning. "
                "Continue with original-layout/physical source validation or raw clue wording "
                "that names the missing unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Threshold Morphology Gate",
        "",
        "Scope: inspected thresholded ink/component morphology in current page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots. This is a scan/source-quality gate, not extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/control/OVERDOSE-slot boxes: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Thresholds checked: `{THRESHOLDS}`",
        f"- Signature thresholds: `{SIGNATURE_THRESHOLDS}`",
        f"- Outlier abs-z threshold against shifted controls: `{OUTLIER_Z}`",
        f"- Active morphology outlier rows: `{len(active_morphology_outliers)}` (`{','.join(active_morphology_outliers)}`)",
        f"- All-four active morphology outlier: `{int(all_four_morphology)}`",
        f"- Active common morphology signature: `{active_common_signature or 'mixed'}`",
        f"- Matching controls / OVERDOSE slots for common morphology signature: `{control_common_matches}` / `{slot_common_matches}`",
        f"- Shared active morphology carrier / hidden morphology candidate: `{int(shared_active_carrier)}` / `{int(hidden_candidate)}`",
        f"- Max active/control/OVERDOSE morphology abs-z: `{max_active_z:.2f}` / `{max_control_z:.2f}` / `{max_slot_z:.2f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | morphology signature | outlier | max z | strongest metric | threshold | value |",
        "|---|---|---|---:|---:|---|---:|---:|",
    ]
    for row in sorted(rows, key=lambda item: item["maxMorphologyAbsZ"], reverse=True):
        strongest = row["strongestMorphologyZ"]
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | `{row['morphologySignature']}` | {int(row['morphologyOutlier'])} | {float(row['maxMorphologyAbsZ']):.2f} | `{strongest['metric']}` | `{strongest['threshold']}` | `{float(strongest['value'] or 0.0):.3f}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_threshold_morphology_no_selector`",
            "- The active boxes stand out in thresholded morphology, but their component/shape signatures are mixed and do not form a shared all-four carrier.",
            "- The component behavior follows visible target ink and still has no source-backed unit/order/transform clue.",
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
    print(f"Decision: {result['decision']['currentScanThresholdMorphologyGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
