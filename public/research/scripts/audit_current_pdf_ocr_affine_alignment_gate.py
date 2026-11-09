#!/usr/bin/env python3
"""Test whether PDF OCR geometry can be affinely realigned to page 76.

The current PDFs contain page images plus OCR/text overlays. The previous pass
checked those overlays directly. This pass asks a narrower geometry question:
if the OCR layer is misregistered, can an affine fit to the high-resolution
page-76 word map move OCR words back onto O4/B4/G5/O5 or reveal a source-side
unit/order instruction? It does not derive keys, hashes, seed/WIF/address
checks, BIP39 checks, or broad candidates.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ocr_affine_alignment_gate.json"
OUT_MD = OUT / "current_pdf_ocr_affine_alignment_gate.md"
OUT_SHEET = OUT / "current_pdf_ocr_affine_alignment_gate_sheet.jpg"

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
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
SOURCE_IMAGE_SIZE = (2544.0, 3264.0)
RANSAC_SEED = 24076
RANSAC_ITERATIONS = 2000
INLIER_THRESHOLD_PX = 85.0
MIN_PAIR_COUNT = 12

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


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", text.lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def box_distance(point: tuple[float, float], box: list[float]) -> float:
    px, py = point
    dx = max(box[0] - px, 0.0, px - box[2])
    dy = max(box[1] - py, 0.0, py - box[3])
    return float((dx * dx + dy * dy) ** 0.5)


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        rows.append(row)
    return rows


def article_words() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    page = next(row for row in data["pages"] if row["page"] == 76)
    words = []
    for word in page["words"]:
        token = clean_token(str(word.get("token") or word.get("text") or ""))
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


def pdf_words(pdf_path: Path) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    page = doc[3]
    rect, size = image_rect(page)
    rows = []
    for row in page.get_text("words"):
        x0, y0, x1, y1, text, block, line, word = row
        token = clean_token(str(text))
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
            }
        )
    return {
        "pdf": rel(pdf_path),
        "sha256": sha256(pdf_path),
        "rotation": page.rotation,
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
                    "matchType": "unique",
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
        return {
            "fitAvailable": False,
            "reason": "too_few_token_pairs",
            "pairCount": len(pairs),
            "inlierCount": 0,
        }
    src = np.array([row["source"] for row in pairs], dtype=float)
    dst = np.array([row["target"] for row in pairs], dtype=float)
    rng = random.Random(RANSAC_SEED)
    best_inliers: list[int] = []
    best_median = float("inf")
    indexes = list(range(len(pairs)))
    for _ in range(RANSAC_ITERATIONS):
        sample = rng.sample(indexes, 3)
        matrix = fit_affine(src[sample], dst[sample])
        if matrix is None:
            continue
        pred = transform_points(matrix, src)
        residuals = np.linalg.norm(pred - dst, axis=1)
        inliers = [i for i, value in enumerate(residuals) if value <= INLIER_THRESHOLD_PX]
        if len(inliers) > len(best_inliers) or (
            len(inliers) == len(best_inliers)
            and len(inliers) > 0
            and float(np.median(residuals[inliers])) < best_median
        ):
            best_inliers = inliers
            best_median = float(np.median(residuals[inliers])) if inliers else float("inf")

    if len(best_inliers) < 3:
        return {
            "fitAvailable": False,
            "reason": "no_stable_inliers",
            "pairCount": len(pairs),
            "inlierCount": 0,
        }
    matrix = fit_affine(src[best_inliers], dst[best_inliers])
    pred = transform_points(matrix, src)
    residuals = np.linalg.norm(pred - dst, axis=1)
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


def evaluate_targets(
    pdf_record: dict[str, Any],
    fit: dict[str, Any],
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    if not fit.get("fitAvailable"):
        return {
            "targetRows": [],
            "componentRows": [],
            "strictInstructionRows": [],
            "targetWordHitRowCount": 0,
            "targetExactComponentRowCount": 0,
            "targetStrictInstructionRowCount": 0,
        }
    matrix = np.array(fit["matrix"], dtype=float)
    words = pdf_record["wordRows"]
    points = np.array([row["imageMappedCenter"] for row in words], dtype=float)
    aligned = transform_points(matrix, points) if len(points) else np.empty((0, 2))
    aligned_words = []
    for row, point in zip(words, aligned):
        out = dict(row)
        out["alignedCenter"] = [round(float(point[0]), 3), round(float(point[1]), 3)]
        aligned_words.append(out)

    target_rows = []
    for target in targets:
        hits = [row for row in aligned_words if in_box(tuple(row["alignedCenter"]), target["box"])]
        hit_text = compact(" ".join(row["text"] for row in hits))
        terms = TARGET_COMPONENT_TERMS[target["shortId"]]
        component_hits = [
            row
            for row in hits
            if any(row["token"] == term or (len(term) >= 5 and term in row["token"]) for term in terms)
        ]
        strict_hits = [row for row in hits if row["token"] in STRICT_UNIT_ORDER_TERMS]
        target_rows.append(
            {
                "target": target["shortId"],
                "label": target["label"],
                "alignedWordCount": len(hits),
                "alignedText": hit_text,
                "componentHitWords": [row["text"] for row in component_hits],
                "strictInstructionWords": [row["text"] for row in strict_hits],
            }
        )

    component_rows = []
    for target in targets:
        for term in TARGET_COMPONENT_TERMS[target["shortId"]]:
            candidates = [
                row
                for row in aligned_words
                if row["token"] == term or (len(term) >= 5 and term in row["token"])
            ]
            ranked = sorted(
                candidates,
                key=lambda row: box_distance(tuple(row["alignedCenter"]), target["box"]),
            )
            if ranked:
                best = ranked[0]
                component_rows.append(
                    {
                        "target": target["shortId"],
                        "term": term,
                        "word": best["text"],
                        "alignedCenter": best["alignedCenter"],
                        "distanceToTargetBoxPx": round(box_distance(tuple(best["alignedCenter"]), target["box"]), 3),
                        "insideTarget": in_box(tuple(best["alignedCenter"]), target["box"]),
                    }
                )

    strict_rows = [
        {
            "word": row["text"],
            "token": row["token"],
            "alignedCenter": row["alignedCenter"],
            "nearestTarget": min(
                targets,
                key=lambda target: box_distance(tuple(row["alignedCenter"]), target["box"]),
            )["shortId"],
            "nearestTargetDistancePx": round(
                min(box_distance(tuple(row["alignedCenter"]), target["box"]) for target in targets),
                3,
            ),
        }
        for row in aligned_words
        if row["token"] in STRICT_UNIT_ORDER_TERMS
    ]

    return {
        "targetRows": target_rows,
        "componentRows": component_rows,
        "strictInstructionRows": strict_rows,
        "targetWordHitRowCount": sum(1 for row in target_rows if row["alignedWordCount"] > 0),
        "targetExactComponentRowCount": sum(1 for row in target_rows if row["componentHitWords"]),
        "targetStrictInstructionRowCount": sum(1 for row in target_rows if row["strictInstructionWords"]),
    }


def draw_sheet(records: list[dict[str, Any]], targets: list[dict[str, Any]]) -> None:
    base = Image.open(UPRIGHT_PAGE).convert("RGB")
    scale = 0.35
    page = base.resize((int(base.width * scale), int(base.height * scale)))
    title_f = font(26)
    body_f = font(16)
    small_f = font(12)
    width = 1840
    row_h = max(page.height + 120, 1280)
    height = 90 + row_h * len(records)
    sheet = Image.new("RGB", (width, height), (245, 246, 248))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 22), "Current PDF OCR Affine Alignment Gate", fill=(20, 28, 38), font=title_f)
    draw.text(
        (24, 55),
        "OCR words transformed onto the high-res page-76 map. Green boxes are active targets; blue labels are target components.",
        fill=(62, 72, 86),
        font=body_f,
    )
    target_colors = {"O4": (255, 130, 0), "B4": (50, 50, 50), "G5": (50, 50, 50), "O5": (255, 130, 0)}
    component_terms = {term for terms in TARGET_COMPONENT_TERMS.values() for term in terms}

    for idx, record in enumerate(records):
        y = 90 + idx * row_h
        x = 22
        sheet.paste(page, (x, y + 24))
        for target in targets:
            box = [int(x + target["box"][0] * scale), int(y + 24 + target["box"][1] * scale), int(x + target["box"][2] * scale), int(y + 24 + target["box"][3] * scale)]
            color = target_colors[target["shortId"]]
            draw.rectangle(box, outline=color, width=3)
            draw.text((box[0] + 3, max(y + 24, box[1] - 15)), target["shortId"], fill=color, font=small_f)

        fit = record["fit"]
        if fit.get("fitAvailable"):
            matrix = np.array(fit["matrix"], dtype=float)
            points = np.array([row["imageMappedCenter"] for row in record["pdfRecord"]["wordRows"]], dtype=float)
            aligned = transform_points(matrix, points) if len(points) else np.empty((0, 2))
            for word, point in zip(record["pdfRecord"]["wordRows"], aligned):
                token = word["token"]
                if token not in component_terms and token not in STRICT_UNIT_ORDER_TERMS and token != "overdose":
                    continue
                px = int(x + point[0] * scale)
                py = int(y + 24 + point[1] * scale)
                color = (20, 105, 220) if token in component_terms or token == "overdose" else (205, 40, 40)
                draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=color)
                draw.text((px + 5, py - 7), word["text"][:18], fill=color, font=small_f)

        tx = x + page.width + 26
        draw.text((tx, y + 24), record["pdfRecord"]["pdf"], fill=(20, 28, 38), font=body_f)
        draw.text(
            (tx, y + 50),
            f"pairs={fit.get('pairCount', 0)} inliers={fit.get('inlierCount', 0)} median={fit.get('medianResidualPx')}px "
            f"target word rows={record['evaluation']['targetWordHitRowCount']}/4 component rows={record['evaluation']['targetExactComponentRowCount']}/4 "
            f"strict rows={record['evaluation']['targetStrictInstructionRowCount']}/4",
            fill=(62, 72, 86),
            font=small_f,
        )
        yy = y + 84
        for row in record["evaluation"]["targetRows"]:
            draw.text(
                (tx, yy),
                f"{row['target']} words={row['alignedWordCount']} component={row['componentHitWords'] or '-'} strict={row['strictInstructionWords'] or '-'} text={row['alignedText'][:90] or '-'}",
                fill=(45, 50, 58),
                font=small_f,
            )
            yy += 24
        yy += 10
        for row in record["evaluation"]["componentRows"][:12]:
            draw.text(
                (tx, yy),
                f"{row['target']} term {row['term']} nearest '{row['word']}' distance={row['distanceToTargetBoxPx']}px inside={row['insideTarget']}",
                fill=(45, 50, 58),
                font=small_f,
            )
            yy += 24
        if not fit.get("fitAvailable"):
            draw.text((tx, yy), f"Fit unavailable: {fit.get('reason')}", fill=(160, 40, 40), font=small_f)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    targets = active_targets()
    map_words = article_words()
    source_review = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    records = []
    for pdf in PDFS:
        if not pdf.exists():
            continue
        pdf_record = pdf_words(pdf)
        pairs = build_pairs(pdf_record["wordRows"], map_words)
        fit = robust_fit(pairs)
        evaluation = evaluate_targets(pdf_record, fit, targets)
        records.append(
            {
                "pdfRecord": {k: v for k, v in pdf_record.items() if k != "wordRows"},
                "wordCount": len(pdf_record["wordRows"]),
                "pairSamples": pairs[:30],
                "fit": fit,
                "evaluation": evaluation,
                "_pdfWords": pdf_record,
            }
        )

    source_r3 = (
        source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount")
        or reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount")
        or 0
    )
    satisfied = (
        source_review.get("summary", {}).get("satisfiedReopenTriggerCount")
        or reopen.get("summary", {}).get("satisfiedTriggerCount")
        or reopen.get("summary", {}).get("satisfiedNow")
        or 0
    )
    trigger_count = (
        reopen.get("summary", {}).get("triggerCount")
        or reopen.get("triggerCount")
        or len(reopen.get("triggerRows", []))
        or 9
    )
    fit_available_count = sum(1 for row in records if row["fit"].get("fitAvailable"))
    total_pairs = sum(row["fit"].get("pairCount", 0) for row in records)
    total_inliers = sum(row["fit"].get("inlierCount", 0) for row in records)
    target_word_rows = sum(row["evaluation"]["targetWordHitRowCount"] for row in records)
    target_component_rows = sum(row["evaluation"]["targetExactComponentRowCount"] for row in records)
    target_strict_rows = sum(row["evaluation"]["targetStrictInstructionRowCount"] for row in records)
    strict_after_alignment = sorted(
        {
            strict["token"]
            for row in records
            for strict in row["evaluation"]["strictInstructionRows"]
        }
    )
    min_component_distances = []
    for row in records:
        distances = [
            comp["distanceToTargetBoxPx"]
            for comp in row["evaluation"]["componentRows"]
            if not comp["insideTarget"]
        ]
        if distances:
            min_component_distances.append(min(distances))
    min_component_distance = round(min(min_component_distances), 3) if min_component_distances else None
    fingerprint = (
        f"pdfs={len(records)}|fits={fit_available_count}|pairs={total_pairs}|inliers={total_inliers}|"
        f"targetWordRows={target_word_rows}|targetComponentRows={target_component_rows}|"
        f"targetStrictRows={target_strict_rows}|strictAfter={','.join(strict_after_alignment) if strict_after_alignment else '-'}|"
        f"minCompDist={min_component_distance}|sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    summary = {
        "pdfCount": len(records),
        "fitAvailableCount": fit_available_count,
        "totalTokenPairCount": total_pairs,
        "totalInlierCount": total_inliers,
        "targetWordHitRowCount": target_word_rows,
        "targetExactComponentRowCount": target_component_rows,
        "targetStrictInstructionRowCount": target_strict_rows,
        "strictInstructionTermsAfterAlignment": strict_after_alignment,
        "minimumComponentDistanceToOwnTargetBoxPx": min_component_distance,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "pdfOcrAffineAlignmentFingerprint": fingerprint,
    }
    public_records = []
    for row in records:
        record = {k: v for k, v in row.items() if k != "_pdfWords"}
        public_records.append(record)

    draw_sheet(
        [
            {
                "pdfRecord": row["_pdfWords"],
                "fit": row["fit"],
                "evaluation": row["evaluation"],
            }
            for row in records
        ],
        targets,
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current PDF OCR affine alignment gate. Fits page-76 PDF OCR word coordinates to the "
            "high-resolution 3D word map and tests aligned OCR words against O4/B4/G5/O5. "
            "No key/hash/seed/WIF/address/BIP39/candidate work."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "records": public_records,
        "decision": {
            "currentPdfOcrAffineAlignmentGate": "do_not_reopen_pdf_ocr_alignment",
            "selectorUnlocked": False,
            "reason": (
                "Affine realignment can fit the low-resolution duplicate OCR layer to the page map, "
                "but aligned target boxes still contain no exact target components or source-side "
                "unit/order words. The high-resolution magazine OCR layer cannot produce a useful "
                "fit from unique word tokens."
            ),
            "nextMove": (
                "Keep PDF OCR alignment as a closed provenance layer. Future local work should be "
                "source-intake/reopen-gate validation, not text-layer coordinate repair."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF OCR Affine Alignment Gate",
        "",
        "Scope: fit page-76 PDF OCR word coordinates to the high-resolution 3D word map and test aligned OCR words against O4/B4/G5/O5. This checks OCR-layer misregistration only; no key derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs checked: `{summary['pdfCount']}`",
        f"- Fits available: `{summary['fitAvailableCount']}`",
        f"- Token pairs / inliers: `{summary['totalTokenPairCount']}` / `{summary['totalInlierCount']}`",
        f"- Target word-hit rows after alignment: `{summary['targetWordHitRowCount']}`",
        f"- Target exact-component rows after alignment: `{summary['targetExactComponentRowCount']}`",
        f"- Target strict-instruction rows after alignment: `{summary['targetStrictInstructionRowCount']}`",
        f"- Strict instruction terms after alignment: `{', '.join(summary['strictInstructionTermsAfterAlignment']) if summary['strictInstructionTermsAfterAlignment'] else '-'}`",
        f"- Minimum component distance to its own target box: `{summary['minimumComponentDistanceToOwnTargetBoxPx']}` px",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | words | pairs | inliers | median residual | target word rows | component rows | strict rows | nearest component distance |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in public_records:
        fit = row["fit"]
        evaluation = row["evaluation"]
        distances = [
            comp["distanceToTargetBoxPx"]
            for comp in evaluation["componentRows"]
            if not comp["insideTarget"]
        ]
        min_dist = min(distances) if distances else "-"
        lines.append(
            f"| `{row['pdfRecord']['pdf']}` | `{row['wordCount']}` | `{fit.get('pairCount', 0)}` | `{fit.get('inlierCount', 0)}` | `{fit.get('medianResidualPx')}` | `{evaluation['targetWordHitRowCount']}/4` | `{evaluation['targetExactComponentRowCount']}/4` | `{evaluation['targetStrictInstructionRowCount']}/4` | `{min_dist}` |"
        )
    lines.extend(["", "## Target Rows", ""])
    for row in public_records:
        lines.append(f"### `{row['pdfRecord']['pdf']}`")
        lines.append("")
        fit = row["fit"]
        if not fit.get("fitAvailable"):
            lines.append(f"- Fit unavailable: `{fit.get('reason')}` with `{fit.get('pairCount', 0)}` token pairs.")
            lines.append("")
            continue
        for target in row["evaluation"]["targetRows"]:
            lines.append(
                f"- {target['target']} `{target['label']}` aligned words: `{target['alignedText'] or '-'}`; components: `{target['componentHitWords'] or '-'}`; strict: `{target['strictInstructionWords'] or '-'}`"
            )
        for comp in row["evaluation"]["componentRows"]:
            lines.append(
                f"- {comp['target']} nearest `{comp['term']}` component after alignment: `{comp['word']}` at `{comp['distanceToTargetBoxPx']}` px; inside target: `{comp['insideTarget']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Decision",
            "",
            "- Do not reopen PDF OCR alignment as a selector.",
            "- The low-resolution duplicate PDFs can be geometrically fit back onto the high-resolution word map, but the aligned OCR layer still does not put exact active target components or strict unit/order terms into the O4/B4/G5/O5 boxes.",
            "- The high-resolution `magazine.pdf` OCR text is too corrupt/rotated to provide enough unique word correspondences for a useful fit.",
            "",
            "## Next Move",
            "",
            "- Treat OCR-layer coordinate repair as closed. Future useful work remains source-intake/reopen-gate validation unless new physical/original-layout/source evidence arrives.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()
