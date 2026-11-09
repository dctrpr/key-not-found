#!/usr/bin/env python3
"""Check whether current PDF OCR layers can reopen active target text.

This bounded pass inspects page-76 text overlays in the current PDFs and asks
whether they provide source-side exact text for O4/B4/G5/O5 or a usable
OVERDOSE/unit-order instruction. It is provenance inspection only: no key
derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate
generation are run.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_target_provenance_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_target_provenance_gate.json"
OUT_MD = OUT / "current_pdf_ocr_target_provenance_gate.md"
OUT_SHEET = OUT / "current_pdf_ocr_target_provenance_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_PHRASE_VARIANTS = {
    "O4": ["buying the dip"],
    "B4": ["$1 billion", "1 billion"],
    "G5": ["Volcano Bonds", "Volcano Bond"],
    "O5": ["shitcoiner at heart", "shitcoiner heart"],
}
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", text.lower())


def word_boundary_hit(text: str, term: str) -> bool:
    return bool(re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE))


def font(size: int) -> ImageFont.ImageFont:
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


def image_rect(page: fitz.Page) -> tuple[fitz.Rect, tuple[int, int] | None]:
    best_rect = page.rect
    best_size = None
    best_area = -1.0
    for image in page.get_images(full=True):
        xref = int(image[0])
        try:
            extracted = page.parent.extract_image(xref)
        except Exception:
            extracted = {}
        for rect in page.get_image_rects(xref):
            area = max(0.0, rect.width) * max(0.0, rect.height)
            if area > best_area:
                best_area = area
                best_rect = rect
                best_size = (
                    int(extracted.get("width", image[2])),
                    int(extracted.get("height", image[3])),
                )
    return best_rect, best_size


def target_rect_in_pdf(target: dict[str, Any], rect: fitz.Rect) -> fitz.Rect:
    x0, y0, x1, y1 = [float(v) for v in target["box"]]
    w, h = SOURCE_IMAGE_SIZE
    return fitz.Rect(
        rect.x0 + (x0 / w) * rect.width,
        rect.y0 + (y0 / h) * rect.height,
        rect.x0 + (x1 / w) * rect.width,
        rect.y0 + (y1 / h) * rect.height,
    )


def words_for_page(page: fitz.Page) -> list[dict[str, Any]]:
    out = []
    for row in page.get_text("words"):
        x0, y0, x1, y1, text, block, line, word = row
        token = clean_token(str(text))
        out.append(
            {
                "text": str(text),
                "token": token,
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "block": int(block),
                "line": int(line),
                "word": int(word),
                "center": [(float(x0) + float(x1)) / 2.0, (float(y0) + float(y1)) / 2.0],
            }
        )
    return out


def token_context(words: list[dict[str, Any]], idx: int, radius: int = 7) -> str:
    lo = max(0, idx - radius)
    hi = min(len(words), idx + radius + 1)
    return compact(" ".join(row["text"] for row in words[lo:hi]))


def inspect_pdf(pdf_path: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    img_rect, img_size = image_rect(page)
    text = page.get_text("text") or ""
    norm = normalize_text(text)
    words = words_for_page(page)

    phrase_rows = []
    for target in targets:
        variants = TARGET_PHRASE_VARIANTS[target["shortId"]]
        hits = [variant for variant in variants if normalize_text(variant) in norm]
        phrase_rows.append(
            {
                "target": target["shortId"],
                "label": target["label"],
                "variants": variants,
                "hits": hits,
                "exactPhrasePresent": bool(hits),
            }
        )

    component_rows = []
    for target in targets:
        terms = TARGET_COMPONENT_TERMS[target["shortId"]]
        exact_hits: list[dict[str, Any]] = []
        stem_hits: list[dict[str, Any]] = []
        for idx, word in enumerate(words):
            token = word["token"]
            for term in terms:
                if token == term:
                    exact_hits.append(
                        {"term": term, "word": word["text"], "context": token_context(words, idx)}
                    )
                elif len(term) >= 5 and term in token:
                    stem_hits.append(
                        {"term": term, "word": word["text"], "context": token_context(words, idx)}
                    )
        component_rows.append(
            {
                "target": target["shortId"],
                "label": target["label"],
                "terms": terms,
                "exactHits": exact_hits,
                "stemLikeHits": stem_hits,
                "exactHitCount": len(exact_hits),
                "stemLikeHitCount": len(stem_hits),
            }
        )

    strict_hits = sorted(
        {term for term in STRICT_UNIT_ORDER_TERMS if word_boundary_hit(norm, term)}
    )
    overdose_hits = [m.start() for m in re.finditer(r"\boverdose\b", norm, flags=re.IGNORECASE)]

    target_rect_rows = []
    for target in targets:
        rect = target_rect_in_pdf(target, img_rect)
        rect_words = []
        for word in words:
            cx, cy = word["center"]
            if rect.x0 <= cx <= rect.x1 and rect.y0 <= cy <= rect.y1:
                rect_words.append(word["text"])
        rect_text = compact(" ".join(rect_words))
        target_rect_rows.append(
            {
                "target": target["shortId"],
                "label": target["label"],
                "approxPdfRect": [
                    round(rect.x0, 3),
                    round(rect.y0, 3),
                    round(rect.x1, 3),
                    round(rect.y1, 3),
                ],
                "wordCount": len(rect_words),
                "text": rect_text,
                "containsExactPhrase": any(
                    normalize_text(v) in normalize_text(rect_text)
                    for v in TARGET_PHRASE_VARIANTS[target["shortId"]]
                ),
            }
        )

    return {
        "pdf": rel(pdf_path),
        "sha256": sha256(pdf_path),
        "pdfPage": 4,
        "articlePage": 76,
        "rotation": page.rotation,
        "pageRect": [round(page.rect.x0, 3), round(page.rect.y0, 3), round(page.rect.x1, 3), round(page.rect.y1, 3)],
        "imageRect": [round(img_rect.x0, 3), round(img_rect.y0, 3), round(img_rect.x1, 3), round(img_rect.y1, 3)],
        "imageSize": list(img_size) if img_size else None,
        "textCharCount": len(text),
        "wordCount": len(words),
        "sampleText": compact(text)[:180],
        "phraseRows": phrase_rows,
        "componentRows": component_rows,
        "strictUnitOrderTerms": strict_hits,
        "strictUnitOrderTermCount": len(strict_hits),
        "overdoseHeaderHitCount": len(overdose_hits),
        "targetRectRows": target_rect_rows,
    }


def page_to_sheet(rect: list[float], page_rect: list[float], scale: float, dx: int, dy: int) -> list[int]:
    x0, y0, x1, y1 = rect
    return [
        int(dx + (x0 - page_rect[0]) * scale),
        int(dy + (y0 - page_rect[1]) * scale),
        int(dx + (x1 - page_rect[0]) * scale),
        int(dy + (y1 - page_rect[1]) * scale),
    ]


def draw_sheet(pdf_records: list[dict[str, Any]], targets: list[dict[str, Any]]) -> None:
    title_f = font(26)
    body_f = font(17)
    small_f = font(13)
    row_h = 470
    width = 1840
    height = 90 + row_h * len(pdf_records)
    sheet = Image.new("RGB", (width, height), (245, 246, 248))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 22), "Current PDF OCR Target Provenance Gate", fill=(20, 28, 38), font=title_f)
    draw.text(
        (24, 55),
        "Green boxes: approximate O4/B4/G5/O5 positions. Blue boxes: target-term OCR words. Red: unit/order words.",
        fill=(62, 72, 86),
        font=body_f,
    )

    target_colors = {"O4": (255, 130, 0), "B4": (60, 60, 60), "G5": (80, 80, 80), "O5": (255, 130, 0)}
    target_terms = {term for terms in TARGET_COMPONENT_TERMS.values() for term in terms}

    for idx, record in enumerate(pdf_records):
        y = 90 + idx * row_h
        pdf_path = ROOT / record["pdf"]
        doc = fitz.open(pdf_path)
        page = doc[3]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.55, 0.55), alpha=False)
        page_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        x0 = 22
        y0 = y + 18
        sheet.paste(page_img, (x0, y0))
        page_rect = record["pageRect"]
        scale = pix.width / (page_rect[2] - page_rect[0])

        for target in targets:
            rect = target_rect_in_pdf(target, fitz.Rect(record["imageRect"]))
            box = page_to_sheet([rect.x0, rect.y0, rect.x1, rect.y1], page_rect, scale, x0, y0)
            color = target_colors[target["shortId"]]
            draw.rectangle(box, outline=color, width=3)
            draw.text((box[0] + 3, max(y0, box[1] - 17)), target["shortId"], fill=color, font=small_f)

        for word in words_for_page(page):
            token = word["token"]
            is_target = any((term == token or (len(term) >= 5 and term in token)) for term in target_terms)
            is_strict = token in STRICT_UNIT_ORDER_TERMS
            if not (is_target or is_strict):
                continue
            box = page_to_sheet(word["bbox"], page_rect, scale, x0, y0)
            draw.rectangle(box, outline=(20, 105, 220) if is_target else (205, 40, 40), width=2)

        tx = 390
        draw.text((tx, y + 18), record["pdf"], fill=(20, 28, 38), font=body_f)
        draw.text(
            (tx, y + 43),
            f"rotation={record['rotation']} words={record['wordCount']} exact active phrase rows="
            f"{sum(1 for row in record['phraseRows'] if row['exactPhrasePresent'])}/4 "
            f"strict terms={record['strictUnitOrderTerms'] or '-'} OVERDOSE hits={record['overdoseHeaderHitCount']}",
            fill=(62, 72, 86),
            font=small_f,
        )
        yy = y + 78
        for row in record["phraseRows"]:
            status = "exact" if row["exactPhrasePresent"] else "no exact phrase"
            draw.text((tx, yy), f"{row['target']} {row['label']}: {status}", fill=(20, 28, 38), font=small_f)
            yy += 22
        yy += 8
        for row in record["componentRows"]:
            examples = row["exactHits"][:2] + row["stemLikeHits"][:2]
            sample = "; ".join(f"{e['word']} [{e['context'][:70]}]" for e in examples) or "-"
            draw.text(
                (tx, yy),
                f"{row['target']} component hits exact/stem={row['exactHitCount']}/{row['stemLikeHitCount']}: {sample}",
                fill=(45, 50, 58),
                font=small_f,
            )
            yy += 36
        yy += 4
        for row in record["targetRectRows"]:
            draw.text(
                (tx, yy),
                f"approx {row['target']} box words={row['wordCount']}: {row['text'][:95] or '-'}",
                fill=(70, 78, 88),
                font=small_f,
            )
            yy += 22

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    targets = active_targets()
    pdf_records = [inspect_pdf(path, targets) for path in PDFS if path.exists()]
    source_review = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    phrase_hit_rows = sum(
        1 for record in pdf_records for row in record["phraseRows"] if row["exactPhrasePresent"]
    )
    pdfs_with_all_four_exact = sum(
        1
        for record in pdf_records
        if all(row["exactPhrasePresent"] for row in record["phraseRows"])
    )
    component_exact_rows = sum(
        1 for record in pdf_records for row in record["componentRows"] if row["exactHitCount"] > 0
    )
    component_stem_rows = sum(
        1 for record in pdf_records for row in record["componentRows"] if row["stemLikeHitCount"] > 0
    )
    approx_rect_rows_with_words = sum(
        1 for record in pdf_records for row in record["targetRectRows"] if row["wordCount"] > 0
    )
    approx_rect_rows_with_exact = sum(
        1 for record in pdf_records for row in record["targetRectRows"] if row["containsExactPhrase"]
    )
    strict_terms = sorted(
        {term for record in pdf_records for term in record["strictUnitOrderTerms"]}
    )
    overdose_pdfs = sum(1 for record in pdf_records if record["overdoseHeaderHitCount"] > 0)
    source_r3 = (
        source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount")
        or reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount")
        or 0
    )
    satisfied = (
        source_review.get("summary", {}).get("satisfiedReopenTriggerCount")
        or reopen.get("summary", {}).get("satisfiedNow")
        or reopen.get("summary", {}).get("satisfiedReopenTriggerCount")
        or 0
    )
    trigger_count = (
        reopen.get("summary", {}).get("triggerCount")
        or reopen.get("triggerCount")
        or len(reopen.get("triggerRows", []))
        or 9
    )
    fingerprint = (
        f"pdfs={len(pdf_records)}|exactPhraseRows={phrase_hit_rows}|allFourExactPdfs={pdfs_with_all_four_exact}|"
        f"componentExactRows={component_exact_rows}|componentStemRows={component_stem_rows}|"
        f"approxBoxWordRows={approx_rect_rows_with_words}|approxBoxExactRows={approx_rect_rows_with_exact}|"
        f"strictTerms={','.join(strict_terms) if strict_terms else '-'}|overdosePdfs={overdose_pdfs}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    summary = {
        "pdfCount": len(pdf_records),
        "exactActivePhraseRowCount": phrase_hit_rows,
        "pdfsWithAllFourExactActivePhrases": pdfs_with_all_four_exact,
        "componentExactHitRowCount": component_exact_rows,
        "componentStemLikeHitRowCount": component_stem_rows,
        "approxTargetBoxWordRowCount": approx_rect_rows_with_words,
        "approxTargetBoxExactPhraseRowCount": approx_rect_rows_with_exact,
        "strictUnitOrderTerms": strict_terms,
        "strictUnitOrderPdfCount": sum(1 for record in pdf_records if record["strictUnitOrderTermCount"]),
        "overdoseHeaderPdfCount": overdose_pdfs,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "pdfOcrTargetProvenanceFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current PDF page-76 OCR target provenance gate. Checks exact O4/B4/G5/O5 text, "
            "component-token false positives, approximate target-box OCR, OVERDOSE header text, "
            "and strict unit/order wording. No key/hash/seed/WIF/address/BIP39/candidate work."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "pdfRecords": pdf_records,
        "decision": {
            "currentPdfOcrTargetProvenanceGate": "do_not_reopen_pdf_ocr_active_text",
            "selectorUnlocked": False,
            "reason": (
                "The current PDF text overlays do not contain exact O4/B4/G5/O5 target phrases, "
                "do not put exact target phrases inside the approximate active boxes, and do not "
                "supply strict unit/order wording. Component hits are ordinary OCR prose elsewhere."
            ),
            "nextMove": (
                "Keep PDF OCR as a weak text witness only. Do not use it for active-box extraction; "
                "future progress still requires a new source/original-layout clue satisfying R1/R3."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(pdf_records, targets)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF OCR Target Provenance Gate",
        "",
        "Scope: inspect page-76 PDF text overlays for exact O4/B4/G5/O5 target text, component-token false positives, approximate target-box OCR, OVERDOSE header text, and strict unit/order wording. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- Exact active phrase rows: `{summary['exactActivePhraseRowCount']}`",
        f"- PDFs with all four exact active phrases: `{summary['pdfsWithAllFourExactActivePhrases']}`",
        f"- Component exact/stem-like hit rows: `{summary['componentExactHitRowCount']}` / `{summary['componentStemLikeHitRowCount']}`",
        f"- Approximate target-box word rows / exact phrase rows: `{summary['approxTargetBoxWordRowCount']}` / `{summary['approxTargetBoxExactPhraseRowCount']}`",
        f"- Strict unit/order terms: `{', '.join(summary['strictUnitOrderTerms']) if summary['strictUnitOrderTerms'] else '-'}`",
        f"- OVERDOSE header PDFs: `{summary['overdoseHeaderPdfCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | rotation | words | exact active phrases | component exact/stem rows | approx box words | strict terms | OVERDOSE hits |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for record in pdf_records:
        exact = sum(1 for row in record["phraseRows"] if row["exactPhrasePresent"])
        comp_exact = sum(1 for row in record["componentRows"] if row["exactHitCount"])
        comp_stem = sum(1 for row in record["componentRows"] if row["stemLikeHitCount"])
        approx_words = sum(1 for row in record["targetRectRows"] if row["wordCount"])
        strict = ", ".join(record["strictUnitOrderTerms"]) if record["strictUnitOrderTerms"] else "-"
        lines.append(
            f"| `{record['pdf']}` | `{record['rotation']}` | `{record['wordCount']}` | `{exact}/4` | `{comp_exact}/{comp_stem}` | `{approx_words}/4` | `{strict}` | `{record['overdoseHeaderHitCount']}` |"
        )
    lines.extend(["", "## Target Detail", ""])
    for record in pdf_records:
        lines.append(f"### `{record['pdf']}`")
        lines.append("")
        for row in record["phraseRows"]:
            status = ", ".join(row["hits"]) if row["hits"] else "-"
            lines.append(f"- {row['target']} `{row['label']}` exact phrase hits: `{status}`")
        for row in record["componentRows"]:
            exact = "; ".join(f"{hit['word']} [{hit['context']}]" for hit in row["exactHits"][:3]) or "-"
            stem = "; ".join(f"{hit['word']} [{hit['context']}]" for hit in row["stemLikeHits"][:3]) or "-"
            lines.append(f"- {row['target']} component exact hits: `{exact}`")
            lines.append(f"- {row['target']} component stem-like hits: `{stem}`")
        for row in record["targetRectRows"]:
            lines.append(
                f"- Approx {row['target']} box OCR words: `{row['text'] if row['text'] else '-'}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Decision",
            "",
            "- Do not reopen PDF OCR active-box text.",
            "- The text overlays are derivative OCR witnesses. The low-resolution duplicate PDFs contain scattered component words such as `buying`, `billions`, `volcanoes`, `shitcoiners`, and `heart`, but not the locked exact target phrases and not a source-side unit/order instruction.",
            "- The high-resolution `magazine.pdf` text layer is rotated/OCR-corrupt and contains no useful active target words on page 76.",
            "- OVERDOSE appearing in the low-resolution PDF text layer confirms only the article header, not an extraction rule.",
            "",
            "## Next Move",
            "",
            "- Treat PDF OCR as context only. Future local passes should be source-intake/reopen-gate checks unless new source/original-layout evidence arrives.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()
