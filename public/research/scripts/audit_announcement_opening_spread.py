#!/usr/bin/env python3
"""Audit the announcement photo against the full magazine PDF opener spread.

Earlier geometry work focused on article pages 75-80. The announcement image
itself shows the physical OVERDOSE opener spread, which is PDF pages 1-2
(article pages 73-74). This pass records that source/provenance fact and
creates review crops. It does not generate keys.
"""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/announcement_opening_spread"
OUT.mkdir(parents=True, exist_ok=True)
MAGAZINE = ROOT / "magazine.pdf"
ANNOUNCEMENT = ROOT / "analysis_outputs/external_clues/max_thread_media/01_FqZGAb7aYAEdnKL.jpg"
OUT_JSON = OUT / "announcement_opening_spread_audit.json"
OUT_MD = OUT / "announcement_opening_spread_audit.md"
OUT_SHEET = OUT / "announcement_opening_spread_sheet.jpg"


ANNOUNCEMENT_CROPS = {
    "whole_magazine": (140, 250, 520, 535),
    "left_opener_page": (145, 260, 330, 525),
    "right_opener_page": (315, 255, 525, 520),
    "overdose_title": (160, 270, 315, 330),
}


def extract_pdf_image(pdf_page_index: int) -> Image.Image:
    doc = fitz.open(MAGAZINE)
    page = doc[pdf_page_index]
    images = page.get_images(full=True)
    if not images:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    raw = doc.extract_image(images[0][0])["image"]
    img = Image.open(BytesIO(raw)).convert("RGB")
    return img.rotate(180, expand=True)


def thumb(img: Image.Image, size=(320, 390)) -> Image.Image:
    out = img.copy()
    out.thumbnail(size, Image.Resampling.LANCZOS)
    return out


def save_inputs() -> dict:
    ann = Image.open(ANNOUNCEMENT).convert("RGB")
    p73 = extract_pdf_image(0)
    p74 = extract_pdf_image(1)
    p75 = extract_pdf_image(2)
    p76 = extract_pdf_image(3)

    paths = {}
    for name, box in ANNOUNCEMENT_CROPS.items():
        crop = ann.crop(box)
        scale = 3 if crop.width < 300 else 2
        crop = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.LANCZOS)
        path = OUT / f"announcement01_{name}.jpg"
        crop.save(path, quality=94)
        paths[name] = str(path)

    for label, img in [("pdf_p73_opener_left", p73), ("pdf_p74_opener_right", p74), ("pdf_p75_article_start", p75), ("pdf_p76_corridor", p76)]:
        path = OUT / f"{label}.jpg"
        img.save(path, quality=94)
        paths[label] = str(path)

    spread = Image.new("RGB", (p73.width + p74.width, max(p73.height, p74.height)), "white")
    spread.paste(p73, (0, 0))
    spread.paste(p74, (p73.width, 0))
    spread_path = OUT / "pdf_p73_p74_opener_spread.jpg"
    spread.save(spread_path, quality=94)
    paths["pdf_p73_p74_opener_spread"] = str(spread_path)
    return paths


def build_sheet(paths: dict) -> None:
    items = [
        ("announcement crop", Image.open(paths["whole_magazine"]).convert("RGB")),
        ("PDF p73 opener left", Image.open(paths["pdf_p73_opener_left"]).convert("RGB")),
        ("PDF p74 opener right", Image.open(paths["pdf_p74_opener_right"]).convert("RGB")),
        ("PDF p75 article text start", Image.open(paths["pdf_p75_article_start"]).convert("RGB")),
        ("PDF p76 target corridor page", Image.open(paths["pdf_p76_corridor"]).convert("RGB")),
    ]
    thumbs = [(label, thumb(img)) for label, img in items]
    cell_w, cell_h = 360, 450
    cols = 3
    rows = 2
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, (label, img) in enumerate(thumbs):
        x = (idx % cols) * cell_w + 18
        y = (idx // cols) * cell_h + 42
        draw.text((x, y - 28), label, fill=(0, 0, 0))
        sheet.paste(img, (x, y))
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    paths = save_inputs()
    build_sheet(paths)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source/provenance visual audit; no key derivation",
        "announcementImage": str(ANNOUNCEMENT),
        "magazinePdf": str(MAGAZINE),
        "reviewSheet": str(OUT_SHEET),
        "savedImages": paths,
        "findings": [
            "The first announcement image shows the physical OVERDOSE opener spread.",
            "That spread corresponds to magazine.pdf PDF pages 1-2, which precede the article body pages previously mapped as 75-80.",
            "The visible spread is not the page-76 Bukele/IMF corridor; it is the opener/title art with pills, cash, and a field illustration.",
            "Therefore the article source has an overlooked visual/provenance layer: opener pages 73-74 should be tracked separately from the page-75-to-80 body geometry.",
            "The announcement photo is too low-resolution and perspective-skewed to use as geometry truth, but it proves the opener spread is part of the public puzzle presentation.",
        ],
        "nextMove": "Add opener pages 73-74 to the active source model and inspect their pill/cash/field imagery only as a possible source-layer/orientation clue, not as direct key material.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Announcement Opening Spread Audit",
        "",
        "Scope: check the first announcement image against the full eight-page `magazine.pdf`. This is a source/provenance visual audit, not key derivation.",
        "",
        f"- Announcement image: `{ANNOUNCEMENT}`",
        f"- Review sheet: `{OUT_SHEET}`",
        "",
        "## Finding",
        "",
        "- The announcement photo shows Max holding the physical `OVERDOSE` opener spread.",
        "- That opener spread corresponds to `magazine.pdf` PDF pages 1-2, before the body pages previously mapped as article pages 75-80.",
        "- In internal article-page terms, the opener should be tracked as pages 73-74, followed by the body pages 75-80.",
        "- The page-76 Bukele/IMF corridor is still strongly supported, but the public announcement photo points first at the opener layer, not directly at page 76.",
        "",
        "## Consequence",
        "",
        "- Previous page-75-to-80 geometry work is not invalid, but it was missing the photographed opener spread.",
        "- The opener pages contain pills/cash/field imagery that may be part of the orientation/source-layer clue, especially because the Canva note also focused on pills not lining up.",
        "- The announcement photo itself is low-resolution and perspective-skewed, so it should not be geometry truth.",
        "",
        "## Next Best Move",
        "",
        "- Add pages 73-74 to the active source model and run a bounded visual inventory of opener pills/cash/field marks against the already-supported page-76/page-79 corridor.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
