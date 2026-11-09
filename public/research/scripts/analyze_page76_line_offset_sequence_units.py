#!/usr/bin/env python3
"""Audit whether page-76 line-offset hits carry color/order information.

The previous audit found a partial locator sequence:
O1->O2, B1->B2, O3->B3, B5->O5.

This script asks whether that sequence itself tells us what to read next:
color transitions, hit/miss pattern, first/last words, initials, and the
failed #2/#4 landings. No key candidates or hashes are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OFFSET_JSON = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json"
OUT = ROOT / "analysis_outputs/source_audit/page76_line_offset_sequence_units"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_line_offset_sequence_units.json"
OUT_MD = OUT / "page76_line_offset_sequence_units.md"

INSTRUCTION_TERMS = {
    "read",
    "take",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "seed",
    "private",
    "wif",
    "down",
    "up",
    "next",
    "after",
    "before",
}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def initial_stream(items: list[str]) -> str:
    return "".join(item[0] for item in items if item)


def last_stream(items: list[str]) -> str:
    return "".join(item[-1] for item in items if item)


def first_word(text: str) -> str:
    ws = words(text)
    return ws[0] if ws else ""


def last_word(text: str) -> str:
    ws = words(text)
    return ws[-1] if ws else ""


def color_code(kind: str) -> str:
    return "O" if kind == "orange" else "B"


def scan_terms(text: str) -> list[str]:
    tokens = set(w.lower() for w in words(text))
    return sorted(tokens & INSTRUCTION_TERMS)


def main() -> None:
    data = json.loads(OFFSET_JSON.read_text())
    down_rows = [r for r in data["landingRows"] if r["direction"] == "down"]
    hit_rows = [r for r in down_rows if r.get("isHighlightHit")]
    miss_rows = [r for r in down_rows if not r.get("isHighlightHit")]

    units_by_id = {u["id"]: u for u in data["units"]}

    hit_sequence = []
    for row in hit_rows:
        source = units_by_id[row["sourceId"]]
        target_id = row["targetUnits"][0]
        target = units_by_id[target_id]
        source_color = color_code(source["kind"])
        target_color = color_code(target["kind"])
        hit_sequence.append(
            {
                "sourceId": row["sourceId"],
                "targetId": target_id,
                "sourceIndex": source["index"],
                "targetIndex": target["index"],
                "sourceColor": source_color,
                "targetColor": target_color,
                "transition": source_color + target_color,
                "sameColor": source_color == target_color,
                "sourceLabel": source["label"],
                "targetLabel": target["label"],
                "targetLineText": row["targetText"],
                "sourceFirstWord": first_word(source["label"]),
                "targetFirstWord": first_word(target["label"]),
                "targetLineFirstWord": first_word(row["targetText"]),
                "sourceLastWord": last_word(source["label"]),
                "targetLastWord": last_word(target["label"]),
            }
        )

    all_down_sequence = []
    for row in down_rows:
        source = units_by_id[row["sourceId"]]
        all_down_sequence.append(
            {
                "sourceId": row["sourceId"],
                "sourceIndex": source["index"],
                "sourceColor": color_code(source["kind"]),
                "hit": bool(row.get("isHighlightHit")),
                "targetLine": row["targetLine"],
                "targetUnits": row["targetUnits"],
                "targetLineFirstWord": first_word(row["targetText"]),
                "targetLineLastWord": last_word(row["targetText"]),
                "targetLineText": row["targetText"],
            }
        )

    source_ids = [h["sourceId"] for h in hit_sequence]
    target_ids = [h["targetId"] for h in hit_sequence]
    transitions = [h["transition"] for h in hit_sequence]
    same_bits = "".join("0" if h["sameColor"] else "1" for h in hit_sequence)
    hit_miss_bits = "".join("1" if r["hit"] else "0" for r in all_down_sequence)
    hit_source_first = [h["sourceFirstWord"] for h in hit_sequence]
    hit_target_first = [h["targetFirstWord"] for h in hit_sequence]
    hit_target_line_first = [h["targetLineFirstWord"] for h in hit_sequence]
    miss_line_first = [r["targetLineFirstWord"] or "-" for r in all_down_sequence if not r["hit"]]

    streams = {
        "hitSourceIds": " ".join(source_ids),
        "hitTargetIds": " ".join(target_ids),
        "hitTransitions": " ".join(transitions),
        "sameColorBits_same0_cross1": same_bits,
        "allDownHitMissBits_hit1_miss0": hit_miss_bits,
        "hitSourceFirstWords": " ".join(hit_source_first),
        "hitTargetFirstWords": " ".join(hit_target_first),
        "hitTargetLineFirstWords": " ".join(hit_target_line_first),
        "hitSourceInitials": initial_stream(hit_source_first),
        "hitTargetInitials": initial_stream(hit_target_first),
        "hitTargetLineInitials": initial_stream(hit_target_line_first),
        "hitSourceLastLetters": last_stream([h["sourceLastWord"] for h in hit_sequence]),
        "hitTargetLastLetters": last_stream([h["targetLastWord"] for h in hit_sequence]),
        "missTargetLineFirstWords": " ".join(miss_line_first),
        "missTargetLineInitials": initial_stream([w for w in miss_line_first if w != "-"]),
        "allDownTargetLineFirstWords": " ".join(r["targetLineFirstWord"] or "-" for r in all_down_sequence),
        "allDownTargetLineInitials": initial_stream([r["targetLineFirstWord"] for r in all_down_sequence if r["targetLineFirstWord"]]),
    }
    search_text = " ".join(streams.values()) + " " + " ".join(row["targetLineText"] for row in all_down_sequence)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 partial line-offset hit sequence color/order audit; no key derivation.",
        "hitSequence": hit_sequence,
        "allDownSequence": all_down_sequence,
        "streams": streams,
        "instructionTermHits": scan_terms(search_text),
        "assessment": [
            "The hit sequence is O1->O2, B1->B2, O3->B3, B5->O5.",
            "Color transitions are OO, BB, OB, BO; this is balanced but does not read as an instruction.",
            "Same/cross color bits are 0011; the all-down hit/miss mask is 1010100010. Neither stream is human-readable.",
            "First-word and initial streams from source labels, target labels, target lines, and #2/#4 misses do not reveal read/take/fold/mirror/word/letter/key instructions.",
            "Treat the sequence as locator/orientation evidence only until an external/source rule explains how to use it.",
        ],
        "nextMove": "Return to source/provenance evidence: original Canva/source images, physical registration, or a recovered layout rule that explains why #2/#4 fail and what unit the hit sequence selects.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Page 76 Line-Offset Sequence Units Audit",
        "",
        "Scope: check whether the partial line-offset hit sequence carries a simple color/order message. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Hit Sequence",
        "",
        "| source | target | transition | source first | target first | target line first |",
        "|---|---|---|---|---|---|",
    ]
    for row in hit_sequence:
        md.append(
            f"| {row['sourceId']} | {row['targetId']} | {row['transition']} | `{row['sourceFirstWord']}` | `{row['targetFirstWord']}` | `{row['targetLineFirstWord']}` |"
        )

    md.extend(
        [
            "",
            "## Streams",
            "",
        ]
    )
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value}`")

    md.extend(
        [
            "",
            "## Misses",
            "",
            "| source | target line | first word | line text |",
            "|---|---:|---|---|",
        ]
    )
    for row in all_down_sequence:
        if row["hit"]:
            continue
        text = row["targetLineText"].replace("|", "\\|")
        md.append(f"| {row['sourceId']} | {row['targetLine']} | `{row['targetLineFirstWord'] or '-'}` | {text} |")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The color transition sequence is balanced (`OO BB OB BO`) but does not give a readable instruction.",
            "- Hit/miss, first-word, initial, last-letter, and failed-landing streams are not instruction-like.",
            "- This closes the color/order sequence as a standalone selector under the current text model.",
            "- Next best move: seek source/provenance or physical-registration evidence that explains why the partial locator pattern exists and what unit it should select.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
