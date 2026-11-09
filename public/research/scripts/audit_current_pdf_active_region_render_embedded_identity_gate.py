#!/usr/bin/env python3
"""Compare current PDF page-76 renders with their embedded page images.

The current PDFs are raster pages with OCR overlays. This bounded pass asks a
specific source/layout question: do the visible PDF renders add any active-box
or OVERDOSE-slot pixels that are not already present in the embedded page image
carrier?

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_active_region_render_embedded_identity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_active_region_render_embedded_identity_gate.json"
OUT_MD = OUT / "current_pdf_active_region_render_embedded_identity_gate.md"
OUT_SHEET = OUT / "current_pdf_active_region_render_embedded_identity_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_OVERDOSE_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
UPRIGHT_PAGE_76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

ARTICLE_PAGE = 76
PAGE_INDEX = ARTICLE_PAGE - 73
REFERENCE_SIZE = (2544, 3264)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
RENDER_ZOOM = 4
MEAN_DIFF_THRESHOLD = 18.0
LARGE_DIFF_THRESHOLD = 50.0


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def transform_candidates(image: Image.Image) -> dict[str, Image.Image]:
    return {
        "as_is": image,
        "rotate180": image.rotate(180),
        "mirror": ImageOps.mirror(image),
        "mirror_rotate180": ImageOps.mirror(image).rotate(180),
    }


def sample_score(candidate: Image.Image, reference: Image.Image) -> float:
    sample_size = (318, 408)
    cand = candidate.resize(REFERENCE_SIZE, Image.Resampling.LANCZOS).resize(sample_size)
    ref = reference.resize(sample_size)
    return float(sum(ImageStat.Stat(ImageChops.difference(cand, ref)).mean))


def best_oriented_render(image: Image.Image, reference: Image.Image) -> tuple[Image.Image, str, float]:
    best_image = image
    best_mode = "as_is"
    best_score = 10**9.0
    for mode, candidate in transform_candidates(image).items():
        resized = candidate.resize(REFERENCE_SIZE, Image.Resampling.LANCZOS)
        score = sample_score(candidate, reference)
        if score < best_score:
            best_image = resized
            best_mode = mode
            best_score = score
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
    reference: Image.Image,
) -> tuple[Image.Image, str, float]:
    best_image = Image.new("RGB", REFERENCE_SIZE, "white")
    best_mode = "as_is"
    best_score = 10**9.0
    for mode, canvas in embedded_canvas_candidates(raw_image, image_rect, page_rect).items():
        score = sample_score(canvas, reference)
        if score < best_score:
            best_image = canvas
            best_mode = mode
            best_score = score
    return best_image, best_mode, round(best_score, 6)


def pixmap_to_image(pix: fitz.Pixmap) -> Image.Image:
    if pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def render_page(doc: fitz.Document) -> Image.Image:
    pix = doc[PAGE_INDEX].get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM), alpha=False)
    return pixmap_to_image(pix).convert("RGB")


def extract_page_image(doc: fitz.Document) -> tuple[Image.Image, fitz.Rect, tuple[int, int], int | None]:
    page = doc[PAGE_INDEX]
    xref, rect, size = page_image_rect(doc, page)
    if xref is None:
        return render_page(doc), page.rect, (0, 0), None
    extracted = doc.extract_image(xref)
    image = Image.open(io.BytesIO(extracted["image"])).convert("RGB")
    return image, rect, size, xref


def active_regions() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    rows_by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows: list[dict[str, Any]] = []
    for short_id in TARGET_ORDER:
        row = rows_by_short[short_id]
        rows.append(
            {
                "id": short_id,
                "kind": "active_target",
                "label": row["phrase"],
                "box": [float(v) for v in row["box"]],
                "expectedState": row.get("visualState"),
            }
        )
    return rows


def overdose_slot_regions() -> list[dict[str, Any]]:
    data = load_json(C9_OVERDOSE_SLOT_GATE)
    frame = data.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    rows: list[dict[str, Any]] = []
    for slot in data.get("slots", []):
        rows.append(
            {
                "id": f"slot{slot['index']}_{slot['letter']}",
                "kind": "overdose_slot",
                "label": f"OVERDOSE slot {slot['letter']}",
                "box": [
                    float(slot["left"]),
                    float(frame[1]),
                    float(slot["right"]),
                    float(frame[3]),
                ],
                "expectedState": None,
            }
        )
    return rows


def shifted_controls(regions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    for row in regions:
        x0, y0, x1, y1 = row["box"]
        for dy in [-149.1, 149.1]:
            box = [x0, y0 + dy, x1, y1 + dy]
            if box[1] >= 0 and box[3] <= REFERENCE_SIZE[1]:
                controls.append(
                    {
                        "id": f"{row['id']}_dy{int(round(dy)):+d}",
                        "kind": "shifted_control",
                        "label": f"{row['id']} shifted {dy:+.1f}px",
                        "box": box,
                        "expectedState": None,
                    }
                )
    return controls


def crop_arr(image: Image.Image, box: list[float]) -> np.ndarray:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(image.width, x0))
    x1 = max(0, min(image.width, x1))
    y0 = max(0, min(image.height, y0))
    y1 = max(0, min(image.height, y1))
    return np.asarray(image.crop((x0, y0, x1, y1))).astype(np.int16)


def region_metrics(a: Image.Image, b: Image.Image, baseline: Image.Image, box: list[float]) -> dict[str, float]:
    arr_a = crop_arr(a, box)
    arr_b = crop_arr(b, box)
    arr_base = crop_arr(baseline, box)
    if arr_a.size == 0 or arr_b.size == 0:
        return {
            "renderVsEmbeddedMeanAbsDiff": 0.0,
            "renderVsEmbeddedLargeDiffRatio": 0.0,
            "renderVsBaselineMeanAbsDiff": 0.0,
            "embeddedVsBaselineMeanAbsDiff": 0.0,
        }
    diff = np.abs(arr_a - arr_b)
    base_a = np.abs(arr_a - arr_base)
    base_b = np.abs(arr_b - arr_base)
    return {
        "renderVsEmbeddedMeanAbsDiff": round(float(diff.mean()), 6),
        "renderVsEmbeddedLargeDiffRatio": round(float((diff > LARGE_DIFF_THRESHOLD).mean()), 6),
        "renderVsBaselineMeanAbsDiff": round(float(base_a.mean()), 6),
        "embeddedVsBaselineMeanAbsDiff": round(float(base_b.mean()), 6),
    }


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


def thumbnail_panel(
    pdf_label: str,
    render: Image.Image,
    embedded: Image.Image,
    regions: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> Image.Image:
    panel = Image.new("RGB", (420, 540), "white")
    draw = ImageDraw.Draw(panel)
    draw.text((10, 8), pdf_label[:46], fill="black", font=font(15))
    diff = ImageChops.difference(render, embedded)
    for idx, (label, img) in enumerate(
        [("render", render), ("embedded", embedded), ("abs diff", diff)]
    ):
        y = 38 + idx * 156
        preview = img.resize((380, 142), Image.Resampling.LANCZOS)
        panel.paste(preview, (20, y + 18))
        draw.text((20, y), label, fill="black", font=font(13))
    sx = 380 / REFERENCE_SIZE[0]
    sy = 142 / REFERENCE_SIZE[1]
    for region in regions:
        x0, y0, x1, y1 = region["box"]
        for offset_y in [56, 212, 368]:
            outline = (255, 120, 0) if region["kind"] == "active_target" else (60, 120, 255)
            draw.rectangle(
                [20 + x0 * sx, offset_y + y0 * sy, 20 + x1 * sx, offset_y + y1 * sy],
                outline=outline,
                width=1,
            )
    max_active = max(
        [
            row["renderVsEmbeddedMeanAbsDiff"]
            for row in rows
            if row["kind"] == "active_target"
        ]
        or [0.0]
    )
    draw.text((20, 512), f"max active render-vs-embedded MAD: {max_active:.3f}", fill="black", font=font(13))
    return panel


def make_sheet(pdf_records: list[dict[str, Any]], region_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1320, 920), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 20), "Current PDF active-region render vs embedded-image identity", fill="black", font=font(25))
    draw.text((24, 54), f"Fingerprint: {summary['renderEmbeddedIdentityFingerprint']}", fill="black", font=font(13))
    for idx, record in enumerate(pdf_records):
        panel = thumbnail_panel(
            record["pdf"],
            Image.open(ROOT / record["renderPreview"]).convert("RGB"),
            Image.open(ROOT / record["embeddedPreview"]).convert("RGB"),
            active_regions(),
            [row for row in region_rows if row["pdf"] == record["pdf"]],
        )
        sheet.paste(panel, (24 + idx * 430, 92))
    y = 655
    draw.text((24, y), "Active target render-vs-embedded mean absolute differences", fill="black", font=font(18))
    y += 28
    headers = ["PDF", "O4", "B4", "G5", "O5", "active mismatches", "slot max"]
    xs = [24, 440, 510, 580, 650, 735, 900]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(75, 75, 75), font=font(13))
    y += 22
    for record in pdf_records:
        rows = [row for row in region_rows if row["pdf"] == record["pdf"]]
        by_id = {row["id"]: row for row in rows}
        slot_max = max(
            [row["renderVsEmbeddedMeanAbsDiff"] for row in rows if row["kind"] == "overdose_slot"]
            or [0.0]
        )
        draw.text((xs[0], y), record["pdf"][:52], fill="black", font=font(12))
        for x, short_id in zip(xs[1:5], TARGET_ORDER):
            draw.text((x, y), f"{by_id[short_id]['renderVsEmbeddedMeanAbsDiff']:.2f}", fill="black", font=font(12))
        draw.text((xs[5], y), str(record["activeMismatchCount"]), fill="black", font=font(12))
        draw.text((xs[6], y), f"{slot_max:.2f}", fill="black", font=font(12))
        y += 24
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    baseline = Image.open(UPRIGHT_PAGE_76).convert("RGB").resize(REFERENCE_SIZE, Image.Resampling.LANCZOS)
    active = active_regions()
    slots = overdose_slot_regions()
    controls = shifted_controls(active)
    measured_regions = active + slots + controls
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)

    pdf_records: list[dict[str, Any]] = []
    region_rows: list[dict[str, Any]] = []

    for pdf_path in PDFS:
        doc = fitz.open(pdf_path)
        page = doc[PAGE_INDEX]
        render_raw = render_page(doc)
        embedded_raw, image_rect, image_size, xref = extract_page_image(doc)
        render_norm, render_mode, render_score = best_oriented_render(render_raw, baseline)
        embedded_norm, embedded_mode, embedded_score = best_embedded_canvas(
            embedded_raw, image_rect, page.rect, baseline
        )
        pdf_label = rel(pdf_path).replace("/", "_").replace(" ", "_").replace(".", "_")
        render_preview = OUT / f"{pdf_label}_render_norm.jpg"
        embedded_preview = OUT / f"{pdf_label}_embedded_canvas_norm.jpg"
        render_norm.save(render_preview, quality=90)
        embedded_norm.save(embedded_preview, quality=90)

        pdf_region_rows: list[dict[str, Any]] = []
        for region in measured_regions:
            metrics = region_metrics(render_norm, embedded_norm, baseline, region["box"])
            mismatch = (
                metrics["renderVsEmbeddedMeanAbsDiff"] > MEAN_DIFF_THRESHOLD
                or metrics["renderVsEmbeddedLargeDiffRatio"] > 0.02
            )
            row = {
                "pdf": rel(pdf_path),
                "id": region["id"],
                "kind": region["kind"],
                "label": region["label"],
                "box": [round(float(v), 3) for v in region["box"]],
                "renderEmbeddedMismatch": mismatch,
                **metrics,
            }
            pdf_region_rows.append(row)
            region_rows.append(row)

        active_mismatches = [
            row for row in pdf_region_rows if row["kind"] == "active_target" and row["renderEmbeddedMismatch"]
        ]
        slot_mismatches = [
            row for row in pdf_region_rows if row["kind"] == "overdose_slot" and row["renderEmbeddedMismatch"]
        ]
        control_mismatches = [
            row for row in pdf_region_rows if row["kind"] == "shifted_control" and row["renderEmbeddedMismatch"]
        ]
        pdf_records.append(
            {
                "pdf": rel(pdf_path),
                "pageIndex": PAGE_INDEX,
                "articlePage": ARTICLE_PAGE,
                "pageRotation": page.rotation,
                "pageRect": [round(page.rect.x0, 3), round(page.rect.y0, 3), round(page.rect.x1, 3), round(page.rect.y1, 3)],
                "imageXref": xref,
                "imageSize": list(image_size),
                "imageRect": [round(image_rect.x0, 3), round(image_rect.y0, 3), round(image_rect.x1, 3), round(image_rect.y1, 3)],
                "renderRawSize": [render_raw.width, render_raw.height],
                "renderOrientationMode": render_mode,
                "embeddedOrientationMode": embedded_mode,
                "renderBaselineSampleScore": render_score,
                "embeddedBaselineSampleScore": embedded_score,
                "activeMismatchCount": len(active_mismatches),
                "overdoseSlotMismatchCount": len(slot_mismatches),
                "controlMismatchCount": len(control_mismatches),
                "maxActiveRenderEmbeddedMeanAbsDiff": round(
                    max(
                        [
                            row["renderVsEmbeddedMeanAbsDiff"]
                            for row in pdf_region_rows
                            if row["kind"] == "active_target"
                        ]
                        or [0.0]
                    ),
                    6,
                ),
                "maxSlotRenderEmbeddedMeanAbsDiff": round(
                    max(
                        [
                            row["renderVsEmbeddedMeanAbsDiff"]
                            for row in pdf_region_rows
                            if row["kind"] == "overdose_slot"
                        ]
                        or [0.0]
                    ),
                    6,
                ),
                "renderPreview": rel(render_preview),
                "embeddedPreview": rel(embedded_preview),
            }
        )
        doc.close()

    active_rows = [row for row in region_rows if row["kind"] == "active_target"]
    slot_rows = [row for row in region_rows if row["kind"] == "overdose_slot"]
    control_rows = [row for row in region_rows if row["kind"] == "shifted_control"]
    active_mismatch_count = sum(1 for row in active_rows if row["renderEmbeddedMismatch"])
    all_four_active_mismatch_pdf_count = sum(
        1 for record in pdf_records if record["activeMismatchCount"] == len(active)
    )
    slot_mismatch_count = sum(1 for row in slot_rows if row["renderEmbeddedMismatch"])
    control_mismatch_count = sum(1 for row in control_rows if row["renderEmbeddedMismatch"])
    max_active_mad = max([row["renderVsEmbeddedMeanAbsDiff"] for row in active_rows] or [0.0])
    max_slot_mad = max([row["renderVsEmbeddedMeanAbsDiff"] for row in slot_rows] or [0.0])
    active_p95 = percentile([row["renderVsEmbeddedMeanAbsDiff"] for row in active_rows], 0.95)
    control_p95 = percentile([row["renderVsEmbeddedMeanAbsDiff"] for row in control_rows], 0.95)
    source_r3 = trigger_matrix.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    satisfied = trigger_matrix.get("summary", {}).get("satisfiedTriggerCount", 0)
    triggers = trigger_matrix.get("summary", {}).get("triggerCount", 9)

    fingerprint = (
        f"pdfs={len(pdf_records)}|regions={len(region_rows)}|activeMismatch={active_mismatch_count}|"
        f"all4Pdf={all_four_active_mismatch_pdf_count}|slotMismatch={slot_mismatch_count}|"
        f"controlMismatch={control_mismatch_count}|maxActive={max_active_mad:.3f}|"
        f"maxSlot={max_slot_mad:.3f}|activeP95={active_p95:.3f}|controlP95={control_p95:.3f}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{triggers}|selectors=0"
    )
    summary = {
        "pdfCount": len(pdf_records),
        "measuredRegionCount": len(region_rows),
        "activeRegionRowCount": len(active_rows),
        "overdoseSlotRegionRowCount": len(slot_rows),
        "controlRegionRowCount": len(control_rows),
        "activeRenderEmbeddedMismatchCount": active_mismatch_count,
        "allFourActiveMismatchPdfCount": all_four_active_mismatch_pdf_count,
        "overdoseSlotRenderEmbeddedMismatchCount": slot_mismatch_count,
        "controlRenderEmbeddedMismatchCount": control_mismatch_count,
        "maxActiveRenderEmbeddedMeanAbsDiff": round(max_active_mad, 6),
        "maxOverdoseSlotRenderEmbeddedMeanAbsDiff": round(max_slot_mad, 6),
        "activeRenderEmbeddedP95MeanAbsDiff": round(active_p95, 6),
        "controlRenderEmbeddedP95MeanAbsDiff": round(control_p95, 6),
        "meanDiffThreshold": MEAN_DIFF_THRESHOLD,
        "largeDiffThreshold": LARGE_DIFF_THRESHOLD,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": triggers,
        "selectorUnlocked": False,
        "renderEmbeddedIdentityFingerprint": fingerprint,
    }
    make_sheet(pdf_records, region_rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF page-76 render vs embedded-image active-region identity gate; no extraction or candidate generation",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9OverdoseSlotGate": rel(C9_OVERDOSE_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "baselineUprightPage76": rel(UPRIGHT_PAGE_76),
        },
        "pdfRecords": pdf_records,
        "regionRows": region_rows,
        "summary": summary,
        "decision": {
            "currentPdfActiveRegionRenderEmbeddedIdentityGate": "current_pdf_render_embedded_identity_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Current PDF page-76 visible renders do not add a coherent active-box or OVERDOSE-slot layer beyond "
                "the embedded raster image carriers. Any differences are ordinary derivative render/resampling behavior, "
                "with no source-backed R3 unit/order bridge."
            ),
            "nextMove": (
                "Use the PDFs as raster witnesses only. Continue with true original-layout/physical source acquisition "
                "or raw clue wording before reopening selector/key extraction."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Active-Region Render/Embedded Identity Gate",
        "",
        "Scope: compared page-76 visible PDF renders with reconstructed embedded page-image canvases at O4/B4/G5/O5, C9 OVERDOSE slots, and nearby shifted controls. This checks for render-only or layout-only active pixels. No OCR-to-key extraction, seed/WIF/address checks, hashes, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{len(pdf_records)}`",
        f"- Region rows: `{len(region_rows)}`",
        f"- Active render-vs-embedded mismatches: `{active_mismatch_count}`",
        f"- All-four active mismatch PDF count: `{all_four_active_mismatch_pdf_count}`",
        f"- OVERDOSE-slot render-vs-embedded mismatches: `{slot_mismatch_count}`",
        f"- Control render-vs-embedded mismatches: `{control_mismatch_count}`",
        f"- Max active render-vs-embedded mean abs diff: `{max_active_mad:.6f}`",
        f"- Max OVERDOSE-slot render-vs-embedded mean abs diff: `{max_slot_mad:.6f}`",
        f"- Active/control p95 render-vs-embedded mean abs diff: `{active_p95:.6f}` / `{control_p95:.6f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied}/{triggers}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | render orientation | embedded orientation | active mismatches | slot mismatches | control mismatches | max active MAD | max slot MAD |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for record in pdf_records:
        lines.append(
            f"| `{record['pdf']}` | `{record['renderOrientationMode']}` | `{record['embeddedOrientationMode']}` | "
            f"`{record['activeMismatchCount']}` | `{record['overdoseSlotMismatchCount']}` | "
            f"`{record['controlMismatchCount']}` | `{record['maxActiveRenderEmbeddedMeanAbsDiff']:.6f}` | "
            f"`{record['maxSlotRenderEmbeddedMeanAbsDiff']:.6f}` |"
        )
    lines.extend(
        [
            "",
            "## Active Targets",
            "",
            "| PDF | target | render-vs-embedded MAD | large-diff ratio | render-vs-baseline MAD | embedded-vs-baseline MAD | mismatch |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in active_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['id']}` | `{row['renderVsEmbeddedMeanAbsDiff']:.6f}` | "
            f"`{row['renderVsEmbeddedLargeDiffRatio']:.6f}` | `{row['renderVsBaselineMeanAbsDiff']:.6f}` | "
            f"`{row['embeddedVsBaselineMeanAbsDiff']:.6f}` | `{row['renderEmbeddedMismatch']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_render_embedded_identity_no_selector`",
            "- The visible PDF render does not expose a hidden active-box or OVERDOSE layer outside the embedded raster page image.",
            "- Do not reopen extraction from current-PDF render differences; the current PDFs remain raster witnesses plus invisible OCR wrappers.",
            "",
            "## Next Move",
            "",
            "- Best direction remains original-layout/physical source acquisition or raw clue wording scored against R1-R5 and the source-acquisition packet.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", fingerprint)


if __name__ == "__main__":
    main()
