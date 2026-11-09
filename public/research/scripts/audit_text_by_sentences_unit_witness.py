#!/usr/bin/env python3
"""Audit Text_by_sentences.docx as a possible sentence-unit witness.

This file is puzzle-related article text, so it is worth checking whether it
supplies the missing unit (`sentence`). This pass checks fidelity and low-
parameter sentence streams only. It does not derive keys or run BIP39/WIF/hash
checks.
"""

from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/text_by_sentences_unit_witness"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "text_by_sentences_unit_witness.json"
OUT_MD = OUT / "text_by_sentences_unit_witness.md"

DOC = Path("private_inputs/Desktop/Text_by_sentences.docx")
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

TARGET_TERMS = {
    "el_salvador": "El Salvador",
    "imf": "IMF",
    "buying_the_dip": "buying the dip",
    "bukele": "Bukele",
    "volcanoes": "volcanoes",
    "volcano_bonds": "Volcano Bonds",
    "one_billion": "$1 billion",
    "should_sell": "should sell",
    "novogratz": "Novogratz",
    "trust_that_guy": "trust that guy",
    "shitcoiner_at_heart": "shitcoiner at heart",
}

INSTRUCTION_TERMS = [
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
    "first",
    "last",
]


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def rows() -> list[str]:
    with zipfile.ZipFile(DOC) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    return [text for text in (paragraph_text(p) for p in root.findall(".//w:p", NS)) if text]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def main() -> None:
    sentence_rows = rows()
    marker_rows = []
    for idx, text in enumerate(sentence_rows, 1):
        match = re.match(r"^\((\d+)\)", text)
        if match:
            marker_rows.append(
                {
                    "row": idx,
                    "marker": int(match.group(1)),
                    "deltaRowMinusMarker": idx - int(match.group(1)),
                    "text": text,
                }
            )

    term_rows = {}
    for key, term in TARGET_TERMS.items():
        low_term = term.lower()
        term_rows[key] = [
            {"row": idx, "text": text}
            for idx, text in enumerate(sentence_rows, 1)
            if low_term in text.lower()
        ]

    corridor_rows = [
        {"row": idx, "text": sentence_rows[idx - 1]}
        for idx in range(40, 50)
        if idx <= len(sentence_rows)
    ]
    priority_rows = [43, 44, 45, 46, 47, 48]
    priority_texts = [sentence_rows[idx - 1] for idx in priority_rows if idx <= len(sentence_rows)]
    streams = {
        "markerValues": " ".join(str(row["marker"]) for row in marker_rows),
        "markerRowDeltas": " ".join(str(row["deltaRowMinusMarker"]) for row in marker_rows),
        "priorityRowNumbers": " ".join(str(idx) for idx in priority_rows),
        "priorityInitials": "".join(words(text)[0][0].lower() for text in priority_texts if words(text)),
        "priorityLastWords": " ".join(words(text)[-1].lower() for text in priority_texts if words(text)),
        "g5o5SentencePair": "45 48",
        "g5o5SentenceGap": "3",
        "sentence45InitialLast": f"{words(sentence_rows[44])[0][0].lower()}{words(sentence_rows[44])[-1][-1].lower()}",
        "sentence48InitialLast": f"{words(sentence_rows[47])[0][0].lower()}{words(sentence_rows[47])[-1][-1].lower()}",
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}
    missing_priority_terms = [key for key, rows_for_term in term_rows.items() if not rows_for_term]

    assessment = [
        "`Text_by_sentences.docx` is article-related and supplies a sentence-unit layer, but it is a working transcript rather than original layout/geometry.",
        "The active page-76 corridor is represented by sentence rows 43-49.",
        "The crucial `Volcano Bonds` phrase is missing from this witness, so it cannot be trusted as the source for the G5/O5 pair.",
        "Sentence markers `(15)`, `(35)`, `(50)`, `(70)`, and `(85)` are mostly row/count aids, not a clean selector.",
        "Low-parameter sentence streams from the active corridor produce no instruction hits.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Text_by_sentences.docx sentence-unit witness audit; no key derivation, hashing, BIP39, WIF, seed, or address checks",
        "path": str(DOC),
        "rowCount": len(sentence_rows),
        "markerRows": marker_rows,
        "termRows": term_rows,
        "missingPriorityTerms": missing_priority_terms,
        "corridorRows": corridor_rows,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "decision": "Keep Text_by_sentences.docx as a sentence-count working witness only; do not use it as a source-backed selector because it lacks `Volcano Bonds` and original formatting.",
        "nextMove": "If sentence units are ever named by an external clue, rebuild them from the corrected canonical article text, not this imperfect witness.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Text By Sentences Unit Witness",
        "",
        "Scope: audit `Text_by_sentences.docx` as a possible sentence-unit witness. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Rows: `{len(sentence_rows)}`",
        f"- Missing priority terms: `{missing_priority_terms}`",
        "",
        "## Marker Rows",
        "",
        "| row | marker | row-marker | text |",
        "|---:|---:|---:|---|",
    ]
    for row in marker_rows:
        lines.append(f"| {row['row']} | {row['marker']} | {row['deltaRowMinusMarker']} | `{row['text']}` |")

    lines.extend(["", "## Active Corridor Rows", "", "| row | text |", "|---:|---|"])
    for row in corridor_rows:
        lines.append(f"| {row['row']} | `{row['text']}` |")

    lines.extend(["", "## Target Term Rows", "", "| term | rows |", "|---|---|"])
    for key, rows_for_term in term_rows.items():
        row_nums = [row["row"] for row in rows_for_term]
        lines.append(f"| `{key}` | `{row_nums}` |")

    lines.extend(["", "## Low-Parameter Streams", "", "| stream | value | instruction hits |", "|---|---|---|"])
    for name, value in streams.items():
        lines.append(f"| `{name}` | `{value}` | `{stream_hits.get(name, [])}` |")

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("missingPriorityTerms:", missing_priority_terms)
    print("streamInstructionHits:", stream_hits)


if __name__ == "__main__":
    main()
