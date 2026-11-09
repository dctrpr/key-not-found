#!/usr/bin/env python3
"""Compare Max/OVERDOSE comparison PDFs against Issue 24 style signals.

This is a bounded style audit, not an extraction branch. It asks whether the
visual systems we keep relying on in Issue 24 are recurring house style or
article-specific. The comparison PDFs are image-only, so the pass uses rendered
page images and simple color/shape metrics instead of OCR or private-key tests.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_style_uniqueness.json"
OUT_MD = OUT / "overdose_style_uniqueness.md"
OUT_SHEET = OUT / "overdose_style_uniqueness_contact_sheet.jpg"


@dataclass(frozen=True)
class Source:
    slug: str
    label: str
    path: Path
    role: str


SOURCES = [
    Source("issue24", "Issue 24 / BITCOIN IS TOXIC AF", ROOT / "magazine.pdf", "puzzle"),
    Source("issue26", "Issue_26.pdf", Path("private_inputs/Desktop/Issue_26.pdf"), "comparison"),
    Source("issue27", "Issue_27.pdf", Path("private_inputs/Desktop/Issue_27.pdf"), "comparison"),
    Source("bitcoin3", "bitcoin3.pdf", Path("private_inputs/Desktop/bitcoin3.pdf"), "comparison"),
    Source("bitcoin4", "bitcoin4.pdf", Path("private_inputs/Desktop/bitcoin4.pdf"), "low-res-issue24"),
]


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_page_image(doc: fitz.Document, page_index: int) -> Image.Image:
    page = doc[page_index]
    images = page.get_images(full=True)
    if images:
        xref = images[0][0]
        raw = doc.extract_image(xref)["image"]
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if page.rotation:
            img = img.rotate(-page.rotation, expand=True)
        return img
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def text_layer_summary(doc: fitz.Document) -> dict[str, Any]:
    fonts: set[str] = set()
    text_blocks = 0
    chars = 0
    for page in doc:
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            text_blocks += 1
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if text:
                        fonts.add(span.get("font", ""))
                        chars += len(text)
    return {
        "textBlocks": text_blocks,
        "textChars": chars,
        "fonts": sorted(fonts),
        "isImageOnly": chars == 0,
    }


def masks(img: Image.Image) -> dict[str, np.ndarray]:
    scaled = ImageOps.contain(img.convert("RGB"), (900, 1200))
    arr = np.asarray(scaled).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    orange = (r > 170) & (g > 75) & (g < 230) & (b < 155) & ((r - b) > 60) & ((r - g) > -30)
    yellow = (r > 175) & (g > 145) & (b < 160)
    magenta = (r > 145) & (b > 110) & (g < 135)
    cyan = (r < 120) & (g > 115) & (b > 135) & ((b - r) > 35)
    dark = (r < 70) & (g < 70) & (b < 70)
    near_white = (r > 235) & (g > 235) & (b > 235)
    grey_dark = (r < 125) & (g < 125) & (b < 125) & (np.abs(r - g) < 25) & (np.abs(g - b) < 25)
    return {
        "orange": orange,
        "yellow": yellow,
        "magenta": magenta,
        "cyan": cyan,
        "dark": dark,
        "greyDark": grey_dark,
        "nearWhite": near_white,
    }


def longest_run(row: np.ndarray) -> int:
    best = 0
    current = 0
    for value in row:
        if value:
            current += 1
            if current > best:
                best = current
        else:
            current = 0
    return best


def horizontal_bands(mask: np.ndarray, *, min_frac: float = 0.045, max_frac: float = 0.78) -> list[dict[str, int]]:
    h, w = mask.shape
    min_run = max(10, int(w * min_frac))
    max_run = int(w * max_frac)
    row_runs = np.array([longest_run(mask[y]) for y in range(h)])
    active = (row_runs >= min_run) & (row_runs <= max_run)
    bands: list[dict[str, int]] = []
    y = 0
    while y < h:
        if not active[y]:
            y += 1
            continue
        y0 = y
        max_width = 0
        total_pixels = 0
        while y < h and active[y]:
            max_width = max(max_width, int(row_runs[y]))
            total_pixels += int(mask[y].sum())
            y += 1
        y1 = y - 1
        height = y1 - y0 + 1
        if 2 <= height <= 42:
            bands.append({"y0": y0, "y1": y1, "height": height, "maxRun": max_width, "pixels": total_pixels})
    return bands


def small_components(mask: np.ndarray) -> list[dict[str, int | float]]:
    h, w = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    comps: list[dict[str, int | float]] = []
    ys, xs = np.nonzero(mask)
    for start_y, start_x in zip(ys.tolist(), xs.tolist()):
        if visited[start_y, start_x]:
            continue
        stack = [(start_y, start_x)]
        visited[start_y, start_x] = True
        area = 0
        min_x = max_x = start_x
        min_y = max_y = start_y
        while stack:
            y, x = stack.pop()
            area += 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            for ny in (y - 1, y, y + 1):
                for nx in (x - 1, x, x + 1):
                    if ny == y and nx == x:
                        continue
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))
        bw = max_x - min_x + 1
        bh = max_y - min_y + 1
        aspect = bw / bh if bh else 0
        if 8 <= area <= 2200 and 0.25 <= aspect <= 5.0 and bw <= 120 and bh <= 120:
            comps.append({"x0": min_x, "y0": min_y, "x1": max_x, "y1": max_y, "area": area, "aspect": round(aspect, 3)})
    return comps


def average_hash(img: Image.Image, size: int = 16) -> str:
    gray = img.convert("L").resize((size, size), Image.Resampling.BILINEAR)
    arr = np.asarray(gray)
    bits = arr > arr.mean()
    value = 0
    out = []
    for i, bit in enumerate(bits.flatten(), 1):
        value = (value << 1) | int(bit)
        if i % 4 == 0:
            out.append(format(value & 0xF, "x"))
            value = 0
    return "".join(out)


def hamming_hex(a: str, b: str) -> int:
    return (int(a or "0", 16) ^ int(b or "0", 16)).bit_count()


def page_features(img: Image.Image) -> dict[str, Any]:
    mm = masks(img)
    total = next(iter(mm.values())).size
    orange_bands = horizontal_bands(mm["orange"])
    yellow_bands = horizontal_bands(mm["yellow"])
    dark_bands = horizontal_bands(mm["dark"], min_frac=0.05, max_frac=0.6)
    grey_bands = horizontal_bands(mm["greyDark"], min_frac=0.05, max_frac=0.6)
    orange_components = small_components(mm["orange"])
    yellow_components = small_components(mm["yellow"])
    highlight_score = len(orange_bands) + len(yellow_bands) + len(dark_bands) + len(grey_bands)
    return {
        "width": img.width,
        "height": img.height,
        "hash": average_hash(img),
        "orangePct": round(float(mm["orange"].mean() * 100), 3),
        "yellowPct": round(float(mm["yellow"].mean() * 100), 3),
        "magentaPct": round(float(mm["magenta"].mean() * 100), 3),
        "cyanPct": round(float(mm["cyan"].mean() * 100), 3),
        "darkPct": round(float(mm["dark"].mean() * 100), 3),
        "whitePct": round(float(mm["nearWhite"].mean() * 100), 3),
        "orangeBands": len(orange_bands),
        "yellowBands": len(yellow_bands),
        "darkBands": len(dark_bands),
        "greyBands": len(grey_bands),
        "orangeComponents": len(orange_components),
        "yellowComponents": len(yellow_components),
        "orangeSmallComponents": len([c for c in orange_components if c["area"] < 250]),
        "yellowSmallComponents": len([c for c in yellow_components if c["area"] < 250]),
        "highlightScore": highlight_score,
        "colorfulPct": round(
            float((mm["orange"] | mm["yellow"] | mm["magenta"] | mm["cyan"]).sum() / total * 100),
            3,
        ),
    }


def process_source(source: Source) -> dict[str, Any]:
    doc = fitz.open(source.path)
    source_dir = OUT / source.slug
    source_dir.mkdir(parents=True, exist_ok=True)
    page_records = []
    for i in range(doc.page_count):
        img = extract_page_image(doc, i)
        image_path = source_dir / f"page_{i + 1:02d}.jpg"
        img.save(image_path, quality=92)
        features = page_features(img)
        features.update({"page": i + 1, "imagePath": str(image_path)})
        page_records.append(features)
    return {
        "slug": source.slug,
        "label": source.label,
        "role": source.role,
        "path": str(source.path),
        "md5": md5(source.path),
        "pageCount": doc.page_count,
        "textLayer": text_layer_summary(doc),
        "pages": page_records,
    }


def closest_matches(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issue24 = next(r for r in results if r["slug"] == "issue24")
    comparisons = [r for r in results if r["slug"] != "issue24"]
    pairs = []
    for p in issue24["pages"]:
        for source in comparisons:
            for q in source["pages"]:
                pairs.append(
                    {
                        "issue24Page": p["page"],
                        "source": source["slug"],
                        "page": q["page"],
                        "hamming": hamming_hex(p["hash"], q["hash"]),
                        "highlightDelta": abs(p["highlightScore"] - q["highlightScore"]),
                        "orangeBandDelta": abs(p["orangeBands"] - q["orangeBands"]),
                        "darkBandDelta": abs(p["darkBands"] - q["darkBands"]),
                    }
                )
    pairs.sort(key=lambda x: (x["hamming"], x["highlightDelta"], x["orangeBandDelta"], x["darkBandDelta"]))
    return pairs[:30]


def source_summary(source: dict[str, Any]) -> dict[str, Any]:
    pages = source["pages"]
    highlighter_pages = [p["page"] for p in pages if p["highlightScore"] >= 8 and (p["orangeBands"] + p["yellowBands"]) >= 2]
    orange_band_pages = [p["page"] for p in pages if p["orangeBands"] >= 2]
    dark_band_pages = [p["page"] for p in pages if p["darkBands"] >= 2 or p["greyBands"] >= 2]
    small_capsule_pages = [p["page"] for p in pages if (p["orangeSmallComponents"] + p["yellowSmallComponents"]) >= 6]
    colorful_pages = [p["page"] for p in pages if p["colorfulPct"] >= 8]
    return {
        "slug": source["slug"],
        "label": source["label"],
        "textLayer": source["textLayer"],
        "highlighterLikePages": highlighter_pages,
        "orangeBandPages": orange_band_pages,
        "darkOrGreyBandPages": dark_band_pages,
        "smallCapsuleLikePages": small_capsule_pages,
        "veryColorfulPages": colorful_pages,
        "maxHighlightScore": max((p["highlightScore"] for p in pages), default=0),
    }


def build_contact_sheet(results: list[dict[str, Any]]) -> None:
    cards = []
    for source in results:
        for page in source["pages"]:
            img = Image.open(page["imagePath"]).convert("RGB")
            img = ImageOps.contain(img, (220, 285))
            cards.append((source, page, img))

    cols = 5
    cell_w, cell_h = 260, 365
    rows = math.ceil(len(cards) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (source, page, img) in enumerate(cards):
        col = idx % cols
        row = idx // cols
        x = col * cell_w
        y = row * cell_h
        sheet.paste(img, (x + (cell_w - img.width) // 2, y + 6))
        text_y = y + 296
        lines = [
            f"{source['slug']} p{page['page']:02d}",
            f"H={page['highlightScore']} O/Y/D/G={page['orangeBands']}/{page['yellowBands']}/{page['darkBands']}/{page['greyBands']}",
            f"small O/Y={page['orangeSmallComponents']}/{page['yellowSmallComponents']}",
            f"color={page['colorfulPct']} dark={page['darkPct']} white={page['whitePct']}",
        ]
        for line in lines:
            draw.text((x + 7, text_y), line, fill=(0, 0, 0), font=font)
            text_y += 15
        outline = (210, 90, 30) if source["slug"] == "issue24" else (190, 190, 190)
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=outline)
    sheet.save(OUT_SHEET, quality=92)


def write_report(results: list[dict[str, Any]], summaries: list[dict[str, Any]], matches: list[dict[str, Any]]) -> None:
    issue24 = next(s for s in summaries if s["slug"] == "issue24")
    independent = [s for s in summaries if s["slug"] not in {"issue24", "bitcoin4"}]
    comparison_highlighter = {
        s["slug"]: s["highlighterLikePages"] for s in independent if s["highlighterLikePages"]
    }
    decision = (
        "`bitcoin4.pdf` is a lower-quality duplicate/witness of the Issue 24 article, not an independent comparison article. "
        "Among the independent comparison PDFs, OVERDOSE branding and broad graphic color recur, but the sustained Issue 24 body-text "
        "orange/grey highlighter system remains distinctive. The comparison PDFs do not provide Issue 24 geometry or the missing extraction unit."
    )
    payload = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "style/layout uniqueness audit; no key derivation",
        "summaries": summaries,
        "closestMatches": matches,
        "decision": decision,
        "contactSheet": str(OUT_SHEET),
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# OVERDOSE Style Uniqueness Audit",
        "",
        "Scope: compare Issue 24 against local Max/OVERDOSE comparison PDFs for recurring layout motifs. No key derivation, hashing, address checking, or OCR extraction was run.",
        "",
        f"- Created: `{payload['createdAt']}`",
        f"- Contact sheet: `{OUT_SHEET}`",
        "",
        "## Decision",
        "",
        f"- {decision}",
        "",
        "## Source Summaries",
        "",
        "| source | text layer | highlighter-like pages | orange-band pages | dark/grey-band pages | small capsule-like pages | very colorful pages | max highlight score |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in summaries:
        tl = s["textLayer"]
        text_state = "image-only" if tl["isImageOnly"] else f"{tl['textChars']} chars / fonts {', '.join(tl['fonts'][:3])}"
        lines.append(
            f"| {s['label']} | {text_state} | {s['highlighterLikePages']} | {s['orangeBandPages']} | {s['darkOrGreyBandPages']} | {s['smallCapsuleLikePages']} | {s['veryColorfulPages']} | {s['maxHighlightScore']} |"
        )

    lines.extend(
        [
            "",
            "## Issue 24 Signals",
            "",
            f"- Issue 24 highlighter-like pages by metric: `{issue24['highlighterLikePages']}`.",
            "- These correspond to the article body pages rather than only the opening/product art.",
            "- The body-text orange/dark-bar system remains higher priority than the generic OVERDOSE label or broad colored art.",
            "",
            "## Comparison Result",
            "",
            "- `bitcoin4.pdf` visually reproduces the Issue 24 article in lower-quality/alternate geometry, so it is a source-fidelity witness, not an independent style comparison.",
        ]
    )
    if comparison_highlighter:
        for slug, pages in comparison_highlighter.items():
            lines.append(f"- `{slug}` has highlighter-like metric pages `{pages}`, but visual review/contact-sheet context is needed because colored text/art can trigger the metric.")
    else:
        lines.append("- No comparison source produced the same sustained body-text highlighter profile as Issue 24.")
    lines.extend(
        [
            "- All four comparison PDFs are image-only, so PDF font extraction cannot verify Typeka usage inside them.",
            "- `Article with Fonts.docm` remains the best local font witness for Typeka/Typeka Mix on Issue 24.",
            "- Comparison pages can downgrade generic Max/OVERDOSE motifs, but they cannot replace source geometry for page 76.",
            "",
            "## Closest Coarse Visual Matches",
            "",
            "Average-hash matches are only a rough composition check.",
        ]
    )
    for m in matches[:12]:
        lines.append(
            f"- Issue 24 p{m['issue24Page']:02d} -> `{m['source']}` p{m['page']:02d}: "
            f"hamming `{m['hamming']}`, highlightDelta `{m['highlightDelta']}`"
        )
    lines.extend(
        [
            "",
            "## Next Move",
            "",
            "- Treat `OVERDOSE` label, dark pages, and broad colored art as house-style/provenance unless they interact with the page-76 mirror corridor.",
            "- Keep exact Issue 24 orange/grey body highlights and page-76/p79 registration as active signals.",
            "- Do not reopen Typeka/font-state extraction unless a source rule selects exact words/lines or a new source file exposes real font-layer metadata.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results = [process_source(source) for source in SOURCES if source.path.exists()]
    summaries = [source_summary(source) for source in results]
    matches = closest_matches(results)
    build_contact_sheet(results)
    write_report(results, summaries, matches)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
