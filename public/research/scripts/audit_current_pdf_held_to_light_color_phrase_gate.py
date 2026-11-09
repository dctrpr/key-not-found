#!/usr/bin/env python3
"""Audit color-class source phrases in fixed PDF held-to-light geometry.

This bounded pass reuses the all-target held-to-light source-word trace and
groups the active target rows by their locked page-76 color/format classes:
Y/orange and K/black. It tests whether the color split supplies a reading order
or source-side unit/order wording that the all-target phrase pass did not.

No key derivation, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_held_to_light_color_phrase_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_held_to_light_color_phrase_gate.json"
OUT_MD = OUT / "current_pdf_held_to_light_color_phrase_gate.md"
OUT_SHEET = OUT / "current_pdf_held_to_light_color_phrase_gate_sheet.jpg"

ACTIVE_TARGETS = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
ALL_TARGET_PHRASE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate/"
    "current_pdf_held_to_light_all_target_phrase_gate.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
COLOR_ORDER_MODES = [
    ("active_order", TARGET_ORDER),
    ("visual_state_y_then_k", ["O4", "O5", "B4", "G5"]),
    ("visual_state_k_then_y", ["B4", "G5", "O4", "O5"]),
    ("orange_then_black", ["O4", "O5", "B4", "G5"]),
    ("black_then_orange", ["B4", "G5", "O4", "O5"]),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def active_metadata() -> dict[str, dict[str, Any]]:
    data = load_json(ACTIVE_TARGETS)
    rows: dict[str, dict[str, Any]] = {}
    for target in data.get("targets", []):
        label = target.get("label", "")
        code = label.split(" ", 1)[0]
        if code not in TARGET_ORDER:
            fallback = {
                "buying_dip": "O4",
                "one_billion": "B4",
                "volcano_bonds": "G5",
                "shitcoiner_heart": "O5",
            }
            code = fallback.get(target.get("id"), code)
        rows[code] = {
            "target": code,
            "targetId": target.get("id"),
            "targetPhrase": target.get("phrase"),
            "visualState": target.get("visualState"),
            "color": "orange" if target.get("visualState") == "Y" else "black",
            "docmDominantFont": target.get("docmDominantFont"),
            "docmBoldFraction": target.get("docmBoldFraction"),
            "pageLine": target.get("pageLine"),
            "corridorIndex": target.get("corridorIndex"),
        }
    return rows


def target_rows_by_variant(all_target: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    meta = active_metadata()
    for variant in all_target.get("variantRows", []):
        target_rows = []
        for row in variant.get("targetRows", []):
            target = row.get("target")
            target_rows.append({**row, **meta.get(target, {})})
        rows.append({**variant, "targetRows": target_rows})
    return rows


def stream_for_order(target_rows: list[dict[str, Any]], order: list[str]) -> dict[str, Any]:
    by_target = {row["target"]: row for row in target_rows}
    ordered_rows = [by_target[target] for target in order if target in by_target]
    source_texts = [row.get("sourceTextPreview", "") for row in ordered_rows]
    strict_terms = sorted(
        {
            term
            for row in ordered_rows
            for term in row.get("strictInstructionTerms", [])
        }
    )
    action_terms = sorted(
        {
            term
            for row in ordered_rows
            for term in row.get("actionOrderInstructionTerms", [])
        }
    )
    context_terms = sorted(
        {term for row in ordered_rows for term in row.get("contextTerms", [])}
    )
    visual_stream = "".join(str(row.get("visualState") or ".") for row in ordered_rows)
    color_stream = "-".join(str(row.get("color") or "") for row in ordered_rows)
    target_stream = "-".join(row["target"] for row in ordered_rows)
    return {
        "targetStream": target_stream,
        "visualStateStream": visual_stream,
        "colorStream": color_stream,
        "sourceText": " | ".join(f"{row['target']}:{text}" for row, text in zip(ordered_rows, source_texts)),
        "sourceWordHitCount": sum(row.get("selectedWordCount", 0) for row in ordered_rows),
        "populatedTargetCount": sum(1 for row in ordered_rows if row.get("selectedWordCount", 0) > 0),
        "strictInstructionTerms": strict_terms,
        "actionOrderInstructionTerms": action_terms,
        "contextTerms": context_terms,
        "strictInstructionHitCount": sum(row.get("strictInstructionHitCount", 0) for row in ordered_rows),
        "actionOrderInstructionHitCount": sum(row.get("actionOrderInstructionHitCount", 0) for row in ordered_rows),
        "contextTermHitCount": sum(row.get("contextTermHitCount", 0) for row in ordered_rows),
    }


def analyze_variant(variant: dict[str, Any]) -> dict[str, Any]:
    stream_rows = []
    for mode, order in COLOR_ORDER_MODES:
        stream = stream_for_order(variant["targetRows"], order)
        stream_rows.append({"mode": mode, **stream})
    y_rows = [row for row in variant["targetRows"] if row.get("visualState") == "Y"]
    k_rows = [row for row in variant["targetRows"] if row.get("visualState") == "K"]
    y_stream = stream_for_order(y_rows, [row["target"] for row in y_rows])
    k_stream = stream_for_order(k_rows, [row["target"] for row in k_rows])
    return {
        "pdf": variant["pdf"],
        "transform": variant["transform"],
        "allFourSourceWordRows": variant.get("allFourSourceWordRows"),
        "targetRowsWithWords": variant.get("targetRowsWithWords"),
        "streamRows": stream_rows,
        "yGroup": y_stream,
        "kGroup": k_stream,
        "colorSelectorCandidate": False,
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
    width, height = 1880, 1180
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    small = font(15)
    tiny = font(11)
    summary = result["summary"]
    draw.rectangle((0, 0, width, 108), fill=(24, 31, 42))
    draw.text((24, 18), "PDF Held-to-Light Color Phrase Gate", fill="white", font=title)
    draw.text(
        (24, 58),
        "Groups held-to-light source words by active color state: Y/orange vs K/black.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1110, 20),
        f"streams {summary['streamRowCount']} | strict {summary['totalStrictInstructionHits']} | action {summary['totalActionOrderInstructionHits']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1110, 52),
        f"all-four phrase variants {summary['allFourSourceWordVariantCount']} | sourceR3 {summary['sourceBackedR3BridgeHitCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    headers = ["PDF", "transform", "mode", "targets", "pop", "words", "strict", "action", "source text"]
    xs = [20, 270, 470, 660, 790, 850, 920, 990, 1065]
    y = 132
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(40, 43, 50), font=small)
    y += 28
    rows = []
    for variant in result["variantRows"]:
        for row in variant["streamRows"]:
            if row["mode"] in {"active_order", "visual_state_y_then_k", "visual_state_k_then_y"}:
                rows.append((variant, row))
    for idx, (variant, row) in enumerate(rows[:20]):
        draw.rectangle((14, y - 5, width - 14, y + 48), fill=(245, 247, 250) if idx % 2 == 0 else (255, 255, 255))
        values = [
            variant["pdf"],
            variant["transform"],
            row["mode"],
            row["targetStream"],
            row["populatedTargetCount"],
            row["sourceWordHitCount"],
            row["strictInstructionHitCount"],
            row["actionOrderInstructionHitCount"],
            row["sourceText"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:125], fill=(25, 28, 34), font=tiny)
        y += 56
        if y > height - 50:
            break
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Held-to-Light Color Phrase Gate",
        "",
        "Scope: grouped the fixed held-to-light source-word trace by active page-76 color/format states (`Y/orange` and `K/black`) and tested whether color order supplies unit/order wording. No key derivation, hashes, seed/WIF/address checks, BIP39, candidate generation, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Variant rows / stream rows: `{summary['variantCount']}` / `{summary['streamRowCount']}`",
        f"- All-four source-word variants imported: `{summary['allFourSourceWordVariantCount']}`",
        f"- Populated stream rows / source-word hits: `{summary['populatedStreamRowCount']}` / `{summary['totalSourceWordHits']}`",
        f"- Strict instruction hits / action-order hits: `{summary['totalStrictInstructionHits']}` / `{summary['totalActionOrderInstructionHits']}`",
        f"- Context hits: `{summary['totalContextTermHits']}`",
        f"- Color selector candidates: `{summary['colorSelectorCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Stream Rows",
        "",
        "| PDF | transform | mode | targets | populated | words | strict | action | context | source text |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for variant in result["variantRows"]:
        for row in variant["streamRows"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{variant['pdf']}`",
                        f"`{variant['transform']}`",
                        f"`{row['mode']}`",
                        f"`{row['targetStream']}`",
                        str(row["populatedTargetCount"]),
                        str(row["sourceWordHitCount"]),
                        str(row["strictInstructionHitCount"]),
                        str(row["actionOrderInstructionHitCount"]),
                        str(row["contextTermHitCount"]),
                        row["sourceText"].replace("|", "\\|")[:220],
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote the active color split as a held-to-light source selector.",
            "- Y/orange and K/black grouping changes the read order of ordinary page-75 prose, but it adds no strict unit/order/action wording.",
            "- The color split remains useful as a source-validation fingerprint (`YKKY` / `OBBO`), not as an extraction rule.",
            "",
            "## Next Move",
            "",
            "- Keep color/format streams as source-comparison guardrails. A new source or raw clue still needs to provide transform, unit, and read order before any selector/key branch reopens.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    all_target = load_json(ALL_TARGET_PHRASE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    variants = [analyze_variant(row) for row in target_rows_by_variant(all_target)]
    stream_rows = [row for variant in variants for row in variant["streamRows"]]
    summary = {
        "decision": "current_pdf_held_to_light_color_phrase_no_selector",
        "variantCount": len(variants),
        "streamRowCount": len(stream_rows),
        "allFourSourceWordVariantCount": all_target.get("summary", {}).get("allFourSourceWordVariantCount", 0),
        "populatedStreamRowCount": sum(1 for row in stream_rows if row["populatedTargetCount"] > 0),
        "allFourPopulatedStreamRowCount": sum(1 for row in stream_rows if row["populatedTargetCount"] == 4),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in stream_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in stream_rows),
        "totalActionOrderInstructionHits": sum(row["actionOrderInstructionHitCount"] for row in stream_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in stream_rows),
        "colorSelectorCandidateCount": sum(1 for variant in variants if variant["colorSelectorCandidate"]),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
    }
    summary["fingerprint"] = (
        f"variants={summary['variantCount']}|streams={summary['streamRowCount']}|"
        f"allFourWords={summary['allFourSourceWordVariantCount']}|"
        f"populatedStreams={summary['populatedStreamRowCount']}|"
        f"allFourStreams={summary['allFourPopulatedStreamRowCount']}|"
        f"words={summary['totalSourceWordHits']}|strict={summary['totalStrictInstructionHits']}|"
        f"action={summary['totalActionOrderInstructionHits']}|context={summary['totalContextTermHits']}|"
        f"candidates={summary['colorSelectorCandidateCount']}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Fixed PDF held-to-light source-word trace grouped by active color/format streams.",
        "inputs": {
            "activeTargets": rel(ACTIVE_TARGETS),
            "allTargetPhraseGate": rel(ALL_TARGET_PHRASE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "variantRows": variants,
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
