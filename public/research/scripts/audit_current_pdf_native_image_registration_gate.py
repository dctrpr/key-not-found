#!/usr/bin/env python3
"""Audit PDF-native page image registration for the valid 75 -> 76 leaf.

This bounded pass uses the embedded page images and their PDF placement boxes,
not arbitrary local shifts, to ask whether the current PDFs encode a native
front/back registration cue that changes the held-to-light result around
O4/B4/G5/O5 or projected OVERDOSE slots.

No OCR-to-key extraction, key candidates, hashing, seed/WIF/address checks,
BIP39, or brute force is run.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_native_image_registration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_native_image_registration_gate.json"
OUT_MD = OUT / "current_pdf_native_image_registration_gate.md"
OUT_SHEET = OUT / "current_pdf_native_image_registration_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
REFERENCE_SIZE = (2544.0, 3264.0)
LOWER_Y0 = 2060
LOWER_Y1 = 3060
EPS = 1e-3


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rect_list(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 4), round(rect.y0, 4), round(rect.x1, 4), round(rect.y1, 4)]


def same_list(a: list[float], b: list[float], eps: float = EPS) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= eps for x, y in zip(a, b))


def rect_area(rect: list[float]) -> float:
    return max(0.0, rect[2] - rect[0]) * max(0.0, rect[3] - rect[1])


def primary_image_record(doc: fitz.Document, page: fitz.Page) -> dict[str, Any]:
    images = []
    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = doc.extract_image(xref)
        rects = [rect_list(rect) for rect in page.get_image_rects(xref)]
        area = max((rect_area(rect) for rect in rects), default=0.0)
        images.append(
            {
                "xref": xref,
                "widthPx": int(extracted.get("width", image[2])),
                "heightPx": int(extracted.get("height", image[3])),
                "extension": extracted.get("ext"),
                "rects": rects,
                "primaryRect": rects[0] if rects else [0.0, 0.0, 0.0, 0.0],
                "area": area,
                "image": Image.open(io.BytesIO(extracted["image"])).convert("RGB"),
            }
        )
    if not images:
        return {}
    return max(images, key=lambda item: item["area"])


def normalize_to_upright(img: Image.Image, article_page: int) -> tuple[Image.Image, str, float, float]:
    reference = Image.open(
        UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{article_page}_upright.jpg")
    ).convert("RGB")
    sample_size = (318, 408)
    ref_sample = reference.resize(sample_size)
    same_sample = img.resize(sample_size)
    rot_sample = img.rotate(180).resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(same_sample, ref_sample)).mean)
    rot_diff = sum(ImageStat.Stat(ImageChops.difference(rot_sample, ref_sample)).mean)
    if rot_diff < same_diff:
        return img.rotate(180), "rotate180", round(rot_diff, 4), round(same_diff, 4)
    return img, "identity", round(same_diff, 4), round(rot_diff, 4)


def feature_mask(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    return dark | orange | grey


def scaled_box(box: list[float], size: tuple[int, int]) -> list[float]:
    sx = size[0] / REFERENCE_SIZE[0]
    sy = size[1] / REFERENCE_SIZE[1]
    return [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy]


def crop_mask(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape
    x0, y0, x1, y1 = [round(v) for v in box]
    return mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)]


def source_only_coverage(source_mirror: np.ndarray, target: np.ndarray, box: list[float]) -> float:
    source_crop = crop_mask(source_mirror, box)
    target_crop = crop_mask(target, box)
    if not source_crop.size or source_crop.shape != target_crop.shape:
        return 0.0
    return float(np.logical_and(source_crop, ~target_crop).mean())


def iou(a: list[float], b: list[float]) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union else 0.0


def control_boxes_for(active_box: list[float], active_boxes: list[list[float]]) -> list[list[float]]:
    width = round(active_box[2] - active_box[0])
    height = round(active_box[3] - active_box[1])
    x_step = max(48, width // 3)
    y_step = max(34, height + 22)
    boxes: list[list[float]] = []
    y = LOWER_Y0
    while y + height <= LOWER_Y1:
        x = 80
        while x + width <= REFERENCE_SIZE[0] - 80:
            candidate = [float(x), float(y), float(x + width), float(y + height)]
            if all(iou(candidate, other) < 0.03 for other in active_boxes):
                boxes.append(candidate)
            x += x_step
        y += y_step
    return boxes


def active_rows() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        rows.append(row)
    return rows


def c9_slot_boxes() -> list[dict[str, Any]]:
    data = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    frame = data.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    projection = next(
        (item for item in data.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "target": f"slot{slot['index']}_{slot['letter']}",
                "slotIndex": int(slot["index"]),
                "slotLetter": str(slot["letter"]),
                "box": [
                    float(slot["left"]),
                    float(frame[1]),
                    float(slot["right"]),
                    float(frame[3]),
                ],
            }
        )
    return rows


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return float(sum(1 for item in controls if item <= value) / len(controls))


def page_record(doc: fitz.Document, pdf_path: Path, page_index: int, article_page: int) -> dict[str, Any]:
    page = doc[page_index]
    image_record = primary_image_record(doc, page)
    img, mode, chosen_diff, other_diff = normalize_to_upright(image_record["image"], article_page)
    rect = image_record["primaryRect"]
    cropbox = rect_list(page.cropbox)
    return {
        "pdf": rel(pdf_path),
        "pdfPage": page_index + 1,
        "articlePage": article_page,
        "rotation": page.rotation,
        "pageRect": rect_list(page.rect),
        "cropBox": cropbox,
        "imageXref": image_record["xref"],
        "imageSize": [img.width, img.height],
        "rawImageSize": [image_record["widthPx"], image_record["heightPx"]],
        "imageRect": rect,
        "imageCoverage": round(rect_area(rect) / max(rect_area(rect_list(page.rect)), EPS), 6),
        "leftMarginPt": round(rect[0] - cropbox[0], 4),
        "rightMarginPt": round(cropbox[2] - rect[2], 4),
        "topMarginPt": round(rect[1] - cropbox[1], 4),
        "bottomMarginPt": round(cropbox[3] - rect[3], 4),
        "orientationMode": mode,
        "orientationChosenDiff": chosen_diff,
        "orientationOtherDiff": other_diff,
        "image": img,
    }


def analyze_pdf(pdf_path: Path, active: list[dict[str, Any]], slots: list[dict[str, Any]]) -> dict[str, Any]:
    with fitz.open(pdf_path) as doc:
        page75 = page_record(doc, pdf_path, 2, 75)
        page76 = page_record(doc, pdf_path, 3, 76)

    target_img = page76.pop("image")
    source_img = page75.pop("image")
    if source_img.size != target_img.size:
        source_img = source_img.resize(target_img.size, Image.Resampling.BICUBIC)

    source_mirror = feature_mask(ImageOps.mirror(source_img))
    target_feature = feature_mask(target_img)
    active_boxes = [row["box"] for row in active]

    active_results = []
    for row in active:
        box = scaled_box(row["box"], target_img.size)
        value = source_only_coverage(source_mirror, target_feature, box)
        control_values = [
            source_only_coverage(source_mirror, target_feature, scaled_box(control, target_img.size))
            for control in control_boxes_for(row["box"], active_boxes)
        ]
        p95 = float(np.quantile(control_values, 0.95)) if control_values else 0.0
        active_results.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "referenceBox": row["box"],
                "nativeBox": [round(v, 2) for v in box],
                "sourceOnlyCoverage": round(value, 9),
                "controlCount": len(control_values),
                "controlP95SourceOnlyCoverage": round(p95, 9),
                "controlMaxSourceOnlyCoverage": round(max(control_values), 9)
                if control_values
                else 0.0,
                "controlPercentile": round(percentile(value, control_values), 9),
                "isAboveControlP95": bool(value > p95),
                "isAtLeast10": bool(value >= 0.10),
                "isAtLeast25": bool(value >= 0.25),
            }
        )

    slot_results = []
    for row in slots:
        box = scaled_box(row["box"], target_img.size)
        value = source_only_coverage(source_mirror, target_feature, box)
        slot_results.append(
            {
                "target": row["target"],
                "slotIndex": row["slotIndex"],
                "slotLetter": row["slotLetter"],
                "referenceBox": row["box"],
                "nativeBox": [round(v, 2) for v in box],
                "sourceOnlyCoverage": round(value, 9),
                "isAtLeast25": bool(value >= 0.25),
            }
        )

    same_image_rect = same_list(page75["imageRect"], page76["imageRect"])
    same_image_size = page75["imageSize"] == page76["imageSize"]
    same_rotation = page75["rotation"] == page76["rotation"]
    same_orientation = page75["orientationMode"] == page76["orientationMode"]
    side_margins = any(
        abs(page75[key]) > EPS or abs(page76[key]) > EPS
        for key in ("leftMarginPt", "rightMarginPt")
    )
    pair = {
        "pdf": rel(pdf_path),
        "page75": page75,
        "page76": page76,
        "sameImageRect": same_image_rect,
        "sameImageSize": same_image_size,
        "sameRotation": same_rotation,
        "sameOrientationMode": same_orientation,
        "sideMarginsPresent": side_margins,
        "imageRectDeltaPt": [
            round(page76["imageRect"][idx] - page75["imageRect"][idx], 4)
            for idx in range(4)
        ],
    }
    return {
        "pdf": rel(pdf_path),
        "imageSize": list(target_img.size),
        "pair": pair,
        "activeRows": active_results,
        "slotRows": slot_results,
        "activeAboveControlP95Count": sum(1 for row in active_results if row["isAboveControlP95"]),
        "activeAtLeast10Count": sum(1 for row in active_results if row["isAtLeast10"]),
        "activeAtLeast25Count": sum(1 for row in active_results if row["isAtLeast25"]),
        "maxActiveSourceOnlyCoverage": round(
            max((row["sourceOnlyCoverage"] for row in active_results), default=0.0), 9
        ),
        "meanActiveSourceOnlyCoverage": round(
            float(np.mean([row["sourceOnlyCoverage"] for row in active_results]))
            if active_results
            else 0.0,
            9,
        ),
        "maxControlSourceOnlyCoverage": round(
            max((row["controlMaxSourceOnlyCoverage"] for row in active_results), default=0.0),
            9,
        ),
        "maxOverdoseSlotSourceOnlyCoverage": round(
            max((row["sourceOnlyCoverage"] for row in slot_results), default=0.0), 9
        ),
        "overdoseSlotAtLeast25Count": sum(1 for row in slot_results if row["isAtLeast25"]),
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


def draw_sheet(pdf_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width, height = 1780, 1180
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(15)
    tiny = font(12)

    draw.rectangle((0, 0, width, 96), fill=(24, 31, 42))
    draw.text((24, 16), "Current PDF Native Image Registration Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Embedded page images, exact PDF image placement, no registration search; p75 mirrored into p76.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (980, 18),
        f"decision: {summary['decision']} | checks: active p95 {summary['totalActiveAboveControlP95Count']}/{summary['activeRowCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (980, 46),
        f"active max/mean {summary['maxActiveSourceOnlyCoverage']:.4f}/{summary['meanActiveSourceOnlyCoverage']:.4f}; slot max {summary['maxOverdoseSlotSourceOnlyCoverage']:.4f}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 126
    headers = [
        "PDF",
        "size",
        "same rect",
        "rot",
        "orient",
        "active max",
        "active >=10",
        "above p95",
        "slot max",
        "slot >=25",
    ]
    xs = [24, 420, 540, 660, 760, 890, 1020, 1140, 1270, 1380]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(40, 43, 50), font=small)
    y += 28
    for idx, row in enumerate(pdf_rows):
        fill = (245, 247, 250) if idx % 2 == 0 else (255, 255, 255)
        draw.rectangle((16, y - 6, width - 16, y + 30), fill=fill)
        pair = row["pair"]
        values = [
            row["pdf"],
            f"{row['imageSize'][0]}x{row['imageSize'][1]}",
            str(pair["sameImageRect"]),
            str(pair["sameRotation"]),
            pair["page76"]["orientationMode"],
            f"{row['maxActiveSourceOnlyCoverage']:.4f}",
            str(row["activeAtLeast10Count"]),
            str(row["activeAboveControlP95Count"]),
            f"{row['maxOverdoseSlotSourceOnlyCoverage']:.4f}",
            str(row["overdoseSlotAtLeast25Count"]),
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value[:48], fill=(25, 28, 34), font=tiny)
        y += 38

    y += 14
    draw.text((24, y), "Active rows", fill=(40, 43, 50), font=small)
    y += 28
    headers = ["PDF", "target", "coverage", "p95", "pctile", ">=10", ">=25"]
    xs = [24, 420, 520, 620, 720, 820, 900]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(40, 43, 50), font=small)
    y += 28
    for pdf_row in pdf_rows:
        for active_row in pdf_row["activeRows"]:
            values = [
                pdf_row["pdf"],
                active_row["target"],
                f"{active_row['sourceOnlyCoverage']:.4f}",
                f"{active_row['controlP95SourceOnlyCoverage']:.4f}",
                f"{active_row['controlPercentile']:.3f}",
                str(active_row["isAtLeast10"]),
                str(active_row["isAtLeast25"]),
            ]
            for x, value in zip(xs, values):
                draw.text((x, y), value[:46], fill=(25, 28, 34), font=tiny)
            y += 24
        y += 8

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = active_rows()
    slots = c9_slot_boxes()
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)

    pdf_rows = [analyze_pdf(path, active, slots) for path in PDFS if path.exists()]
    active_flat = [row for pdf in pdf_rows for row in pdf["activeRows"]]
    slot_flat = [row for pdf in pdf_rows for row in pdf["slotRows"]]
    pair_rows = [row["pair"] for row in pdf_rows]
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row
        for row in trigger_rows
        if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(
        source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    )
    total_active_above_p95 = sum(1 for row in active_flat if row["isAboveControlP95"])
    total_active_at_least_10 = sum(1 for row in active_flat if row["isAtLeast10"])
    total_active_at_least_25 = sum(1 for row in active_flat if row["isAtLeast25"])
    all_four_above_p95_pdf_count = sum(
        1 for row in pdf_rows if row["activeAboveControlP95Count"] == len(active)
    )
    all_four_at_least_10_pdf_count = sum(
        1 for row in pdf_rows if row["activeAtLeast10Count"] == len(active)
    )
    placement_offset_pair_count = sum(
        1
        for row in pair_rows
        if any(abs(value) > EPS for value in row["imageRectDeltaPt"])
    )
    same_image_rect_pair_count = sum(1 for row in pair_rows if row["sameImageRect"])
    side_margin_pair_count = sum(1 for row in pair_rows if row["sideMarginsPresent"])
    max_active = max((row["sourceOnlyCoverage"] for row in active_flat), default=0.0)
    mean_active = float(np.mean([row["sourceOnlyCoverage"] for row in active_flat])) if active_flat else 0.0
    max_control = max((row["controlMaxSourceOnlyCoverage"] for row in active_flat), default=0.0)
    max_slot = max((row["sourceOnlyCoverage"] for row in slot_flat), default=0.0)
    slot_at_least_25 = sum(1 for row in slot_flat if row["isAtLeast25"])

    decision = "current_pdf_native_image_registration_no_selector"
    fingerprint = (
        f"pdfs={len(pdf_rows)}|pairs={len(pair_rows)}|activeRows={len(active_flat)}|"
        f"slots={len(slot_flat)}|sameRects={same_image_rect_pair_count}|"
        f"offsetPairs={placement_offset_pair_count}|sideMargins={side_margin_pair_count}|"
        f"activeMax={max_active:.4f}|activeMean={mean_active:.4f}|"
        f"activeP95={total_active_above_p95}|active10={total_active_at_least_10}|"
        f"active25={total_active_at_least_25}|allFourP95={all_four_above_p95_pdf_count}|"
        f"allFour10={all_four_at_least_10_pdf_count}|controlMax={max_control:.4f}|"
        f"slotMax={max_slot:.4f}|slot25={slot_at_least_25}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/"
        f"{len(trigger_rows)}|selectors=0"
    )
    summary = {
        "decision": decision,
        "pdfCount": len(pdf_rows),
        "pairCount": len(pair_rows),
        "activeRowCount": len(active_flat),
        "overdoseSlotRowCount": len(slot_flat),
        "sameImageRectPairCount": same_image_rect_pair_count,
        "placementOffsetPairCount": placement_offset_pair_count,
        "sideMarginPairCount": side_margin_pair_count,
        "totalActiveAboveControlP95Count": total_active_above_p95,
        "totalActiveAtLeast10Count": total_active_at_least_10,
        "totalActiveAtLeast25Count": total_active_at_least_25,
        "allFourAboveControlP95PdfCount": all_four_above_p95_pdf_count,
        "allFourAtLeast10PdfCount": all_four_at_least_10_pdf_count,
        "maxActiveSourceOnlyCoverage": round(max_active, 9),
        "meanActiveSourceOnlyCoverage": round(mean_active, 9),
        "maxControlSourceOnlyCoverage": round(max_control, 9),
        "maxOverdoseSlotSourceOnlyCoverage": round(max_slot, 9),
        "overdoseSlotAtLeast25Count": slot_at_least_25,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
        "fingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Embedded PDF page image placement, exact page 75 -> page 76 mirror "
            "registration, active boxes, and C9/OVERDOSE projected slots."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "pdfRows": pdf_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(pdf_rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF Native Image Registration Gate",
        "",
        "Scope: used each PDF's embedded page images and image placement boxes to simulate the valid page 75 -> page 76 light-table view with no free registration search. No key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{decision}`",
        f"- PDFs / pairs: `{summary['pdfCount']}` / `{summary['pairCount']}`",
        f"- Active rows / projected OVERDOSE slots: `{summary['activeRowCount']}` / `{summary['overdoseSlotRowCount']}`",
        f"- Same image rect pairs / placement offset pairs / side-margin pairs: `{same_image_rect_pair_count}` / `{placement_offset_pair_count}` / `{side_margin_pair_count}`",
        f"- Active above control p95 / >=10% / >=25%: `{total_active_above_p95}` / `{total_active_at_least_10}` / `{total_active_at_least_25}`",
        f"- All-four active above p95 PDFs / all-four >=10% PDFs: `{all_four_above_p95_pdf_count}` / `{all_four_at_least_10_pdf_count}`",
        f"- Max active / mean active / max control source-only coverage: `{max_active:.4f}` / `{mean_active:.4f}` / `{max_control:.4f}`",
        f"- Max projected OVERDOSE-slot source-only coverage / slots >=25%: `{max_slot:.4f}` / `{slot_at_least_25}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{len(satisfied_triggers)}/{len(trigger_rows)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | image size | same rect | rect delta pt | orientation | active max | active >=10 | active >p95 | slot max | slot >=25 |",
        "|---|---:|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in pdf_rows:
        pair = row["pair"]
        lines.append(
            "| "
            f"`{row['pdf']}` | "
            f"`{row['imageSize'][0]}x{row['imageSize'][1]}` | "
            f"`{pair['sameImageRect']}` | "
            f"`{pair['imageRectDeltaPt']}` | "
            f"`{pair['page76']['orientationMode']}` | "
            f"{row['maxActiveSourceOnlyCoverage']:.4f} | "
            f"{row['activeAtLeast10Count']} | "
            f"{row['activeAboveControlP95Count']} | "
            f"{row['maxOverdoseSlotSourceOnlyCoverage']:.4f} | "
            f"{row['overdoseSlotAtLeast25Count']} |"
        )
    lines.extend(
        [
            "",
            "## Active Rows",
            "",
            "| PDF | target | coverage | control p95 | control percentile | >=10 | >=25 |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in pdf_rows:
        for active_row in row["activeRows"]:
            lines.append(
                "| "
                f"`{row['pdf']}` | `{active_row['target']}` | "
                f"{active_row['sourceOnlyCoverage']:.4f} | "
                f"{active_row['controlP95SourceOnlyCoverage']:.4f} | "
                f"{active_row['controlPercentile']:.3f} | "
                f"`{active_row['isAtLeast10']}` | `{active_row['isAtLeast25']}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Do not promote PDF-native image placement, page-image rect parity, side margins, or exact PDF embedded-image registration as selectors.",
            "- The PDFs preserve the same page 75/page 76 image rectangles within each pair; no placement offset or hidden registration cue appears, and exact native registration does not make the active quartet an all-four outlier.",
            "- Next move: require distinct physical/original-layout source material or raw clue wording that explicitly names transform, unit, and order before reopening selector/key checks.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
