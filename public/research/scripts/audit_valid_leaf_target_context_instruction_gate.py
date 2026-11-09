#!/usr/bin/env python3
"""Classify target-side context words in the valid leaf line-band trace.

The valid page 75 -> page 76 held-to-light line-band trace contains target-side
article words that look tempting, especially "sell" and "mine". This bounded
pass checks whether those words form instruction grammar or remain ordinary
page-76 article context.

No OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks,
BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "valid_leaf_target_context_instruction_gate.json"
OUT_MD = OUT / "valid_leaf_target_context_instruction_gate.md"
OUT_SHEET = OUT / "valid_leaf_target_context_instruction_gate_sheet.jpg"

PAGE76_IMG = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
VALID_LEAF_LINE_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/"
    "current_scan_valid_leaf_line_band_trace.json"
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

EXTRACTION_ACTION_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "use",
    "using",
    "select",
    "extract",
    "decode",
    "encoded",
    "cipher",
    "key",
    "private",
    "seed",
}
UNIT_TERMS = {
    "line",
    "lines",
    "word",
    "words",
    "phrase",
    "phrases",
    "letter",
    "letters",
    "edge",
    "edges",
    "slot",
    "slots",
    "index",
    "indexes",
    "font",
    "bold",
    "highlight",
    "overdose",
}
ORDER_TERMS = {
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
}
TARGET_CONTEXT_TERMS = {
    "billion",
    "bitcoin",
    "bitcoins",
    "bond",
    "bonds",
    "bukele",
    "dip",
    "heart",
    "imf",
    "maximalist",
    "mine",
    "satoshi",
    "sell",
    "shitcoiner",
    "shitcoiners",
    "toxic",
    "volcano",
    "volcanoes",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def ascii_safe(text: str) -> str:
    return str(text).encode("ascii", "replace").decode("ascii")


def canonical_context(term: str) -> str:
    term = token(term)
    return {
        "bitcoins": "bitcoin",
        "bonds": "bond",
        "shitcoiners": "shitcoiner",
        "volcanoes": "volcano",
    }.get(term, term)


def terms_for_text(text: str) -> dict[str, list[str]]:
    tokens = [token(part) for part in re.findall(r"[A-Za-z0-9'$]+", text)]
    tokens = [part for part in tokens if part]
    return {
        "tokens": tokens,
        "action": sorted({part for part in tokens if part in EXTRACTION_ACTION_TERMS}),
        "unit": sorted({part for part in tokens if part in UNIT_TERMS}),
        "order": sorted({part for part in tokens if part in ORDER_TERMS}),
        "context": sorted(
            {canonical_context(part) for part in tokens if part in TARGET_CONTEXT_TERMS}
        ),
    }


def trace_target_rows(trace: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trace_row in trace.get("traceRows", []):
        target_text = " / ".join(line.get("text", "") for line in trace_row.get("targetLines", []))
        source_text = " / ".join(line.get("sourceText", "") for line in trace_row.get("sourceLines", []))
        target_terms = terms_for_text(target_text)
        source_terms = terms_for_text(source_text)
        phrase_terms = terms_for_text(trace_row.get("phrase", ""))
        source_context = set(source_terms["context"])
        line_context = set(target_terms["context"])
        source_backed_context = sorted(line_context & source_context)
        target_only_context = sorted(line_context - source_context)
        instruction_candidate = bool(
            target_terms["action"] and (target_terms["unit"] or target_terms["order"])
        )
        source_backed_instruction_candidate = bool(
            instruction_candidate and source_backed_context
        )
        rows.append(
            {
                "mode": trace_row.get("mode"),
                "target": trace_row.get("target"),
                "phrase": ascii_safe(trace_row.get("phrase", "")),
                "phraseContextTerms": phrase_terms["context"],
                "targetLineIndexes": [line.get("lineIndex") for line in trace_row.get("targetLines", [])],
                "targetText": ascii_safe(target_text),
                "sourceLineIndexes": [line.get("lineIndex") for line in trace_row.get("sourceLines", [])],
                "sourceText": ascii_safe(source_text),
                "targetContextTerms": target_terms["context"],
                "targetOnlyContextTerms": target_only_context,
                "sourceContextTerms": source_terms["context"],
                "sourceBackedContextTerms": source_backed_context,
                "actionTerms": target_terms["action"],
                "unitTerms": target_terms["unit"],
                "orderTerms": target_terms["order"],
                "instructionCandidate": instruction_candidate,
                "sourceBackedInstructionCandidate": source_backed_instruction_candidate,
                "targetLineHitCount": int(trace_row.get("targetLineHitCount", 0)),
                "sourceLineHitCount": int(trace_row.get("sourceLineHitCount", 0)),
            }
        )
    return rows


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
    image = Image.open(PAGE76_IMG).convert("RGB")
    crop = [430, 2050, 1840, 2550]
    scale = 0.72
    panel = image.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    sheet = Image.new("RGB", (1900, 900), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(14)
    tiny = font(11)
    sheet.paste(panel, (24, 128))
    draw.rectangle((0, 0, 1900, 100), fill=(24, 31, 42))
    draw.text((24, 16), "Valid Leaf Target Context Instruction Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "Target-side held-to-light context words are classified as article prose or extraction grammar.",
        fill=(236, 236, 236),
        font=small,
    )
    summary = result["summary"]
    draw.text(
        (1120, 18),
        f"context rows {summary['targetContextCarrierRowCount']} | instruction candidates {summary['instructionCandidateCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1120, 48),
        f"terms {','.join(summary['targetContextTerms']) or '-'} | triggers {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 525
    draw.text((24, y), "Target-side context carriers", fill=(30, 34, 40), font=small)
    y += 24
    headers = ["mode", "target", "lines", "context", "source-backed", "action", "unit", "order", "target text"]
    xs = [24, 230, 300, 370, 505, 630, 700, 760, 830]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=tiny)
    y += 18
    for row in result["targetContextRows"]:
        values = [
            row["mode"],
            row["target"],
            ",".join(str(item) for item in row["targetLineIndexes"]),
            ",".join(row["targetContextTerms"]) or "-",
            ",".join(row["sourceBackedContextTerms"]) or "-",
            ",".join(row["actionTerms"]) or "-",
            ",".join(row["unitTerms"]) or "-",
            ",".join(row["orderTerms"]) or "-",
            row["targetText"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:120], fill=(25, 28, 34), font=tiny)
        y += 24

    y += 18
    draw.text((24, y), "Interpretation", fill=(30, 34, 40), font=small)
    y += 24
    notes = [
        "The target-side terms are page-76 article context; they do not include read/take/use/extract/decode grammar.",
        "The B4 line contains sell/mine language, but it is content about Bukele and volcano mining, not a rule.",
        "O5's phrase has heart, but the valid line-band target row itself has no readable heart context term.",
        "No source-backed R3 bridge or reopen trigger is satisfied.",
    ]
    for note in notes:
        draw.text((24, y), "- " + note, fill=(25, 28, 34), font=small)
        y += 24
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Valid Leaf Target Context Instruction Gate",
        "",
        "Scope: classified target-side context words in the valid page 75 -> page 76 held-to-light line-band trace, especially article words that can look procedural (`sell`, `mine`, `heart`). No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Trace rows: `{summary['traceRowCount']}`",
        f"- Target context carrier rows: `{summary['targetContextCarrierRowCount']}`",
        f"- Target context terms: `{', '.join(summary['targetContextTerms']) or '-'}`",
        f"- Phrase context terms: `{', '.join(summary['phraseContextTerms']) or '-'}`",
        f"- Target-only context carrier rows: `{summary['targetOnlyContextCarrierRowCount']}`",
        f"- Source-backed context carrier rows: `{summary['sourceBackedContextCarrierRowCount']}`",
        f"- Action / unit / order carrier rows: `{summary['actionCarrierCount']}` / `{summary['unitCarrierCount']}` / `{summary['orderCarrierCount']}`",
        f"- Instruction candidate rows: `{summary['instructionCandidateCount']}`",
        f"- Source-backed instruction candidate rows: `{summary['sourceBackedInstructionCandidateCount']}`",
        f"- All-four active targets covered by target context carriers: `{summary['allFourActiveTargetsCoveredByTargetContext']}`",
        f"- All-four active targets covered by instruction candidates: `{summary['allFourActiveTargetsCoveredByInstructionCandidates']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Target Context Rows",
        "",
        "| mode | target | target lines | target context | source-backed context | action | unit | order | target text |",
        "|---|---|---:|---|---|---|---|---|---|",
    ]
    for row in result["targetContextRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['mode']}`",
                    f"`{row['target']}`",
                    ",".join(str(item) for item in row["targetLineIndexes"]),
                    f"`{','.join(row['targetContextTerms']) or '-'}`",
                    f"`{','.join(row['sourceBackedContextTerms']) or '-'}`",
                    f"`{','.join(row['actionTerms']) or '-'}`",
                    f"`{','.join(row['unitTerms']) or '-'}`",
                    f"`{','.join(row['orderTerms']) or '-'}`",
                    row["targetText"].replace("|", "\\|"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The target-side context terms are ordinary page-76 article context, not extraction grammar.",
            "- `sell` and `mine` occur in the B4 article lines (`he was going to tap his nation's volcanoes to mine` / `eis in bitcoin that he should sell`), but they are content verbs and do not pair with a unit/order such as word, letter, line, first, last, left, or right.",
            "- `heart` appears in the known O5 phrase label (`shitcoiner at heart`) but not as a readable target-side line-band context term in the current trace row.",
            "- Only one row has exact source-backed context (`bitcoin` in the small-jitter G5 row), and it is still context only with no instruction grammar.",
            "- Keep valid 75->76 target-side line-band context closed as prose/context, not a selector.",
            "",
            "## Next Move",
            "",
            "- Do not reopen held-to-light line-band extraction from target context words. Best direction remains original/source-layout validation or raw clue wording that explicitly names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    trace = load_json(VALID_LEAF_LINE_TRACE)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    rows = trace_target_rows(trace)
    target_context_rows = [row for row in rows if row["targetContextTerms"]]
    instruction_rows = [row for row in rows if row["instructionCandidate"]]
    target_context_targets = sorted(
        {row["target"] for row in target_context_rows},
        key=lambda item: TARGET_ORDER.index(item) if item in TARGET_ORDER else 99,
    )
    instruction_targets = sorted(
        {row["target"] for row in instruction_rows},
        key=lambda item: TARGET_ORDER.index(item) if item in TARGET_ORDER else 99,
    )
    target_context_terms = sorted(
        {term for row in target_context_rows for term in row["targetContextTerms"]}
    )
    phrase_context_terms = sorted({term for row in rows for term in row["phraseContextTerms"]})
    source_backed_context_terms = sorted(
        {term for row in target_context_rows for term in row["sourceBackedContextTerms"]}
    )
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    summary = {
        "decision": "valid_leaf_target_context_instruction_no_selector",
        "traceRowCount": len(rows),
        "targetContextCarrierRowCount": len(target_context_rows),
        "targetContextTerms": target_context_terms,
        "phraseContextTerms": phrase_context_terms,
        "targetContextTargets": target_context_targets,
        "targetOnlyContextCarrierRowCount": sum(bool(row["targetOnlyContextTerms"]) for row in target_context_rows),
        "sourceBackedContextCarrierRowCount": sum(bool(row["sourceBackedContextTerms"]) for row in target_context_rows),
        "sourceBackedContextTerms": source_backed_context_terms,
        "actionCarrierCount": sum(bool(row["actionTerms"]) for row in rows),
        "unitCarrierCount": sum(bool(row["unitTerms"]) for row in rows),
        "orderCarrierCount": sum(bool(row["orderTerms"]) for row in rows),
        "instructionCandidateCount": len(instruction_rows),
        "sourceBackedInstructionCandidateCount": sum(
            bool(row["sourceBackedInstructionCandidate"]) for row in rows
        ),
        "allFourActiveTargetsCoveredByTargetContext": all(
            target in target_context_targets for target in TARGET_ORDER
        ),
        "allFourActiveTargetsCoveredByInstructionCandidates": all(
            target in instruction_targets for target in TARGET_ORDER
        ),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"rows={summary['traceRowCount']}|ctxRows={summary['targetContextCarrierRowCount']}|"
        f"lineTerms={','.join(target_context_terms) or '-'}|"
        f"phraseTerms={','.join(phrase_context_terms) or '-'}|"
        f"targetOnly={summary['targetOnlyContextCarrierRowCount']}|"
        f"sourceCtx={summary['sourceBackedContextCarrierRowCount']}|"
        f"sourceCtxTerms={','.join(source_backed_context_terms) or '-'}|"
        f"action={summary['actionCarrierCount']}|unit={summary['unitCarrierCount']}|"
        f"order={summary['orderCarrierCount']}|instr={summary['instructionCandidateCount']}|"
        f"sourceInstr={summary['sourceBackedInstructionCandidateCount']}|"
        f"all4ctx={int(summary['allFourActiveTargetsCoveredByTargetContext'])}|"
        f"all4instr={int(summary['allFourActiveTargetsCoveredByInstructionCandidates'])}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Target-side context words in the valid 75->76 line-band trace classified against extraction grammar.",
        "inputs": {
            "validLeafLineBandTrace": rel(VALID_LEAF_LINE_TRACE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "targetContextRows": target_context_rows,
        "allRows": rows,
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
