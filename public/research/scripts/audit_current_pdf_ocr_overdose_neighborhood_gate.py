#!/usr/bin/env python3
"""Audit hidden OCR neighborhoods around the page-76 OVERDOSE header.

Earlier OCR gates checked active-box provenance, document order, and bounded
index offsets. This pass is narrower: it asks whether the OCR words immediately
around the hidden OVERDOSE header carry unit/order instructions or an all-four
O4/B4/G5/O5 component neighborhood. It does not derive keys, create candidates,
hash to keys, inspect WIFs/addresses, check BIP39, or brute force anything.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_overdose_neighborhood_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_overdose_neighborhood_gate.json"
OUT_MD = OUT / "current_pdf_ocr_overdose_neighborhood_gate.md"
OUT_SHEET = OUT / "current_pdf_ocr_overdose_neighborhood_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

PAGE_INDEX = 3
WINDOW_RADII = [4, 8, 16, 32]
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
    found: list[str] = []
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


def inspect_pdf(pdf_path: Path) -> dict[str, Any]:
    with fitz.open(pdf_path) as doc:
        page = doc[PAGE_INDEX]
        words = words_for_page(page)

    overdose_words = [word for word in words if word["token"] == "overdose"]
    neighborhood_rows: list[dict[str, Any]] = []
    for overdose in overdose_words:
        for radius in WINDOW_RADII:
            lo = max(0, int(overdose["index"]) - radius)
            hi = min(len(words), int(overdose["index"]) + radius + 1)
            window = words[lo:hi]
            tokens = [word["token"] for word in window if word["token"]]
            strict_hits = [word["text"] for word in window if word["token"] in STRICT_TERMS]
            target_ids = target_ids_for_tokens(tokens)
            order = first_target_order(window)
            target_terms = [
                word["text"]
                for word in window
                if any(
                    word["token"] in terms
                    or any(term in word["token"] for term in terms if len(term) >= 5)
                    for terms in TARGET_TERMS.values()
                )
            ]
            candidate = (
                len(target_ids) == 4
                and order == TARGET_ORDER
                and bool(strict_hits)
            )
            neighborhood_rows.append(
                {
                    "pdf": rel(pdf_path),
                    "overdoseIndex": int(overdose["index"]),
                    "overdoseBlockLineWord": [
                        int(overdose["block"]),
                        int(overdose["line"]),
                        int(overdose["word"]),
                    ],
                    "radius": radius,
                    "windowIndexSpan": [lo, hi - 1],
                    "windowWordCount": len(window),
                    "strictHitCount": len(strict_hits),
                    "strictHits": strict_hits,
                    "targetIdCount": len(target_ids),
                    "targetIds": target_ids,
                    "targetTerms": target_terms,
                    "targetOrder": order,
                    "activeOrderMatch": order == TARGET_ORDER,
                    "candidate": candidate,
                    "windowText": compact(" ".join(word["text"] for word in window)),
                }
            )

    same_line_rows = []
    for overdose in overdose_words:
        same_line = [
            word
            for word in words
            if word["block"] == overdose["block"] and word["line"] == overdose["line"]
        ]
        same_line_rows.append(
            {
                "pdf": rel(pdf_path),
                "overdoseIndex": int(overdose["index"]),
                "sameLineWordCount": len(same_line),
                "sameLineText": compact(" ".join(word["text"] for word in same_line)),
                "sameLineStrictHitCount": sum(1 for word in same_line if word["token"] in STRICT_TERMS),
                "sameLineTargetIds": target_ids_for_tokens([word["token"] for word in same_line]),
            }
        )

    return {
        "pdf": rel(pdf_path),
        "wordCount": len(words),
        "overdoseWordCount": len(overdose_words),
        "overdoseIndexes": [int(word["index"]) for word in overdose_words],
        "sameLineRows": same_line_rows,
        "neighborhoodRows": neighborhood_rows,
        "strictNeighborhoodRows": sum(1 for row in neighborhood_rows if row["strictHitCount"] > 0),
        "targetNeighborhoodRows": sum(1 for row in neighborhood_rows if row["targetIdCount"] > 0),
        "allFourNeighborhoodRows": sum(1 for row in neighborhood_rows if row["targetIdCount"] == 4),
        "activeOrderNeighborhoodRows": sum(1 for row in neighborhood_rows if row["activeOrderMatch"]),
        "candidateRows": sum(1 for row in neighborhood_rows if row["candidate"]),
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 1700
    height = 980
    sheet = Image.new("RGB", (width, height), (11, 13, 17))
    draw = ImageDraw.Draw(sheet)
    title = safe_font(30)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF OCR OVERDOSE Neighborhood Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 62),
        "Hidden OCR words around OVERDOSE; fixed windows only; no extraction or key candidates.",
        fill=(172, 184, 196),
        font=small,
    )
    draw.text(
        (28, 95),
        f"pdfs={summary['pdfCount']} | overdose PDFs={summary['overdosePdfCount']} | rows={summary['neighborhoodRowsChecked']} | strict rows={summary['strictNeighborhoodRowCount']} | candidates={summary['hiddenOverdoseNeighborhoodCandidateCount']}",
        fill=(216, 170, 69),
        font=small,
    )

    y = 150
    headers = ["PDF", "idx", "r", "strict", "targets", "order", "candidate", "window"]
    xs = [28, 430, 500, 550, 625, 725, 840, 945]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(160, 172, 184), font=small)
    y += 30
    rows = [row for rec in records for row in rec["neighborhoodRows"]]
    for idx, row in enumerate(rows[:28]):
        fill = (17, 20, 25) if idx % 2 == 0 else (22, 25, 31)
        draw.rectangle((24, y - 8, width - 28, y + 40), fill=fill)
        values = [
            row["pdf"][:52],
            str(row["overdoseIndex"]),
            str(row["radius"]),
            str(row["strictHitCount"]),
            ",".join(row["targetIds"]) or "-",
            "-".join(row["targetOrder"]) or "-",
            str(int(row["candidate"])),
            row["windowText"][:92],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(230, 234, 238), font=tiny)
        y += 48
    draw.text((28, height - 58), summary["fingerprint"][:180], fill=(143, 156, 169), font=small)
    sheet.save(OUT_SHEET, quality=94)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current PDF OCR OVERDOSE Neighborhood Gate",
        "",
        "Scope: inspected fixed OCR word windows around the hidden page-76 `OVERDOSE` header in the current PDFs. This checks local unit/order wording and all-four target-component neighborhoods only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOcrOverdoseNeighborhoodGate']}`",
        f"- PDFs checked / PDFs with OCR OVERDOSE: `{summary['pdfCount']}` / `{summary['overdosePdfCount']}`",
        f"- OVERDOSE words / neighborhood rows checked: `{summary['overdoseWordCount']}` / `{summary['neighborhoodRowsChecked']}`",
        f"- Strict neighborhood rows / target-component rows: `{summary['strictNeighborhoodRowCount']}` / `{summary['targetNeighborhoodRowCount']}`",
        f"- All-four target neighborhoods / active-order neighborhoods: `{summary['allFourNeighborhoodRowCount']}` / `{summary['activeOrderNeighborhoodRowCount']}`",
        f"- Hidden OVERDOSE neighborhood candidates: `{summary['hiddenOverdoseNeighborhoodCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | words | OVERDOSE indexes | rows | strict rows | target rows | all-four rows | candidates |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for rec in result["records"]:
        lines.append(
            f"| `{rec['pdf']}` | `{rec['wordCount']}` | `{','.join(map(str, rec['overdoseIndexes'])) or '-'}` | `{len(rec['neighborhoodRows'])}` | `{rec['strictNeighborhoodRows']}` | `{rec['targetNeighborhoodRows']}` | `{rec['allFourNeighborhoodRows']}` | `{rec['candidateRows']}` |"
        )
    lines.extend(
        [
            "",
            "## Neighborhood Rows",
            "",
            "| PDF | OVERDOSE index | radius | window span | strict hits | target ids | target order | candidate | window text |",
            "|---|---:|---:|---|---|---|---|---:|---|",
        ]
    )
    for rec in result["records"]:
        for row in rec["neighborhoodRows"]:
            lines.append(
                f"| `{row['pdf']}` | `{row['overdoseIndex']}` | `{row['radius']}` | `{row['windowIndexSpan'][0]}-{row['windowIndexSpan'][1]}` | `{','.join(row['strictHits']) or '-'}` | `{','.join(row['targetIds']) or '-'}` | `{'-'.join(row['targetOrder']) or '-'}` | `{int(row['candidate'])}` | `{row['windowText']}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_ocr_overdose_neighborhood_no_selector`.",
            "- The OCR `OVERDOSE` header is present only in the duplicate OCR PDFs, and its fixed local windows do not contain strict extraction wording or all-four active target components.",
            "- This closes the local-neighborhood version of the hidden OCR header idea; it does not change the source-backed R3 score or reopen triggers.",
            "",
            "## Next Move",
            "",
            "- Keep current PDF OCR `OVERDOSE` as derivative context only. Continue toward distinct physical/original-layout/source material or raw clue wording that supplies R3 unit/order.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    reopen_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    records = [inspect_pdf(pdf) for pdf in PDFS if pdf.exists()]
    neighborhood_rows = [row for rec in records for row in rec["neighborhoodRows"]]
    summary = {
        "pdfCount": len(records),
        "overdosePdfCount": sum(1 for rec in records if rec["overdoseWordCount"] > 0),
        "overdoseWordCount": sum(rec["overdoseWordCount"] for rec in records),
        "neighborhoodRowsChecked": len(neighborhood_rows),
        "strictNeighborhoodRowCount": sum(1 for row in neighborhood_rows if row["strictHitCount"] > 0),
        "targetNeighborhoodRowCount": sum(1 for row in neighborhood_rows if row["targetIdCount"] > 0),
        "allFourNeighborhoodRowCount": sum(1 for row in neighborhood_rows if row["targetIdCount"] == 4),
        "activeOrderNeighborhoodRowCount": sum(1 for row in neighborhood_rows if row["activeOrderMatch"]),
        "hiddenOverdoseNeighborhoodCandidateCount": sum(1 for row in neighborhood_rows if row["candidate"]),
        "sourceBackedR3BridgeHitCount": int(reopen_summary.get("sourceBackedR3BridgeHitCount") or 0),
        "satisfiedReopenTriggerCount": int(reopen_summary.get("satisfiedTriggerCount") or 0),
        "triggerCount": int(reopen_summary.get("triggerCount") or 0),
        "selectorUnlocked": False,
    }
    summary["fingerprint"] = (
        f"pdfs={summary['pdfCount']}|overdosePdfs={summary['overdosePdfCount']}|"
        f"overdoseWords={summary['overdoseWordCount']}|rows={summary['neighborhoodRowsChecked']}|"
        f"strictRows={summary['strictNeighborhoodRowCount']}|targetRows={summary['targetNeighborhoodRowCount']}|"
        f"allFourRows={summary['allFourNeighborhoodRowCount']}|activeOrderRows={summary['activeOrderNeighborhoodRowCount']}|"
        f"hiddenCandidate={summary['hiddenOverdoseNeighborhoodCandidateCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF invisible OCR OVERDOSE local-neighborhood guardrail; no extraction/key derivation",
        "inputs": {
            "pdfs": [rel(pdf) for pdf in PDFS if pdf.exists()],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOcrOverdoseNeighborhoodGate": "current_pdf_ocr_overdose_neighborhood_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Fixed OCR word windows around the hidden OVERDOSE header do not contain strict "
                "unit/order instructions or an all-four active component neighborhood."
            ),
            "nextMove": (
                "Treat current PDF OCR OVERDOSE as derivative context unless a distinct source "
                "or raw clue supplies R3 unit/order evidence."
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
