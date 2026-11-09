#!/usr/bin/env python3
"""Audit which local sources can actually witness typography/font state.

This does not try to solve keys. It tests whether the user-provided comparison
PDFs can confirm/deny Typeka usage, and separates embedded/PDF text layers from
the printed page images and Word DOCM formatting witnesses.
"""

from __future__ import annotations

import json
import subprocess
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "typography_source_provenance.json"
OUT_MD = OUT / "typography_source_provenance.md"

PDFS = [
    ("issue24_best_scan", ROOT / "magazine.pdf"),
    ("issue24_desktop_scan", Path("private_inputs/Desktop/magazine.pdf")),
    ("issue26_comparison", Path("private_inputs/Desktop/Issue_26.pdf")),
    ("issue27_comparison", Path("private_inputs/Desktop/Issue_27.pdf")),
    ("bitcoin3_comparison", Path("private_inputs/Desktop/bitcoin3.pdf")),
    ("bitcoin4_issue24_witness", Path("private_inputs/Desktop/bitcoin4.pdf")),
]

DOCMS = [
    ("article_with_fonts", Path("private_inputs/Desktop/Article with Fonts.docm")),
    ("bold_docm", Path("private_inputs/Desktop/BOLD.docm")),
]

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def run_text(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return 127, ""
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def parse_pdffonts(output: str) -> list[dict]:
    rows = []
    for line in output.splitlines():
        line = line.rstrip()
        if not line or line.startswith("name ") or line.startswith("-"):
            continue
        parts = line.split()
        if not parts:
            continue
        # pdffonts columns are whitespace-separated for the local files here.
        rows.append(
            {
                "name": parts[0],
                "raw": line,
                "embedded": parts[4] if len(parts) > 4 else "",
                "subset": parts[5] if len(parts) > 5 else "",
                "unicode": parts[6] if len(parts) > 6 else "",
            }
        )
    return rows


def pdf_summary(label: str, path: Path) -> dict:
    item = {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        return item
    doc = fitz.open(path)
    page_images = []
    text_lengths = []
    for page in doc:
        images = []
        for img in page.get_images(full=True):
            info = doc.extract_image(img[0])
            images.append(
                {
                    "width": info.get("width"),
                    "height": info.get("height"),
                    "ext": info.get("ext"),
                    "bytes": len(info.get("image", b"")),
                }
            )
        page_images.append(images)
        text_lengths.append(len(page.get_text("text") or ""))

    code, fonts_out = run_text(["pdffonts", str(path)])
    fonts = parse_pdffonts(fonts_out)
    code_text, extracted = run_text(["pdftotext", str(path), "-"])
    item.update(
        {
            "pages": doc.page_count,
            "metadata": doc.metadata,
            "rotationSet": sorted({page.rotation for page in doc}),
            "pageTextLengths": text_lengths,
            "pdftotextChars": len(extracted.strip()),
            "fontRows": fonts,
            "fontNames": sorted({f["name"] for f in fonts}),
            "hasTypekaFontResource": any("Typeka" in f["name"] for f in fonts),
            "imageCounts": [len(images) for images in page_images],
            "embeddedImageSizes": [
                [{"width": img["width"], "height": img["height"], "ext": img["ext"]} for img in images]
                for images in page_images
            ],
            "isImageOnlyOrRasterWitness": not fonts or not any(len_ > 20 for len_ in text_lengths),
            "toolExit": {"pdffonts": code, "pdftotext": code_text},
        }
    )
    return item


def qn(local: str) -> str:
    return f"{{{NS['w']}}}{local}"


def run_font_state(run: ET.Element) -> tuple[str, bool, str]:
    props = run.find("w:rPr", NS)
    font = ""
    bold = False
    highlight = ""
    if props is not None:
        fonts = props.find("w:rFonts", NS)
        if fonts is not None:
            font = (
                fonts.get(qn("ascii"))
                or fonts.get(qn("hAnsi"))
                or fonts.get(qn("cs"))
                or fonts.get(qn("eastAsia"))
                or ""
            )
        bold = props.find("w:b", NS) is not None or props.find("w:bCs", NS) is not None
        hl = props.find("w:highlight", NS)
        if hl is not None:
            highlight = hl.get(qn("val")) or ""
    return font, bold, highlight


def docm_summary(label: str, path: Path) -> dict:
    item = {"label": label, "path": str(path), "exists": path.exists()}
    if not path.exists():
        return item
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        has_vba = "word/vbaProject.bin" in names
        doc_xml = zf.read("word/document.xml")
    root = ET.fromstring(doc_xml)

    font_chars: Counter[str] = Counter()
    state_chars: Counter[str] = Counter()
    font_runs: Counter[str] = Counter()
    highlights: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    total_runs = 0
    total_chars = 0
    for run in root.findall(".//w:r", NS):
        text = "".join(t.text or "" for t in run.findall("w:t", NS))
        if not text:
            continue
        font, bold, highlight = run_font_state(run)
        font_key = font or "(none)"
        state_key = f"{font_key}{'+bold' if bold else ''}{'+' + highlight if highlight else ''}"
        total_runs += 1
        total_chars += len(text)
        font_runs[font_key] += 1
        font_chars[font_key] += len(text)
        state_chars[state_key] += len(text)
        if highlight:
            highlights[highlight] += len(text)
        if len(samples[font_key]) < 8:
            samples[font_key].append(text.strip())

    item.update(
        {
            "hasVbaProject": has_vba,
            "totalRuns": total_runs,
            "totalChars": total_chars,
            "fontRuns": dict(font_runs.most_common()),
            "fontChars": dict(font_chars.most_common()),
            "fontStateChars": dict(state_chars.most_common()),
            "highlightChars": dict(highlights.most_common()),
            "typekaFontChars": {
                k: v for k, v in font_chars.items() if "Typeka" in k
            },
            "typekaFontRuns": {
                k: v for k, v in font_runs.items() if "Typeka" in k
            },
            "fontSamples": {k: [s for s in v if s] for k, v in samples.items()},
        }
    )
    return item


def main() -> None:
    pdfs = [pdf_summary(label, path) for label, path in PDFS]
    docms = [docm_summary(label, path) for label, path in DOCMS]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source typography/font provenance only; no key derivation",
        "pdfs": pdfs,
        "docms": docms,
        "conclusion": {
            "pdfFontWitness": "The comparison PDFs are raster/image witnesses, not font witnesses. Issue 24 only exposes Helvetica OCR/text-layer resources, not visible printed Typeka fonts.",
            "docmFontWitness": "Article with Fonts.docm is the only local source that directly records Typeka/Typeka Mix/bold Typeka states.",
            "risk": "Claims that other Max articles do or do not use Typeka cannot be proven from these local comparison PDFs alone because their visible type is flattened into images.",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Typography Source Provenance",
        "",
        "Scope: determine which local sources can actually witness font usage, especially Typeka / Typeka Mix / Typeka-bold. This is a provenance check only; no key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## PDF Font Evidence",
        "",
    ]
    for item in pdfs:
        if not item["exists"]:
            lines.append(f"- `{item['label']}` missing at `{item['path']}`")
            continue
        lines.append(
            f"- `{item['label']}`: pages={item['pages']}, fonts={item['fontNames'] or 'none'}, "
            f"pdftotextChars={item['pdftotextChars']}, imageCounts={item['imageCounts']}, "
            f"TypekaFontResource={item['hasTypekaFontResource']}"
        )
        if item["fontRows"]:
            for row in item["fontRows"][:8]:
                lines.append(f"  - font row: `{row['raw']}`")

    lines.extend(["", "## DOCM Font Evidence", ""])
    for item in docms:
        if not item["exists"]:
            lines.append(f"- `{item['label']}` missing at `{item['path']}`")
            continue
        lines.append(
            f"- `{item['label']}`: runs={item['totalRuns']}, chars={item['totalChars']}, "
            f"hasVBA={item['hasVbaProject']}, Typeka chars={item['typekaFontChars']}"
        )
        lines.append(f"  - font chars: `{item['fontChars']}`")
        lines.append(f"  - highlight chars: `{item['highlightChars']}`")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- `Article with Fonts.docm` remains the only local source that directly records the Typeka family states.",
            "- `magazine.pdf` does not embed visible Typeka fonts; the only reported PDF fonts are Helvetica OCR/text-layer resources. That layer should not be interpreted as printed typography.",
            "- `Issue_26.pdf`, `Issue_27.pdf`, and `bitcoin3.pdf` expose no useful embedded Typeka font evidence; they cannot prove or disprove Typeka usage by metadata.",
            "- `bitcoin4.pdf` is a low-resolution Issue 24 witness. It can preserve visual style, but it still does not expose printed Typeka as a usable font layer.",
            "- The existing visual comparison still matters: those comparison articles show loud OVERDOSE art, but not the same Issue 24 orange/grey highlighted text grammar. Font uniqueness needs original layout/source files or better visual OCR, not these flattened PDFs.",
            "- Next best move: treat Typeka as a confirmed Issue 24 formatting witness only inside `Article with Fonts.docm`; do not run more Typeka-only selectors unless a separate instruction tells us which font state to use.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
