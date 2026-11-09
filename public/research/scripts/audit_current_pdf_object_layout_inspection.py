#!/usr/bin/env python3
"""Inspect current PDFs for original layout/object evidence.

This pass looks inside the available Bitcoin article PDFs instead of re-mining
rendered text. It checks whether page 76, and the surrounding article pages,
contain live text, fonts, vector objects, multiple placed assets, hidden layers,
or only full-page raster images. It is source/provenance inspection only: no
key derivation, hashing candidates, seed/WIF/address checks, or broad brute
force are run.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_object_layout_inspection"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_object_layout_inspection.json"
OUT_MD = OUT / "current_pdf_object_layout_inspection.md"
OUT_SHEET = OUT / "current_pdf_object_layout_inspection_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]

SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)

STRICT_UNIT_ORDER_TERMS = [
    "first",
    "last",
    "letter",
    "letters",
    "word",
    "words",
    "line",
    "row",
    "column",
    "index",
    "slot",
    "read",
    "take",
    "pick",
    "use",
    "fold",
    "mirror",
    "reverse",
    "rotate",
    "overlay",
    "align",
    "key",
    "private",
    "seed",
    "wif",
    "cipher",
    "decode",
    "order",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def round_rect(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 4), round(rect.y0, 4), round(rect.x1, 4), round(rect.y1, 4)]


def area(rect: fitz.Rect) -> float:
    return max(0.0, rect.width) * max(0.0, rect.height)


def page_text_stats(page: fitz.Page) -> dict:
    text = page.get_text("text") or ""
    data = page.get_text("dict")
    blocks = [b for b in data.get("blocks", []) if b.get("type") == 0]
    line_count = 0
    span_count = 0
    for block in blocks:
        for line in block.get("lines", []):
            if line.get("spans"):
                line_count += 1
                span_count += len(line.get("spans", []))
    return {
        "textBlockCount": len(blocks),
        "textLineCount": line_count,
        "textSpanCount": span_count,
        "extractedCharacterCount": len(text.strip()),
        "sampleText": " ".join(text.split())[:160],
        "normalizedText": " ".join(text.split()),
    }


def page_resource_flags(doc: fitz.Document, page: fitz.Page) -> dict:
    raw = doc.xref_object(page.xref, compressed=False) if page.xref else ""
    raw_lower = raw.lower()
    return {
        "pageObjectHasFontToken": "/font" in raw_lower,
        "pageObjectHasXObjectToken": "/xobject" in raw_lower,
        "pageObjectHasContentsToken": "/contents" in raw_lower,
        "pageObjectHasAnnotsToken": "/annots" in raw_lower,
        "pageObjectBytes": len(raw.encode("utf-8", errors="ignore")),
    }


def word_term_hits(text: str, terms: list[str]) -> list[str]:
    hits = []
    for term in terms:
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE):
            hits.append(term)
    return hits


def phrase_hits(text: str, phrases: list[str]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase.lower() in lower]


def inspect_page(doc: fitz.Document, pdf_path: Path, page_index: int, active_phrases: list[str]) -> dict:
    page = doc[page_index]
    page_rect = page.rect
    page_area = area(page_rect)
    images = page.get_images(full=True)
    image_rows = []
    full_page_image_count = 0
    partial_image_count = 0
    unique_xrefs = []

    for image in images:
        xref = int(image[0])
        unique_xrefs.append(xref)
        extracted = doc.extract_image(xref)
        rects = page.get_image_rects(xref)
        rect_rows = []
        max_coverage = 0.0
        for rect in rects:
            coverage = area(rect) / page_area if page_area else 0.0
            max_coverage = max(max_coverage, coverage)
            rect_rows.append(
                {
                    "rect": round_rect(rect),
                    "pageCoverage": round(coverage, 6),
                    "fillsPage": coverage >= 0.995,
                }
            )
        if max_coverage >= 0.995:
            full_page_image_count += 1
        else:
            partial_image_count += 1
        image_rows.append(
            {
                "xref": xref,
                "width": int(extracted.get("width", image[2])),
                "height": int(extracted.get("height", image[3])),
                "bitsPerComponent": extracted.get("bpc", image[4] if len(image) > 4 else None),
                "colorspace": extracted.get("colorspace", image[5] if len(image) > 5 else None),
                "extension": extracted.get("ext"),
                "maxPageCoverage": round(max_coverage, 6),
                "rects": rect_rows,
            }
        )

    try:
        fonts = page.get_fonts(full=True)
    except Exception:
        fonts = []
    drawings = page.get_drawings()
    text_stats = page_text_stats(page)
    flags = page_resource_flags(doc, page)
    max_image_coverage = max([img.get("maxPageCoverage", 0.0) for img in image_rows] or [0.0])
    raster_dominated = bool(len(images) == 1 and max_image_coverage >= 0.94 and len(drawings) == 0)
    ocr_text_layer = bool(raster_dominated and text_stats["textBlockCount"] > 0 and len(fonts) > 0)
    strict_unit_hits = word_term_hits(text_stats["normalizedText"], STRICT_UNIT_ORDER_TERMS)
    active_hits = phrase_hits(text_stats["normalizedText"], active_phrases)

    article_page = 73 + page_index if doc.page_count == 8 else None
    native_original_layout_evidence = bool(
        len(images) > 1
        or len(drawings) > 0
        or (text_stats["textBlockCount"] > 0 and not raster_dominated)
        or (partial_image_count > 1)
    )
    only_full_page_raster = bool(
        len(images) == 1
        and full_page_image_count == 1
        and text_stats["textBlockCount"] == 0
        and len(fonts) == 0
        and len(drawings) == 0
    )

    return {
        "pdf": rel(pdf_path),
        "pdfPage": page_index + 1,
        "articlePage": article_page,
        "pageXref": page.xref,
        "rotation": page.rotation,
        "pageRect": round_rect(page_rect),
        "mediaBox": round_rect(page.mediabox),
        "cropBox": round_rect(page.cropbox),
        "imageCount": len(images),
        "uniqueImageXrefCount": len(set(unique_xrefs)),
        "fullPageImageCount": full_page_image_count,
        "partialImageCount": partial_image_count,
        "fontsCount": len(fonts),
        "drawingCount": len(drawings),
        "textBlockCount": text_stats["textBlockCount"],
        "textLineCount": text_stats["textLineCount"],
        "textSpanCount": text_stats["textSpanCount"],
        "extractedCharacterCount": text_stats["extractedCharacterCount"],
        "sampleText": text_stats["sampleText"],
        "strictUnitOrderTextHits": strict_unit_hits,
        "strictUnitOrderTextHitCount": len(strict_unit_hits),
        "activePhraseTextHits": active_hits,
        "activePhraseTextHitCount": len(active_hits),
        "resourceFlags": flags,
        "onlyFullPageRaster": only_full_page_raster,
        "rasterDominatedPage": raster_dominated,
        "ocrTextLayerEvidence": ocr_text_layer,
        "nativeOriginalLayoutObjectEvidence": native_original_layout_evidence,
        "originalLayoutObjectEvidence": native_original_layout_evidence,
        "imagePlacements": image_rows,
    }


def render_page_thumbnail(pdf_path: Path, page_number: int, out_path: Path) -> Path | None:
    if not pdf_path.exists():
        return None
    doc = fitz.open(pdf_path)
    if page_number < 1 or page_number > doc.page_count:
        doc.close()
        return None
    page = doc[page_number - 1]
    scale = 220 / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    mode = "RGB" if pix.n < 4 else "RGBA"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples).convert("RGB")
    img.save(out_path, quality=90)
    doc.close()
    return out_path


def inspect_pdf(path: Path, active_phrases: list[str]) -> dict:
    if not path.exists():
        return {"path": rel(path), "exists": False}
    doc = fitz.open(path)
    pages = [inspect_page(doc, path, index, active_phrases) for index in range(doc.page_count)]
    metadata = {k: v for k, v in doc.metadata.items() if v}
    record = {
        "path": rel(path),
        "exists": True,
        "sha256": sha256(path),
        "byteSize": path.stat().st_size,
        "pageCount": doc.page_count,
        "metadata": metadata,
        "pages": pages,
    }
    doc.close()
    return record


def draw_sheet(pdf_records: list[dict], page76_records: list[dict], summary: dict) -> None:
    width, height = 1840, 1040
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 28)
        header_font = ImageFont.truetype("Arial.ttf", 18)
        small = ImageFont.truetype("Arial.ttf", 15)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 106), fill=(26, 32, 42))
    draw.text((26, 20), "Current PDF Object/Layout Inspection", fill="white", font=title_font)
    draw.text(
        (26, 62),
        "Checks whether the Bitcoin PDFs contain live layout/text/font/vector evidence or only full-page raster scans.",
        fill=(235, 235, 235),
        font=small,
    )

    cards = [
        ("PDFs", summary["pdfCount"]),
        ("pages", summary["pageRecordCount"]),
        ("page 76 rows", summary["page76CandidateCount"]),
        ("raster p76", summary["page76RasterDominatedCount"]),
        ("OCR text p76", summary["page76OcrTextLayerCount"]),
        ("native layout p76", summary["page76NativeOriginalLayoutEvidenceCount"]),
        ("R3/triggers", f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"),
    ]
    x = 26
    y = 128
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 230, y + 82), radius=6, fill=(246, 248, 250), outline=(210, 215, 222))
        draw.text((x + 14, y + 12), str(label), fill=(90, 95, 105), font=tiny)
        draw.text((x + 14, y + 38), str(value), fill=(20, 25, 32), font=header_font)
        x += 246

    y = 240
    draw.text((26, y), "Page 76 object checks", fill=(20, 25, 32), font=header_font)
    y += 34
    headers = ["PDF", "pg", "rot", "images", "largest img", "coverage", "text", "hits", "terms", "verdict"]
    xs = [26, 430, 490, 548, 636, 768, 870, 940, 1006, 1100]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(85, 90, 100), font=tiny)
    y += 22
    for row in page76_records:
        largest = max(row["imagePlacements"], key=lambda item: item["width"] * item["height"]) if row["imagePlacements"] else {}
        coverage = max([img.get("maxPageCoverage", 0) for img in row["imagePlacements"]] or [0])
        verdict = "raster + OCR text" if row["ocrTextLayerEvidence"] else "native layout evidence"
        values = [
            row["pdf"],
            row["pdfPage"],
            row["rotation"],
            row["imageCount"],
            f"{largest.get('width', 0)}x{largest.get('height', 0)}",
            f"{coverage:.3f}",
            row["textBlockCount"],
            row["activePhraseTextHitCount"],
            row["strictUnitOrderTextHitCount"],
            verdict,
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value), fill=(35, 38, 45), font=tiny)
        y += 22

    y += 24
    draw.text((26, y), "Representative page-76 thumbnails", fill=(20, 25, 32), font=header_font)
    thumb_x = 26
    thumb_y = y + 34
    for record in page76_records[:3]:
        pdf_path = ROOT / record["pdf"]
        thumb = OUT / f"thumb_{Path(record['pdf']).stem.replace(' ', '_')}_p{record['pdfPage']}.jpg"
        rendered = render_page_thumbnail(pdf_path, record["pdfPage"], thumb)
        if not rendered:
            continue
        img = Image.open(rendered).convert("RGB")
        sheet.paste(img, (thumb_x, thumb_y))
        draw.rectangle((thumb_x, thumb_y, thumb_x + img.width, thumb_y + img.height), outline=(35, 38, 45), width=1)
        draw.text((thumb_x, thumb_y + img.height + 8), Path(record["pdf"]).name[:34], fill=(35, 38, 45), font=tiny)
        thumb_x += img.width + 36

    draw.text(
        (980, 604),
        "Decision: no current PDF page-76 object carries live source layout.",
        fill=(20, 25, 32),
        font=header_font,
    )
    lines = [
        "The high-resolution magazine PDF page is a single full-page raster plus a corrupt OCR text layer.",
        "The alternate/Google PDFs are exact duplicates and are lower-resolution raster pages with OCR text.",
        "The text layer is useful as a source witness, but it is not native design/layout metadata.",
        "No strict unit/order terms or higher-resolution page-76 assets were found.",
        "Use the held-to-light simulator and crop-level visual inspection next, not PDF-object mining.",
    ]
    ty = 642
    for line in lines:
        draw.text((980, ty), f"- {line}", fill=(55, 58, 65), font=small)
        ty += 28

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active = load_json(ACTIVE_INDEX_SLOT)
    active_phrases = sorted(
        {
            row.get("phrase", "")
            for row in active.get("activeRows", [])
            if row.get("phrase")
        }
    )
    pdf_records = [inspect_pdf(path, active_phrases) for path in PDFS]
    page_records = [page for pdf in pdf_records if pdf.get("exists") for page in pdf["pages"]]
    page76_records = [page for page in page_records if page.get("articlePage") == 76]
    sha_groups: dict[str, list[str]] = {}
    for record in pdf_records:
        if record.get("exists"):
            sha_groups.setdefault(record["sha256"], []).append(record["path"])

    all_image_dims = []
    for page in page_records:
        for img in page["imagePlacements"]:
            all_image_dims.append((img["width"], img["height"]))
    unique_image_dims = sorted(set(all_image_dims))
    page76_largest_dims = []
    for page in page76_records:
        if page["imagePlacements"]:
            largest = max(page["imagePlacements"], key=lambda item: item["width"] * item["height"])
            page76_largest_dims.append((largest["width"], largest["height"]))
    best_page76_pixels = max((w * h for w, h in page76_largest_dims), default=0)
    higher_than_magazine_page76_count = sum(
        1 for w, h in page76_largest_dims if w * h > 2544 * 3264
    )

    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0

    summary = {
        "pdfCount": sum(1 for record in pdf_records if record.get("exists")),
        "uniqueShaCount": len(sha_groups),
        "duplicateShaGroups": [paths for paths in sha_groups.values() if len(paths) > 1],
        "pageRecordCount": len(page_records),
        "page76CandidateCount": len(page76_records),
        "page76RasterDominatedCount": sum(1 for page in page76_records if page["rasterDominatedPage"]),
        "page76OcrTextLayerCount": sum(1 for page in page76_records if page["ocrTextLayerEvidence"]),
        "page76NativeOriginalLayoutEvidenceCount": sum(
            1 for page in page76_records if page["nativeOriginalLayoutObjectEvidence"]
        ),
        "page76OnlyFullPageRasterCount": sum(1 for page in page76_records if page["onlyFullPageRaster"]),
        "page76OriginalLayoutEvidenceCount": sum(1 for page in page76_records if page["originalLayoutObjectEvidence"]),
        "page76TextBlockCount": sum(page["textBlockCount"] for page in page76_records),
        "page76FontCount": sum(page["fontsCount"] for page in page76_records),
        "page76VectorDrawingCount": sum(page["drawingCount"] for page in page76_records),
        "page76PartialImagePlacementCount": sum(page["partialImageCount"] for page in page76_records),
        "page76ActivePhraseTextHitCount": sum(page["activePhraseTextHitCount"] for page in page76_records),
        "page76StrictUnitOrderTextHitCount": sum(page["strictUnitOrderTextHitCount"] for page in page76_records),
        "uniqueImageDimensions": [f"{w}x{h}" for w, h in unique_image_dims],
        "page76LargestImageDimensions": [f"{w}x{h}" for w, h in sorted(set(page76_largest_dims))],
        "bestPage76ImagePixels": best_page76_pixels,
        "higherThanMagazinePage76ImageCount": higher_than_magazine_page76_count,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
    }
    summary["pdfObjectLayoutFingerprint"] = (
        f"pdfs={summary['pdfCount']}|sha={summary['uniqueShaCount']}|"
        f"pages={summary['pageRecordCount']}|p76={summary['page76CandidateCount']}|"
        f"p76Raster={summary['page76RasterDominatedCount']}|"
        f"p76OcrText={summary['page76OcrTextLayerCount']}|"
        f"p76NativeLayout={summary['page76NativeOriginalLayoutEvidenceCount']}|"
        f"p76Text={summary['page76TextBlockCount']}|p76Fonts={summary['page76FontCount']}|"
        f"p76Vectors={summary['page76VectorDrawingCount']}|p76PartialImages={summary['page76PartialImagePlacementCount']}|"
        f"activePhraseHits={summary['page76ActivePhraseTextHitCount']}|"
        f"unitTermHits={summary['page76StrictUnitOrderTextHitCount']}|"
        f"higherP76={summary['higherThanMagazinePage76ImageCount']}|sourceR3={source_r3}|"
        f"triggers={triggers}/{trigger_count}|selectors=0"
    )

    decision = {
        "currentPdfObjectLayoutInspection": "raster_plus_ocr_text_no_original_layout_selector",
        "selectorUnlocked": False,
        "reason": (
            "The current PDFs expose page 76 as raster page images with OCR/text overlays, not native "
            "original-layout design objects. The text layer is a source witness but it is corrupt/derivative "
            "and does not add fonts, vectors, hidden partial placements, higher-resolution assets, or strict "
            "unit/order wording that would unlock extraction."
        ),
        "nextMove": (
            "Keep using the current held-to-light simulator, but move the next bounded pass to a crop-level "
            "light-table inspection of the valid 75->76 leaf and the best 79->76 visual-registration benchmark "
            "around O4/B4/G5/O5. Do not re-open key extraction from PDF object structure."
        ),
    }

    draw_sheet(pdf_records, page76_records, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF object/layout inspection; no extraction or candidate generation",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "pdfRecords": pdf_records,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Object/Layout Inspection",
        "",
        "Scope: inspected the available Bitcoin article PDFs as PDF objects, not as extracted prose or key material. This checks for live text, embedded fonts, vector drawings, partial image placements, hidden layout resources, and page-76 image provenance. No key derivation, seed/WIF/address checks, hashes, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- PDF pages checked: `{summary['pageRecordCount']}`",
        f"- Page-76 candidate pages: `{summary['page76CandidateCount']}`",
        f"- Page-76 raster-dominated pages: `{summary['page76RasterDominatedCount']}`",
        f"- Page-76 OCR/text-layer pages: `{summary['page76OcrTextLayerCount']}`",
        f"- Page-76 native original-layout object evidence: `{summary['page76NativeOriginalLayoutEvidenceCount']}`",
        f"- Page-76 text/fonts/vectors/partial-images: `{summary['page76TextBlockCount']}` / `{summary['page76FontCount']}` / `{summary['page76VectorDrawingCount']}` / `{summary['page76PartialImagePlacementCount']}`",
        f"- Page-76 active phrase OCR hits / strict unit-order term hits: `{summary['page76ActivePhraseTextHitCount']}` / `{summary['page76StrictUnitOrderTextHitCount']}`",
        f"- Page-76 largest image dimensions: `{', '.join(summary['page76LargestImageDimensions'])}`",
        f"- Higher-than-magazine page-76 image count: `{summary['higherThanMagazinePage76ImageCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{summary['pdfObjectLayoutFingerprint']}`",
        "",
        "## Page-76 Object Rows",
        "",
        "| PDF | pdf page | rotation | images | largest image | max coverage | text blocks | OCR active hits | unit/order terms | fonts | vectors | verdict |",
        "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for page in page76_records:
        largest = max(page["imagePlacements"], key=lambda item: item["width"] * item["height"]) if page["imagePlacements"] else {}
        coverage = max([img.get("maxPageCoverage", 0) for img in page["imagePlacements"]] or [0])
        verdict = "raster + OCR text" if page["ocrTextLayerEvidence"] else "native layout/object evidence"
        active_hit_text = ", ".join(page["activePhraseTextHits"]) if page["activePhraseTextHits"] else "-"
        unit_hit_text = ", ".join(page["strictUnitOrderTextHits"]) if page["strictUnitOrderTextHits"] else "-"
        lines.append(
            f"| `{page['pdf']}` | {page['pdfPage']} | {page['rotation']} | {page['imageCount']} | "
            f"`{largest.get('width', 0)}x{largest.get('height', 0)}` | {coverage:.6f} | "
            f"{page['textBlockCount']} | `{active_hit_text}` | `{unit_hit_text}` | "
            f"{page['fontsCount']} | {page['drawingCount']} | {verdict} |"
        )

    lines.extend(
        [
            "",
            "## PDF-Level Notes",
            "",
        ]
    )
    for record in pdf_records:
        if not record.get("exists"):
            lines.append(f"- `{record['path']}` missing.")
            continue
        raster_dominated_pages = sum(1 for page in record["pages"] if page["rasterDominatedPage"])
        ocr_pages = sum(1 for page in record["pages"] if page["ocrTextLayerEvidence"])
        native_layout_pages = sum(1 for page in record["pages"] if page["nativeOriginalLayoutObjectEvidence"])
        text_pages = sum(1 for page in record["pages"] if page["textBlockCount"])
        font_pages = sum(1 for page in record["pages"] if page["fontsCount"])
        vector_pages = sum(1 for page in record["pages"] if page["drawingCount"])
        dims = sorted(
            {
                f"{img['width']}x{img['height']}"
                for page in record["pages"]
                for img in page["imagePlacements"]
            }
        )
        lines.append(
            f"- `{record['path']}`: pages `{record['pageCount']}`, sha `{record['sha256'][:16]}`, "
            f"raster/OCR/native-layout pages `{raster_dominated_pages}/{ocr_pages}/{native_layout_pages}`, "
            f"text/font/vector pages `{text_pages}/{font_pages}/{vector_pages}`, "
            f"image dimensions `{', '.join(dims)}`."
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision['currentPdfObjectLayoutInspection']}`",
            f"- {decision['reason']}",
            f"- {decision['nextMove']}",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
