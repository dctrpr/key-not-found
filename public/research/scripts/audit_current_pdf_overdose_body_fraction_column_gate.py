#!/usr/bin/env python3
"""Audit OVERDOSE normalized body-row plus x-column landings in current PDFs.

This bounded pass asks whether the repeated OCR `OVERDOSE` body grid becomes
selective if the page-76 active rows are transferred as normalized body-height
fractions instead of raw row numbers. It derives four page-76 row fractions and
x positions, transfers them to repeated OVERDOSE pages, chooses only the
nearest OCR word on each landed row, and checks for target terms, strict
unit/order words, all-four coverage, active target order, and source-backed R3.
It does not derive keys, generate candidates, hash to keys, inspect
WIFs/addresses, check BIP39, or brute force anything.
"""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "scripts/audit_current_pdf_overdose_body_offset_column_gate.py"
spec = importlib.util.spec_from_file_location("offset_column_gate", HELPER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot import helper script: {HELPER_PATH}")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_body_fraction_column_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_body_fraction_column_gate.json"
OUT_MD = OUT / "current_pdf_overdose_body_fraction_column_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_body_fraction_column_gate_sheet.jpg"

BODY_OFFSET_COLUMN = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate/"
    "current_pdf_overdose_body_offset_column_gate.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def derive_source_points(
    pdf: str,
    source_page: fitz.Page,
    source_lines: list[dict[str, Any]],
    targets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    img_rect = helpers.image_rect(source_page)
    max_index = max(1, len(source_lines) - 1)
    rows: list[dict[str, Any]] = []
    for target in targets:
        target_rect = helpers.source_box_to_pdf_rect(target["box"], img_rect)
        center_x = (target_rect.x0 + target_rect.x1) / 2.0
        center_y = (target_rect.y0 + target_rect.y1) / 2.0
        nearest_line = min(source_lines, key=lambda row: abs(row["center"][1] - center_y))
        nearest_word = min(
            nearest_line["words"],
            key=lambda word: abs(word["center"][0] - center_x),
        )
        rows.append(
            {
                "pdf": pdf,
                "sourceArticlePage": helpers.SOURCE_ARTICLE_PAGE,
                "sourceTarget": target["shortId"],
                "expectedPhrase": target["phrase"],
                "sourceBodyLineCount": len(source_lines),
                "sourceBodyRowIndex": int(nearest_line["bodyRowIndex"]),
                "sourceRowFraction": round(float(nearest_line["bodyRowIndex"] / max_index), 6),
                "sourceXPt": round(float(center_x), 4),
                "sourceXFractionOfImage": round(float((center_x - img_rect.x0) / img_rect.width), 6),
                "sourceLineDistancePt": round(float(abs(nearest_line["center"][1] - center_y)), 4),
                "sourceNearestWordText": nearest_word["text"],
                "sourceNearestWordToken": nearest_word["token"],
                "sourceNearestWordDistancePt": round(float(abs(nearest_word["center"][0] - center_x)), 4),
                "sourceLineText": nearest_line["text"],
            }
        )
    return rows


def inspect_fraction_row(
    pdf: str,
    article_page: int,
    source_point: dict[str, Any],
    lines: list[dict[str, Any]],
    page: fitz.Page,
) -> dict[str, Any]:
    max_index = max(0, len(lines) - 1)
    landed_index = int(round(float(source_point["sourceRowFraction"]) * max_index))
    line = lines[landed_index] if 0 <= landed_index < len(lines) else None
    img_rect = helpers.image_rect(page)
    landed_x = img_rect.x0 + float(source_point["sourceXFractionOfImage"]) * img_rect.width
    if not line or not line["words"]:
        return {
            "pdf": pdf,
            "articlePage": article_page,
            "sourceTarget": source_point["sourceTarget"],
            "expectedPhrase": source_point["expectedPhrase"],
            "sourceRowFraction": source_point["sourceRowFraction"],
            "landedBodyLineCount": len(lines),
            "landedBodyRowIndex": landed_index,
            "landedXPt": round(float(landed_x), 4),
            "lineAvailable": False,
            "nearestWordText": None,
            "nearestWordToken": None,
            "nearestWordDistancePt": None,
            "nearestWordTargetId": None,
            "ownTargetWordHit": False,
            "strictWordHit": False,
            "lineStrictHits": [],
            "lineTargetIds": [],
            "bodyLineText": None,
            "isSourceCalibrationPage": article_page == helpers.SOURCE_ARTICLE_PAGE,
        }
    nearest_word = min(line["words"], key=lambda word: abs(word["center"][0] - landed_x))
    nearest_target_id = helpers.target_id_for_token(nearest_word["token"])
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "sourceTarget": source_point["sourceTarget"],
        "expectedPhrase": source_point["expectedPhrase"],
        "sourceRowFraction": source_point["sourceRowFraction"],
        "landedBodyLineCount": len(lines),
        "landedBodyRowIndex": landed_index,
        "landedXPt": round(float(landed_x), 4),
        "lineAvailable": True,
        "nearestWordText": nearest_word["text"],
        "nearestWordToken": nearest_word["token"],
        "nearestWordDistancePt": round(float(abs(nearest_word["center"][0] - landed_x)), 4),
        "nearestWordTargetId": nearest_target_id,
        "ownTargetWordHit": nearest_target_id == source_point["sourceTarget"],
        "strictWordHit": nearest_word["token"] in helpers.STRICT_TERMS,
        "lineStrictHits": line["strictHits"],
        "lineTargetIds": line["targetIds"],
        "bodyLineText": line["text"],
        "isSourceCalibrationPage": article_page == helpers.SOURCE_ARTICLE_PAGE,
    }


def variant_row(pdf: str, article_page: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
    available = [row for row in rows if row["lineAvailable"]]
    word_target_sequence = [
        row["nearestWordTargetId"] for row in available if row["nearestWordTargetId"]
    ]
    strict_word_rows = [row for row in available if row["strictWordHit"]]
    own_word_hits = [row for row in available if row["ownTargetWordHit"]]
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "fractionRows": len(rows),
        "availableFractionRows": len(available),
        "nearestWordTargetHitCount": len(word_target_sequence),
        "ownTargetWordHitCount": len(own_word_hits),
        "strictWordHitCount": len(strict_word_rows),
        "nearestWordTargetSequence": word_target_sequence,
        "allFourOwnTargetWords": len(own_word_hits) == 4,
        "activeWordTargetOrder": word_target_sequence == helpers.TARGET_ORDER,
        "candidate": len(own_word_hits) == 4
        and word_target_sequence == helpers.TARGET_ORDER
        and bool(strict_word_rows),
        "nearestWordStream": " ".join(row["nearestWordText"] or "." for row in rows),
        "landedRowIndexes": [row["landedBodyRowIndex"] for row in rows],
        "isSourceCalibrationPage": article_page == helpers.SOURCE_ARTICLE_PAGE,
    }


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    pdf = rel(pdf_path)
    page_rows: list[dict[str, Any]] = []
    source_point_rows: list[dict[str, Any]] = []
    landed_word_rows: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as doc:
        page_lines: dict[int, list[dict[str, Any]]] = {}
        page_objects: dict[int, fitz.Page] = {}
        for article_page in helpers.ARTICLE_PAGES:
            page_index = article_page - 73
            if page_index < 0 or page_index >= len(doc):
                continue
            page = doc[page_index]
            words = helpers.page_words(page)
            if not words or words[0]["token"] != "overdose":
                continue
            lines = helpers.line_rows(words, words[0])
            page_rows.append(helpers.page_summary(pdf, article_page, words, lines))
            page_lines[article_page] = lines
            page_objects[article_page] = page

        if helpers.SOURCE_ARTICLE_PAGE in page_lines and page_lines[helpers.SOURCE_ARTICLE_PAGE]:
            source_point_rows = derive_source_points(
                pdf,
                page_objects[helpers.SOURCE_ARTICLE_PAGE],
                page_lines[helpers.SOURCE_ARTICLE_PAGE],
                targets,
            )

        if source_point_rows:
            for article_page in helpers.ARTICLE_PAGES:
                lines = page_lines.get(article_page, [])
                page = page_objects.get(article_page)
                if not lines or page is None:
                    continue
                page_landed_rows = [
                    inspect_fraction_row(pdf, article_page, source_point, lines, page)
                    for source_point in source_point_rows
                ]
                landed_word_rows.extend(page_landed_rows)
                variant_rows.append(variant_row(pdf, article_page, page_landed_rows))

    return {
        "pdf": pdf,
        "overdosePageRows": page_rows,
        "sourcePointRows": source_point_rows,
        "landedWordRows": landed_word_rows,
        "variantRows": variant_rows,
    }


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    header_rows = [row for record in records for row in record["overdosePageRows"]]
    source_rows = [row for record in records for row in record["sourcePointRows"]]
    landed_rows = [row for record in records for row in record["landedWordRows"]]
    variants = [row for record in records for row in record["variantRows"]]
    available_rows = [row for row in landed_rows if row["lineAvailable"]]
    target_word_rows = [row for row in available_rows if row["nearestWordTargetId"]]
    own_word_rows = [row for row in available_rows if row["ownTargetWordHit"]]
    strict_word_rows = [row for row in available_rows if row["strictWordHit"]]
    all_four_pages = [row for row in variants if row["allFourOwnTargetWords"]]
    active_order_pages = [row for row in variants if row["activeWordTargetOrder"]]
    candidate_pages = [row for row in variants if row["candidate"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 0))
    fingerprint = (
        f"pdfs={len(records)}|headers={len(header_rows)}|sourceFractions={len(source_rows)}|"
        f"fractionPages={len(variants)}|wordRows={len(landed_rows)}|"
        f"targetWordRows={len(target_word_rows)}|ownWordRows={len(own_word_rows)}|"
        f"strictWordRows={len(strict_word_rows)}|allFourPages={len(all_four_pages)}|"
        f"activeOrderPages={len(active_order_pages)}|candidates={len(candidate_pages)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "overdoseHeaderRowCount": len(header_rows),
        "sourceFractionRowCount": len(source_rows),
        "fractionLandingPageCount": len(variants),
        "landedWordRowCount": len(landed_rows),
        "targetWordHitCount": len(target_word_rows),
        "ownTargetWordHitCount": len(own_word_rows),
        "strictWordHitCount": len(strict_word_rows),
        "allFourOwnTargetPageCount": len(all_four_pages),
        "activeWordTargetOrderPageCount": len(active_order_pages),
        "bodyFractionColumnCandidateCount": len(candidate_pages),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2450
    height = 1320
    img = Image.new("RGB", (width, height), (9, 11, 15))
    draw = ImageDraw.Draw(img)
    title = helpers.safe_font(31)
    small = helpers.safe_font(16)
    tiny = helpers.safe_font(12)
    draw.text((28, 22), "Current PDF OVERDOSE Body-Fraction Column Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Transfers active normalized body-row fractions plus x-position and keeps only nearest OCR word.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    columns = [
        ("PDF", 28),
        ("page", 520),
        ("source", 585),
        ("frac", 665),
        ("row", 740),
        ("x", 790),
        ("word", 870),
        ("token", 1000),
        ("target", 1125),
        ("own", 1190),
        ("strict", 1245),
        ("stream line", 1325),
    ]
    y = 145
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["landedWordRows"]]
    for idx, row in enumerate(rows[:40]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:60],
            "page": str(row["articlePage"]),
            "source": row["sourceTarget"],
            "frac": str(row["sourceRowFraction"]),
            "row": str(row["landedBodyRowIndex"]),
            "x": str(row["landedXPt"]),
            "word": str(row["nearestWordText"] or "-")[:16],
            "token": str(row["nearestWordToken"] or "-")[:16],
            "target": str(row["nearestWordTargetId"] or "-"),
            "own": str(int(row["ownTargetWordHit"])),
            "strict": str(int(row["strictWordHit"])),
            "stream line": (row["bodyLineText"] or "")[:120],
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires all four own-target nearest words, active target order, strict wording, and source-backed R3.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Body-Fraction Column Gate",
        "",
        "Scope: derived the four page-76 active normalized body-row fractions and x positions from the repeated OCR `OVERDOSE` body grid, transferred those fraction-plus-column points to repeated `OVERDOSE` pages 74/76/78 in the current PDFs, kept only the nearest OCR word on each landed row, and checked for target terms, strict unit/order words, all-four coverage, active target order, and source-backed R3. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseBodyFractionColumnGate']}`",
        f"- PDFs checked / OVERDOSE header rows / source fractions: `{summary['pdfCount']}` / `{summary['overdoseHeaderRowCount']}` / `{summary['sourceFractionRowCount']}`",
        f"- Fraction landing pages / landed word rows: `{summary['fractionLandingPageCount']}` / `{summary['landedWordRowCount']}`",
        f"- Target-word hits / own-target word hits / strict-word hits: `{summary['targetWordHitCount']}` / `{summary['ownTargetWordHitCount']}` / `{summary['strictWordHitCount']}`",
        f"- All-four pages / active-order pages / candidates: `{summary['allFourOwnTargetPageCount']}` / `{summary['activeWordTargetOrderPageCount']}` / `{summary['bodyFractionColumnCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Source Fractions",
        "",
        "| PDF | source page | target | source rows | row index | row fraction | x fraction | source nearest word | source line |",
        "|---|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for record in result["records"]:
        for row in record["sourcePointRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{count}` | `{idx}` | `{frac}` | `{xfrac}` | `{word}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["sourceArticlePage"],
                    target=row["sourceTarget"],
                    count=row["sourceBodyLineCount"],
                    idx=row["sourceBodyRowIndex"],
                    frac=row["sourceRowFraction"],
                    xfrac=row["sourceXFractionOfImage"],
                    word=row["sourceNearestWordText"],
                    line=row["sourceLineText"],
                )
            )
    lines.extend(
        [
            "",
            "## Variant Pages",
            "",
            "| PDF | article page | landed rows | target word hits | own-target hits | strict words | target sequence | nearest-word stream | candidate |",
            "|---|---:|---|---:|---:|---:|---|---|---:|",
        ]
    )
    for record in result["records"]:
        for row in record["variantRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{rows}` | `{target_hits}` | `{own}` | `{strict}` | `{targets}` | `{stream}` | `{candidate}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    rows=",".join(str(v) for v in row["landedRowIndexes"]),
                    target_hits=row["nearestWordTargetHitCount"],
                    own=row["ownTargetWordHitCount"],
                    strict=row["strictWordHitCount"],
                    targets=",".join(row["nearestWordTargetSequence"]) or "-",
                    stream=row["nearestWordStream"],
                    candidate=int(row["candidate"]),
                )
            )
    lines.extend(
        [
            "",
            "## Landed Words",
            "",
            "| PDF | article page | source target | row fraction | landed row | nearest word | token | distance | target id | own hit | strict word | body line |",
            "|---|---:|---|---:|---:|---|---|---:|---|---:|---:|---|",
        ]
    )
    for record in result["records"]:
        for row in record["landedWordRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{frac}` | `{row}` | `{word}` | `{token}` | `{dist}` | `{target_id}` | `{own}` | `{strict}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    target=row["sourceTarget"],
                    frac=row["sourceRowFraction"],
                    row=row["landedBodyRowIndex"],
                    word=row["nearestWordText"] or "-",
                    token=row["nearestWordToken"] or "-",
                    dist=row["nearestWordDistancePt"],
                    target_id=row["nearestWordTargetId"] or "-",
                    own=int(row["ownTargetWordHit"]),
                    strict=int(row["strictWordHit"]),
                    line=row["bodyLineText"] or "-",
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfOverdoseBodyFractionColumnGate']}`.",
            "- Normalizing active row positions by body-line count changes the page-78 landing rows, but the nearest-word streams remain ordinary OCR noise/prose rather than target or instruction words.",
            "- The source calibration page still does not recover expected target words at those fraction-plus-column points.",
            "- No landed word supplies target recovery, strict unit/order wording, active-order coverage, a selector candidate, or source-backed R3.",
            "",
            "## Next Move",
            "",
            "- Keep repeated OVERDOSE body-fraction column mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a normalized row-plus-column word unit/order rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = helpers.active_targets()
    reopen = load_json(helpers.REOPEN_TRIGGER_MATRIX)
    offset_column = load_json(BODY_OFFSET_COLUMN)
    records = [inspect_pdf(pdf, targets) for pdf in helpers.PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "sourceArticlePage": helpers.SOURCE_ARTICLE_PAGE,
            "articlePages": helpers.ARTICLE_PAGES,
            "method": "Transfer page-76 active normalized body-row fractions plus target x positions to repeated OVERDOSE body pages and keep only nearest OCR word.",
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
            "pdfs": [rel(path) for path in helpers.PDFS],
            "activeIndexSlotControl": rel(helpers.ACTIVE_INDEX_SLOT),
            "bodyOffsetColumn": rel(BODY_OFFSET_COLUMN),
            "bodyOffsetColumnFingerprint": offset_column.get("summary", {}).get(
                "fingerprint"
            ),
            "reopenTriggerMatrix": rel(helpers.REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseBodyFractionColumnGate": "current_pdf_overdose_body_fraction_column_no_selector",
            "selectorUnlocked": False,
            "reason": "Normalized row-fraction plus x-column nearest-word landings recover no target words, strict unit/order wording, candidate page, or source-backed R3.",
            "nextMove": "Treat repeated OVERDOSE normalized body-row plus column mechanics as closed unless source material names this exact word-unit rule.",
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
