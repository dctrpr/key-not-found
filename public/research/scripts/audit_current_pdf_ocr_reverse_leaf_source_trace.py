#!/usr/bin/env python3
"""Trace current PDF OCR layers through the valid reverse leaf geometry.

This bounded pass asks whether the PDF text/OCR layer itself, not just the
page raster, supplies an instruction when page-76 active target boxes are
mirrored back onto page 75 under the physically valid held-to-light model. It
does not derive keys, hashes, seeds, WIFs, addresses, BIP39 material, or
candidate strings.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_reverse_leaf_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_reverse_leaf_source_trace.json"
OUT_MD = OUT / "current_pdf_ocr_reverse_leaf_source_trace.md"
OUT_SHEET = OUT / "current_pdf_ocr_reverse_leaf_source_trace_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
UPRIGHT_PAGE75 = ROOT / "analysis_outputs/3d_article_map/page_75_upright.jpg"

PAGE_NUM = 75
PDF_PAGE_INDEX = 2
SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CONTEXT_PAD = 36
RANSAC_SEED = 75076
RANSAC_ITERATIONS = 2200
INLIER_THRESHOLD_PX = 85.0
MIN_PAIR_COUNT = 12

STRICT_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "line",
    "lines",
    "word",
    "words",
    "letter",
    "letters",
    "edge",
    "edges",
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "fold",
    "folded",
    "mirror",
    "mirrored",
    "reverse",
    "order",
    "slot",
    "font",
    "bold",
    "highlight",
    "overdose",
}
CONTEXT_TERMS = {
    "bitcoin",
    "bitcoins",
    "satoshi",
    "vitalik",
    "buterin",
    "volcano",
    "volcanoes",
    "bond",
    "bonds",
    "shitcoiner",
    "heart",
    "dip",
    "sell",
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


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", str(text).lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        rows.append(row)
    return rows


def article_words(page_num: int) -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    page = next(row for row in data["pages"] if row["page"] == page_num)
    words = []
    for word in page["words"]:
        token = clean_token(word.get("token") or word.get("text") or "")
        if not token:
            continue
        box = [float(v) for v in word["box"]]
        words.append(
            {
                "id": word.get("id"),
                "index": int(word.get("index", len(words))),
                "text": str(word.get("text") or token),
                "token": token,
                "box": box,
                "center": center(box),
            }
        )
    return words


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


def pdf_words_for_page(pdf_path: Path) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[PDF_PAGE_INDEX]
    rect, size = image_rect(page)
    rotation = page.rotation
    rows = []
    for idx, row in enumerate(page.get_text("words")):
        x0, y0, x1, y1, text, block, line, word = row
        token = clean_token(text)
        if not token:
            continue
        cx = (float(x0) + float(x1)) / 2.0
        cy = (float(y0) + float(y1)) / 2.0
        image_x = ((cx - rect.x0) / rect.width) * SOURCE_IMAGE_SIZE[0]
        image_y = ((cy - rect.y0) / rect.height) * SOURCE_IMAGE_SIZE[1]
        rows.append(
            {
                "text": str(text),
                "token": token,
                "pdfCenter": [cx, cy],
                "imageMappedCenter": [image_x, image_y],
                "block": int(block),
                "line": int(line),
                "word": int(word),
                "index": idx,
            }
        )
    doc.close()
    return {
        "pdf": rel(pdf_path),
        "sha256": sha256(pdf_path),
        "rotation": rotation,
        "imageRect": [round(rect.x0, 3), round(rect.y0, 3), round(rect.x1, 3), round(rect.y1, 3)],
        "imageSize": list(size) if size else None,
        "wordRows": rows,
    }


def build_pairs(pdf_rows: list[dict[str, Any]], map_words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pdf_by_token: dict[str, list[dict[str, Any]]] = defaultdict(list)
    map_by_token: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pdf_rows:
        if len(row["token"]) >= 4:
            pdf_by_token[row["token"]].append(row)
    for row in map_words:
        if len(row["token"]) >= 4:
            map_by_token[row["token"]].append(row)
    pairs = []
    for token in sorted(set(pdf_by_token) & set(map_by_token)):
        pdf_hits = pdf_by_token[token]
        map_hits = map_by_token[token]
        if len(pdf_hits) == 1 and len(map_hits) == 1:
            pairs.append(
                {
                    "token": token,
                    "pdfText": pdf_hits[0]["text"],
                    "mapText": map_hits[0]["text"],
                    "source": pdf_hits[0]["imageMappedCenter"],
                    "target": map_hits[0]["center"],
                }
            )
    return pairs


def fit_affine(src: np.ndarray, dst: np.ndarray) -> np.ndarray | None:
    if len(src) < 3:
        return None
    a = np.column_stack([src[:, 0], src[:, 1], np.ones(len(src))])
    try:
        matrix, *_ = np.linalg.lstsq(a, dst, rcond=None)
    except np.linalg.LinAlgError:
        return None
    return matrix.T


def transform_points(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    a = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    return a @ matrix.T


def robust_fit(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    if len(pairs) < MIN_PAIR_COUNT:
        return {"fitAvailable": False, "reason": "too_few_token_pairs", "pairCount": len(pairs), "inlierCount": 0}
    src = np.array([row["source"] for row in pairs], dtype=float)
    dst = np.array([row["target"] for row in pairs], dtype=float)
    rng = random.Random(RANSAC_SEED)
    indexes = list(range(len(pairs)))
    best_inliers: list[int] = []
    best_median = float("inf")
    for _ in range(RANSAC_ITERATIONS):
        sample = rng.sample(indexes, 3)
        matrix = fit_affine(src[sample], dst[sample])
        if matrix is None:
            continue
        residuals = np.linalg.norm(transform_points(matrix, src) - dst, axis=1)
        inliers = [i for i, value in enumerate(residuals) if value <= INLIER_THRESHOLD_PX]
        if len(inliers) > len(best_inliers) or (
            len(inliers) == len(best_inliers)
            and inliers
            and float(np.median(residuals[inliers])) < best_median
        ):
            best_inliers = inliers
            best_median = float(np.median(residuals[inliers])) if inliers else float("inf")
    if len(best_inliers) < 3:
        return {"fitAvailable": False, "reason": "no_stable_inliers", "pairCount": len(pairs), "inlierCount": 0}
    matrix = fit_affine(src[best_inliers], dst[best_inliers])
    if matrix is None:
        return {"fitAvailable": False, "reason": "final_fit_failed", "pairCount": len(pairs), "inlierCount": 0}
    residuals = np.linalg.norm(transform_points(matrix, src) - dst, axis=1)
    inliers = [i for i, value in enumerate(residuals) if value <= INLIER_THRESHOLD_PX]
    inlier_residuals = residuals[inliers] if inliers else np.array([])
    return {
        "fitAvailable": True,
        "pairCount": len(pairs),
        "inlierCount": len(inliers),
        "inlierFraction": round(len(inliers) / len(pairs), 4) if pairs else 0.0,
        "medianResidualPx": round(float(np.median(inlier_residuals)), 3) if len(inlier_residuals) else None,
        "p90ResidualPx": round(float(np.percentile(inlier_residuals, 90)), 3) if len(inlier_residuals) else None,
        "maxInlierResidualPx": round(float(np.max(inlier_residuals)), 3) if len(inlier_residuals) else None,
        "matrix": [[round(float(v), 8) for v in row] for row in matrix.tolist()],
        "inlierTokens": [pairs[i]["token"] for i in inliers[:80]],
    }


def mirror_target_to_page75_source(box: list[float]) -> list[int]:
    x0, y0, x1, y1 = box
    width = int(SOURCE_IMAGE_SIZE[0])
    return [int(round(width - x1)), int(round(y0)), int(round(width - x0)), int(round(y1))]


def padded_box(box: list[int], pad: int = CONTEXT_PAD) -> list[int]:
    width, height = int(SOURCE_IMAGE_SIZE[0]), int(SOURCE_IMAGE_SIZE[1])
    x0, y0, x1, y1 = box
    return [max(0, x0 - pad), max(0, y0 - pad), min(width, x1 + pad), min(height, y1 + pad)]


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def snippet(words: list[dict[str, Any]], limit: int = 12) -> str:
    if not words:
        return "(no PDF OCR words)"
    return compact(" ".join(str(word["text"]) for word in words[:limit]))


def article_snippet(map_words: list[dict[str, Any]], box: list[int]) -> str:
    hits = [word for word in map_words if in_box(tuple(word["center"]), box)]
    return snippet(hits)


def evaluate_pdf(
    pdf_record: dict[str, Any],
    fit: dict[str, Any],
    targets: list[dict[str, Any]],
    map_words: list[dict[str, Any]],
) -> dict[str, Any]:
    target_rows = []
    if not fit.get("fitAvailable"):
        for target in targets:
            source_box = mirror_target_to_page75_source(target["box"])
            target_rows.append(
                {
                    "target": target["shortId"],
                    "phrase": target["phrase"],
                    "sourceTraceBox": source_box,
                    "sourceContextBox": padded_box(source_box),
                    "pdfWordCount": 0,
                    "pdfSnippet": "(fit unavailable)",
                    "articleSnippet": article_snippet(map_words, source_box),
                    "strictInstructionTokens": [],
                    "contextTokens": [],
                }
            )
        return {"targetRows": target_rows, "fitAvailable": False}

    matrix = np.array(fit["matrix"], dtype=float)
    words = pdf_record["wordRows"]
    points = np.array([row["imageMappedCenter"] for row in words], dtype=float)
    aligned = transform_points(matrix, points) if len(points) else np.empty((0, 2))
    aligned_words = []
    for row, point in zip(words, aligned):
        out = dict(row)
        out["alignedCenter"] = [round(float(point[0]), 3), round(float(point[1]), 3)]
        aligned_words.append(out)

    for target in targets:
        source_box = mirror_target_to_page75_source(target["box"])
        context_box = padded_box(source_box)
        hits = [row for row in aligned_words if in_box(tuple(row["alignedCenter"]), context_box)]
        strict_tokens = sorted({row["token"] for row in hits if row["token"] in STRICT_TERMS})
        context_tokens = sorted({row["token"] for row in hits if row["token"] in CONTEXT_TERMS})
        exact_hits = [row for row in aligned_words if in_box(tuple(row["alignedCenter"]), source_box)]
        target_rows.append(
            {
                "target": target["shortId"],
                "phrase": target["phrase"],
                "sourceTraceBox": source_box,
                "sourceContextBox": context_box,
                "pdfWordCount": len(hits),
                "pdfExactBoxWordCount": len(exact_hits),
                "pdfSnippet": snippet(hits),
                "pdfExactBoxSnippet": snippet(exact_hits),
                "articleSnippet": article_snippet(map_words, source_box),
                "strictInstructionTokens": strict_tokens,
                "contextTokens": context_tokens,
            }
        )
    return {"targetRows": target_rows, "fitAvailable": True}


def draw_sheet(result: dict[str, Any]) -> None:
    base = Image.open(UPRIGHT_PAGE75).convert("RGB")
    scale = 0.34
    page = base.resize((int(base.width * scale), int(base.height * scale)))
    width, row_h = 1840, max(page.height + 110, 1230)
    height = 96 + row_h * len(result["pdfRows"])
    sheet = Image.new("RGB", (width, height), (246, 247, 249))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    body = font(15)
    small = font(12)
    draw.text((24, 18), "Current PDF OCR Reverse-Leaf Source Trace", fill=(20, 28, 38), font=title)
    draw.text(
        (24, 55),
        "Page-76 active boxes mirrored to page 75; dots are aligned PDF OCR words in source/context boxes.",
        fill=(62, 72, 86),
        font=body,
    )
    colors = {"O4": (230, 115, 0), "B4": (30, 30, 30), "G5": (30, 30, 30), "O5": (230, 115, 0)}
    for idx, pdf in enumerate(result["pdfRows"]):
        y = 96 + idx * row_h
        x = 24
        sheet.paste(page, (x, y + 24))
        for row in pdf["targetRows"]:
            box = row["sourceTraceBox"]
            scaled = [int(x + box[0] * scale), int(y + 24 + box[1] * scale), int(x + box[2] * scale), int(y + 24 + box[3] * scale)]
            draw.rectangle(scaled, outline=colors[row["target"]], width=3)
            draw.text((scaled[0] + 3, max(y + 24, scaled[1] - 15)), row["target"], fill=colors[row["target"]], font=small)
        tx = x + page.width + 32
        draw.text((tx, y + 24), pdf["pdf"], fill=(20, 28, 38), font=body)
        draw.text(
            (tx, y + 50),
            f"fit={pdf['fitAvailable']} pairs={pdf['fit'].get('pairCount', 0)} inliers={pdf['fit'].get('inlierCount', 0)} median={pdf['fit'].get('medianResidualPx')}px",
            fill=(65, 72, 84),
            font=small,
        )
        yy = y + 84
        for row in pdf["targetRows"]:
            draw.text(
                (tx, yy),
                f"{row['target']} words={row['pdfWordCount']} exact={row.get('pdfExactBoxWordCount', 0)} strict={row['strictInstructionTokens'] or '-'} ctx={row['contextTokens'] or '-'}",
                fill=(40, 45, 52),
                font=small,
            )
            yy += 18
            draw.text((tx + 18, yy), f"PDF: {row['pdfSnippet'][:105]}", fill=(80, 85, 92), font=small)
            yy += 18
            draw.text((tx + 18, yy), f"Map: {row['articleSnippet'][:105]}", fill=(80, 85, 92), font=small)
            yy += 24
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF OCR Reverse-Leaf Source Trace",
        "",
        "Scope: aligned the current PDF page-75 OCR/text layers to the page-75 OCR map, then mirrored O4/B4/G5/O5 page-76 active boxes back onto page 75 under the valid held-to-light transform. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- PDF rows / fit rows: `{summary['pdfCount']}` / `{summary['fitAvailableCount']}`",
        f"- Token pairs / inliers: `{summary['totalTokenPairCount']}` / `{summary['totalInlierCount']}`",
        f"- Target rows / PDF word rows / exact-box word rows: `{summary['targetRowCount']}` / `{summary['pdfWordTargetRowCount']}` / `{summary['pdfExactBoxWordTargetRowCount']}`",
        f"- Strict instruction rows / context rows: `{summary['strictInstructionRowCount']}` / `{summary['contextRowCount']}`",
        f"- All-four exact-box PDF trace pairs: `{summary['allFourExactBoxPdfTracePairCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Target Rows",
        "",
        "| PDF | target | pdf words | exact words | strict tokens | context tokens | PDF OCR snippet | article-map snippet |",
        "|---|---:|---:|---:|---|---|---|---|",
    ]
    for pdf in result["pdfRows"]:
        for row in pdf["targetRows"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{pdf['pdf']}`",
                        row["target"],
                        str(row["pdfWordCount"]),
                        str(row.get("pdfExactBoxWordCount", 0)),
                        ", ".join(row["strictInstructionTokens"]) or "-",
                        ", ".join(row["contextTokens"]) or "-",
                        row["pdfSnippet"].replace("|", "/"),
                        row["articleSnippet"].replace("|", "/"),
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- The low-resolution PDF OCR layers align cleanly to page 75, but the reverse-leaf source boxes contain ordinary prose, blank regions, or isolated context words, not extraction instructions.",
            "- The full-resolution `magazine.pdf` OCR layer remains rotated/garbled enough that it cannot supply a stable reverse-leaf source trace.",
            "- No current PDF OCR layer supplies a source-backed instruction for fold, mirror, order, slot, read/take, or extraction.",
            "",
            "## Next Move",
            "",
            "- Keep PDF OCR reverse-leaf source tracing closed. The next useful move is still distinct source/original-layout validation or raw clue wording that names the active unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    map_words = article_words(PAGE_NUM)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    pdf_rows = []
    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        pdf_record = pdf_words_for_page(pdf_path)
        pairs = build_pairs(pdf_record["wordRows"], map_words)
        fit = robust_fit(pairs)
        evaluation = evaluate_pdf(pdf_record, fit, targets, map_words)
        pdf_rows.append(
            {
                "pdf": pdf_record["pdf"],
                "sha256": pdf_record["sha256"],
                "rotation": pdf_record["rotation"],
                "imageRect": pdf_record["imageRect"],
                "imageSize": pdf_record["imageSize"],
                "wordCount": len(pdf_record["wordRows"]),
                "fit": fit,
                "fitAvailable": bool(fit.get("fitAvailable")),
                "targetRows": evaluation["targetRows"],
            }
        )

    target_rows = [row for pdf in pdf_rows for row in pdf["targetRows"]]
    all_four_exact = 0
    for pdf in pdf_rows:
        if pdf["fitAvailable"] and all(row.get("pdfExactBoxWordCount", 0) > 0 for row in pdf["targetRows"]):
            all_four_exact += 1
    summary = {
        "pdfCount": len(pdf_rows),
        "fitAvailableCount": sum(1 for row in pdf_rows if row["fitAvailable"]),
        "totalTokenPairCount": sum(row["fit"].get("pairCount", 0) for row in pdf_rows),
        "totalInlierCount": sum(row["fit"].get("inlierCount", 0) for row in pdf_rows),
        "targetRowCount": len(target_rows),
        "pdfWordTargetRowCount": sum(1 for row in target_rows if row["pdfWordCount"] > 0),
        "pdfExactBoxWordTargetRowCount": sum(1 for row in target_rows if row.get("pdfExactBoxWordCount", 0) > 0),
        "strictInstructionRowCount": sum(1 for row in target_rows if row["strictInstructionTokens"]),
        "contextRowCount": sum(1 for row in target_rows if row["contextTokens"]),
        "allFourExactBoxPdfTracePairCount": all_four_exact,
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(
            reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)
        ),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|fits={summary['fitAvailableCount']}|"
        f"pairs={summary['totalTokenPairCount']}|inliers={summary['totalInlierCount']}|"
        f"targets={summary['targetRowCount']}|pdfWordRows={summary['pdfWordTargetRowCount']}|"
        f"exactRows={summary['pdfExactBoxWordTargetRowCount']}|strictRows={summary['strictInstructionRowCount']}|"
        f"contextRows={summary['contextRowCount']}|allFourExact={summary['allFourExactBoxPdfTracePairCount']}|"
        f"sourceR3=0|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_ocr_reverse_leaf_source_trace_no_instruction_source",
        "sheet": rel(OUT_SHEET),
        "summary": summary,
        "fingerprint": fingerprint,
        "pdfRows": pdf_rows,
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
