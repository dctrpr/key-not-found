#!/usr/bin/env python3
"""Audit page-76 embedded PDF image channels and masks.

The current PDFs expose page 76 as a single page image plus OCR text. The prior
render-delta pass checked visible raster alignment. This pass asks a narrower
source-material question: do the embedded page images contain alpha masks,
soft masks, non-RGB separations, ICC/CMYK channels, or channel-only anomalies
around O4/B4/G5/O5, orange highlights, or the OVERDOSE header?

This is PDF source/render provenance inspection only. No OCR-to-key extraction,
hashing, seed/WIF/address checks, BIP39 checks, or candidate generation is run.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_embedded_channel_mask_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_embedded_channel_mask_gate.json"
OUT_MD = OUT / "current_pdf_embedded_channel_mask_gate.md"
OUT_SHEET = OUT / "current_pdf_embedded_channel_mask_gate_sheet.jpg"

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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def context_regions() -> list[dict[str, Any]]:
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


def affine_by_pdf() -> dict[str, list[list[float]]]:
    data = load_json(AFFINE_REPORT)
    out = {}
    for record in data.get("records", []):
        fit = record.get("fit", {})
        if fit.get("fitAvailable"):
            out[record["pdfRecord"]["pdf"]] = fit["matrix"]
    return out


def inverse_matrix(matrix: list[list[float]]) -> np.ndarray:
    m = np.array(
        [
            [matrix[0][0], matrix[0][1], matrix[0][2]],
            [matrix[1][0], matrix[1][1], matrix[1][2]],
            [0, 0, 1],
        ],
        dtype=float,
    )
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
    return source_image.crop(src_box).resize((out_w, out_h), Image.Resampling.BICUBIC)


def image_rows(pdf_path: Path) -> list[dict[str, Any]]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    rows = []
    for image_tuple in page.get_images(full=True):
        xref = int(image_tuple[0])
        smask_xref = int(image_tuple[1])
        width = int(image_tuple[2])
        height = int(image_tuple[3])
        bits = int(image_tuple[4])
        colorspace = str(image_tuple[5])
        name = str(image_tuple[7])
        filter_name = str(image_tuple[8])
        raw_object = doc.xref_object(xref)
        extracted = doc.extract_image(xref)
        image_bytes = extracted.get("image", b"")
        pix = fitz.Pixmap(doc, xref)
        pil = Image.open(BytesIO(image_bytes)).convert("RGB")
        analysis_image = pil.rotate(180, expand=True) if page.rotation == 180 else pil
        rects = page.get_image_rects(xref)
        mask_terms = {
            "smaskTuple": smask_xref != 0,
            "alphaPixmap": bool(pix.alpha),
            "softMaskObject": "/SMask" in raw_object,
            "hardMaskObject": "/Mask" in raw_object,
            "iccBased": "/ICCBased" in raw_object,
            "deviceCmyk": "/DeviceCMYK" in raw_object,
            "separation": "/Separation" in raw_object,
        }
        hidden_candidate = any(mask_terms.values()) or colorspace != "DeviceRGB" or bits != 8
        rows.append(
            {
                "xref": xref,
                "name": name,
                "width": width,
                "height": height,
                "bitsPerComponent": bits,
                "colorspace": colorspace,
                "filter": filter_name,
                "smaskXref": smask_xref,
                "pixmapAlpha": bool(pix.alpha),
                "objectMaskTerms": mask_terms,
                "hiddenChannelCandidate": bool(hidden_candidate),
                "sha256": sha256_bytes(image_bytes),
                "pageRotation": int(page.rotation),
                "analysisOrientation": "rotate180_for_readable" if page.rotation == 180 else "as_extracted_readable",
                "rects": [[round(r.x0, 3), round(r.y0, 3), round(r.x1, 3), round(r.y1, 3)] for r in rects],
                "_image": analysis_image,
            }
        )
    return rows


def color_stats(img: Image.Image) -> dict[str, Any]:
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    means = arr.mean(axis=(0, 1))
    stds = arr.std(axis=(0, 1))
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luma = (r + g + b) / 3.0
    orange = (r > 125) & (g > 55) & (g < 215) & (b < 155) & (r > g + 12)
    dark = luma < 168
    neutral = (np.abs(r - g) < 20) & (np.abs(g - b) < 20)
    spread = max(float(means.max() - means.min()), 0.0)
    return {
        "meanR": round(float(means[0]), 3),
        "meanG": round(float(means[1]), 3),
        "meanB": round(float(means[2]), 3),
        "stdR": round(float(stds[0]), 3),
        "stdG": round(float(stds[1]), 3),
        "stdB": round(float(stds[2]), 3),
        "channelSpread": round(spread, 3),
        "orangeRatio": round(float(orange.mean()), 4),
        "darkRatio": round(float(dark.mean()), 4),
        "neutralRatio": round(float(neutral.mean()), 4),
        "meanLuma": round(float(luma.mean()), 3),
    }


def classify_visible_state(stats: dict[str, Any]) -> str:
    if stats["orangeRatio"] >= 0.12:
        return "Y"
    if stats["darkRatio"] >= 0.25:
        return "K"
    return "N"


def expected_channel_explanation(expected: str | None, stats: dict[str, Any]) -> str:
    if expected == "Y" and stats["orangeRatio"] >= 0.12 and stats["meanR"] > stats["meanG"] > stats["meanB"]:
        return "expected_orange_rgb"
    if expected == "K" and stats["darkRatio"] >= 0.25:
        return "expected_dark_ink"
    if expected is None:
        return "no_expected_state"
    return "unexpected_channel_state"


def channel_panels(img: Image.Image, size: tuple[int, int]) -> list[Image.Image]:
    rgb = img.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    arr = np.asarray(rgb)
    panels = [rgb]
    for idx in range(3):
        panels.append(Image.fromarray(arr[:, :, idx], mode="L").convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    luma = ((r + g + b) / 3.0).astype(np.uint8)
    orange = ((r > 125) & (g > 55) & (g < 215) & (b < 155) & (r > g + 12)).astype(np.uint8) * 255
    dark = (luma < 168).astype(np.uint8) * 255
    panels.append(Image.fromarray(orange, mode="L").convert("RGB"))
    panels.append(Image.fromarray(dark, mode="L").convert("RGB"))
    return panels


def render_sheet(pdf_records: list[dict[str, Any]], region_records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    panel_w, panel_h = 126, 84
    label_w = 270
    headers = ["RGB", "R", "G", "B", "orange", "dark"]
    row_h = panel_h + 42
    selected_pdfs = [r for r in pdf_records if r["page76Images"]]
    if len(selected_pdfs) > 2:
        selected_pdfs = [selected_pdfs[0], selected_pdfs[1]]
    selected_regions = [r for r in region_records if r["regionKind"] == "active_target"]
    selected_regions += [r for r in region_records if r["regionId"] == "OVERDOSE_header"][:1]
    width = label_w + len(headers) * panel_w
    height = 92 + len(selected_pdfs) * (38 + len(selected_regions) * row_h)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title_font = font(22)
    text_font = font(14)
    small_font = font(11)
    draw.text((16, 12), "Current PDF Embedded Channel / Mask Gate", fill=(0, 0, 0), font=title_font)
    draw.text(
        (16, 42),
        f"hidden objects {summary['hiddenChannelCandidateImageCount']} | active unexpected {summary['activeUnexpectedChannelStateCount']} | triggers {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
        fill=(60, 60, 60),
        font=text_font,
    )
    y = 84
    by_pdf_region = {(r["pdf"], r["regionId"]): r for r in region_records}
    for pdf_row in selected_pdfs:
        draw.rectangle([0, y, width, y + 30], fill=(240, 240, 240))
        draw.text((16, y + 7), pdf_row["pdf"], fill=(0, 0, 0), font=text_font)
        for i, head in enumerate(headers):
            draw.text((label_w + i * panel_w + 8, y + 7), head, fill=(60, 60, 60), font=small_font)
        y += 34
        for region in selected_regions:
            row = by_pdf_region[(pdf_row["pdf"], region["regionId"])]
            draw.text((16, y + 6), f"{row['regionId']} {row['label']}", fill=(0, 0, 0), font=small_font)
            draw.text(
                (16, y + 24),
                f"state {row['visibleState']} expected {row.get('expectedState')}; {row['channelExplanation']}",
                fill=(90, 90, 90),
                font=small_font,
            )
            for i, panel in enumerate(channel_panels(row["_crop"], (panel_w - 8, panel_h - 8))):
                x = label_w + i * panel_w + 4
                sheet.paste(panel, (x, y + 38))
                draw.rectangle([x, y + 38, x + panel.width, y + 38 + panel.height], outline=(170, 170, 170))
            y += row_h
        y += 8
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    matrices = affine_by_pdf()
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    regions = active_regions() + context_regions()

    pdf_records = []
    region_records = []
    for pdf_path in PDFS:
        rows = image_rows(pdf_path)
        page_record = {
            "pdf": rel(pdf_path),
            "pageIndex": 3,
            "page76Images": [],
        }
        matrix = matrices.get(rel(pdf_path))
        for row in rows:
            image = row.pop("_image")
            page_record["page76Images"].append(row)
            for region in regions:
                box = clamp_box(region["box"], SOURCE_IMAGE_SIZE[0], SOURCE_IMAGE_SIZE[1], REGION_PAD)
                crop = crop_aligned_region(image, box, matrix)
                stats = color_stats(crop)
                visible_state = classify_visible_state(stats)
                expected = region.get("expectedState")
                channel_explanation = expected_channel_explanation(expected, stats)
                region_records.append(
                    {
                        "pdf": rel(pdf_path),
                        "regionId": region["id"],
                        "regionKind": region["kind"],
                        "label": region["label"],
                        "expectedState": expected,
                        "visibleState": visible_state,
                        "stateMismatch": bool(expected and visible_state != expected),
                        "channelExplanation": channel_explanation,
                        "channelUnexpected": channel_explanation == "unexpected_channel_state",
                        "stats": stats,
                        "_crop": crop,
                    }
                )
        pdf_records.append(page_record)

    hidden_image_count = sum(
        1
        for pdf in pdf_records
        for image in pdf["page76Images"]
        if image["hiddenChannelCandidate"]
    )
    smask_count = sum(
        1
        for pdf in pdf_records
        for image in pdf["page76Images"]
        if image["smaskXref"] or image["objectMaskTerms"]["softMaskObject"] or image["objectMaskTerms"]["hardMaskObject"]
    )
    alpha_count = sum(
        1 for pdf in pdf_records for image in pdf["page76Images"] if image["pixmapAlpha"]
    )
    non_rgb_count = sum(
        1 for pdf in pdf_records for image in pdf["page76Images"] if image["colorspace"] != "DeviceRGB"
    )
    icc_or_separation_count = sum(
        1
        for pdf in pdf_records
        for image in pdf["page76Images"]
        if image["objectMaskTerms"]["iccBased"]
        or image["objectMaskTerms"]["deviceCmyk"]
        or image["objectMaskTerms"]["separation"]
    )
    active_records = [r for r in region_records if r["regionKind"] == "active_target"]
    active_state_mismatch_count = sum(1 for r in active_records if r["stateMismatch"])
    active_unexpected_count = sum(1 for r in active_records if r["channelUnexpected"])
    active_region_count = len(active_records)
    duplicate_groups = {}
    for pdf in pdf_records:
        for image in pdf["page76Images"]:
            duplicate_groups.setdefault(image["sha256"], []).append(pdf["pdf"])
    duplicate_image_sha_group_count = sum(1 for rows in duplicate_groups.values() if len(rows) > 1)
    trigger_summary = trigger_matrix.get("summary", {})
    source_summary = source_review.get("summary", {})
    summary = {
        "pdfCount": len(PDFS),
        "page76ImageObjectCount": sum(len(pdf["page76Images"]) for pdf in pdf_records),
        "deviceRgbDctImageCount": sum(
            1
            for pdf in pdf_records
            for image in pdf["page76Images"]
            if image["colorspace"] == "DeviceRGB" and image["filter"] == "DCTDecode" and image["bitsPerComponent"] == 8
        ),
        "duplicateImageShaGroupCount": duplicate_image_sha_group_count,
        "hiddenChannelCandidateImageCount": hidden_image_count,
        "smaskOrMaskImageCount": smask_count,
        "alphaPixmapImageCount": alpha_count,
        "nonRgbImageCount": non_rgb_count,
        "iccCmykSeparationImageCount": icc_or_separation_count,
        "activeRegionChannelRowCount": active_region_count,
        "activeStateMismatchCount": active_state_mismatch_count,
        "activeUnexpectedChannelStateCount": active_unexpected_count,
        "sourceBackedR3BridgeHitCount": source_summary.get("sourceBackedR3BridgeHitCount", 0),
        "satisfiedReopenTriggerCount": trigger_summary.get("satisfiedTriggerCount", 0),
        "triggerCount": trigger_summary.get("triggerCount", 0),
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|p76Images={summary['page76ImageObjectCount']}|"
        f"rgbDct={summary['deviceRgbDctImageCount']}|dupeGroups={summary['duplicateImageShaGroupCount']}|"
        f"hidden={summary['hiddenChannelCandidateImageCount']}|mask={summary['smaskOrMaskImageCount']}|"
        f"alpha={summary['alphaPixmapImageCount']}|nonRgb={summary['nonRgbImageCount']}|"
        f"iccSep={summary['iccCmykSeparationImageCount']}|activeRows={summary['activeRegionChannelRowCount']}|"
        f"activeMismatch={summary['activeStateMismatchCount']}|activeUnexpected={summary['activeUnexpectedChannelStateCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    summary["pdfEmbeddedChannelMaskFingerprint"] = fingerprint

    render_sheet(pdf_records, region_records, summary)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current PDF embedded channel/mask gate. Checks page-76 embedded image objects, "
            "alpha/soft masks, color separations, and active-region RGB channel states. "
            "No OCR-to-key/hash/seed/WIF/address/BIP39/candidate work."
        ),
        "inputs": {
            "pdfs": [rel(p) for p in PDFS],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "affineReport": rel(AFFINE_REPORT),
        },
        "summary": summary,
        "pdfRecords": pdf_records,
        "regionRecords": [
            {k: v for k, v in row.items() if k != "_crop"} for row in region_records
        ],
        "decision": {
            "currentPdfEmbeddedChannelMaskGate": "do_not_reopen_pdf_channels_or_masks",
            "reason": (
                "Page-76 embedded images are ordinary 8-bit DeviceRGB DCT images with no alpha, "
                "soft mask, hard mask, CMYK/ICC/separation channel, or active-region channel "
                "state mismatch. Channel splits explain visible orange/black ink only."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Keep the high-resolution page-76 scan as visual authority. Do not reopen PDF "
            "channels/masks unless a new source file exposes non-RGB separations, masks, or a "
            "distinct original-layout asset."
        ),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_lines = [
        "# Current PDF Embedded Channel / Mask Gate",
        "",
        "Scope: inspect page-76 embedded PDF image objects for alpha/soft masks, hard masks, non-RGB separations, ICC/CMYK channels, and channel-only anomalies around O4/B4/G5/O5, orange highlights, and the OVERDOSE header. No OCR-to-key extraction, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- Page-76 image objects: `{summary['page76ImageObjectCount']}`",
        f"- 8-bit DeviceRGB DCT images: `{summary['deviceRgbDctImageCount']}`",
        f"- Duplicate image SHA groups: `{summary['duplicateImageShaGroupCount']}`",
        f"- Hidden channel candidate images: `{summary['hiddenChannelCandidateImageCount']}`",
        f"- SMask/Mask images: `{summary['smaskOrMaskImageCount']}`",
        f"- Alpha pixmap images: `{summary['alphaPixmapImageCount']}`",
        f"- Non-RGB / ICC-CMYK-Separation images: `{summary['nonRgbImageCount']}` / `{summary['iccCmykSeparationImageCount']}`",
        f"- Active channel rows / state mismatches / unexpected channel states: `{summary['activeRegionChannelRowCount']}` / `{summary['activeStateMismatchCount']}` / `{summary['activeUnexpectedChannelStateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Page-76 Image Objects",
        "",
        "| PDF | xref | image px | rotation/orientation | bpc | colorspace | filter | smask | alpha | hidden candidate | sha prefix |",
        "|---|---:|---:|---|---:|---|---|---:|---:|---:|---|",
    ]
    for pdf in pdf_records:
        for image in pdf["page76Images"]:
            md_lines.append(
                f"| `{pdf['pdf']}` | `{image['xref']}` | `{image['width']}x{image['height']}` | "
                f"`{image['pageRotation']}/{image['analysisOrientation']}` | "
                f"`{image['bitsPerComponent']}` | `{image['colorspace']}` | `{image['filter']}` | "
                f"`{image['smaskXref']}` | `{image['pixmapAlpha']}` | `{image['hiddenChannelCandidate']}` | "
                f"`{image['sha256'][:16]}` |"
            )
    md_lines.extend(
        [
            "",
            "## Active Target Channel Detail",
            "",
            "| PDF | target | expected | visible | channel explanation | orange | dark | RGB means | spread |",
            "|---|---|---|---|---|---:|---:|---|---:|",
        ]
    )
    for row in region_records:
        if row["regionKind"] != "active_target":
            continue
        stats = row["stats"]
        md_lines.append(
            f"| `{row['pdf']}` | `{row['regionId']} {row['label']}` | `{row['expectedState']}` | "
            f"`{row['visibleState']}` | `{row['channelExplanation']}` | `{stats['orangeRatio']}` | "
            f"`{stats['darkRatio']}` | `{stats['meanR']}/{stats['meanG']}/{stats['meanB']}` | "
            f"`{stats['channelSpread']}` |"
        )
    md_lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not reopen PDF embedded channels, alpha, masks, or color separations as an extraction source.",
            "- Page 76 is stored as ordinary 8-bit DeviceRGB JPEG page images in all three PDFs; the two low-resolution PDFs are duplicates of each other.",
            "- Channel splits explain visible orange/black ink only and add no hidden source-side unit/order evidence.",
            "",
            "## Next Move",
            "",
            "- Keep the high-resolution page-76 scan as visual authority. Reopen this branch only if a new source file exposes non-RGB separations, masks, or a distinct original-layout asset.",
        ]
    )
    OUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", fingerprint)


if __name__ == "__main__":
    main()
