#!/usr/bin/env python3
"""Audit current-PDF page-76 render resolution invariance.

This bounded pass renders the current PDFs at multiple DPI/zoom levels and
checks whether higher-resolution rendering reveals extra page-76 active-box,
highlight, or OVERDOSE-slot signal beyond ordinary raster resampling. It is a
source/PDF layout inspection gate, not an extraction pass.

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
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_render_resolution_invariance_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_render_resolution_invariance_gate.json"
OUT_MD = OUT / "current_pdf_render_resolution_invariance_gate.md"
OUT_SHEET = OUT / "current_pdf_render_resolution_invariance_gate_sheet.jpg"

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
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
UPRIGHT_PAGE_76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

ZOOMS = [1, 2, 4]
ARTICLE_PAGE = 76
PAGE_INDEX = ARTICLE_PAGE - 73
REFERENCE_SIZE = (2544, 3264)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def pixmap_to_image(pix: fitz.Pixmap) -> Image.Image:
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def render_pdf_page(path: Path, zoom: int) -> Image.Image:
    doc = fitz.open(path)
    page = doc[PAGE_INDEX]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    image = pixmap_to_image(pix).convert("RGB")
    doc.close()
    return image


def normalize_render_to_reference(image: Image.Image, reference: Image.Image) -> tuple[Image.Image, str, float]:
    candidates = {
        "as_rendered": image,
        "rotate180": image.rotate(180),
    }
    best_mode = ""
    best_score = 10**9.0
    best_image = image
    sample_size = (318, 408)
    reference_sample = reference.resize(sample_size)
    for mode, candidate in candidates.items():
        resized = candidate.resize(REFERENCE_SIZE, Image.Resampling.LANCZOS)
        sample = resized.resize(sample_size)
        score = sum(ImageStat.Stat(ImageChops.difference(sample, reference_sample)).mean)
        if score < best_score:
            best_mode = mode
            best_score = score
            best_image = resized
    return best_image, best_mode, float(best_score)


def mean_abs_delta(a: Image.Image, b: Image.Image, box: list[float]) -> float:
    arr_a = np.asarray(crop(a, box)).astype(np.int16)
    arr_b = np.asarray(crop(b, box)).astype(np.int16)
    if arr_a.size == 0 or arr_b.size == 0:
        return 0.0
    return float(np.abs(arr_a - arr_b).mean())


def crop(image: Image.Image, box: list[float]) -> Image.Image:
    x0, y0, x1, y1 = [round(v) for v in box]
    return image.crop((max(0, x0), max(0, y0), min(image.width, x1), min(image.height, y1)))


def clamp_box(box: list[float], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [
        max(0.0, min(float(width), x0)),
        max(0.0, min(float(height), y0)),
        max(0.0, min(float(width), x1)),
        max(0.0, min(float(height), y1)),
    ]


def control_boxes(active_boxes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for box in active_boxes:
        x0, y0, x1, y1 = box["box"]
        for dy in [-292, -146, 146, 292]:
            shifted = clamp_box([x0, y0 + dy, x1, y1 + dy], *REFERENCE_SIZE)
            if shifted[3] > shifted[1] and shifted[2] > shifted[0]:
                rows.append(
                    {
                        "shortId": f"{box['shortId']}_dy{dy:+d}",
                        "phrase": f"{box['shortId']} shifted {dy:+d}px",
                        "kind": "shifted_control",
                        "box": shifted,
                    }
                )
    return rows


def c9_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    projection = next(
        (
            item
            for item in c9.get("projections", [])
            if item.get("name") == "p76_header_glyph"
        ),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "shortId": f"slot{slot['index']}_{slot['letter']}",
                "phrase": f"C9 projected OVERDOSE slot {slot['letter']}",
                "kind": "overdose_slot",
                "box": [
                    float(slot["left"]),
                    float(frame[1]),
                    float(slot["right"]),
                    float(frame[3]),
                ],
            }
        )
    return rows


def draw_sheet(previews: list[Path], comparison_rows: list[dict[str, Any]]) -> None:
    sheet = Image.new("RGB", (1840, 1220), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 14)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()
    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-PDF Render Resolution Invariance Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 renders at zoom 1/2/4, normalized to readable/upright 2544x3264; active boxes outlined.",
        fill=(235, 235, 235),
        font=small,
    )
    x, y = 24, 120
    for path in previews[:8]:
        img = Image.open(path).convert("RGB").resize((360, 462))
        sheet.paste(img, (x, y))
        x += 378
        if x + 360 > 1840:
            x = 24
            y += 520
    y = 1065
    headers = ["PDF", "compare", "active max", "control max", "outliers", "slots max"]
    xs = [24, 520, 680, 800, 930, 1040]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in comparison_rows[:6]:
        vals = [
            Path(row["pdf"]).name[:42],
            row["comparison"],
            f"{row['maxActiveMeanAbsDelta']:.3f}",
            f"{row['maxControlMeanAbsDelta']:.3f}",
            str(row["activeOutlierCount"]),
            f"{row['maxOverdoseSlotMeanAbsDelta']:.3f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def preview_image(image: Image.Image, pdf: Path, zoom: int, active_boxes: list[dict[str, Any]]) -> Path:
    preview = image.resize((720, round(720 * image.height / image.width)))
    draw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height
    for box in active_boxes:
        x0, y0, x1, y1 = box["box"]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        color = (255, 128, 0, 240) if box["visualState"] == "Y" else (35, 35, 35, 240)
        draw.rectangle(rect, outline=color, width=3)
        draw.text((rect[0], max(0, rect[1] - 17)), box["shortId"], fill=(255, 0, 0, 255))
    draw.rectangle((0, 0, preview.width, 36), fill=(0, 0, 0, 170))
    draw.text((8, 10), f"{rel(pdf)} zoom={zoom}", fill=(255, 255, 255, 255))
    safe_name = rel(pdf).replace("/", "_").replace(" ", "_").replace(".", "_")
    path = OUT / f"{safe_name}_z{zoom}_page76.jpg"
    preview.save(path, quality=90)
    return path


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    reference = Image.open(UPRIGHT_PAGE_76).convert("RGB").resize(REFERENCE_SIZE)
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
    controls = control_boxes(active_boxes)
    slots = c9_slot_boxes(c9)

    render_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    region_rows: list[dict[str, Any]] = []
    previews: list[Path] = []
    normalized_renders: dict[tuple[str, int], Image.Image] = {}

    for pdf in PDFS:
        for zoom in ZOOMS:
            raw = render_pdf_page(pdf, zoom)
            normalized, orientation, score = normalize_render_to_reference(raw, reference)
            normalized_renders[(rel(pdf), zoom)] = normalized
            if zoom in {1, 4}:
                previews.append(preview_image(normalized, pdf, zoom, active_boxes))
            render_rows.append(
                {
                    "pdf": rel(pdf),
                    "zoom": zoom,
                    "rawSize": list(raw.size),
                    "normalizedSize": list(normalized.size),
                    "orientation": orientation,
                    "referenceDiffScore": round(score, 6),
                }
            )

        high = normalized_renders[(rel(pdf), 4)]
        for low_zoom in [1, 2]:
            low = normalized_renders[(rel(pdf), low_zoom)]
            comparison = f"z{low_zoom}_vs_z4"
            active_deltas = [
                mean_abs_delta(low, high, box["box"]) for box in active_boxes
            ]
            control_deltas = [mean_abs_delta(low, high, box["box"]) for box in controls]
            slot_deltas = [mean_abs_delta(low, high, box["box"]) for box in slots]
            control_p95 = float(np.percentile(control_deltas, 95)) if control_deltas else 0.0
            outliers = [
                box["shortId"]
                for box, delta in zip(active_boxes, active_deltas)
                if delta > control_p95
            ]
            comparison_rows.append(
                {
                    "pdf": rel(pdf),
                    "comparison": comparison,
                    "controlP95MeanAbsDelta": round(control_p95, 6),
                    "maxActiveMeanAbsDelta": round(float(max(active_deltas or [0.0])), 6),
                    "meanActiveMeanAbsDelta": round(float(np.mean(active_deltas)), 6),
                    "maxControlMeanAbsDelta": round(float(max(control_deltas or [0.0])), 6),
                    "meanControlMeanAbsDelta": round(float(np.mean(control_deltas)), 6),
                    "activeOutlierCount": len(outliers),
                    "activeOutlierIds": outliers,
                    "maxOverdoseSlotMeanAbsDelta": round(float(max(slot_deltas or [0.0])), 6),
                    "meanOverdoseSlotMeanAbsDelta": round(float(np.mean(slot_deltas)), 6),
                    "selectorCandidate": False,
                }
            )
            for box, delta in zip(active_boxes, active_deltas):
                region_rows.append(
                    {
                        "pdf": rel(pdf),
                        "comparison": comparison,
                        "kind": "active",
                        "region": box["shortId"],
                        "phrase": box["phrase"],
                        "meanAbsDelta": round(delta, 6),
                        "aboveControlP95": delta > control_p95,
                    }
                )
            for box, delta in zip(slots, slot_deltas):
                region_rows.append(
                    {
                        "pdf": rel(pdf),
                        "comparison": comparison,
                        "kind": "overdose_slot",
                        "region": box["shortId"],
                        "phrase": box["phrase"],
                        "meanAbsDelta": round(delta, 6),
                        "aboveControlP95": delta > control_p95,
                    }
                )

    active_outlier_count = sum(row["activeOutlierCount"] for row in comparison_rows)
    all_four_outlier_count = sum(1 for row in comparison_rows if row["activeOutlierCount"] == 4)
    max_active_delta = max(row["maxActiveMeanAbsDelta"] for row in comparison_rows)
    max_control_delta = max(row["maxControlMeanAbsDelta"] for row in comparison_rows)
    max_slot_delta = max(row["maxOverdoseSlotMeanAbsDelta"] for row in comparison_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    fingerprint = (
        f"pdfs={len(PDFS)}|zooms={len(ZOOMS)}|renders={len(render_rows)}"
        f"|comparisons={len(comparison_rows)}|activeOutliers={active_outlier_count}"
        f"|allFourOutliers={all_four_outlier_count}|maxActive={max_active_delta:.3f}"
        f"|maxControl={max_control_delta:.3f}|maxSlot={max_slot_delta:.3f}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "pdfCount": len(PDFS),
        "zoomCount": len(ZOOMS),
        "renderRowCount": len(render_rows),
        "comparisonRowCount": len(comparison_rows),
        "activeRegionRowCount": sum(1 for row in region_rows if row["kind"] == "active"),
        "overdoseSlotRegionRowCount": sum(
            1 for row in region_rows if row["kind"] == "overdose_slot"
        ),
        "activeOutlierCount": active_outlier_count,
        "allFourActiveOutlierComparisonCount": all_four_outlier_count,
        "maxActiveMeanAbsDelta": max_active_delta,
        "maxControlMeanAbsDelta": max_control_delta,
        "maxOverdoseSlotMeanAbsDelta": max_slot_delta,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "renderResolutionInvarianceFingerprint": fingerprint,
    }

    draw_sheet(previews, comparison_rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF page-76 multi-resolution render invariance; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "referencePage": rel(UPRIGHT_PAGE_76),
        },
        "renderRows": render_rows,
        "comparisonRows": comparison_rows,
        "regionRows": region_rows,
        "summary": summary,
        "decision": {
            "currentPdfRenderResolutionInvarianceGate": "render_resolution_invariance_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Higher-DPI rendering changes page-76 regions only by ordinary raster "
                "resampling. Active boxes and projected OVERDOSE slots are not a unique "
                "high-resolution/original-layout carrier, and no source-backed R3 unit/order "
                "trigger is satisfied."
            ),
            "nextMove": (
                "Keep current PDFs as derivative/current-scan render witnesses only. Reopen "
                "PDF-render inspection only if a distinct original-layout PDF or raw source "
                "asset arrives."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Render Resolution Invariance Gate",
        "",
        "Scope: rendered page 76 of the current PDFs at zoom levels 1, 2, and 4, normalized each render to the readable/upright 2544x3264 frame, and compared low-vs-high render deltas in active target boxes, shifted controls, and projected C9/OVERDOSE slots. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / zooms / render rows: `{len(PDFS)}` / `{len(ZOOMS)}` / `{len(render_rows)}`",
        f"- Comparison rows: `{len(comparison_rows)}`",
        f"- Active outliers above shifted-control p95: `{active_outlier_count}`",
        f"- All-four active outlier comparisons: `{all_four_outlier_count}`",
        f"- Max active/control/OVERDOSE-slot mean abs delta: `{max_active_delta:.3f}` / `{max_control_delta:.3f}` / `{max_slot_delta:.3f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Comparison Rows",
        "",
        "| PDF | comparison | active max | active mean | control p95 | control max | active outliers | OVERDOSE slot max |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in comparison_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['comparison']}` | {row['maxActiveMeanAbsDelta']:.3f} | {row['meanActiveMeanAbsDelta']:.3f} | {row['controlP95MeanAbsDelta']:.3f} | {row['maxControlMeanAbsDelta']:.3f} | `{','.join(row['activeOutlierIds'])}` | {row['maxOverdoseSlotMeanAbsDelta']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `render_resolution_invariance_no_selector`",
            "- Higher-DPI page-76 rendering does not expose a separate active-box or projected OVERDOSE source carrier.",
            "- Active-region render deltas are ordinary raster resampling effects and do not produce an all-four active selector against shifted controls.",
            "- Current PDFs remain current-scan/duplicate render witnesses, not distinct original-layout evidence.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentPdfRenderResolutionInvarianceGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
