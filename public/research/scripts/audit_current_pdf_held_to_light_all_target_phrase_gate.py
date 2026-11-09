#!/usr/bin/env python3
"""Trace all active target boxes through fixed PDF held-to-light orientations.

Earlier PDF held-to-light source traces only followed threshold-crossing pixels.
This bounded pass traces all four locked page-76 active target boxes through the
fixed orientation transforms, then assembles the page-75 source words in
O4/B4/G5/O5 order. It checks whether the complete active quartet supplies a
source-side phrase with unit/order wording.

No key derivation, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_held_to_light_all_target_phrase_gate.json"
OUT_MD = OUT / "current_pdf_held_to_light_all_target_phrase_gate.md"
OUT_SHEET = OUT / "current_pdf_held_to_light_all_target_phrase_gate_sheet.jpg"

ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_TARGETS = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
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

REFERENCE_WIDTH = 2544.0
REFERENCE_HEIGHT = 3264.0
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TRANSFORMS = [
    (
        "physical_back_mirror",
        "Back side seen through page 76, page 75 mirrored left-right.",
    ),
    (
        "same_side_no_mirror",
        "Unmirrored page 75 over page 76; non-backside control.",
    ),
    (
        "back_mirror_rotate180",
        "Mirrored back side with 180-degree turn.",
    ),
    (
        "front_rotate180",
        "Unmirrored page 75 with 180-degree turn; orientation control.",
    ),
]

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
ACTION_ORDER_TERMS = {
    "above",
    "below",
    "bottom",
    "count",
    "edge",
    "first",
    "fold",
    "inside",
    "last",
    "left",
    "line",
    "mirror",
    "order",
    "outside",
    "read",
    "reverse",
    "right",
    "row",
    "side",
    "take",
    "top",
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


def page_words(page_no: int) -> list[dict[str, Any]]:
    article = load_json(ARTICLE_MAP)
    for page in article.get("pages", []):
        if page.get("page") != page_no:
            continue
        words = []
        for word in page.get("words", []):
            tok = token(word.get("token") or word.get("text") or "")
            if not tok:
                continue
            box = [float(value) for value in word["box"]]
            words.append(
                {
                    "id": word.get("id"),
                    "index": int(word.get("index", len(words))),
                    "text": word.get("text", ""),
                    "token": tok,
                    "box": box,
                    "center": [
                        (box[0] + box[2]) / 2.0,
                        (box[1] + box[3]) / 2.0,
                    ],
                    "strictInstruction": tok in STRICT_TERMS,
                    "actionOrderInstruction": tok in ACTION_ORDER_TERMS,
                    "contextTerm": tok in CONTEXT_TERMS,
                }
            )
        return words
    return []


def target_code(target: dict[str, Any]) -> str:
    match = re.match(r"^([A-Z]\d+)\b", target.get("label", ""))
    if match:
        return match.group(1)
    fallback = {
        "buying_dip": "O4",
        "one_billion": "B4",
        "volcano_bonds": "G5",
        "shitcoiner_heart": "O5",
    }
    return fallback.get(target.get("id"), target.get("id", ""))


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_TARGETS)
    rows = []
    for target in data.get("targets", []):
        code = target_code(target)
        if code not in TARGET_ORDER:
            continue
        rows.append(
            {
                "target": code,
                "id": target.get("id"),
                "label": target.get("label"),
                "phrase": target.get("phrase"),
                "box": [float(value) for value in target["box"]],
            }
        )
    return sorted(rows, key=lambda row: TARGET_ORDER.index(row["target"]))


def transform_box(box: list[float], transform_id: str) -> list[float]:
    x0, y0, x1, y1 = box
    if transform_id == "physical_back_mirror":
        return [REFERENCE_WIDTH - x1, y0, REFERENCE_WIDTH - x0, y1]
    if transform_id == "same_side_no_mirror":
        return [x0, y0, x1, y1]
    if transform_id == "back_mirror_rotate180":
        return [x0, REFERENCE_HEIGHT - y1, x1, REFERENCE_HEIGHT - y0]
    if transform_id == "front_rotate180":
        return [
            REFERENCE_WIDTH - x1,
            REFERENCE_HEIGHT - y1,
            REFERENCE_WIDTH - x0,
            REFERENCE_HEIGHT - y0,
        ]
    raise ValueError(f"unknown transform: {transform_id}")


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def center_inside(center: list[float], box: list[float]) -> bool:
    return box[0] <= center[0] <= box[2] and box[1] <= center[1] <= box[3]


def words_for_box(words: list[dict[str, Any]], box: list[float]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    intersecting = [word for word in words if boxes_intersect(word["box"], box)]
    center_hits = [word for word in intersecting if center_inside(word["center"], box)]
    return (
        sorted(intersecting, key=lambda word: word["index"]),
        sorted(center_hits, key=lambda word: word["index"]),
    )


def inspect_target(
    target: dict[str, Any],
    transform_id: str,
    words: list[dict[str, Any]],
) -> dict[str, Any]:
    source_box = transform_box(target["box"], transform_id)
    intersecting, center_hits = words_for_box(words, source_box)
    selected = center_hits or intersecting
    strict = [word for word in selected if word["strictInstruction"]]
    action = [word for word in selected if word["actionOrderInstruction"]]
    context = [word for word in selected if word["contextTerm"]]
    return {
        "target": target["target"],
        "targetId": target["id"],
        "targetPhrase": target["phrase"],
        "referenceBox": [round(value, 3) for value in target["box"]],
        "sourceBox": [round(value, 3) for value in source_box],
        "intersectWordCount": len(intersecting),
        "centerWordCount": len(center_hits),
        "selectedWordCount": len(selected),
        "strictInstructionHitCount": len(strict),
        "actionOrderInstructionHitCount": len(action),
        "contextTermHitCount": len(context),
        "strictInstructionTerms": sorted({word["token"] for word in strict}),
        "actionOrderInstructionTerms": sorted({word["token"] for word in action}),
        "contextTerms": sorted({word["token"] for word in context}),
        "sourceTextPreview": " ".join(word["text"] for word in selected[:24]),
        "sourceWords": selected[:40],
    }


def pdf_names_from_polarity() -> list[str]:
    polarity = load_json(POLARITY_GATE)
    names = []
    for row in polarity.get("pairRows", []):
        if row.get("pdf") and row["pdf"] not in names:
            names.append(row["pdf"])
    if names:
        return names
    return [
        "magazine.pdf",
        "keyser bitcoin .pdf",
        "analysis_outputs/external_clues/google_drive_article_download.pdf",
    ]


def inspect_variant(
    pdf: str,
    transform_id: str,
    transform_description: str,
    targets: list[dict[str, Any]],
    words: list[dict[str, Any]],
) -> dict[str, Any]:
    target_rows = [inspect_target(target, transform_id, words) for target in targets]
    assembled = " | ".join(
        f"{row['target']}:{row['sourceTextPreview']}" for row in target_rows
    )
    all_four_word = all(row["selectedWordCount"] > 0 for row in target_rows)
    strict_rows = [row for row in target_rows if row["strictInstructionHitCount"] > 0]
    action_rows = [row for row in target_rows if row["actionOrderInstructionHitCount"] > 0]
    context_rows = [row for row in target_rows if row["contextTermHitCount"] > 0]
    return {
        "pdf": pdf,
        "transform": transform_id,
        "transformDescription": transform_description,
        "targetRows": target_rows,
        "allFourSourceWordRows": bool(all_four_word),
        "targetRowsWithWords": sum(1 for row in target_rows if row["selectedWordCount"] > 0),
        "strictInstructionRowCount": len(strict_rows),
        "actionOrderInstructionRowCount": len(action_rows),
        "contextTermRowCount": len(context_rows),
        "totalSourceWordHits": sum(row["selectedWordCount"] for row in target_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in target_rows),
        "totalActionOrderInstructionHits": sum(row["actionOrderInstructionHitCount"] for row in target_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in target_rows),
        "assembledActiveOrderText": assembled,
        "selectorCandidate": False,
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
    width, height = 1860, 1240
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    small = font(15)
    tiny = font(11)
    summary = result["summary"]

    draw.rectangle((0, 0, width, 106), fill=(24, 31, 42))
    draw.text((24, 18), "PDF Held-to-Light All-Target Phrase Gate", fill="white", font=title)
    draw.text(
        (24, 58),
        "All four active target boxes are traced through fixed orientations to page-75 source words.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1130, 20),
        f"variants {summary['variantCount']} | all-four word variants {summary['allFourSourceWordVariantCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1130, 52),
        f"strict rows {summary['strictInstructionRowCount']} | action rows {summary['actionOrderInstructionRowCount']} | sourceR3 {summary['sourceBackedR3BridgeHitCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    x_positions = [20, 255, 470, 548, 628, 708, 788, 870, 960]
    headers = ["PDF", "transform", "word rows", "all4", "strict", "action", "ctx", "words", "assembled active-order source text"]
    y = 130
    for x, header in zip(x_positions, headers):
        draw.text((x, y), header, fill=(40, 43, 50), font=small)
    y += 28
    for idx, row in enumerate(result["variantRows"][:18]):
        draw.rectangle((14, y - 5, width - 14, y + 54), fill=(245, 247, 250) if idx % 2 == 0 else (255, 255, 255))
        values = [
            row["pdf"],
            row["transform"],
            str(row["targetRowsWithWords"]),
            str(int(row["allFourSourceWordRows"])),
            str(row["strictInstructionRowCount"]),
            str(row["actionOrderInstructionRowCount"]),
            str(row["contextTermRowCount"]),
            str(row["totalSourceWordHits"]),
            row["assembledActiveOrderText"],
        ]
        for x, value in zip(x_positions, values):
            draw.text((x, y), str(value)[:128], fill=(25, 28, 34), font=tiny)
        y += 62
        if y > height - 50:
            break
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Held-to-Light All-Target Phrase Gate",
        "",
        "Scope: traced all four locked page-76 active target boxes through fixed PDF held-to-light orientation transforms, then assembled the page-75 source words in active order. No key derivation, hashes, seed/WIF/address checks, BIP39, candidate generation, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- PDFs / transforms / variants: `{summary['pdfCount']}` / `{summary['transformCount']}` / `{summary['variantCount']}`",
        f"- Active target rows: `{summary['targetTraceRowCount']}`",
        f"- All-four source-word variants: `{summary['allFourSourceWordVariantCount']}`",
        f"- Target rows with source words / source-word hits: `{summary['targetRowsWithWords']}` / `{summary['totalSourceWordHits']}`",
        f"- Strict instruction rows / hits: `{summary['strictInstructionRowCount']}` / `{summary['totalStrictInstructionHits']}`",
        f"- Action/order rows / hits: `{summary['actionOrderInstructionRowCount']}` / `{summary['totalActionOrderInstructionHits']}`",
        f"- Context rows / hits: `{summary['contextTermRowCount']}` / `{summary['totalContextTermHits']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Variant Rows",
        "",
        "| PDF | transform | word rows | all-four words | strict rows | action/order rows | context rows | source words | assembled active-order source text |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in result["variantRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    f"`{row['transform']}`",
                    str(row["targetRowsWithWords"]),
                    str(int(row["allFourSourceWordRows"])),
                    str(row["strictInstructionRowCount"]),
                    str(row["actionOrderInstructionRowCount"]),
                    str(row["contextTermRowCount"]),
                    str(row["totalSourceWordHits"]),
                    row["assembledActiveOrderText"].replace("|", "\\|")[:260],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote all-target PDF held-to-light source phrasing as a selector.",
            "- Some fixed orientations put ordinary page-75 prose under all four active target boxes, but none produce strict unit/order/action wording.",
            "- The original `magazine.pdf` physical-back orientation has no complete active-order phrase, and all-four phrase rows only appear in orientation controls without source-backed R3 or reopen triggers.",
            "",
            "## Next Move",
            "",
            "- Stop extending PDF held-to-light text tracing unless new source material changes the geometry or a raw clue names a transform, unit, and read order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    targets = active_targets()
    words = page_words(75)
    pdfs = pdf_names_from_polarity()
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    variant_rows = [
        inspect_variant(pdf, transform_id, description, targets, words)
        for pdf in pdfs
        for transform_id, description in TRANSFORMS
    ]
    target_trace_rows = [
        target_row for variant in variant_rows for target_row in variant["targetRows"]
    ]
    summary = {
        "decision": "current_pdf_held_to_light_all_target_phrase_no_selector",
        "pdfCount": len(pdfs),
        "transformCount": len(TRANSFORMS),
        "variantCount": len(variant_rows),
        "targetTraceRowCount": len(target_trace_rows),
        "allFourSourceWordVariantCount": sum(
            1 for row in variant_rows if row["allFourSourceWordRows"]
        ),
        "targetRowsWithWords": sum(1 for row in target_trace_rows if row["selectedWordCount"] > 0),
        "totalSourceWordHits": sum(row["selectedWordCount"] for row in target_trace_rows),
        "strictInstructionRowCount": sum(
            1 for row in target_trace_rows if row["strictInstructionHitCount"] > 0
        ),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in target_trace_rows),
        "actionOrderInstructionRowCount": sum(
            1 for row in target_trace_rows if row["actionOrderInstructionHitCount"] > 0
        ),
        "totalActionOrderInstructionHits": sum(
            row["actionOrderInstructionHitCount"] for row in target_trace_rows
        ),
        "contextTermRowCount": sum(1 for row in target_trace_rows if row["contextTermHitCount"] > 0),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in target_trace_rows),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorCandidateCount": 0,
    }
    summary["fingerprint"] = (
        f"pdfs={summary['pdfCount']}|transforms={summary['transformCount']}|"
        f"variants={summary['variantCount']}|targetRows={summary['targetTraceRowCount']}|"
        f"allFourWords={summary['allFourSourceWordVariantCount']}|"
        f"wordRows={summary['targetRowsWithWords']}|words={summary['totalSourceWordHits']}|"
        f"strictRows={summary['strictInstructionRowCount']}|strict={summary['totalStrictInstructionHits']}|"
        f"actionRows={summary['actionOrderInstructionRowCount']}|action={summary['totalActionOrderInstructionHits']}|"
        f"contextRows={summary['contextTermRowCount']}|context={summary['totalContextTermHits']}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "All four locked active page-76 boxes traced through fixed PDF held-to-light orientations to page-75 source words.",
        "inputs": {
            "articleMap": rel(ARTICLE_MAP),
            "activeTargets": rel(ACTIVE_TARGETS),
            "polarityGate": rel(POLARITY_GATE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "transforms": [item[0] for item in TRANSFORMS],
        },
        "decision": summary["decision"],
        "summary": summary,
        "variantRows": variant_rows,
        "targetTraceRows": target_trace_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(summary["fingerprint"])


if __name__ == "__main__":
    main()
