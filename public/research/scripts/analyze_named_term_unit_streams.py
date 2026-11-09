#!/usr/bin/env python3
"""Audit externally named term streams from the page-76 line-offset map.

This is a low-parameter extraction-unit test. It does not hash text or check
keys. It asks: if the line-offset map is real, and the external layers name
particular words on the landing lines, do those named words/initials/indexed
letters form a readable instruction?
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_JSON = ROOT / "analysis_outputs/source_audit/supported_landing_sequence_units/supported_landing_sequence_units.json"
WEAK_JSON = ROOT / "analysis_outputs/source_audit/page76_weak_landing_support/page76_weak_landing_support.json"
LINE_JSON = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"

OUT = ROOT / "analysis_outputs/source_audit/named_term_unit_streams"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "named_term_unit_streams.json"
OUT_MD = OUT / "named_term_unit_streams.md"


ORDER = ["O1", "O2", "B1", "B2", "O3", "B3", "O4", "B4", "B5"]
INSTRUCTION_WORDS = {
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "seed",
    "wif",
    "address",
    "below",
    "above",
    "down",
    "up",
    "first",
    "last",
    "index",
}


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def text_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def unique_preserve(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        norm = normalize_token(value)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


def natural_order_terms(line_text: str, allowed: set[str]) -> list[str]:
    out = []
    for token in text_tokens(line_text):
        norm = normalize_token(token)
        if norm in allowed:
            out.append(norm)
    return unique_preserve(out)


def evidence_terms(base_row: dict) -> list[str]:
    terms: list[str] = []
    for item in base_row.get("evidence", []):
        for chunk in re.findall(r"terms:\s*([^;]+)", item):
            terms.extend(part.strip() for part in chunk.split(","))
    return unique_preserve(terms)


def source_color(source_id: str) -> str:
    return source_id[0]


def source_index(source_id: str) -> int:
    return int(source_id[1:])


def char_at(term: str, index: int, from_end: bool = False) -> str:
    if not term:
        return ""
    pos = index - 1
    if pos >= len(term):
        return ""
    return term[-index] if from_end else term[pos]


def stream_record(name: str, values: list[str]) -> dict:
    compact = "".join(values)
    words = [normalize_token(v) for v in values if normalize_token(v)]
    instruction_hits = sorted(set(words) & INSTRUCTION_WORDS)
    compact_hits = sorted(word for word in INSTRUCTION_WORDS if word in compact.lower())
    return {
        "name": name,
        "values": values,
        "joinedWithSpaces": " ".join(values),
        "compact": compact,
        "instructionWordHits": instruction_hits,
        "instructionSubstringHits": compact_hits,
    }


def build_rows() -> list[dict]:
    supported = json.loads(SUPPORTED_JSON.read_text())
    weak = json.loads(WEAK_JSON.read_text())
    line = json.loads(LINE_JSON.read_text())

    rows_by_id = {row["sourceId"]: row for row in line["scoredLandings"]}
    supported_by_id = {row["sourceId"]: row for row in supported["supportedRows"]}
    weak_by_id = {row["sourceId"]: row for row in weak["auditedLandings"]}

    out = []
    for sid in ORDER:
        base = rows_by_id[sid]
        terms: list[str] = []
        provenance: list[str] = []
        preferred = ""

        if sid in supported_by_id:
            sup = supported_by_id[sid]
            preferred = normalize_token(sup["preferredTerm"])
            # Keep only the externally repeated terms, not every word on the line.
            terms.extend(unique_preserve(sup.get("evidenceTerms", [])))
            terms.extend(evidence_terms(base))
            provenance.extend(sup.get("layers", []))

        if sid in weak_by_id:
            weak_row = weak_by_id[sid]
            if weak_row["graphSupport"]:
                allowed = set()
                for edge in weak_row["graphSupport"]:
                    allowed.update(normalize_token(term) for term in edge.get("matchedTerms", []))
                natural = natural_order_terms(weak_row["targetText"], allowed)
                terms.extend(natural)
                provenance.append("reflected carrier terms")
                if not preferred and natural:
                    preferred = natural[0]
            if weak_row["packageNumberSupport"]:
                for hit in weak_row["packageNumberSupport"]:
                    word = hit.get("hits", {}).get("oneBasedWord")
                    if word:
                        terms.append(word)
                        provenance.append(f"p80 number {hit['number']}")
                        if not preferred:
                            preferred = normalize_token(word)
            if weak_row["packageTermSupport"]:
                for hit in weak_row["packageTermSupport"]:
                    for fam in hit.get("familyTerms", []):
                        # Use the landing-side word as the term selected on page 76.
                        terms.append(fam["landingToken"])
                        provenance.append(f"p80 term {hit['packageLabel']}")
                        if not preferred:
                            preferred = normalize_token(fam["landingToken"])

        terms = unique_preserve(terms)
        if terms:
            line_order = natural_order_terms(base["targetText"], set(terms))
            # If a named source token is not literally present on the landing
            # line, preserve it after the landing-line terms.
            terms = unique_preserve(line_order + terms)
        row = {
            "sourceId": sid,
            "sourceColor": source_color(sid),
            "sourceIndex": source_index(sid),
            "targetLine": base["targetLine"],
            "targetText": base["targetText"],
            "namedTerms": terms,
            "preferredTerm": preferred or (terms[0] if terms else ""),
            "provenance": unique_preserve(provenance),
        }
        out.append(row)
    return out


def indexed_letters(rows: list[dict], use_last_term: bool = False, from_end: bool = False) -> list[str]:
    letters = []
    for row in rows:
        if not row["namedTerms"]:
            continue
        term = row["namedTerms"][-1] if use_last_term else row["namedTerms"][0]
        letters.append(char_at(term, row["sourceIndex"], from_end=from_end))
    return letters


def main() -> None:
    rows = build_rows()
    rows_with_terms = [row for row in rows if row["namedTerms"]]

    first_terms = [row["namedTerms"][0] for row in rows_with_terms]
    last_terms = [row["namedTerms"][-1] for row in rows_with_terms]
    preferred_terms = [row["preferredTerm"] for row in rows_with_terms if row["preferredTerm"]]
    all_terms = [term for row in rows_with_terms for term in row["namedTerms"]]
    source_index_terms = [
        row["namedTerms"][(row["sourceIndex"] - 1) % len(row["namedTerms"])]
        for row in rows_with_terms
    ]
    color_first_last = [
        row["namedTerms"][0] if row["sourceColor"] == "O" else row["namedTerms"][-1]
        for row in rows_with_terms
    ]
    color_last_first = [
        row["namedTerms"][-1] if row["sourceColor"] == "O" else row["namedTerms"][0]
        for row in rows_with_terms
    ]

    streams = [
        stream_record("preferred_terms_forward", preferred_terms),
        stream_record("preferred_terms_reverse", list(reversed(preferred_terms))),
        stream_record("all_named_terms_forward", all_terms),
        stream_record("all_named_terms_reverse", list(reversed(all_terms))),
        stream_record("first_named_term_per_row", first_terms),
        stream_record("last_named_term_per_row", last_terms),
        stream_record("source_index_selected_terms", source_index_terms),
        stream_record("color_rule_O_first_B_last", color_first_last),
        stream_record("color_rule_O_last_B_first", color_last_first),
        stream_record("preferred_initials", [term[0] for term in preferred_terms if term]),
        stream_record("all_named_initials", [term[0] for term in all_terms if term]),
        stream_record("source_index_letters_first_terms", indexed_letters(rows_with_terms)),
        stream_record("source_index_letters_last_terms", indexed_letters(rows_with_terms, use_last_term=True)),
        stream_record("source_index_letters_first_terms_from_end", indexed_letters(rows_with_terms, from_end=True)),
        stream_record("source_index_letters_last_terms_from_end", indexed_letters(rows_with_terms, use_last_term=True, from_end=True)),
    ]

    flagged = [
        stream
        for stream in streams
        if stream["instructionWordHits"] or stream["instructionSubstringHits"]
    ]

    all_named_summary = " ".join(all_terms)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Externally named term/unit stream audit; no key candidates, hashes, seed phrases, or address checks.",
        "rows": rows,
        "streams": streams,
        "flaggedStreams": flagged,
        "assessment": [
            "Adding the secondary-supported #2 terms does not turn the named-term streams into a readable instruction.",
            "The strongest expanded preferred sequence is `bitcoin george bitcoin dulled genitals earnings sell heart`, with initials `bgbdgesh`; reversed and color-rule variants are also not instruction-like.",
            f"All-named terms mainly restate source provenance: `{all_named_summary}`.",
            "Source-index letter picks and O/B first-last rules produce short nonsense strings rather than `read/take/mirror/word/letter/key` language.",
            "This closes externally named terms as a standalone extraction unit, while preserving them as a cleaner locator ledger.",
        ],
        "nextMove": "Use the named-term ledger to drive a visual/typography audit around only those exact words on page 76, especially whether Typeka states or highlight edges mark one letter per named word.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Named Term Unit Streams Audit",
        "",
        "Scope: test whether externally named words from the page-76 line-offset map form a readable instruction. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Named Term Rows",
        "",
        "| source | line | named terms | preferred | provenance | target text |",
        "|---|---:|---|---|---|---|",
    ]
    for row in rows:
        terms = " ".join(row["namedTerms"]) or "-"
        provenance = ", ".join(row["provenance"]) or "-"
        text = row["targetText"].replace("|", "\\|")
        md.append(
            f"| `{row['sourceId']}` | {row['targetLine']} | `{terms}` | `{row['preferredTerm'] or '-'}` | {provenance} | {text} |"
        )

    md.extend(["", "## Stream Checks", "", "| stream | spaced | compact | instruction hits |", "|---|---|---|---|"])
    for stream in streams:
        hits = ",".join(stream["instructionWordHits"] + stream["instructionSubstringHits"]) or "-"
        md.append(
            f"| `{stream['name']}` | `{stream['joinedWithSpaces']}` | `{stream['compact']}` | `{hits}` |"
        )

    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    md.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
