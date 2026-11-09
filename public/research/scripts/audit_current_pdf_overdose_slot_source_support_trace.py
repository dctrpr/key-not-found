#!/usr/bin/env python3
"""Check whether PDF-native carriers reproduce the OVERDOSE OSE source run.

The current-scan OVERDOSE slot trace found a real source-supported OSE run under
the valid 75 -> 76 mirror, but it mapped to ordinary page-75 prose. This bounded
pass repeats that slot-source partition on current PDF carriers (visible render
and embedded page-image canvas) to see whether the run is stable in the original
PDF layout/render surface or scan-specific.

No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address
checks, BIP39 checks, or broad brute force is run.
"""

from __future__ import annotations

import io
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_slot_source_support_trace.json"
OUT_MD = OUT / "current_pdf_overdose_slot_source_support_trace.md"
OUT_SHEET = OUT / "current_pdf_overdose_slot_source_support_trace_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
CURRENT_SCAN_SLOT_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace/"
    "current_scan_overdose_slot_source_support_trace.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PDF_PAGE_INDEX = {75: 2, 76: 3}
REFERENCE_SIZE = (2544, 3264)
RENDER_ZOOM = 4
SOURCE_INK_LUMA_THRESHOLD = 238.0
TARGET_INK_LUMA_THRESHOLD = 238.0
AVERAGE_ALPHA = 0.70
HIGH_SOURCE_SHARE_THRESHOLD = 0.50

STRICT_INSTRUCTION_TERMS = {
    "above",
    "below",
    "bold",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "edges",
    "first",
    "fold",
    "folded",
    "font",
    "highlight",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "letters",
    "line",
    "lines",
    "mirror",
    "mirrored",
    "order",
    "outside",
    "read",
    "reads",
    "reverse",
    "right",
    "side",
    "slot",
    "take",
    "takes",
    "top",
    "window",
    "word",
    "words",
}
ACTION_ORDER_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "edges",
    "first",
    "fold",
    "folded",
    "inside",
    "key",
    "last",
    "left",
    "mirror",
    "mirrored",
    "order",
    "outside",
    "read",
    "reads",
    "reverse",
    "right",
    "side",
    "take",
    "takes",
    "top",
    "window",
}
CONTEXT_TERMS = {
    "bitcoin",
    "bitcoins",
    "bond",
    "bonds",
    "bukele",
    "dip",
    "heart",
    "imf",
    "overdose",
    "salvador",
    "sell",
    "shitcoiner",
    "volcano",
    "volcanoes",
}


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def pixmap_to_image(pix: fitz.Pixmap) -> Image.Image:
    if pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGB")


def transform_candidates(image: Image.Image) -> dict[str, Image.Image]:
    rgb = image.convert("RGB")
    return {
        "as_is": rgb,
        "rotate180": rgb.rotate(180),
        "mirror": ImageOps.mirror(rgb),
        "mirror_rotate180": ImageOps.mirror(rgb).rotate(180),
    }


def sample_score(candidate: Image.Image, reference: Image.Image) -> float:
    sample_size = (318, 408)
    cand = candidate.resize(REFERENCE_SIZE, Image.Resampling.LANCZOS).resize(sample_size)
    ref = reference.resize(sample_size)
    return float(sum(ImageStat.Stat(ImageChops.difference(cand, ref)).mean))


def best_oriented(image: Image.Image, article_page: int) -> tuple[Image.Image, str, float]:
    reference = Image.open(
        UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{article_page}_upright.jpg")
    ).convert("RGB")
    best_image = image.convert("RGB").resize(REFERENCE_SIZE, Image.Resampling.LANCZOS)
    best_mode = "as_is"
    best_score = 10**9.0
    for mode, candidate in transform_candidates(image).items():
        score = sample_score(candidate, reference)
        if score < best_score:
            best_score = score
            best_mode = mode
            best_image = candidate.resize(REFERENCE_SIZE, Image.Resampling.LANCZOS)
    return best_image, best_mode, round(best_score, 6)


def page_image_rect(doc: fitz.Document, page: fitz.Page) -> tuple[int | None, fitz.Rect, tuple[int, int]]:
    best_xref = None
    best_rect = page.rect
    best_size = (0, 0)
    best_area = -1.0
    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = doc.extract_image(xref)
        for rect in page.get_image_rects(xref):
            area = max(0.0, rect.width) * max(0.0, rect.height)
            if area > best_area:
                best_area = area
                best_xref = xref
                best_rect = rect
                best_size = (
                    int(extracted.get("width", image[2])),
                    int(extracted.get("height", image[3])),
                )
    return best_xref, best_rect, best_size


def rect_to_reference(rect: fitz.Rect, page_rect: fitz.Rect) -> tuple[int, int, int, int]:
    sx = REFERENCE_SIZE[0] / page_rect.width
    sy = REFERENCE_SIZE[1] / page_rect.height
    return (
        int(round((rect.x0 - page_rect.x0) * sx)),
        int(round((rect.y0 - page_rect.y0) * sy)),
        int(round((rect.x1 - page_rect.x0) * sx)),
        int(round((rect.y1 - page_rect.y0) * sy)),
    )


def embedded_canvas_candidates(
    raw_image: Image.Image,
    image_rect: fitz.Rect,
    page_rect: fitz.Rect,
) -> dict[str, Image.Image]:
    x0, y0, x1, y1 = rect_to_reference(image_rect, page_rect)
    x0 = max(0, min(REFERENCE_SIZE[0], x0))
    x1 = max(0, min(REFERENCE_SIZE[0], x1))
    y0 = max(0, min(REFERENCE_SIZE[1], y0))
    y1 = max(0, min(REFERENCE_SIZE[1], y1))
    out: dict[str, Image.Image] = {}
    for mode, candidate in transform_candidates(raw_image).items():
        canvas = Image.new("RGB", REFERENCE_SIZE, "white")
        if x1 > x0 and y1 > y0:
            canvas.paste(candidate.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS), (x0, y0))
        out[mode] = canvas
    return out


def best_embedded_canvas(
    raw_image: Image.Image,
    image_rect: fitz.Rect,
    page_rect: fitz.Rect,
    article_page: int,
) -> tuple[Image.Image, str, float]:
    reference = Image.open(
        UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{article_page}_upright.jpg")
    ).convert("RGB")
    best_image = Image.new("RGB", REFERENCE_SIZE, "white")
    best_mode = "as_is"
    best_score = 10**9.0
    for mode, canvas in embedded_canvas_candidates(raw_image, image_rect, page_rect).items():
        score = sample_score(canvas, reference)
        if score < best_score:
            best_score = score
            best_mode = mode
            best_image = canvas
    return best_image, best_mode, round(best_score, 6)


def page_carriers(doc: fitz.Document, article_page: int) -> dict[str, dict[str, Any]]:
    page = doc[PDF_PAGE_INDEX[article_page]]
    render_pix = page.get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM), alpha=False)
    render_img, render_mode, render_score = best_oriented(pixmap_to_image(render_pix), article_page)

    xref, image_rect, image_size = page_image_rect(doc, page)
    if xref is not None:
        raw = Image.open(io.BytesIO(doc.extract_image(xref)["image"])).convert("RGB")
        embedded_img, embedded_mode, embedded_score = best_embedded_canvas(
            raw, image_rect, page.rect, article_page
        )
    else:
        embedded_img = render_img
        embedded_mode = "render_fallback"
        embedded_score = render_score
    return {
        "render": {
            "image": render_img,
            "orientationMode": render_mode,
            "orientationScore": render_score,
            "imageXref": None,
            "rawImageSize": [render_pix.width, render_pix.height],
        },
        "embedded_canvas": {
            "image": embedded_img,
            "orientationMode": embedded_mode,
            "orientationScore": embedded_score,
            "imageXref": xref,
            "rawImageSize": list(image_size),
            "imageRect": [round(image_rect.x0, 4), round(image_rect.y0, 4), round(image_rect.x1, 4), round(image_rect.y1, 4)],
        },
    }


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def average_blend(target_arr: np.ndarray, source_arr: np.ndarray) -> np.ndarray:
    return np.clip(
        (1.0 - AVERAGE_ALPHA) * target_arr.astype(np.float32)
        + AVERAGE_ALPHA * source_arr.astype(np.float32),
        0,
        255,
    ).astype(np.uint8)


def crop_arr(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return arr[y0:y1, x0:x1, :]


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def box_area(box: list[float] | None) -> float:
    if box is None:
        return 0.0
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0


def overlap_box(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def page75_words() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    for page in data.get("pages", []):
        if int(page.get("page", -1)) != 75:
            continue
        words: list[dict[str, Any]] = []
        for word in page.get("words", []):
            text = compact(str(word.get("text") or word.get("token") or ""))
            token = clean_token(str(word.get("token") or text))
            if not text and not token:
                continue
            box = [float(v) for v in word["box"]]
            words.append(
                {
                    "id": word.get("id"),
                    "index": word.get("index"),
                    "text": text,
                    "token": token,
                    "box": box,
                    "center": center(box),
                }
            )
        return words
    return []


def words_in_region(words: list[dict[str, Any]], region: list[float]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for word in words:
        inter = overlap_box(region, word["box"])
        word_area = max(box_area(word["box"]), 1.0)
        overlap_fraction = box_area(inter) / word_area if inter else 0.0
        center_hit = in_box(word["center"], region)
        if center_hit or overlap_fraction >= 0.10:
            hits.append(
                {
                    **word,
                    "centerInRegion": center_hit,
                    "overlapFraction": round(overlap_fraction, 4),
                    "strictInstruction": word["token"] in STRICT_INSTRUCTION_TERMS,
                    "contextTerm": word["token"] in CONTEXT_TERMS,
                }
            )
    return sorted(hits, key=lambda item: (item["box"][1], item["box"][0], item.get("index") or 0))


def source_box_from_target_box(target_box: list[float], width: int, height: int) -> list[float]:
    tx0, ty0, tx1, ty1 = [float(v) for v in target_box]
    return [
        max(0.0, width - tx1),
        max(0.0, ty0),
        min(float(width), width - tx0),
        min(float(height), ty1),
    ]


def overdose_slot_boxes() -> list[dict[str, Any]]:
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    frame = [float(v) for v in c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])]
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "slotIndex": int(slot["index"]),
                "slotLetter": str(slot["letter"]),
                "slotId": f"{slot['letter']}{slot['index']}",
                "targetBox": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return rows


def measure_slot(
    slot: dict[str, Any],
    target_arr: np.ndarray,
    source_arr: np.ndarray,
    words: list[dict[str, Any]],
) -> dict[str, Any]:
    target_box = slot["targetBox"]
    mirrored_source_arr = np.asarray(ImageOps.mirror(Image.fromarray(source_arr)).convert("RGB"))
    target_crop = crop_arr(target_arr, target_box)
    source_crop = crop_arr(mirrored_source_arr, target_box)
    blend_crop = average_blend(target_crop, source_crop)
    source_ink = crop_bool(luma(mirrored_source_arr) < SOURCE_INK_LUMA_THRESHOLD, target_box)
    target_ink = crop_bool(luma(target_arr) < TARGET_INK_LUMA_THRESHOLD, target_box)
    delta = np.abs(luma(target_crop) - luma(blend_crop))
    total_delta = float(delta.sum())
    source_supported_delta = float(delta[source_ink].sum()) if source_ink.any() else 0.0
    target_only = target_ink & ~source_ink
    target_only_delta = float(delta[target_only].sum()) if target_only.any() else 0.0
    source_box = source_box_from_target_box(target_box, target_arr.shape[1], target_arr.shape[0])
    source_words = words_in_region(words, source_box)
    strict_hits = sorted({word["token"] for word in source_words if word["strictInstruction"]})
    action_hits = sorted({token for token in strict_hits if token in ACTION_ORDER_TERMS})
    unit_only_hits = sorted({token for token in strict_hits if token not in ACTION_ORDER_TERMS})
    context_hits = sorted({word["token"] for word in source_words if word["contextTerm"]})
    source_share = round(source_supported_delta / total_delta, 6) if total_delta else 0.0
    target_share = round(target_only_delta / total_delta, 6) if total_delta else 0.0
    return {
        **slot,
        "sourceBox": [round(v, 2) for v in source_box],
        "sourceSupportedDeltaShare": source_share,
        "targetOnlyDeltaShare": target_share,
        "sourceSupportedDeltaMean": round(float((delta * source_ink).mean()), 6) if delta.size else 0.0,
        "sourceInkRatio": round(float(source_ink.mean()), 6) if source_ink.size else 0.0,
        "targetInkRatio": round(float(target_ink.mean()), 6) if target_ink.size else 0.0,
        "sourceSupportedDominant": source_share >= HIGH_SOURCE_SHARE_THRESHOLD,
        "sourceWordCount": len(source_words),
        "sourceTextPreview": compact(" ".join(word["text"] for word in source_words))[:180],
        "strictInstructionHits": strict_hits,
        "actionOrderInstructionHits": action_hits,
        "unitOnlyInstructionHits": unit_only_hits,
        "contextTermHits": context_hits,
    }


def high_run(slot_rows: list[dict[str, Any]]) -> str:
    runs: list[str] = []
    current: list[dict[str, Any]] = []
    for row in sorted(slot_rows, key=lambda item: item["slotIndex"]):
        if row["sourceSupportedDominant"]:
            current.append(row)
        elif current:
            runs.append(f"{''.join(item['slotLetter'] for item in current)}@{current[0]['slotIndex']}-{current[-1]['slotIndex']}")
            current = []
    if current:
        runs.append(f"{''.join(item['slotLetter'] for item in current)}@{current[0]['slotIndex']}-{current[-1]['slotIndex']}")
    return ",".join(runs)


def analyze_pdf(pdf_path: Path, slots: list[dict[str, Any]], words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as doc:
        carriers75 = page_carriers(doc, 75)
        carriers76 = page_carriers(doc, 76)
    for carrier_name in ["render", "embedded_canvas"]:
        source_img = carriers75[carrier_name]["image"]
        target_img = carriers76[carrier_name]["image"]
        source_arr = np.asarray(source_img.convert("RGB"))
        target_arr = np.asarray(target_img.convert("RGB"))
        slot_rows = [measure_slot(slot, target_arr, source_arr, words) for slot in slots]
        slot_rows.sort(key=lambda row: row["slotIndex"])
        high_slots = [row["slotId"] for row in slot_rows if row["sourceSupportedDominant"]]
        rows.append(
            {
                "pdf": rel(pdf_path),
                "pdfName": pdf_path.name,
                "carrier": carrier_name,
                "sourceOrientationMode": carriers75[carrier_name]["orientationMode"],
                "targetOrientationMode": carriers76[carrier_name]["orientationMode"],
                "sourceOrientationScore": carriers75[carrier_name]["orientationScore"],
                "targetOrientationScore": carriers76[carrier_name]["orientationScore"],
                "sourceRawImageSize": carriers75[carrier_name].get("rawImageSize"),
                "targetRawImageSize": carriers76[carrier_name].get("rawImageSize"),
                "slotRows": slot_rows,
                "highSourceSupportedSlotIds": high_slots,
                "highSourceSupportedSlotIdsCsv": ",".join(high_slots),
                "highSourceSupportedRun": high_run(slot_rows),
                "highSourceSupportedSlotCount": len(high_slots),
                "totalSourceWordHits": sum(row["sourceWordCount"] for row in slot_rows),
                "totalStrictInstructionHits": sum(len(row["strictInstructionHits"]) for row in slot_rows),
                "totalActionOrderInstructionHits": sum(len(row["actionOrderInstructionHits"]) for row in slot_rows),
                "highSlotActionOrderInstructionHitCount": sum(
                    len(row["actionOrderInstructionHits"])
                    for row in slot_rows
                    if row["sourceSupportedDominant"]
                ),
                "unitOnlyInstructionHits": sorted({term for row in slot_rows for term in row["unitOnlyInstructionHits"]}),
                "contextTermHits": sorted({term for row in slot_rows for term in row["contextTermHits"]}),
            }
        )
    return rows


def draw_sheet(carrier_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 1220), (248, 248, 244))
    draw = ImageDraw.Draw(sheet, "RGBA")
    draw.rectangle((0, 0, 1840, 92), fill=(28, 32, 39))
    draw.text((24, 16), "PDF OVERDOSE Slot Source-Support Trace", fill="white", font=font(26, True))
    draw.text((24, 52), summary["fingerprint"], fill=(230, 230, 230), font=font(12))

    y = 122
    headers = ["pdf", "carrier", "high slots", "run", "action/order", "unit-only", "context", "orientation"]
    xs = [24, 345, 495, 635, 760, 900, 1035, 1210]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 70, 70), font=font(12, True))
    y += 24
    for row in carrier_rows:
        values = [
            row["pdfName"][:38],
            row["carrier"],
            row["highSourceSupportedSlotIdsCsv"] or "-",
            row["highSourceSupportedRun"] or "-",
            str(row["totalActionOrderInstructionHits"]),
            ",".join(row["unitOnlyInstructionHits"]) or "-",
            ",".join(row["contextTermHits"]) or "-",
            f"p75 {row['sourceOrientationMode']} / p76 {row['targetOrientationMode']}",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value), fill=(24, 31, 42), font=font(11))
        y += 22

    y += 28
    draw.text((24, y), "Slot Shares", fill=(30, 30, 30), font=font(18, True))
    y += 30
    slot_headers = ["pdf/carrier", "O0", "V1", "E2", "R3", "D4", "O5", "S6", "E7"]
    slot_xs = [24, 325, 415, 505, 595, 685, 775, 865, 955]
    for x, header in zip(slot_xs, slot_headers):
        draw.text((x, y), header, fill=(70, 70, 70), font=font(12, True))
    y += 22
    for row in carrier_rows:
        draw.text((24, y), f"{row['pdfName']} / {row['carrier']}"[:40], fill=(24, 31, 42), font=font(11))
        for x, slot in zip(slot_xs[1:], row["slotRows"]):
            color = (180, 75, 0) if slot["sourceSupportedDominant"] else (25, 25, 25)
            draw.text((x, y), f"{slot['sourceSupportedDeltaShare']:.3f}", fill=color, font=font(11))
        y += 22

    y += 34
    draw.rectangle((24, y, 1816, y + 150), outline=(210, 216, 226), width=1)
    draw.text((44, y + 18), "Decision", fill=(24, 31, 42), font=font(18, True))
    decision_lines = [
        f"Magazine render high run: {summary['magazineRenderHighRun'] or '-'}; embedded high run: {summary['magazineEmbeddedHighRun'] or '-'}.",
        f"Rows matching current scan OSE run: {summary['carrierRowsMatchingScanRun']}/{summary['carrierRowCount']}; action/order hits: {summary['totalActionOrderInstructionHits']}.",
        "PDF-native carriers reproduce the same source-band control behavior, but still provide no source-backed unit/order selector.",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((44, y + 54 + idx * 25), line, fill=(55, 65, 80), font=font(14))
    sheet.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Slot Source-Support Trace",
        "",
        "Scope: current PDF carriers only. For each PDF, the visible render and embedded page-image canvas for pages `75` and `76` were normalized to the same upright 2544x3264 page geometry, then the valid `75 -> 76` mirror was measured across projected OVERDOSE slots. No OCR-to-key extraction, candidates, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Carrier rows: `{summary['carrierRowCount']}`",
        f"- Rows matching current-scan high run: `{summary['carrierRowsMatchingScanRun']}/{summary['carrierRowCount']}`",
        f"- Magazine render/embedded high run: `{summary['magazineRenderHighRun'] or '-'}` / `{summary['magazineEmbeddedHighRun'] or '-'}`",
        f"- Total action/order instruction hits: `{summary['totalActionOrderInstructionHits']}`",
        f"- High-slot action/order instruction hits: `{summary['highSlotActionOrderInstructionHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Carrier Rows",
        "",
        "| pdf | carrier | p75 orientation | p76 orientation | high slots | high run | action/order | unit-only | context |",
        "|---|---|---|---|---|---|---:|---|---|",
    ]
    for row in result["carrierRows"]:
        lines.append(
            f"| `{row['pdfName']}` | `{row['carrier']}` | `{row['sourceOrientationMode']}` | `{row['targetOrientationMode']}` | "
            f"`{row['highSourceSupportedSlotIdsCsv'] or '-'}` | `{row['highSourceSupportedRun'] or '-'}` | "
            f"{row['totalActionOrderInstructionHits']} | `{', '.join(row['unitOnlyInstructionHits']) or '-'}` | `{', '.join(row['contextTermHits']) or '-'}` |"
        )
    lines.extend(
        [
            "",
            "## Slot Source Shares",
            "",
            "| pdf/carrier | O0 | V1 | E2 | R3 | D4 | O5 | S6 | E7 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result["carrierRows"]:
        shares = " | ".join(f"`{slot['sourceSupportedDeltaShare']}`" for slot in row["slotRows"])
        lines.append(f"| `{row['pdfName']} / {row['carrier']}` | {shares} |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`.",
            f"- Reason: {result['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    slots = overdose_slot_boxes()
    words = page75_words()
    current_scan = load_json(CURRENT_SCAN_SLOT_TRACE)
    current_scan_run = current_scan.get("summary", {}).get("highSourceSupportedRunsCsv") or "OSE@5-7"
    carrier_rows: list[dict[str, Any]] = []
    for pdf_path in PDFS:
        if pdf_path.exists():
            carrier_rows.extend(analyze_pdf(pdf_path, slots, words))

    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    magazine_render = next(
        (row for row in carrier_rows if row["pdfName"] == "magazine.pdf" and row["carrier"] == "render"),
        {},
    )
    magazine_embedded = next(
        (row for row in carrier_rows if row["pdfName"] == "magazine.pdf" and row["carrier"] == "embedded_canvas"),
        {},
    )
    match_count = sum(1 for row in carrier_rows if row["highSourceSupportedRun"] == current_scan_run)
    total_action = sum(row["totalActionOrderInstructionHits"] for row in carrier_rows)
    high_action = sum(row["highSlotActionOrderInstructionHitCount"] for row in carrier_rows)
    selector = bool(source_r3 and high_action)
    decision = (
        "pdf_overdose_slot_source_support_matches_scan_but_no_selector"
        if not selector and match_count
        else "pdf_overdose_slot_source_support_unstable_no_selector"
        if not selector
        else "pdf_overdose_slot_source_support_requires_manual_review"
    )
    reason = (
        "The byte-locked PDF render and embedded page-image canvas reproduce the same high OSE source-support run as the current scan, but action/order instruction hits remain 0 and source-backed R3 remains absent."
        if match_count
        else "The PDF-native carriers do not stably reproduce the current-scan OSE run, and they still provide no action/order instruction or source-backed R3 permission."
    )
    next_move = (
        "Treat PDF-native OVERDOSE slot source support as a stable page-75 text-band control, not an extraction path; the next useful move needs new source/clue material with unit, transform, and read order."
        if not selector
        else "Manually inspect the source-backed high-slot row against source-reopen requirements before extraction."
    )
    fingerprint = (
        f"carriers={len(carrier_rows)}|scanRun={current_scan_run}|match={match_count}/{len(carrier_rows)}|"
        f"magRender={magazine_render.get('highSourceSupportedRun') or '-'}|"
        f"magEmbedded={magazine_embedded.get('highSourceSupportedRun') or '-'}|"
        f"actionOrder={total_action}|highActionOrder={high_action}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={int(selector)}"
    )
    summary = {
        "carrierRowCount": len(carrier_rows),
        "currentScanHighRun": current_scan_run,
        "carrierRowsMatchingScanRun": match_count,
        "magazineRenderHighRun": magazine_render.get("highSourceSupportedRun"),
        "magazineEmbeddedHighRun": magazine_embedded.get("highSourceSupportedRun"),
        "totalActionOrderInstructionHits": total_action,
        "highSlotActionOrderInstructionHitCount": high_action,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector,
        "fingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "current PDF render/embedded OVERDOSE slot source-support trace; no extraction, candidates, hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "currentScanSlotTrace": rel(CURRENT_SCAN_SLOT_TRACE),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "alpha": AVERAGE_ALPHA,
            "sourceInkLumaThreshold": SOURCE_INK_LUMA_THRESHOLD,
            "targetInkLumaThreshold": TARGET_INK_LUMA_THRESHOLD,
        },
        "summary": summary,
        "carrierRows": carrier_rows,
        "decision": decision,
        "reason": reason,
        "nextMove": next_move,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(carrier_rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)
    print(decision)


if __name__ == "__main__":
    main()
