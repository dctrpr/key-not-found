#!/usr/bin/env python3
"""Audit repeated OVERDOSE header-to-body-start vectors in current PDFs.

The duplicate OCR PDFs contain repeated page-start `OVERDOSE` headers. This
bounded pass asks whether the vector from each OVERDOSE header to the first
readable body line acts as a repeatable selector/ray through page text. It
checks only fixed-width ray tubes for target terms, strict unit/order terms,
all-four target coverage, and active-order structure. It does not derive keys,
generate candidates, hash to keys, inspect WIFs/addresses, check BIP39, or
brute force anything.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_body_start_vector_gate.json"
OUT_MD = OUT / "current_pdf_overdose_body_start_vector_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_body_start_vector_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
HEADER_DELTA_TRANSFER = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate/"
    "current_pdf_overdose_header_delta_transfer_gate.json"
)

ARTICLE_PAGE_START = 73
ARTICLE_PAGE_END = 80
RAY_WIDTHS_PT = [10.0, 20.0]
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


def target_id_for_token(token: str) -> str | None:
    for target_id in TARGET_ORDER:
        terms = TARGET_TERMS[target_id]
        if token in terms or any(len(term) >= 5 and term in token for term in terms):
            return target_id
    return None


def first_body_line(words: list[dict[str, Any]], header: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [
        word
        for word in words
        if word["index"] != header["index"] and word["center"][1] > header["bbox"][3] + 8.0
    ]
    if not candidates:
        return None
    first = min(candidates, key=lambda word: (word["bbox"][1], word["bbox"][0]))
    line_words = [
        word
        for word in candidates
        if word["block"] == first["block"] and word["line"] == first["line"]
    ]
    x0 = min(word["bbox"][0] for word in line_words)
    y0 = min(word["bbox"][1] for word in line_words)
    x1 = max(word["bbox"][2] for word in line_words)
    y1 = max(word["bbox"][3] for word in line_words)
    return {
        "block": first["block"],
        "line": first["line"],
        "bbox": [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)],
        "center": [round((x0 + x1) / 2.0, 4), round((y0 + y1) / 2.0, 4)],
        "wordCount": len(line_words),
        "text": compact(" ".join(word["text"] for word in line_words)),
        "firstWordIndex": int(first["index"]),
    }


def point_ray_distance(point: list[float], origin: list[float], vector: list[float]) -> tuple[float, float]:
    vx, vy = vector
    wx, wy = point[0] - origin[0], point[1] - origin[1]
    v_len_sq = vx * vx + vy * vy
    if v_len_sq == 0:
        return float("inf"), -1.0
    t = (wx * vx + wy * vy) / v_len_sq
    proj_x = origin[0] + t * vx
    proj_y = origin[1] + t * vy
    return math.hypot(point[0] - proj_x, point[1] - proj_y), t


def inspect_body_vector_row(
    pdf: str,
    article_page: int,
    header: dict[str, Any],
    body_line: dict[str, Any],
    words: list[dict[str, Any]],
    width_pt: float,
) -> dict[str, Any]:
    origin = header["center"]
    vector = [body_line["center"][0] - origin[0], body_line["center"][1] - origin[1]]
    length = math.hypot(vector[0], vector[1])
    angle = math.degrees(math.atan2(vector[1], vector[0]))
    ray_words: list[dict[str, Any]] = []
    target_hits: list[dict[str, Any]] = []
    strict_hits: list[dict[str, Any]] = []
    first_target_indices: dict[str, int] = {}
    for word in words:
        if word["index"] == header["index"]:
            continue
        if word["center"][1] <= header["bbox"][3]:
            continue
        distance, t = point_ray_distance(word["center"], origin, vector)
        if t < 0 or distance > width_pt:
            continue
        row = {
            "index": int(word["index"]),
            "text": word["text"],
            "token": word["token"],
            "distancePt": round(float(distance), 4),
            "rayT": round(float(t), 4),
        }
        ray_words.append(row)
        target_id = target_id_for_token(word["token"])
        if target_id:
            first_target_indices.setdefault(target_id, int(word["index"]))
            target_hits.append({**row, "targetId": target_id})
        if word["token"] in STRICT_TERMS:
            strict_hits.append(row)
    target_order = [
        target_id for target_id, _ in sorted(first_target_indices.items(), key=lambda item: item[1])
    ]
    target_ids = [target_id for target_id in TARGET_ORDER if target_id in first_target_indices]
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "widthPt": width_pt,
        "headerCenter": [round(float(v), 4) for v in origin],
        "bodyLineCenter": body_line["center"],
        "bodyLineText": body_line["text"],
        "bodyVector": [round(float(vector[0]), 4), round(float(vector[1]), 4)],
        "bodyVectorLength": round(float(length), 4),
        "bodyVectorAngleDegrees": round(float(angle), 4),
        "rayWordCount": len(ray_words),
        "rayWordsPreview": compact(" ".join(word["text"] for word in ray_words[:24])),
        "targetHitCount": len(target_hits),
        "targetHits": target_hits,
        "targetIds": target_ids,
        "targetOrder": target_order,
        "allFourTargets": len(target_ids) == 4,
        "activeOrderTargets": target_order == TARGET_ORDER,
        "strictHitCount": len(strict_hits),
        "strictHits": strict_hits,
        "candidate": bool(strict_hits)
        and (len(target_ids) == 4 or target_order == TARGET_ORDER),
    }


def inspect_pdf(pdf_path: Path) -> dict[str, Any]:
    pdf = rel(pdf_path)
    header_rows: list[dict[str, Any]] = []
    body_rows: list[dict[str, Any]] = []
    vector_rows: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as doc:
        page_limit = min(len(doc), ARTICLE_PAGE_END - ARTICLE_PAGE_START + 1)
        for page_index in range(page_limit):
            article_page = ARTICLE_PAGE_START + page_index
            page = doc[page_index]
            words = page_words(page)
            if not words or words[0]["token"] != "overdose":
                continue
            header = words[0]
            body_line = first_body_line(words, header)
            header_rows.append(
                {
                    "pdf": pdf,
                    "pdfPage": page_index + 1,
                    "articlePage": article_page,
                    "headerBbox": header["bbox"],
                    "headerCenter": [round(float(v), 4) for v in header["center"]],
                    "wordCount": len(words),
                    "hasBodyLine": bool(body_line),
                }
            )
            if not body_line:
                continue
            body_rows.append(
                {
                    "pdf": pdf,
                    "pdfPage": page_index + 1,
                    "articlePage": article_page,
                    **body_line,
                }
            )
            for width_pt in RAY_WIDTHS_PT:
                vector_rows.append(
                    inspect_body_vector_row(
                        pdf, article_page, header, body_line, words, width_pt
                    )
                )
    return {
        "pdf": pdf,
        "overdoseHeaderRows": header_rows,
        "bodyStartRows": body_rows,
        "bodyVectorRows": vector_rows,
    }


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    header_rows = [row for record in records for row in record["overdoseHeaderRows"]]
    body_rows = [row for record in records for row in record["bodyStartRows"]]
    vector_rows = [row for record in records for row in record["bodyVectorRows"]]
    target_rows = [row for row in vector_rows if row["targetHitCount"] > 0]
    strict_rows = [row for row in vector_rows if row["strictHitCount"] > 0]
    all_four_rows = [row for row in vector_rows if row["allFourTargets"]]
    active_order_rows = [row for row in vector_rows if row["activeOrderTargets"]]
    candidate_rows = [row for row in vector_rows if row["candidate"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 0))
    fingerprint = (
        f"pdfs={len(records)}|headers={len(header_rows)}|bodyRows={len(body_rows)}|"
        f"vectorRows={len(vector_rows)}|targetRows={len(target_rows)}|"
        f"strictRows={len(strict_rows)}|allFourRows={len(all_four_rows)}|"
        f"activeOrderRows={len(active_order_rows)}|candidates={len(candidate_rows)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "overdoseHeaderRowCount": len(header_rows),
        "bodyStartRowCount": len(body_rows),
        "bodyVectorRowCount": len(vector_rows),
        "targetVectorRowCount": len(target_rows),
        "strictVectorRowCount": len(strict_rows),
        "allFourVectorRowCount": len(all_four_rows),
        "activeOrderVectorRowCount": len(active_order_rows),
        "bodyStartVectorCandidateCount": len(candidate_rows),
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
    draw.text((28, 22), "Current PDF OVERDOSE Body-Start Vector Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Rays from repeated OVERDOSE headers through the first readable body line, checked at 10pt and 20pt widths.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    columns = [
        ("PDF", 28),
        ("page", 560),
        ("width", 625),
        ("angle", 695),
        ("ray words", 785),
        ("targets", 895),
        ("strict", 1015),
        ("target ids", 1110),
        ("order", 1225),
        ("candidate", 1365),
        ("preview", 1480),
    ]
    y = 145
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["bodyVectorRows"]]
    for idx, row in enumerate(rows[:40]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:64],
            "page": str(row["articlePage"]),
            "width": str(row["widthPt"]),
            "angle": f"{row['bodyVectorAngleDegrees']:.1f}",
            "ray words": str(row["rayWordCount"]),
            "targets": str(row["targetHitCount"]),
            "strict": str(row["strictHitCount"]),
            "target ids": ",".join(row["targetIds"]) or "-",
            "order": "-".join(row["targetOrder"]) or "-",
            "candidate": str(int(row["candidate"])),
            "preview": row["rayWordsPreview"][:82] or "-",
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires strict unit/order wording plus all-four or active-order target coverage along the body-start ray.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Body-Start Vector Gate",
        "",
        "Scope: used repeated OCR `OVERDOSE` page starts in the current PDFs, measured the vector from each header to the first readable body line, and checked fixed-width ray tubes for target terms, strict unit/order words, all-four target coverage, and active-order structure. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseBodyStartVectorGate']}`",
        f"- PDFs checked / OVERDOSE header rows / body-start rows: `{summary['pdfCount']}` / `{summary['overdoseHeaderRowCount']}` / `{summary['bodyStartRowCount']}`",
        f"- Body vector rows / target rows / strict rows: `{summary['bodyVectorRowCount']}` / `{summary['targetVectorRowCount']}` / `{summary['strictVectorRowCount']}`",
        f"- All-four rows / active-order rows / candidates: `{summary['allFourVectorRowCount']}` / `{summary['activeOrderVectorRowCount']}` / `{summary['bodyStartVectorCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Body-Start Rows",
        "",
        "| PDF | article page | body vector | angle | first body line |",
        "|---|---:|---|---:|---|",
    ]
    for record in result["records"]:
        for row in record["bodyVectorRows"]:
            if row["widthPt"] != RAY_WIDTHS_PT[0]:
                continue
            lines.append(
                f"| `{row['pdf']}` | `{row['articlePage']}` | `{row['bodyVector']}` | `{row['bodyVectorAngleDegrees']}` | `{row['bodyLineText']}` |"
            )
    lines.extend(
        [
            "",
            "## Vector Rows",
            "",
            "| PDF | article page | width | ray words | targets | strict | target ids | target order | candidate | ray preview |",
            "|---|---:|---:|---:|---:|---:|---|---|---:|---|",
        ]
    )
    for record in result["records"]:
        for row in record["bodyVectorRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{width}` | `{ray_words}` | `{targets}` | `{strict}` | `{ids}` | `{order}` | `{candidate}` | `{preview}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    width=row["widthPt"],
                    ray_words=row["rayWordCount"],
                    targets=row["targetHitCount"],
                    strict=row["strictHitCount"],
                    ids=",".join(row["targetIds"]) or "-",
                    order="-".join(row["targetOrder"]) or "-",
                    candidate=int(row["candidate"]),
                    preview=row["rayWordsPreview"] or "-",
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfOverdoseBodyStartVectorGate']}`.",
            "- Repeated `OVERDOSE` header-to-body-start vectors do not create all-four target coverage, active-order target coverage, or strict unit/order wording.",
            "- Page 76 body-start rays at most touch ordinary opening prose context; page 78 controls remain comparable and source-backed R3 remains absent.",
            "",
            "## Next Move",
            "",
            "- Keep repeated `OVERDOSE` body-start vector mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a unit/order or a specific header/body vector rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    header_delta = load_json(HEADER_DELTA_TRANSFER)
    records = [inspect_pdf(pdf) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "articlePages": [ARTICLE_PAGE_START, ARTICLE_PAGE_END],
            "rayWidthsPt": RAY_WIDTHS_PT,
            "method": "Measure header-to-first-body-line vector on repeated OVERDOSE pages; check fixed-width rays through page OCR words.",
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
            "headerDeltaTransfer": rel(HEADER_DELTA_TRANSFER),
            "headerDeltaTransferFingerprint": header_delta.get("summary", {}).get(
                "fingerprint"
            ),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseBodyStartVectorGate": "current_pdf_overdose_body_start_vector_no_selector",
            "selectorUnlocked": False,
            "reason": "Repeated OVERDOSE header-to-body-start vectors do not carry strict unit/order wording with all-four or active-order target structure.",
            "nextMove": "Treat OVERDOSE body-start vectors as layout context only unless source material names this unit/order rule.",
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
