#!/usr/bin/env python3
"""Trace PDF-native held-to-light composite candidate pixels to page-75 words.

This bounded pass follows only the threshold-crossing rows from the exact
PDF-native held-to-light composite polarity gate. It maps source-only pixels
back through the tested orientation transform to page-75 source words.

It does not derive keys, hashes, seed phrases, WIFs, addresses, BIP39 checks,
or broad candidate material.
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
import audit_current_pdf_held_to_light_composite_polarity_gate as polarity  # noqa: E402
import audit_current_pdf_native_image_registration_gate as native  # noqa: E402
import audit_current_pdf_native_registration_candidate_source_trace as trace  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_pdf_held_to_light_candidate_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_held_to_light_candidate_source_trace.json"
OUT_MD = OUT / "current_pdf_held_to_light_candidate_source_trace.md"
OUT_SHEET = OUT / "current_pdf_held_to_light_candidate_source_trace_sheet.jpg"

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

REFERENCE_SIZE = (2544.0, 3264.0)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def inverse_transform_box(box: list[int], width: int, height: int, transform_id: str) -> list[float]:
    x0, y0, x1, y1 = [float(v) for v in box]
    if transform_id == "physical_back_mirror":
        return [width - x1, y0, width - x0, y1]
    if transform_id == "same_side_no_mirror":
        return [x0, y0, x1, y1]
    if transform_id == "back_mirror_rotate180":
        return [x0, height - y1, x1, height - y0]
    if transform_id == "front_rotate180":
        return [width - x1, height - y1, width - x0, height - y0]
    raise ValueError(f"unknown transform: {transform_id}")


def source_native_box_to_ref(box: list[float], width: int, height: int) -> list[float]:
    sx = REFERENCE_SIZE[0] / width
    sy = REFERENCE_SIZE[1] / height
    return [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy]


def candidate_rows(polarity_gate: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for variant in polarity_gate.get("variantRows", []):
        base = {
            "pdf": variant["pdf"],
            "transform": variant["transform"],
            "transformDescription": variant.get("transformDescription"),
        }
        for row in variant.get("activeRows", []):
            if row.get("isAtLeast10") or row.get("isAboveControlP95") or row.get("isCleanThrough10"):
                rows.append({"kind": "active", **base, **row})
        for row in variant.get("slotRows", []):
            if row.get("isAtLeast25"):
                rows.append({"kind": "overdose_slot", **base, **row})
    rows.sort(
        key=lambda row: (
            row["pdf"],
            row["transform"],
            row["kind"],
            row.get("slotIndex", 99),
            row.get("target", ""),
        )
    )
    return rows


def page_images(pdf: str) -> tuple[Any, Any, tuple[int, int]]:
    source_img, target_img, _pair = polarity.page_images(ROOT / pdf)
    if source_img.size != target_img.size:
        source_img = source_img.resize(target_img.size, Image.Resampling.BICUBIC)
    return source_img, target_img, target_img.size


def transform_source(source_img: Any, target_size: tuple[int, int], transform_id: str) -> Any:
    transform = next(item[2] for item in polarity.TRANSFORMS if item[0] == transform_id)
    transformed = transform(source_img).convert("RGB")
    if transformed.size != target_size:
        transformed = transformed.resize(target_size, Image.Resampling.BICUBIC)
    return transformed


def trace_candidate(
    row: dict[str, Any],
    image_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, tuple[int, int]]],
    page75_words: list[dict[str, Any]],
) -> dict[str, Any]:
    cache_key = (row["pdf"], row["transform"])
    if cache_key not in image_cache:
        source_img, target_img, size = page_images(row["pdf"])
        source_transformed = transform_source(source_img, size, row["transform"])
        image_cache[cache_key] = (
            native.feature_mask(source_transformed),
            native.feature_mask(target_img),
            size,
        )
    source_mask, target_mask, size = image_cache[cache_key]
    width, height = size
    native_box = [float(v) for v in row["nativeBox"]]
    row_mask = trace.mask_for_box(source_mask.shape, native_box)
    source_only = np.logical_and(np.logical_and(source_mask, row_mask), ~target_mask)
    components = trace.connected_components(source_only)
    component_source_ref_boxes = []
    for component in components:
        source_native = inverse_transform_box(
            component["nativeTargetBox"], width, height, row["transform"]
        )
        component_source_ref_boxes.append(source_native_box_to_ref(source_native, width, height))
    source_ref_box = trace.padded_ref_box(trace.union_box(component_source_ref_boxes))
    words = trace.words_for_box(page75_words, source_ref_box)
    strict_words = [word for word in words if word["strictInstruction"]]
    context_words = [word for word in words if word["contextTerm"]]
    area = max(0.0, native_box[2] - native_box[0]) * max(0.0, native_box[3] - native_box[1])
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
        "referenceBox": row.get("referenceBox"),
        "nativeBox": row.get("nativeBox"),
        "sourceOnlyCoverage": row.get("sourceOnlyCoverage"),
        "recomputedSourceOnlyCoverage": round(float(source_only.sum() / area), 9) if area else 0.0,
        "sourceOnlyPixelCount": int(source_only.sum()),
        "componentCount": len(components),
        "componentPixelCount": int(sum(component["pixelCount"] for component in components)),
        "largestComponentPixelCount": components[0]["pixelCount"] if components else 0,
        "componentSourceRefBoxes": component_source_ref_boxes,
        "sourceTraceRefBox": source_ref_box,
        "sourceWordHitCount": len(words),
        "strictInstructionHitCount": len(strict_words),
        "contextTermHitCount": len(context_words),
        "strictInstructionTerms": sorted({word["token"] for word in strict_words}),
        "contextTerms": sorted({word["token"] for word in context_words}),
        "sourceTextPreview": " ".join(word["text"] for word in words[:34]),
        "sourceWords": words[:56],
    }


def unique_trace_shape_count(rows: list[dict[str, Any]]) -> int:
    keys = set()
    for row in rows:
        box = row.get("sourceTraceRefBox")
        rounded_box = tuple(round(float(v), 1) for v in box) if box else ()
        keys.add(
            (
                row["transform"],
                row["kind"],
                row["target"],
                rounded_box,
                row["sourceTextPreview"][:80],
            )
        )
    return len(keys)


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


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1780, 1180
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(15)
    tiny = font(11)
    summary = result["summary"]
    draw.rectangle((0, 0, width, 100), fill=(24, 31, 42))
    draw.text((24, 16), "PDF Held-to-Light Candidate Source Trace", fill="white", font=title)
    draw.text(
        (24, 54),
        "Only threshold-crossing composite rows are traced through their orientation transform to page-75 source words.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (990, 18),
        f"candidates {summary['candidateTraceRowCount']} | unique {summary['uniqueTraceShapeCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (990, 48),
        f"strict rows {summary['strictInstructionRowCount']} | context rows {summary['contextTermRowCount']} | sourceR3 {summary['sourceBackedR3BridgeHitCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 124
    headers = ["PDF", "transform", "kind", "target", "cov", "cmp", "words", "strict", "ctx", "source preview"]
    xs = [20, 315, 505, 615, 705, 775, 835, 900, 960, 1015]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(40, 43, 50), font=small)
    y += 28
    for idx, row in enumerate(result["traceRows"][:32]):
        draw.rectangle((14, y - 5, width - 14, y + 38), fill=(245, 247, 250) if idx % 2 == 0 else (255, 255, 255))
        values = [
            row["pdf"],
            row["transform"],
            row["kind"],
            row["label"],
            f"{row['recomputedSourceOnlyCoverage']:.3f}",
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            str(row["contextTermHitCount"]),
            row["sourceTextPreview"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:82], fill=(25, 28, 34), font=tiny)
        y += 45
        if y > height - 46:
            break
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Held-to-Light Candidate Source Trace",
        "",
        "Scope: traced only threshold-crossing rows from the exact PDF-native held-to-light composite polarity gate back through their orientation transform to page-75 source words. No key derivation, hashes, seed/WIF/address checks, BIP39, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Candidate trace rows / active / OVERDOSE slots: `{summary['candidateTraceRowCount']}` / `{summary['activeTraceRowCount']}` / `{summary['overdoseSlotTraceRowCount']}`",
        f"- Unique trace shapes: `{summary['uniqueTraceShapeCount']}`",
        f"- Source-word rows / source-word hits: `{summary['sourceWordRowCount']}` / `{summary['totalSourceWordHits']}`",
        f"- Strict instruction rows / hits: `{summary['strictInstructionRowCount']}` / `{summary['totalStrictInstructionHits']}`",
        f"- Context rows / hits: `{summary['contextTermRowCount']}` / `{summary['totalContextTermHits']}`",
        f"- Component rows / components / source-only pixels: `{summary['componentRowCount']}` / `{summary['totalComponentCount']}` / `{summary['totalSourceOnlyPixelCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Trace Rows",
        "",
        "| PDF | transform | kind | target | coverage | components | words | strict | context | source preview |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in result["traceRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    f"`{row['transform']}`",
                    f"`{row['kind']}`",
                    f"`{row['label']}`",
                    f"{row['recomputedSourceOnlyCoverage']:.4f}",
                    str(row["componentCount"]),
                    str(row["sourceWordHitCount"]),
                    str(row["strictInstructionHitCount"]),
                    str(row["contextTermHitCount"]),
                    row["sourceTextPreview"].replace("|", "\\|")[:160],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote derivative PDF held-to-light composite hits as selectors.",
            "- Threshold-crossing rows trace to ordinary page-75 prose, blank/no-word regions, or broad rotated/mirrored slices; they do not expose source-backed unit/order instructions.",
            "- The apparent hits remain derivative-only, non-quartet, and control-dominated; source-backed R3 and reopen triggers remain absent.",
            "",
            "## Next Move",
            "",
            "- Stop tracing local derivative held-to-light hits unless a new source materially changes the page geometry. The best next move remains external/original-layout source validation or raw clue wording that names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    polarity_gate = load_json(POLARITY_GATE)
    page75_words = trace.page_words(75)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    candidates = candidate_rows(polarity_gate)
    image_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, tuple[int, int]]] = {}
    trace_rows = [trace_candidate(row, image_cache, page75_words) for row in candidates]

    summary = {
        "decision": "current_pdf_held_to_light_candidate_trace_no_instruction_source",
        "candidateTraceRowCount": len(trace_rows),
        "activeTraceRowCount": sum(1 for row in trace_rows if row["kind"] == "active"),
        "overdoseSlotTraceRowCount": sum(1 for row in trace_rows if row["kind"] == "overdose_slot"),
        "uniqueTraceShapeCount": unique_trace_shape_count(trace_rows),
        "componentRowCount": sum(1 for row in trace_rows if row["componentCount"] > 0),
        "totalComponentCount": sum(row["componentCount"] for row in trace_rows),
        "totalComponentPixelCount": sum(row["componentPixelCount"] for row in trace_rows),
        "totalSourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in trace_rows),
        "sourceWordRowCount": sum(1 for row in trace_rows if row["sourceWordHitCount"] > 0),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in trace_rows),
        "strictInstructionRowCount": sum(1 for row in trace_rows if row["strictInstructionHitCount"] > 0),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in trace_rows),
        "contextTermRowCount": sum(1 for row in trace_rows if row["contextTermHitCount"] > 0),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in trace_rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"rows={summary['candidateTraceRowCount']}|active={summary['activeTraceRowCount']}|"
        f"slots={summary['overdoseSlotTraceRowCount']}|unique={summary['uniqueTraceShapeCount']}|"
        f"componentRows={summary['componentRowCount']}|components={summary['totalComponentCount']}|"
        f"sourceOnly={summary['totalSourceOnlyPixelCount']}|wordRows={summary['sourceWordRowCount']}|"
        f"words={summary['totalSourceWordHits']}|strictRows={summary['strictInstructionRowCount']}|"
        f"strict={summary['totalStrictInstructionHits']}|contextRows={summary['contextTermRowCount']}|"
        f"context={summary['totalContextTermHits']}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Threshold-crossing exact PDF-native held-to-light composite rows traced back through orientation transforms to page-75 source words.",
        "inputs": {
            "polarityGate": rel(POLARITY_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
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
