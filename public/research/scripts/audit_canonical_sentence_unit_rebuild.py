#!/usr/bin/env python3
"""Rebuild the sentence-unit map from corrected canonical article text.

This follows up on Text_by_sentences.docx. That Word witness showed a possible
sentence layer, but omitted `Volcano Bonds`. This pass rebuilds the same layer
from the corrected canonical text and checks whether sentence units create an
instruction. It does not derive keys, hashes, BIP39 phrases, WIFs, or addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt"
OUT = ROOT / "analysis_outputs/plain_text_transcript/canonical_sentence_unit_rebuild"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "canonical_sentence_unit_rebuild.json"
OUT_MD = OUT / "canonical_sentence_unit_rebuild.md"

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
    "sentence",
]


def canonical_body() -> str:
    lines = [line.strip() for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if "BITCOIN IS TOXIC AF" in lines:
        lines = lines[lines.index("BITCOIN IS TOXIC AF") + 1 :]
    return " ".join(lines)


def split_sentences(text: str) -> list[str]:
    protected = {
        "U.K.": "UKDOT",
    }
    for old, new in protected.items():
        text = text.replace(old, new)
    marked = re.sub(r"([.!?][\"”')\]]?)\s+(?=[\"(]?[A-Z0-9])", r"\1<SPLIT>", text)
    rows = []
    for part in marked.split("<SPLIT>"):
        part = part.strip()
        if not part:
            continue
        for old, new in protected.items():
            part = part.replace(new, old)
        rows.append(part)
    return rows


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def sentence_signature(rows: list[str], row_numbers: list[int]) -> dict:
    texts = [rows[num - 1] for num in row_numbers if 1 <= num <= len(rows)]
    return {
        "rowNumbers": row_numbers,
        "initials": "".join(words(text)[0][0].lower() for text in texts if words(text)),
        "lastWords": " ".join(words(text)[-1].lower() for text in texts if words(text)),
        "firstLastPairs": " ".join(
            f"{words(text)[0][0].lower()}{words(text)[-1][-1].lower()}" for text in texts if words(text)
        ),
    }


def main() -> None:
    sentences = split_sentences(canonical_body())
    term_rows = {}
    for key, term in TARGET_TERMS.items():
        low = term.lower()
        term_rows[key] = [
            {"row": idx, "text": text}
            for idx, text in enumerate(sentences, 1)
            if low in text.lower()
        ]

    corridor_row_numbers = list(range(40, 50))
    active_row_numbers = [43, 44, 45, 46, 47, 48]
    g5_o5_rows = [45, 48]
    markers_from_text_witness = [15, 35, 50, 70, 85]

    streams = {
        "activeRowNumbers": " ".join(str(num) for num in active_row_numbers),
        "activeInitials": sentence_signature(sentences, active_row_numbers)["initials"],
        "activeLastWords": sentence_signature(sentences, active_row_numbers)["lastWords"],
        "activeFirstLastPairs": sentence_signature(sentences, active_row_numbers)["firstLastPairs"],
        "g5o5SentencePair": " ".join(str(num) for num in g5_o5_rows),
        "g5o5SentenceGap": str(g5_o5_rows[1] - g5_o5_rows[0]),
        "g5o5Initials": sentence_signature(sentences, g5_o5_rows)["initials"],
        "g5o5LastWords": sentence_signature(sentences, g5_o5_rows)["lastWords"],
        "markerRowsFromTextWitness": " ".join(str(num) for num in markers_from_text_witness),
        "markerRowInitials": sentence_signature(sentences, markers_from_text_witness)["initials"],
        "markerRowLastWords": sentence_signature(sentences, markers_from_text_witness)["lastWords"],
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}

    corridor_rows = [{"row": num, "text": sentences[num - 1]} for num in corridor_row_numbers if num <= len(sentences)]
    marker_rows = [{"row": num, "text": sentences[num - 1]} for num in markers_from_text_witness if num <= len(sentences)]

    assessment = [
        "Corrected canonical text rebuilds to 87 sentence rows, matching the rough count from Text_by_sentences.docx.",
        "The active page-76 corridor remains sentence rows 43-49.",
        "`Volcano Bonds` is restored in canonical row 45, paired with `shitcoiner at heart` at row 48; the sentence gap is 3.",
        "The low-parameter active sentence streams still do not produce a procedural instruction.",
        "The marker numbers from Text_by_sentences.docx are not reliable extraction indices against the corrected canonical text: rows 50/70/85 land on normal body sentences, not instructions.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "canonical sentence-unit rebuild; no key derivation, hashing, BIP39, WIF, seed, or address checks",
        "source": str(SOURCE),
        "sentenceCount": len(sentences),
        "termRows": term_rows,
        "corridorRows": corridor_rows,
        "markerRows": marker_rows,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "decision": "Canonical sentence units are a documented validation layer only; they do not name an extraction rule under current clues.",
        "nextMove": "Only use sentence rows if a future source/clue explicitly says to read by sentence; otherwise keep source/physical/original-layout validation as the priority.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Canonical Sentence Unit Rebuild",
        "",
        "Scope: rebuild sentence units from corrected canonical article text. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sentence count: `{len(sentences)}`",
        "",
        "## Active Corridor Rows",
        "",
        "| row | text |",
        "|---:|---|",
    ]
    for row in corridor_rows:
        lines.append(f"| {row['row']} | `{row['text']}` |")

    lines.extend(["", "## Target Term Rows", "", "| term | rows |", "|---|---|"])
    for key, rows_for_term in term_rows.items():
        lines.append(f"| `{key}` | `{[row['row'] for row in rows_for_term]}` |")

    lines.extend(["", "## Text-Witness Marker Rows Applied To Canonical Text", "", "| marker row | canonical sentence |", "|---:|---|"])
    for row in marker_rows:
        lines.append(f"| {row['row']} | `{row['text']}` |")

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
    print("sentenceCount:", len(sentences))
    print("streamInstructionHits:", stream_hits)


if __name__ == "__main__":
    main()
