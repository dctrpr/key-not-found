#!/usr/bin/env python3
"""Audit whether repeated OVERDOSE header offsets transfer page-76 targets.

The duplicate OCR PDFs place `OVERDOSE` at the start of pages 74, 76, and 78.
This bounded pass uses the measured header-center deltas from page 76 to pages
74/78 as possible layout registration rules, applies direct and mirrored
transfers to the locked page-76 O4/B4/G5/O5 target boxes, and checks whether
the transferred boxes land on target words, strict unit/order words, or an
all-four/active-order selector. It does not derive keys, generate candidates,
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_header_delta_transfer_gate.json"
OUT_MD = OUT / "current_pdf_overdose_header_delta_transfer_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_header_delta_transfer_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
REPEATED_HEADER_LANE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate/"
    "current_pdf_repeated_overdose_header_lane_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ARTICLE_PAGE_START = 73
ARTICLE_PAGE_END = 80
SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
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
    return [dict(by_short[short_id]) for short_id in TARGET_ORDER]


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
    x0, y0, x1, y1 = [float(v) for v in target["box"]]
    w, h = SOURCE_IMAGE_SIZE
    return fitz.Rect(
        rect.x0 + (x0 / w) * rect.width,
        rect.y0 + (y0 / h) * rect.height,
        rect.x0 + (x1 / w) * rect.width,
        rect.y0 + (y1 / h) * rect.height,
    )


def page_words(page: fitz.Page) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, word in enumerate(page.get_text("words")):
        x0, y0, x1, y1, text, block, line, word_no = word
        token = clean_token(str(text))
        rows.append(
            {
                "index": idx,
                "text": str(text),
                "token": token,
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "center": [float((x0 + x1) / 2.0), float((y0 + y1) / 2.0)],
                "block": int(block),
                "line": int(line),
                "word": int(word_no),
            }
        )
    return rows


def first_overdose_header(words: list[dict[str, Any]]) -> dict[str, Any] | None:
    if words and words[0]["token"] == "overdose":
        return words[0]
    return None


def target_id_for_token(token: str) -> str | None:
    for target_id in TARGET_ORDER:
        terms = TARGET_TERMS[target_id]
        if token in terms:
            return target_id
        if any(len(term) >= 5 and term in token for term in terms):
            return target_id
    return None


def rect_to_list(rect: fitz.Rect) -> list[float]:
    return [round(float(rect.x0), 4), round(float(rect.y0), 4), round(float(rect.x1), 4), round(float(rect.y1), 4)]


def rect_from_list(values: list[float]) -> fitz.Rect:
    return fitz.Rect(float(values[0]), float(values[1]), float(values[2]), float(values[3]))


def transfer_rect(
    source_rect: fitz.Rect,
    page_width: float,
    source_header_center: list[float],
    dest_header_center: list[float],
    variant: str,
) -> fitz.Rect:
    sx, sy = source_header_center
    dx, dy = dest_header_center[0] - sx, dest_header_center[1] - sy
    if variant == "direct_delta":
        return fitz.Rect(source_rect.x0 + dx, source_rect.y0 + dy, source_rect.x1 + dx, source_rect.y1 + dy)
    if variant == "x_mirror_about_header_delta":
        mirrored_x0 = sx - (source_rect.x1 - sx)
        mirrored_x1 = sx - (source_rect.x0 - sx)
        return fitz.Rect(mirrored_x0 + dx, source_rect.y0 + dy, mirrored_x1 + dx, source_rect.y1 + dy)
    if variant == "x_mirror_about_page_center_delta":
        mirrored_x0 = page_width - source_rect.x1
        mirrored_x1 = page_width - source_rect.x0
        return fitz.Rect(mirrored_x0 + dx, source_rect.y0 + dy, mirrored_x1 + dx, source_rect.y1 + dy)
    raise ValueError(variant)


def words_in_rect(words: list[dict[str, Any]], rect: fitz.Rect) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        cx, cy = word["center"]
        if rect.x0 <= cx <= rect.x1 and rect.y0 <= cy <= rect.y1:
            hits.append(word)
    return hits


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    pdf = rel(pdf_path)
    header_rows: list[dict[str, Any]] = []
    transfer_rows: list[dict[str, Any]] = []
    variant_summary: dict[tuple[int, str], dict[str, Any]] = {}
    with fitz.open(pdf_path) as doc:
        pages: dict[int, dict[str, Any]] = {}
        page_limit = min(len(doc), ARTICLE_PAGE_END - ARTICLE_PAGE_START + 1)
        for page_index in range(page_limit):
            article_page = ARTICLE_PAGE_START + page_index
            page = doc[page_index]
            words = page_words(page)
            header = first_overdose_header(words)
            pages[article_page] = {
                "page": page,
                "words": words,
                "header": header,
                "imageRect": image_rect(page),
            }
            if header:
                header_rows.append(
                    {
                        "pdf": pdf,
                        "pdfPage": page_index + 1,
                        "articlePage": article_page,
                        "pageWidth": float(page.rect.width),
                        "pageHeight": float(page.rect.height),
                        "headerBbox": header["bbox"],
                        "headerCenter": header["center"],
                        "wordCount": len(words),
                    }
                )
        if 76 not in pages or not pages[76]["header"]:
            return {
                "pdf": pdf,
                "overdoseHeaderRows": header_rows,
                "transferRows": transfer_rows,
                "variantSummaryRows": [],
            }
        source_page = pages[76]["page"]
        source_header = pages[76]["header"]
        source_header_center = source_header["center"]
        source_img_rect = pages[76]["imageRect"]
        source_target_rects = {
            target["shortId"]: target_rect_in_pdf(target, source_img_rect)
            for target in targets
        }
        for dest_article_page in [74, 78]:
            dest = pages.get(dest_article_page)
            if not dest or not dest["header"]:
                continue
            dest_header_center = dest["header"]["center"]
            delta = [
                round(dest_header_center[0] - source_header_center[0], 4),
                round(dest_header_center[1] - source_header_center[1], 4),
            ]
            for variant in [
                "direct_delta",
                "x_mirror_about_header_delta",
                "x_mirror_about_page_center_delta",
            ]:
                key = (dest_article_page, variant)
                variant_summary[key] = {
                    "pdf": pdf,
                    "sourceArticlePage": 76,
                    "destArticlePage": dest_article_page,
                    "variant": variant,
                    "headerDelta": delta,
                    "boxRows": 0,
                    "textHitRows": 0,
                    "targetTermRows": 0,
                    "strictTermRows": 0,
                    "targetIds": [],
                    "targetOrder": [],
                    "candidate": False,
                }
                first_target_indices: dict[str, int] = {}
                for target in targets:
                    target_id = target["shortId"]
                    transferred = transfer_rect(
                        source_target_rects[target_id],
                        float(source_page.rect.width),
                        source_header_center,
                        dest_header_center,
                        variant,
                    )
                    word_hits = words_in_rect(dest["words"], transferred)
                    target_hits = []
                    strict_hits = []
                    for word in word_hits:
                        hit_target_id = target_id_for_token(word["token"])
                        if hit_target_id:
                            first_target_indices.setdefault(hit_target_id, int(word["index"]))
                            target_hits.append(
                                {
                                    "targetId": hit_target_id,
                                    "word": word["text"],
                                    "token": word["token"],
                                    "index": int(word["index"]),
                                }
                            )
                        if word["token"] in STRICT_TERMS:
                            strict_hits.append(
                                {
                                    "word": word["text"],
                                    "token": word["token"],
                                    "index": int(word["index"]),
                                }
                            )
                    row = {
                        "pdf": pdf,
                        "sourceArticlePage": 76,
                        "destArticlePage": dest_article_page,
                        "variant": variant,
                        "headerDelta": delta,
                        "target": target_id,
                        "targetLabel": target["label"],
                        "sourceRect": rect_to_list(source_target_rects[target_id]),
                        "transferredRect": rect_to_list(transferred),
                        "wordHitCount": len(word_hits),
                        "wordText": compact(" ".join(word["text"] for word in word_hits)),
                        "targetTermHits": target_hits,
                        "targetTermHitCount": len(target_hits),
                        "strictTermHits": strict_hits,
                        "strictTermHitCount": len(strict_hits),
                    }
                    transfer_rows.append(row)
                    summary_row = variant_summary[key]
                    summary_row["boxRows"] += 1
                    if word_hits:
                        summary_row["textHitRows"] += 1
                    if target_hits:
                        summary_row["targetTermRows"] += 1
                    if strict_hits:
                        summary_row["strictTermRows"] += 1
                target_order = [
                    target_id
                    for target_id, _ in sorted(
                        first_target_indices.items(), key=lambda item: item[1]
                    )
                ]
                summary_row = variant_summary[key]
                summary_row["targetIds"] = [tid for tid in TARGET_ORDER if tid in first_target_indices]
                summary_row["targetOrder"] = target_order
                summary_row["allFourTargets"] = len(summary_row["targetIds"]) == 4
                summary_row["activeOrderTargets"] = target_order == TARGET_ORDER
                summary_row["candidate"] = bool(summary_row["strictTermRows"]) and (
                    summary_row["allFourTargets"] or summary_row["activeOrderTargets"]
                )
    return {
        "pdf": pdf,
        "overdoseHeaderRows": header_rows,
        "transferRows": transfer_rows,
        "variantSummaryRows": list(variant_summary.values()),
    }


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    header_rows = [row for record in records for row in record["overdoseHeaderRows"]]
    transfer_rows = [row for record in records for row in record["transferRows"]]
    variant_rows = [row for record in records for row in record["variantSummaryRows"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 0))
    text_rows = [row for row in transfer_rows if row["wordHitCount"] > 0]
    target_rows = [row for row in transfer_rows if row["targetTermHitCount"] > 0]
    strict_rows = [row for row in transfer_rows if row["strictTermHitCount"] > 0]
    candidate_rows = [row for row in variant_rows if row.get("candidate")]
    all_four_rows = [row for row in variant_rows if row.get("allFourTargets")]
    active_order_rows = [row for row in variant_rows if row.get("activeOrderTargets")]
    fingerprint = (
        f"pdfs={len(records)}|headers={len(header_rows)}|variants={len(variant_rows)}|"
        f"boxRows={len(transfer_rows)}|textRows={len(text_rows)}|targetRows={len(target_rows)}|"
        f"strictRows={len(strict_rows)}|allFourVariants={len(all_four_rows)}|"
        f"activeOrderVariants={len(active_order_rows)}|candidates={len(candidate_rows)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "overdoseHeaderRowCount": len(header_rows),
        "transferVariantRowCount": len(variant_rows),
        "transferBoxRowCount": len(transfer_rows),
        "textHitBoxRowCount": len(text_rows),
        "targetTermBoxRowCount": len(target_rows),
        "strictTermBoxRowCount": len(strict_rows),
        "allFourTransferVariantCount": len(all_four_rows),
        "activeOrderTransferVariantCount": len(active_order_rows),
        "headerDeltaTransferCandidateCount": len(candidate_rows),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2200
    height = 1420
    img = Image.new("RGB", (width, height), (9, 11, 15))
    draw = ImageDraw.Draw(img)
    title = safe_font(31)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF OVERDOSE Header Delta Transfer Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Measured page-76 OVERDOSE header offsets transfer O4/B4/G5/O5 boxes to repeated OVERDOSE pages 74/78.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    y = 145
    columns = [
        ("PDF", 28),
        ("dest", 560),
        ("variant", 625),
        ("delta", 900),
        ("text rows", 1010),
        ("target rows", 1110),
        ("strict rows", 1225),
        ("target ids", 1340),
        ("order", 1455),
        ("candidate", 1585),
    ]
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["variantSummaryRows"]]
    for idx, row in enumerate(rows[:48]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:64],
            "dest": str(row["destArticlePage"]),
            "variant": row["variant"],
            "delta": ",".join(str(v) for v in row["headerDelta"]),
            "text rows": str(row["textHitRows"]),
            "target rows": str(row["targetTermRows"]),
            "strict rows": str(row["strictTermRows"]),
            "target ids": ",".join(row["targetIds"]) or "-",
            "order": "-".join(row["targetOrder"]) or "-",
            "candidate": str(int(row["candidate"])),
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires transferred boxes to combine strict unit/order wording with all-four or active-order target coverage.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Header Delta Transfer Gate",
        "",
        "Scope: measured repeated OCR `OVERDOSE` header-center deltas from article page 76 to pages 74/78 in the current PDFs, applied direct and mirrored transfers to locked page-76 O4/B4/G5/O5 target boxes, and checked whether transferred boxes land on target terms, strict unit/order words, or all-four/active-order structure. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseHeaderDeltaTransferGate']}`",
        f"- PDFs checked / OVERDOSE header rows: `{summary['pdfCount']}` / `{summary['overdoseHeaderRowCount']}`",
        f"- Transfer variants / transferred target boxes: `{summary['transferVariantRowCount']}` / `{summary['transferBoxRowCount']}`",
        f"- Text-hit boxes / target-term boxes / strict-term boxes: `{summary['textHitBoxRowCount']}` / `{summary['targetTermBoxRowCount']}` / `{summary['strictTermBoxRowCount']}`",
        f"- All-four variants / active-order variants / candidates: `{summary['allFourTransferVariantCount']}` / `{summary['activeOrderTransferVariantCount']}` / `{summary['headerDeltaTransferCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Header Rows",
        "",
        "| PDF | article page | header center | header bbox | word count |",
        "|---|---:|---|---|---:|",
    ]
    for record in result["records"]:
        for row in record["overdoseHeaderRows"]:
            lines.append(
                f"| `{row['pdf']}` | `{row['articlePage']}` | `{[round(v, 3) for v in row['headerCenter']]}` | `{[round(v, 3) for v in row['headerBbox']]}` | `{row['wordCount']}` |"
            )
    lines.extend(
        [
            "",
            "## Transfer Variant Rows",
            "",
            "| PDF | destination page | variant | header delta | text rows | target rows | strict rows | target ids | target order | candidate |",
            "|---|---:|---|---|---:|---:|---:|---|---|---:|",
        ]
    )
    for record in result["records"]:
        for row in record["variantSummaryRows"]:
            lines.append(
                "| `{pdf}` | `{dest}` | `{variant}` | `{delta}` | `{text}` | `{target}` | `{strict}` | `{ids}` | `{order}` | `{candidate}` |".format(
                    pdf=row["pdf"],
                    dest=row["destArticlePage"],
                    variant=row["variant"],
                    delta=row["headerDelta"],
                    text=row["textHitRows"],
                    target=row["targetTermRows"],
                    strict=row["strictTermRows"],
                    ids=",".join(row["targetIds"]) or "-",
                    order="-".join(row["targetOrder"]) or "-",
                    candidate=int(row["candidate"]),
                )
            )
    lines.extend(
        [
            "",
            "## Nonempty Transferred Boxes",
            "",
            "| PDF | dest | variant | target box | words | target hits | strict hits |",
            "|---|---:|---|---|---|---:|---:|",
        ]
    )
    for record in result["records"]:
        for row in record["transferRows"]:
            if row["wordHitCount"] == 0:
                continue
            lines.append(
                "| `{pdf}` | `{dest}` | `{variant}` | `{target}` | `{words}` | `{target_hits}` | `{strict_hits}` |".format(
                    pdf=row["pdf"],
                    dest=row["destArticlePage"],
                    variant=row["variant"],
                    target=row["target"],
                    words=row["wordText"] or "-",
                    target_hits=row["targetTermHitCount"],
                    strict_hits=row["strictTermHitCount"],
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfOverdoseHeaderDeltaTransferGate']}`.",
            "- Measured `OVERDOSE` header offsets do not turn the page-76 active boxes into an all-four, active-order, or instruction-bearing selector on pages 74/78.",
            "- The transfer rows remain ordinary prose/layout contacts and source-backed R3 remains absent.",
            "",
            "## Next Move",
            "",
            "- Keep repeated `OVERDOSE` header-offset transfer mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue supplies a named unit/order or materially different page registration.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    repeated_header_lane = load_json(REPEATED_HEADER_LANE)
    records = [inspect_pdf(pdf, targets) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "articlePages": [ARTICLE_PAGE_START, ARTICLE_PAGE_END],
            "sourceArticlePage": 76,
            "destinationArticlePages": [74, 78],
            "variants": [
                "direct_delta",
                "x_mirror_about_header_delta",
                "x_mirror_about_page_center_delta",
            ],
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
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "repeatedHeaderLane": rel(REPEATED_HEADER_LANE),
            "repeatedHeaderLaneFingerprint": repeated_header_lane.get("summary", {}).get(
                "fingerprint"
            ),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseHeaderDeltaTransferGate": "current_pdf_overdose_header_delta_transfer_no_selector",
            "selectorUnlocked": False,
            "reason": "Measured repeated-OVERDOSE header offsets do not transfer active target boxes onto strict unit/order wording, all-four target coverage, or active-order target structure.",
            "nextMove": "Treat repeated OVERDOSE header offsets as layout context only unless new source material supplies unit/order evidence.",
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
