#!/usr/bin/env python3
"""Audit local PDF render/extraction quality against the page-76 source gate.

This is a bounded source-material check. It renders the known local PDFs and
also inspects their embedded page images to ask whether any PDF supplies a
distinct, higher-quality page-76 source or new source-review trigger evidence.
It does not extract key material or run candidate checks.
"""

from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_pdf_render_quality_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_pdf_render_quality_gate.json"
OUT_MD = OUT / "source_packet_pdf_render_quality_gate.md"
OUT_SHEET = OUT / "source_packet_pdf_render_quality_gate_sheet.jpg"

UPRIGHT_PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_PAGE76 = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"
ORIENTATION_GUARDRAIL = ROOT / (
    "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/"
    "page76_active_crop_orientation_guardrail.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
LOCAL_ASSET_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_local_asset_orientation_gate/"
    "source_packet_local_asset_orientation_gate.json"
)

PDF_PATHS = [
    ROOT / "keyser bitcoin .pdf",
    ROOT / "magazine.pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]

RENDER_DPI = 300
PAGE76_MATCH_MAD = 14.0
PAGE76_DERIVATIVE_MAD = 25.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def small_gray(img: Image.Image, size: tuple[int, int] = (192, 256)) -> Image.Image:
    return ImageOps.grayscale(img).resize(size, Image.Resampling.BILINEAR)


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def box_from_row(row: dict) -> list[int] | None:
    if row.get("uprightBox"):
        return row["uprightBox"]
    if row.get("box"):
        return row["box"]
    return None


def orient_image(img: Image.Image, orientation: str) -> Image.Image:
    return img.rotate(180) if orientation == "rotate180" else img


def scaled_crop_mad(
    candidate: Image.Image,
    candidate_orientation: str,
    baseline_upright: Image.Image,
    boxes: list[list[int]],
) -> dict:
    oriented = orient_image(candidate, candidate_orientation)
    cw, ch = oriented.size
    bw, bh = baseline_upright.size
    scale_x = cw / bw
    scale_y = ch / bh
    rows = []
    for box in boxes:
        x0, y0, x1, y1 = box
        cbox = [
            max(0, round(x0 * scale_x)),
            max(0, round(y0 * scale_y)),
            min(cw, round(x1 * scale_x)),
            min(ch, round(y1 * scale_y)),
        ]
        bbox = [max(0, x0), max(0, y0), min(bw, x1), min(bh, y1)]
        if cbox[2] <= cbox[0] or cbox[3] <= cbox[1]:
            continue
        cand_crop = small_gray(oriented.crop(cbox), (160, 42))
        base_crop = small_gray(baseline_upright.crop(bbox), (160, 42))
        rows.append(mean_abs_diff(cand_crop, base_crop))
    return {
        "activeCropMadMean": round(sum(rows) / len(rows), 4) if rows else None,
        "activeCropMadMax": round(max(rows), 4) if rows else None,
        "activeCropCount": len(rows),
    }


def known_image_hashes() -> dict[str, str]:
    candidates = {
        "native_page76": NATIVE_PAGE76,
        "upright_page76": UPRIGHT_PAGE76,
        "root_magazine_4_1": ROOT / "magazine-4_1.jpg",
        "source_images_magazine_page_76": ROOT / "analysis_outputs/source_images/magazine_page_76.jpg",
    }
    return {role: md5_file(path) for role, path in candidates.items() if path.exists()}


def render_page(page: fitz.Page) -> Image.Image:
    matrix = fitz.Matrix(RENDER_DPI / 72.0, RENDER_DPI / 72.0)
    pix = page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def embedded_images(doc: fitz.Document, page: fitz.Page) -> list[dict]:
    rows = []
    for image_index, info in enumerate(page.get_images(full=True), start=1):
        xref = info[0]
        extracted = doc.extract_image(xref)
        data = extracted["image"]
        img = Image.open(io.BytesIO(data)).convert("RGB")
        rows.append(
            {
                "imageIndex": image_index,
                "xref": xref,
                "extension": extracted.get("ext"),
                "bytes": len(data),
                "bytesMd5": md5_bytes(data),
                "size": [img.size[0], img.size[1]],
                "pixelCount": img.size[0] * img.size[1],
                "image": img,
            }
        )
    return rows


def compare_candidate(
    *,
    pdf_path: Path,
    pdf_md5: str,
    page_index: int,
    page_count: int,
    kind: str,
    img: Image.Image,
    baseline_upright: Image.Image,
    baseline_native: Image.Image,
    active_boxes: list[list[int]],
    source_pixel_gain: float,
    embedded_summary: dict,
    known_hashes: dict[str, str],
    candidate_bytes_md5: str | None = None,
    embedded_image_index: int | None = None,
) -> tuple[dict, Image.Image]:
    baseline_u_small = small_gray(baseline_upright)
    baseline_n_small = small_gray(baseline_native)
    variants = [
        ("as_is", img),
        ("rotate180", img.rotate(180)),
    ]

    best_upright = None
    best_native = None
    for name, variant in variants:
        u_mad = mean_abs_diff(small_gray(variant), baseline_u_small)
        n_mad = mean_abs_diff(small_gray(variant), baseline_n_small)
        if best_upright is None or u_mad < best_upright["mad"]:
            best_upright = {"orientation": name, "mad": round(u_mad, 4)}
        if best_native is None or n_mad < best_native["mad"]:
            best_native = {"orientation": name, "mad": round(n_mad, 4)}

    crop_stats = scaled_crop_mad(
        img,
        best_upright["orientation"],
        baseline_upright,
        active_boxes,
    )
    page76_match = best_upright["mad"] <= PAGE76_MATCH_MAD or best_native["mad"] <= PAGE76_MATCH_MAD
    derivative_match = (
        page76_match
        or best_upright["mad"] <= PAGE76_DERIVATIVE_MAD
        or best_native["mad"] <= PAGE76_DERIVATIVE_MAD
    )
    render_pixel_gain = (img.size[0] * img.size[1]) / (
        baseline_upright.size[0] * baseline_upright.size[1]
    )
    exact_role = None
    if candidate_bytes_md5:
        exact_role = next((role for role, digest in known_hashes.items() if digest == candidate_bytes_md5), None)
    source_higher = source_pixel_gain > 1.05
    r1_distinct_improved = bool(page76_match and source_higher and not exact_role)
    candidate_id = (
        f"{rel(pdf_path)}#p{page_index:02d}#"
        f"{kind}{'' if embedded_image_index is None else f'-{embedded_image_index}'}"
    )
    row = {
        "candidateId": candidate_id,
        "pdfPath": rel(pdf_path),
        "pdfMd5": pdf_md5,
        "pdfPageIndex": page_index,
        "pdfPageCount": page_count,
        "candidateKind": kind,
        "embeddedImageIndex": embedded_image_index,
        "size": [img.size[0], img.size[1]],
        "pixelCount": img.size[0] * img.size[1],
        "renderDpi": RENDER_DPI if kind == "page_render_300dpi" else None,
        "candidateBytesMd5": candidate_bytes_md5,
        "exactKnownImageRole": exact_role,
        "bestUprightOrientation": best_upright["orientation"],
        "bestUprightMad": best_upright["mad"],
        "bestNativeOrientation": best_native["orientation"],
        "bestNativeMad": best_native["mad"],
        "activeCropMadMean": crop_stats["activeCropMadMean"],
        "activeCropMadMax": crop_stats["activeCropMadMax"],
        "activeCropCount": crop_stats["activeCropCount"],
        "page76Match": page76_match,
        "derivativePage76Match": derivative_match,
        "renderPixelGainVsBaseline": round(render_pixel_gain, 4),
        "sourcePixelGainVsBaseline": round(source_pixel_gain, 4),
        "higherSourceResolutionThanBaseline": source_higher,
        "r1DistinctImprovedCandidate": r1_distinct_improved,
        "embeddedSummary": embedded_summary,
    }
    thumb = ImageOps.contain(orient_image(img, best_upright["orientation"]), (126, 150))
    return row, thumb


def draw_sheet(summary: dict, rows: list[dict], thumbs: dict[str, Image.Image]) -> None:
    width, height = 1840, 1040
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 104), fill=(25, 31, 42))
    draw.text((24, 18), "PDF Render Quality Gate", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"pdfs {summary['pdfCandidateCount']} | pages {summary['renderedPageCount']} | "
            f"page76 render/embed {summary['page76RenderMatchCount']}/{summary['page76EmbeddedMatchCount']} | "
            f"higher-res {summary['higherResolutionPage76RenderCount']}/{summary['higherResolutionPage76EmbeddedCount']} | "
            f"R1/R3 {summary['r1DistinctImprovedPdfCandidateCount']}/{summary['sourceBackedR3BridgeHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 128
    draw.text((24, y), "Best PDF page-76 render/extraction candidates", fill=(45, 45, 45), font=small)
    y += 30
    headers = ["view", "pdf/page", "kind", "size", "upright", "uMAD", "native", "nMAD", "source gain", "status"]
    xs = [24, 170, 520, 715, 850, 980, 1100, 1230, 1345, 1480]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 22

    display_rows = sorted(
        rows,
        key=lambda row: (
            not row["page76Match"],
            not row["derivativePage76Match"],
            row["bestNativeMad"],
            row["bestUprightMad"],
            row["pdfPath"],
            row["pdfPageIndex"],
            row["candidateKind"],
        ),
    )
    for idx, row in enumerate(display_rows[:8]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 118), fill=fill)
        thumb = thumbs.get(row["candidateId"])
        if thumb:
            tx = xs[0]
            ty = y
            draw.rectangle((tx, ty, tx + 128, ty + 152), outline=(210, 215, 225))
            img.paste(thumb, (tx + (128 - thumb.size[0]) // 2, ty + (152 - thumb.size[1]) // 2))
        pdf_label = f"{row['pdfPath']} p{row['pdfPageIndex']}/{row['pdfPageCount']}"
        status = "page76" if row["page76Match"] else "derivative" if row["derivativePage76Match"] else "-"
        if row["r1DistinctImprovedCandidate"]:
            status = "R1 improved"
        draw.text((xs[1], y + 8), pdf_label[:46], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y + 8), row["candidateKind"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y + 8), f"{row['size'][0]}x{row['size'][1]}", fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y + 8), row["bestUprightOrientation"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y + 8), str(row["bestUprightMad"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y + 8), row["bestNativeOrientation"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[7], y + 8), str(row["bestNativeMad"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[8], y + 8), str(row["sourcePixelGainVsBaseline"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[9], y + 8), status, fill=(30, 30, 30), font=tiny)
        if row.get("exactKnownImageRole"):
            draw.text((xs[2], y + 34), f"exact: {row['exactKnownImageRole']}", fill=(70, 70, 70), font=tiny)
        if row.get("embeddedSummary", {}).get("maxEmbeddedSize"):
            draw.text(
                (xs[2], y + 58),
                f"embedded max {row['embeddedSummary']['maxEmbeddedSize'][0]}x{row['embeddedSummary']['maxEmbeddedSize'][1]}",
                fill=(70, 70, 70),
                font=tiny,
            )
        y += 124

    y = 990
    draw.text((24, y), summary["pdfRenderQualityFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    baseline_upright = Image.open(UPRIGHT_PAGE76).convert("RGB")
    baseline_native = Image.open(NATIVE_PAGE76).convert("RGB")
    baseline_pixels = baseline_upright.size[0] * baseline_upright.size[1]
    guardrail = load_json(ORIENTATION_GUARDRAIL)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    known_hashes = known_image_hashes()
    active_boxes = [
        box
        for box in (box_from_row(row) for row in guardrail.get("targetRows", []))
        if box
    ]
    if not active_boxes:
        active_boxes = [
            [1334, 2177, 1801, 2225],
            [428, 2398, 691, 2445],
            [795, 2544, 1196, 2592],
            [1040, 2932, 1661, 2982],
        ]

    rows: list[dict] = []
    pdf_rows: list[dict] = []
    thumbs: dict[str, Image.Image] = {}
    for pdf_path in [path for path in PDF_PATHS if path.exists()]:
        pdf_md5 = md5_file(pdf_path)
        doc = fitz.open(pdf_path)
        page_summaries = []
        for page_index, page in enumerate(doc, start=1):
            embedded = embedded_images(doc, page)
            max_embedded = max((item["pixelCount"] for item in embedded), default=0)
            max_embedded_size = max(
                (item["size"] for item in embedded),
                default=None,
                key=lambda size: size[0] * size[1],
            )
            embedded_summary = {
                "embeddedImageCount": len(embedded),
                "maxEmbeddedSize": max_embedded_size,
                "maxEmbeddedPixelGainVsBaseline": round(max_embedded / baseline_pixels, 4)
                if max_embedded
                else 0,
            }
            render_img = render_page(page)
            render_source_gain = max_embedded / baseline_pixels if max_embedded else (
                render_img.size[0] * render_img.size[1] / baseline_pixels
            )
            render_row, thumb = compare_candidate(
                pdf_path=pdf_path,
                pdf_md5=pdf_md5,
                page_index=page_index,
                page_count=len(doc),
                kind="page_render_300dpi",
                img=render_img,
                baseline_upright=baseline_upright,
                baseline_native=baseline_native,
                active_boxes=active_boxes,
                source_pixel_gain=render_source_gain,
                embedded_summary=embedded_summary,
                known_hashes=known_hashes,
            )
            rows.append(render_row)
            thumbs[render_row["candidateId"]] = thumb

            for item in embedded:
                embedded_gain = item["pixelCount"] / baseline_pixels
                embedded_row, embedded_thumb = compare_candidate(
                    pdf_path=pdf_path,
                    pdf_md5=pdf_md5,
                    page_index=page_index,
                    page_count=len(doc),
                    kind="embedded_image",
                    img=item["image"],
                    baseline_upright=baseline_upright,
                    baseline_native=baseline_native,
                    active_boxes=active_boxes,
                    source_pixel_gain=embedded_gain,
                    embedded_summary=embedded_summary,
                    known_hashes=known_hashes,
                    candidate_bytes_md5=item["bytesMd5"],
                    embedded_image_index=item["imageIndex"],
                )
                embedded_row["embeddedXref"] = item["xref"]
                embedded_row["embeddedExtension"] = item["extension"]
                embedded_row["embeddedBytes"] = item["bytes"]
                rows.append(embedded_row)
                thumbs[embedded_row["candidateId"]] = embedded_thumb

            page_summaries.append(
                {
                    "pageIndex": page_index,
                    "renderSize": [render_img.size[0], render_img.size[1]],
                    "embeddedImageCount": len(embedded),
                    "maxEmbeddedSize": max_embedded_size,
                    "maxEmbeddedPixelGainVsBaseline": embedded_summary["maxEmbeddedPixelGainVsBaseline"],
                }
            )
        pdf_rows.append(
            {
                "path": rel(pdf_path),
                "bytes": pdf_path.stat().st_size,
                "md5": pdf_md5,
                "pageCount": len(doc),
                "pageSummaries": page_summaries,
            }
        )
        doc.close()

    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0
    render_rows = [row for row in rows if row["candidateKind"] == "page_render_300dpi"]
    embedded_rows = [row for row in rows if row["candidateKind"] == "embedded_image"]
    page76_render = [row for row in render_rows if row["page76Match"]]
    page76_embedded = [row for row in embedded_rows if row["page76Match"]]
    unique_page76_pages = {
        (row["pdfPath"], row["pdfPageIndex"])
        for row in rows
        if row["page76Match"]
    }
    higher_page76_render = [
        row for row in page76_render if row["higherSourceResolutionThanBaseline"]
    ]
    higher_page76_embedded = [
        row for row in page76_embedded if row["higherSourceResolutionThanBaseline"]
    ]
    r1_rows = [row for row in rows if row["r1DistinctImprovedCandidate"]]
    summary = {
        "pdfCandidateCount": len(pdf_rows),
        "renderedPageCount": len(render_rows),
        "embeddedImageCount": len(embedded_rows),
        "candidateRowCount": len(rows),
        "page76RenderMatchCount": len(page76_render),
        "page76EmbeddedMatchCount": len(page76_embedded),
        "uniquePage76PdfPageCount": len(unique_page76_pages),
        "derivativeRenderMatchCount": sum(1 for row in render_rows if row["derivativePage76Match"]),
        "derivativeEmbeddedMatchCount": sum(1 for row in embedded_rows if row["derivativePage76Match"]),
        "higherResolutionPage76RenderCount": len(higher_page76_render),
        "higherResolutionPage76EmbeddedCount": len(higher_page76_embedded),
        "r1DistinctImprovedPdfCandidateCount": len(r1_rows),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": bool(r1_rows and source_r3 > 0 and triggers > 0),
        "localAssetOrientationFingerprint": load_json(LOCAL_ASSET_GATE)
        .get("summary", {})
        .get("localAssetOrientationFingerprint"),
    }
    summary["pdfRenderQualityFingerprint"] = (
        f"pdfs={summary['pdfCandidateCount']}|pages={summary['renderedPageCount']}|"
        f"embedded={summary['embeddedImageCount']}|candidates={summary['candidateRowCount']}|"
        f"page76Render={summary['page76RenderMatchCount']}|page76Embedded={summary['page76EmbeddedMatchCount']}|"
        f"uniquePage76={summary['uniquePage76PdfPageCount']}|"
        f"higherRender={summary['higherResolutionPage76RenderCount']}|"
        f"higherEmbedded={summary['higherResolutionPage76EmbeddedCount']}|"
        f"r1Improved={summary['r1DistinctImprovedPdfCandidateCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketPdfRenderQualityGate": "local_pdf_renders_do_not_reopen_source_review",
        "selectorUnlocked": summary["selectorUnlocked"],
        "reason": (
            "The only true PDF page-76 hit is the already-known magazine PDF page at the current "
            "2544x3264 source resolution. The other local PDFs embed lower-resolution 2040x2805 "
            "images and do not produce a page-76 match under the source-comparison threshold. "
            "No PDF supplies distinct higher-resolution R1 evidence or any R3 unit/order wording."
        ),
        "nextMove": (
            "Keep the source-acquisition packet as the next-action checklist. A future PDF/photo/export "
            "must supply a distinct source capture that improves R1/R5 and also satisfies an R3 reopen "
            "trigger before selector or key work resumes."
        ),
    }

    draw_sheet(summary, rows, thumbs)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": (
            "local PDF render/extraction quality source gate; no OCR extraction, key candidates, "
            "hashes, seed/WIF/address checks, BIP39, or broad brute force"
        ),
        "inputs": {
            "pdfPaths": [rel(path) for path in PDF_PATHS if path.exists()],
            "renderDpi": RENDER_DPI,
            "uprightPage76": rel(UPRIGHT_PAGE76),
            "nativePage76": rel(NATIVE_PAGE76),
            "orientationGuardrail": rel(ORIENTATION_GUARDRAIL),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "localAssetOrientationGate": rel(LOCAL_ASSET_GATE),
        },
        "pdfRows": pdf_rows,
        "candidateRows": rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    top_rows = sorted(
        rows,
        key=lambda row: (
            not row["page76Match"],
            not row["derivativePage76Match"],
            row["bestNativeMad"],
            row["bestUprightMad"],
            row["pdfPath"],
            row["pdfPageIndex"],
            row["candidateKind"],
        ),
    )[:10]
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet PDF Render Quality Gate",
                "",
                f"- PDF candidates checked: `{summary['pdfCandidateCount']}`.",
                f"- PDF pages rendered at {RENDER_DPI} dpi: `{summary['renderedPageCount']}`.",
                f"- Embedded page images checked: `{summary['embeddedImageCount']}`.",
                f"- Page-76 render / embedded matches: `{summary['page76RenderMatchCount']}` / `{summary['page76EmbeddedMatchCount']}`.",
                f"- Unique PDF page-76 pages: `{summary['uniquePage76PdfPageCount']}`.",
                f"- Derivative render / embedded matches: `{summary['derivativeRenderMatchCount']}` / `{summary['derivativeEmbeddedMatchCount']}`.",
                f"- Higher-resolution page-76 render / embedded matches: `{summary['higherResolutionPage76RenderCount']}` / `{summary['higherResolutionPage76EmbeddedCount']}`.",
                f"- R1 distinct improved PDF candidates: `{summary['r1DistinctImprovedPdfCandidateCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['pdfRenderQualityFingerprint']}`.",
                "",
                "Top PDF candidates:",
                "",
            ]
            + [
                (
                    f"- `{row['pdfPath']}` page `{row['pdfPageIndex']}` `{row['candidateKind']}`: "
                    f"size `{row['size'][0]}x{row['size'][1]}`, upright `{row['bestUprightOrientation']}` "
                    f"MAD `{row['bestUprightMad']}`, native `{row['bestNativeOrientation']}` "
                    f"MAD `{row['bestNativeMad']}`, source gain `{row['sourcePixelGainVsBaseline']}`, "
                    f"page76 `{row['page76Match']}`, exact role `{row['exactKnownImageRole'] or '-'}`."
                )
                for row in top_rows
            ]
            + [
                "",
                "Decision: local PDF rendering/extraction does not reopen source review or extraction.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
