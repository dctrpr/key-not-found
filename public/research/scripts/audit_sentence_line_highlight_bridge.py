#!/usr/bin/env python3
"""Bridge canonical sentence rows to page-76 visual lines/highlights.

The sentence-unit rebuild restored `Volcano Bonds` at sentence row 45 and
`shitcoiner at heart` at row 48. This pass checks whether joining sentence rows
to the known page-76 line/highlight model supplies the missing extraction unit.

No key derivation, hashing, BIP39, WIF, seed, or address checks are run.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SENTENCE_JSON = ROOT / "analysis_outputs/plain_text_transcript/canonical_sentence_unit_rebuild/canonical_sentence_unit_rebuild.json"
LINE_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
OUT = ROOT / "analysis_outputs/plain_text_transcript/sentence_line_highlight_bridge"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "sentence_line_highlight_bridge.json"
OUT_MD = OUT / "sentence_line_highlight_bridge.md"

ACTIVE_SENTENCE_ROWS = [43, 44, 45, 46, 47, 48]
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
STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "but",
    "he",
    "he's",
    "i",
    "in",
    "it",
    "of",
    "on",
    "the",
    "them",
    "to",
    "was",
    "when",
    "with",
}


def words(text: str) -> list[str]:
    return [word.lower() for word in re.findall(r"[A-Za-z0-9'$]+", text)]


def content_words(text: str) -> list[str]:
    return [word for word in words(text) if word not in STOPWORDS]


def overlap_count(left: str, right: str) -> int:
    a = Counter(content_words(left))
    b = Counter(content_words(right))
    return sum(min(a[key], b[key]) for key in a.keys() & b.keys())


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def line_span(records: list[dict]) -> str:
    if not records:
        return ""
    indexes = [row["lineIndex"] for row in records]
    return str(indexes[0]) if len(indexes) == 1 else f"{indexes[0]}-{indexes[-1]}"


def corridor_span(records: list[dict]) -> str:
    if not records:
        return ""
    indexes = [row["corridorIndex"] for row in records]
    return str(indexes[0]) if len(indexes) == 1 else f"{indexes[0]}-{indexes[-1]}"


def main() -> None:
    sentences_data = json.loads(SENTENCE_JSON.read_text(encoding="utf-8"))
    line_data = json.loads(LINE_JSON.read_text(encoding="utf-8"))
    sentence_by_row = {row["row"]: row["text"] for row in sentences_data["corridorRows"]}
    line_records = line_data["records"]

    bridges = []
    for sentence_row in ACTIVE_SENTENCE_ROWS:
        sentence_text = sentence_by_row[sentence_row]
        overlaps = []
        for line in line_records:
            count = overlap_count(sentence_text, line["text"])
            if count >= 2:
                overlaps.append(
                    {
                        "lineIndex": line["lineIndex"],
                        "corridorIndex": line["corridorIndex"],
                        "overlapContentWords": count,
                        "lineInitial": line["initial"],
                        "lineLastWord": line["lastWord"],
                        "highlights": line["highlights"],
                        "boldLetters": line["boldLetters"],
                        "partialBoldLetters": line["partialBoldLetters"],
                        "text": line["text"],
                    }
                )
        highlights = []
        for row in overlaps:
            highlights.extend(row["highlights"])
        bridges.append(
            {
                "sentenceRow": sentence_row,
                "sentenceText": sentence_text,
                "pageLineSpan": line_span(overlaps),
                "corridorSpan": corridor_span(overlaps),
                "lineInitials": "".join(row["lineInitial"] for row in overlaps),
                "lineLastWords": " ".join(row["lineLastWord"] for row in overlaps),
                "highlightCount": len(highlights),
                "highlights": highlights,
                "lineOverlaps": overlaps,
            }
        )

    bridge_by_sentence = {row["sentenceRow"]: row for row in bridges}
    g5_sentence = bridge_by_sentence[45]
    o5_sentence = bridge_by_sentence[48]
    g5_metrics = {
        "g5Sentence": 45,
        "o5Sentence": 48,
        "sentenceGap": 3,
        "g5PageLine": 27,
        "o5PageLine": 32,
        "pageLineGap": 5,
        "g5CorridorIndex": 9,
        "o5CorridorIndex": 14,
        "corridorGap": 5,
        "sentenceToPageLineDiffs": [45 - 27, 48 - 32],
    }

    streams = {
        "sentenceToLineSpans": ";".join(f"{row['sentenceRow']}:{row['pageLineSpan']}" for row in bridges),
        "sentenceToCorridorSpans": ";".join(f"{row['sentenceRow']}:{row['corridorSpan']}" for row in bridges),
        "sentenceLineInitials": "".join(row["lineInitials"] for row in bridges),
        "sentenceLineLastWords": " | ".join(row["lineLastWords"] for row in bridges),
        "highlightCountsBySentence": " ".join(str(row["highlightCount"]) for row in bridges),
        "highlightTermsBySentence": " | ".join(",".join(row["highlights"]) or "-" for row in bridges),
        "g5o5SentenceLineCorridorTriples": "45-27-9 48-32-14",
        "g5o5Gaps": "3 5 5",
        "g5o5SentenceMinusLine": "18 16",
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}

    assessment = [
        "Sentence row 45 cleanly carries the `Volcano Bonds`/Bukele/IMF source sentence and spans page lines 23-28.",
        "Sentence row 48 carries `shitcoiner at heart` and maps to page line 32.",
        "The G5/O5 pair is therefore sentence rows 45/48, page lines 27/32, and corridor indexes 9/14.",
        "The resulting gaps are sentence gap 3 and line/corridor gap 5; this is a stable locator but not an instruction.",
        "Line 28 and line 31 are mixed visual lines that cross sentence boundaries, so sentence units and printed line units do not collapse into one clean extraction grid.",
        "No sentence-line/highlight stream names a procedural unit such as read/take/first/last/word/letter.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "canonical sentence rows bridged to page-76 line/highlight model; no key derivation, hashing, BIP39, WIF, seed, or address checks",
        "bridges": bridges,
        "g5o5Metrics": g5_metrics,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "decision": "Use sentence-line/highlight bridge as validation/locator evidence only; it does not supply the missing extraction unit.",
        "nextMove": "Keep source/physical/original-layout validation as priority. Reopen sentence-line bridge only if a new clue names sentence, line, or gap units.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Sentence-Line Highlight Bridge",
        "",
        "Scope: bridge canonical sentence rows to the page-76 visual line/highlight model. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Sentence Bridges",
        "",
        "| sentence | page lines | corridor | line initials | highlights | text |",
        "|---:|---|---|---|---|---|",
    ]
    for row in bridges:
        lines.append(
            f"| {row['sentenceRow']} | `{row['pageLineSpan']}` | `{row['corridorSpan']}` | `{row['lineInitials']}` | `{row['highlights']}` | `{row['sentenceText']}` |"
        )

    lines.extend(
        [
            "",
            "## G5/O5 Metrics",
            "",
            f"- Sentence pair: `{g5_metrics['g5Sentence']} -> {g5_metrics['o5Sentence']}`",
            f"- Page-line pair: `{g5_metrics['g5PageLine']} -> {g5_metrics['o5PageLine']}`",
            f"- Corridor pair: `{g5_metrics['g5CorridorIndex']} -> {g5_metrics['o5CorridorIndex']}`",
            f"- Gaps: sentence `{g5_metrics['sentenceGap']}`, page-line `{g5_metrics['pageLineGap']}`, corridor `{g5_metrics['corridorGap']}`",
            f"- Sentence minus page-line diffs: `{g5_metrics['sentenceToPageLineDiffs']}`",
            "",
            "## Streams",
            "",
            "| stream | value | instruction hits |",
            "|---|---|---|",
        ]
    )
    for name, value in streams.items():
        lines.append(f"| `{name}` | `{value}` | `{stream_hits.get(name, [])}` |")

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("streamInstructionHits:", stream_hits)


if __name__ == "__main__":
    main()
