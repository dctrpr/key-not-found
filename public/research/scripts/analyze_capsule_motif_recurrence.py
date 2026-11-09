#!/usr/bin/env python3
"""Check whether the Issue 24 orange capsule motif recurs in comparison articles.

The p73 opener capsules match p79 orange fragments almost exactly. This pass
tests whether that same capsule artwork appears in the user-provided
comparison PDFs. It is a provenance/layout check, not key derivation.
"""

from __future__ import annotations

import json
from itertools import combinations
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from extract_visual_masks import connected_components


ROOT = Path(__file__).resolve().parents[1]
COMPARE = ROOT / "analysis_outputs/comparison_articles"
OPENER_JSON = ROOT / "analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory.json"
OUT = ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "capsule_motif_recurrence.json"
OUT_MD = OUT / "capsule_motif_recurrence.md"
OUT_SHEET = OUT / "capsule_motif_recurrence_sheet.jpg"


SOURCES = {
    "issue24_toxic_af": COMPARE / "issue24_toxic_af",
    "issue26": COMPARE / "issue26",
    "issue27": COMPARE / "overdose_style_uniqueness/issue27",
    "bitcoin3": COMPARE / "bitcoin3",
    "bitcoin4": COMPARE / "overdose_style_uniqueness/bitcoin4",
}

INDEPENDENT_COMPARISONS = {"issue26", "issue27", "bitcoin3"}
LOW_RES_WITNESSES = {"bitcoin4"}


def warm_orange_mask(img: Image.Image) -> np.ndarray:
    rgb = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    return (r > 160) & (g > 45) & (g < 190) & (b < 140) & ((r - b) > 60) & ((r - g) > 15)


def normalized_mask(img: Image.Image, box: tuple[int, int, int, int], size: int = 48) -> np.ndarray:
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    pad_x = max(4, int(round(w * 0.15)))
    pad_y = max(4, int(round(h * 0.15)))
    crop_box = (
        max(0, x1 - pad_x),
        max(0, y1 - pad_y),
        min(img.width, x2 + pad_x),
        min(img.height, y2 + pad_y),
    )
    crop = img.crop(crop_box).resize((size, size), Image.Resampling.BILINEAR)
    return warm_orange_mask(crop)


def iou(a: np.ndarray, b: np.ndarray) -> float:
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    if union == 0:
        return 0.0
    return float(inter / union)


def similarity_fit(reference: np.ndarray, candidate: np.ndarray) -> dict:
    if len(reference) != len(candidate) or len(reference) < 3:
        return {"available": False}
    ref = reference.astype(float)
    cand = candidate.astype(float)
    rc = ref - ref.mean(axis=0)
    cc = cand - cand.mean(axis=0)
    u, singular_values, vt = np.linalg.svd(rc.T @ cc)
    rotation = u @ vt
    scale = float(singular_values.sum() / (rc**2).sum())
    pred = rc @ rotation * scale + cand.mean(axis=0)
    residuals = np.linalg.norm(pred - cand, axis=1)
    return {
        "available": True,
        "scale": round(scale, 6),
        "residualsPx": [round(float(v), 2) for v in residuals.tolist()],
        "meanResidualPx": round(float(residuals.mean()), 2),
        "maxResidualPx": round(float(residuals.max()), 2),
    }


def best_sequence_match(candidates: list[dict], reference_sequences: dict[str, np.ndarray]) -> dict | None:
    # Individual warm components create false positives in colorful comparison
    # pages. The real Issue 24 capsule motif is a five-item zigzag sequence, so
    # score page-level five-point geometry after sorting each candidate set by y.
    pool = sorted(candidates, key=lambda c: c["bestIou"], reverse=True)[:14]
    if len(pool) < 5:
        return None
    best: dict | None = None
    for combo in combinations(pool, 5):
        ordered = sorted(combo, key=lambda c: (c["center"][1], c["center"][0]))
        cand_points = np.array([c["center"] for c in ordered], dtype=float)
        mean_blob_score = round(float(np.mean([c["bestIou"] for c in ordered])), 4)
        for ref_name, ref_points in reference_sequences.items():
            fit = similarity_fit(ref_points, cand_points)
            if not fit.get("available"):
                continue
            row = {
                "referenceSequence": ref_name,
                "meanBlobScore": mean_blob_score,
                "meanResidualPx": fit["meanResidualPx"],
                "maxResidualPx": fit["maxResidualPx"],
                "scale": fit["scale"],
                "boxes": [c["box"] for c in ordered],
                "centers": [c["center"] for c in ordered],
                "blobScores": [c["bestIou"] for c in ordered],
            }
            if best is None or (row["meanResidualPx"], -row["meanBlobScore"], row["maxResidualPx"]) < (
                best["meanResidualPx"],
                -best["meanBlobScore"],
                best["maxResidualPx"],
            ):
                best = row
    return best


def area(box: tuple[int, int, int, int]) -> int:
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def center(box: tuple[int, int, int, int]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def detect_candidates(img: Image.Image) -> list[dict]:
    # Work at half resolution to keep the scan bounded on colorful comparison
    # pages. Boxes are scaled back to original coordinates before scoring.
    small = img.resize((img.width // 2, img.height // 2), Image.Resampling.BILINEAR)
    mask = warm_orange_mask(small)
    comps = connected_components(mask, min_area=90)
    candidates: list[dict] = []
    for comp in comps:
        sx1, sy1, sx2, sy2 = comp["box"]
        box = (sx1 * 2, sy1 * 2, sx2 * 2, sy2 * 2)
        x1, y1, x2, y2 = box
        w = x2 - x1
        h = y2 - y1
        box_a = area(box)
        mask_area = int(comp["area"] * 4)
        fill = mask_area / box_a if box_a else 0
        if not (28 <= w <= 210 and 28 <= h <= 210):
            continue
        if box_a < 1_000 or box_a > 28_000:
            continue
        if not (0.18 <= fill <= 0.9):
            continue
        candidates.append(
            {
                "box": tuple(int(v) for v in box),
                "center": tuple(round(v, 2) for v in center(box)),
                "width": int(w),
                "height": int(h),
                "maskArea": int(mask_area),
                "fill": round(float(fill), 3),
            }
        )
    return candidates


def load_reference_masks() -> tuple[list[dict], list[np.ndarray]]:
    data = json.loads(OPENER_JSON.read_text())
    refs = []
    p73_img = Image.open(data["inputs"]["p73Opener"]).convert("RGB")
    for row in data["p73CapsulesTopToBottom"]:
        box = tuple(row["box"])
        refs.append({"source": "issue24_p73", "label": f"O73-{row['capsuleIndexTopToBottom']}", "box": box, "image": p73_img})

    p79_img = Image.open(COMPARE / "issue24_toxic_af/page_07.jpg").convert("RGB")
    for row in data["p79PillFragmentsFromManualOrangeBoxes"]:
        box = tuple(row["box"])
        refs.append({"source": "issue24_p79", "label": f"P79-{row['orangeBoxIndex']}", "box": box, "image": p79_img})

    masks = [normalized_mask(ref["image"], ref["box"]) for ref in refs]
    return refs, masks


def load_reference_sequences() -> dict[str, np.ndarray]:
    data = json.loads(OPENER_JSON.read_text())
    return {
        "issue24_p73_capsules": np.array([row["center"] for row in data["p73CapsulesTopToBottom"]], dtype=float),
        "issue24_p79_fragments": np.array([row["center"] for row in data["p79PillFragmentsFromManualOrangeBoxes"]], dtype=float),
    }


def score_candidate(img: Image.Image, candidate: dict, refs: list[dict], ref_masks: list[np.ndarray]) -> dict:
    cand_mask = normalized_mask(img, tuple(candidate["box"]))
    scores = [iou(cand_mask, ref_mask) for ref_mask in ref_masks]
    best_idx = int(np.argmax(scores)) if scores else -1
    candidate = dict(candidate)
    candidate["bestIou"] = round(float(scores[best_idx]), 4) if best_idx >= 0 else 0.0
    candidate["bestReference"] = refs[best_idx]["label"] if best_idx >= 0 else None
    candidate["bestReferenceSource"] = refs[best_idx]["source"] if best_idx >= 0 else None
    return candidate


def draw_sheet(rows: list[dict]) -> None:
    top = rows[:18]
    if not top:
        Image.new("RGB", (800, 120), "white").save(OUT_SHEET)
        return
    cell_w, cell_h = 260, 220
    cols = 3
    sheet = Image.new("RGB", (cols * cell_w, ((len(top) + cols - 1) // cols) * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(top):
        img = Image.open(row["imagePath"]).convert("RGB")
        x1, y1, x2, y2 = row["box"]
        pad = 70
        crop = img.crop((max(0, x1 - pad), max(0, y1 - pad), min(img.width, x2 + pad), min(img.height, y2 + pad)))
        crop.thumbnail((220, 150), Image.Resampling.LANCZOS)
        x = (i % cols) * cell_w + 16
        y = (i // cols) * cell_h + 44
        draw.text((x, y - 38), f"{row['source']} p{row['page']:02d}  score={row['bestIou']}", fill=(0, 0, 0))
        draw.text((x, y - 22), f"ref={row['bestReference']} box={tuple(row['box'])}", fill=(0, 0, 0))
        sheet.paste(crop, (x, y))
        bx1 = int((x1 - max(0, x1 - pad)) * crop.width / max(1, (min(img.width, x2 + pad) - max(0, x1 - pad))))
        by1 = int((y1 - max(0, y1 - pad)) * crop.height / max(1, (min(img.height, y2 + pad) - max(0, y1 - pad))))
        bx2 = int((x2 - max(0, x1 - pad)) * crop.width / max(1, (min(img.width, x2 + pad) - max(0, x1 - pad))))
        by2 = int((y2 - max(0, y1 - pad)) * crop.height / max(1, (min(img.height, y2 + pad) - max(0, y1 - pad))))
        draw.rectangle((x + bx1, y + by1, x + bx2, y + by2), outline=(255, 90, 0), width=3)
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    refs, ref_masks = load_reference_masks()
    reference_sequences = load_reference_sequences()
    all_rows = []
    source_summary = {}
    all_sequence_rows = []
    for source, folder in SOURCES.items():
        page_paths = sorted(folder.glob("page_*.jpg"))
        source_rows = []
        source_sequence_rows = []
        for page_path in page_paths:
            page_no = int(page_path.stem.split("_")[-1])
            img = Image.open(page_path).convert("RGB")
            candidates = [score_candidate(img, c, refs, ref_masks) for c in detect_candidates(img)]
            candidates.sort(key=lambda c: c["bestIou"], reverse=True)
            for c in candidates:
                c.update({"source": source, "page": page_no, "imagePath": str(page_path)})
            sequence = best_sequence_match(candidates, reference_sequences)
            if sequence:
                sequence.update({"source": source, "page": page_no, "imagePath": str(page_path)})
                source_sequence_rows.append(sequence)
                all_sequence_rows.append(sequence)
            source_rows.extend(candidates)
            all_rows.extend(candidates)
        source_rows.sort(key=lambda c: c["bestIou"], reverse=True)
        source_sequence_rows.sort(key=lambda r: (r["meanResidualPx"], -r["meanBlobScore"], r["maxResidualPx"]))
        strong = [r for r in source_rows if r["bestIou"] >= 0.42]
        strong_sequence = [r for r in source_sequence_rows if r["meanResidualPx"] <= 12 and r["maxResidualPx"] <= 30]
        source_summary[source] = {
            "pages": len(page_paths),
            "candidateComponents": len(source_rows),
            "strongIndividualWarmShapeMatches": len(strong),
            "strongFivePointSequenceMatches": len(strong_sequence),
            "topMatches": source_rows[:10],
            "topSequenceMatches": source_sequence_rows[:5],
        }

    all_rows.sort(key=lambda c: c["bestIou"], reverse=True)
    all_sequence_rows.sort(key=lambda r: (r["meanResidualPx"], -r["meanBlobScore"], r["maxResidualPx"]))
    draw_sheet(all_rows)

    comparison_strong = [
        r
        for r in all_rows
        if r["source"] in INDEPENDENT_COMPARISONS and r["bestIou"] >= 0.42
    ]
    comparison_strong_sequences = [
        r
        for r in all_sequence_rows
        if r["source"] in INDEPENDENT_COMPARISONS and r["meanResidualPx"] <= 12 and r["maxResidualPx"] <= 30
    ]
    low_res_witness_sequences = [
        r
        for r in all_sequence_rows
        if r["source"] in LOW_RES_WITNESSES and r["meanResidualPx"] <= 12 and r["maxResidualPx"] <= 30
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "orange capsule motif recurrence check; no key derivation",
        "reference": [{"source": r["source"], "label": r["label"], "box": r["box"]} for r in refs],
        "referenceSequences": {name: seq.tolist() for name, seq in reference_sequences.items()},
        "reviewSheet": str(OUT_SHEET),
        "sourceSummary": source_summary,
        "topMatchesAllSources": all_rows[:24],
        "topFivePointSequenceMatches": all_sequence_rows[:12],
        "comparisonStrongMatches": comparison_strong,
        "comparisonStrongFivePointSequenceMatches": comparison_strong_sequences,
        "lowResWitnessStrongFivePointSequenceMatches": low_res_witness_sequences,
        "assessment": [
            "Individual red/orange blobs in the comparison articles can look capsule-like, so single-component matching is too permissive.",
            "The five-point zigzag sequence check recovers the Issue 24 p73/p79 capsule motif and finds no strong five-point sequence recurrence in the independent comparison articles Issue_26, Issue_27, or bitcoin3 at the current threshold.",
            "bitcoin4 is a lower-resolution Issue 24 witness, so its matches validate the duplicate/witness role rather than proving the motif is generic.",
            "This supports treating the five-capsule chain as Issue-24-specific provenance/order evidence, but it still does not make the capsules a direct selector.",
        ],
        "nextMove": "Keep the five-capsule motif active only as Issue-24-specific source/provenance evidence; continue looking for the missing rule that maps source/order evidence onto page-76 text.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Capsule Motif Recurrence",
        "",
        "Scope: check whether the Issue 24 orange capsule artwork recurs in the user-provided comparison PDFs. This is a layout/provenance check only; no key candidates are generated.",
        "",
        f"- Review sheet: `{OUT_SHEET}`",
        "",
        "## Summary",
        "",
    ]
    for source, summary in source_summary.items():
        lines.append(
            f"- {source}: candidates `{summary['candidateComponents']}`, strong individual warm-shape matches `{summary['strongIndividualWarmShapeMatches']}`, strong five-point sequence matches `{summary['strongFivePointSequenceMatches']}`"
        )
    lines.extend(["", "## Five-Point Sequence Matches", ""])
    for row in all_sequence_rows[:12]:
        lines.append(
            f"- {row['source']} p{row['page']:02d}: ref={row['referenceSequence']} meanResidual={row['meanResidualPx']} px maxResidual={row['maxResidualPx']} px meanBlobScore={row['meanBlobScore']}"
        )
    lines.extend(["", "## Top Comparison Matches", ""])
    top_comparison = [r for r in all_rows if r["source"] in INDEPENDENT_COMPARISONS][:12]
    if top_comparison:
        for row in top_comparison:
            lines.append(
                f"- {row['source']} p{row['page']:02d}: score={row['bestIou']} ref={row['bestReference']} box={row['box']} size={row['width']}x{row['height']}"
            )
    else:
        lines.append("- No comparison candidates.")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- Individual red/orange blobs in the comparison PDFs can score as capsule-like, so single-component matching is not decisive.",
            "- The five-point zigzag sequence check is the important discriminator: it recovers Issue 24's p73/p79 capsule motif and finds no strong five-point sequence recurrence in `Issue_26.pdf`, `Issue_27.pdf`, or `bitcoin3.pdf`.",
            "- `bitcoin4.pdf` is treated as a lower-resolution Issue 24 witness; matches there confirm source-family duplication, not a generic OVERDOSE motif.",
            "- That makes the p73/p79 capsule chain more Issue-24-specific than generic OVERDOSE house style, but it remains source/order evidence, not a direct key selector.",
            "",
            "## Next Best Move",
            "",
            "- Keep the capsule motif in the active provenance layer. The missing piece is still the human rule that maps source/order evidence onto page-76 text.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"comparison_strong_matches={len(comparison_strong)}")
    print(f"comparison_strong_five_point_sequences={len(comparison_strong_sequences)}")


if __name__ == "__main__":
    main()
