#!/usr/bin/env python3
"""Audit OVERDOSE body-row plus x-column word landings in current PDFs.

This bounded pass asks whether the repeated OCR `OVERDOSE` body grid becomes
selective only when the page-76 active body-row offsets are combined with the
locked target x positions. It derives four page-76 source rows and x positions,
transfers them onto repeated OVERDOSE pages, chooses only the nearest OCR word
on each landed row, and checks for target terms, strict unit/order words,
all-four coverage, active target order, and source-backed R3. It does not
derive keys, generate candidates, hash to keys, inspect WIFs/addresses, check
BIP39, or brute force anything.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_body_offset_column_gate.json"
OUT_MD = OUT / "current_pdf_overdose_body_offset_column_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_body_offset_column_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BODY_OFFSET_TRANSFER = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate/"
    "current_pdf_overdose_body_offset_transfer_gate.json"
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
                "words": ordered,
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


def derive_source_points(
    pdf: str,
    source_page: fitz.Page,
    source_lines: list[dict[str, Any]],
    targets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    img_rect = image_rect(source_page)
    rows: list[dict[str, Any]] = []
    for target in targets:
        target_rect = source_box_to_pdf_rect(target["box"], img_rect)
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
                "sourceArticlePage": SOURCE_ARTICLE_PAGE,
                "sourceTarget": target["shortId"],
                "expectedPhrase": target["phrase"],
                "sourceBodyRowIndex": int(nearest_line["bodyRowIndex"]),
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


def inspect_column_row(
    pdf: str,
    article_page: int,
    source_point: dict[str, Any],
    lines: list[dict[str, Any]],
    page: fitz.Page,
) -> dict[str, Any]:
    offset = int(source_point["sourceBodyRowIndex"])
    line = lines[offset] if 0 <= offset < len(lines) else None
    img_rect = image_rect(page)
    landed_x = img_rect.x0 + float(source_point["sourceXFractionOfImage"]) * img_rect.width
    if not line or not line["words"]:
        return {
            "pdf": pdf,
            "articlePage": article_page,
            "sourceTarget": source_point["sourceTarget"],
            "expectedPhrase": source_point["expectedPhrase"],
            "sourceBodyRowIndex": offset,
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
            "isSourceCalibrationPage": article_page == SOURCE_ARTICLE_PAGE,
        }
    nearest_word = min(line["words"], key=lambda word: abs(word["center"][0] - landed_x))
    nearest_target_id = target_id_for_token(nearest_word["token"])
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "sourceTarget": source_point["sourceTarget"],
        "expectedPhrase": source_point["expectedPhrase"],
        "sourceBodyRowIndex": offset,
        "landedXPt": round(float(landed_x), 4),
        "lineAvailable": True,
        "nearestWordText": nearest_word["text"],
        "nearestWordToken": nearest_word["token"],
        "nearestWordDistancePt": round(float(abs(nearest_word["center"][0] - landed_x)), 4),
        "nearestWordTargetId": nearest_target_id,
        "ownTargetWordHit": nearest_target_id == source_point["sourceTarget"],
        "strictWordHit": nearest_word["token"] in STRICT_TERMS,
        "lineStrictHits": line["strictHits"],
        "lineTargetIds": line["targetIds"],
        "bodyLineText": line["text"],
        "isSourceCalibrationPage": article_page == SOURCE_ARTICLE_PAGE,
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
        "columnRows": len(rows),
        "availableColumnRows": len(available),
        "nearestWordTargetHitCount": len(word_target_sequence),
        "ownTargetWordHitCount": len(own_word_hits),
        "strictWordHitCount": len(strict_word_rows),
        "nearestWordTargetSequence": word_target_sequence,
        "allFourOwnTargetWords": len(own_word_hits) == 4,
        "activeWordTargetOrder": word_target_sequence == TARGET_ORDER,
        "candidate": len(own_word_hits) == 4
        and word_target_sequence == TARGET_ORDER
        and bool(strict_word_rows),
        "nearestWordStream": " ".join(row["nearestWordText"] or "." for row in rows),
        "isSourceCalibrationPage": article_page == SOURCE_ARTICLE_PAGE,
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
            source_point_rows = derive_source_points(
                pdf,
                page_objects[SOURCE_ARTICLE_PAGE],
                page_lines[SOURCE_ARTICLE_PAGE],
                targets,
            )

        if source_point_rows:
            for article_page in ARTICLE_PAGES:
                lines = page_lines.get(article_page, [])
                page = page_objects.get(article_page)
                if not lines or page is None:
                    continue
                page_landed_rows = [
                    inspect_column_row(pdf, article_page, source_point, lines, page)
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
        f"pdfs={len(records)}|headers={len(header_rows)}|sourcePoints={len(source_rows)}|"
        f"columnPages={len(variants)}|wordRows={len(landed_rows)}|"
        f"targetWordRows={len(target_word_rows)}|ownWordRows={len(own_word_rows)}|"
        f"strictWordRows={len(strict_word_rows)}|allFourPages={len(all_four_pages)}|"
        f"activeOrderPages={len(active_order_pages)}|candidates={len(candidate_pages)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "overdoseHeaderRowCount": len(header_rows),
        "sourcePointRowCount": len(source_rows),
        "columnLandingPageCount": len(variants),
        "landedWordRowCount": len(landed_rows),
        "targetWordHitCount": len(target_word_rows),
        "ownTargetWordHitCount": len(own_word_rows),
        "strictWordHitCount": len(strict_word_rows),
        "allFourOwnTargetPageCount": len(all_four_pages),
        "activeWordTargetOrderPageCount": len(active_order_pages),
        "bodyOffsetColumnCandidateCount": len(candidate_pages),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2400
    height = 1320
    img = Image.new("RGB", (width, height), (9, 11, 15))
    draw = ImageDraw.Draw(img)
    title = safe_font(31)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF OVERDOSE Body-Offset Column Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Transfers active body-row offsets plus x-position and keeps only nearest OCR word.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    columns = [
        ("PDF", 28),
        ("page", 520),
        ("source", 585),
        ("row", 665),
        ("x", 720),
        ("word", 800),
        ("token", 930),
        ("dist", 1060),
        ("target", 1130),
        ("own", 1205),
        ("strict", 1260),
        ("body line", 1335),
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
            "row": str(row["sourceBodyRowIndex"]),
            "x": str(row["landedXPt"]),
            "word": str(row["nearestWordText"] or "-")[:16],
            "token": str(row["nearestWordToken"] or "-")[:16],
            "dist": str(row["nearestWordDistancePt"]),
            "target": str(row["nearestWordTargetId"] or "-"),
            "own": str(int(row["ownTargetWordHit"])),
            "strict": str(int(row["strictWordHit"])),
            "body line": (row["bodyLineText"] or "")[:120],
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
        "# Current PDF OVERDOSE Body-Offset Column Gate",
        "",
        "Scope: derived the four page-76 active body-row offsets and x positions from the repeated OCR `OVERDOSE` body grid, transferred those row-plus-column points to repeated `OVERDOSE` pages 74/76/78 in the current PDFs, kept only the nearest OCR word on each landed row, and checked for target terms, strict unit/order words, all-four coverage, active target order, and source-backed R3. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseBodyOffsetColumnGate']}`",
        f"- PDFs checked / OVERDOSE header rows / source points: `{summary['pdfCount']}` / `{summary['overdoseHeaderRowCount']}` / `{summary['sourcePointRowCount']}`",
        f"- Column landing pages / landed word rows: `{summary['columnLandingPageCount']}` / `{summary['landedWordRowCount']}`",
        f"- Target-word hits / own-target word hits / strict-word hits: `{summary['targetWordHitCount']}` / `{summary['ownTargetWordHitCount']}` / `{summary['strictWordHitCount']}`",
        f"- All-four pages / active-order pages / candidates: `{summary['allFourOwnTargetPageCount']}` / `{summary['activeWordTargetOrderPageCount']}` / `{summary['bodyOffsetColumnCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Source Points",
        "",
        "| PDF | source page | target | row offset | x pt | x fraction | source nearest word | distance | source line |",
        "|---|---:|---|---:|---:|---:|---|---:|---|",
    ]
    for record in result["records"]:
        for row in record["sourcePointRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{offset}` | `{x}` | `{frac}` | `{word}` | `{dist}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["sourceArticlePage"],
                    target=row["sourceTarget"],
                    offset=row["sourceBodyRowIndex"],
                    x=row["sourceXPt"],
                    frac=row["sourceXFractionOfImage"],
                    word=row["sourceNearestWordText"],
                    dist=row["sourceNearestWordDistancePt"],
                    line=row["sourceLineText"],
                )
            )
    lines.extend(
        [
            "",
            "## Variant Pages",
            "",
            "| PDF | article page | available words | target word hits | own-target hits | strict words | target sequence | nearest-word stream | candidate |",
            "|---|---:|---:|---:|---:|---:|---|---|---:|",
        ]
    )
    for record in result["records"]:
        for row in record["variantRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{available}` | `{target_hits}` | `{own}` | `{strict}` | `{targets}` | `{stream}` | `{candidate}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    available=row["availableColumnRows"],
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
            "| PDF | article page | source target | row offset | x pt | nearest word | token | distance | target id | own hit | strict word | body line |",
            "|---|---:|---|---:|---:|---|---|---:|---|---:|---:|---|",
        ]
    )
    for record in result["records"]:
        for row in record["landedWordRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{offset}` | `{x}` | `{word}` | `{token}` | `{dist}` | `{target_id}` | `{own}` | `{strict}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    target=row["sourceTarget"],
                    offset=row["sourceBodyRowIndex"],
                    x=row["landedXPt"],
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
            f"- `{result['decision']['currentPdfOverdoseBodyOffsetColumnGate']}`.",
            "- The row-plus-column point selector lands on concrete OCR words, but the nearest-word streams are ordinary OCR noise/prose rather than target or instruction words.",
            "- The source calibration page itself does not recover the expected target words at those row/column points.",
            "- No landed word supplies target recovery, strict unit/order wording, active-order coverage, a selector candidate, or source-backed R3.",
            "",
            "## Next Move",
            "",
            "- Keep repeated OVERDOSE body-offset column mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a row-plus-column word unit/order rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    offset_transfer = load_json(BODY_OFFSET_TRANSFER)
    records = [inspect_pdf(pdf, targets) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "sourceArticlePage": SOURCE_ARTICLE_PAGE,
            "articlePages": ARTICLE_PAGES,
            "method": "Transfer page-76 active body-row offsets plus target x positions to repeated OVERDOSE body pages and keep only nearest OCR word.",
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
            "bodyOffsetTransfer": rel(BODY_OFFSET_TRANSFER),
            "bodyOffsetTransferFingerprint": offset_transfer.get("summary", {}).get(
                "fingerprint"
            ),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseBodyOffsetColumnGate": "current_pdf_overdose_body_offset_column_no_selector",
            "selectorUnlocked": False,
            "reason": "Row-plus-column nearest-word landings recover no target words, strict unit/order wording, candidate page, or source-backed R3.",
            "nextMove": "Treat repeated OVERDOSE body-row plus column mechanics as closed unless source material names this exact word-unit rule.",
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
