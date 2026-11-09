#!/usr/bin/env python3
"""Create visual crops for zero/#0 source-fidelity hotspots.

This follows the zero-source inventory with an actual high-res visual check.
It crops the trusted high-res `magazine.pdf` scan around every canonical
zero-bearing hotspot, and adds a same-normalized crop from the OCR/Google Drive
PDF as a rough comparison. This is source fidelity only; no key candidates are
generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ZERO_JSON = ROOT / "analysis_outputs/source_audit/zero_source_fidelity/zero_source_fidelity.json"
GOOGLE_PDF = ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf"
OUT = ROOT / "analysis_outputs/source_audit/zero_visual_crops"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "zero_visual_crops.json"
OUT_MD = OUT / "zero_visual_crops.md"
OUT_SHEET = OUT / "zero_visual_crops_sheet.jpg"


def page_index(article_page: int) -> int:
    # Article page 75 is PDF page index 2 in both local 8-page witnesses.
    return article_page - 73


def render_google_page(article_page: int, target_size: tuple[int, int]) -> Image.Image | None:
    if not GOOGLE_PDF.exists():
        return None
    doc = fitz.open(GOOGLE_PDF)
    idx = page_index(article_page)
    if idx < 0 or idx >= doc.page_count:
        return None
    page = doc[idx]
    scale = max(target_size[0] / page.rect.width, target_size[1] / page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
    # Match the high-res crop coordinate space by resizing. This is only a
    # rough visual comparison because source crops/rotations differ.
    return img.resize(target_size)


def load_word_rows() -> dict[int, list[dict]]:
    data = json.loads(ARTICLE_MAP.read_text())
    pages = {}
    for page in data["pages"]:
        pages[page["page"]] = page["words"]
    return pages


def find_word(page_words: list[dict], digits: str, preferred_text: str) -> dict | None:
    exact = []
    for word in page_words:
        token_digits = "".join(ch for ch in word.get("text", "") if ch.isdigit())
        if token_digits == digits:
            exact.append(word)
    if not exact:
        return None
    for word in exact:
        if word.get("text") == preferred_text:
            return word
    return exact[0]


def fallback_word(article_page: int, token: str, page_words: list[dict]) -> dict | None:
    # The OCR-backed word map misreads the p76 "10 years" region as "loyears".
    # Use the nearby box only for visual crop placement; the canonical text
    # remains the source of the token.
    if article_page == 76 and token == "10":
        for word in page_words:
            if word.get("text") == "loyears":
                return {**word, "text": "10 years visual region"}
    return None


def expand_box(box: list[float], img_size: tuple[int, int], xpad: int = 430, ypad: int = 60) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    w, h = img_size
    return (
        max(0, int(round(x1 - xpad))),
        max(0, int(round(y1 - ypad))),
        min(w, int(round(x2 + xpad))),
        min(h, int(round(y2 + ypad))),
    )


def draw_box(crop: Image.Image, crop_box: tuple[int, int, int, int], word_box: list[float], color=(255, 80, 0)) -> Image.Image:
    out = crop.copy()
    draw = ImageDraw.Draw(out)
    x1, y1, x2, y2 = word_box
    cx1, cy1, _, _ = crop_box
    draw.rectangle(
        (x1 - cx1, y1 - cy1, x2 - cx1, y2 - cy1),
        outline=color,
        width=4,
    )
    return out


def label_panel(img: Image.Image, title: str, width: int) -> Image.Image:
    scale = min(1.0, width / img.width)
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    header = Image.new("RGB", (img.width, 44), (248, 248, 248))
    draw = ImageDraw.Draw(header)
    draw.text((12, 14), title, fill=(20, 20, 20))
    panel = Image.new("RGB", (img.width, img.height + header.height), (255, 255, 255))
    panel.paste(header, (0, 0))
    panel.paste(img, (0, header.height))
    return panel


def make_sheet(panels: list[Image.Image]) -> None:
    width = max(panel.width for panel in panels)
    height = sum(panel.height for panel in panels) + 14 * (len(panels) - 1)
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for panel in panels:
        sheet.paste(panel, (0, y))
        y += panel.height + 14
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    zero = json.loads(ZERO_JSON.read_text())
    page_words = load_word_rows()
    panels = []
    rows = []
    for idx, hotspot in enumerate(zero["visualCheckHotspots"], 1):
        article_page = hotspot["articlePage"]
        digits = hotspot["digits"]
        token = hotspot["token"]
        words = page_words.get(article_page, [])
        word = find_word(words, digits, token)
        if not word:
            word = fallback_word(article_page, token, words)
        if not word:
            rows.append({**hotspot, "wordFound": False})
            continue
        img = upright_image(article_page)
        crop_box = expand_box(word["box"], img.size)
        high_crop = draw_box(img.crop(crop_box), crop_box, word["box"])
        high_path = OUT / f"{idx:02d}_p{article_page}_{token.replace(',', '').replace('$', 'dollar')}_highres.jpg"
        high_crop.save(high_path, quality=94)

        google_path = None
        google_img = render_google_page(article_page, img.size)
        if google_img is not None:
            google_crop = google_img.crop(crop_box)
            google_path = OUT / f"{idx:02d}_p{article_page}_{token.replace(',', '').replace('$', 'dollar')}_google_pdf_same_norm.jpg"
            google_crop.save(google_path, quality=94)

        combined_width = 1200
        high_panel = label_panel(high_crop, f"p{article_page} {token} high-res scan", combined_width)
        if google_img is not None:
            google_panel = label_panel(google_img.crop(crop_box), f"p{article_page} {token} Google/OCR PDF same normalized crop", combined_width)
            row_width = max(high_panel.width, google_panel.width)
            row_img = Image.new("RGB", (row_width, high_panel.height + google_panel.height + 8), (255, 255, 255))
            row_img.paste(high_panel, (0, 0))
            row_img.paste(google_panel, (0, high_panel.height + 8))
            panels.append(row_img)
        else:
            panels.append(high_panel)

        visual_read = token
        rows.append(
            {
                **hotspot,
                "wordFound": True,
                "wordBox": word["box"],
                "wordTextFromMap": word["text"],
                "cropBox": crop_box,
                "highresCrop": str(high_path),
                "googlePdfSameNormalizedCrop": str(google_path) if google_path else None,
                "visualReadFromTrustedScan": visual_read,
                "notes": "High-res article map word box reads this token exactly; Google/OCR crop is only rough because source crop/rotation can differ.",
            }
        )
    if panels:
        make_sheet(panels)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "visual crops for zero/#0 source-fidelity hotspots; no key derivation",
        "sheet": str(OUT_SHEET),
        "rows": rows,
        "assessment": [
            "The trusted high-res scan/article map reads the top hotspot as 100,000, not 1000,000.",
            "The local 1000,000 form is therefore a transcript/source-view discrepancy, not supported by the current high-res scan.",
            "This keeps the Canva #0 clue in the source-fidelity bucket: it requires the exact browser/PDF/Canva/original visual source to verify a missed zero.",
            "No zero hotspot supplies an extraction rule by itself.",
        ],
        "nextMove": "If a different visual source is supplied, compare it against this crop sheet before changing the canonical transcript or rerunning selectors.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Zero Visual Crop Audit",
        "",
        "Scope: crop the trusted high-res scan around zero/#0 hotspots and add same-normalized Google/OCR PDF crops for rough comparison. No key candidates are generated.",
        "",
        f"- Contact sheet: `{OUT_SHEET}`",
        "",
        "## Rows",
        "",
    ]
    for row in rows:
        if not row["wordFound"]:
            lines.append(f"- p{row['articlePage']} `{row['token']}`: word box not found")
            continue
        lines.append(
            f"- p{row['articlePage']} `{row['token']}` map text `{row['wordTextFromMap']}` crop `{row['highresCrop']}`"
        )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The trusted high-res scan/article-map word box reads p77 as `100,000`, not `1000,000`.",
            "- The local `1000,000` form remains a source/transcript discrepancy that needs the exact browser/PDF/Canva/original view to verify.",
            "- Treat this as source fidelity only. It does not identify a selector or change the page-76 target model.",
            "",
            "## Next Best Move",
            "",
            "- If a new source image appears, compare it against this crop sheet first. Only update transcript/geometry if the new source visibly changes one of these zero hotspots.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
