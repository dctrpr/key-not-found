#!/usr/bin/env python3
"""Reconcile active O4/B4/G5/O5 units across sentence, line, corridor, and DOCM layers."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_JSON = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
SENTENCE_BRIDGE_JSON = ROOT / "analysis_outputs/plain_text_transcript/sentence_line_highlight_bridge/sentence_line_highlight_bridge.json"
CORRECTION_IMPACT_JSON = ROOT / "analysis_outputs/plain_text_transcript/correction_selector_impact/correction_selector_impact.json"
OUT_DIR = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]

ACTIVE_ORDER = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]


def hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def parse_span(span: str) -> tuple[int, int]:
    if "-" in span:
        a, b = span.split("-", 1)
        return int(a), int(b)
    value = int(span)
    return value, value


def sentence_for_line(line_index: int, bridges: list[dict]) -> dict | None:
    for bridge in bridges:
        start, end = parse_span(bridge["pageLineSpan"])
        if start <= line_index <= end:
            return bridge
    return None


def first_letters(words: list[str]) -> str:
    out = []
    for word in words:
        match = re.search(r"[A-Za-z0-9$]", word)
        out.append(match.group(0) if match else "-")
    return "".join(out)


def last_letters(words: list[str]) -> str:
    out = []
    for word in words:
        match = re.search(r"[A-Za-z0-9$](?!.*[A-Za-z0-9$])", word)
        out.append(match.group(0) if match else "-")
    return "".join(out)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anchor_data = json.loads(ANCHOR_JSON.read_text())
    bridge_data = json.loads(SENTENCE_BRIDGE_JSON.read_text())
    correction_data = json.loads(CORRECTION_IMPACT_JSON.read_text())
    anchors = {anchor["id"]: anchor for anchor in anchor_data["anchors"]}
    bridges = bridge_data["bridges"]

    records = []
    for idx, anchor_id in enumerate(ACTIVE_ORDER, start=1):
        anchor = anchors[anchor_id]
        line = anchor["canonicalLineIndex"]
        bridge = sentence_for_line(line, bridges)
        if not bridge:
            raise RuntimeError(f"No sentence bridge for line {line}")
        start, _end = parse_span(bridge["corridorSpan"])
        corridor_index = line - 18
        phrase = anchor["label"]
        state = "Y" if anchor["color"] == "orange" else "K"
        records.append(
            {
                "order": idx,
                "id": anchor_id,
                "label": phrase,
                "color": anchor["color"],
                "visualState": state,
                "docmDominantFont": anchor["docm"]["dominantFont"],
                "docmBoldFraction": anchor["docm"]["boldFraction"],
                "docmHighlights": anchor["docm"]["highlights"],
                "pageLine": line,
                "corridorIndex": corridor_index,
                "sentenceRow": bridge["sentenceRow"],
                "sentenceSpan": bridge["pageLineSpan"],
                "sentenceCorridorSpan": bridge["corridorSpan"],
                "canonicalLine": anchor["canonicalLine"],
                "leftBoundaryWord": anchor["sameLine"]["leftBoundaryWord"] or "-",
                "rightBoundaryWord": anchor["sameLine"]["rightBoundaryWord"] or "-",
                "aboveWord": anchor["vertical"]["aboveCenterWord"] or "-",
                "belowWord": anchor["vertical"]["belowCenterWord"] or "-",
                "phraseInitials": anchor["letterUnits"]["phraseInitials"],
                "phraseEdges": anchor["letterUnits"]["phraseEdges"],
            }
        )

    streams = {
        "visualStateOrder": "".join(record["visualState"] for record in records),
        "pageLines": " ".join(str(record["pageLine"]) for record in records),
        "sentenceRows": " ".join(str(record["sentenceRow"]) for record in records),
        "corridorIndexes": " ".join(str(record["corridorIndex"]) for record in records),
        "sentenceLinePairs": " ".join(f"{record['sentenceRow']}-{record['pageLine']}" for record in records),
        "lineGaps": " ".join(str(records[i + 1]["pageLine"] - records[i]["pageLine"]) for i in range(len(records) - 1)),
        "sentenceGaps": " ".join(str(records[i + 1]["sentenceRow"] - records[i]["sentenceRow"]) for i in range(len(records) - 1)),
        "corridorGaps": " ".join(str(records[i + 1]["corridorIndex"] - records[i]["corridorIndex"]) for i in range(len(records) - 1)),
        "phraseInitials": " ".join(record["phraseInitials"] for record in records),
        "phraseEdges": " ".join(record["phraseEdges"] for record in records),
        "leftBoundaryWords": " | ".join(record["leftBoundaryWord"] for record in records),
        "rightBoundaryWords": " | ".join(record["rightBoundaryWord"] for record in records),
        "aboveWords": " | ".join(record["aboveWord"] for record in records),
        "belowWords": " | ".join(record["belowWord"] for record in records),
    }
    streams["leftBoundaryInitials"] = first_letters([record["leftBoundaryWord"] for record in records])
    streams["rightBoundaryInitials"] = first_letters([record["rightBoundaryWord"] for record in records])
    streams["aboveInitials"] = first_letters([record["aboveWord"] for record in records])
    streams["belowInitials"] = first_letters([record["belowWord"] for record in records])
    streams["leftBoundaryLasts"] = last_letters([record["leftBoundaryWord"] for record in records])
    streams["rightBoundaryLasts"] = last_letters([record["rightBoundaryWord"] for record in records])
    streams["aboveLasts"] = last_letters([record["aboveWord"] for record in records])
    streams["belowLasts"] = last_letters([record["belowWord"] for record in records])

    stream_hits = {name: hits(value) for name, value in streams.items()}
    mixed_sentence_units = {}
    for record in records:
        mixed_sentence_units.setdefault(record["sentenceRow"], []).append(record["id"])
    duplicate_sentence_rows = {row: ids for row, ids in mixed_sentence_units.items() if len(ids) > 1}

    selector_added_terms = [
        row
        for row in correction_data["rows"]
        if row.get("addedInstructionHits")
    ]

    assessment = [
        "O4/B4/G5/O5 are stable as visual/DOCM units, but they do not map one-to-one across sentence rows and printed line rows.",
        "B4 `$1 billion` and G5 `Volcano Bonds` share canonical sentence row 45 while occupying different printed lines; this blocks sentence-row numbering as a precise four-unit selector.",
        "The four active line units form page-line stream `22 25 27 32`, sentence stream `44 45 45 48`, and corridor-index stream `4 7 9 14`; none contains procedural terms or an obvious human-readable instruction.",
        "The O-B-B-O / Y-K-K-Y visual-state order remains real, but it is only a locator signature unless a clue names sentence, line, corridor index, or side words.",
        "The latest correction audit confirms no correction-added word grants selector permission, so line-unit reconciliation remains validation-only.",
    ]
    decision = (
        "Use active line/sentence/corridor rows as locator evidence only. Do not extract by line, sentence, gap, or side-word streams without a new clue naming that unit."
    )
    next_move = (
        "Keep source/original-layout validation as the next productive path; reopen line units only if a clue explicitly says sentence, line, gap, first/last, or side."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Active O4/B4/G5/O5 line-unit reconciliation across corrected text, sentence rows, page lines, corridor indexes, and DOCM states. No key derivation.",
        "sources": {
            "anchorAdjacency": str(ANCHOR_JSON.relative_to(ROOT)),
            "sentenceLineBridge": str(SENTENCE_BRIDGE_JSON.relative_to(ROOT)),
            "correctionSelectorImpact": str(CORRECTION_IMPACT_JSON.relative_to(ROOT)),
        },
        "records": records,
        "duplicateSentenceRows": duplicate_sentence_rows,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "selectorPermissionCorrections": selector_added_terms,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "active_line_unit_reconciliation.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# Active Line Unit Reconciliation",
        "",
        "Scope: reconcile the locked O4/B4/G5/O5 units across corrected text, sentence rows, printed page lines, corridor indexes, and DOCM/font states. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active units checked: `{len(records)}`",
        f"- Duplicate active units in same sentence row: `{duplicate_sentence_rows or '-'}`",
        "",
        "## Active Units",
        "",
        "| order | id | state | sentence | page line | corridor | DOCM | left | right | above | below | line text |",
        "|---:|---|---|---:|---:|---:|---|---|---|---|---|---|",
    ]
    for record in records:
        docm = f"{record['docmDominantFont']} bold={record['docmBoldFraction']} hi={record['docmHighlights']}"
        line_text = record["canonicalLine"].replace("|", "\\|")
        lines.append(
            f"| {record['order']} | `{record['id']}` | `{record['visualState']}` | {record['sentenceRow']} | "
            f"{record['pageLine']} | {record['corridorIndex']} | `{docm}` | `{record['leftBoundaryWord']}` | "
            f"`{record['rightBoundaryWord']}` | `{record['aboveWord']}` | `{record['belowWord']}` | {line_text} |"
        )

    lines.extend(["", "## Streams", "", "| stream | value | instruction hits |", "|---|---|---|"])
    for name, value in streams.items():
        lines.append(f"| `{name}` | `{value}` | {', '.join(stream_hits[name]) or '-'} |")

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "active_line_unit_reconciliation.md").write_text("\n".join(lines))

    print(OUT_DIR / "active_line_unit_reconciliation.md")
    print(OUT_DIR / "active_line_unit_reconciliation.json")


if __name__ == "__main__":
    main()
