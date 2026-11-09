#!/usr/bin/env python3
"""Audit repeated OVERDOSE page-header lane projections in current PDFs.

The duplicate OCR PDFs start pages 74, 76, and 78 with OCR `OVERDOSE`. This
bounded pass treats those repeated page-start headers as controls, splits each
header into letter lanes, tests normal/mirrored/reversed lane projections, and
checks whether the lanes carry target terms, strict unit/order words, or an
active-order selector. It does not derive keys, generate candidates, hash to
keys, inspect WIFs/addresses, check BIP39, or brute force anything.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_repeated_overdose_header_lane_gate.json"
OUT_MD = OUT / "current_pdf_repeated_overdose_header_lane_gate.md"
OUT_SHEET = OUT / "current_pdf_repeated_overdose_header_lane_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
VISUAL_HEADER_FOOTER = ROOT / (
    "analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate/"
    "current_pdf_visual_header_footer_band_sequence_gate.json"
)

ARTICLE_PAGE_START = 73
ARTICLE_PAGE_END = 80
HEADER_WORD = "OVERDOSE"
LANE_HALF_WIDTH_PT = 10.0
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_TERMS = {
    "O4": {"buy", "buying", "dip"},
    "B4": {"billion", "novogratz"},
    "G5": {"volcano", "bonds", "bond"},
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
    return re.sub(r"[^a-z0-9]+", "", text.lower())


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


def render_page(page: fitz.Page) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    mode = "RGB" if pix.n >= 3 else "L"
    return Image.frombytes(mode, (pix.width, pix.height), pix.samples).convert("RGB")


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


def target_for_token(token: str) -> str | None:
    for target_id in TARGET_ORDER:
        for term in TARGET_TERMS[target_id]:
            if token == term or (len(term) >= 5 and term in token):
                return target_id
    return None


def lane_centers(header_bbox: list[float]) -> list[float]:
    x0, _y0, x1, _y1 = header_bbox
    width = x1 - x0
    return [x0 + ((idx + 0.5) * width / len(HEADER_WORD)) for idx in range(len(HEADER_WORD))]


def variant_lanes(page_width: float, header_bbox: list[float], variant: str) -> list[dict[str, Any]]:
    centers = lane_centers(header_bbox)
    labels = list(HEADER_WORD)
    if "x_mirror" in variant:
        centers = [page_width - center for center in centers]
        centers.reverse()
        labels.reverse()
    if "reverse_labels" in variant:
        labels.reverse()
    lanes = []
    for idx, (label, center) in enumerate(zip(labels, centers)):
        lanes.append(
            {
                "slot": idx,
                "label": label,
                "x0": round(float(center - LANE_HALF_WIDTH_PT), 4),
                "x1": round(float(center + LANE_HALF_WIDTH_PT), 4),
                "centerX": round(float(center), 4),
            }
        )
    return lanes


def lane_for_x(x: float, lanes: list[dict[str, Any]]) -> dict[str, Any] | None:
    for lane in lanes:
        if lane["x0"] <= x <= lane["x1"]:
            return lane
    return None


def inspect_lane_variant(
    pdf: str,
    article_page: int,
    page_width: float,
    header_word: dict[str, Any],
    words: list[dict[str, Any]],
    variant: str,
) -> dict[str, Any]:
    lanes = variant_lanes(page_width, header_word["bbox"], variant)
    lane_words: list[dict[str, Any]] = []
    target_hits: list[dict[str, Any]] = []
    strict_hits: list[dict[str, Any]] = []
    for word in words:
        if word["index"] == header_word["index"]:
            continue
        if word["center"][1] <= header_word["bbox"][3]:
            continue
        lane = lane_for_x(word["center"][0], lanes)
        if not lane:
            continue
        row = {
            "index": word["index"],
            "text": word["text"],
            "token": word["token"],
            "articlePage": article_page,
            "laneSlot": lane["slot"],
            "laneLabel": lane["label"],
            "center": word["center"],
        }
        lane_words.append(row)
        target_id = target_for_token(word["token"])
        if target_id:
            target_hits.append({**row, "targetId": target_id})
        if word["token"] in STRICT_TERMS:
            strict_hits.append(row)
    first_target_by_id: dict[str, int] = {}
    for hit in target_hits:
        first_target_by_id.setdefault(hit["targetId"], hit["index"])
    target_order = [
        target_id for target_id, _idx in sorted(first_target_by_id.items(), key=lambda item: item[1])
    ]
    target_ids = [target_id for target_id in TARGET_ORDER if target_id in first_target_by_id]
    lane_stream = compact(
        " ".join(
            f"{hit['targetId']}:{hit['laneLabel']}:{hit['token']}" for hit in target_hits
        )
    )
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "variant": variant,
        "laneHalfWidthPt": LANE_HALF_WIDTH_PT,
        "headerBbox": header_word["bbox"],
        "headerCenter": header_word["center"],
        "laneWordCount": len(lane_words),
        "strictHitCount": len(strict_hits),
        "strictHits": strict_hits,
        "targetHitCount": len(target_hits),
        "targetHits": target_hits,
        "targetIds": target_ids,
        "targetOrder": target_order,
        "allFourTargets": len(target_ids) == 4,
        "activeOrderTargets": target_order == TARGET_ORDER,
        "laneTargetStream": lane_stream,
        "candidate": bool(strict_hits)
        and (len(target_ids) == 4 or target_order == TARGET_ORDER),
    }


def inspect_pdf(pdf_path: Path) -> dict[str, Any]:
    pdf = rel(pdf_path)
    header_rows: list[dict[str, Any]] = []
    lane_rows: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as doc:
        page_limit = min(len(doc), ARTICLE_PAGE_END - ARTICLE_PAGE_START + 1)
        for page_index in range(page_limit):
            article_page = ARTICLE_PAGE_START + page_index
            page = doc[page_index]
            words = page_words(page)
            first_token = words[0]["token"] if words else ""
            if first_token != HEADER_WORD.lower():
                continue
            header_word = words[0]
            header_rows.append(
                {
                    "pdf": pdf,
                    "pdfPage": page_index + 1,
                    "articlePage": article_page,
                    "pageWidth": float(page.rect.width),
                    "pageHeight": float(page.rect.height),
                    "headerText": header_word["text"],
                    "headerBbox": header_word["bbox"],
                    "headerCenter": header_word["center"],
                    "wordCount": len(words),
                }
            )
            for variant in [
                "normal",
                "reverse_labels",
                "x_mirror",
                "x_mirror_reverse_labels",
            ]:
                lane_rows.append(
                    inspect_lane_variant(
                        pdf,
                        article_page,
                        float(page.rect.width),
                        header_word,
                        words,
                        variant,
                    )
                )
    return {
        "pdf": pdf,
        "overdoseHeaderPageCount": len(header_rows),
        "overdoseHeaderRows": header_rows,
        "laneRows": lane_rows,
    }


def draw_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    width = 2100
    height = 1380
    img = Image.new("RGB", (width, height), (9, 11, 15))
    draw = ImageDraw.Draw(img)
    title = safe_font(31)
    small = safe_font(16)
    tiny = safe_font(12)
    draw.text((28, 22), "Current PDF Repeated OVERDOSE Header Lane Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Repeated OCR OVERDOSE page starts on pages 74/76/78 are split into normal/mirrored/reversed vertical lanes.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    y = 145
    columns = [
        ("PDF", 28),
        ("page", 560),
        ("variant", 630),
        ("lane words", 845),
        ("strict", 955),
        ("targets", 1045),
        ("target order", 1165),
        ("candidate", 1325),
        ("target lane stream", 1435),
    ]
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["laneRows"]]
    for idx, row in enumerate(rows[:48]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:64],
            "page": str(row["articlePage"]),
            "variant": row["variant"],
            "lane words": str(row["laneWordCount"]),
            "strict": str(row["strictHitCount"]),
            "targets": ",".join(row["targetIds"]) or "-",
            "target order": "-".join(row["targetOrder"]) or "-",
            "candidate": str(int(row["candidate"])),
            "target lane stream": row["laneTargetStream"][:82] or "-",
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires lane-carried strict unit/order wording plus all-four or active-order target structure. Source-backed R3 remains separate.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    lane_rows = [row for record in records for row in record["laneRows"]]
    header_rows = [row for record in records for row in record["overdoseHeaderRows"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    triggers = int(reopen.get("summary", {}).get("triggerCount", 0))
    target_rows = [row for row in lane_rows if row["targetHitCount"] > 0]
    strict_rows = [row for row in lane_rows if row["strictHitCount"] > 0]
    all_four_rows = [row for row in lane_rows if row["allFourTargets"]]
    active_order_rows = [row for row in lane_rows if row["activeOrderTargets"]]
    candidate_rows = [row for row in lane_rows if row["candidate"]]
    page76_target_rows = [
        row for row in target_rows if int(row["articlePage"]) == 76
    ]
    fingerprint = (
        f"pdfs={len(records)}|overdoseHeaders={len(header_rows)}|laneRows={len(lane_rows)}|"
        f"targetRows={len(target_rows)}|strictRows={len(strict_rows)}|"
        f"allFourRows={len(all_four_rows)}|activeOrderRows={len(active_order_rows)}|"
        f"page76TargetRows={len(page76_target_rows)}|candidates={len(candidate_rows)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{triggers}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "overdoseHeaderRowCount": len(header_rows),
        "laneRowsChecked": len(lane_rows),
        "targetLaneRowCount": len(target_rows),
        "strictLaneRowCount": len(strict_rows),
        "allFourLaneRowCount": len(all_four_rows),
        "activeOrderLaneRowCount": len(active_order_rows),
        "page76TargetLaneRowCount": len(page76_target_rows),
        "headerLaneCandidateCount": len(candidate_rows),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": triggers,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Repeated OVERDOSE Header Lane Gate",
        "",
        "Scope: used the repeated OCR `OVERDOSE` page-start rows in the current PDFs as controls, split each header into normal/mirrored/reversed vertical letter lanes, and checked whether those lanes carry target terms, strict unit/order words, or active-order structure. This is a bounded layout/OCR-overlay check only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfRepeatedOverdoseHeaderLaneGate']}`",
        f"- PDFs checked / OVERDOSE header rows / lane rows checked: `{summary['pdfCount']}` / `{summary['overdoseHeaderRowCount']}` / `{summary['laneRowsChecked']}`",
        f"- Target lane rows / strict lane rows: `{summary['targetLaneRowCount']}` / `{summary['strictLaneRowCount']}`",
        f"- All-four lane rows / active-order lane rows: `{summary['allFourLaneRowCount']}` / `{summary['activeOrderLaneRowCount']}`",
        f"- Page-76 target lane rows / candidates: `{summary['page76TargetLaneRowCount']}` / `{summary['headerLaneCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Header Rows",
        "",
        "| PDF | article page | word count | header bbox |",
        "|---|---:|---:|---|",
    ]
    for record in result["records"]:
        for row in record["overdoseHeaderRows"]:
            lines.append(
                f"| `{row['pdf']}` | `{row['articlePage']}` | `{row['wordCount']}` | `{[round(v, 3) for v in row['headerBbox']]}` |"
            )
    lines.extend(
        [
            "",
            "## Lane Rows",
            "",
            "| PDF | article page | variant | lane words | strict | targets | target order | candidate | target lane stream |",
            "|---|---:|---|---:|---:|---|---|---:|---|",
        ]
    )
    for record in result["records"]:
        for row in record["laneRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{variant}` | `{lane_words}` | `{strict}` | `{targets}` | `{order}` | `{candidate}` | `{stream}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    variant=row["variant"],
                    lane_words=row["laneWordCount"],
                    strict=row["strictHitCount"],
                    targets=",".join(row["targetIds"]) or "-",
                    order="-".join(row["targetOrder"]) or "-",
                    candidate=int(row["candidate"]),
                    stream=row["laneTargetStream"] or "-",
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfRepeatedOverdoseHeaderLaneGate']}`.",
            "- Repeated `OVERDOSE` page-start lanes do not combine strict unit/order wording with all-four active target coverage or active target order.",
            "- Page 76 target-lane hits are sparse context, and the repeated page-start controls do not supply a source-backed extraction rule.",
            "",
            "## Next Move",
            "",
            "- Keep repeated `OVERDOSE` header lane mechanics closed for the current PDFs. Continue only with source/provenance evidence that names a unit/order, or with a true source asset that materially changes the page registration.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    visual_header_footer = load_json(VISUAL_HEADER_FOOTER)
    records = [inspect_pdf(pdf) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "articlePages": [ARTICLE_PAGE_START, ARTICLE_PAGE_END],
            "headerWord": HEADER_WORD,
            "laneHalfWidthPt": LANE_HALF_WIDTH_PT,
            "variants": [
                "normal",
                "reverse_labels",
                "x_mirror",
                "x_mirror_reverse_labels",
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
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "visualHeaderFooterBandSequence": rel(VISUAL_HEADER_FOOTER),
            "visualHeaderFooterFingerprint": visual_header_footer.get("summary", {}).get(
                "fingerprint"
            ),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfRepeatedOverdoseHeaderLaneGate": "current_pdf_repeated_overdose_header_lane_no_selector",
            "selectorUnlocked": False,
            "reason": "Repeated OVERDOSE page-start lanes do not carry strict unit/order wording with all-four or active-order target structure, and source-backed R3 remains absent.",
            "nextMove": "Treat repeated OVERDOSE lane mechanics as context only unless new source material supplies unit/order evidence.",
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
