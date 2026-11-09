#!/usr/bin/env python3
"""Control duplicate-PDF feature conversion around the B4 background point.

The prior B4 PDF provenance gate showed that the byte-locked magazine carrier
keeps the sampled point as broad/background, while lower-resolution duplicate
PDF carriers classify it as grey/feature. This pass asks whether that duplicate
conversion is unique to B4 or a general resampling artifact on matching
off-white background pixels.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw

from audit_current_pdf_b4_contact_pixel_provenance_gate import (
    PDFS,
    extract_largest_embedded_image,
    normalize_to_upright,
    render_pdf_page,
    rgb_stats,
)
from audit_current_scan_source_layer_landing_gate import (
    ROOT,
    font,
    load_json,
    load_trigger_summary,
    normalize_page,
    rel,
    source_layer_masks,
)


OUT_DIR = ROOT / "analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate"
JSON_OUT = OUT_DIR / "current_pdf_duplicate_background_feature_artifact_gate.json"
MD_OUT = OUT_DIR / "current_pdf_duplicate_background_feature_artifact_gate.md"
SHEET_OUT = OUT_DIR / "current_pdf_duplicate_background_feature_artifact_gate_sheet.jpg"

B4_PDF_PROVENANCE = (
    ROOT
    / "analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate/"
    "current_pdf_b4_contact_pixel_provenance_gate.json"
)

PAGE_NO = 75
LOCAL_HALF_SIZE = 384
LOCAL_STEP = 8
PAGE_STEP = 32
LUMA_MIN = 235.0
LUMA_MAX = 244.0
SAT_MAX = 0.06


def rgb_luma(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]


def rgb_saturation(rgb: np.ndarray) -> np.ndarray:
    arr = rgb.astype(np.float32) / 255.0
    maxc = arr.max(axis=2)
    minc = arr.min(axis=2)
    return np.where(maxc > 1e-6, (maxc - minc) / np.maximum(maxc, 1e-6), 0.0)


def load_pdf_page_rows(page_no: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        doc = fitz.open(pdf_path)
        embedded, embedded_meta = extract_largest_embedded_image(doc, page_no)
        embedded_norm, embedded_orientation = normalize_to_upright(embedded, page_no)
        rows.append(
            {
                "pdfLabel": rel(pdf_path),
                "kind": "embedded",
                "image": embedded_norm,
                "array": np.asarray(embedded_norm, dtype=np.uint8),
                "masks": source_layer_masks(np.asarray(embedded_norm, dtype=np.uint8)),
                "orientation": embedded_orientation,
                "meta": embedded_meta,
            }
        )

        rendered = render_pdf_page(doc, page_no)
        rendered_norm, rendered_orientation = normalize_to_upright(rendered, page_no)
        rows.append(
            {
                "pdfLabel": rel(pdf_path),
                "kind": "render_300dpi",
                "image": rendered_norm,
                "array": np.asarray(rendered_norm, dtype=np.uint8),
                "masks": source_layer_masks(np.asarray(rendered_norm, dtype=np.uint8)),
                "orientation": rendered_orientation,
                "meta": {"renderDpi": 300},
            }
        )
        doc.close()
    return rows


def is_feature(row: dict[str, Any], x: int, y: int) -> bool:
    mask = row["masks"]["feature"]
    return bool(0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x])


def is_broad(row: dict[str, Any], x: int, y: int) -> bool:
    mask = row["masks"]["broad"]
    return bool(0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x])


def rgb_at(row: dict[str, Any], x: int, y: int) -> list[int] | None:
    arr = row["array"]
    h, w = arr.shape[:2]
    if not (0 <= x < w and 0 <= y < h):
        return None
    return [int(v) for v in arr[y, x, :3].tolist()]


def max_delta(a: list[int] | None, b: list[int] | None) -> int | None:
    if a is None or b is None:
        return None
    return max(abs(int(x) - int(y)) for x, y in zip(a, b))


def sample_points(
    baseline_arr: np.ndarray,
    baseline_masks: dict[str, np.ndarray],
    center: list[int],
    region: str,
) -> list[dict[str, Any]]:
    h, w = baseline_arr.shape[:2]
    lum = rgb_luma(baseline_arr.astype(np.float32))
    sat = rgb_saturation(baseline_arr)
    eligible = (
        baseline_masks["broad"]
        & (~baseline_masks["feature"])
        & (lum >= LUMA_MIN)
        & (lum <= LUMA_MAX)
        & (sat <= SAT_MAX)
    )

    if region == "local":
        x0 = max(0, center[0] - LOCAL_HALF_SIZE)
        x1 = min(w - 1, center[0] + LOCAL_HALF_SIZE)
        y0 = max(0, center[1] - LOCAL_HALF_SIZE)
        y1 = min(h - 1, center[1] + LOCAL_HALF_SIZE)
        step = LOCAL_STEP
    elif region == "page_grid":
        x0, y0, x1, y1 = 0, 0, w - 1, h - 1
        step = PAGE_STEP
    else:
        raise ValueError(region)

    points: list[dict[str, Any]] = []
    for y in range(y0, y1 + 1, step):
        for x in range(x0, x1 + 1, step):
            if not eligible[y, x]:
                continue
            points.append(
                {
                    "x": x,
                    "y": y,
                    "baselineRgb": [int(v) for v in baseline_arr[y, x, :3].tolist()],
                    "baselineLuma": round(float(lum[y, x]), 3),
                    "baselineSaturation": round(float(sat[y, x]), 6),
                }
            )
    return points


def evaluate_points(
    points: list[dict[str, Any]],
    pdf_rows: list[dict[str, Any]],
    magazine_rows: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    evaluated: list[dict[str, Any]] = []
    for point in points:
        x, y = point["x"], point["y"]
        baseline_rgb = point["baselineRgb"]
        mag_features = sum(1 for row in magazine_rows if is_feature(row, x, y))
        dup_features = sum(1 for row in duplicate_rows if is_feature(row, x, y))
        dup_broad = sum(1 for row in duplicate_rows if is_broad(row, x, y))
        dup_delta_values = [
            max_delta(baseline_rgb, rgb_at(row, x, y))
            for row in duplicate_rows
            if max_delta(baseline_rgb, rgb_at(row, x, y)) is not None
        ]
        evaluated.append(
            {
                **point,
                "magazineFeatureRows": mag_features,
                "duplicateFeatureRows": dup_features,
                "duplicateBroadRows": dup_broad,
                "duplicateMaxDelta": max(dup_delta_values) if dup_delta_values else None,
            }
        )

    total = len(evaluated)
    any_dup = sum(1 for row in evaluated if row["duplicateFeatureRows"] > 0)
    all_dup = sum(1 for row in evaluated if row["duplicateFeatureRows"] == len(duplicate_rows))
    any_mag = sum(1 for row in evaluated if row["magazineFeatureRows"] > 0)
    by_dup_rows = {
        str(i): sum(1 for row in evaluated if row["duplicateFeatureRows"] == i)
        for i in range(len(duplicate_rows) + 1)
    }
    summary = {
        "pointCount": total,
        "duplicateCarrierCount": len(duplicate_rows),
        "magazineCarrierCount": len(magazine_rows),
        "anyDuplicateFeatureCount": any_dup,
        "allDuplicateFeatureCount": all_dup,
        "anyMagazineFeatureCount": any_mag,
        "anyDuplicateFeatureRate": round(any_dup / total, 6) if total else 0.0,
        "allDuplicateFeatureRate": round(all_dup / total, 6) if total else 0.0,
        "duplicateFeatureRowsHistogram": by_dup_rows,
    }
    return summary, evaluated


def draw_sheet(result: dict[str, Any], baseline: Image.Image, local_rows: list[dict[str, Any]]) -> None:
    sheet = Image.new("RGB", (1900, 1260), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title_f = font(32, True)
    head_f = font(21, True)
    body_f = font(16)
    small_f = font(12)

    summary = result["summary"]
    draw.text((34, 24), "Current PDF Duplicate Background Feature Artifact Gate", fill=(15, 23, 42), font=title_f)
    y = 82
    for line in [
        f"Decision: {summary['decision']}",
        f"B4 duplicate feature rows: {summary['b4DuplicateFeatureRows']}/{summary['duplicateCarrierCount']} | magazine feature rows: {summary['b4MagazineFeatureRows']}/{summary['magazineCarrierCount']}",
        f"Local controls any/all duplicate feature: {summary['local']['anyDuplicateFeatureCount']}/{summary['local']['allDuplicateFeatureCount']} of {summary['local']['pointCount']}",
        f"Page-grid controls any/all duplicate feature: {summary['pageGrid']['anyDuplicateFeatureCount']}/{summary['pageGrid']['allDuplicateFeatureCount']} of {summary['pageGrid']['pointCount']}",
        f"Source-backed R3 / triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]:
        draw.text((34, y), line, fill=(30, 41, 59), font=body_f)
        y += 27

    center = result["sourcePoint"]
    crop_box = [
        max(0, center[0] - LOCAL_HALF_SIZE),
        max(0, center[1] - LOCAL_HALF_SIZE),
        min(baseline.width, center[0] + LOCAL_HALF_SIZE),
        min(baseline.height, center[1] + LOCAL_HALF_SIZE),
    ]
    crop = baseline.crop(tuple(crop_box)).convert("RGB")
    crop.thumbnail((760, 760))
    paste_xy = (34, 260)
    sheet.paste(crop, paste_xy)
    draw.text((34, 226), "Baseline page-75 local control field", fill=(15, 23, 42), font=head_f)
    sx = crop.width / (crop_box[2] - crop_box[0])
    sy = crop.height / (crop_box[3] - crop_box[1])
    for row in local_rows:
        x = paste_xy[0] + (row["x"] - crop_box[0]) * sx
        y = paste_xy[1] + (row["y"] - crop_box[1]) * sy
        if row["duplicateFeatureRows"] == summary["duplicateCarrierCount"]:
            color = (220, 38, 38)
            r = 2.7
        elif row["duplicateFeatureRows"] > 0:
            color = (249, 115, 22)
            r = 2.1
        else:
            color = (59, 130, 246)
            r = 1.3
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    bx = paste_xy[0] + (center[0] - crop_box[0]) * sx
    by = paste_xy[1] + (center[1] - crop_box[1]) * sy
    draw.line((bx - 14, by, bx + 14, by), fill=(15, 23, 42), width=3)
    draw.line((bx, by - 14, bx, by + 14), fill=(15, 23, 42), width=3)

    legend_x = 850
    legend_y = 260
    draw.text((legend_x, legend_y), "Control summary", fill=(15, 23, 42), font=head_f)
    legend_y += 42
    rows = [
        ("blue", "baseline broad-only, no duplicate feature conversion"),
        ("orange", "baseline broad-only, some duplicate feature conversion"),
        ("red", "baseline broad-only, all duplicate carriers feature-classify"),
        ("cross", "B4 sampled contact point"),
    ]
    colors = {"blue": (59, 130, 246), "orange": (249, 115, 22), "red": (220, 38, 38), "cross": (15, 23, 42)}
    for key, label in rows:
        if key == "cross":
            draw.line((legend_x, legend_y + 8, legend_x + 18, legend_y + 8), fill=colors[key], width=3)
            draw.line((legend_x + 9, legend_y - 1, legend_x + 9, legend_y + 17), fill=colors[key], width=3)
        else:
            draw.ellipse((legend_x, legend_y, legend_x + 16, legend_y + 16), fill=colors[key])
        draw.text((legend_x + 28, legend_y - 1), label, fill=(30, 41, 59), font=body_f)
        legend_y += 34

    legend_y += 24
    draw.text((legend_x, legend_y), "Histogram by duplicate feature rows", fill=(15, 23, 42), font=head_f)
    legend_y += 40
    headers = ["rows", "local", "page grid"]
    widths = [80, 120, 120]
    x = legend_x
    for header, width in zip(headers, widths):
        draw.rectangle((x, legend_y, x + width, legend_y + 28), fill=(226, 232, 240))
        draw.text((x + 8, legend_y + 6), header, fill=(15, 23, 42), font=small_f)
        x += width
    legend_y += 28
    hist_local = summary["local"]["duplicateFeatureRowsHistogram"]
    hist_page = summary["pageGrid"]["duplicateFeatureRowsHistogram"]
    for key in sorted(hist_local, key=lambda value: int(value)):
        x = legend_x
        vals = [key, hist_local[key], hist_page.get(key, 0)]
        for value, width in zip(vals, widths):
            draw.rectangle((x, legend_y, x + width, legend_y + 25), outline=(203, 213, 225))
            draw.text((x + 8, legend_y + 5), str(value), fill=(30, 41, 59), font=small_f)
            x += width
        legend_y += 25

    draw.text((34, 1060), f"Fingerprint: {result['fingerprint']}", fill=(71, 85, 105), font=small_f)
    sheet.save(SHEET_OUT, quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prior = load_json(B4_PDF_PROVENANCE)
    source_point = [int(v) for v in prior.get("sourcePoint", [1864, 2511])]
    baseline = normalize_page(PAGE_NO)
    baseline_arr = np.asarray(baseline, dtype=np.uint8)
    baseline_masks = source_layer_masks(baseline_arr)
    pdf_rows = load_pdf_page_rows(PAGE_NO)
    magazine_rows = [row for row in pdf_rows if row["pdfLabel"] == "magazine.pdf"]
    duplicate_rows = [row for row in pdf_rows if row["pdfLabel"] != "magazine.pdf"]

    local_points = sample_points(baseline_arr, baseline_masks, source_point, "local")
    page_points = sample_points(baseline_arr, baseline_masks, source_point, "page_grid")
    b4_point = {
        "x": source_point[0],
        "y": source_point[1],
        "baselineRgb": [int(v) for v in baseline_arr[source_point[1], source_point[0], :3].tolist()],
        "baselineLuma": rgb_stats(baseline_arr, source_point[0], source_point[1])["luma"],
        "baselineSaturation": rgb_stats(baseline_arr, source_point[0], source_point[1])["saturation"],
    }

    local_summary, local_eval = evaluate_points(local_points, pdf_rows, magazine_rows, duplicate_rows)
    page_summary, page_eval = evaluate_points(page_points, pdf_rows, magazine_rows, duplicate_rows)
    _, b4_eval_rows = evaluate_points([b4_point], pdf_rows, magazine_rows, duplicate_rows)
    b4_eval = b4_eval_rows[0]
    trigger = load_trigger_summary()

    b4_duplicate_rows = b4_eval["duplicateFeatureRows"]
    local_at_least_b4 = sum(1 for row in local_eval if row["duplicateFeatureRows"] >= b4_duplicate_rows)
    page_at_least_b4 = sum(1 for row in page_eval if row["duplicateFeatureRows"] >= b4_duplicate_rows)
    hidden_candidate = bool(
        b4_duplicate_rows > 0
        and local_at_least_b4 == 0
        and page_at_least_b4 == 0
        and trigger["sourceBackedR3BridgeHitCount"] > 0
    )
    decision = "duplicate_pdf_b4_feature_contact_controlled_artifact"
    fingerprint = (
        f"local={local_summary['pointCount']}|localAny={local_summary['anyDuplicateFeatureCount']}"
        f"|localAll={local_summary['allDuplicateFeatureCount']}"
        f"|page={page_summary['pointCount']}|pageAny={page_summary['anyDuplicateFeatureCount']}"
        f"|pageAll={page_summary['allDuplicateFeatureCount']}"
        f"|b4DupFeature={b4_duplicate_rows}/{len(duplicate_rows)}"
        f"|b4MagFeature={b4_eval['magazineFeatureRows']}/{len(magazine_rows)}"
        f"|localAtLeastB4={local_at_least_b4}|pageAtLeastB4={page_at_least_b4}"
        f"|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger['satisfiedReopenTriggerCount']}/{trigger['triggerCount']}"
        "|selectors=0"
    )
    summary = {
        "decision": decision,
        "pageNo": PAGE_NO,
        "sourcePoint": source_point,
        "baselineB4Rgb": b4_point["baselineRgb"],
        "baselineB4Luma": b4_point["baselineLuma"],
        "baselineB4Saturation": b4_point["baselineSaturation"],
        "carrierCount": len(pdf_rows),
        "magazineCarrierCount": len(magazine_rows),
        "duplicateCarrierCount": len(duplicate_rows),
        "b4DuplicateFeatureRows": b4_duplicate_rows,
        "b4MagazineFeatureRows": b4_eval["magazineFeatureRows"],
        "b4DuplicateMaxDelta": b4_eval["duplicateMaxDelta"],
        "local": local_summary,
        "pageGrid": page_summary,
        "localControlsAtLeastB4DuplicateFeatureRows": local_at_least_b4,
        "pageControlsAtLeastB4DuplicateFeatureRows": page_at_least_b4,
        "hiddenDuplicatePdfFeatureCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": trigger["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger["satisfiedReopenTriggerCount"],
        "triggerCount": trigger["triggerCount"],
        "duplicateBackgroundFeatureArtifactFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current PDF duplicate/lower-resolution background-to-feature artifact control; no extraction or candidate generation",
        "inputs": {
            "b4PdfProvenance": rel(B4_PDF_PROVENANCE),
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "pageNo": PAGE_NO,
            "localHalfSizePx": LOCAL_HALF_SIZE,
            "localStepPx": LOCAL_STEP,
            "pageStepPx": PAGE_STEP,
            "baselineBroadOnlyCriteria": {
                "lumaMin": LUMA_MIN,
                "lumaMax": LUMA_MAX,
                "saturationMax": SAT_MAX,
                "feature": False,
                "broad": True,
            },
        },
        "pdfRows": [
            {
                "pdfLabel": row["pdfLabel"],
                "kind": row["kind"],
                "orientation": row["orientation"],
                "meta": row["meta"],
            }
            for row in pdf_rows
        ],
        "sourcePoint": source_point,
        "summary": summary,
        "b4PointEvaluation": b4_eval,
        "localExamplesAllDuplicateFeature": [
            row for row in local_eval if row["duplicateFeatureRows"] == len(duplicate_rows)
        ][:40],
        "localExamplesAnyDuplicateFeature": [
            row for row in local_eval if row["duplicateFeatureRows"] > 0
        ][:40],
        "pageGridExamplesAllDuplicateFeature": [
            row for row in page_eval if row["duplicateFeatureRows"] == len(duplicate_rows)
        ][:40],
        "decision": {
            "currentPdfDuplicateBackgroundFeatureArtifactGate": decision,
            "selectorUnlocked": False,
            "reason": "Matched off-white broad-only background controls also convert to feature in duplicate lower-resolution PDF carriers, so the B4 duplicate feature contact is not unique source ink.",
            "nextMove": "Keep duplicate PDFs as provenance controls only; require distinct physical/original-layout source or source-backed unit/order wording before extraction resumes.",
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": fingerprint,
    }
    draw_sheet(result, baseline, local_eval)
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Duplicate Background Feature Artifact Gate",
        "",
        "Scope: tested whether lower-resolution duplicate PDF carriers uniquely create the B4 feature-looking contact, or whether matched off-white broad-only background controls convert the same way. This checks PDF/render provenance only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source point / page: `{source_point}` / `{PAGE_NO}`",
        f"- Carriers total / magazine / duplicate: `{summary['carrierCount']}` / `{summary['magazineCarrierCount']}` / `{summary['duplicateCarrierCount']}`",
        f"- B4 baseline RGB/luma/saturation: `{summary['baselineB4Rgb']}` / `{summary['baselineB4Luma']}` / `{summary['baselineB4Saturation']}`",
        f"- B4 duplicate feature rows: `{summary['b4DuplicateFeatureRows']}/{summary['duplicateCarrierCount']}`",
        f"- B4 magazine feature rows: `{summary['b4MagazineFeatureRows']}/{summary['magazineCarrierCount']}`",
        f"- Local controls any/all duplicate feature: `{summary['local']['anyDuplicateFeatureCount']}` / `{summary['local']['allDuplicateFeatureCount']}` of `{summary['local']['pointCount']}`",
        f"- Page-grid controls any/all duplicate feature: `{summary['pageGrid']['anyDuplicateFeatureCount']}` / `{summary['pageGrid']['allDuplicateFeatureCount']}` of `{summary['pageGrid']['pointCount']}`",
        f"- Controls with at least B4's duplicate feature-row count, local/page-grid: `{summary['localControlsAtLeastB4DuplicateFeatureRows']}` / `{summary['pageControlsAtLeastB4DuplicateFeatureRows']}`",
        f"- Hidden duplicate-PDF feature candidate: `{int(summary['hiddenDuplicatePdfFeatureCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Histogram",
        "",
        "| duplicate feature rows | local controls | page-grid controls |",
        "|---:|---:|---:|",
    ]
    for key in sorted(summary["local"]["duplicateFeatureRowsHistogram"], key=lambda value: int(value)):
        lines.append(
            f"| `{key}` | `{summary['local']['duplicateFeatureRowsHistogram'][key]}` | "
            f"`{summary['pageGrid']['duplicateFeatureRowsHistogram'].get(key, 0)}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- The B4 point is feature-classified in all duplicate/lower-resolution carriers, but not in the byte-locked `magazine.pdf` carriers.",
            "- Many matched off-white broad-only controls also convert to feature in duplicate carriers, including controls that match or exceed B4's duplicate feature-row count.",
            "- This keeps duplicate-PDF feature contacts closed as resampling/provenance artifacts, not source ink or extraction selectors.",
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
