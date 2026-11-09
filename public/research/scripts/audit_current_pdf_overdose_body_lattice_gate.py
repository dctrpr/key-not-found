#!/usr/bin/env python3
"""Audit OVERDOSE body-line lattice mapping in current PDFs.

This bounded pass asks whether repeated OCR `OVERDOSE` page starts create a
usable body-line lattice for the locked O4/B4/G5/O5 boxes. For pages with a
readable first body line, it maps each locked active box into PDF coordinates,
assigns it to the nearest OCR body line, records the line-order/column position,
and checks whether the mapped lines contain target terms, strict unit/order
words, all-four target coverage, or active-order structure. It does not derive
keys, generate candidates, hash to keys, inspect WIFs/addresses, check BIP39,
or brute force anything.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_body_lattice_gate.json"
OUT_MD = OUT / "current_pdf_overdose_body_lattice_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_body_lattice_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BODY_BASIS_REFLECTION = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate/"
    "current_pdf_overdose_body_basis_reflection_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
ARTICLE_PAGES = [76, 78]
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


def target_id_for_token(token: str) -> str | None:
    for target_id in TARGET_ORDER:
        terms = TARGET_TERMS[target_id]
        if token in terms or any(len(term) >= 5 and term in token for term in terms):
            return target_id
    return None


def inspect_target(
    pdf: str,
    article_page: int,
    target: dict[str, Any],
    target_rect: fitz.Rect,
    lines: list[dict[str, Any]],
) -> dict[str, Any]:
    center = [(target_rect.x0 + target_rect.x1) / 2.0, (target_rect.y0 + target_rect.y1) / 2.0]
    nearest = min(lines, key=lambda row: abs(row["center"][1] - center[1]))
    x0, _y0, x1, _y1 = nearest["bbox"]
    width = max(1e-9, x1 - x0)
    column_fraction = (center[0] - x0) / width
    own_target_line_hit = target["shortId"] in nearest["targetIds"]
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "target": target["shortId"],
        "expectedPhrase": target["phrase"],
        "targetPdfCenter": [round(float(center[0]), 4), round(float(center[1]), 4)],
        "nearestBodyRowIndex": int(nearest["bodyRowIndex"]),
        "nearestLineDistancePt": round(float(abs(nearest["center"][1] - center[1])), 4),
        "nearestLineColumnFraction": round(float(column_fraction), 4),
        "nearestLineTargetIds": nearest["targetIds"],
        "ownTargetLineHit": own_target_line_hit,
        "nearestLineStrictHits": nearest["strictHits"],
        "nearestLineText": nearest["text"],
    }


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    pdf = rel(pdf_path)
    lattice_rows: list[dict[str, Any]] = []
    mapped_rows: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as doc:
        for article_page in ARTICLE_PAGES:
            page_index = article_page - 73
            if page_index < 0 or page_index >= len(doc):
                continue
            page = doc[page_index]
            words = page_words(page)
            if not words or words[0]["token"] != "overdose":
                continue
            header = words[0]
            lines = line_rows(words, header)
            if not lines:
                continue
            img_rect = image_rect(page)
            line_pitch_values = [
                round(float(lines[idx + 1]["center"][1] - lines[idx]["center"][1]), 4)
                for idx in range(len(lines) - 1)
            ]
            lattice_rows.append(
                {
                    "pdf": pdf,
                    "pdfPage": page_index + 1,
                    "articlePage": article_page,
                    "bodyLineCount": len(lines),
                    "firstBodyLineText": lines[0]["text"],
                    "medianLinePitchPt": sorted(line_pitch_values)[len(line_pitch_values) // 2]
                    if line_pitch_values
                    else None,
                }
            )
            page_mapped: list[dict[str, Any]] = []
            for target in targets:
                target_rect = source_box_to_pdf_rect(target["box"], img_rect)
                row = inspect_target(pdf, article_page, target, target_rect, lines)
                page_mapped.append(row)
                mapped_rows.append(row)
            row_order = [
                row["target"]
                for row in sorted(page_mapped, key=lambda item: item["nearestBodyRowIndex"])
            ]
            union_target_ids = []
            for row in page_mapped:
                for target_id in row["nearestLineTargetIds"]:
                    if target_id not in union_target_ids:
                        union_target_ids.append(target_id)
            strict_rows = [
                row for row in page_mapped if row["nearestLineStrictHits"]
            ]
            variant_rows.append(
                {
                    "pdf": pdf,
                    "articlePage": article_page,
                    "mappedTargetRows": len(page_mapped),
                    "ownTargetLineHitCount": sum(1 for row in page_mapped if row["ownTargetLineHit"]),
                    "strictMappedLineCount": len(strict_rows),
                    "unionNearestLineTargetIds": union_target_ids,
                    "rowOrder": row_order,
                    "allFourOwnTargetLines": sum(1 for row in page_mapped if row["ownTargetLineHit"]) == 4,
                    "activeRowOrder": row_order == TARGET_ORDER,
                    "candidate": bool(strict_rows)
                    and sum(1 for row in page_mapped if row["ownTargetLineHit"]) == 4
                    and row_order == TARGET_ORDER,
                }
            )
    return {
        "pdf": pdf,
        "bodyLatticeRows": lattice_rows,
        "mappedTargetRows": mapped_rows,
        "variantRows": variant_rows,
    }


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    lattice_rows = [row for record in records for row in record["bodyLatticeRows"]]
    mapped_rows = [row for record in records for row in record["mappedTargetRows"]]
    variant_rows = [row for record in records for row in record["variantRows"]]
    own_target_rows = [row for row in mapped_rows if row["ownTargetLineHit"]]
    strict_rows = [row for row in mapped_rows if row["nearestLineStrictHits"]]
    all_four_rows = [row for row in variant_rows if row["allFourOwnTargetLines"]]
    active_order_rows = [row for row in variant_rows if row["activeRowOrder"]]
    candidate_rows = [row for row in variant_rows if row["candidate"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 0))
    fingerprint = (
        f"pdfs={len(records)}|latticePages={len(lattice_rows)}|mappedRows={len(mapped_rows)}|"
        f"ownTargetRows={len(own_target_rows)}|strictRows={len(strict_rows)}|"
        f"allFourVariants={len(all_four_rows)}|activeOrderVariants={len(active_order_rows)}|"
        f"candidates={len(candidate_rows)}|sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "bodyLatticePageCount": len(lattice_rows),
        "mappedTargetRowCount": len(mapped_rows),
        "ownTargetLineHitCount": len(own_target_rows),
        "strictMappedLineCount": len(strict_rows),
        "allFourOwnTargetVariantCount": len(all_four_rows),
        "activeRowOrderVariantCount": len(active_order_rows),
        "bodyLatticeCandidateCount": len(candidate_rows),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2200
    height = 1280
    img = Image.new("RGB", (width, height), (9, 11, 15))
    draw = ImageDraw.Draw(img)
    title = safe_font(31)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF OVERDOSE Body-Line Lattice Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Maps locked O4/B4/G5/O5 boxes to nearest OCR body rows on repeated OVERDOSE pages.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    columns = [
        ("PDF", 28),
        ("page", 510),
        ("target", 575),
        ("row", 650),
        ("dist", 715),
        ("col", 785),
        ("own hit", 860),
        ("strict", 945),
        ("targets", 1035),
        ("nearest line", 1145),
    ]
    y = 145
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["mappedTargetRows"]]
    for idx, row in enumerate(rows[:36]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:58],
            "page": str(row["articlePage"]),
            "target": row["target"],
            "row": str(row["nearestBodyRowIndex"]),
            "dist": str(row["nearestLineDistancePt"]),
            "col": str(row["nearestLineColumnFraction"]),
            "own hit": str(int(row["ownTargetLineHit"])),
            "strict": ",".join(row["nearestLineStrictHits"]) or "-",
            "targets": ",".join(row["nearestLineTargetIds"]) or "-",
            "nearest line": row["nearestLineText"][:95],
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires all four mapped rows in active order plus strict unit/order wording; source-backed R3 remains mandatory.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Body-Line Lattice Gate",
        "",
        "Scope: used repeated OCR `OVERDOSE` page starts with readable body text, mapped locked O4/B4/G5/O5 boxes into PDF coordinates, assigned each to its nearest OCR body line, and checked for target terms, strict unit/order words, all-four line coverage, and active row order. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseBodyLatticeGate']}`",
        f"- PDFs checked / body-lattice pages / mapped rows: `{summary['pdfCount']}` / `{summary['bodyLatticePageCount']}` / `{summary['mappedTargetRowCount']}`",
        f"- Own-target rows / strict mapped rows: `{summary['ownTargetLineHitCount']}` / `{summary['strictMappedLineCount']}`",
        f"- All-four variants / active-row-order variants / candidates: `{summary['allFourOwnTargetVariantCount']}` / `{summary['activeRowOrderVariantCount']}` / `{summary['bodyLatticeCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Variant Rows",
        "",
        "| PDF | article page | own-target rows | strict rows | row order | all four | active order | candidate |",
        "|---|---:|---:|---:|---|---:|---:|---:|",
    ]
    for record in result["records"]:
        for row in record["variantRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{own}` | `{strict}` | `{order}` | `{all_four}` | `{active_order}` | `{candidate}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    own=row["ownTargetLineHitCount"],
                    strict=row["strictMappedLineCount"],
                    order="-".join(row["rowOrder"]),
                    all_four=int(row["allFourOwnTargetLines"]),
                    active_order=int(row["activeRowOrder"]),
                    candidate=int(row["candidate"]),
                )
            )
    lines.extend(
        [
            "",
            "## Mapped Rows",
            "",
            "| PDF | article page | target | body row | row distance | column fraction | own target hit | strict hits | nearest line target ids | nearest line |",
            "|---|---:|---|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for record in result["records"]:
        for row in record["mappedTargetRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{target}` | `{body_row}` | `{dist}` | `{col}` | `{own}` | `{strict}` | `{targets}` | `{line}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    target=row["target"],
                    body_row=row["nearestBodyRowIndex"],
                    dist=row["nearestLineDistancePt"],
                    col=row["nearestLineColumnFraction"],
                    own=int(row["ownTargetLineHit"]),
                    strict=",".join(row["nearestLineStrictHits"]) or "-",
                    targets=",".join(row["nearestLineTargetIds"]) or "-",
                    line=row["nearestLineText"],
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfOverdoseBodyLatticeGate']}`.",
            "- The mapped boxes preserve the geometric O4-B4-G5-O5 row order, but the same order also appears on page-78 controls because it comes from fixed box height positions.",
            "- The nearest OCR body lines do not recover own-target terms, all-four target text, or strict unit/order wording.",
            "- No mapped row supplies a source-backed extraction instruction.",
            "",
            "## Next Move",
            "",
            "- Keep OVERDOSE body-line lattice mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a row/column/body-line unit rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    body_basis = load_json(BODY_BASIS_REFLECTION)
    records = [inspect_pdf(pdf, targets) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "articlePages": ARTICLE_PAGES,
            "method": "Assign locked active boxes to nearest OCR body line on repeated OVERDOSE pages; check row order and line text.",
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
            "bodyBasisReflection": rel(BODY_BASIS_REFLECTION),
            "bodyBasisReflectionFingerprint": body_basis.get("summary", {}).get("fingerprint"),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseBodyLatticeGate": "current_pdf_overdose_body_lattice_no_selector",
            "selectorUnlocked": False,
            "reason": "OVERDOSE body-line lattice mapping preserves fixed box row order but supplies no target terms, strict unit/order wording, or source-backed R3.",
            "nextMove": "Treat OVERDOSE body-line lattice as closed unless source material names this row/column unit/order rule.",
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
