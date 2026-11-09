#!/usr/bin/env python3
"""Audit visible PDF header/footer band sequence around page 76.

This bounded visual pass renders the current PDF pages as displayed, crops the
top and bottom bands for article pages 73-80, and checks whether page 76's
visible OVERDOSE/header layout behaves like a unique extraction selector. It
does not derive keys, generate candidates, hash to keys, inspect WIFs/addresses,
check BIP39, or brute force anything.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_visual_header_footer_band_sequence_gate.json"
OUT_MD = OUT / "current_pdf_visual_header_footer_band_sequence_gate.md"
OUT_SHEET = OUT / "current_pdf_visual_header_footer_band_sequence_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
OCR_PAGE_HEADER_SEQUENCE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate/"
    "current_pdf_ocr_page_header_sequence_gate.json"
)

ARTICLE_PAGE_START = 73
ARTICLE_PAGE_END = 80
HEADER_FRAC = 0.14
FOOTER_FRAC = 0.14
BAND_COMPARE_SIZE = (640, 120)
VISUAL_MAD_NEAR_THRESHOLD = 35.0


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


def render_page_image(page: fitz.Page) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    mode = "RGB" if pix.n >= 3 else "L"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    return img.convert("RGB")


def largest_embedded_image_meta(doc: fitz.Document, page_index: int) -> dict[str, Any]:
    best: dict[str, Any] = {}
    for image in doc[page_index].get_images(full=True):
        xref = int(image[0])
        try:
            extracted = doc.extract_image(xref)
            pil = Image.open(io.BytesIO(extracted["image"]))
        except Exception:
            continue
        area = pil.width * pil.height
        if area > int(best.get("area", -1)):
            best = {
                "xref": xref,
                "width": int(pil.width),
                "height": int(pil.height),
                "area": int(area),
                "ext": str(extracted.get("ext", "")),
            }
    return best


def crop_band(img: Image.Image, band: str) -> Image.Image:
    width, height = img.size
    if band == "top":
        box = (0, 0, width, max(1, int(height * HEADER_FRAC)))
    elif band == "bottom":
        box = (0, min(height - 1, int(height * (1 - FOOTER_FRAC))), width, height)
    else:
        raise ValueError(f"unknown band: {band}")
    return img.crop(box)


def compare_array(img: Image.Image) -> np.ndarray:
    return np.asarray(img.resize(BAND_COMPARE_SIZE).convert("RGB"), dtype=np.float32)


def band_metrics(arr: np.ndarray) -> dict[str, Any]:
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    lum = (r + g + b) / 3.0
    dark = lum < 170
    black = lum < 75
    orange = (r > 135) & (g > 45) & (g < 215) & (b < 165) & (r > g + 12) & (r > b + 35)
    white = lum > 235
    dx = np.abs(np.diff(lum, axis=1))
    dy = np.abs(np.diff(lum, axis=0))
    edge_ratio = float(((dx > 28).mean() + (dy > 28).mean()) / 2.0)
    return {
        "meanLum": round(float(lum.mean()), 4),
        "darkRatio": round(float(dark.mean()), 6),
        "blackRatio": round(float(black.mean()), 6),
        "orangeRatio": round(float(orange.mean()), 6),
        "whiteRatio": round(float(white.mean()), 6),
        "edgeRatio": round(edge_ratio, 6),
        "signature": (
            f"D{int(float(dark.mean()) * 1000):03d}-"
            f"K{int(float(black.mean()) * 1000):03d}-"
            f"O{int(float(orange.mean()) * 1000):03d}-"
            f"E{int(edge_ratio * 1000):03d}-"
            f"L{int(float(lum.mean())):03d}"
        ),
    }


def inspect_pdf(pdf_path: Path) -> dict[str, Any]:
    page_rows: list[dict[str, Any]] = []
    band_rows: list[dict[str, Any]] = []
    band_arrays: dict[tuple[int, str], np.ndarray] = {}
    band_images: dict[tuple[int, str], Image.Image] = {}
    with fitz.open(pdf_path) as doc:
        page_limit = min(len(doc), ARTICLE_PAGE_END - ARTICLE_PAGE_START + 1)
        for page_index in range(page_limit):
            article_page = ARTICLE_PAGE_START + page_index
            page = doc[page_index]
            rendered = render_page_image(page)
            image_meta = largest_embedded_image_meta(doc, page_index)
            page_rows.append(
                {
                    "pdf": rel(pdf_path),
                    "pdfPage": page_index + 1,
                    "articlePage": article_page,
                    "pageRotation": int(page.rotation),
                    "renderedSize": [int(rendered.width), int(rendered.height)],
                    "largestEmbeddedImage": image_meta,
                }
            )
            for band in ["top", "bottom"]:
                band_img = crop_band(rendered, band)
                arr = compare_array(band_img)
                band_arrays[(article_page, band)] = arr
                band_images[(article_page, band)] = band_img.copy()
                metrics = band_metrics(arr)
                if band == "top":
                    box = [0, 0, rendered.width, int(rendered.height * HEADER_FRAC)]
                else:
                    box = [
                        0,
                        int(rendered.height * (1 - FOOTER_FRAC)),
                        rendered.width,
                        rendered.height,
                    ]
                band_rows.append(
                    {
                        "pdf": rel(pdf_path),
                        "pdfPage": page_index + 1,
                        "articlePage": article_page,
                        "band": band,
                        "bandBoxPx": [int(v) for v in box],
                        **metrics,
                    }
                )
    return {
        "pdf": rel(pdf_path),
        "pageCount": len(page_rows),
        "pageRows": page_rows,
        "bandRows": band_rows,
        "_bandArrays": band_arrays,
        "_bandImages": band_images,
    }


def ocr_overdose_start_pages(ocr_report: dict[str, Any], pdf: str) -> list[int]:
    pages: list[int] = []
    for record in ocr_report.get("records", []):
        if record.get("pdf") != pdf:
            continue
        for row in record.get("pageRows", []):
            if row.get("startsWithOverdose"):
                pages.append(int(row.get("articlePage")))
    return pages


def compare_page76_bands(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    arrays = record["_bandArrays"]
    for band in ["top", "bottom"]:
        base = arrays.get((76, band))
        if base is None:
            continue
        for (article_page, other_band), arr in arrays.items():
            if other_band != band:
                continue
            mad = float(np.mean(np.abs(base - arr)))
            rows.append(
                {
                    "pdf": record["pdf"],
                    "band": band,
                    "baseArticlePage": 76,
                    "compareArticlePage": int(article_page),
                    "meanAbsDiff": round(mad, 4),
                    "nearByMadThreshold": bool(
                        article_page != 76 and mad <= VISUAL_MAD_NEAR_THRESHOLD
                    ),
                    "selfComparison": bool(article_page == 76),
                }
            )
    return sorted(rows, key=lambda row: (row["pdf"], row["band"], row["meanAbsDiff"]))


def visual_summary(records: list[dict[str, Any]], comparisons: list[dict[str, Any]], ocr_report: dict[str, Any], reopen: dict[str, Any]) -> dict[str, Any]:
    reopen_summary = reopen.get("summary", {})
    pdf_count = len(records)
    page_rows_checked = sum(record["pageCount"] for record in records)
    band_rows_checked = sum(len(record["bandRows"]) for record in records)
    ocr_overdose_rows = []
    pdf_summaries = []
    page76_top_near = []
    page76_bottom_near = []
    for record in records:
        pdf = record["pdf"]
        overdose_pages = ocr_overdose_start_pages(ocr_report, pdf)
        ocr_overdose_rows.extend({"pdf": pdf, "articlePage": page} for page in overdose_pages)
        top_near = [
            row
            for row in comparisons
            if row["pdf"] == pdf and row["band"] == "top" and row["nearByMadThreshold"]
        ]
        bottom_near = [
            row
            for row in comparisons
            if row["pdf"] == pdf and row["band"] == "bottom" and row["nearByMadThreshold"]
        ]
        page76_top_near.extend(top_near)
        page76_bottom_near.extend(bottom_near)
        closest_top = [
            row
            for row in comparisons
            if row["pdf"] == pdf and row["band"] == "top" and not row["selfComparison"]
        ][:3]
        closest_bottom = [
            row
            for row in comparisons
            if row["pdf"] == pdf and row["band"] == "bottom" and not row["selfComparison"]
        ][:3]
        p76_top = next(
            row
            for row in record["bandRows"]
            if row["articlePage"] == 76 and row["band"] == "top"
        )
        p76_bottom = next(
            row
            for row in record["bandRows"]
            if row["articlePage"] == 76 and row["band"] == "bottom"
        )
        pdf_summaries.append(
            {
                "pdf": pdf,
                "pageCount": record["pageCount"],
                "ocrOverdoseStartPages": overdose_pages,
                "page76TopNearOtherCount": len(top_near),
                "page76BottomNearOtherCount": len(bottom_near),
                "page76TopSignature": p76_top["signature"],
                "page76BottomSignature": p76_bottom["signature"],
                "closestPage76TopMatches": closest_top,
                "closestPage76BottomMatches": closest_bottom,
                "visualHeaderFooterSelectorCandidate": False,
            }
        )
    visual_candidate_count = 0
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0))
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen_summary.get("triggerCount", 0))
    fingerprint = (
        f"pdfs={pdf_count}|pages={page_rows_checked}|bands={band_rows_checked}|"
        f"p76TopNear={len(page76_top_near)}|p76BottomNear={len(page76_bottom_near)}|"
        f"ocrOverdoseStarts={len(ocr_overdose_rows)}|candidates={visual_candidate_count}|"
        f"sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": pdf_count,
        "pageRowsChecked": page_rows_checked,
        "bandRowsChecked": band_rows_checked,
        "ocrOverdoseStartRowCount": len(ocr_overdose_rows),
        "ocrOverdoseStartRows": ocr_overdose_rows,
        "page76TopNearMatchCount": len(page76_top_near),
        "page76BottomNearMatchCount": len(page76_bottom_near),
        "visualHeaderFooterSequenceCandidateCount": visual_candidate_count,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "pdfSummaries": pdf_summaries,
        "fingerprint": fingerprint,
    }


def draw_sheet(records: list[dict[str, Any]], comparisons: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2200
    height = 1500
    img = Image.new("RGB", (width, height), (10, 12, 16))
    draw = ImageDraw.Draw(img)
    title = safe_font(32)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF Visual Header/Footer Band Sequence Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Rendered top/bottom bands for article pages 73-80; page 76 similarity is compared within each PDF.",
        fill=(176, 188, 198),
        font=small,
    )
    draw.text(
        (28, 94),
        summary["fingerprint"],
        fill=(223, 174, 72),
        font=small,
    )
    thumb_w = 190
    top_h = 54
    bot_h = 54
    gap = 12
    group_h = 410
    start_y = 150
    x0 = 28
    for group_idx, record in enumerate(records):
        y = start_y + group_idx * group_h
        draw.text((x0, y), record["pdf"], fill=(235, 238, 244), font=small)
        overdose_pages = [
            page
            for page in summary["pdfSummaries"][group_idx]["ocrOverdoseStartPages"]
        ]
        draw.text(
            (x0, y + 24),
            f"OCR OVERDOSE starts: {','.join(map(str, overdose_pages)) or '-'}",
            fill=(151, 163, 175),
            font=tiny,
        )
        for i, article_page in enumerate(range(ARTICLE_PAGE_START, ARTICLE_PAGE_END + 1)):
            x = x0 + i * (thumb_w + gap)
            label_fill = (255, 190, 84) if article_page == 76 else (188, 198, 208)
            draw.text((x, y + 52), str(article_page), fill=label_fill, font=small)
            top_img = record["_bandImages"][(article_page, "top")].resize((thumb_w, top_h))
            bot_img = record["_bandImages"][(article_page, "bottom")].resize((thumb_w, bot_h))
            draw.rectangle((x - 2, y + 78, x + thumb_w + 2, y + 78 + top_h + 2), outline=(41, 48, 60))
            draw.rectangle((x - 2, y + 152, x + thumb_w + 2, y + 152 + bot_h + 2), outline=(41, 48, 60))
            img.paste(top_img, (x, y + 80))
            img.paste(bot_img, (x, y + 154))
            if article_page == 76:
                draw.rectangle(
                    (x - 4, y + 76, x + thumb_w + 4, y + 210),
                    outline=(240, 147, 55),
                    width=3,
                )
            top_comp = next(
                row
                for row in comparisons
                if row["pdf"] == record["pdf"]
                and row["band"] == "top"
                and row["compareArticlePage"] == article_page
            )
            bot_comp = next(
                row
                for row in comparisons
                if row["pdf"] == record["pdf"]
                and row["band"] == "bottom"
                and row["compareArticlePage"] == article_page
            )
            draw.text((x, y + 222), f"T {top_comp['meanAbsDiff']:.1f}", fill=(166, 178, 188), font=tiny)
            draw.text((x, y + 240), f"B {bot_comp['meanAbsDiff']:.1f}", fill=(166, 178, 188), font=tiny)
            top_metrics = next(
                row
                for row in record["bandRows"]
                if row["articlePage"] == article_page and row["band"] == "top"
            )
            bot_metrics = next(
                row
                for row in record["bandRows"]
                if row["articlePage"] == article_page and row["band"] == "bottom"
            )
            draw.text((x, y + 262), f"T {top_metrics['signature']}", fill=(128, 140, 150), font=tiny)
            draw.text((x, y + 280), f"B {bot_metrics['signature']}", fill=(128, 140, 150), font=tiny)
    draw.text(
        (28, height - 58),
        "MAD values are distance from page 76 in the same PDF/band. Threshold for a near non-self match: <= 35.0.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Visual Header/Footer Band Sequence Gate",
        "",
        "Scope: rendered the current PDF article pages 73-80 as displayed, cropped top and bottom page bands, and compared page 76 against neighboring page bands. This is a visible layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfVisualHeaderFooterBandSequenceGate']}`",
        f"- PDFs checked / page rows checked / band rows checked: `{summary['pdfCount']}` / `{summary['pageRowsChecked']}` / `{summary['bandRowsChecked']}`",
        f"- OCR OVERDOSE page-start rows imported from previous gate: `{summary['ocrOverdoseStartRowCount']}`",
        f"- Page-76 top-band near matches / bottom-band near matches: `{summary['page76TopNearMatchCount']}` / `{summary['page76BottomNearMatchCount']}`",
        f"- Visual header/footer sequence candidates: `{summary['visualHeaderFooterSequenceCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## PDF Summary",
        "",
        "| PDF | pages | OCR OVERDOSE starts | p76 top near others | p76 bottom near others | p76 top signature | p76 bottom signature | candidates |",
        "|---|---:|---|---:|---:|---|---|---:|",
    ]
    for row in summary["pdfSummaries"]:
        lines.append(
            "| `{pdf}` | `{pages}` | `{ocr}` | `{top}` | `{bottom}` | `{top_sig}` | `{bottom_sig}` | `0` |".format(
                pdf=row["pdf"],
                pages=row["pageCount"],
                ocr=",".join(map(str, row["ocrOverdoseStartPages"])) or "-",
                top=row["page76TopNearOtherCount"],
                bottom=row["page76BottomNearOtherCount"],
                top_sig=row["page76TopSignature"],
                bottom_sig=row["page76BottomSignature"],
            )
        )
    lines.extend(
        [
            "",
            "## Closest Page-76 Band Matches",
            "",
            "| PDF | band | closest non-self pages by MAD |",
            "|---|---|---|",
        ]
    )
    for row in summary["pdfSummaries"]:
        top = ", ".join(
            f"{match['compareArticlePage']}={match['meanAbsDiff']:.1f}"
            for match in row["closestPage76TopMatches"]
        )
        bottom = ", ".join(
            f"{match['compareArticlePage']}={match['meanAbsDiff']:.1f}"
            for match in row["closestPage76BottomMatches"]
        )
        lines.append(f"| `{row['pdf']}` | `top` | `{top or '-'}` |")
        lines.append(f"| `{row['pdf']}` | `bottom` | `{bottom or '-'}` |")
    lines.extend(
        [
            "",
            "## Band Rows",
            "",
            "| PDF | article page | band | mean lum | dark | black | orange | edge | signature |",
            "|---|---:|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for record in result["records"]:
        for row in record["bandRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{band}` | `{lum}` | `{dark}` | `{black}` | `{orange}` | `{edge}` | `{sig}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    band=row["band"],
                    lum=row["meanLum"],
                    dark=row["darkRatio"],
                    black=row["blackRatio"],
                    orange=row["orangeRatio"],
                    edge=row["edgeRatio"],
                    sig=row["signature"],
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfVisualHeaderFooterBandSequenceGate']}`.",
            "- The visible header/footer bands do not add a source-backed extraction rule. Page 76 remains a useful target/validation area, but its top/bottom band state does not supply a unit, order, or selector.",
            "- The repeated OCR `OVERDOSE` page-start rows belong to the duplicate OCR PDFs and remain context unless a separate source/provenance trigger supplies R3 wording.",
            "",
            "## Next Move",
            "",
            "- Use visual PDF band state only as registration evidence. The next best move is a direct held-to-light/source-layout comparison against any true physical scan, original layout export, or raw clue wording that names a unit/order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"_bandArrays", "_bandImages"}
    }


def main() -> None:
    ocr_report = load_json(OCR_PAGE_HEADER_SEQUENCE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    records = [inspect_pdf(pdf) for pdf in PDFS]
    comparisons = [row for record in records for row in compare_page76_bands(record)]
    summary = visual_summary(records, comparisons, ocr_report, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "articlePages": [ARTICLE_PAGE_START, ARTICLE_PAGE_END],
            "headerFraction": HEADER_FRAC,
            "footerFraction": FOOTER_FRAC,
            "compareSize": list(BAND_COMPARE_SIZE),
            "nearMadThreshold": VISUAL_MAD_NEAR_THRESHOLD,
            "method": "Render current PDFs as displayed; crop top/bottom bands; compare page 76 against same-band neighbors.",
            "excluded": [
                "OCR-to-key extraction",
                "private-key candidate generation",
                "hash-to-key checks",
                "seed/WIF/address checks",
                "BIP39 checks",
                "broad brute force",
            ],
        },
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "ocrPageHeaderSequence": rel(OCR_PAGE_HEADER_SEQUENCE),
        },
        "summary": summary,
        "comparisons": comparisons,
        "records": [public_record(record) for record in records],
        "decision": {
            "currentPdfVisualHeaderFooterBandSequenceGate": "current_pdf_visual_header_footer_band_sequence_no_selector",
            "selectorUnlocked": False,
            "reason": "Rendered header/footer bands do not add source-backed R3 unit/order evidence or a selector; page 76 is still context/validation, not extraction material.",
            "nextMove": "Use PDF visual band state as registration evidence only; reopen extraction only if a true source asset or raw clue supplies unit/order wording.",
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(records, comparisons, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")


if __name__ == "__main__":
    main()
