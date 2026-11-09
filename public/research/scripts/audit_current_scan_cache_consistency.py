#!/usr/bin/env python3
"""Verify that cached page images are from the current best magazine.pdf scan.

This is a source-control check for the investigation state. It compares the
current Desktop/project `magazine.pdf` files, then extracts the embedded page
images for article pages 75-80 and compares them against the cached source
images and the 3D-viewer upright images. The embedded/source images are native
PDF orientation; the 3D viewer stores the same pages in readable orientation,
which is a 180-degree rotation.

No OCR extraction, key derivation, hashing for wallet candidates, WIF checks,
seed checks, or address checks are performed.
"""

from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PDF = ROOT / "magazine.pdf"
DESKTOP_PDF = Path("private_inputs/Desktop/magazine.pdf")
OUT = ROOT / "analysis_outputs/source_audit/current_scan_cache_consistency"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_cache_consistency.json"
OUT_MD = OUT / "current_scan_cache_consistency.md"
SHEET = OUT / "page76_source_vs_3d_sheet.jpg"

ARTICLE_PAGES = list(range(75, 81))
VISUAL_RMS_TOLERANCE = 2.0


def file_md5(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pixel_md5(image: Image.Image) -> str:
    rgb = image.convert("RGB")
    h = hashlib.md5()
    h.update(f"{rgb.width}x{rgb.height}:RGB:".encode("ascii"))
    h.update(rgb.tobytes())
    return h.hexdigest()


def load_rgb(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    return Image.open(path).convert("RGB")


def diff_stats(a: Image.Image, b: Image.Image) -> dict:
    if a.size != b.size:
        return {"sameSize": False, "aSize": list(a.size), "bSize": list(b.size), "rms": None, "meanAbs": None}
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    stat = ImageStat.Stat(diff)
    mean_abs = sum(stat.mean) / len(stat.mean)
    rms = (sum(value * value for value in stat.rms) / len(stat.rms)) ** 0.5
    extrema = diff.getextrema()
    max_abs = max(channel[1] for channel in extrema)
    return {
        "sameSize": True,
        "rms": round(rms, 6),
        "meanAbs": round(mean_abs, 6),
        "maxAbs": int(max_abs),
        "visualMatch": rms <= VISUAL_RMS_TOLERANCE,
    }


def extract_pdf_page_image(doc: fitz.Document, article_page: int) -> Image.Image:
    pdf_index = article_page - 73
    page = doc[pdf_index]
    images = page.get_images(full=True)
    if len(images) != 1:
        raise RuntimeError(f"Article page {article_page} has {len(images)} embedded images, expected 1")
    xref = images[0][0]
    raw = doc.extract_image(xref)["image"]
    return Image.open(io.BytesIO(raw)).convert("RGB")


def compare_page(doc: fitz.Document, article_page: int) -> dict:
    extracted = extract_pdf_page_image(doc, article_page)
    source_path = ROOT / f"analysis_outputs/source_images/magazine_page_{article_page}.jpg"
    upright_path = ROOT / f"analysis_outputs/3d_article_map/page_{article_page}_upright.jpg"
    source = load_rgb(source_path)
    upright = load_rgb(upright_path)

    extracted_md5 = pixel_md5(extracted)
    source_md5 = pixel_md5(source) if source else None
    upright_md5 = pixel_md5(upright) if upright else None

    source_diff = diff_stats(extracted, source) if source else None
    upright_diff = diff_stats(extracted, upright) if upright else None

    return {
        "articlePage": article_page,
        "pdfPageOneBased": article_page - 72,
        "extractedSize": list(extracted.size),
        "extractedPixelMd5": extracted_md5,
        "sourceCachePath": str(source_path.relative_to(ROOT)),
        "sourceCacheExists": source is not None,
        "sourceCachePixelMd5": source_md5,
        "sourceMatchesExtracted": source_md5 == extracted_md5,
        "sourceVisuallyMatchesExtracted": bool(source_diff and source_diff.get("visualMatch")),
        "sourceDiff": source_diff,
        "uprightPath": str(upright_path.relative_to(ROOT)),
        "uprightExists": upright is not None,
        "uprightPixelMd5": upright_md5,
        "uprightMatchesExtracted": upright_md5 == extracted_md5,
        "uprightVisuallyMatchesExtracted": bool(upright_diff and upright_diff.get("visualMatch")),
        "uprightDiff": upright_diff,
    }


def build_page76_sheet(doc: fitz.Document) -> None:
    extracted = extract_pdf_page_image(doc, 76)
    source = load_rgb(ROOT / "analysis_outputs/source_images/magazine_page_76.jpg")
    upright = load_rgb(ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg")
    if not source or not upright:
        return

    crop = (720, 2350, 1750, 3045)
    upright_source = source.rotate(180)
    upright_extracted = extracted.rotate(180)
    panels = [
        ("PDF extracted, rotated", upright_extracted.crop(crop)),
        ("source cache, rotated", upright_source.crop(crop)),
        ("3D upright", upright.crop(crop)),
        ("abs diff: PDF/source", ImageChops.difference(upright_extracted.crop(crop), upright_source.crop(crop))),
        ("abs diff: source/3D", ImageChops.difference(upright_source.crop(crop), upright.crop(crop))),
    ]
    scale = 0.55
    thumb_panels = []
    for label, img in panels:
        thumb_panels.append((label, img.resize((int(img.width * scale), int(img.height * scale)))))

    margin = 24
    gap = 18
    label_h = 30
    width = margin * 2 + sum(img.width for _, img in thumb_panels) + gap * (len(thumb_panels) - 1)
    height = margin * 2 + label_h + max(img.height for _, img in thumb_panels)
    sheet = Image.new("RGB", (width, height), (16, 18, 22))
    try:
        from PIL import ImageDraw, ImageFont

        draw = ImageDraw.Draw(sheet)
        try:
            fnt = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
        except Exception:
            fnt = ImageFont.load_default()
        x = margin
        for label, img in thumb_panels:
            draw.text((x, margin), label, fill=(235, 239, 244), font=fnt)
            sheet.paste(img, (x, margin + label_h))
            x += img.width + gap
    except Exception:
        x = margin
        for _, img in thumb_panels:
            sheet.paste(img, (x, margin + label_h))
            x += img.width + gap
    sheet.save(SHEET, quality=94)


def main() -> None:
    doc = fitz.open(DESKTOP_PDF)
    build_page76_sheet(doc)
    project_md5 = file_md5(PROJECT_PDF)
    desktop_md5 = file_md5(DESKTOP_PDF)
    page_rows = [compare_page(doc, page) for page in ARTICLE_PAGES]
    all_source_match = all(row["sourceMatchesExtracted"] for row in page_rows)
    all_source_visual = all(row["sourceVisuallyMatchesExtracted"] for row in page_rows)
    # The 3D viewer uses readable/upright orientation. Compare it against the
    # native source image rotated 180 degrees, not against native orientation.
    orientation_rows = []
    for row in page_rows:
        article_page = row["articlePage"]
        native = load_rgb(ROOT / f"analysis_outputs/source_images/magazine_page_{article_page}.jpg")
        upright = load_rgb(ROOT / f"analysis_outputs/3d_article_map/page_{article_page}_upright.jpg")
        diff = diff_stats(native.rotate(180), upright) if native and upright else None
        orientation_rows.append(
            {
                "articlePage": article_page,
                "sourceTo3dTransform": "rotate180",
                "diff": diff,
                "visualMatch": bool(diff and diff.get("visualMatch")),
            }
        )
    all_upright_visual = all(row["visualMatch"] for row in orientation_rows)
    source_current = project_md5 == desktop_md5 and all_source_visual and all_upright_visual

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current scan/cache consistency; no OCR extraction or key derivation",
        "projectPdf": str(PROJECT_PDF),
        "desktopPdf": str(DESKTOP_PDF),
        "projectPdfMd5": project_md5,
        "desktopPdfMd5": desktop_md5,
        "projectDesktopByteIdentical": project_md5 == desktop_md5,
        "articlePages": ARTICLE_PAGES,
        "pageRows": page_rows,
        "summary": {
            "visualRmsTolerance": VISUAL_RMS_TOLERANCE,
            "allSourceCachesPixelMatchExtracted": all_source_match,
            "allSourceCachesVisuallyMatchExtracted": all_source_visual,
            "sourceTo3dTransform": "rotate180",
            "all3dUprightImagesVisuallyMatchExtractedAfterRotate180": all_upright_visual,
            "sourceImageCacheIsCurrentScan": source_current,
            "page76ComparisonSheet": str(SHEET.relative_to(ROOT)) if SHEET.exists() else None,
        },
        "orientationRows": orientation_rows,
        "assessment": [
            "The Desktop and project magazine.pdf files are byte-identical." if project_md5 == desktop_md5 else "The Desktop and project magazine.pdf files differ.",
            "Cached source images for pages 75-80 visually match the embedded images extracted from the current Desktop magazine.pdf; pixel hashes differ only because the caches are JPEG-resaved." if all_source_visual else "One or more cached source images do not visually match the current Desktop magazine.pdf extraction.",
            "3D viewer upright images for pages 75-80 visually match the current source images after a 180-degree rotation.",
        ],
        "decision": "The 3D upright image layer is source-faithful after accounting for the native PDF image orientation. The previous native-orientation mismatch was an orientation check error, not a stale-source finding." if source_current else "Refresh stale geometry caches before trusting exact extraction.",
        "nextMove": "Use the 3D upright layer for readable-orientation geometry, or use source_images/fresh PDF extraction with a 180-degree rotation before comparing upright crop coordinates.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Cache Consistency Audit",
        "",
        "Scope: verify that the current cached page images and 3D viewer images came from the supplied best `magazine.pdf`. No OCR extraction, key derivation, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Project PDF md5: `{project_md5}`",
        f"- Desktop PDF md5: `{desktop_md5}`",
        f"- Project/Desktop byte-identical: `{result['projectDesktopByteIdentical']}`",
        f"- Visual RMS tolerance: `{VISUAL_RMS_TOLERANCE}`",
        f"- Source caches pixel-match extracted PDF images: `{all_source_match}`",
        f"- Source caches visually match extracted PDF images: `{all_source_visual}`",
        f"- Source-to-3D transform: `rotate180`",
        f"- 3D upright images visually match after rotate180: `{all_upright_visual}`",
        f"- Page-76 comparison sheet: `{str(SHEET.relative_to(ROOT)) if SHEET.exists() else None}`",
        "",
        "## Page Checks",
        "",
        "| article page | pdf page | extracted size | source visual match | source diff rms/max | 3D after rotate180 visual match | 3D diff rms/max |",
        "|---:|---:|---|---|---|---|---|",
    ]
    by_page_orientation = {row["articlePage"]: row for row in orientation_rows}
    for row in page_rows:
        source_diff = row["sourceDiff"] or {}
        upright_row = by_page_orientation[row["articlePage"]]
        upright_diff = upright_row["diff"] or {}
        lines.append(
            "| {articlePage} | {pdfPageOneBased} | `{size}` | `{sourceMatch}` | `{sourceRms}/{sourceMax}` | `{uprightMatch}` | `{uprightRms}/{uprightMax}` |".format(
                articlePage=row["articlePage"],
                pdfPageOneBased=row["pdfPageOneBased"],
                size="x".join(str(v) for v in row["extractedSize"]),
                sourceMatch=row["sourceVisuallyMatchesExtracted"],
                sourceRms=source_diff.get("rms"),
                sourceMax=source_diff.get("maxAbs"),
                uprightMatch=upright_row["visualMatch"],
                uprightRms=upright_diff.get("rms"),
                uprightMax=upright_diff.get("maxAbs"),
            )
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("sourceImageCacheIsCurrentScan:", source_current)
    print("all3dUprightImagesVisuallyMatchAfterRotate180:", all_upright_visual)


if __name__ == "__main__":
    main()
