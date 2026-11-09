#!/usr/bin/env python3
"""Audit the supported page-76 landing-line sequence.

The line-offset landing evidence audit showed that supported landings are not
just highlighted boxes; #4 lands in the p78 graphic reflection band. This
script tests whether the supported landing sequence itself gives a simple
instruction through source ids/colors/indices, line numbers, first/last words,
or support terms.

No key candidates or hashes are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANDING_JSON = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"
OUT = ROOT / "analysis_outputs/source_audit/supported_landing_sequence_units"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "supported_landing_sequence_units.json"
OUT_MD = OUT / "supported_landing_sequence_units.md"

STOP = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "into",
    "from",
    "because",
    "worth",
    "future",
    "would",
    "could",
    "should",
    "have",
    "been",
    "were",
    "they",
    "their",
    "your",
    "here",
    "there",
}

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


def first_word(text: str) -> str:
    ws = words(text)
    return ws[0] if ws else ""


def last_word(text: str) -> str:
    ws = words(text)
    return ws[-1] if ws else ""


def initials(items: list[str]) -> str:
    return "".join(item[0] for item in items if item)


def lasts(items: list[str]) -> str:
    return "".join(item[-1] for item in items if item)


def color_of_source(source_id: str) -> str:
    return "O" if source_id.startswith("O") else "B"


def interesting_words(text: str) -> list[str]:
    out = []
    for word in words(text):
        low = word.lower()
        if len(low) >= 4 and low not in STOP:
            out.append(word)
    return out


def evidence_terms(row: dict) -> list[str]:
    terms: list[str] = []
    for item in row.get("evidence", []):
        for part in re.findall(r"terms=([A-Za-z0-9,]+)|terms: ([A-Za-z0-9, ]+)", item):
            raw = part[0] or part[1]
            for token in re.split(r"[, ]+", raw):
                if token and token.lower() not in STOP:
                    terms.append(token)
    return terms


def scan_instruction_terms(text: str) -> list[str]:
    tokens = {w.lower() for w in words(text)}
    return sorted(tokens & INSTRUCTION_TERMS)


def main() -> None:
    data = json.loads(LANDING_JSON.read_text())
    supported = [row for row in data["scoredLandings"] if row["score"] > 0]
    unsupported = [row for row in data["scoredLandings"] if row["score"] == 0 and row["targetText"]]

    rows = []
    for row in supported:
        row_terms = evidence_terms(row)
        line_words = interesting_words(row["targetText"])
        rows.append(
            {
                "sourceId": row["sourceId"],
                "sourceColor": color_of_source(row["sourceId"]),
                "sourceIndex": row["sourceIndex"],
                "targetLine0": row["targetLine"],
                "targetLine1": row["targetLine"] + 1,
                "score": row["score"],
                "layers": row["layers"],
                "targetUnits": row["targetUnits"],
                "targetText": row["targetText"],
                "lineFirstWord": first_word(row["targetText"]),
                "lineLastWord": last_word(row["targetText"]),
                "interestingLineWords": line_words,
                "evidenceTerms": row_terms,
                "preferredTerm": (row_terms or line_words or [first_word(row["targetText"])])[0],
            }
        )

    source_ids = [row["sourceId"] for row in rows]
    source_colors = [row["sourceColor"] for row in rows]
    source_indices = [str(row["sourceIndex"]) for row in rows]
    target_lines0 = [str(row["targetLine0"]) for row in rows]
    target_lines1 = [str(row["targetLine1"]) for row in rows]
    first_words = [row["lineFirstWord"] for row in rows]
    last_words = [row["lineLastWord"] for row in rows]
    preferred_terms = [row["preferredTerm"] for row in rows]
    evidence_terms_flat = [term for row in rows for term in row["evidenceTerms"]]

    unsupported_first = [first_word(row["targetText"]) for row in unsupported]
    unsupported_last = [last_word(row["targetText"]) for row in unsupported]

    streams = {
        "sourceIds": " ".join(source_ids),
        "sourceColors": "".join(source_colors),
        "sourceIndices": "".join(source_indices),
        "targetLines0": " ".join(target_lines0),
        "targetLines1": " ".join(target_lines1),
        "lineFirstWords": " ".join(first_words),
        "lineFirstInitials": initials(first_words),
        "lineLastWords": " ".join(last_words),
        "lineLastLetters": lasts(last_words),
        "preferredTerms": " ".join(preferred_terms),
        "preferredTermInitials": initials(preferred_terms),
        "evidenceTerms": " ".join(evidence_terms_flat),
        "evidenceTermInitials": initials(evidence_terms_flat),
        "scores": "".join(str(row["score"]) for row in rows),
        "unsupportedFirstWords": " ".join(unsupported_first),
        "unsupportedFirstInitials": initials(unsupported_first),
        "unsupportedLastWords": " ".join(unsupported_last),
        "unsupportedLastLetters": lasts(unsupported_last),
    }

    search_text = " ".join(streams.values()) + " " + " ".join(row["targetText"] for row in rows)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Supported page-76 landing-line sequence unit audit; no key derivation.",
        "supportedRows": rows,
        "unsupportedRows": unsupported,
        "streams": streams,
        "instructionTermHits": scan_instruction_terms(search_text),
        "assessment": [
            "The supported landing sequence is O1, B1, O3, O4, B4, B5 with source-color stream OBOOBB and index stream 113445.",
            "The obvious landing-line streams are not instruction-like: first-word initials BnlbNM, preferred-term initials Bbgecs, and evidence-term initials bbbsebbbecc.",
            "The supported #4 lines add real p78-graphic evidence, but they still do not define whether to extract a word, letter, line number, color, or adjacent unit.",
            "Treat supported landing lines as target-location evidence only.",
        ],
        "nextMove": "Look for a source/provenance rule outside the landing-line text, especially in p78/p79/p80 graphics or physical registration, that names the extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Supported Landing Sequence Units Audit",
        "",
        "Scope: test whether the supported page-76 landing-line sequence gives a simple instruction. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Supported Sequence",
        "",
        "| source | target line | score | preferred term | first word | last word | target text |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        text = row["targetText"].replace("|", "\\|")
        md.append(
            f"| {row['sourceId']} | {row['targetLine0']} | {row['score']} | `{row['preferredTerm']}` | `{row['lineFirstWord']}` | `{row['lineLastWord']}` | {text} |"
        )

    md.extend(["", "## Streams", ""])
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value}`")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The supported landing lines are coherent as a target set, but the simple streams do not become an instruction.",
            "- #4 remains active as target evidence because it is supported by p78 graphic/reflection layers.",
            "- No extraction unit is specified by the supported sequence itself.",
            "- Next best move: inspect source/provenance or physical-registration layers for a rule naming the unit to extract.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
