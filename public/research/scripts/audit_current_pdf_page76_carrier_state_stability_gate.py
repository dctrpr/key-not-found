#!/usr/bin/env python3
"""Audit page-76 active/OVERDOSE carrier state stability across current PDFs.

After controlling the B4 duplicate-PDF feature artifact on page 75, this pass
checks whether the duplicate/lower-resolution PDF carriers distort the page-76
active targets or OVERDOSE slot regions relative to the byte-locked
`magazine.pdf` carrier.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from audit_current_pdf_duplicate_background_feature_artifact_gate import load_pdf_page_rows
from audit_current_scan_source_layer_landing_gate import (
    ACTIVE_INDEX_SLOT,
    ROOT,
    active_boxes,
    estimated_line_pitch,
    font,
    load_json,
    load_trigger_summary,
    normalize_page,
    rel,
)


OUT_DIR = ROOT / "analysis_outputs/source_audit/current_pdf_page76_carrier_state_stability_gate"
JSON_OUT = OUT_DIR / "current_pdf_page76_carrier_state_stability_gate.json"
MD_OUT = OUT_DIR / "current_pdf_page76_carrier_state_stability_gate.md"
SHEET_OUT = OUT_DIR / "current_pdf_page76_carrier_state_stability_gate_sheet.jpg"

C9_OVERDOSE_SLOT_GATE = (
    ROOT
    / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json"
)
DUPLICATE_ARTIFACT_GATE = (
    ROOT
    / "analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate/"
    "current_pdf_duplicate_background_feature_artifact_gate.json"
)

PAGE_NO = 76
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
LAYER_ORDER = ["black", "orange", "grey", "feature", "broad"]
PRESENCE_THRESHOLD = 0.05
OUTLIER_PERCENTILE = 0.95


def crop_mask(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def crop_arr(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return arr[y0:y1, x0:x1, :3]


def ratio_metrics(row: dict[str, Any], box: list[float]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for layer in LAYER_ORDER:
        cropped = crop_mask(row["masks"][layer], box)
        metrics[f"{layer}Ratio"] = round(float(cropped.mean()) if cropped.size else 0.0, 6)
    rgb = crop_arr(row["array"], box)
    if rgb.size:
        mean_rgb = rgb.reshape(-1, 3).mean(axis=0)
        metrics["meanRgb"] = [round(float(v), 3) for v in mean_rgb.tolist()]
        metrics["meanLuma"] = round(
            float(0.2126 * mean_rgb[0] + 0.7152 * mean_rgb[1] + 0.0722 * mean_rgb[2]),
            3,
        )
    else:
        metrics["meanRgb"] = None
        metrics["meanLuma"] = None
    metrics["presenceSignature"] = "".join(
        "1" if metrics[f"{layer}Ratio"] >= PRESENCE_THRESHOLD else "0"
        for layer in ("black", "orange", "grey", "feature")
    )
    if metrics["orangeRatio"] >= PRESENCE_THRESHOLD:
        metrics["dominantState"] = "orange"
    elif metrics["blackRatio"] >= PRESENCE_THRESHOLD:
        metrics["dominantState"] = "black"
    elif metrics["greyRatio"] >= PRESENCE_THRESHOLD:
        metrics["dominantState"] = "grey"
    elif metrics["featureRatio"] >= PRESENCE_THRESHOLD:
        metrics["dominantState"] = "feature"
    elif metrics["broadRatio"] >= PRESENCE_THRESHOLD:
        metrics["dominantState"] = "broad"
    else:
        metrics["dominantState"] = "blank"
    return metrics


def mean_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for layer in LAYER_ORDER:
        key = f"{layer}Ratio"
        out[key] = round(float(np.mean([row[key] for row in rows])) if rows else 0.0, 6)
    out["presenceSignature"] = "".join(
        "1" if out[f"{layer}Ratio"] >= PRESENCE_THRESHOLD else "0"
        for layer in ("black", "orange", "grey", "feature")
    )
    states = [row["dominantState"] for row in rows]
    out["dominantState"] = max(set(states), key=states.count) if states else "none"
    return out


def max_layer_delta(left: dict[str, Any], right: dict[str, Any]) -> float:
    return round(
        max(abs(float(left[f"{layer}Ratio"]) - float(right[f"{layer}Ratio"])) for layer in LAYER_ORDER),
        6,
    )


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = (len(ordered) - 1) * pct
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(ordered[lo])
    frac = pos - lo
    return float(ordered[lo] * (1.0 - frac) + ordered[hi] * frac)


def page76_regions() -> list[dict[str, Any]]:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    active = active_boxes(active_index)
    regions: list[dict[str, Any]] = []
    for row in active:
        regions.append(
            {
                "id": row["shortId"],
                "kind": "active_target",
                "label": row["phrase"],
                "expectedState": row["visualState"],
                "box": row["box"],
                "pageLine": row["pageLine"],
            }
        )

    c9 = load_json(C9_OVERDOSE_SLOT_GATE)
    frame = c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    for slot in c9.get("slots", []):
        regions.append(
            {
                "id": f"slot{slot['index']}_{slot['letter']}",
                "kind": "overdose_slot",
                "label": f"OVERDOSE slot {slot['letter']}",
                "expectedState": None,
                "box": [
                    float(slot["left"]),
                    float(frame[1]),
                    float(slot["right"]),
                    float(frame[3]),
                ],
                "pageLine": None,
            }
        )

    pitch = estimated_line_pitch(active)
    for row in active:
        for multiplier in (-2, -1, 1, 2):
            dy = pitch * multiplier
            box = [row["box"][0], row["box"][1] + dy, row["box"][2], row["box"][3] + dy]
            if box[1] < 0 or box[3] > 3264:
                continue
            regions.append(
                {
                    "id": f"{row['shortId']}_ctrl{multiplier:+d}",
                    "kind": "line_shift_control",
                    "label": f"{row['shortId']} shifted {multiplier:+d} line pitch",
                    "expectedState": None,
                    "box": box,
                    "pageLine": None,
                }
            )
    return regions


def draw_sheet(result: dict[str, Any], baseline: Image.Image) -> None:
    sheet = Image.new("RGB", (1920, 1260), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title_f = font(31, True)
    head_f = font(20, True)
    body_f = font(15)
    small_f = font(12)

    summary = result["summary"]
    draw.text((34, 24), "Current PDF Page-76 Carrier State Stability Gate", fill=(15, 23, 42), font=title_f)
    y = 82
    for line in [
        f"Decision: {summary['decision']}",
        f"Active mismatch rows: {summary['activeDuplicatePresenceMismatchRows']} | active outliers over controls: {summary['activeDuplicateOutlierRows']}",
        f"Slot mismatch rows: {summary['slotDuplicatePresenceMismatchRows']} | slot outliers: {summary['slotDuplicateOutlierRows']}",
        f"Control p95 max-layer delta: {summary['controlP95MaxLayerDelta']} | max active/slot delta: {summary['maxActiveDuplicateLayerDelta']}/{summary['maxSlotDuplicateLayerDelta']}",
        f"Source-backed R3 / triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]:
        draw.text((34, y), line, fill=(30, 41, 59), font=body_f)
        y += 26

    preview = baseline.copy()
    preview.thumbnail((820, 1040))
    sheet.paste(preview, (34, 210))
    sx = preview.width / baseline.width
    sy = preview.height / baseline.height
    for region in result["regionSummaries"]:
        if region["kind"] not in {"active_target", "overdose_slot"}:
            continue
        x0, y0, x1, y1 = region["box"]
        if region["kind"] == "active_target":
            color = (220, 38, 38) if region["duplicateOutlier"] else (249, 115, 22)
            width = 3
        else:
            color = (37, 99, 235) if region["duplicateOutlier"] else (96, 165, 250)
            width = 1
        draw.rectangle(
            (34 + x0 * sx, 210 + y0 * sy, 34 + x1 * sx, 210 + y1 * sy),
            outline=color,
            width=width,
        )
    draw.text((34, 178), "Page-76 active targets and OVERDOSE slots", fill=(15, 23, 42), font=head_f)

    table_x = 910
    table_y = 210
    draw.text((table_x, table_y - 32), "Carrier-state deltas", fill=(15, 23, 42), font=head_f)
    headers = ["region", "kind", "mag state", "dup state", "delta", "mismatch"]
    widths = [145, 145, 105, 105, 70, 90]
    x = table_x
    for header, width in zip(headers, widths):
        draw.rectangle((x, table_y, x + width, table_y + 28), fill=(226, 232, 240))
        draw.text((x + 6, table_y + 7), header, fill=(15, 23, 42), font=small_f)
        x += width
    y = table_y + 28
    rows = [row for row in result["regionSummaries"] if row["kind"] in {"active_target", "overdose_slot"}]
    for row in rows[:18]:
        x = table_x
        vals = [
            row["id"],
            row["kind"].replace("_", " "),
            row["magazineConsensus"]["dominantState"],
            row["duplicateConsensus"]["dominantState"],
            f"{row['maxDuplicateLayerDelta']:.3f}",
            str(int(row["presenceMismatch"])),
        ]
        fill = (255, 247, 237) if row["kind"] == "active_target" else (239, 246, 255)
        for val, width in zip(vals, widths):
            draw.rectangle((x, y, x + width, y + 25), fill=fill, outline=(203, 213, 225))
            draw.text((x + 6, y + 6), val[:18], fill=(30, 41, 59), font=small_f)
            x += width
        y += 25

    draw.text((34, 1180), f"Fingerprint: {result['fingerprint']}", fill=(71, 85, 105), font=small_f)
    sheet.save(SHEET_OUT, quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    baseline = normalize_page(PAGE_NO)
    pdf_rows = load_pdf_page_rows(PAGE_NO)
    magazine_rows = [row for row in pdf_rows if row["pdfLabel"] == "magazine.pdf"]
    duplicate_rows = [row for row in pdf_rows if row["pdfLabel"] != "magazine.pdf"]
    regions = page76_regions()

    carrier_rows: list[dict[str, Any]] = []
    region_summaries: list[dict[str, Any]] = []
    for region in regions:
        magazine_metrics = [
            {"pdfLabel": row["pdfLabel"], "kind": row["kind"], **ratio_metrics(row, region["box"])}
            for row in magazine_rows
        ]
        duplicate_metrics = [
            {"pdfLabel": row["pdfLabel"], "kind": row["kind"], **ratio_metrics(row, region["box"])}
            for row in duplicate_rows
        ]
        mag_mean = mean_metrics(magazine_metrics)
        dup_mean = mean_metrics(duplicate_metrics)
        duplicate_deltas = [max_layer_delta(metrics, mag_mean) for metrics in duplicate_metrics]
        presence_mismatch_rows = [
            metrics
            for metrics in duplicate_metrics
            if metrics["presenceSignature"] != mag_mean["presenceSignature"]
        ]
        carrier_rows.extend(
            [
                {
                    "regionId": region["id"],
                    "regionKind": region["kind"],
                    "regionLabel": region["label"],
                    "carrierGroup": "magazine",
                    **metrics,
                }
                for metrics in magazine_metrics
            ]
        )
        carrier_rows.extend(
            [
                {
                    "regionId": region["id"],
                    "regionKind": region["kind"],
                    "regionLabel": region["label"],
                    "carrierGroup": "duplicate",
                    "maxLayerDeltaVsMagazineConsensus": delta,
                    **metrics,
                }
                for metrics, delta in zip(duplicate_metrics, duplicate_deltas)
            ]
        )
        region_summaries.append(
            {
                **region,
                "box": [round(float(v), 3) for v in region["box"]],
                "magazineConsensus": mag_mean,
                "duplicateConsensus": dup_mean,
                "duplicatePresenceMismatchRows": len(presence_mismatch_rows),
                "presenceMismatch": bool(presence_mismatch_rows),
                "maxDuplicateLayerDelta": max(duplicate_deltas) if duplicate_deltas else 0.0,
                "medianDuplicateLayerDelta": round(float(median(duplicate_deltas)) if duplicate_deltas else 0.0, 6),
            }
        )

    control_deltas = [
        row["maxLayerDeltaVsMagazineConsensus"]
        for row in carrier_rows
        if row["regionKind"] == "line_shift_control" and row.get("carrierGroup") == "duplicate"
    ]
    control_p95 = round(percentile(control_deltas, OUTLIER_PERCENTILE), 6)
    for region in region_summaries:
        region["duplicateOutlier"] = bool(
            region["kind"] != "line_shift_control"
            and region["maxDuplicateLayerDelta"] > control_p95
        )

    active_regions = [row for row in region_summaries if row["kind"] == "active_target"]
    slot_regions = [row for row in region_summaries if row["kind"] == "overdose_slot"]
    control_regions = [row for row in region_summaries if row["kind"] == "line_shift_control"]
    active_mismatch_rows = sum(row["duplicatePresenceMismatchRows"] for row in active_regions)
    slot_mismatch_rows = sum(row["duplicatePresenceMismatchRows"] for row in slot_regions)
    active_outliers = sum(1 for row in active_regions if row["duplicateOutlier"])
    slot_outliers = sum(1 for row in slot_regions if row["duplicateOutlier"])
    control_outliers = sum(1 for row in control_regions if row["maxDuplicateLayerDelta"] > control_p95)
    all_four_active_outlier = int(active_outliers == len(active_regions))

    trigger = load_trigger_summary()
    hidden_candidate = bool(
        all_four_active_outlier
        and active_mismatch_rows > 0
        and trigger["sourceBackedR3BridgeHitCount"] > 0
    )
    prior = load_json(DUPLICATE_ARTIFACT_GATE)
    decision = "page76_duplicate_carrier_state_stability_no_selector"
    fingerprint = (
        f"carriers={len(pdf_rows)}|active={len(active_regions)}|slots={len(slot_regions)}"
        f"|controls={len(control_regions)}|activeMismatchRows={active_mismatch_rows}"
        f"|slotMismatchRows={slot_mismatch_rows}|activeOutliers={active_outliers}"
        f"|slotOutliers={slot_outliers}|controlP95={control_p95}"
        f"|all4ActiveOutlier={all_four_active_outlier}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger['satisfiedReopenTriggerCount']}/{trigger['triggerCount']}"
        "|selectors=0"
    )
    summary = {
        "decision": decision,
        "pageNo": PAGE_NO,
        "carrierCount": len(pdf_rows),
        "magazineCarrierCount": len(magazine_rows),
        "duplicateCarrierCount": len(duplicate_rows),
        "activeRegionCount": len(active_regions),
        "overdoseSlotRegionCount": len(slot_regions),
        "lineShiftControlRegionCount": len(control_regions),
        "activeDuplicatePresenceMismatchRows": active_mismatch_rows,
        "slotDuplicatePresenceMismatchRows": slot_mismatch_rows,
        "activeDuplicateOutlierRows": active_outliers,
        "slotDuplicateOutlierRows": slot_outliers,
        "lineShiftControlOutlierRows": control_outliers,
        "allFourActiveOutlier": bool(all_four_active_outlier),
        "controlP95MaxLayerDelta": control_p95,
        "maxActiveDuplicateLayerDelta": round(
            max([row["maxDuplicateLayerDelta"] for row in active_regions] or [0.0]),
            6,
        ),
        "maxSlotDuplicateLayerDelta": round(
            max([row["maxDuplicateLayerDelta"] for row in slot_regions] or [0.0]),
            6,
        ),
        "priorDuplicateBackgroundFeatureArtifactFingerprint": prior.get("summary", {}).get(
            "duplicateBackgroundFeatureArtifactFingerprint"
        ),
        "hiddenPage76DuplicateCarrierCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": trigger["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger["satisfiedReopenTriggerCount"],
        "triggerCount": trigger["triggerCount"],
        "page76CarrierStateStabilityFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current PDF page-76 active target and OVERDOSE carrier-state stability; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9OverdoseSlotGate": rel(C9_OVERDOSE_SLOT_GATE),
            "duplicateArtifactGate": rel(DUPLICATE_ARTIFACT_GATE),
            "presenceThreshold": PRESENCE_THRESHOLD,
            "outlierControlPercentile": OUTLIER_PERCENTILE,
        },
        "summary": summary,
        "regionSummaries": region_summaries,
        "carrierRows": carrier_rows,
        "decision": {
            "currentPdfPage76CarrierStateStabilityGate": decision,
            "selectorUnlocked": False,
            "reason": "Duplicate/lower-resolution carriers do not create an all-four active target state outlier or a source-backed OVERDOSE selector relative to magazine.pdf.",
            "nextMove": "Keep current PDF derivatives as controls only; require distinct physical/original-layout source or source-backed unit/order wording.",
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": fingerprint,
    }
    draw_sheet(result, baseline)
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    active_table = [
        row for row in region_summaries if row["kind"] == "active_target"
    ]
    slot_table = [
        row for row in region_summaries if row["kind"] == "overdose_slot"
    ]
    lines = [
        "# Current PDF Page-76 Carrier State Stability Gate",
        "",
        "Scope: compared byte-locked `magazine.pdf` embedded/render carriers against duplicate/lower-resolution PDF carriers over page-76 active target boxes, OVERDOSE slot boxes, and matched line-shift controls. This checks source/render provenance only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Carriers total / magazine / duplicate: `{summary['carrierCount']}` / `{summary['magazineCarrierCount']}` / `{summary['duplicateCarrierCount']}`",
        f"- Regions active / OVERDOSE slots / controls: `{summary['activeRegionCount']}` / `{summary['overdoseSlotRegionCount']}` / `{summary['lineShiftControlRegionCount']}`",
        f"- Active duplicate presence-mismatch rows: `{summary['activeDuplicatePresenceMismatchRows']}`",
        f"- OVERDOSE slot duplicate presence-mismatch rows: `{summary['slotDuplicatePresenceMismatchRows']}`",
        f"- Active / slot outliers above line-shift control p95: `{summary['activeDuplicateOutlierRows']}` / `{summary['slotDuplicateOutlierRows']}`",
        f"- All-four active outlier: `{int(summary['allFourActiveOutlier'])}`",
        f"- Control p95 max-layer delta: `{summary['controlP95MaxLayerDelta']}`",
        f"- Max active / slot duplicate layer delta: `{summary['maxActiveDuplicateLayerDelta']}` / `{summary['maxSlotDuplicateLayerDelta']}`",
        f"- Hidden page-76 duplicate carrier candidate: `{int(summary['hiddenPage76DuplicateCarrierCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Active Targets",
        "",
        "| id | expected | magazine state | duplicate state | max layer delta | duplicate mismatch rows | outlier |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in active_table:
        lines.append(
            f"| `{row['id']}` | `{row['expectedState']}` | `{row['magazineConsensus']['dominantState']}` | "
            f"`{row['duplicateConsensus']['dominantState']}` | `{row['maxDuplicateLayerDelta']}` | "
            f"`{row['duplicatePresenceMismatchRows']}` | `{int(row['duplicateOutlier'])}` |"
        )
    lines.extend(
        [
            "",
            "## OVERDOSE Slots",
            "",
            "| id | letter | magazine state | duplicate state | max layer delta | duplicate mismatch rows | outlier |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in slot_table:
        lines.append(
            f"| `{row['id']}` | `{row['label'].split()[-1]}` | `{row['magazineConsensus']['dominantState']}` | "
            f"`{row['duplicateConsensus']['dominantState']}` | `{row['maxDuplicateLayerDelta']}` | "
            f"`{row['duplicatePresenceMismatchRows']}` | `{int(row['duplicateOutlier'])}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Duplicate/lower-resolution carriers introduce some state/raster deltas, but they do not create an all-four active target outlier relative to matched line-shift controls.",
            "- OVERDOSE slot deltas also remain source-provenance evidence only; no source-backed unit/order cue is present.",
            "- This keeps duplicate/current-PDF carrier differences closed as selectors.",
            "",
            "## Next Move",
            "",
            "- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {rel(MD_OUT)}")
    print(f"Wrote {rel(JSON_OUT)}")
    print(f"Wrote {rel(SHEET_OUT)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
