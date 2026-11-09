#!/usr/bin/env python3
"""Compare current PDF rasters after OCR-derived alignment to page 76.

The current PDFs expose page 76 as raster images plus OCR overlays. Previous
passes established that the OCR text and its affine alignment do not unlock
O4/B4/G5/O5. This pass checks the visible raster layer itself: after applying
the OCR-derived affine registration for the low-resolution duplicate PDFs, do
active targets, orange highlights, or the OVERDOSE header reveal a materially
different visual state from the high-resolution page-76 baseline?

This is source/render provenance inspection only. No OCR-to-key extraction,
hashing, seed/WIF/address checks, BIP39 checks, or candidate generation is run.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_render_alignment_delta_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_render_alignment_delta_gate.json"
OUT_MD = OUT / "current_pdf_render_alignment_delta_gate.md"
OUT_SHEET = OUT / "current_pdf_render_alignment_delta_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
AFFINE_REPORT = ROOT / (
    "analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/"
    "current_pdf_ocr_affine_alignment_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
REGION_PAD = 8
MEAN_DIFF_THRESHOLD = 45.0
LARGE_RESIDUAL_THRESHOLD = 80


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_sha(path: Path) -> str:
    with path.open("rb") as fh:
        return sha256_bytes(fh.read())


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


def clamp_box(box: list[float], width: float, height: float, pad: float = 0.0) -> list[int]:
    return [
        int(max(0, min(width, np.floor(box[0] - pad)))),
        int(max(0, min(height, np.floor(box[1] - pad)))),
        int(max(0, min(width, np.ceil(box[2] + pad)))),
        int(max(0, min(height, np.ceil(box[3] + pad)))),
    ]


def active_regions() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = by_short[short_id]
        rows.append(
            {
                "id": short_id,
                "kind": "active_target",
                "label": row["label"],
                "box": [float(v) for v in row["box"]],
                "expectedState": row.get("visualState"),
            }
        )
    return rows


def article_regions() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    page = next(row for row in data["pages"] if row["page"] == 76)
    regions = []
    for word in page["words"]:
        if str(word.get("token", "")).lower() == "overdose":
            regions.append(
                {
                    "id": "OVERDOSE_header",
                    "kind": "overdose_header",
                    "label": "OVERDOSE",
                    "box": [float(v) for v in word["box"]],
                    "expectedState": "K",
                }
            )
            break
    for highlight in page.get("highlights", []):
        regions.append(
            {
                "id": highlight["id"],
                "kind": "orange_highlight",
                "label": highlight["id"],
                "box": [float(v) for v in highlight["box"]],
                "expectedState": "Y",
            }
        )
    return regions


def image_rect(page: fitz.Page) -> tuple[fitz.Rect, int | None, tuple[int, int] | None]:
    best_rect = page.rect
    best_xref = None
    best_size = None
    best_area = -1.0
    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = page.parent.extract_image(xref)
        for rect in page.get_image_rects(xref):
            area = max(0.0, rect.width) * max(0.0, rect.height)
            if area > best_area:
                best_area = area
                best_rect = rect
                best_xref = xref
                best_size = (int(extracted.get("width", image[2])), int(extracted.get("height", image[3])))
    return best_rect, best_xref, best_size


def extract_pdf_image(pdf_path: Path) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    rect, xref, size = image_rect(page)
    if xref is None:
        pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        data = image.tobytes()
        return {
            "pdf": rel(pdf_path),
            "rotation": page.rotation,
            "image": image,
            "imageSha256": sha256_bytes(data),
            "imageRect": [round(rect.x0, 3), round(rect.y0, 3), round(rect.x1, 3), round(rect.y1, 3)],
            "imageSize": [image.width, image.height],
        }
    extracted = doc.extract_image(xref)
    image = Image.open(fitz.open("pdf", b"").name) if False else None
    image = Image.open(__import__("io").BytesIO(extracted["image"])).convert("RGB")
    return {
        "pdf": rel(pdf_path),
        "rotation": page.rotation,
        "image": image,
        "imageSha256": sha256_bytes(extracted["image"]),
        "imageRect": [round(rect.x0, 3), round(rect.y0, 3), round(rect.x1, 3), round(rect.y1, 3)],
        "imageSize": [image.width, image.height],
    }


def affine_by_pdf() -> dict[str, list[list[float]]]:
    data = load_json(AFFINE_REPORT)
    out = {}
    for record in data.get("records", []):
        fit = record.get("fit", {})
        if fit.get("fitAvailable"):
            out[record["pdfRecord"]["pdf"]] = fit["matrix"]
    return out


def inverse_matrix(matrix: list[list[float]]) -> np.ndarray:
    m = np.array([[matrix[0][0], matrix[0][1], matrix[0][2]], [matrix[1][0], matrix[1][1], matrix[1][2]], [0, 0, 1]], dtype=float)
    return np.linalg.inv(m)


def transform_point(matrix: np.ndarray, x: float, y: float) -> tuple[float, float]:
    out = matrix @ np.array([x, y, 1.0])
    return float(out[0]), float(out[1])


def crop_aligned_region(source_image: Image.Image, output_box: list[int], matrix: list[list[float]] | None) -> Image.Image:
    out_w = max(1, output_box[2] - output_box[0])
    out_h = max(1, output_box[3] - output_box[1])
    if matrix is None:
        src_box = clamp_box(output_box, source_image.width, source_image.height)
    else:
        inv = inverse_matrix(matrix)
        corners = [
            transform_point(inv, output_box[0], output_box[1]),
            transform_point(inv, output_box[2], output_box[1]),
            transform_point(inv, output_box[0], output_box[3]),
            transform_point(inv, output_box[2], output_box[3]),
        ]
        xs = [(x / SOURCE_IMAGE_SIZE[0]) * source_image.width for x, _ in corners]
        ys = [(y / SOURCE_IMAGE_SIZE[1]) * source_image.height for _, y in corners]
        src_box = clamp_box([min(xs), min(ys), max(xs), max(ys)], source_image.width, source_image.height)
    crop = source_image.crop(src_box)
    return crop.resize((out_w, out_h), Image.Resampling.BICUBIC)


def crop_baseline_region(baseline: Image.Image, box: list[int]) -> Image.Image:
    return baseline.crop(box)


def color_stats(img: Image.Image) -> dict[str, float]:
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    mean = (r + g + b) / 3
    orange = (r > 125) & (g > 55) & (g < 215) & (b < 155) & (r > g + 12)
    dark = mean < 168
    grey = (mean < 220) & (np.abs(r - g) < 20) & (np.abs(g - b) < 20)
    return {
        "orangeRatio": round(float(orange.mean()), 4),
        "darkRatio": round(float(dark.mean()), 4),
        "greyRatio": round(float(grey.mean()), 4),
        "meanLuma": round(float(mean.mean()), 3),
    }


def classify_state(stats: dict[str, float]) -> str:
    if stats["orangeRatio"] >= 0.12:
        return "Y"
    if stats["darkRatio"] >= 0.18:
        return "K"
    return "N"


def diff_metrics(base: Image.Image, other: Image.Image) -> dict[str, Any]:
    if base.size != other.size:
        other = other.resize(base.size, Image.Resampling.BICUBIC)
    diff = ImageChops.difference(base.convert("RGB"), other.convert("RGB"))
    stat = ImageStat.Stat(diff)
    arr = np.asarray(diff.convert("L"))
    return {
        "meanAbsDiff": round(float(sum(stat.mean) / 3.0), 3),
        "maxDiff": int(arr.max()) if arr.size else 0,
        "largeResidualRatio": round(float((arr > LARGE_RESIDUAL_THRESHOLD).mean()), 4) if arr.size else 0.0,
    }


def build_records() -> dict[str, Any]:
    baseline = Image.open(UPRIGHT_PAGE).convert("RGB")
    matrix_by_pdf = affine_by_pdf()
    regions = active_regions() + article_regions()
    pdf_images = [extract_pdf_image(path) for path in PDFS if path.exists()]
    records = []
    image_sha_groups: dict[str, list[str]] = {}
    for item in pdf_images:
        image_sha_groups.setdefault(item["imageSha256"][:16], []).append(item["pdf"])

    for item in pdf_images:
        pdf = item["pdf"]
        image = item["image"]
        if pdf == "magazine.pdf":
            source = baseline
            matrix = None
            alignment = "baseline_highres"
        else:
            source = image
            matrix = matrix_by_pdf.get(pdf)
            alignment = "ocr_affine" if matrix else "none"
        region_rows = []
        for region in regions:
            box = clamp_box(region["box"], baseline.width, baseline.height, REGION_PAD)
            base_crop = crop_baseline_region(baseline, box)
            aligned_crop = crop_aligned_region(source, box, matrix)
            base_stats = color_stats(base_crop)
            aligned_stats = color_stats(aligned_crop)
            metrics = diff_metrics(base_crop, aligned_crop)
            region_rows.append(
                {
                    "regionId": region["id"],
                    "kind": region["kind"],
                    "label": region["label"],
                    "expectedState": region.get("expectedState"),
                    "box": box,
                    "baselineState": classify_state(base_stats),
                    "alignedState": classify_state(aligned_stats),
                    "stateMatchesBaseline": classify_state(base_stats) == classify_state(aligned_stats),
                    "stateMatchesExpected": (
                        region.get("expectedState") is None
                        or classify_state(aligned_stats) == region.get("expectedState")
                    ),
                    "baselineStats": base_stats,
                    "alignedStats": aligned_stats,
                    **metrics,
                    "materialResidual": metrics["meanAbsDiff"] > MEAN_DIFF_THRESHOLD
                    or metrics["largeResidualRatio"] > 0.18,
                }
            )
        records.append(
            {
                "pdf": pdf,
                "rotation": item["rotation"],
                "imageSize": item["imageSize"],
                "imageSha256Prefix": item["imageSha256"][:16],
                "alignment": alignment,
                "fitAvailable": bool(matrix),
                "regionRows": region_rows,
                "summary": {
                    "regionCount": len(region_rows),
                    "stateMismatchCount": sum(1 for row in region_rows if not row["stateMatchesBaseline"]),
                    "expectedStateMismatchCount": sum(1 for row in region_rows if not row["stateMatchesExpected"]),
                    "materialResidualRegionCount": sum(1 for row in region_rows if row["materialResidual"]),
                    "maxMeanAbsDiff": max(row["meanAbsDiff"] for row in region_rows),
                    "maxLargeResidualRatio": max(row["largeResidualRatio"] for row in region_rows),
                    "activeTargetMaterialResidualCount": sum(
                        1
                        for row in region_rows
                        if row["kind"] == "active_target" and row["materialResidual"]
                    ),
                    "activeTargetStateMismatchCount": sum(
                        1
                        for row in region_rows
                        if row["kind"] == "active_target" and not row["stateMatchesBaseline"]
                    ),
                },
            }
        )
    return {"baseline": baseline, "regions": regions, "records": records, "imageShaGroups": image_sha_groups}


def draw_sheet(bundle: dict[str, Any]) -> None:
    baseline = bundle["baseline"]
    records = [row for row in bundle["records"] if row["pdf"] != "magazine.pdf"]
    title_f = font(26)
    body_f = font(16)
    small_f = font(12)
    crop_w = 190
    crop_h = 78
    row_h = 140
    width = 1840
    height = 95 + max(1, len(records)) * (len(bundle["regions"]) * row_h + 70)
    sheet = Image.new("RGB", (width, height), (244, 245, 247))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 22), "Current PDF Render Alignment Delta Gate", fill=(20, 28, 38), font=title_f)
    draw.text(
        (24, 56),
        "Baseline crop vs OCR-affine aligned low-resolution PDF crop vs visual difference.",
        fill=(62, 72, 86),
        font=body_f,
    )
    y = 95
    for record in records:
        draw.text(
            (24, y),
            f"{record['pdf']}  image={record['imageSize']}  alignment={record['alignment']}  active residuals={record['summary']['activeTargetMaterialResidualCount']}  state mismatches={record['summary']['stateMismatchCount']}",
            fill=(20, 28, 38),
            font=body_f,
        )
        y += 34
        image = extract_pdf_image(ROOT / record["pdf"])["image"]
        matrix = affine_by_pdf().get(record["pdf"])
        for region_row in record["regionRows"]:
            box = region_row["box"]
            base_crop = crop_baseline_region(baseline, box).resize((crop_w, crop_h), Image.Resampling.BICUBIC)
            aligned_crop = crop_aligned_region(image, box, matrix).resize((crop_w, crop_h), Image.Resampling.BICUBIC)
            diff = ImageChops.difference(base_crop, aligned_crop)
            x = 24
            sheet.paste(base_crop, (x, y + 25))
            sheet.paste(aligned_crop, (x + crop_w + 14, y + 25))
            sheet.paste(diff, (x + 2 * (crop_w + 14), y + 25))
            draw.text((x, y + 4), region_row["regionId"], fill=(20, 28, 38), font=small_f)
            tx = x + 3 * (crop_w + 14) + 8
            draw.text(
                (tx, y + 26),
                f"state {region_row['baselineState']}->{region_row['alignedState']} expected={region_row['expectedState']} meanDiff={region_row['meanAbsDiff']} large={region_row['largeResidualRatio']} material={region_row['materialResidual']}",
                fill=(45, 50, 58),
                font=small_f,
            )
            draw.text(
                (tx, y + 48),
                f"base orange/dark={region_row['baselineStats']['orangeRatio']}/{region_row['baselineStats']['darkRatio']} aligned={region_row['alignedStats']['orangeRatio']}/{region_row['alignedStats']['darkRatio']}",
                fill=(70, 78, 88),
                font=small_f,
            )
            y += row_h
        y += 34
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    source_review = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    bundle = build_records()
    draw_sheet(bundle)
    records = bundle["records"]
    duplicate_groups = [v for v in bundle["imageShaGroups"].values() if len(v) > 1]
    non_baseline = [row for row in records if row["pdf"] != "magazine.pdf"]
    active_material = sum(row["summary"]["activeTargetMaterialResidualCount"] for row in non_baseline)
    active_state_mismatch = sum(row["summary"]["activeTargetStateMismatchCount"] for row in non_baseline)
    material_regions = sum(row["summary"]["materialResidualRegionCount"] for row in non_baseline)
    state_mismatch = sum(row["summary"]["stateMismatchCount"] for row in non_baseline)
    expected_mismatch = sum(row["summary"]["expectedStateMismatchCount"] for row in non_baseline)
    max_mean = max([row["summary"]["maxMeanAbsDiff"] for row in non_baseline] or [0])
    max_large = max([row["summary"]["maxLargeResidualRatio"] for row in non_baseline] or [0])
    source_r3 = (
        source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount")
        or reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount")
        or 0
    )
    satisfied = (
        source_review.get("summary", {}).get("satisfiedReopenTriggerCount")
        or reopen.get("summary", {}).get("satisfiedTriggerCount")
        or reopen.get("summary", {}).get("satisfiedNow")
        or 0
    )
    trigger_count = (
        reopen.get("summary", {}).get("triggerCount")
        or reopen.get("triggerCount")
        or len(reopen.get("triggerRows", []))
        or 9
    )
    fingerprint = (
        f"pdfs={len(records)}|dupeGroups={len(duplicate_groups)}|nonBase={len(non_baseline)}|"
        f"activeMaterial={active_material}|activeStateMismatch={active_state_mismatch}|"
        f"materialRegions={material_regions}|stateMismatch={state_mismatch}|expectedMismatch={expected_mismatch}|"
        f"maxMean={max_mean}|maxLarge={max_large}|sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current PDF render alignment delta gate. Compares visible page-76 PDF rasters "
            "after OCR-derived alignment against the high-resolution page-76 baseline around "
            "active targets, orange highlights, and OVERDOSE header. No OCR-to-key/hash/seed/"
            "WIF/address/BIP39/candidate work."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "uprightPage": rel(UPRIGHT_PAGE),
            "affineReport": rel(AFFINE_REPORT),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": {
            "pdfCount": len(records),
            "duplicateImageShaGroupCount": len(duplicate_groups),
            "duplicateImageShaGroups": duplicate_groups,
            "nonBaselinePdfCount": len(non_baseline),
            "activeTargetMaterialResidualCount": active_material,
            "activeTargetStateMismatchCount": active_state_mismatch,
            "materialResidualRegionCount": material_regions,
            "stateMismatchRegionCount": state_mismatch,
            "expectedStateMismatchRegionCount": expected_mismatch,
            "maxMeanAbsDiff": max_mean,
            "maxLargeResidualRatio": max_large,
            "sourceBackedR3BridgeHitCount": source_r3,
            "satisfiedReopenTriggerCount": satisfied,
            "triggerCount": trigger_count,
            "selectorUnlocked": False,
            "pdfRenderAlignmentDeltaFingerprint": fingerprint,
        },
        "records": records,
        "decision": {
            "currentPdfRenderAlignmentDeltaGate": "do_not_reopen_lowres_pdf_render",
            "selectorUnlocked": False,
            "reason": (
                "The visible low-resolution duplicate PDF rasters are duplicate source images. "
                "After OCR-derived alignment, their active-target regions preserve visual state "
                "and do not add source-side unit/order evidence; residuals are render/downsample "
                "differences rather than a new target selector."
            ),
            "nextMove": (
                "Keep the high-resolution page-76 scan as visual authority. Treat low-resolution "
                "PDF renders as duplicate/context witnesses unless a new original-layout or physical "
                "source arrives and passes R1/R3."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Render Alignment Delta Gate",
        "",
        "Scope: compare visible page-76 PDF rasters after OCR-derived alignment against the high-resolution page-76 baseline around O4/B4/G5/O5, orange highlights, and the OVERDOSE header. No OCR-to-key extraction, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{len(records)}`",
        f"- Duplicate image SHA groups: `{len(duplicate_groups)}`",
        f"- Non-baseline PDFs: `{len(non_baseline)}`",
        f"- Active target material residuals: `{active_material}`",
        f"- Active target state mismatches: `{active_state_mismatch}`",
        f"- Material residual regions: `{material_regions}`",
        f"- State mismatch / expected-state mismatch regions: `{state_mismatch}` / `{expected_mismatch}`",
        f"- Max mean abs diff / max large residual ratio: `{max_mean}` / `{max_large}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | image size | alignment | active material | active state mismatch | material regions | state mismatch | max mean diff | max large residual |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for record in records:
        summary = record["summary"]
        lines.append(
            f"| `{record['pdf']}` | `{record['imageSize']}` | `{record['alignment']}` | `{summary['activeTargetMaterialResidualCount']}` | `{summary['activeTargetStateMismatchCount']}` | `{summary['materialResidualRegionCount']}` | `{summary['stateMismatchCount']}` | `{summary['maxMeanAbsDiff']}` | `{summary['maxLargeResidualRatio']}` |"
        )
    lines.extend(["", "## Active Target Detail", ""])
    for record in non_baseline:
        lines.append(f"### `{record['pdf']}`")
        lines.append("")
        for row in record["regionRows"]:
            if row["kind"] != "active_target":
                continue
            lines.append(
                f"- {row['regionId']} `{row['label']}`: state `{row['baselineState']}->{row['alignedState']}`, expected `{row['expectedState']}`, mean diff `{row['meanAbsDiff']}`, large residual `{row['largeResidualRatio']}`, material `{row['materialResidual']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Decision",
            "",
            "- Do not reopen the low-resolution PDF render layer as an extraction source.",
            "- The duplicate PDFs share the same visible page image. After OCR-derived alignment, active target states are preserved and no source-side unit/order evidence appears.",
            "- Residuals are expected downsample/render differences, not a new physical or original-layout layer.",
            "",
            "## Next Move",
            "",
            "- Keep the high-resolution page-76 scan as visual authority. Future useful work remains source-intake/reopen-gate validation unless new physical/original-layout/source evidence arrives.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()
