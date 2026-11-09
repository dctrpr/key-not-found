#!/usr/bin/env python3
"""Audit current PDF OCR document order around active page-76 targets.

The current PDFs are raster pages plus invisible OCR overlays. Earlier gates
checked visibility, active-box OCR words, and affine alignment. This bounded
pass asks whether the OCR overlay document order itself supplies a coherent
O4/B4/G5/O5 unit/order signal or strict extraction wording.

No OCR-to-key extraction, key candidates, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_document_order_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_document_order_gate.json"
OUT_MD = OUT / "current_pdf_ocr_document_order_gate.md"
OUT_SHEET = OUT / "current_pdf_ocr_document_order_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_COMPONENT_TERMS = {
    "O4": ["buying", "dip"],
    "B4": ["billion"],
    "G5": ["volcano", "bonds"],
    "O5": ["shitcoiner", "heart"],
}
STRICT_UNIT_ORDER_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
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
    "read",
    "reverse",
    "right",
    "row",
    "side",
    "slot",
    "take",
    "top",
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
    out = []
    for short_id in TARGET_ORDER:
        row = by_short[short_id]
        out.append(
            {
                "shortId": short_id,
                "label": row.get("label") or row.get("phrase"),
                "phrase": row.get("phrase"),
                "box": [float(v) for v in row["box"]],
            }
        )
    return out


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


def target_rect_in_pdf(target: dict[str, Any], rect: fitz.Rect) -> fitz.Rect:
    x0, y0, x1, y1 = target["box"]
    w, h = SOURCE_IMAGE_SIZE
    return fitz.Rect(
        rect.x0 + (x0 / w) * rect.width,
        rect.y0 + (y0 / h) * rect.height,
        rect.x0 + (x1 / w) * rect.width,
        rect.y0 + (y1 / h) * rect.height,
    )


def words_for_page(page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(page.get_text("words")):
        x0, y0, x1, y1, text, block, line, word = item
        rows.append(
            {
                "index": idx,
                "text": str(text),
                "token": clean_token(str(text)),
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "center": [(float(x0) + float(x1)) / 2.0, (float(y0) + float(y1)) / 2.0],
                "block": int(block),
                "line": int(line),
                "word": int(word),
            }
        )
    return rows


def in_rect(word: dict[str, Any], rect: fitz.Rect) -> bool:
    x, y = word["center"]
    return rect.x0 <= x <= rect.x1 and rect.y0 <= y <= rect.y1


def context(words: list[dict[str, Any]], idx: int, radius: int = 8) -> str:
    lo = max(0, idx - radius)
    hi = min(len(words), idx + radius + 1)
    return compact(" ".join(row["text"] for row in words[lo:hi]))


def component_occurrences(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for target in TARGET_ORDER:
        for term in TARGET_COMPONENT_TERMS[target]:
            for word in words:
                token = word["token"]
                if token == term or (len(term) >= 5 and term in token):
                    rows.append(
                        {
                            "target": target,
                            "term": term,
                            "text": word["text"],
                            "index": word["index"],
                            "context": context(words, word["index"]),
                        }
                    )
    return sorted(rows, key=lambda row: row["index"])


def first_component_order(component_rows: list[dict[str, Any]]) -> list[str]:
    first_by_target = {}
    for row in component_rows:
        first_by_target.setdefault(row["target"], row["index"])
    return [
        target
        for target, _ in sorted(first_by_target.items(), key=lambda item: item[1])
    ]


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    rect = image_rect(page)
    words = words_for_page(page)
    target_rows = []
    strict_near_count = 0
    box_word_rows = 0
    populated_targets = 0
    for target in targets:
        target_rect = target_rect_in_pdf(target, rect)
        hits = [word for word in words if in_rect(word, target_rect)]
        hit_text = compact(" ".join(word["text"] for word in hits))
        strict_hits = [
            word
            for word in hits
            if word["token"] in STRICT_UNIT_ORDER_TERMS
        ]
        strict_near = []
        for word in hits:
            lo = max(0, word["index"] - 8)
            hi = min(len(words), word["index"] + 9)
            for neighbor in words[lo:hi]:
                if neighbor["token"] in STRICT_UNIT_ORDER_TERMS:
                    strict_near.append(neighbor["text"])
        terms = TARGET_COMPONENT_TERMS[target["shortId"]]
        component_hits = [
            word
            for word in hits
            if word["token"] in terms or any(term in word["token"] for term in terms if len(term) >= 5)
        ]
        if hits:
            populated_targets += 1
        if len(hits) > 0:
            box_word_rows += 1
        strict_near_count += len(set(strict_near)) + len(strict_hits)
        target_rows.append(
            {
                "target": target["shortId"],
                "label": target["label"],
                "boxWordCount": len(hits),
                "boxIndexSpan": [hits[0]["index"], hits[-1]["index"]] if hits else [],
                "boxText": hit_text,
                "componentHits": [word["text"] for word in component_hits],
                "strictInside": [word["text"] for word in strict_hits],
                "strictNear": sorted(set(strict_near)),
            }
        )

    component_rows = component_occurrences(words)
    component_order = first_component_order(component_rows)
    first_indices = {target: None for target in TARGET_ORDER}
    for row in component_rows:
        if first_indices[row["target"]] is None:
            first_indices[row["target"]] = row["index"]
    all_four_components_present = all(first_indices[target] is not None for target in TARGET_ORDER)
    active_order_match = component_order == TARGET_ORDER
    component_index_span = []
    if all_four_components_present:
        values = [int(first_indices[target]) for target in TARGET_ORDER if first_indices[target] is not None]
        component_index_span = [min(values), max(values), max(values) - min(values)]

    strict_doc_hits = [
        word
        for word in words
        if word["token"] in STRICT_UNIT_ORDER_TERMS
    ]
    box_words_text = compact(" | ".join(row["boxText"] or "-" for row in target_rows))
    target_box_text_has_instruction = any(term in clean_token(box_words_text) for term in STRICT_UNIT_ORDER_TERMS)
    hidden_ocr_order_candidate = (
        populated_targets == 4
        and all_four_components_present
        and active_order_match
        and (strict_near_count > 0 or target_box_text_has_instruction)
    )

    doc.close()
    return {
        "pdf": rel(pdf_path),
        "wordCount": len(words),
        "targetRows": target_rows,
        "populatedTargetCount": populated_targets,
        "boxWordRows": box_word_rows,
        "boxWordsText": box_words_text,
        "componentOccurrenceCount": len(component_rows),
        "componentRows": component_rows[:30],
        "componentFirstIndices": first_indices,
        "componentFirstOrder": component_order,
        "allFourComponentsPresent": all_four_components_present,
        "componentOrderMatchesActiveOrder": active_order_match,
        "componentIndexSpan": component_index_span,
        "strictDocumentHitCount": len(strict_doc_hits),
        "strictNearActiveBoxCount": strict_near_count,
        "targetBoxTextHasInstruction": target_box_text_has_instruction,
        "hiddenOcrOrderCandidate": hidden_ocr_order_candidate,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 1500
    margin = 28
    row_h = 68
    height = 136 + len(records) * row_h + 96
    img = Image.new("RGB", (width, height), (11, 13, 17))
    draw = ImageDraw.Draw(img)
    draw.text((margin, 24), "Current PDF OCR Document-Order Gate", fill=(245, 247, 250), font=safe_font(32))
    draw.text(
        (margin, 66),
        "Invisible OCR overlay order around O4/B4/G5/O5; source/render provenance only.",
        fill=(172, 184, 196),
        font=safe_font(17),
    )
    draw.text(
        (margin, 96),
        f"pdfs={summary['pdfCount']} | populatedAllFour={summary['allFourBoxPopulatedPdfCount']} | orderCandidates={summary['hiddenOcrOrderCandidateCount']} | sourceR3=0",
        fill=(216, 170, 69),
        font=safe_font(16),
    )
    y = 136
    for rec in records:
        draw.rectangle((margin, y - 8, width - margin, y + row_h - 14), fill=(17, 20, 25))
        draw.text((margin + 8, y), rec["pdf"][:70], fill=(235, 239, 243), font=safe_font(16))
        draw.text(
            (margin + 640, y),
            f"targets {rec['populatedTargetCount']}/4",
            fill=(154, 167, 181),
            font=safe_font(15),
        )
        draw.text(
            (margin + 800, y),
            "component order " + ("-".join(rec["componentFirstOrder"]) or "-"),
            fill=(154, 167, 181),
            font=safe_font(15),
        )
        draw.text(
            (margin + 1120, y),
            f"candidate {int(rec['hiddenOcrOrderCandidate'])}",
            fill=(216, 170, 69),
            font=safe_font(15),
        )
        draw.text((margin + 8, y + 28), rec["boxWordsText"][:140], fill=(139, 152, 166), font=safe_font(13))
        y += row_h
    draw.text((margin, height - 50), summary["fingerprint"][:170], fill=(143, 156, 169), font=safe_font(14))
    img.save(OUT_SHEET, quality=94)


def main() -> None:
    targets = active_targets()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    records = [inspect_pdf(pdf, targets) for pdf in PDFS if pdf.exists()]
    all_four_box_count = sum(1 for row in records if row["populatedTargetCount"] == 4)
    all_four_component_count = sum(1 for row in records if row["allFourComponentsPresent"])
    active_order_match_count = sum(1 for row in records if row["componentOrderMatchesActiveOrder"])
    candidate_count = sum(1 for row in records if row["hiddenOcrOrderCandidate"])
    strict_near_count = sum(row["strictNearActiveBoxCount"] for row in records)
    summary = {
        "pdfCount": len(records),
        "allFourBoxPopulatedPdfCount": all_four_box_count,
        "allFourComponentPresentPdfCount": all_four_component_count,
        "componentOrderMatchesActiveOrderPdfCount": active_order_match_count,
        "strictNearActiveBoxCount": strict_near_count,
        "hiddenOcrOrderCandidateCount": candidate_count,
        "sourceBackedR3BridgeHitCount": int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0),
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 0) or 0),
        "selectorUnlocked": False,
    }
    summary["fingerprint"] = (
        f"pdfs={summary['pdfCount']}|allFourBoxes={all_four_box_count}|"
        f"allFourComponents={all_four_component_count}|activeOrder={active_order_match_count}|"
        f"strictNear={strict_near_count}|hiddenCandidate={candidate_count}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF invisible OCR document-order guardrail around active page-76 target boxes; no extraction/key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOcrDocumentOrderGate": "no_selector",
            "reason": (
                "The OCR layer is derivative and does not put all four active boxes, target component terms, "
                "active target order, and strict unit/order wording together in any current PDF."
            ),
            "nextMove": (
                "Treat invisible PDF OCR document order as context only; reopen only with distinct source/original-layout "
                "material or raw clue wording that supplies R3 unit/order."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(records, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF OCR Document-Order Gate",
        "",
        "Scope: inspected invisible PDF OCR document order around page-76 O4/B4/G5/O5 active boxes. No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- PDFs with all four active boxes populated by OCR words: `{summary['allFourBoxPopulatedPdfCount']}`",
        f"- PDFs with all four active component targets present somewhere in OCR order: `{summary['allFourComponentPresentPdfCount']}`",
        f"- PDFs whose first component occurrences match active order O4/B4/G5/O5: `{summary['componentOrderMatchesActiveOrderPdfCount']}`",
        f"- Strict unit/order hits near active boxes: `{summary['strictNearActiveBoxCount']}`",
        f"- Hidden OCR document-order candidates: `{summary['hiddenOcrOrderCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | words | populated boxes | box OCR text | component first order | all components | active order | strict near | candidate |",
        "|---|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    for rec in records:
        lines.append(
            f"| `{rec['pdf']}` | `{rec['wordCount']}` | `{rec['populatedTargetCount']}/4` | `{rec['boxWordsText']}` | `{'-'.join(rec['componentFirstOrder']) or '-'}` | `{int(rec['allFourComponentsPresent'])}` | `{int(rec['componentOrderMatchesActiveOrder'])}` | `{rec['strictNearActiveBoxCount']}` | `{int(rec['hiddenOcrOrderCandidate'])}` |"
        )
    lines += ["", "## Active Box Detail", ""]
    for rec in records:
        lines.append(f"### `{rec['pdf']}`")
        lines += ["", "| target | OCR words | word indexes | component hits | strict inside/near |", "|---|---|---|---|---|"]
        for target in rec["targetRows"]:
            idx_span = "-".join(map(str, target["boxIndexSpan"])) if target["boxIndexSpan"] else "-"
            strict = ",".join(target["strictInside"] + target["strictNear"]) or "-"
            lines.append(
                f"| `{target['target']}` | `{target['boxText'] or '-'}` | `{idx_span}` | `{','.join(target['componentHits']) or '-'}` | `{strict}` |"
            )
        lines.append("")
    lines += [
        "## Decision",
        "",
        "- `current_pdf_ocr_document_order_no_selector`.",
        "- Invisible OCR order is derivative page prose/context, not original-layout authority.",
        "- No current PDF simultaneously provides all-four active-box OCR population, all-four target components in active order, and strict unit/order wording near the active boxes.",
        "",
        "## Next Move",
        "",
        "- Keep current PDF OCR as context only. Future progress still requires distinct physical/original-layout/source evidence or raw clue wording that supplies R3 unit/order before extraction.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": summary}, indent=2))


if __name__ == "__main__":
    main()
