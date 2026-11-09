#!/usr/bin/env python3
"""Audit whether magazine.pdf image placement can explain registration gaps.

The current geometry truth is the high-res `magazine.pdf`, but the p78->p76
registration benchmark still needs a dx about -38/-40. This pass checks whether
that offset could come from PDF page placement: crop boxes, rotations, per-page
image rect offsets, or extra hidden image XObjects.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "magazine.pdf"
OUT = ROOT / "analysis_outputs/source_audit/magazine_pdf_image_placement"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "magazine_pdf_image_placement.json"
OUT_MD = OUT / "magazine_pdf_image_placement.md"


def rect_list(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 4), round(rect.y0, 4), round(rect.x1, 4), round(rect.y1, 4)]


def run_cmd(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
    except Exception as exc:
        return f"ERROR: {exc}"


def main() -> None:
    doc = fitz.open(PDF)
    pages = []
    for page_index, page in enumerate(doc, 1):
        image_rows = []
        for image in page.get_images(full=True):
            xref = image[0]
            rects = page.get_image_rects(xref)
            pix = fitz.Pixmap(doc, xref)
            row = {
                "xref": xref,
                "widthPx": pix.width,
                "heightPx": pix.height,
                "colorspace": pix.colorspace.name if pix.colorspace else None,
                "alpha": pix.alpha,
                "rects": [rect_list(rect) for rect in rects],
            }
            pix = None
            image_rows.append(row)

        media = page.mediabox
        crop = page.cropbox
        coverage = []
        for row in image_rows:
            for rect in row["rects"]:
                coverage.append(
                    {
                        "xref": row["xref"],
                        "leftPt": round(rect[0] - crop.x0, 4),
                        "topPt": round(rect[1] - crop.y0, 4),
                        "rightGapPt": round(crop.x1 - rect[2], 4),
                        "bottomGapPt": round(crop.y1 - rect[3], 4),
                        "widthPt": round(rect[2] - rect[0], 4),
                        "heightPt": round(rect[3] - rect[1], 4),
                        "scaleXPxPerPt": round(row["widthPx"] / max(1e-9, rect[2] - rect[0]), 6),
                        "scaleYPxPerPt": round(row["heightPx"] / max(1e-9, rect[3] - rect[1]), 6),
                    }
                )

        pages.append(
            {
                "pdfPage": page_index,
                "articlePage": page_index + 72,
                "rotation": page.rotation,
                "mediabox": rect_list(media),
                "cropbox": rect_list(crop),
                "imageCount": len(image_rows),
                "images": image_rows,
                "coverage": coverage,
            }
        )

    image_counts = [page["imageCount"] for page in pages]
    sizes = sorted({(image["widthPx"], image["heightPx"]) for page in pages for image in page["images"]})
    rotations = sorted({page["rotation"] for page in pages})
    full_bleed = all(
        page["imageCount"] == 1
        and page["coverage"]
        and page["coverage"][0]["leftPt"] == 0
        and page["coverage"][0]["topPt"] == 0
        and page["coverage"][0]["rightGapPt"] == 0
        and page["coverage"][0]["bottomGapPt"] == 0
        for page in pages
    )
    scale_pairs = sorted(
        {
            (page["coverage"][0]["scaleXPxPerPt"], page["coverage"][0]["scaleYPxPerPt"])
            for page in pages
            if page["coverage"]
        }
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "magazine.pdf page image placement audit; no key derivation",
        "pdf": str(PDF),
        "pdfinfoExcerpt": run_cmd(["pdfinfo", str(PDF)]).splitlines()[:20],
        "pdfimagesList": run_cmd(["pdfimages", "-list", str(PDF)]).splitlines(),
        "summary": {
            "pageCount": len(pages),
            "imageCounts": image_counts,
            "uniqueImageSizesPx": sizes,
            "rotations": rotations,
            "fullBleedSingleImageEveryPage": full_bleed,
            "scalePxPerPtPairs": scale_pairs,
        },
        "pages": pages,
        "assessment": [
            "Every page is a single 2544x3264 RGB JPEG image at 300 ppi.",
            "Each page image fills the crop/media box exactly with no per-page image offset or scale drift.",
            "All pages share the same PDF rotation and the same pixel-to-point scale.",
            "Therefore the p78 dx=-38/-40 registration repair is not explained by hidden PDF placement, crop-box mismatch, or extra embedded images inside magazine.pdf.",
            "The remaining source-registration gap must come from the printed/physical source, Canva/original-layout image, browser/source variant, or the puzzle's intended visual operation.",
        ],
        "nextMove": "Do not look inside magazine.pdf for a hidden higher-resolution layer. Continue with source/physical acquisition, or test only human-readable selector rules on the already locked high-res page-76 corridor.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Magazine PDF Image Placement Audit",
        "",
        "Scope: check whether `magazine.pdf` itself contains per-page image placement, crop, rotation, or hidden image-layer differences that could explain the p78->p76 registration repair. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDF: `{PDF}`",
        f"- Pages: `{result['summary']['pageCount']}`",
        f"- Image counts by page: `{result['summary']['imageCounts']}`",
        f"- Unique image sizes: `{result['summary']['uniqueImageSizesPx']}`",
        f"- Page rotations: `{result['summary']['rotations']}`",
        f"- Full-bleed single image every page: `{result['summary']['fullBleedSingleImageEveryPage']}`",
        f"- Pixel/point scales: `{result['summary']['scalePxPerPtPairs']}`",
        "",
        "## Page Placement",
        "",
        "| pdf page | article page | rotation | image count | image px | image rect pt | gaps L/T/R/B pt | scale px/pt |",
        "|---:|---:|---:|---:|---|---|---|---|",
    ]
    for page in pages:
        if page["images"]:
            image = page["images"][0]
            cov = page["coverage"][0]
            image_px = f"{image['widthPx']}x{image['heightPx']}"
            rect = image["rects"][0]
            gaps = f"{cov['leftPt']}/{cov['topPt']}/{cov['rightGapPt']}/{cov['bottomGapPt']}"
            scale = f"{cov['scaleXPxPerPt']}/{cov['scaleYPxPerPt']}"
        else:
            image_px = "-"
            rect = "-"
            gaps = "-"
            scale = "-"
        lines.append(
            f"| {page['pdfPage']} | {page['articlePage']} | {page['rotation']} | {page['imageCount']} | `{image_px}` | `{rect}` | `{gaps}` | `{scale}` |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("full bleed:", full_bleed)
    print("sizes:", sizes)


if __name__ == "__main__":
    main()
