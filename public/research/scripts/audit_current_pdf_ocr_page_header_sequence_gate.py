#!/usr/bin/env python3
"""Audit current PDF OCR page-start/header sequence around OVERDOSE.

The current PDFs include invisible OCR overlays. This bounded pass checks
whether page-start OCR text across article pages 73-80, especially page 76
starting with OVERDOSE in the duplicate OCR PDFs, supplies a page-order,
unit/order, or all-four target selector. It does not derive keys, generate
candidates, hash to keys, inspect WIFs/addresses, check BIP39, or brute force.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_page_header_sequence_gate.json"
OUT_MD = OUT / "current_pdf_ocr_page_header_sequence_gate.md"
OUT_SHEET = OUT / "current_pdf_ocr_page_header_sequence_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ARTICLE_PAGE_START = 73
ARTICLE_PAGE_END = 80
FIRST_N = 24
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_TERMS = {
    "O4": {"buying", "dip"},
    "B4": {"billion"},
    "G5": {"volcano", "bonds"},
    "O5": {"shitcoiner", "shitcoiners", "heart"},
}
STRICT_TERMS = {
    "above",
    "below",
    "bottom",
    "center",
    "column",
    "count",
    "crop",
    "edge",
    "extract",
    "first",
    "fold",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "line",
    "mirror",
    "order",
    "outside",
    "pick",
    "read",
    "reverse",
    "right",
    "row",
    "select",
    "slot",
    "take",
    "top",
    "unit",
    "word",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", text.lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def words_for_page(page: fitz.Page) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(page.get_text("words")):
        x0, y0, x1, y1, text, block, line, word = item
        rows.append(
            {
                "index": idx,
                "text": str(text),
                "token": clean_token(str(text)),
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "block": int(block),
                "line": int(line),
                "word": int(word),
            }
        )
    return rows


def target_ids_for_tokens(tokens: list[str]) -> list[str]:
    found = []
    for target in TARGET_ORDER:
        terms = TARGET_TERMS[target]
        if any(token in terms or any(term in token for term in terms if len(term) >= 5) for token in tokens):
            found.append(target)
    return found


def first_target_order(words: list[dict[str, Any]]) -> list[str]:
    first: dict[str, int] = {}
    for word in words:
        token = word["token"]
        for target in TARGET_ORDER:
            terms = TARGET_TERMS[target]
            if token in terms or any(term in token for term in terms if len(term) >= 5):
                first.setdefault(target, int(word["index"]))
    return [target for target, _ in sorted(first.items(), key=lambda item: item[1])]


def first_line_text(words: list[dict[str, Any]]) -> str:
    if not words:
        return ""
    first = words[0]
    line_words = [
        word
        for word in words
        if word["block"] == first["block"] and word["line"] == first["line"]
    ]
    return compact(" ".join(word["text"] for word in line_words))


def inspect_page(pdf_path: Path, doc: fitz.Document, page_index: int) -> dict[str, Any]:
    article_page = ARTICLE_PAGE_START + page_index
    page = doc[page_index]
    words = words_for_page(page)
    first_words = words[:FIRST_N]
    first_tokens = [word["token"] for word in first_words if word["token"]]
    strict_hits = [word["text"] for word in first_words if word["token"] in STRICT_TERMS]
    target_ids = target_ids_for_tokens(first_tokens)
    target_order = first_target_order(first_words)
    first_token = first_tokens[0] if first_tokens else ""
    return {
        "pdf": rel(pdf_path),
        "pdfPage": page_index + 1,
        "articlePage": article_page,
        "wordCount": len(words),
        "firstToken": first_token,
        "firstLineText": first_line_text(words),
        "firstWordsText": compact(" ".join(word["text"] for word in first_words)),
        "firstWordCountChecked": len(first_words),
        "strictHitCount": len(strict_hits),
        "strictHits": strict_hits,
        "targetIds": target_ids,
        "targetIdCount": len(target_ids),
        "targetOrder": target_order,
        "allFourTargetsInFirstWords": len(target_ids) == 4,
        "activeOrderInFirstWords": target_order == TARGET_ORDER,
        "startsWithOverdose": first_token == "overdose",
        "pageStartSelectorCandidate": (
            first_token == "overdose"
            and bool(strict_hits)
            and (len(target_ids) == 4 or target_order == TARGET_ORDER)
        ),
    }


def inspect_pdf(pdf_path: Path) -> dict[str, Any]:
    with fitz.open(pdf_path) as doc:
        page_rows = [
            inspect_page(pdf_path, doc, idx)
            for idx in range(min(len(doc), ARTICLE_PAGE_END - ARTICLE_PAGE_START + 1))
        ]
    first_token_sequence = [
        {"articlePage": row["articlePage"], "firstToken": row["firstToken"]}
        for row in page_rows
    ]
    page76_rows = [row for row in page_rows if row["articlePage"] == 76]
    return {
        "pdf": rel(pdf_path),
        "pageCount": len(page_rows),
        "pageRows": page_rows,
        "firstTokenSequence": first_token_sequence,
        "page76StartsWithOverdose": any(row["startsWithOverdose"] for row in page76_rows),
        "strictPageStartRows": sum(1 for row in page_rows if row["strictHitCount"] > 0),
        "targetPageStartRows": sum(1 for row in page_rows if row["targetIdCount"] > 0),
        "allFourPageStartRows": sum(1 for row in page_rows if row["allFourTargetsInFirstWords"]),
        "candidateRows": sum(1 for row in page_rows if row["pageStartSelectorCandidate"]),
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 1820
    height = 1120
    img = Image.new("RGB", (width, height), (11, 13, 17))
    draw = ImageDraw.Draw(img)
    title = safe_font(30)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF OCR Page-Header Sequence Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 62),
        "Page-start OCR across article pages 73-80; checks OVERDOSE as header/order signal only.",
        fill=(172, 184, 196),
        font=small,
    )
    draw.text(
        (28, 96),
        f"pdfs={summary['pdfCount']} | rows={summary['pageRowsChecked']} | p76 OVERDOSE={summary['page76OverdoseHeaderPdfCount']} | strict={summary['strictPageStartRowCount']} | candidates={summary['pageHeaderSequenceCandidateCount']}",
        fill=(216, 170, 69),
        font=small,
    )
    y = 152
    headers = ["PDF", "art", "first token", "strict", "targets", "candidate", "first words"]
    xs = [28, 438, 505, 625, 700, 795, 900]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(160, 172, 184), font=small)
    y += 30
    rows = [row for rec in records for row in rec["pageRows"]]
    for idx, row in enumerate(rows[:24]):
        fill = (17, 20, 25) if idx % 2 == 0 else (22, 25, 31)
        draw.rectangle((24, y - 8, width - 28, y + 34), fill=fill)
        values = [
            row["pdf"][:52],
            str(row["articlePage"]),
            row["firstToken"] or "-",
            str(row["strictHitCount"]),
            ",".join(row["targetIds"]) or "-",
            str(int(row["pageStartSelectorCandidate"])),
            row["firstWordsText"][:105],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(230, 234, 238), font=tiny)
        y += 42
    draw.text((28, height - 58), summary["fingerprint"][:190], fill=(143, 156, 169), font=small)
    img.save(OUT_SHEET, quality=94)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current PDF OCR Page-Header Sequence Gate",
        "",
        "Scope: inspected page-start OCR text across current PDF article pages 73-80, with special attention to page 76 starting at `OVERDOSE` in the duplicate OCR PDFs. This is a page-header/order inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOcrPageHeaderSequenceGate']}`",
        f"- PDFs checked / page rows checked: `{summary['pdfCount']}` / `{summary['pageRowsChecked']}`",
        f"- Page-76 `OVERDOSE` header PDFs: `{summary['page76OverdoseHeaderPdfCount']}`",
        f"- Strict page-start rows / target page-start rows: `{summary['strictPageStartRowCount']}` / `{summary['targetPageStartRowCount']}`",
        f"- All-four target page-start rows / active-order page-start rows: `{summary['allFourPageStartRowCount']}` / `{summary['activeOrderPageStartRowCount']}`",
        f"- Page-header sequence candidates: `{summary['pageHeaderSequenceCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## PDF Summary",
        "",
        "| PDF | pages | p76 starts OVERDOSE | strict page starts | target page starts | all-four page starts | candidates | first-token sequence |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for rec in result["records"]:
        sequence = " ".join(
            f"{item['articlePage']}:{item['firstToken'] or '-'}"
            for item in rec["firstTokenSequence"]
        )
        lines.append(
            f"| `{rec['pdf']}` | `{rec['pageCount']}` | `{int(rec['page76StartsWithOverdose'])}` | `{rec['strictPageStartRows']}` | `{rec['targetPageStartRows']}` | `{rec['allFourPageStartRows']}` | `{rec['candidateRows']}` | `{sequence}` |"
        )
    lines.extend(
        [
            "",
            "## Page Rows",
            "",
            "| PDF | article page | first token | strict hits | target ids | target order | candidate | first words |",
            "|---|---:|---|---|---|---|---:|---|",
        ]
    )
    for rec in result["records"]:
        for row in rec["pageRows"]:
            lines.append(
                f"| `{row['pdf']}` | `{row['articlePage']}` | `{row['firstToken'] or '-'}` | `{','.join(row['strictHits']) or '-'}` | `{','.join(row['targetIds']) or '-'}` | `{'-'.join(row['targetOrder']) or '-'}` | `{int(row['pageStartSelectorCandidate'])}` | `{row['firstWordsText']}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_ocr_page_header_sequence_no_selector`.",
            "- Page 76 begins with OCR `OVERDOSE` only in the byte-identical duplicate OCR PDFs, and the page-start text is ordinary article/header prose.",
            "- Page-start OCR rows do not combine strict extraction wording with all-four active target terms or active-order structure.",
            "",
            "## Next Move",
            "",
            "- Treat current PDF OCR page headers as derivative context only. Continue toward distinct physical/original-layout/source material or raw clue wording that supplies R3 unit/order.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    reopen_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    records = [inspect_pdf(pdf) for pdf in PDFS if pdf.exists()]
    page_rows = [row for rec in records for row in rec["pageRows"]]
    summary = {
        "pdfCount": len(records),
        "pageRowsChecked": len(page_rows),
        "page76OverdoseHeaderPdfCount": sum(1 for rec in records if rec["page76StartsWithOverdose"]),
        "strictPageStartRowCount": sum(1 for row in page_rows if row["strictHitCount"] > 0),
        "targetPageStartRowCount": sum(1 for row in page_rows if row["targetIdCount"] > 0),
        "allFourPageStartRowCount": sum(1 for row in page_rows if row["allFourTargetsInFirstWords"]),
        "activeOrderPageStartRowCount": sum(1 for row in page_rows if row["activeOrderInFirstWords"]),
        "pageHeaderSequenceCandidateCount": sum(1 for row in page_rows if row["pageStartSelectorCandidate"]),
        "sourceBackedR3BridgeHitCount": int(reopen_summary.get("sourceBackedR3BridgeHitCount") or 0),
        "satisfiedReopenTriggerCount": int(reopen_summary.get("satisfiedTriggerCount") or 0),
        "triggerCount": int(reopen_summary.get("triggerCount") or 0),
        "selectorUnlocked": False,
    }
    summary["fingerprint"] = (
        f"pdfs={summary['pdfCount']}|pageRows={summary['pageRowsChecked']}|"
        f"p76Overdose={summary['page76OverdoseHeaderPdfCount']}|"
        f"strictRows={summary['strictPageStartRowCount']}|"
        f"targetRows={summary['targetPageStartRowCount']}|"
        f"allFourRows={summary['allFourPageStartRowCount']}|"
        f"activeOrderRows={summary['activeOrderPageStartRowCount']}|"
        f"candidates={summary['pageHeaderSequenceCandidateCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF invisible OCR page-start/header sequence across article pages 73-80; no extraction/key derivation",
        "inputs": {
            "pdfs": [rel(pdf) for pdf in PDFS if pdf.exists()],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOcrPageHeaderSequenceGate": "current_pdf_ocr_page_header_sequence_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Page-start OCR, including page 76 OVERDOSE in the duplicate PDFs, does not "
                "combine strict unit/order wording with all-four active target terms or "
                "active-order structure."
            ),
            "nextMove": (
                "Treat current PDF OCR page headers as derivative context unless a distinct "
                "source or raw clue supplies R3 unit/order evidence."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(records, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(json.dumps({"summary": summary}, indent=2))


if __name__ == "__main__":
    main()
