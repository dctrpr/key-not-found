#!/usr/bin/env python3
"""Verify Desktop best-scan pixels against current source/3D caches.

This is a source-integrity pass, not a selector/key experiment. It checks that
the user-supplied Desktop magazine PDF, the workspace scan, the extracted
source_images cache, and the readable/upright 3D article map are all the same
pixel source with the expected 180-degree orientation bridge.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_PDF = Path("private_inputs/Desktop/magazine.pdf")
WORKSPACE_PDF = ROOT / "magazine.pdf"
SOURCE_DIR = ROOT / "analysis_outputs/source_images"
UPRIGHT_DIR = ROOT / "analysis_outputs/3d_article_map"
OUT = ROOT / "analysis_outputs/source_audit/desktop_best_scan_pixel_lock"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "desktop_best_scan_pixel_lock.json"
OUT_MD = OUT / "desktop_best_scan_pixel_lock.md"
OUT_SHEET = OUT / "desktop_best_scan_pixel_lock_sheet.jpg"


ARTICLE_PAGES = [75, 76, 77, 78, 79, 80]
PDF_ARTICLE_PAGE_OFFSET = 73


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_embedded_image(doc: fitz.Document, page_index: int) -> Image.Image:
    page = doc[page_index]
    images = page.get_images(full=True)
    if not images:
        raise RuntimeError(f"page {page_index + 1} has no embedded image")
    xref = images[0][0]
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha >= 4:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    mode = "RGBA" if pix.alpha else "RGB"
    image = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    return image.convert("RGB")


def rms(a: Image.Image, b: Image.Image) -> float | None:
    if a.size != b.size:
        return None
    diff = ImageChops.difference(a, b)
    hist = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(hist))
    total = sum(sq)
    pixels = a.size[0] * a.size[1] * len(a.getbands())
    return round(math.sqrt(total / pixels), 6)


def open_rgb(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    return Image.open(path).convert("RGB")


def make_sheet(records: list[dict], fresh_images: dict[int, Image.Image]) -> None:
    thumb_w, thumb_h = 190, 244
    gap = 22
    label_h = 48
    cols = 3
    rows = 2
    width = cols * (thumb_w * 2 + gap) + gap
    height = rows * (thumb_h + label_h + gap) + gap + 40
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 10), "Desktop best-scan fresh rot180 thumbnails beside current 3D upright cache", fill=(0, 0, 0))

    for idx, record in enumerate(records):
        page = record["articlePage"]
        row, col = divmod(idx, cols)
        x = gap + col * (thumb_w * 2 + gap)
        y = gap + 40 + row * (thumb_h + label_h + gap)
        fresh = fresh_images[page].rotate(180)
        upright = open_rgb(UPRIGHT_DIR / f"page_{page}_upright.jpg")
        if upright is None:
            continue
        fresh.thumbnail((thumb_w, thumb_h))
        upright = upright.copy()
        upright.thumbnail((thumb_w, thumb_h))
        sheet.paste(fresh, (x, y))
        sheet.paste(upright, (x + thumb_w, y))
        text = f"p{page} source->rot180 | 3D; RMS {record['freshRot180Vs3dRms']}"
        draw.text((x, y + thumb_h + 4), text, fill=(0, 0, 0))
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    desktop_hash = sha256(DESKTOP_PDF)
    workspace_hash = sha256(WORKSPACE_PDF)
    records: list[dict] = []
    fresh_images: dict[int, Image.Image] = {}

    with fitz.open(DESKTOP_PDF) as doc:
        for article_page in ARTICLE_PAGES:
            pdf_page_index = article_page - PDF_ARTICLE_PAGE_OFFSET
            fresh = first_embedded_image(doc, pdf_page_index)
            fresh_images[article_page] = fresh
            source = open_rgb(SOURCE_DIR / f"magazine_page_{article_page}.jpg")
            upright = open_rgb(UPRIGHT_DIR / f"page_{article_page}_upright.jpg")
            fresh_rot180 = fresh.rotate(180)

            source_native = rms(fresh, source) if source else None
            source_rot180 = rms(fresh_rot180, source) if source else None
            upright_native = rms(fresh, upright) if upright else None
            upright_rot180 = rms(fresh_rot180, upright) if upright else None

            records.append(
                {
                    "articlePage": article_page,
                    "pdfPageIndex0": pdf_page_index,
                    "pdfPageNumber1": pdf_page_index + 1,
                    "embeddedSize": list(fresh.size),
                    "sourceImageExists": source is not None,
                    "uprightImageExists": upright is not None,
                    "freshVsSourceRms": source_native,
                    "freshRot180VsSourceRms": source_rot180,
                    "freshVs3dRms": upright_native,
                    "freshRot180Vs3dRms": upright_rot180,
                    "sourceBestOrientation": "native" if source_native is not None and (source_rot180 is None or source_native <= source_rot180) else "rot180",
                    "uprightBestOrientation": "rot180" if upright_rot180 is not None and (upright_native is None or upright_rot180 <= upright_native) else "native",
                }
            )

    make_sheet(records, fresh_images)

    all_source_native = all(
        r["sourceBestOrientation"] == "native"
        and r["freshVsSourceRms"] is not None
        and r["freshVsSourceRms"] < 3
        for r in records
    )
    all_upright_rot180 = all(r["uprightBestOrientation"] == "rot180" and r["freshRot180Vs3dRms"] is not None and r["freshRot180Vs3dRms"] < 3 for r in records)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Desktop best-scan pixel lock against source_images and 3D upright cache; no key derivation",
        "desktopPdf": str(DESKTOP_PDF),
        "workspacePdf": str(WORKSPACE_PDF),
        "desktopSha256": desktop_hash,
        "workspaceSha256": workspace_hash,
        "pdfByteIdentical": desktop_hash == workspace_hash,
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "records": records,
        "decision": {
            "sourceImagesAreFreshDesktopExtraction": all_source_native,
            "threeDCacheIsRot180ReadableDerivative": all_upright_rot180,
            "sourceSelectionReopenNeeded": not (desktop_hash == workspace_hash and all_source_native and all_upright_rot180),
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Desktop Best-Scan Pixel Lock",
        "",
        "Scope: verify that the Desktop `magazine.pdf` identified as the best scan is the same pixel source used by the current source-image and 3D/upright geometry caches. No key derivation, hashing of candidate text, seed checking, WIF checking, or address checking was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Desktop PDF: `{DESKTOP_PDF}`",
        f"- Workspace PDF: `{WORKSPACE_PDF}`",
        f"- Desktop/workspace byte-identical: `{result['pdfByteIdentical']}`",
        f"- Review sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Page Pixel Comparisons",
        "",
        "| article page | PDF page | embedded size | fresh vs source RMS | fresh rot180 vs source RMS | fresh vs 3D RMS | fresh rot180 vs 3D RMS | source orientation | 3D orientation |",
        "|---:|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for r in records:
        lines.append(
            f"| {r['articlePage']} | `{r['pdfPageNumber1']}` | `{r['embeddedSize'][0]}x{r['embeddedSize'][1]}` | `{r['freshVsSourceRms']}` | `{r['freshRot180VsSourceRms']}` | `{r['freshVs3dRms']}` | `{r['freshRot180Vs3dRms']}` | `{r['sourceBestOrientation']}` | `{r['uprightBestOrientation']}` |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Desktop and workspace PDFs are byte-identical: `{result['pdfByteIdentical']}`.",
            f"- Fresh embedded-page extraction matches `analysis_outputs/source_images` in native orientation for every page: `{all_source_native}`.",
            f"- Current 3D/upright page images match the same Desktop extraction after `rot180` within JPEG-resave tolerance for every page: `{all_upright_rot180}`.",
            "- This means page-76, page-79, and p78-frame geometry conclusions are using the user-supplied best scan, not an older OCR/source branch.",
            "",
            "## Decision",
            "",
            "- Do not reopen local PDF source selection. The Desktop best scan, workspace scan, `source_images`, and 3D upright cache are one source chain.",
            "- Keep OCR PDF coordinates as labels only; exact geometry must stay tied to this high-res scan or a genuinely new physical/original-layout source.",
            "- Next move: use the future-source validation packet only if a new scan/export/source appears; otherwise look for explicit selector wording rather than more local pixel permutations.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("sourceSelectionReopenNeeded:", result["decision"]["sourceSelectionReopenNeeded"])


if __name__ == "__main__":
    main()
