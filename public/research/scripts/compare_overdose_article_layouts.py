#!/usr/bin/env python3
"""Compare local Max/OVERDOSE article PDFs as visual-layout witnesses."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs" / "comparison_articles"


@dataclass(frozen=True)
class Source:
    slug: str
    label: str
    path: Path
    note: str


SOURCES = [
    Source(
        "issue24_toxic_af",
        "Issue 24 / BITCOIN IS TOXIC AF",
        ROOT / "magazine.pdf",
        "puzzle source, best local scan",
    ),
    Source(
        "issue26",
        "Issue_26.pdf",
        Path("private_inputs/Desktop/Issue_26.pdf"),
        "user-provided comparison article",
    ),
    Source(
        "bitcoin3",
        "bitcoin3.pdf",
        Path("private_inputs/Desktop/bitcoin3.pdf"),
        "user-provided comparison article",
    ),
]


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_page_image(doc: fitz.Document, page_index: int) -> Image.Image:
    """Extract the embedded page image when present, respecting PDF rotation."""
    page = doc[page_index]
    images = page.get_images(full=True)
    if images:
        xref = images[0][0]
        raw = doc.extract_image(xref)["image"]
        import io

        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if page.rotation:
            img = img.rotate(-page.rotation, expand=True)
        return img

    # Fallback for non-image-only PDFs.
    zoom = 3
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def mask_metrics(img: Image.Image) -> dict:
    small = img.resize((max(1, img.width // 4), max(1, img.height // 4)))
    arr = np.asarray(small).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    total = arr.shape[0] * arr.shape[1]

    orange = (r > 175) & (g > 95) & (g < 235) & (b < 135) & ((r - b) > 70)
    yellow = (r > 180) & (g > 150) & (b < 145)
    cyan = (r < 110) & (g > 120) & (b > 140) & ((b - r) > 45)
    magenta = (r > 150) & (b > 120) & (g < 120)
    dark = (r < 48) & (g < 48) & (b < 48)
    near_white = (r > 235) & (g > 235) & (b > 235)

    # A coarse row/column density signature helps spot page-level layout reuse
    # without depending on OCR.
    ink = ~near_white
    row_profile = ink.mean(axis=1)
    col_profile = ink.mean(axis=0)
    dense_rows = int((row_profile > 0.35).sum())
    dense_cols = int((col_profile > 0.35).sum())

    return {
        "orangePct": round(float(orange.mean() * 100), 3),
        "yellowPct": round(float(yellow.mean() * 100), 3),
        "cyanPct": round(float(cyan.mean() * 100), 3),
        "magentaPct": round(float(magenta.mean() * 100), 3),
        "darkPct": round(float(dark.mean() * 100), 3),
        "whitePct": round(float(near_white.mean() * 100), 3),
        "denseRows": dense_rows,
        "denseCols": dense_cols,
        "colorScore": round(
            float((orange | yellow | cyan | magenta).mean() * 100),
            3,
        ),
    }


def average_hash(img: Image.Image, size: int = 16) -> str:
    gray = img.convert("L").resize((size, size), Image.Resampling.BILINEAR)
    arr = np.asarray(gray)
    bits = arr > arr.mean()
    value = 0
    out = []
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
        if value.bit_length() >= 4:
            out.append(format(value & 0xF, "x"))
            value = 0
    return "".join(out)


def hamming_hex(a: str, b: str) -> int:
    width = max(len(a), len(b)) * 4
    return (int(a or "0", 16) ^ int(b or "0", 16)).bit_count() if width else 0


def make_contact_sheet(source_dir: Path, page_records: list[dict], out_path: Path) -> None:
    thumbs = []
    for record in page_records:
        img = Image.open(record["imagePath"]).convert("RGB")
        thumb_w = 330
        thumb_h = int(img.height * thumb_w / img.width)
        img = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        thumbs.append((record, img))

    cols = 2
    label_h = 72
    gap = 18
    rows = math.ceil(len(thumbs) / cols)
    cell_w = 330
    cell_h = max((img.height for _, img in thumbs), default=430) + label_h
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (record, img) in enumerate(thumbs):
        row, col = divmod(idx, cols)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + gap)
        draw.rectangle([x - 1, y - 1, x + cell_w + 1, y + img.height + 1], outline=(180, 180, 180))
        sheet.paste(img, (x, y))
        text_y = y + img.height + 8
        label = (
            f"p{record['page']}  color={record['metrics']['colorScore']}% "
            f"orange={record['metrics']['orangePct']}% cyan={record['metrics']['cyanPct']}%"
        )
        draw.text((x, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((x, text_y + 16), f"dark={record['metrics']['darkPct']}% white={record['metrics']['whitePct']}%", fill=(0, 0, 0), font=font)
    sheet.save(out_path, quality=92)


def process_source(source: Source) -> dict:
    doc = fitz.open(source.path)
    source_dir = OUT / source.slug
    source_dir.mkdir(parents=True, exist_ok=True)
    pages = []
    for i in range(doc.page_count):
        img = extract_page_image(doc, i)
        out_img = source_dir / f"page_{i + 1:02d}.jpg"
        img.save(out_img, quality=92)
        images = doc[i].get_images(full=True)
        embedded = []
        for raw_img in images:
            info = doc.extract_image(raw_img[0])
            embedded.append(
                {
                    "width": info.get("width"),
                    "height": info.get("height"),
                    "ext": info.get("ext"),
                    "bytes": len(info.get("image", b"")),
                }
            )
        pages.append(
            {
                "page": i + 1,
                "imagePath": str(out_img),
                "width": img.width,
                "height": img.height,
                "rotation": doc[i].rotation,
                "embeddedImages": embedded,
                "metrics": mask_metrics(img),
                "averageHash": average_hash(img),
            }
        )
    contact = source_dir / "contact_sheet.jpg"
    make_contact_sheet(source_dir, pages, contact)
    return {
        "slug": source.slug,
        "label": source.label,
        "path": str(source.path),
        "note": source.note,
        "md5": md5(source.path),
        "pages": doc.page_count,
        "metadata": doc.metadata,
        "contactSheet": str(contact),
        "pageRecords": pages,
    }


def compare_hashes(results: list[dict]) -> list[dict]:
    puzzle = next(item for item in results if item["slug"] == "issue24_toxic_af")
    others = [item for item in results if item["slug"] != "issue24_toxic_af"]
    pairs = []
    for p in puzzle["pageRecords"]:
        for source in others:
            for q in source["pageRecords"]:
                pairs.append(
                    {
                        "puzzlePage": p["page"],
                        "otherSource": source["slug"],
                        "otherPage": q["page"],
                        "hamming": hamming_hex(p["averageHash"], q["averageHash"]),
                        "colorDelta": round(abs(p["metrics"]["colorScore"] - q["metrics"]["colorScore"]), 3),
                        "darkDelta": round(abs(p["metrics"]["darkPct"] - q["metrics"]["darkPct"]), 3),
                    }
                )
    pairs.sort(key=lambda item: (item["hamming"], item["colorDelta"], item["darkDelta"]))
    return pairs[:20]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = [process_source(source) for source in SOURCES]
    similar = compare_hashes(results)
    report = {"sources": results, "closestHashPairs": similar}
    (OUT / "comparison_layout_audit.json").write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Max Article Layout Comparison",
        "",
        "Scope: compare user-provided Max article PDFs against the Issue 24 puzzle scan as visual/layout witnesses. These PDFs are image-only, so this pass uses embedded page images and color/layout metrics, not text OCR.",
        "",
        "## Sources",
        "",
    ]
    for source in results:
        lines.extend(
            [
                f"### {source['label']}",
                "",
                f"- path: `{source['path']}`",
                f"- MD5: `{source['md5']}`",
                f"- pages: `{source['pages']}`",
                f"- note: {source['note']}",
                f"- contact sheet: `{source['contactSheet']}`",
                "- page metrics:",
            ]
        )
        for page in source["pageRecords"]:
            m = page["metrics"]
            lines.append(
                f"  - p{page['page']:02d}: image `{page['width']}x{page['height']}`, "
                f"orange/yellow/cyan/magenta `{m['orangePct']}/{m['yellowPct']}/{m['cyanPct']}/{m['magentaPct']}%`, "
                f"dark/white `{m['darkPct']}/{m['whitePct']}%`, colorScore `{m['colorScore']}%`"
            )
        lines.append("")

    lines.extend(
        [
            "## Closest Coarse Visual Matches",
            "",
            "These are average-hash matches only. They help spot reused page composition, not proof of puzzle relation.",
        ]
    )
    for pair in similar[:12]:
        lines.append(
            f"- puzzle p{pair['puzzlePage']:02d} ↔ {pair['otherSource']} p{pair['otherPage']:02d}: "
            f"hamming `{pair['hamming']}`, colorDelta `{pair['colorDelta']}`, darkDelta `{pair['darkDelta']}`"
        )

    lines.extend(
        [
            "",
            "## Preliminary Assessment",
            "",
            "- The two comparison PDFs use the same 2040 x 2805 embedded JPEG page format as the public/OCR article PDF branch, not the 2544 x 3264 best-scan geometry of `magazine.pdf`.",
            "- The comparison set should help separate recurring Max/OVERDOSE layout conventions from article-specific puzzle marks.",
            "- Any motif appearing across these comparison articles, especially orange/yellow highlights or large black editorial blocks, should be downgraded as house style unless it interacts with the page-76 mirror geometry.",
            "- Any motif unique to Issue 24, especially the p76/p79 mirror corridor, p80 package-copy system, cyan `MNBILLION`, or page-76 Bukele/IMF/$1 billion cluster, remains higher priority.",
        ]
    )
    (OUT / "comparison_layout_audit.md").write_text("\n".join(lines) + "\n")

    print(OUT / "comparison_layout_audit.md")
    print(OUT / "comparison_layout_audit.json")
    for source in results:
        print(source["contactSheet"])


if __name__ == "__main__":
    main()
