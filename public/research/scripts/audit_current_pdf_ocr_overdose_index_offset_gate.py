#!/usr/bin/env python3
"""Audit hidden PDF OCR OVERDOSE index offsets.

This bounded pass uses the current PDFs' invisible OCR word order only as a
provenance/layout witness. It asks whether the OCR word `OVERDOSE` plus/minus
already-known active units (page line, corridor index, center slot index, span
slot indexes) lands on active target component words or strict instruction
terms. It does not derive key material.

No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address
checks, BIP39 checks, or broad brute force are run.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_overdose_index_offset_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_overdose_index_offset_gate.json"
OUT_MD = OUT / "current_pdf_ocr_overdose_index_offset_gate.md"
OUT_SHEET = OUT / "current_pdf_ocr_overdose_index_offset_gate_sheet.jpg"

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

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_COMPONENT_TERMS = {
    "O4": {"buying", "dip"},
    "B4": {"billion", "billions"},
    "G5": {"volcano", "volcanoes", "bonds"},
    "O5": {"shitcoiner", "shitcoiners", "shitcoiners", "heart"},
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


def active_rows() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = by_short[short_id]
        offsets = {
            "pageLine": int(row["pageLine"]),
            "corridorIndex": int(row["corridorIndex"]),
            "centerSlotIndex": int(row["centerSlotIndex"]),
        }
        for idx, value in enumerate(row.get("spanSlotIndexes", [])):
            offsets[f"spanSlotIndex{idx + 1}"] = int(value)
        rows.append(
            {
                "shortId": short_id,
                "label": row.get("label") or row.get("phrase"),
                "phrase": row.get("phrase"),
                "offsets": offsets,
            }
        )
    return rows


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
                "block": int(block),
                "line": int(line),
                "word": int(word),
            }
        )
    return rows


def context(words: list[dict[str, Any]], idx: int, radius: int = 5) -> str:
    lo = max(0, idx - radius)
    hi = min(len(words), idx + radius + 1)
    return compact(" ".join(row["text"] for row in words[lo:hi]))


def target_for_token(token: str) -> str | None:
    for target, terms in TARGET_COMPONENT_TERMS.items():
        if token in terms or any(len(term) >= 5 and term in token for term in terms):
            return target
    return None


def inspect_pdf(pdf_path: Path, active: list[dict[str, Any]]) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    words = words_for_page(page)
    overdose_indexes = [row["index"] for row in words if row["token"] == "overdose"]
    component_rows = []
    for row in words:
        target = target_for_token(row["token"])
        if target:
            component_rows.append(
                {
                    "target": target,
                    "index": row["index"],
                    "text": row["text"],
                    "context": context(words, row["index"]),
                }
            )
    first_component_by_target: dict[str, dict[str, Any] | None] = {target: None for target in TARGET_ORDER}
    for row in component_rows:
        if first_component_by_target[row["target"]] is None:
            first_component_by_target[row["target"]] = row

    offset_rows = []
    target_hits = []
    strict_hits = []
    for overdose_index in overdose_indexes:
        for active_row in active:
            for offset_name, offset_value in active_row["offsets"].items():
                for direction in [-1, 1]:
                    landed_index = overdose_index + direction * int(offset_value)
                    if not (0 <= landed_index < len(words)):
                        continue
                    landed = words[landed_index]
                    landed_target = target_for_token(landed["token"])
                    strict = landed["token"] in STRICT_UNIT_ORDER_TERMS
                    hit = landed_target is not None or strict
                    offset_row = {
                        "pdf": rel(pdf_path),
                        "overdoseIndex": overdose_index,
                        "sourceTarget": active_row["shortId"],
                        "offsetName": offset_name,
                        "offsetValue": offset_value,
                        "direction": "+" if direction > 0 else "-",
                        "landedIndex": landed_index,
                        "landedText": landed["text"],
                        "landedToken": landed["token"],
                        "landedTarget": landed_target,
                        "strictInstructionHit": strict,
                        "context": context(words, landed_index),
                        "hit": hit,
                    }
                    offset_rows.append(offset_row)
                    if landed_target:
                        target_hits.append(offset_row)
                    if strict:
                        strict_hits.append(offset_row)

    component_delta_rows = []
    for target in TARGET_ORDER:
        first = first_component_by_target[target]
        if not first or not overdose_indexes:
            continue
        nearest_overdose = min(overdose_indexes, key=lambda idx: abs(idx - int(first["index"])))
        delta = int(first["index"]) - nearest_overdose
        active_for_target = next(row for row in active if row["shortId"] == target)
        offset_values = set(active_for_target["offsets"].values())
        component_delta_rows.append(
            {
                "target": target,
                "firstComponentIndex": first["index"],
                "firstComponentText": first["text"],
                "nearestOverdoseIndex": nearest_overdose,
                "delta": delta,
                "absDelta": abs(delta),
                "matchesOwnKnownUnit": abs(delta) in offset_values,
                "ownOffsetValues": sorted(offset_values),
            }
        )

    all_four_components = all(first_component_by_target[target] for target in TARGET_ORDER)
    all_four_delta_known = all(row["matchesOwnKnownUnit"] for row in component_delta_rows) and len(component_delta_rows) == 4
    candidate = bool(overdose_indexes) and all_four_components and all_four_delta_known and (target_hits or strict_hits)
    doc.close()
    return {
        "pdf": rel(pdf_path),
        "wordCount": len(words),
        "overdoseIndexes": overdose_indexes,
        "componentFirstOrder": [
            row["target"]
            for row in sorted(
                [r for r in first_component_by_target.values() if r],
                key=lambda item: int(item["index"]),
            )
        ],
        "firstComponentByTarget": first_component_by_target,
        "componentDeltaRows": component_delta_rows,
        "offsetRowsChecked": len(offset_rows),
        "targetOffsetHitCount": len(target_hits),
        "strictOffsetHitCount": len(strict_hits),
        "offsetHitRows": target_hits[:20] + strict_hits[:20],
        "allFourComponentsPresent": all_four_components,
        "allFourDeltaKnownUnit": all_four_delta_known,
        "hiddenOverdoseIndexCandidate": candidate,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 1500
    margin = 28
    row_h = 66
    height = 136 + len(records) * row_h + 92
    img = Image.new("RGB", (width, height), (11, 13, 17))
    draw = ImageDraw.Draw(img)
    draw.text((margin, 24), "Current PDF OCR OVERDOSE Index Offset Gate", fill=(245, 247, 250), font=safe_font(31))
    draw.text(
        (margin, 66),
        "Hidden OCR OVERDOSE index plus/minus active line/corridor/slot units.",
        fill=(172, 184, 196),
        font=safe_font(17),
    )
    draw.text(
        (margin, 96),
        f"overdosePdfs={summary['overdosePdfCount']} | targetHits={summary['targetOffsetHitCount']} | strictHits={summary['strictOffsetHitCount']} | candidates={summary['hiddenOverdoseIndexCandidateCount']}",
        fill=(216, 170, 69),
        font=safe_font(16),
    )
    y = 136
    for rec in records:
        draw.rectangle((margin, y - 8, width - margin, y + row_h - 12), fill=(17, 20, 25))
        draw.text((margin + 8, y), rec["pdf"][:72], fill=(235, 239, 243), font=safe_font(16))
        draw.text((margin + 680, y), f"OVERDOSE idx {rec['overdoseIndexes'] or '-'}", fill=(154, 167, 181), font=safe_font(15))
        draw.text((margin + 920, y), f"order {'-'.join(rec['componentFirstOrder']) or '-'}", fill=(154, 167, 181), font=safe_font(15))
        draw.text((margin + 1220, y), f"hits {rec['targetOffsetHitCount']}/{rec['strictOffsetHitCount']}", fill=(216, 170, 69), font=safe_font(15))
        delta_text = "; ".join(
            f"{row['target']} d={row['delta']} own={int(row['matchesOwnKnownUnit'])}"
            for row in rec["componentDeltaRows"]
        )
        draw.text((margin + 8, y + 27), delta_text[:145], fill=(139, 152, 166), font=safe_font(13))
        y += row_h
    draw.text((margin, height - 48), summary["fingerprint"][:170], fill=(143, 156, 169), font=safe_font(14))
    img.save(OUT_SHEET, quality=94)


def main() -> None:
    active = active_rows()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    records = [inspect_pdf(pdf, active) for pdf in PDFS if pdf.exists()]
    overdose_pdf_count = sum(1 for row in records if row["overdoseIndexes"])
    target_offset_hit_count = sum(row["targetOffsetHitCount"] for row in records)
    strict_offset_hit_count = sum(row["strictOffsetHitCount"] for row in records)
    all_four_delta_known_count = sum(1 for row in records if row["allFourDeltaKnownUnit"])
    candidate_count = sum(1 for row in records if row["hiddenOverdoseIndexCandidate"])
    summary = {
        "pdfCount": len(records),
        "overdosePdfCount": overdose_pdf_count,
        "offsetRowsChecked": sum(row["offsetRowsChecked"] for row in records),
        "targetOffsetHitCount": target_offset_hit_count,
        "strictOffsetHitCount": strict_offset_hit_count,
        "allFourDeltaKnownUnitPdfCount": all_four_delta_known_count,
        "hiddenOverdoseIndexCandidateCount": candidate_count,
        "sourceBackedR3BridgeHitCount": int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0),
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 0) or 0),
        "selectorUnlocked": False,
    }
    summary["fingerprint"] = (
        f"pdfs={summary['pdfCount']}|overdosePdfs={overdose_pdf_count}|offsetRows={summary['offsetRowsChecked']}|"
        f"targetHits={target_offset_hit_count}|strictHits={strict_offset_hit_count}|"
        f"allFourKnownDelta={all_four_delta_known_count}|hiddenCandidate={candidate_count}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF invisible OCR OVERDOSE index offset guardrail; no extraction/key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOcrOverdoseIndexOffsetGate": "no_selector",
            "reason": (
                "OVERDOSE OCR document index plus/minus existing active line/corridor/slot units does not land on "
                "active component words or strict unit/order instructions in a selective all-four way."
            ),
            "nextMove": (
                "Keep hidden PDF OCR OVERDOSE index offsets closed. Reopen only with source/original-layout material "
                "or raw clue wording that explicitly names document-order indexes or a unit/order rule."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(records, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF OCR OVERDOSE Index Offset Gate",
        "",
        "Scope: inspected hidden PDF OCR `OVERDOSE` word index plus/minus existing active line, corridor, and slot units. No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- PDFs with OCR `OVERDOSE`: `{summary['overdosePdfCount']}`",
        f"- Offset landing rows checked: `{summary['offsetRowsChecked']}`",
        f"- Target-component offset hits: `{summary['targetOffsetHitCount']}`",
        f"- Strict instruction offset hits: `{summary['strictOffsetHitCount']}`",
        f"- PDFs where all four component deltas match their own known units: `{summary['allFourDeltaKnownUnitPdfCount']}`",
        f"- Hidden OVERDOSE index candidates: `{summary['hiddenOverdoseIndexCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | words | OVERDOSE indexes | component order | component deltas | target hits | strict hits | candidate |",
        "|---|---:|---|---|---|---:|---:|---:|",
    ]
    for rec in records:
        deltas = "; ".join(
            f"{row['target']}:{row['delta']} own={int(row['matchesOwnKnownUnit'])}"
            for row in rec["componentDeltaRows"]
        ) or "-"
        lines.append(
            f"| `{rec['pdf']}` | `{rec['wordCount']}` | `{rec['overdoseIndexes'] or '-'}` | `{'-'.join(rec['componentFirstOrder']) or '-'}` | `{deltas}` | `{rec['targetOffsetHitCount']}` | `{rec['strictOffsetHitCount']}` | `{int(rec['hiddenOverdoseIndexCandidate'])}` |"
        )
    lines += ["", "## Offset Hits", ""]
    any_hits = False
    for rec in records:
        if rec["offsetHitRows"]:
            any_hits = True
            lines.append(f"### `{rec['pdf']}`")
            lines += ["", "| source target | offset | landed index | landed text | hit target | strict | context |", "|---|---|---:|---|---|---:|---|"]
            for row in rec["offsetHitRows"]:
                lines.append(
                    f"| `{row['sourceTarget']}` | `{row['direction']}{row['offsetName']}={row['offsetValue']}` | `{row['landedIndex']}` | `{row['landedText']}` | `{row['landedTarget'] or '-'}` | `{int(row['strictInstructionHit'])}` | `{row['context']}` |"
                )
            lines.append("")
    if not any_hits:
        lines.append("- None.")
    lines += [
        "",
        "## Decision",
        "",
        "- `current_pdf_ocr_overdose_index_offset_no_selector`.",
        "- The hidden OCR `OVERDOSE` word is present only in the duplicate OCR PDFs and does not supply a selective index-offset rule.",
        "- Existing active line/corridor/slot units do not land on active component words or strict unit/order terms in a way that covers all four active targets.",
        "",
        "## Next Move",
        "",
        "- Keep hidden PDF OCR OVERDOSE index offsets closed. Continue toward physical/original-layout/source evidence or raw clue wording that supplies R3 unit/order.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": summary}, indent=2))


if __name__ == "__main__":
    main()
