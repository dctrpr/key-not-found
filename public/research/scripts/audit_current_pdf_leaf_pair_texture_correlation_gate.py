#!/usr/bin/env python3
"""Audit current-PDF leaf-pair texture correlation under physical mirror controls.

This bounded source/provenance pass compares embedded PDF page-image texture for
article leaf pairs 75/76, 77/78, and 79/80 under fixed physical orientation
hypotheses. It checks whether the natural back-side mirror transform is a
distinct registration signal in the current PDFs. It does not extract key
material, generate candidates, hash, check seeds/WIF/addresses, or brute force.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_pdf_native_image_registration_gate as native  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_pdf_leaf_pair_texture_correlation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_leaf_pair_texture_correlation_gate.json"
OUT_MD = OUT / "current_pdf_leaf_pair_texture_correlation_gate.md"
OUT_SHEET = OUT / "current_pdf_leaf_pair_texture_correlation_gate_sheet.jpg"

SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

PAGE_PAIRS = [(75, 76), (77, 78), (79, 80)]
ACTIVE_REGION_REF = [240.0, 2080.0, 1900.0, 3050.0]
LOWER_REGION_REF = [0.0, 1900.0, 2544.0, 3264.0]

Transform = tuple[str, str, Callable[[Image.Image], Image.Image]]
TRANSFORMS: list[Transform] = [
    (
        "physical_back_mirror",
        "Back side seen through the target page, source page mirrored left-right.",
        ImageOps.mirror,
    ),
    (
        "same_side_no_mirror",
        "Unmirrored source page over target page, included as a non-backside control.",
        lambda img: img,
    ),
    (
        "back_mirror_rotate180",
        "Mirrored back side with 180-degree turn, testing page-turn ambiguity.",
        lambda img: ImageOps.mirror(img).rotate(180),
    ),
    (
        "front_rotate180",
        "Unmirrored 180-degree turn, included as an orientation control.",
        lambda img: img.rotate(180),
    ),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def article_page_index(article_page: int) -> int:
    return article_page - 73


def scaled_box(box: list[float], size: tuple[int, int]) -> list[float]:
    return native.scaled_box(box, size)


def crop_array(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [round(v) for v in box]
    return arr[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)]


def grayscale(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("L"), dtype=np.float32) / 255.0


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0 or a.shape != b.shape:
        return 0.0
    av = a.astype(np.float32).ravel()
    bv = b.astype(np.float32).ravel()
    av = av - float(av.mean())
    bv = bv - float(bv.mean())
    denom = float(np.sqrt(np.sum(av * av) * np.sum(bv * bv)))
    if denom <= 1e-9:
        return 0.0
    return float(np.sum(av * bv) / denom)


def feature_metrics(source_mask: np.ndarray, target_mask: np.ndarray) -> dict[str, float]:
    if not source_mask.size or source_mask.shape != target_mask.shape:
        return {
            "sourceCoverage": 0.0,
            "targetCoverage": 0.0,
            "overlapCoverage": 0.0,
            "unionCoverage": 0.0,
            "featureIou": 0.0,
            "sourceOnlyCoverage": 0.0,
            "targetOnlyCoverage": 0.0,
        }
    source = source_mask.astype(bool)
    target = target_mask.astype(bool)
    overlap = np.logical_and(source, target)
    union = np.logical_or(source, target)
    source_only = np.logical_and(source, ~target)
    target_only = np.logical_and(target, ~source)
    union_count = int(union.sum())
    return {
        "sourceCoverage": float(source.mean()),
        "targetCoverage": float(target.mean()),
        "overlapCoverage": float(overlap.mean()),
        "unionCoverage": float(union.mean()),
        "featureIou": float(overlap.sum() / union_count) if union_count else 0.0,
        "sourceOnlyCoverage": float(source_only.mean()),
        "targetOnlyCoverage": float(target_only.mean()),
    }


def region_metrics(
    source_gray: np.ndarray,
    target_gray: np.ndarray,
    source_mask: np.ndarray,
    target_mask: np.ndarray,
    box: list[float],
) -> dict[str, float]:
    source_gray_crop = crop_array(source_gray, box)
    target_gray_crop = crop_array(target_gray, box)
    source_mask_crop = crop_array(source_mask, box)
    target_mask_crop = crop_array(target_mask, box)
    metrics = feature_metrics(source_mask_crop, target_mask_crop)
    metrics["luminanceCorrelation"] = pearson(source_gray_crop, target_gray_crop)
    if source_gray_crop.size and source_gray_crop.shape == target_gray_crop.shape:
        metrics["meanAbsDiff"] = float(np.mean(np.abs(source_gray_crop - target_gray_crop)))
    else:
        metrics["meanAbsDiff"] = 0.0
    return {key: round(value, 9) for key, value in metrics.items()}


def load_pair_images(
    pdf_path: Path,
    source_article_page: int,
    target_article_page: int,
) -> tuple[Image.Image, Image.Image, dict[str, Any]]:
    with fitz.open(pdf_path) as doc:
        source_record = native.page_record(
            doc, pdf_path, article_page_index(source_article_page), source_article_page
        )
        target_record = native.page_record(
            doc, pdf_path, article_page_index(target_article_page), target_article_page
        )
    source = source_record.pop("image")
    target = target_record.pop("image")
    if source.size != target.size:
        source = source.resize(target.size, Image.Resampling.BICUBIC)
    pair = {
        "pdf": rel(pdf_path),
        "pair": f"{source_article_page}/{target_article_page}",
        "sourceArticlePage": source_article_page,
        "targetArticlePage": target_article_page,
        "sourceRecord": source_record,
        "targetRecord": target_record,
        "sameImageSize": source_record.get("imageSize") == target_record.get("imageSize"),
        "sameImageRect": native.same_list(
            source_record.get("imageRect", []), target_record.get("imageRect", [])
        ),
        "imageRectDeltaPt": [
            round(target_record.get("imageRect", [0, 0, 0, 0])[idx] - source_record.get("imageRect", [0, 0, 0, 0])[idx], 4)
            for idx in range(4)
        ],
    }
    return source, target, pair


def analyze_variant(
    pdf_path: Path,
    pair: tuple[int, int],
    transform_id: str,
    transform_description: str,
    source_img: Image.Image,
    target_img: Image.Image,
    transform: Callable[[Image.Image], Image.Image],
    active_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    source_transformed = transform(source_img).convert("RGB")
    if source_transformed.size != target_img.size:
        source_transformed = source_transformed.resize(target_img.size, Image.Resampling.BICUBIC)

    source_gray = grayscale(source_transformed)
    target_gray = grayscale(target_img)
    source_mask = native.feature_mask(source_transformed)
    target_mask = native.feature_mask(target_img)

    active_region_box = scaled_box(ACTIVE_REGION_REF, target_img.size)
    lower_region_box = scaled_box(LOWER_REGION_REF, target_img.size)
    full_box = [0.0, 0.0, float(target_img.size[0]), float(target_img.size[1])]
    active_boxes = [row["box"] for row in active_rows]

    active_box_rows: list[dict[str, Any]] = []
    for row in active_rows:
        box = scaled_box(row["box"], target_img.size)
        metrics = region_metrics(source_gray, target_gray, source_mask, target_mask, box)
        control_iou = [
            region_metrics(
                source_gray,
                target_gray,
                source_mask,
                target_mask,
                scaled_box(control, target_img.size),
            )["featureIou"]
            for control in native.control_boxes_for(row["box"], active_boxes)
        ]
        p95 = float(np.quantile(control_iou, 0.95)) if control_iou else 0.0
        active_box_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "box": [round(value, 2) for value in box],
                **metrics,
                "controlCount": len(control_iou),
                "controlP95FeatureIou": round(p95, 9),
                "controlMaxFeatureIou": round(max(control_iou), 9) if control_iou else 0.0,
                "isAboveControlP95": bool(metrics["featureIou"] > p95),
                "isFeatureIouAtLeast10": bool(metrics["featureIou"] >= 0.10),
                "isCorrelationAtLeast25": bool(metrics["luminanceCorrelation"] >= 0.25),
            }
        )

    region_summaries = {
        "full": region_metrics(source_gray, target_gray, source_mask, target_mask, full_box),
        "lower": region_metrics(source_gray, target_gray, source_mask, target_mask, lower_region_box),
        "activeRegion": region_metrics(
            source_gray, target_gray, source_mask, target_mask, active_region_box
        ),
    }
    feature_iou_values = [row["featureIou"] for row in active_box_rows]
    corr_values = [row["luminanceCorrelation"] for row in active_box_rows]
    return {
        "pdf": rel(pdf_path),
        "pair": f"{pair[0]}/{pair[1]}",
        "sourceArticlePage": pair[0],
        "targetArticlePage": pair[1],
        "transform": transform_id,
        "transformDescription": transform_description,
        "imageSize": list(target_img.size),
        "regions": region_summaries,
        "activeBoxRows": active_box_rows,
        "activeBoxAboveControlP95Count": sum(row["isAboveControlP95"] for row in active_box_rows),
        "activeBoxIouAtLeast10Count": sum(row["isFeatureIouAtLeast10"] for row in active_box_rows),
        "activeBoxCorrelationAtLeast25Count": sum(
            row["isCorrelationAtLeast25"] for row in active_box_rows
        ),
        "allFourActiveBoxAboveControlP95": all(row["isAboveControlP95"] for row in active_box_rows),
        "allFourActiveBoxIouAtLeast10": all(row["isFeatureIouAtLeast10"] for row in active_box_rows),
        "meanActiveBoxFeatureIou": round(float(np.mean(feature_iou_values)), 9),
        "maxActiveBoxFeatureIou": round(max(feature_iou_values), 9),
        "meanActiveBoxCorrelation": round(float(np.mean(corr_values)), 9),
        "maxActiveBoxCorrelation": round(max(corr_values), 9),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1840, 1260
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(11)

    summary = result["summary"]
    draw.rectangle((0, 0, width, 105), fill=(27, 32, 43))
    draw.text((24, 16), "Current PDF Leaf-Pair Texture Correlation Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Embedded PDF page images; physical back-mirror vs fixed orientation controls; no key extraction.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1120, 22),
        f"pairs: {summary['pairCount']} | rows: {summary['variantRowCount']} | phys-best: {summary['physicalBestVariantCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1120, 52),
        f"page75/76 phys best: {summary['page75_76PhysicalBestCount']} | all-four p95: {summary['allFourAboveControlP95VariantCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 126
    xs = [22, 350, 438, 665, 785, 905, 1045, 1175, 1295, 1415]
    headers = [
        "PDF",
        "pair",
        "transform",
        "active corr",
        "active IoU",
        "full corr",
        "above p95",
        "all4 p95",
        "IoU>=10",
        "best?",
    ]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(45, 48, 54), font=small)
    y += 24
    for idx, row in enumerate(result["rankedVariantRows"][:36]):
        fill = (246, 248, 250) if idx % 2 == 0 else (255, 255, 255)
        draw.rectangle((16, y - 5, width - 16, y + 20), fill=fill)
        values = [
            row["pdf"],
            row["pair"],
            row["transform"],
            f"{row['regions']['activeRegion']['luminanceCorrelation']:.4f}",
            f"{row['regions']['activeRegion']['featureIou']:.4f}",
            f"{row['regions']['full']['luminanceCorrelation']:.4f}",
            str(row["activeBoxAboveControlP95Count"]),
            str(int(row["allFourActiveBoxAboveControlP95"])),
            str(row["activeBoxIouAtLeast10Count"]),
            str(int(row["isBestForPair"])),
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value[:45], fill=(25, 28, 34), font=tiny)
        y += 23

    draw.text((24, 988), "Decision", fill=(45, 48, 54), font=small)
    notes = [
        f"Physical-back mirror is top by active-region correlation in {summary['physicalBestVariantCount']} of {summary['pairCount']} pair rows.",
        f"Page 75/76 physical-back mirror top rows: {summary['page75_76PhysicalBestCount']} of {summary['page75_76PairCount']}.",
        f"All-four active boxes above same-size control p95: {summary['allFourAboveControlP95VariantCount']} variants.",
        f"Source-backed R3 / triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}.",
    ]
    yy = 1018
    for note in notes:
        draw.text((24, yy), note, fill=(25, 28, 34), font=small)
        yy += 28

    sheet.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current PDF Leaf-Pair Texture Correlation Gate",
        "",
        "Scope: compared embedded PDF page-image texture for article leaf pairs 75/76, 77/78, and 79/80 under four fixed orientation hypotheses, including the natural physical back-side mirror. This is source/provenance validation only; no OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- PDFs / leaf pairs / transforms / variant rows: `{summary['pdfCount']}` / `{summary['pairCount']}` / `{summary['transformCount']}` / `{summary['variantRowCount']}`",
        f"- Active-box rows / above control p95 / all-four above p95 variants: `{summary['activeBoxRowCount']}` / `{summary['activeBoxAboveControlP95Count']}` / `{summary['allFourAboveControlP95VariantCount']}`",
        f"- Physical-back mirror best pair rows: `{summary['physicalBestVariantCount']}` / `{summary['pairCount']}`",
        f"- Page 75/76 physical-back mirror best rows: `{summary['page75_76PhysicalBestCount']}` / `{summary['page75_76PairCount']}`",
        f"- Max page 75/76 physical active-region correlation / feature IoU: `{summary['page75_76PhysicalMaxActiveRegionCorrelation']:.4f}` / `{summary['page75_76PhysicalMaxActiveRegionFeatureIou']:.4f}`",
        f"- Max active-box feature IoU / active-box correlation: `{summary['maxActiveBoxFeatureIou']:.4f}` / `{summary['maxActiveBoxCorrelation']:.4f}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Pair Rows",
        "",
        "| PDF | pair | transform | active-region corr | active-region IoU | full corr | active boxes >p95 | all-four >p95 | IoU>=10 | best for pair |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["rankedVariantRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    f"`{row['pair']}`",
                    f"`{row['transform']}`",
                    f"{row['regions']['activeRegion']['luminanceCorrelation']:.4f}",
                    f"{row['regions']['activeRegion']['featureIou']:.4f}",
                    f"{row['regions']['full']['luminanceCorrelation']:.4f}",
                    str(row["activeBoxAboveControlP95Count"]),
                    str(int(row["allFourActiveBoxAboveControlP95"])),
                    str(row["activeBoxIouAtLeast10Count"]),
                    str(int(row["isBestForPair"])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_leaf_pair_texture_correlation_no_selector`.",
            "- Physical back-side mirror is not a distinctive all-pair or all-target registration signal in the current PDFs.",
            "- Page 75/76 can show ordinary page-text texture correlation in derivative PDFs, but it does not create an all-four active-box outlier above same-size controls and does not supply unit/order wording.",
            "- Treat this as another source/provenance stop-check, not a selector.",
            "",
            "## Next Move",
            "",
            "- Keep local PDF leaf-pair texture/correlation mechanics closed unless a distinct physical/original-layout source appears or raw clue wording names the transform, unit, and read order.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    active_rows = native.active_rows()
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))

    pair_records: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    for pdf_path in native.PDFS:
        if not pdf_path.exists():
            continue
        for pair in PAGE_PAIRS:
            source_img, target_img, pair_record = load_pair_images(pdf_path, pair[0], pair[1])
            pair_records.append(pair_record)
            for transform_id, description, transform in TRANSFORMS:
                variant_rows.append(
                    analyze_variant(
                        pdf_path,
                        pair,
                        transform_id,
                        description,
                        source_img,
                        target_img,
                        transform,
                        active_rows,
                    )
                )

    best_by_pair: dict[tuple[str, str], str] = {}
    for row in variant_rows:
        key = (row["pdf"], row["pair"])
        current = next(
            (
                candidate
                for candidate in variant_rows
                if (candidate["pdf"], candidate["pair"]) == key
                and candidate["transform"] == best_by_pair.get(key)
            ),
            None,
        )
        if current is None or row["regions"]["activeRegion"]["luminanceCorrelation"] > current[
            "regions"
        ]["activeRegion"]["luminanceCorrelation"]:
            best_by_pair[key] = row["transform"]

    for row in variant_rows:
        row["isBestForPair"] = row["transform"] == best_by_pair[(row["pdf"], row["pair"])]

    ranked_variant_rows = sorted(
        variant_rows,
        key=lambda row: (
            row["pdf"],
            row["pair"],
            -int(row["isBestForPair"]),
            row["transform"],
        ),
    )
    physical_rows = [row for row in variant_rows if row["transform"] == "physical_back_mirror"]
    page75_76_physical_rows = [row for row in physical_rows if row["pair"] == "75/76"]
    active_box_rows = [box for row in variant_rows for box in row["activeBoxRows"]]
    summary = {
        "pdfCount": len([path for path in native.PDFS if path.exists()]),
        "pairCount": len(pair_records),
        "transformCount": len(TRANSFORMS),
        "variantRowCount": len(variant_rows),
        "activeBoxRowCount": len(active_box_rows),
        "activeBoxAboveControlP95Count": sum(row["isAboveControlP95"] for row in active_box_rows),
        "allFourAboveControlP95VariantCount": sum(
            row["allFourActiveBoxAboveControlP95"] for row in variant_rows
        ),
        "allFourIouAtLeast10VariantCount": sum(
            row["allFourActiveBoxIouAtLeast10"] for row in variant_rows
        ),
        "physicalBestVariantCount": sum(row["isBestForPair"] for row in physical_rows),
        "page75_76PairCount": len(page75_76_physical_rows),
        "page75_76PhysicalBestCount": sum(row["isBestForPair"] for row in page75_76_physical_rows),
        "page75_76PhysicalMaxActiveRegionCorrelation": max(
            (row["regions"]["activeRegion"]["luminanceCorrelation"] for row in page75_76_physical_rows),
            default=0.0,
        ),
        "page75_76PhysicalMaxActiveRegionFeatureIou": max(
            (row["regions"]["activeRegion"]["featureIou"] for row in page75_76_physical_rows),
            default=0.0,
        ),
        "maxActiveBoxFeatureIou": max(
            (row["featureIou"] for row in active_box_rows), default=0.0
        ),
        "maxActiveBoxCorrelation": max(
            (row["luminanceCorrelation"] for row in active_box_rows), default=0.0
        ),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pairs={summary['pairCount']}|"
        f"transforms={summary['transformCount']}|rows={summary['variantRowCount']}|"
        f"activeRows={summary['activeBoxRowCount']}|activeP95={summary['activeBoxAboveControlP95Count']}|"
        f"allFourP95={summary['allFourAboveControlP95VariantCount']}|"
        f"physBest={summary['physicalBestVariantCount']}|"
        f"p7576PhysBest={summary['page75_76PhysicalBestCount']}/{summary['page75_76PairCount']}|"
        f"p7576PhysCorrMax={summary['page75_76PhysicalMaxActiveRegionCorrelation']:.4f}|"
        f"p7576PhysIouMax={summary['page75_76PhysicalMaxActiveRegionFeatureIou']:.4f}|"
        f"activeIouMax={summary['maxActiveBoxFeatureIou']:.4f}|"
        f"activeCorrMax={summary['maxActiveBoxCorrelation']:.4f}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|"
        "selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current-PDF embedded leaf-pair texture/correlation comparison across fixed "
            "physical mirror and orientation-control transforms."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in native.PDFS if path.exists()],
            "pagePairs": [f"{a}/{b}" for a, b in PAGE_PAIRS],
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": "current_pdf_leaf_pair_texture_correlation_no_selector",
        "summary": summary,
        "fingerprint": fingerprint,
        "pairRecords": pair_records,
        "variantRows": variant_rows,
        "rankedVariantRows": ranked_variant_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()
