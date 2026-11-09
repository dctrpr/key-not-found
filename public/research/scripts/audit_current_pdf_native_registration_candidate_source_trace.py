#!/usr/bin/env python3
"""Trace exact PDF-native registration candidate pixels back to page 75.

The native image registration gate found only a narrow anomaly: in the two
low-resolution duplicate PDFs, O4 and projected OVERDOSE slot0 cross local
coverage thresholds under exact embedded-image registration. This pass maps
only those candidate pixels back through the physical page 75 -> page 76 mirror
to page-75 OCR/source words.

No OCR-to-key extraction, key candidates, hashing, seed/WIF/address checks,
BIP39, or brute force is run.
"""

from __future__ import annotations

import json
import sys
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_pdf_native_image_registration_gate as native  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_pdf_native_registration_candidate_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_native_registration_candidate_source_trace.json"
OUT_MD = OUT / "current_pdf_native_registration_candidate_source_trace.md"
OUT_SHEET = OUT / "current_pdf_native_registration_candidate_source_trace_sheet.jpg"

NATIVE_GATE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_native_image_registration_gate/"
    "current_pdf_native_image_registration_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

REFERENCE_SIZE = (2544.0, 3264.0)
TRACE_PAD_REF = 42.0
COMPONENT_LIMIT = 16
MIN_COMPONENT_PIXELS = 24

STRICT_TERMS = {
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
    "words",
}
CONTEXT_TERMS = {
    "bitcoin",
    "bond",
    "bonds",
    "bukele",
    "buterin",
    "dip",
    "heart",
    "imf",
    "satoshi",
    "sell",
    "shitcoiner",
    "shitcoinery",
    "vitalik",
    "volcano",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def token(text: str) -> str:
    return "".join(ch.lower() for ch in str(text) if ch.isalnum())


def page_words(page: int) -> list[dict[str, Any]]:
    article = load_json(ARTICLE_MAP)
    for page_row in article.get("pages", []):
        if page_row.get("page") == page:
            words = []
            for word in page_row.get("words", []):
                tok = token(word.get("token") or word.get("text") or "")
                if not tok:
                    continue
                words.append(
                    {
                        "text": word.get("text", ""),
                        "token": tok,
                        "box": [float(v) for v in word["box"]],
                        "index": word.get("index"),
                        "strictInstruction": tok in STRICT_TERMS,
                        "contextTerm": tok in CONTEXT_TERMS,
                    }
                )
            return words
    return []


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def words_for_box(words: list[dict[str, Any]], box: list[float] | None) -> list[dict[str, Any]]:
    if not box:
        return []
    return [word for word in words if boxes_intersect(word["box"], box)]


def mask_for_box(shape: tuple[int, int], box: list[float]) -> np.ndarray:
    h, w = shape
    x0, y0, x1, y1 = [round(v) for v in box]
    mask = np.zeros((h, w), dtype=bool)
    mask[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = True
    return mask


def connected_components(mask: np.ndarray, limit: int = COMPONENT_LIMIT) -> list[dict[str, Any]]:
    visited = np.zeros(mask.shape, dtype=bool)
    ys, xs = np.where(mask)
    h, w = mask.shape
    components: list[dict[str, Any]] = []
    for start_y, start_x in zip(ys.tolist(), xs.tolist()):
        if visited[start_y, start_x]:
            continue
        queue: deque[tuple[int, int]] = deque([(start_y, start_x)])
        visited[start_y, start_x] = True
        count = 0
        min_x = max_x = start_x
        min_y = max_y = start_y
        while queue:
            y, x = queue.popleft()
            count += 1
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            for ny in range(max(0, y - 1), min(h, y + 2)):
                for nx in range(max(0, x - 1), min(w, x + 2)):
                    if not visited[ny, nx] and mask[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        if count >= MIN_COMPONENT_PIXELS:
            components.append(
                {
                    "pixelCount": count,
                    "nativeTargetBox": [min_x, min_y, max_x + 1, max_y + 1],
                }
            )
    components.sort(key=lambda row: row["pixelCount"], reverse=True)
    return components[:limit]


def native_target_box_to_source_ref(box: list[int], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = box
    source_native = [width - x1, y0, width - x0, y1]
    sx = REFERENCE_SIZE[0] / width
    sy = REFERENCE_SIZE[1] / height
    return [
        source_native[0] * sx,
        source_native[1] * sy,
        source_native[2] * sx,
        source_native[3] * sy,
    ]


def union_box(boxes: list[list[float]]) -> list[float] | None:
    if not boxes:
        return None
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def padded_ref_box(box: list[float] | None) -> list[float] | None:
    if not box:
        return None
    return [
        max(0.0, box[0] - TRACE_PAD_REF),
        max(0.0, box[1] - TRACE_PAD_REF),
        min(REFERENCE_SIZE[0], box[2] + TRACE_PAD_REF),
        min(REFERENCE_SIZE[1], box[3] + TRACE_PAD_REF),
    ]


def candidate_rows(native_gate: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for pdf_row in native_gate.get("pdfRows", []):
        for row in pdf_row.get("activeRows", []):
            if row.get("isAboveControlP95") or row.get("isAtLeast10") or row.get("isAtLeast25"):
                rows.append({"kind": "active", "pdf": pdf_row["pdf"], **row})
        for row in pdf_row.get("slotRows", []):
            if row.get("isAtLeast25"):
                rows.append({"kind": "overdose_slot", "pdf": pdf_row["pdf"], **row})
    return rows


def page_images(pdf_path: Path) -> tuple[Image.Image, Image.Image, tuple[int, int]]:
    with fitz.open(pdf_path) as doc:
        page75 = native.page_record(doc, pdf_path, 2, 75)
        page76 = native.page_record(doc, pdf_path, 3, 76)
    source = page75.pop("image")
    target = page76.pop("image")
    if source.size != target.size:
        source = source.resize(target.size, Image.Resampling.BICUBIC)
    return source, target, target.size


def trace_candidate(row: dict[str, Any], page75_words: list[dict[str, Any]]) -> dict[str, Any]:
    pdf_path = ROOT / row["pdf"]
    source_img, target_img, size = page_images(pdf_path)
    width, height = size
    source_mirror = native.feature_mask(ImageOps.mirror(source_img))
    target_feature = native.feature_mask(target_img)
    native_box = [float(v) for v in row["nativeBox"]]
    source_only = np.logical_and(
        np.logical_and(source_mirror, mask_for_box(source_mirror.shape, native_box)),
        ~target_feature,
    )
    components = connected_components(source_only)
    component_source_ref_boxes = [
        native_target_box_to_source_ref(component["nativeTargetBox"], width, height)
        for component in components
    ]
    source_ref_box = padded_ref_box(union_box(component_source_ref_boxes))
    words = words_for_box(page75_words, source_ref_box)
    strict_words = [word for word in words if word["strictInstruction"]]
    context_words = [word for word in words if word["contextTerm"]]
    area = max(0.0, native_box[2] - native_box[0]) * max(0.0, native_box[3] - native_box[1])
    label = row["target"]
    if row["kind"] == "overdose_slot":
        label = f"{row['target']}_{row.get('slotLetter', '')}"
    return {
        "kind": row["kind"],
        "pdf": row["pdf"],
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
        "sourceTextPreview": " ".join(word["text"] for word in words[:32]),
        "sourceWords": words[:48],
    }


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
    width, height = 1780, 980
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(15)
    tiny = font(12)
    summary = result["summary"]
    draw.rectangle((0, 0, width, 98), fill=(24, 31, 42))
    draw.text((24, 16), "PDF Native Registration Candidate Source Trace", fill="white", font=title)
    draw.text(
        (24, 54),
        "Only threshold-crossing exact-native rows are traced back to page 75 source words.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (980, 18),
        f"decision: {result['decision']} | candidates {summary['candidateTraceRowCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (980, 46),
        f"strict rows {summary['strictInstructionRowCount']} | context rows {summary['contextTermRowCount']} | words {summary['totalSourceWordHits']}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 124
    headers = ["PDF", "kind", "target", "coverage", "components", "words", "strict", "context", "source preview"]
    xs = [24, 470, 585, 690, 790, 905, 985, 1060, 1160]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(40, 43, 50), font=small)
    y += 30
    for idx, row in enumerate(result["traceRows"]):
        draw.rectangle((16, y - 6, width - 16, y + 42), fill=(245, 247, 250) if idx % 2 == 0 else (255, 255, 255))
        values = [
            row["pdf"],
            row["kind"],
            row["label"],
            f"{row['recomputedSourceOnlyCoverage']:.4f}",
            str(row["componentCount"]),
            str(row["sourceWordHitCount"]),
            str(row["strictInstructionHitCount"]),
            str(row["contextTermHitCount"]),
            row["sourceTextPreview"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:70], fill=(25, 28, 34), font=tiny)
        y += 54
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    native_gate = load_json(NATIVE_GATE)
    page75_words = page_words(75)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row
        for row in trigger_rows
        if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(
        source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    )

    candidates = candidate_rows(native_gate)
    trace_rows = [trace_candidate(row, page75_words) for row in candidates]
    strict_rows = [row for row in trace_rows if row["strictInstructionHitCount"]]
    context_rows = [row for row in trace_rows if row["contextTermHitCount"]]
    active_rows = [row for row in trace_rows if row["kind"] == "active"]
    slot_rows = [row for row in trace_rows if row["kind"] == "overdose_slot"]
    decision = "current_pdf_native_registration_candidate_trace_no_instruction_source"
    fingerprint = (
        f"rows={len(trace_rows)}|active={len(active_rows)}|slots={len(slot_rows)}|"
        f"components={sum(row['componentCount'] for row in trace_rows)}|"
        f"pixels={sum(row['componentPixelCount'] for row in trace_rows)}|"
        f"sourceOnly={sum(row['sourceOnlyPixelCount'] for row in trace_rows)}|"
        f"wordRows={sum(1 for row in trace_rows if row['sourceWordHitCount'])}|"
        f"words={sum(row['sourceWordHitCount'] for row in trace_rows)}|"
        f"strictRows={len(strict_rows)}|strict={sum(row['strictInstructionHitCount'] for row in trace_rows)}|"
        f"contextRows={len(context_rows)}|context={sum(row['contextTermHitCount'] for row in trace_rows)}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary = {
        "candidateTraceRowCount": len(trace_rows),
        "activeTraceRowCount": len(active_rows),
        "overdoseSlotTraceRowCount": len(slot_rows),
        "totalComponentCount": sum(row["componentCount"] for row in trace_rows),
        "totalComponentPixelCount": sum(row["componentPixelCount"] for row in trace_rows),
        "totalSourceOnlyPixelCount": sum(row["sourceOnlyPixelCount"] for row in trace_rows),
        "sourceWordRowCount": sum(1 for row in trace_rows if row["sourceWordHitCount"]),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in trace_rows),
        "strictInstructionRowCount": len(strict_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in trace_rows),
        "contextTermRowCount": len(context_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in trace_rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
        "fingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Trace only exact PDF-native registration rows that crossed candidate thresholds back to page 75 source words.",
        "inputs": {
            "nativeRegistrationGate": rel(NATIVE_GATE),
            "articleMap": rel(ARTICLE_MAP),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": decision,
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF Native Registration Candidate Source Trace",
        "",
        "Scope: traced only the exact-native registration rows that crossed candidate thresholds in the previous gate. This is provenance review only: no key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{decision}`",
        f"- Candidate trace rows / active / projected OVERDOSE slots: `{len(trace_rows)}` / `{len(active_rows)}` / `{len(slot_rows)}`",
        f"- Components / component pixels / source-only pixels: `{summary['totalComponentCount']}` / `{summary['totalComponentPixelCount']}` / `{summary['totalSourceOnlyPixelCount']}`",
        f"- Source-word rows / source-word hits: `{summary['sourceWordRowCount']}` / `{summary['totalSourceWordHits']}`",
        f"- Strict instruction rows / hits: `{summary['strictInstructionRowCount']}` / `{summary['totalStrictInstructionHits']}`",
        f"- Context rows / hits: `{summary['contextTermRowCount']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{len(satisfied_triggers)}/{len(trigger_rows)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Trace Rows",
        "",
        "| PDF | kind | target | coverage | components | source words | strict | context | source preview |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in trace_rows:
        lines.append(
            "| "
            f"`{row['pdf']}` | `{row['kind']}` | `{row['label']}` | "
            f"{row['recomputedSourceOnlyCoverage']:.4f} | "
            f"{row['componentCount']} | {row['sourceWordHitCount']} | "
            f"{row['strictInstructionHitCount']} | {row['contextTermHitCount']} | "
            f"{row['sourceTextPreview']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- Do not promote the low-resolution duplicate PDF O4/slot0 native-registration spike as a selector.",
            "- The threshold-crossing pixels trace to ordinary page-75 prose/context rather than source-side unit/order wording, and the spike remains duplicate-only and non-quartet.",
            "- Next move: require distinct physical/original-layout source material or raw clue wording that explicitly names transform, unit, and order before reopening selector/key checks.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
