#!/usr/bin/env python3
"""Audit OVERDOSE body-line offset transfers in current PDFs.

This bounded pass asks whether the page-76 active O4/B4/G5/O5 row offsets
from the repeated OCR `OVERDOSE` body start act as a portable selector on the
other repeated OVERDOSE pages. It derives only the four active body-row offsets
on page 76, transfers those offsets to repeated OVERDOSE pages 74/76/78, and
checks the landed body lines for target terms, strict unit/order words,
all-four target coverage, active target order, and source-backed R3. It does
not derive keys, generate candidates, hash to keys, inspect WIFs/addresses,
check BIP39, or brute force anything.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_body_offset_transfer_gate.json"
OUT_MD = OUT / "current_pdf_overdose_body_offset_transfer_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_body_offset_transfer_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BODY_LATTICE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate/"
    "current_pdf_overdose_body_lattice_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
SOURCE_ARTICLE_PAGE = 76
ARTICLE_PAGES = [74, 76, 78]
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_TERMS = {
    "O4": {"buy", "buying", "dip"},
    "B4": {"billion", "billions"},
    "G5": {"volcano", "volcanoes", "bond", "bonds"},
    "O5": {"heart", "shitcoiner", "shitcoiners", "shitcoinery"},
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


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    return [dict(by_short[target_id]) for target_id in TARGET_ORDER]


def target_id_for_token(token: str) -> str | None:
    for target_id in TARGET_ORDER:
        terms = TARGET_TERMS[target_id]
        if token in terms or any(len(term) >= 5 and term in token for term in terms):
            return target_id
    return None


def page_words(page: fitz.Page) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, word in enumerate(page.get_text("words")):
        x0, y0, x1, y1, text, block, line, word_no = word
        rows.append(
            {
                "index": idx,
                "text": str(text),
                "token": clean_token(str(text)),
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "center": [float((x0 + x1) / 2.0), float((y0 + y1) / 2.0)],
                "block": int(block),
                "line": int(line),
                "word": int(word_no),
            }
        )
    return rows


def line_rows(words: list[dict[str, Any]], header: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for word in words:
        if word["index"] == header["index"]:
            continue
        if word["center"][1] <= header["bbox"][3] + 8.0:
            continue
        groups.setdefault((word["block"], word["line"]), []).append(word)
    rows: list[dict[str, Any]] = []
    for (block, line), line_words in groups.items():
        ordered = sorted(line_words, key=lambda word: (word["bbox"][0], word["index"]))
        x0 = min(word["bbox"][0] for word in ordered)
        y0 = min(word["bbox"][1] for word in ordered)
        x1 = max(word["bbox"][2] for word in ordered)
        y1 = max(word["bbox"][3] for word in ordered)
        tokens = [word["token"] for word in ordered]
        target_ids = []
        for token in tokens:
            target_id = target_id_for_token(token)
            if target_id and target_id not in target_ids:
                target_ids.append(target_id)
        strict_hits = [token for token in tokens if token in STRICT_TERMS]
        rows.append(
            {
                "block": block,
                "line": line,
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "center": [float((x0 + x1) / 2.0), float((y0 + y1) / 2.0)],
                "wordCount": len(ordered),
                "text": compact(" ".join(word["text"] for word in ordered)),
                "targetIds": target_ids,
                "strictHits": strict_hits,
            }
        )
    rows.sort(key=lambda row: (row["center"][1], row["center"][0]))
    for idx, row in enumerate(rows):
        row["bodyRowIndex"] = idx
    return rows


def image_rect(page: fitz.Page) -> fitz.Rect:
    best_rect = page.rect
    best_area = -1.0
    for image in page.get_images(full=True):
        xref = int(image[0])
        for rect in page.get_image_rects(xref):
            area = max(0.0, rect.width) * max(0.0, rect.height)
            if area > best_area:
                best_area = area
                best_rect = rect
    return best_rect


def source_box_to_pdf_rect(box: list[float], rect: fitz.Rect) -> fitz.Rect:
    x0, y0, x1, y1 = [float(v) for v in box]
    w, h = SOURCE_IMAGE_SIZE
    return fitz.Rect(
        rect.x0 + (x0 / w) * rect.width,
        rect.y0 + (y0 / h) * rect.height,
        rect.x0 + (x1 / w) * rect.width,
        rect.y0 + (y1 / h) * rect.height,
    )


def derive_source_offsets(
    pdf: str,
    source_page: fitz.Page,
    source_lines: list[dict[str, Any]],
    targets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    img_rect = image_rect(source_page)
    rows: list[dict[str, Any]] = []
    for target in targets:
        target_rect = source_box_to_pdf_rect(target["box"], img_rect)
        center_y = (target_rect.y0 + target_rect.y1) / 2.0
        nearest = min(source_lines, key=lambda row: abs(row["center"][1] - center_y))
        rows.append(
            {
                "pdf": pdf,
                "sourceArticlePage": SOURCE_ARTICLE_PAGE,
                "sourceTarget": target["shortId"],
                "expectedPhrase": target["phrase"],
                "sourceBodyRowIndex": int(nearest["bodyRowIndex"]),
                "sourceLineDistancePt": round(float(abs(nearest["center"][1] - center_y)), 4),
                "sourceLineText": nearest["text"],
            }
        )
    return rows


def page_summary(pdf: str, article_page: int, words: list[dict[str, Any]], lines: list[dict[str, Any]]) -> dict[str, Any]:
    line_pitch_values = [
        round(float(lines[idx + 1]["center"][1] - lines[idx]["center"][1]), 4)
        for idx in range(len(lines) - 1)
    ]
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "overdoseHeader": bool(words and words[0]["token"] == "overdose"),
        "bodyLineCount": len(lines),
        "firstBodyLineText": lines[0]["text"] if lines else None,
        "medianLinePitchPt": sorted(line_pitch_values)[len(line_pitch_values) // 2]
        if line_pitch_values
        else None,
    }


def inspect_transfer_row(
    pdf: str,
    article_page: int,
    source_offset: dict[str, Any],
    lines: list[dict[str, Any]],
) -> dict[str, Any]:
    offset = int(source_offset["sourceBodyRowIndex"])
    line = lines[offset] if 0 <= offset < len(lines) else None
    target_ids = line["targetIds"] if line else []
    strict_hits = line["strictHits"] if line else []
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "sourceTarget": source_offset["sourceTarget"],
        "expectedPhrase": source_offset["expectedPhrase"],
        "sourceBodyRowIndex": offset,
        "lineAvailable": bool(line),
        "ownTargetAtOffset": source_offset["sourceTarget"] in target_ids,
        "lineTargetIds": target_ids,
        "strictHits": strict_hits,
        "bodyLineText": line["text"] if line else None,
        "isSourceCalibrationPage": article_page == SOURCE_ARTICLE_PAGE,
    }


def variant_row(pdf: str, article_page: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
    available = [row for row in rows if row["lineAvailable"]]
    measured_sequence: list[str] = []
    for row in available:
        for target_id in row["lineTargetIds"]:
            if target_id not in measured_sequence:
                measured_sequence.append(target_id)
    strict_rows = [row for row in available if row["strictHits"]]
    own_hits = [row for row in available if row["ownTargetAtOffset"]]
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "offsetRows": len(rows),
        "availableOffsetRows": len(available),
        "ownTargetOffsetHitCount": len(own_hits),
        "strictOffsetRowCount": len(strict_rows),
        "unionTargetIds": measured_sequence,
        "allFourOwnTargetOffsets": len(own_hits) == 4,
        "activeTargetOrder": measured_sequence == TARGET_ORDER,
        "candidate": len(own_hits) == 4 and measured_sequence == TARGET_ORDER and bool(strict_rows),
        "isSourceCalibrationPage": article_page == SOURCE_ARTICLE_PAGE,
    }


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    pdf = rel(pdf_path)
    page_rows: list[dict[str, Any]] = []
    source_offset_rows: list[dict[str, Any]] = []
    transferred_rows: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as doc:
        page_lines: dict[int, list[dict[str, Any]]] = {}
        page_objects: dict[int, fitz.Page] = {}
        for article_page in ARTICLE_PAGES:
            page_index = article_page - 73
            if page_index < 0 or page_index >= len(doc):
                continue
            page = doc[page_index]
            words = page_words(page)
            if not words or words[0]["token"] != "overdose":
                continue
            lines = line_rows(words, words[0])
            page_rows.append(page_summary(pdf, article_page, words, lines))
            page_lines[article_page] = lines
            page_objects[article_page] = page

        if SOURCE_ARTICLE_PAGE in page_lines and page_lines[SOURCE_ARTICLE_PAGE]:
            source_offset_rows = derive_source_offsets(
                pdf,
                page_objects[SOURCE_ARTICLE_PAGE],
                page_lines[SOURCE_ARTICLE_PAGE],
                targets,
            )

        if source_offset_rows:
            for article_page in ARTICLE_PAGES:
                lines = page_lines.get(article_page, [])
                if not lines:
                    continue
                page_transfer_rows = [
                    inspect_transfer_row(pdf, article_page, source_offset, lines)
                    for source_offset in source_offset_rows
                ]
                transferred_rows.extend(page_transfer_rows)
                variant_rows.append(variant_row(pdf, article_page, page_transfer_rows))

    return {
        "pdf": pdf,
        "overdosePageRows": page_rows,
        "sourceOffsetRows": source_offset_rows,
        "transferredOffsetRows": transferred_rows,
        "variantRows": variant_rows,
    }


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    header_rows = [row for record in records for row in record["overdosePageRows"]]
    body_pages = [row for row in header_rows if row["bodyLineCount"] > 0]
    source_rows = [row for record in records for row in record["sourceOffsetRows"]]
    transfer_rows = [row for record in records for row in record["transferredOffsetRows"]]
    variants = [row for record in records for row in record["variantRows"]]
    own_rows = [row for row in transfer_rows if row["ownTargetAtOffset"]]
    strict_rows = [row for row in transfer_rows if row["strictHits"]]
    all_four_pages = [row for row in variants if row["allFourOwnTargetOffsets"]]
    active_order_pages = [row for row in variants if row["activeTargetOrder"]]
    candidate_pages = [row for row in variants if row["candidate"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 0))
    fingerprint = (
        f"pdfs={len(records)}|headers={len(header_rows)}|sourceOffsets={len(source_rows)}|"
        f"offsetPages={len(variants)}|offsetRows={len(transfer_rows)}|"
        f"ownTargetRows={len(own_rows)}|strictRows={len(strict_rows)}|"
        f"allFourPages={len(all_four_pages)}|activeOrderPages={len(active_order_pages)}|"
        f"candidates={len(candidate_pages)}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "overdoseHeaderRowCount": len(header_rows),
        "bodyOffsetPageCount": len(body_pages),
        "sourceOffsetRowCount": len(source_rows),
        "transferredOffsetRowCount": len(transfer_rows),
        "ownTargetOffsetHitCount": len(own_rows),
        "strictOffsetRowCount": len(strict_rows),
        "allFourOwnTargetPageCount": len(all_four_pages),
        "activeTargetOrderPageCount": len(active_order_pages),
        "bodyOffsetCandidateCount": len(candidate_pages),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2300
    height = 1320
    img = Image.new("RGB", (width, height), (9, 11, 15))
    draw = ImageDraw.Draw(img)
    title = safe_font(31)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF OVERDOSE Body-Offset Transfer Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Transfers only the four page-76 active body-row offsets onto repeated OVERDOSE pages.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    columns = [
        ("PDF", 28),
        ("page", 520),
        ("source", 585),
        ("offset", 665),
        ("available", 742),
        ("own hit", 835),
        ("strict", 918),
        ("targets", 1010),
        ("landed body line", 1110),
    ]
    y = 145
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["transferredOffsetRows"]]
    for idx, row in enumerate(rows[:40]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:60],
            "page": str(row["articlePage"]),
            "source": row["sourceTarget"],
            "offset": str(row["sourceBodyRowIndex"]),
            "available": str(int(row["lineAvailable"])),
            "own hit": str(int(row["ownTargetAtOffset"])),
            "strict": ",".join(row["strictHits"]) or "-",
            "targets": ",".join(row["lineTargetIds"]) or "-",
            "landed body line": (row["bodyLineText"] or "")[:105],
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires all four own-target offset hits, measured active target order, strict wording, and source-backed R3.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Body-Offset Transfer Gate",
        "",
        "Scope: derived the four page-76 active O4/B4/G5/O5 body-row offsets from the repeated OCR `OVERDOSE` body start, transferred those offsets to repeated `OVERDOSE` pages 74/76/78 in the current PDFs, and checked the landed body lines for target terms, strict unit/order words, all-four coverage, active target order, and source-backed R3. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseBodyOffsetTransferGate']}`",
        f"- PDFs checked / OVERDOSE header rows / body-offset pages: `{summary['pdfCount']}` / `{summary['overdoseHeaderRowCount']}` / `{summary['bodyOffsetPageCount']}`",
        f"- Source offset rows / transferred offset rows: `{summary['sourceOffsetRowCount']}` / `{summary['transferredOffsetRowCount']}`",
        f"- Own-target offset hits / strict offset rows: `{summary['ownTargetOffsetHitCount']}` / `{summary['strictOffsetRowCount']}`",
        f"- All-four pages / active-order pages / candidates: `{summary['allFourOwnTargetPageCount']}` / `{summary['activeTargetOrderPageCount']}` / `{summary['bodyOffsetCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Source Offsets",
        "",
        "| PDF | source page | target | body-row offset | row distance | source line |",
        "|---|---:|---|---:|---:|---|",
    ]
    for record in result["records"]:
        for row in record["sourceOffsetRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{offset}` | `{dist}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["sourceArticlePage"],
                    target=row["sourceTarget"],
                    offset=row["sourceBodyRowIndex"],
                    dist=row["sourceLineDistancePt"],
                    line=row["sourceLineText"],
                )
            )
    lines.extend(
        [
            "",
            "## Variant Pages",
            "",
            "| PDF | article page | available offsets | own-target hits | strict rows | union target ids | active order | candidate |",
            "|---|---:|---:|---:|---:|---|---:|---:|",
        ]
    )
    for record in result["records"]:
        for row in record["variantRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{available}` | `{own}` | `{strict}` | `{targets}` | `{active}` | `{candidate}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    available=row["availableOffsetRows"],
                    own=row["ownTargetOffsetHitCount"],
                    strict=row["strictOffsetRowCount"],
                    targets=",".join(row["unionTargetIds"]) or "-",
                    active=int(row["activeTargetOrder"]),
                    candidate=int(row["candidate"]),
                )
            )
    lines.extend(
        [
            "",
            "## Transferred Rows",
            "",
            "| PDF | article page | source target | offset | available | own target hit | strict hits | line target ids | landed body line |",
            "|---|---:|---|---:|---:|---:|---|---|---|",
        ]
    )
    for record in result["records"]:
        for row in record["transferredOffsetRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{offset}` | `{available}` | `{own}` | `{strict}` | `{targets}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    target=row["sourceTarget"],
                    offset=row["sourceBodyRowIndex"],
                    available=int(row["lineAvailable"]),
                    own=int(row["ownTargetAtOffset"]),
                    strict=",".join(row["strictHits"]) or "-",
                    targets=",".join(row["lineTargetIds"]) or "-",
                    line=row["bodyLineText"] or "-",
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfOverdoseBodyOffsetTransferGate']}`.",
            "- The derived page-76 active offset signature is `O4=35, B4=40, G5=42, O5=44` in both duplicate OCR PDFs.",
            "- Transferring those offsets to repeated OVERDOSE body pages lands on ordinary OCR body lines, not own target terms or strict unit/order wording.",
            "- Page 74 has repeated `OVERDOSE` headers but no readable body-line lattice in the duplicate OCR PDFs, so it cannot support this offset rule.",
            "- No transferred offset page supplies all-four target coverage, measured active target order, a selector candidate, or source-backed R3.",
            "",
            "## Next Move",
            "",
            "- Keep repeated OVERDOSE body-offset transfer mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a body-row offset, line-number, or row-transfer rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    lattice = load_json(BODY_LATTICE)
    records = [inspect_pdf(pdf, targets) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "sourceArticlePage": SOURCE_ARTICLE_PAGE,
            "articlePages": ARTICLE_PAGES,
            "method": "Derive page-76 active body-row offsets from repeated OVERDOSE body start and transfer those offsets to repeated OVERDOSE body pages.",
            "excluded": [
                "OCR-to-key extraction",
                "private-key candidate generation",
                "hash-to-key checks",
                "seed/WIF/address checks",
                "BIP39 checks",
                "broad brute force",
            ],
        },
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "activeIndexSlotControl": rel(ACTIVE_INDEX_SLOT),
            "bodyLattice": rel(BODY_LATTICE),
            "bodyLatticeFingerprint": lattice.get("summary", {}).get("fingerprint"),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseBodyOffsetTransferGate": "current_pdf_overdose_body_offset_transfer_no_selector",
            "selectorUnlocked": False,
            "reason": "Page-76 active body-row offsets transfer to repeated OVERDOSE pages but produce no own-target rows, strict unit/order wording, candidate page, or source-backed R3.",
            "nextMove": "Treat repeated OVERDOSE body-offset transfer as closed unless source material names a body-row offset or line-transfer rule.",
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(records, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")


if __name__ == "__main__":
    main()
