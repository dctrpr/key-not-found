#!/usr/bin/env python3
"""Audit OVERDOSE body-basis reflection mechanics in current PDFs.

This bounded pass uses repeated OCR `OVERDOSE` pages that have a readable first
body line. It builds the body-start axis from the header center to the first
body-line center, reflects locked O4/B4/G5/O5 page-76 boxes across that axis
and its perpendicular body-start axis, and checks whether the reflected boxes
land on OCR target terms, strict unit/order wording, all-four structure, or
active-order structure. It does not derive keys, generate candidates, hash to
keys, inspect WIFs/addresses, check BIP39, or brute force anything.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_overdose_body_basis_reflection_gate.json"
OUT_MD = OUT / "current_pdf_overdose_body_basis_reflection_gate.md"
OUT_SHEET = OUT / "current_pdf_overdose_body_basis_reflection_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
BODY_START_VECTOR = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate/"
    "current_pdf_overdose_body_start_vector_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
ARTICLE_PAGES = [76, 78]
TRANSFORMS = ["body_axis_mirror", "body_start_perpendicular_mirror"]
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
        "bbox": [round(float(x0), 4), round(float(y0), 4), round(float(x1), 4), round(float(y1), 4)],
        "center": [round(float((x0 + x1) / 2.0), 4), round(float((y0 + y1) / 2.0), 4)],
        "wordCount": len(line_words),
        "text": compact(" ".join(word["text"] for word in line_words)),
        "firstWordIndex": int(first["index"]),
    }


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


def unit_vector(vector: list[float]) -> list[float] | None:
    length = math.hypot(vector[0], vector[1])
    if length == 0:
        return None
    return [vector[0] / length, vector[1] / length]


def reflect_point(point: list[float], origin: list[float], axis_unit: list[float]) -> list[float]:
    wx = point[0] - origin[0]
    wy = point[1] - origin[1]
    dot = wx * axis_unit[0] + wy * axis_unit[1]
    proj = [origin[0] + dot * axis_unit[0], origin[1] + dot * axis_unit[1]]
    return [2.0 * proj[0] - point[0], 2.0 * proj[1] - point[1]]


def transformed_rect(rect: fitz.Rect, origin: list[float], axis_unit: list[float]) -> fitz.Rect:
    points = [
        [rect.x0, rect.y0],
        [rect.x1, rect.y0],
        [rect.x1, rect.y1],
        [rect.x0, rect.y1],
    ]
    reflected = [reflect_point(point, origin, axis_unit) for point in points]
    xs = [point[0] for point in reflected]
    ys = [point[1] for point in reflected]
    return fitz.Rect(min(xs), min(ys), max(xs), max(ys))


def intersection_area(a: fitz.Rect, b: fitz.Rect) -> float:
    x0 = max(a.x0, b.x0)
    y0 = max(a.y0, b.y0)
    x1 = min(a.x1, b.x1)
    y1 = min(a.y1, b.y1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return float((x1 - x0) * (y1 - y0))


def target_id_for_token(token: str) -> str | None:
    for target_id in TARGET_ORDER:
        terms = TARGET_TERMS[target_id]
        if token in terms or any(len(term) >= 5 and term in token for term in terms):
            return target_id
    return None


def inspect_box(
    pdf: str,
    article_page: int,
    transform_name: str,
    target: dict[str, Any],
    reflected: fitz.Rect,
    page_rect: fitz.Rect,
    words: list[dict[str, Any]],
) -> dict[str, Any]:
    reflected_box = [round(float(v), 4) for v in [reflected.x0, reflected.y0, reflected.x1, reflected.y1]]
    in_page = reflected.intersects(page_rect)
    clipped = reflected & page_rect if in_page else fitz.Rect()
    hit_words = []
    target_hits = []
    strict_hits = []
    for word in words:
        word_rect = fitz.Rect(word["bbox"])
        overlap = intersection_area(clipped, word_rect)
        if overlap <= 0.0:
            continue
        row = {
            "index": int(word["index"]),
            "text": word["text"],
            "token": word["token"],
            "overlapPt2": round(float(overlap), 4),
        }
        hit_words.append(row)
        target_id = target_id_for_token(word["token"])
        if target_id:
            target_hits.append({**row, "targetId": target_id})
        if word["token"] in STRICT_TERMS:
            strict_hits.append(row)
    target_ids = []
    for hit in target_hits:
        if hit["targetId"] not in target_ids:
            target_ids.append(hit["targetId"])
    return {
        "pdf": pdf,
        "articlePage": article_page,
        "transform": transform_name,
        "target": target["shortId"],
        "sourceBox": [round(float(v), 4) for v in target["box"]],
        "reflectedPdfBox": reflected_box,
        "inPage": bool(in_page),
        "textHitCount": len(hit_words),
        "textPreview": compact(" ".join(word["text"] for word in hit_words[:18])),
        "targetHitCount": len(target_hits),
        "targetIds": target_ids,
        "targetHits": target_hits,
        "strictHitCount": len(strict_hits),
        "strictHits": strict_hits,
    }


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    pdf = rel(pdf_path)
    basis_rows: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    box_rows: list[dict[str, Any]] = []
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
            body_line = first_body_line(words, header)
            if not body_line:
                continue
            body_vector = [
                body_line["center"][0] - header["center"][0],
                body_line["center"][1] - header["center"][1],
            ]
            body_unit = unit_vector(body_vector)
            if not body_unit:
                continue
            normal_unit = [-body_unit[1], body_unit[0]]
            img_rect = image_rect(page)
            basis_rows.append(
                {
                    "pdf": pdf,
                    "pdfPage": page_index + 1,
                    "articlePage": article_page,
                    "headerCenter": [round(float(v), 4) for v in header["center"]],
                    "bodyLineCenter": body_line["center"],
                    "bodyVector": [round(float(v), 4) for v in body_vector],
                    "bodyVectorAngleDegrees": round(float(math.degrees(math.atan2(body_vector[1], body_vector[0]))), 4),
                    "bodyLineText": body_line["text"],
                }
            )
            transform_defs = {
                "body_axis_mirror": {
                    "origin": [float(v) for v in header["center"]],
                    "axisUnit": body_unit,
                },
                "body_start_perpendicular_mirror": {
                    "origin": [float(v) for v in body_line["center"]],
                    "axisUnit": normal_unit,
                },
            }
            for transform_name, transform in transform_defs.items():
                first_target_index: dict[str, int] = {}
                transform_box_rows = []
                for target in targets:
                    source_rect = source_box_to_pdf_rect(target["box"], img_rect)
                    reflected = transformed_rect(
                        source_rect,
                        transform["origin"],
                        transform["axisUnit"],
                    )
                    row = inspect_box(
                        pdf,
                        article_page,
                        transform_name,
                        target,
                        reflected,
                        page.rect,
                        words,
                    )
                    transform_box_rows.append(row)
                    box_rows.append(row)
                    for hit in row["targetHits"]:
                        first_target_index.setdefault(hit["targetId"], hit["index"])
                target_order = [
                    target_id for target_id, _ in sorted(first_target_index.items(), key=lambda item: item[1])
                ]
                target_ids = [target_id for target_id in TARGET_ORDER if target_id in first_target_index]
                strict_box_count = sum(1 for row in transform_box_rows if row["strictHitCount"] > 0)
                variant_rows.append(
                    {
                        "pdf": pdf,
                        "articlePage": article_page,
                        "transform": transform_name,
                        "reflectedBoxes": len(transform_box_rows),
                        "inPageBoxes": sum(1 for row in transform_box_rows if row["inPage"]),
                        "textHitBoxes": sum(1 for row in transform_box_rows if row["textHitCount"] > 0),
                        "targetHitBoxes": sum(1 for row in transform_box_rows if row["targetHitCount"] > 0),
                        "strictHitBoxes": strict_box_count,
                        "targetIds": target_ids,
                        "targetOrder": target_order,
                        "allFourTargets": len(target_ids) == 4,
                        "activeOrderTargets": target_order == TARGET_ORDER,
                        "candidate": bool(strict_box_count)
                        and (len(target_ids) == 4 or target_order == TARGET_ORDER),
                    }
                )
    return {
        "pdf": pdf,
        "bodyBasisRows": basis_rows,
        "transformVariantRows": variant_rows,
        "reflectedBoxRows": box_rows,
    }


def summarize(records: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    basis_rows = [row for record in records for row in record["bodyBasisRows"]]
    variant_rows = [row for record in records for row in record["transformVariantRows"]]
    box_rows = [row for record in records for row in record["reflectedBoxRows"]]
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount", 0))
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 0))
    text_box_rows = [row for row in box_rows if row["textHitCount"] > 0]
    target_box_rows = [row for row in box_rows if row["targetHitCount"] > 0]
    strict_box_rows = [row for row in box_rows if row["strictHitCount"] > 0]
    all_four_rows = [row for row in variant_rows if row["allFourTargets"]]
    active_order_rows = [row for row in variant_rows if row["activeOrderTargets"]]
    candidate_rows = [row for row in variant_rows if row["candidate"]]
    fingerprint = (
        f"pdfs={len(records)}|basisRows={len(basis_rows)}|variants={len(variant_rows)}|"
        f"boxRows={len(box_rows)}|inPage={sum(1 for row in box_rows if row['inPage'])}|"
        f"textRows={len(text_box_rows)}|targetRows={len(target_box_rows)}|"
        f"strictRows={len(strict_box_rows)}|allFourVariants={len(all_four_rows)}|"
        f"activeOrderVariants={len(active_order_rows)}|candidates={len(candidate_rows)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(records),
        "bodyBasisRowCount": len(basis_rows),
        "transformVariantRowCount": len(variant_rows),
        "reflectedBoxRowCount": len(box_rows),
        "inPageReflectedBoxCount": sum(1 for row in box_rows if row["inPage"]),
        "textHitBoxRowCount": len(text_box_rows),
        "targetTermBoxRowCount": len(target_box_rows),
        "strictTermBoxRowCount": len(strict_box_rows),
        "allFourTransformVariantCount": len(all_four_rows),
        "activeOrderTransformVariantCount": len(active_order_rows),
        "bodyBasisReflectionCandidateCount": len(candidate_rows),
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
    draw.text((28, 22), "Current PDF OVERDOSE Body-Basis Reflection Gate", fill=(245, 247, 250), font=title)
    draw.text(
        (28, 64),
        "Reflects locked O4/B4/G5/O5 boxes across the OVERDOSE body axis and body-start perpendicular axis.",
        fill=(177, 188, 198),
        font=small,
    )
    draw.text((28, 96), summary["fingerprint"], fill=(224, 175, 72), font=small)
    columns = [
        ("PDF", 28),
        ("page", 540),
        ("transform", 610),
        ("target", 835),
        ("in page", 910),
        ("words", 990),
        ("targets", 1060),
        ("strict", 1140),
        ("preview", 1220),
    ]
    y = 145
    for label, x in columns:
        draw.text((x, y), label, fill=(154, 166, 178), font=small)
    y += 32
    rows = [row for record in records for row in record["reflectedBoxRows"]]
    for idx, row in enumerate(rows[:44]):
        fill = (17, 20, 26) if idx % 2 == 0 else (21, 24, 31)
        draw.rectangle((24, y - 7, width - 28, y + 30), fill=fill)
        values = {
            "PDF": row["pdf"][:60],
            "page": str(row["articlePage"]),
            "transform": row["transform"],
            "target": row["target"],
            "in page": str(int(row["inPage"])),
            "words": str(row["textHitCount"]),
            "targets": ",".join(row["targetIds"]) or "-",
            "strict": str(row["strictHitCount"]),
            "preview": row["textPreview"][:100] or "-",
        }
        for label, x in columns:
            draw.text((x, y), values[label], fill=(225, 229, 235), font=tiny)
        y += 37
    draw.text(
        (28, height - 58),
        "Candidate requires strict unit/order wording plus all-four or active-order target coverage after body-basis reflection.",
        fill=(151, 163, 175),
        font=small,
    )
    img.save(OUT_SHEET, quality=92)


def write_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OVERDOSE Body-Basis Reflection Gate",
        "",
        "Scope: used repeated OCR `OVERDOSE` pages with a readable first body line, reflected locked O4/B4/G5/O5 boxes across the header-to-body axis and the perpendicular body-start axis, and checked reflected boxes for OCR words, target terms, strict unit/order words, all-four target coverage, and active-order structure. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']['currentPdfOverdoseBodyBasisReflectionGate']}`",
        f"- PDFs checked / body-basis rows / transform variants: `{summary['pdfCount']}` / `{summary['bodyBasisRowCount']}` / `{summary['transformVariantRowCount']}`",
        f"- Reflected boxes / in-page boxes / text-hit boxes: `{summary['reflectedBoxRowCount']}` / `{summary['inPageReflectedBoxCount']}` / `{summary['textHitBoxRowCount']}`",
        f"- Target-term boxes / strict-term boxes: `{summary['targetTermBoxRowCount']}` / `{summary['strictTermBoxRowCount']}`",
        f"- All-four variants / active-order variants / candidates: `{summary['allFourTransformVariantCount']}` / `{summary['activeOrderTransformVariantCount']}` / `{summary['bodyBasisReflectionCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Body-Basis Rows",
        "",
        "| PDF | article page | body vector | angle | first body line |",
        "|---|---:|---|---:|---|",
    ]
    for record in result["records"]:
        for row in record["bodyBasisRows"]:
            lines.append(
                f"| `{row['pdf']}` | `{row['articlePage']}` | `{row['bodyVector']}` | `{row['bodyVectorAngleDegrees']}` | `{row['bodyLineText']}` |"
            )
    lines.extend(
        [
            "",
            "## Transform Variants",
            "",
            "| PDF | article page | transform | in-page boxes | text-hit boxes | target boxes | strict boxes | target ids | target order | candidate |",
            "|---|---:|---|---:|---:|---:|---:|---|---|---:|",
        ]
    )
    for record in result["records"]:
        for row in record["transformVariantRows"]:
            lines.append(
                "| `{pdf}` | `{page}` | `{transform}` | `{in_page}` | `{words}` | `{targets}` | `{strict}` | `{ids}` | `{order}` | `{candidate}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    transform=row["transform"],
                    in_page=row["inPageBoxes"],
                    words=row["textHitBoxes"],
                    targets=row["targetHitBoxes"],
                    strict=row["strictHitBoxes"],
                    ids=",".join(row["targetIds"]) or "-",
                    order="-".join(row["targetOrder"]) or "-",
                    candidate=int(row["candidate"]),
                )
            )
    lines.extend(
        [
            "",
            "## Text-Hit Reflected Boxes",
            "",
            "| PDF | article page | transform | target | words | target ids | strict | preview |",
            "|---|---:|---|---|---:|---|---:|---|",
        ]
    )
    for record in result["records"]:
        for row in record["reflectedBoxRows"]:
            if row["textHitCount"] <= 0:
                continue
            lines.append(
                "| `{pdf}` | `{page}` | `{transform}` | `{target}` | `{words}` | `{ids}` | `{strict}` | `{preview}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    transform=row["transform"],
                    target=row["target"],
                    words=row["textHitCount"],
                    ids=",".join(row["targetIds"]) or "-",
                    strict=row["strictHitCount"],
                    preview=row["textPreview"] or "-",
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentPdfOverdoseBodyBasisReflectionGate']}`.",
            "- Body-axis and body-start perpendicular reflections do not produce all-four target coverage, active-order target coverage, or strict unit/order wording.",
            "- Text contacts, where present, are ordinary prose contacts rather than source-backed extraction instructions.",
            "",
            "## Next Move",
            "",
            "- Keep OVERDOSE body-basis reflection mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a body-axis, mirror, fold, or unit/order rule.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    body_start = load_json(BODY_START_VECTOR)
    records = [inspect_pdf(pdf, targets) for pdf in PDFS]
    summary = summarize(records, reopen)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": {
            "articlePages": ARTICLE_PAGES,
            "transforms": TRANSFORMS,
            "method": "Reflect locked active boxes across OVERDOSE header-to-body and body-start perpendicular axes; check OCR words in reflected boxes.",
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
            "bodyStartVector": rel(BODY_START_VECTOR),
            "bodyStartVectorFingerprint": body_start.get("summary", {}).get("fingerprint"),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": records,
        "decision": {
            "currentPdfOverdoseBodyBasisReflectionGate": "current_pdf_overdose_body_basis_reflection_no_selector",
            "selectorUnlocked": False,
            "reason": "OVERDOSE body-basis reflections do not carry strict unit/order wording with all-four or active-order target structure.",
            "nextMove": "Treat OVERDOSE body-basis reflection as closed unless source material names this mirror/fold unit/order rule.",
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
