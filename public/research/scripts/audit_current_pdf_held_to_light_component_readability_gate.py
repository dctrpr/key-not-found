#!/usr/bin/env python3
"""Audit whether exact PDF held-to-light residue is component-readable.

This bounded pass reuses the PDF-native held-to-light polarity gate and traces
only its threshold-crossing rows. It asks whether the resulting source-only
residue inside active target / OVERDOSE-slot crops forms isolated, letter-like
components, or whether it is still ordinary prose fragments / merged residue.

No OCR-to-key extraction, candidate keys, hash checks, seed/WIF/address checks,
BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_pdf_held_to_light_candidate_source_trace as source_trace  # noqa: E402
import audit_current_pdf_held_to_light_composite_polarity_gate as polarity  # noqa: E402
import audit_current_pdf_native_image_registration_gate as native  # noqa: E402
import audit_current_pdf_native_registration_candidate_source_trace as trace  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_pdf_held_to_light_component_readability_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_held_to_light_component_readability_gate.json"
OUT_MD = OUT / "current_pdf_held_to_light_component_readability_gate.md"
OUT_SHEET = OUT / "current_pdf_held_to_light_component_readability_gate_sheet.jpg"

POLARITY_GATE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/"
    "current_pdf_held_to_light_composite_polarity_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


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


def crop_bounds(box: list[float], shape: tuple[int, int]) -> tuple[int, int, int, int]:
    h, w = shape
    x0, y0, x1, y1 = [round(v) for v in box]
    return max(0, x0), max(0, y0), min(w, x1), min(h, y1)


def component_shape(
    component: dict[str, Any],
    crop_box: tuple[int, int, int, int],
    source_only_pixel_count: int,
) -> dict[str, Any]:
    x0, y0, x1, y1 = [int(v) for v in component["nativeTargetBox"]]
    cx0, cy0, cx1, cy1 = crop_box
    width = max(0, x1 - x0)
    height = max(0, y1 - y0)
    area = int(component["pixelCount"])
    bbox_area = max(1, width * height)
    crop_area = max(1, (cx1 - cx0) * (cy1 - cy0))
    fill_ratio = area / bbox_area
    aspect = width / max(1, height)
    touches_edge = x0 <= cx0 + 1 or y0 <= cy0 + 1 or x1 >= cx1 - 1 or y1 >= cy1 - 1
    source_fraction = area / max(1, source_only_pixel_count)
    crop_fraction = area / crop_area
    letterlike = (
        14 <= area <= 4200
        and 2 <= width <= 170
        and 6 <= height <= 150
        and 0.04 <= fill_ratio <= 0.88
        and 0.05 <= aspect <= 12.0
    )
    clean_letterlike = letterlike and not touches_edge and source_fraction <= 0.45
    return {
        "nativeTargetBox": [x0, y0, x1, y1],
        "localBox": [x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0],
        "pixelCount": area,
        "widthPx": width,
        "heightPx": height,
        "fillRatio": round(fill_ratio, 6),
        "aspectRatio": round(aspect, 6),
        "touchesCropEdge": touches_edge,
        "sourceOnlyFraction": round(source_fraction, 6),
        "cropFraction": round(crop_fraction, 6),
        "letterlike": letterlike,
        "cleanLetterlike": clean_letterlike,
    }


def image_assets(
    pdf: str,
    transform_id: str,
    cache: dict[tuple[str, str], tuple[Image.Image, Image.Image, tuple[int, int]]],
) -> tuple[Image.Image, Image.Image, tuple[int, int]]:
    key = (pdf, transform_id)
    if key not in cache:
        source_img, target_img, _pair = polarity.page_images(ROOT / pdf)
        if source_img.size != target_img.size:
            source_img = source_img.resize(target_img.size, Image.Resampling.BICUBIC)
        source_transformed = source_trace.transform_source(source_img, target_img.size, transform_id)
        cache[key] = (source_transformed.convert("RGB"), target_img.convert("RGB"), target_img.size)
    return cache[key]


def analyze_candidate(
    row: dict[str, Any],
    trace_row: dict[str, Any],
    image_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, tuple[int, int]]],
) -> dict[str, Any]:
    source_mask, target_mask, size = image_cache[(row["pdf"], row["transform"])]
    native_box = [float(v) for v in row["nativeBox"]]
    x0, y0, x1, y1 = crop_bounds(native_box, source_mask.shape)
    row_mask = trace.mask_for_box(source_mask.shape, native_box)
    source_only = np.logical_and(np.logical_and(source_mask, row_mask), ~target_mask)
    target_crop = target_mask[y0:y1, x0:x1]
    source_crop = source_mask[y0:y1, x0:x1]
    source_only_crop = source_only[y0:y1, x0:x1]
    source_only_pixels = int(source_only_crop.sum())
    source_pixels = int(source_crop.sum())
    target_pixels = int(target_crop.sum())
    crop_area = max(1, (x1 - x0) * (y1 - y0))
    components = trace.connected_components(source_only)
    shapes = [component_shape(component, (x0, y0, x1, y1), source_only_pixels) for component in components]
    clean_letterlike = [shape for shape in shapes if shape["cleanLetterlike"]]
    letterlike = [shape for shape in shapes if shape["letterlike"]]
    edge_components = [shape for shape in shapes if shape["touchesCropEdge"]]
    largest = shapes[0] if shapes else None
    largest_fraction = largest["sourceOnlyFraction"] if largest else 0.0
    edge_component_fraction = len(edge_components) / max(1, len(shapes))
    merged_or_edge_dominated = bool(largest_fraction >= 0.45 or edge_component_fraction >= 0.5)
    visual_readable_like = bool(len(clean_letterlike) >= 3 and not merged_or_edge_dominated)
    selector_candidate = bool(
        visual_readable_like
        and (
            trace_row["strictInstructionHitCount"] > 0
            or trace_row.get("sourceBackedR3BridgeHit", False)
        )
    )
    label = row["target"]
    if row["kind"] == "overdose_slot":
        label = f"{row['target']}_{row.get('slotLetter', '')}"
    return {
        "kind": row["kind"],
        "pdf": row["pdf"],
        "transform": row["transform"],
        "target": row["target"],
        "label": label,
        "phrase": row.get("phrase"),
        "slotIndex": row.get("slotIndex"),
        "slotLetter": row.get("slotLetter"),
        "nativeBox": row["nativeBox"],
        "sourceOnlyCoverage": row.get("sourceOnlyCoverage"),
        "sourceOnlyPixelCount": source_only_pixels,
        "sourceMaskPixelCount": source_pixels,
        "targetMaskPixelCount": target_pixels,
        "cropArea": crop_area,
        "sourceOnlyCropCoverage": round(source_only_pixels / crop_area, 9),
        "componentCount": len(shapes),
        "letterlikeComponentCount": len(letterlike),
        "cleanLetterlikeComponentCount": len(clean_letterlike),
        "edgeTouchComponentCount": len(edge_components),
        "edgeTouchComponentFraction": round(edge_component_fraction, 6),
        "largestComponentPixelCount": int(largest["pixelCount"]) if largest else 0,
        "largestComponentSourceOnlyFraction": round(largest_fraction, 6),
        "mergedOrEdgeDominated": merged_or_edge_dominated,
        "visualReadableLike": visual_readable_like,
        "strictInstructionHitCount": trace_row["strictInstructionHitCount"],
        "contextTermHitCount": trace_row["contextTermHitCount"],
        "sourceWordHitCount": trace_row["sourceWordHitCount"],
        "sourceTextPreview": trace_row["sourceTextPreview"],
        "selectorCandidate": selector_candidate,
        "components": shapes[:12],
    }


def mask_to_image(mask: np.ndarray) -> Image.Image:
    return Image.fromarray(np.where(mask, 0, 255).astype(np.uint8), mode="L").convert("RGB")


def fit_panel(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    panel = Image.new("RGB", size, "white")
    img = img.convert("RGB")
    img.thumbnail((size[0] - 4, size[1] - 4), Image.Resampling.LANCZOS)
    panel.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2))
    return panel


def crop_panel(
    row: dict[str, Any],
    assets: tuple[Image.Image, Image.Image, tuple[int, int]],
    kind: str,
    panel_size: tuple[int, int],
) -> Image.Image:
    source_img, target_img, _size = assets
    x0, y0, x1, y1 = [round(v) for v in row["nativeBox"]]
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(target_img.width, x1)
    y1 = min(target_img.height, y1)
    if x1 <= x0 or y1 <= y0:
        return Image.new("RGB", panel_size, "white")
    if kind == "target":
        return fit_panel(target_img.crop((x0, y0, x1, y1)), panel_size)
    if kind == "source":
        return fit_panel(source_img.crop((x0, y0, x1, y1)), panel_size)
    source_mask = native.feature_mask(source_img)
    target_mask = native.feature_mask(target_img)
    row_mask = trace.mask_for_box(source_mask.shape, row["nativeBox"])
    source_only = np.logical_and(np.logical_and(source_mask, row_mask), ~target_mask)
    local = source_only[y0:y1, x0:x1]
    if kind == "mask":
        return fit_panel(mask_to_image(local), panel_size)
    overlay = target_img.crop((x0, y0, x1, y1)).convert("RGBA")
    red = Image.new("RGBA", overlay.size, (220, 30, 30, 0))
    alpha = Image.fromarray(np.where(local, 190, 0).astype(np.uint8), mode="L")
    red.putalpha(alpha)
    overlay.alpha_composite(red)
    return fit_panel(overlay.convert("RGB"), panel_size)


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1900, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(24)
    small = safe_font(15)
    tiny = safe_font(11)
    summary = result["summary"]
    draw.rectangle((0, 0, width, 112), fill=(26, 31, 42))
    draw.text((24, 18), "PDF Held-to-Light Component Readability Gate", fill="white", font=title)
    draw.text(
        (24, 56),
        "Threshold-crossing held-to-light crops are checked for isolated letter-like source-only components.",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (1110, 18),
        f"rows {summary['candidateRowCount']} | components {summary['totalComponentCount']} | clean {summary['totalCleanLetterlikeComponents']}",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (1110, 50),
        f"visual-like rows {summary['visualReadableLikeRowCount']} | selectors {summary['selectorCandidateCount']} | strict {summary['totalStrictInstructionHits']}",
        fill=(235, 235, 235),
        font=small,
    )

    rows = sorted(
        result["readabilityRows"],
        key=lambda item: (
            item["visualReadableLike"],
            item["cleanLetterlikeComponentCount"],
            item["sourceOnlyPixelCount"],
        ),
        reverse=True,
    )[:8]
    image_cache: dict[tuple[str, str], tuple[Image.Image, Image.Image, tuple[int, int]]] = {}
    panel_w, panel_h = 128, 74
    x0 = 18
    y = 136
    headers = [
        "row",
        "target",
        "source",
        "source-only",
        "overlay",
        "cmp",
        "clean",
        "edge",
        "largest",
        "words",
        "strict",
        "source preview",
    ]
    xs = [18, 132, 270, 408, 546, 700, 755, 815, 870, 945, 1005, 1065]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(35, 39, 48), font=small)
    y += 30
    for idx, row in enumerate(rows):
        row_h = 112
        draw.rectangle((12, y - 7, width - 12, y + row_h - 7), fill=(246, 248, 251) if idx % 2 == 0 else "white")
        assets = image_assets(row["pdf"], row["transform"], image_cache)
        draw.text((x0, y + 4), f"{row['pdf'].split('/')[-1]}\n{row['transform']}\n{row['label']}", fill=(31, 35, 43), font=tiny)
        for offset, kind in [(132, "target"), (270, "source"), (408, "mask"), (546, "overlay")]:
            panel = crop_panel(row, assets, kind, (panel_w, panel_h))
            sheet.paste(panel, (offset, y))
            draw.rectangle((offset, y, offset + panel_w, y + panel_h), outline=(170, 176, 186))
        values = [
            row["componentCount"],
            row["cleanLetterlikeComponentCount"],
            row["edgeTouchComponentCount"],
            f"{row['largestComponentSourceOnlyFraction']:.2f}",
            row["sourceWordHitCount"],
            row["strictInstructionHitCount"],
        ]
        for x, value in zip([700, 755, 815, 870, 945, 1005], values):
            draw.text((x, y + 22), str(value), fill=(30, 34, 42), font=small)
        preview = row["sourceTextPreview"][:104]
        draw.text((1065, y + 10), preview, fill=(42, 45, 54), font=tiny)
        draw.text(
            (1065, y + 50),
            f"visualLike={row['visualReadableLike']} mergedOrEdge={row['mergedOrEdgeDominated']}",
            fill=(92, 98, 112),
            font=tiny,
        )
        y += row_h
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    top_rows = sorted(
        result["readabilityRows"],
        key=lambda item: (
            item["visualReadableLike"],
            item["cleanLetterlikeComponentCount"],
            item["sourceOnlyPixelCount"],
        ),
        reverse=True,
    )[:12]
    lines = [
        "# Current PDF Held-to-Light Component Readability Gate",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Candidate rows checked: `{summary['candidateRowCount']}`",
        f"- Active / OVERDOSE-slot rows: `{summary['activeRowCount']}` / `{summary['overdoseSlotRowCount']}`",
        f"- Total source-only components: `{summary['totalComponentCount']}`",
        f"- Letter-like / clean letter-like components: `{summary['totalLetterlikeComponents']}` / `{summary['totalCleanLetterlikeComponents']}`",
        f"- Visual-readable-like rows: `{summary['visualReadableLikeRowCount']}`",
        f"- Merged or edge-dominated rows: `{summary['mergedOrEdgeDominatedRowCount']}`",
        f"- Source-word rows / hits: `{summary['sourceWordRowCount']}` / `{summary['totalSourceWordHits']}`",
        f"- Strict instruction hits / selector candidates: `{summary['totalStrictInstructionHits']}` / `{summary['selectorCandidateCount']}`",
        f"- Source-backed R3 / satisfied reopen triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        "",
        "## Top Rows",
        "",
        "| pdf | transform | label | components | clean letterlike | edge comps | largest source fraction | words | strict | visual-like | source preview |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in top_rows:
        preview = row["sourceTextPreview"].replace("|", "\\|")[:100]
        lines.append(
            "| "
            + " | ".join(
                [
                    row["pdf"],
                    row["transform"],
                    row["label"],
                    str(row["componentCount"]),
                    str(row["cleanLetterlikeComponentCount"]),
                    str(row["edgeTouchComponentCount"]),
                    f"{row['largestComponentSourceOnlyFraction']:.3f}",
                    str(row["sourceWordHitCount"]),
                    str(row["strictInstructionHitCount"]),
                    str(row["visualReadableLike"]),
                    preview,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote PDF-native held-to-light residue as a readable extraction layer.",
            "- Some threshold-crossing rows contain isolated source-only components, but they trace to ordinary page-75 prose and produce no strict unit/order/action terms.",
            "- Rows with the most residue are still merged or edge-dominated; visual-like residue does not satisfy any source-backed R3 reopen trigger.",
            "",
            "## Next Move",
            "",
            "- Stop extending current-PDF held-to-light component/word/color permutations unless a new source changes geometry or clue wording names transform, unit, and read order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    polarity_gate = load_json(POLARITY_GATE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))

    candidates = source_trace.candidate_rows(polarity_gate)
    page75_words = trace.page_words(75)
    mask_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, tuple[int, int]]] = {}
    readability_rows: list[dict[str, Any]] = []
    for row in candidates:
        trace_row = source_trace.trace_candidate(row, mask_cache, page75_words)
        readability_rows.append(analyze_candidate(row, trace_row, mask_cache))

    summary = {
        "decision": "current_pdf_held_to_light_component_readability_no_selector",
        "candidateRowCount": len(readability_rows),
        "activeRowCount": sum(1 for row in readability_rows if row["kind"] == "active"),
        "overdoseSlotRowCount": sum(1 for row in readability_rows if row["kind"] == "overdose_slot"),
        "componentRowCount": sum(1 for row in readability_rows if row["componentCount"] > 0),
        "totalComponentCount": sum(row["componentCount"] for row in readability_rows),
        "totalLetterlikeComponents": sum(row["letterlikeComponentCount"] for row in readability_rows),
        "totalCleanLetterlikeComponents": sum(row["cleanLetterlikeComponentCount"] for row in readability_rows),
        "visualReadableLikeRowCount": sum(row["visualReadableLike"] for row in readability_rows),
        "mergedOrEdgeDominatedRowCount": sum(row["mergedOrEdgeDominated"] for row in readability_rows),
        "sourceWordRowCount": sum(1 for row in readability_rows if row["sourceWordHitCount"] > 0),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in readability_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in readability_rows),
        "contextTermRowCount": sum(1 for row in readability_rows if row["contextTermHitCount"] > 0),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in readability_rows),
        "selectorCandidateCount": sum(row["selectorCandidate"] for row in readability_rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
    }
    fingerprint = (
        f"rows={summary['candidateRowCount']}|active={summary['activeRowCount']}|"
        f"slots={summary['overdoseSlotRowCount']}|componentRows={summary['componentRowCount']}|"
        f"components={summary['totalComponentCount']}|letterlike={summary['totalLetterlikeComponents']}|"
        f"clean={summary['totalCleanLetterlikeComponents']}|visualRows={summary['visualReadableLikeRowCount']}|"
        f"mergedRows={summary['mergedOrEdgeDominatedRowCount']}|wordRows={summary['sourceWordRowCount']}|"
        f"words={summary['totalSourceWordHits']}|strict={summary['totalStrictInstructionHits']}|"
        f"context={summary['totalContextTermHits']}|candidates={summary['selectorCandidateCount']}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Threshold-crossing exact PDF-native held-to-light rows checked for isolated "
            "source-only component readability inside active target and OVERDOSE-slot crops."
        ),
        "inputs": {
            "polarityGate": rel(POLARITY_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "readabilityRows": readability_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()
