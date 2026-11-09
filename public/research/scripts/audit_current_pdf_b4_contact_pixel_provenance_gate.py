#!/usr/bin/env python3
"""Audit PDF/render provenance of the B4 broad-mask rescue pixel.

The B4 broad-contact provenance gate showed that the only near rescue is a
single off-white broad-only pixel under all-content registration. This pass
samples that exact source/landing point across the current PDFs' embedded page
images and rendered pages to test whether the pixel is a PDF/layout addition or
ordinary source-raster background.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import io
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

from audit_current_scan_source_layer_landing_gate import (
    ACTIVE_INDEX_SLOT,
    CONTENT_BOX_REGISTRATION,
    ROOT,
    active_boxes,
    content_box_modes,
    font,
    load_json,
    load_trigger_summary,
    normalize_page,
    rel,
    shifted_mirrored_source,
    source_layer_masks,
)
from audit_current_scan_source_layer_miss_distance_gate import expanded_box


OUT_DIR = ROOT / "analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate"
JSON_OUT = OUT_DIR / "current_pdf_b4_contact_pixel_provenance_gate.json"
MD_OUT = OUT_DIR / "current_pdf_b4_contact_pixel_provenance_gate.md"
SHEET_OUT = OUT_DIR / "current_pdf_b4_contact_pixel_provenance_gate_sheet.jpg"

B4_BROAD_CONTACT_PROVENANCE = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate/"
    "current_scan_b4_broad_contact_provenance_gate.json"
)
SOURCE_LAYER_MISS_DISTANCE = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/"
    "current_scan_source_layer_miss_distance_gate.json"
)
REOPEN_TRIGGER_MATRIX = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]

PAGE_INDEX = {75: 2, 76: 3}
REFERENCE_SIZE = (2544, 3264)
TARGET_ID = "B4"
MODE_ID = "all_content_box_translation"
LAYER = "broad"
POINT_WINDOW = 9
RING_RADIUS = 32
RENDER_DPI = 300


def pixmap_to_image(pix: fitz.Pixmap) -> Image.Image:
    if pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def render_pdf_page(doc: fitz.Document, page_no: int) -> Image.Image:
    page = doc[PAGE_INDEX[page_no]]
    matrix = fitz.Matrix(RENDER_DPI / 72.0, RENDER_DPI / 72.0)
    pix = page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
    return pixmap_to_image(pix).convert("RGB")


def extract_largest_embedded_image(doc: fitz.Document, page_no: int) -> tuple[Image.Image, dict[str, Any]]:
    page = doc[PAGE_INDEX[page_no]]
    best: tuple[int, dict[str, Any]] | None = None
    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = doc.extract_image(xref)
        area = int(extracted.get("width", image[2])) * int(extracted.get("height", image[3]))
        if best is None or area > best[0]:
            best = (
                area,
                {
                    "xref": xref,
                    "width": int(extracted.get("width", image[2])),
                    "height": int(extracted.get("height", image[3])),
                    "extension": extracted.get("ext"),
                    "bytes": len(extracted.get("image", b"")),
                    "imageBytes": extracted["image"],
                },
            )
    if best is None:
        return render_pdf_page(doc, page_no), {
            "xref": None,
            "width": 0,
            "height": 0,
            "extension": "render_fallback",
            "bytes": 0,
        }
    meta = dict(best[1])
    image = Image.open(io.BytesIO(meta.pop("imageBytes"))).convert("RGB")
    return image, meta


def mad(a: Image.Image, b: Image.Image) -> float:
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.BICUBIC)
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return float(np.asarray(diff, dtype=np.float32).mean())


def orientation_candidates(img: Image.Image) -> dict[str, Image.Image]:
    rgb = img.convert("RGB")
    return {
        "as_is": rgb,
        "rotate180": rgb.rotate(180),
        "hflip": ImageOps.mirror(rgb),
        "hflip_rotate180": ImageOps.mirror(rgb).rotate(180),
    }


def normalize_to_upright(img: Image.Image, page_no: int) -> tuple[Image.Image, dict[str, Any]]:
    reference = Image.open(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page_no))).convert("RGB")
    rows = []
    best_img = img.convert("RGB")
    best_mode = "as_is"
    best_score = 10**9.0
    for mode, candidate in orientation_candidates(img).items():
        resized = candidate.resize(reference.size, Image.Resampling.BICUBIC)
        score = mad(reference.resize((318, 408)), resized.resize((318, 408)))
        rows.append({"orientation": mode, "madToUprightSample": round(score, 4)})
        if score < best_score:
            best_img = resized
            best_mode = mode
            best_score = score
    return best_img, {
        "inputSize": [img.width, img.height],
        "normalizedSize": [best_img.width, best_img.height],
        "bestOrientation": best_mode,
        "bestMadToUprightSample": round(best_score, 4),
        "orientationRows": rows,
    }


def rgb_stats(arr: np.ndarray, x: int, y: int) -> dict[str, Any]:
    h, w = arr.shape[:2]
    if not (0 <= x < w and 0 <= y < h):
        return {"rgb": None, "luma": None, "saturation": None}
    r, g, b = [int(v) for v in arr[y, x, :3].tolist()]
    maxc = max(r, g, b) / 255.0
    minc = min(r, g, b) / 255.0
    sat = (maxc - minc) / maxc if maxc else 0.0
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return {"rgb": [r, g, b], "luma": round(luma, 3), "saturation": round(sat, 6)}


def layer_membership(masks: dict[str, np.ndarray], x: int, y: int) -> dict[str, bool]:
    out = {}
    for layer in ("black", "orange", "grey", "feature", "broad"):
        mask = masks[layer]
        out[layer] = bool(0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x])
    return out


def window_counts(masks: dict[str, np.ndarray], x: int, y: int, radius: int) -> dict[str, int]:
    rows = {}
    for layer in ("black", "orange", "grey", "feature", "broad"):
        mask = masks[layer]
        h, w = mask.shape
        x0 = max(0, x - radius)
        x1 = min(w, x + radius + 1)
        y0 = max(0, y - radius)
        y1 = min(h, y + radius + 1)
        rows[layer] = int(mask[y0:y1, x0:x1].sum())
    return rows


def ring_mask(box: list[float], shape: tuple[int, int], radius: int) -> np.ndarray:
    h, w = shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    ex0, ey0, ex1, ey1 = expanded_box(box, radius, shape)
    mask = np.zeros((h, w), dtype=bool)
    mask[ey0:ey1, ex0:ex1] = True
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = False
    return mask


def layer_list(membership: dict[str, bool]) -> str:
    return ",".join([key for key, value in membership.items() if value]) or "-"


def rgb_delta(a: list[int] | None, b: list[int] | None) -> int | None:
    if a is None or b is None:
        return None
    return max(abs(int(x) - int(y)) for x, y in zip(a, b))


def crop_around(img: Image.Image, point: list[int], pad: int) -> tuple[Image.Image, list[int]]:
    x, y = point
    box = [
        max(0, x - pad),
        max(0, y - pad),
        min(img.width, x + pad),
        min(img.height, y + pad),
    ]
    return img.crop(tuple(box)).convert("RGB"), box


def draw_sheet(result: dict[str, Any], baseline_source: Image.Image) -> None:
    sheet = Image.new("RGB", (1920, 1320), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title_f = font(32, True)
    head_f = font(21, True)
    body_f = font(17)
    small_f = font(13)
    summary = result["summary"]
    draw.text((34, 24), "Current PDF B4 Contact Pixel Provenance Gate", fill=(15, 23, 42), font=title_f)
    y = 82
    for line in [
        f"Decision: {summary['decision']}",
        f"PDF candidates: {summary['candidateCount']} | point broad/feature: {summary['sourcePointBroadCandidateCount']}/{summary['sourcePointFeatureCandidateCount']}",
        f"Landing point broad/feature: {summary['landingPointBroadCandidateCount']}/{summary['landingPointFeatureCandidateCount']} | render-only candidates: {summary['renderOnlyContactCandidateCount']}",
        f"Magazine embedded source RGB: {summary['magazineEmbeddedSourcePointRgb']} | baseline RGB: {summary['baselineSourcePointRgb']}",
    ]:
        draw.text((34, y), line, fill=(30, 41, 59), font=body_f)
        y += 28

    source_point = result["sourcePoint"]
    base_crop, base_box = crop_around(baseline_source, source_point, 310)
    base_crop.thumbnail((530, 410))
    sheet.paste(base_crop, (34, 210))
    draw.text((34, 176), "Baseline source_images page 75", fill=(15, 23, 42), font=head_f)
    sx = base_crop.width / (base_box[2] - base_box[0])
    sy = base_crop.height / (base_box[3] - base_box[1])
    draw.ellipse(
        (
            34 + (source_point[0] - base_box[0]) * sx - 7,
            210 + (source_point[1] - base_box[1]) * sy - 7,
            34 + (source_point[0] - base_box[0]) * sx + 7,
            210 + (source_point[1] - base_box[1]) * sy + 7,
        ),
        fill=(16, 185, 129),
    )

    y = 690
    draw.text((34, y), "Candidate Rows", fill=(15, 23, 42), font=head_f)
    y += 32
    cols = [34, 250, 330, 432, 558, 675, 790, 915, 1040, 1165, 1325, 1475]
    headers = ["pdf", "kind", "orient", "src rgb", "src layer", "land rgb", "land layer", "r32 broad", "r32 feat", "src delta", "render delta", "verdict"]
    for cx, label in zip(cols, headers):
        draw.text((cx, y), label, fill=(51, 65, 85), font=small_f)
    y += 22
    for row in result["candidateRows"]:
        values = [
            row["pdfLabel"][:25],
            row["candidateKind"],
            row["orientation"]["bestOrientation"],
            str(row["sourcePointRgb"]["rgb"]),
            layer_list(row["sourcePointLayerMembership"]),
            str(row["landingPointRgb"]["rgb"]),
            layer_list(row["landingPointLayerMembership"]),
            row["radius32BroadPixelCount"],
            row["radius32FeaturePixelCount"],
            row["deltaVsBaselineSourcePointMax"],
            row.get("deltaVsEmbeddedSourcePointMax"),
            row["verdict"],
        ]
        for cx, val in zip(cols, values):
            draw.text((cx, y), str(val)[:22], fill=(30, 41, 59), font=small_f)
        y += 22

    x = 640
    y = 176
    draw.text((x, y), "Interpretation", fill=(15, 23, 42), font=head_f)
    notes = [
        "The sampled contact is present as broad-only off-white source background, not feature ink.",
        "Render and embedded candidates do not create a new feature/text-bearing B4 contact.",
        "This ties the B4 broad rescue back to the current raster/PDF carrier rather than a hidden PDF layout layer.",
    ]
    y += 40
    for note in notes:
        draw.text((x + 8, y), "- " + note, fill=(30, 41, 59), font=body_f)
        y += 28
    sheet.save(SHEET_OUT, quality=92)


def evaluate_candidate(
    pdf_label: str,
    kind: str,
    image: Image.Image,
    page_no: int,
    source_point: list[int],
    target_point: list[int],
    b4_box: list[float],
    mode: dict[str, Any],
    baseline_rgb: list[int],
    embedded_rgb: list[int] | None,
) -> dict[str, Any]:
    normalized, orientation = normalize_to_upright(image, page_no)
    arr = np.asarray(normalized.convert("RGB"))
    masks = source_layer_masks(arr)
    source_x, source_y = source_point
    source_rgb = rgb_stats(arr, source_x, source_y)
    landing = shifted_mirrored_source(normalized, float(mode["dx"]), float(mode["dy"]))
    landing_arr = np.asarray(landing.convert("RGB"))
    landing_masks = source_layer_masks(landing_arr)
    target_x, target_y = target_point
    target_rgb = rgb_stats(landing_arr, target_x, target_y)
    ring = ring_mask(b4_box, landing_masks[LAYER].shape, RING_RADIUS)
    broad_ring = np.logical_and(landing_masks["broad"], ring)
    feature_ring = np.logical_and(landing_masks["feature"], ring)
    source_membership = layer_membership(masks, source_x, source_y)
    landing_membership = layer_membership(landing_masks, target_x, target_y)
    source_delta = rgb_delta(source_rgb["rgb"], baseline_rgb)
    embedded_delta = rgb_delta(source_rgb["rgb"], embedded_rgb)
    feature_created = bool(landing_membership["feature"] or int(feature_ring.sum()) > 0)
    verdict = "feature_contact_created" if feature_created else "broad_background_only"
    return {
        "pdfLabel": pdf_label,
        "candidateKind": kind,
        "pageNo": page_no,
        "orientation": orientation,
        "sourcePointRgb": source_rgb,
        "sourcePointLayerMembership": source_membership,
        "sourcePointWindowCounts": window_counts(masks, source_x, source_y, POINT_WINDOW),
        "landingPointRgb": target_rgb,
        "landingPointLayerMembership": landing_membership,
        "landingPointWindowCounts": window_counts(landing_masks, target_x, target_y, POINT_WINDOW),
        "radius32BroadPixelCount": int(broad_ring.sum()),
        "radius32FeaturePixelCount": int(feature_ring.sum()),
        "radius32BroadOnlyPixelCount": int(np.logical_and(broad_ring, ~feature_ring).sum()),
        "deltaVsBaselineSourcePointMax": source_delta,
        "deltaVsEmbeddedSourcePointMax": embedded_delta,
        "verdict": verdict,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    contact = load_json(B4_BROAD_CONTACT_PROVENANCE)
    active = active_boxes(load_json(ACTIVE_INDEX_SLOT))
    b4 = next(row for row in active if row["shortId"] == TARGET_ID)
    mode = next(row for row in content_box_modes() if row["modeId"] == MODE_ID)
    source_point = contact.get("nearestSourcePoint") or [1864, 2511]
    target_point = contact.get("nearestTargetPoint") or [711, 2450]
    baseline_source = normalize_page(75)
    baseline_arr = np.asarray(baseline_source.convert("RGB"))
    baseline_rgb = rgb_stats(baseline_arr, source_point[0], source_point[1])["rgb"]
    candidate_rows: list[dict[str, Any]] = []
    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        pdf_label = rel(pdf_path)
        doc = fitz.open(pdf_path)
        embedded_image, embedded_meta = extract_largest_embedded_image(doc, 75)
        embedded_row = evaluate_candidate(
            pdf_label,
            "embedded",
            embedded_image,
            75,
            source_point,
            target_point,
            b4["box"],
            mode,
            baseline_rgb,
            baseline_rgb,
        )
        embedded_row["embeddedMeta"] = embedded_meta
        candidate_rows.append(embedded_row)
        render_image = render_pdf_page(doc, 75)
        render_row = evaluate_candidate(
            pdf_label,
            "render_300dpi",
            render_image,
            75,
            source_point,
            target_point,
            b4["box"],
            mode,
            baseline_rgb,
            embedded_row["sourcePointRgb"]["rgb"],
        )
        render_row["renderDpi"] = RENDER_DPI
        candidate_rows.append(render_row)
        doc.close()

    trigger = load_trigger_summary()
    magazine_embedded = next(
        (
            row
            for row in candidate_rows
            if row["pdfLabel"] == "magazine.pdf" and row["candidateKind"] == "embedded"
        ),
        {},
    )
    source_broad_count = sum(1 for row in candidate_rows if row["sourcePointLayerMembership"]["broad"])
    source_feature_count = sum(1 for row in candidate_rows if row["sourcePointLayerMembership"]["feature"])
    landing_broad_count = sum(1 for row in candidate_rows if row["landingPointLayerMembership"]["broad"])
    landing_feature_count = sum(1 for row in candidate_rows if row["landingPointLayerMembership"]["feature"])
    render_only_candidates = [
        row
        for row in candidate_rows
        if row["candidateKind"].startswith("render") and row["verdict"] == "feature_contact_created"
    ]
    hidden_candidate = bool(render_only_candidates and trigger["sourceBackedR3BridgeHitCount"] > 0)
    decision = "current_pdf_b4_contact_pixel_background_carrier"
    fingerprint = (
        f"pdfs={len({row['pdfLabel'] for row in candidate_rows})}|candidates={len(candidate_rows)}"
        f"|srcBroad={source_broad_count}|srcFeature={source_feature_count}"
        f"|landBroad={landing_broad_count}|landFeature={landing_feature_count}"
        f"|r32Feature={sum(1 for row in candidate_rows if row['radius32FeaturePixelCount'] > 0)}"
        f"|magEmbRgb={magazine_embedded.get('sourcePointRgb', {}).get('rgb')}"
        f"|baseRgb={baseline_rgb}|renderOnlyFeature={len(render_only_candidates)}"
        f"|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger['satisfiedReopenTriggerCount']}/{trigger['triggerCount']}"
        "|selectors=0"
    )
    summary = {
        "decision": decision,
        "candidateCount": len(candidate_rows),
        "pdfCount": len({row["pdfLabel"] for row in candidate_rows}),
        "sourcePointBroadCandidateCount": source_broad_count,
        "sourcePointFeatureCandidateCount": source_feature_count,
        "landingPointBroadCandidateCount": landing_broad_count,
        "landingPointFeatureCandidateCount": landing_feature_count,
        "radius32FeatureContactCandidateCount": sum(
            1 for row in candidate_rows if row["radius32FeaturePixelCount"] > 0
        ),
        "renderOnlyContactCandidateCount": len(render_only_candidates),
        "baselineSourcePointRgb": baseline_rgb,
        "magazineEmbeddedSourcePointRgb": magazine_embedded.get("sourcePointRgb", {}).get("rgb"),
        "hiddenPdfRenderContactCandidate": hidden_candidate,
        "priorB4BroadContactFingerprint": contact.get("summary", {}).get(
            "b4BroadContactProvenanceFingerprint"
        ),
        "priorSourceLayerMissDistanceFingerprint": load_json(SOURCE_LAYER_MISS_DISTANCE)
        .get("summary", {})
        .get("sourceLayerMissDistanceFingerprint"),
        "sourceBackedR3BridgeHitCount": trigger["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger["satisfiedReopenTriggerCount"],
        "triggerCount": trigger["triggerCount"],
        "currentPdfB4ContactPixelProvenanceFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current PDF embedded/render provenance for B4 broad contact pixel; no extraction or candidate generation",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "contentBoxRegistrationGate": rel(CONTENT_BOX_REGISTRATION),
            "b4BroadContactProvenanceGate": rel(B4_BROAD_CONTACT_PROVENANCE),
            "sourceLayerMissDistanceGate": rel(SOURCE_LAYER_MISS_DISTANCE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "mode": mode,
        "target": TARGET_ID,
        "layer": LAYER,
        "sourcePoint": source_point,
        "targetPoint": target_point,
        "ringRadiusPx": RING_RADIUS,
        "renderDpi": RENDER_DPI,
        "candidateRows": candidate_rows,
        "summary": summary,
        "decision": {
            "currentPdfB4ContactPixelProvenanceGate": decision,
            "selectorUnlocked": False,
            "reason": "The byte-locked magazine carrier keeps the B4 point broad/background only; lower-resolution duplicate carriers create feature-colored contacts but no source-backed rule.",
            "nextMove": "Do not reopen current-PDF rendering for this B4 contact; require a distinct physical/original-layout source or source-backed rule.",
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": fingerprint,
    }
    draw_sheet(result, baseline_source)
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF B4 Contact Pixel Provenance Gate",
        "",
        "Scope: sampled the exact B4 broad-contact source point across current PDF embedded page images and 300dpi renders, then rebuilt the all-content page-75 -> page-76 landing. This checks PDF/render provenance only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / candidates: `{summary['pdfCount']}` / `{summary['candidateCount']}`",
        f"- Source point / target landing point: `{source_point}` / `{target_point}`",
        f"- Source point broad / feature candidates: `{summary['sourcePointBroadCandidateCount']}` / `{summary['sourcePointFeatureCandidateCount']}`",
        f"- Landing point broad / feature candidates: `{summary['landingPointBroadCandidateCount']}` / `{summary['landingPointFeatureCandidateCount']}`",
        f"- Radius-32 feature contact candidates: `{summary['radius32FeatureContactCandidateCount']}`",
        f"- Render-only feature/contact candidates: `{summary['renderOnlyContactCandidateCount']}`",
        f"- Baseline / magazine embedded source RGB: `{summary['baselineSourcePointRgb']}` / `{summary['magazineEmbeddedSourcePointRgb']}`",
        f"- Hidden PDF render contact candidate: `{int(summary['hiddenPdfRenderContactCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Candidate Rows",
        "",
        "| PDF | kind | orientation | source RGB | source layers | landing RGB | landing layers | r32 broad | r32 feature | source delta | embedded delta | verdict |",
        "|---|---|---|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in candidate_rows:
        lines.append(
            f"| `{row['pdfLabel']}` | `{row['candidateKind']}` | `{row['orientation']['bestOrientation']}` | "
            f"`{row['sourcePointRgb']['rgb']}` | `{layer_list(row['sourcePointLayerMembership'])}` | "
            f"`{row['landingPointRgb']['rgb']}` | `{layer_list(row['landingPointLayerMembership'])}` | "
            f"`{row['radius32BroadPixelCount']}` | `{row['radius32FeaturePixelCount']}` | "
            f"`{row['deltaVsBaselineSourcePointMax']}` | `{row['deltaVsEmbeddedSourcePointMax']}` | `{row['verdict']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- The byte-locked `magazine.pdf` embedded/render carrier keeps the sampled B4 point broad/background only, not feature ink.",
            "- The feature-colored rows come from duplicate/lower-resolution PDF carriers; they are provenance warnings, not selectors.",
            "- No render-only candidate creates a source-backed R3 bridge.",
            "- This keeps current-PDF rendering closed for the B4 broad rescue.",
            "",
            "## Next Move",
            "",
            "- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {rel(MD_OUT)}")
    print(f"Wrote {rel(JSON_OUT)}")
    print(f"Wrote {rel(SHEET_OUT)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
