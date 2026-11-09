#!/usr/bin/env python3
"""Audit exact-edge line numbers and gaps as a local selector.

The previous pass found a stable repaired exact-edge trio on page 76:
    should sell | Volcano Bonds | shitcoiner at heart

Their page-line indexes are 25, 27, 32; their corridor indexes are
7, 9, 14; both gaps are 2 then 5. This pass tests whether those numbers
act as a simple human-readable selector inside the page-76 corridor.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRIDOR_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
OUT = ROOT / "analysis_outputs/source_audit/exact_edge_line_gap_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "exact_edge_line_gap_selector.json"
OUT_MD = OUT / "exact_edge_line_gap_selector.md"

EXACT_NEEDLES = ["should sell", "Volcano Bonds", "shitcoiner at heart"]
PAGE_LINE_NUMBERS = [25, 27, 32]
CORRIDOR_NUMBERS = [7, 9, 14]
GAP_NUMBERS = [2, 5]

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "line",
    "word",
    "letter",
    "index",
    "key",
    "private",
    "first",
    "last",
    "middle",
    "center",
    "down",
    "up",
    "left",
    "right",
    "below",
    "above",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def letters(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text)


def compact(text: str, limit: int = 150) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def alpha_value(n: int) -> str:
    """Map 1->A, 26->Z, wrapping larger positive values."""
    return chr(((n - 1) % 26) + ord("A"))


def word_at(text: str, one_based: int) -> str:
    ws = words(text)
    if 1 <= one_based <= len(ws):
        return ws[one_based - 1]
    return ""


def char_at_wrapped(text: str, one_based: int) -> str:
    clean = letters(text)
    if not clean:
        return ""
    return clean[(one_based - 1) % len(clean)]


def by_line(records: list[dict]) -> dict[int, dict]:
    return {record["lineIndex"]: record for record in records}


def by_corridor(records: list[dict]) -> dict[int, dict]:
    return {record["corridorIndex"]: record for record in records}


def find_record(records: list[dict], needle: str) -> dict:
    low = needle.lower()
    for record in records:
        if low in record["text"].lower():
            return record
    raise ValueError(needle)


def line_label(record: dict | None) -> str:
    if not record:
        return ""
    return f"L{record['lineIndex']}/C{record['corridorIndex']}: {record['text']}"


def select_words_on_lines(records: list[dict], positions: list[int]) -> str:
    chunks = []
    for record in records:
        chosen = [word_at(record["text"], pos) for pos in positions]
        chunks.append(" ".join(word for word in chosen if word))
    return " | ".join(chunks)


def select_words_from_stream(stream: str, positions: list[int]) -> str:
    ws = words(stream)
    return " ".join(ws[pos - 1] for pos in positions if 1 <= pos <= len(ws))


def operation(name: str, reason: str, output: str) -> dict:
    return {
        "name": name,
        "reason": reason,
        "output": output,
        "outputCompact": compact(output),
        "instructionHits": instruction_hits(output),
        "lettersOnly": letters(output),
        "letterLength": len(letters(output)),
    }


def main() -> None:
    corridor = json.loads(CORRIDOR_JSON.read_text(encoding="utf-8"))
    records = corridor["records"]
    line_map = by_line(records)
    corridor_map = by_corridor(records)

    exact_records = [find_record(records, needle) for needle in EXACT_NEEDLES]
    exact_stream = " | ".join(EXACT_NEEDLES)
    interval_records = [
        line_map[i]
        for i in range(exact_records[1]["lineIndex"], exact_records[2]["lineIndex"] + 1)
        if i in line_map
    ]
    highlighted_records = [r for r in records if r.get("highlights")]

    page_line_wrapped_to_corridor = [
        corridor_map[((n - 1) % len(records)) + 1] for n in PAGE_LINE_NUMBERS
    ]

    ops = [
        operation(
            "numbers_as_letters",
            "map page lines, corridor lines, and gaps through A1Z26",
            "page=" + "".join(alpha_value(n) for n in PAGE_LINE_NUMBERS)
            + " corridor=" + "".join(alpha_value(n) for n in CORRIDOR_NUMBERS)
            + " gaps=" + "".join(alpha_value(n) for n in GAP_NUMBERS),
        ),
        operation(
            "numbers_as_letters_reversed",
            "same A1Z26 streams in mirror order",
            "page=" + "".join(alpha_value(n) for n in reversed(PAGE_LINE_NUMBERS))
            + " corridor=" + "".join(alpha_value(n) for n in reversed(CORRIDOR_NUMBERS))
            + " gaps=" + "".join(alpha_value(n) for n in reversed(GAP_NUMBERS)),
        ),
        operation(
            "gap_words_on_exact_lines",
            "take words 2 and 5 from each exact-edge line",
            select_words_on_lines(exact_records, GAP_NUMBERS),
        ),
        operation(
            "gap_words_on_highlighted_corridor_lines",
            "take words 2 and 5 from every highlighted corridor line",
            select_words_on_lines(highlighted_records, GAP_NUMBERS),
        ),
        operation(
            "gap_words_in_exact_stream",
            "take words 2 and 5 from the exact trio stream",
            select_words_from_stream(exact_stream, GAP_NUMBERS),
        ),
        operation(
            "corridor_numbers_as_lines",
            "use 7, 9, 14 as corridor line selectors",
            " | ".join(line_label(corridor_map.get(n)) for n in CORRIDOR_NUMBERS),
        ),
        operation(
            "page_numbers_wrapped_to_corridor_lines",
            "wrap page line numbers 25, 27, 32 through the 14-line corridor",
            " | ".join(line_label(record) for record in page_line_wrapped_to_corridor),
        ),
        operation(
            "corridor_numbers_as_interval_words",
            "use 7, 9, 14 as word selectors in the G5-to-O5 interval",
            select_words_from_stream(" ".join(r["text"] for r in interval_records), CORRIDOR_NUMBERS),
        ),
        operation(
            "page_numbers_as_interval_words",
            "use 25, 27, 32 as word selectors in the G5-to-O5 interval",
            select_words_from_stream(" ".join(r["text"] for r in interval_records), PAGE_LINE_NUMBERS),
        ),
        operation(
            "gap_jump_forward",
            "start at should-sell, jump +2 to Volcano, then +5 to heart",
            " -> ".join(
                line_label(line_map.get(n))
                for n in [PAGE_LINE_NUMBERS[0], PAGE_LINE_NUMBERS[0] + GAP_NUMBERS[0], PAGE_LINE_NUMBERS[0] + GAP_NUMBERS[0] + GAP_NUMBERS[1]]
            ),
        ),
        operation(
            "gap_jump_backward",
            "mirror the same gap walk backward from heart",
            " -> ".join(
                line_label(line_map.get(n))
                for n in [PAGE_LINE_NUMBERS[2], PAGE_LINE_NUMBERS[2] - GAP_NUMBERS[1], PAGE_LINE_NUMBERS[2] - GAP_NUMBERS[1] - GAP_NUMBERS[0]]
            ),
        ),
        operation(
            "same_phrase_wrapped_chars_by_page_line",
            "use page line number as wrapped character index inside each exact phrase",
            "".join(char_at_wrapped(needle, n) for needle, n in zip(EXACT_NEEDLES, PAGE_LINE_NUMBERS)),
        ),
        operation(
            "same_phrase_wrapped_chars_by_corridor_line",
            "use corridor number as wrapped character index inside each exact phrase",
            "".join(char_at_wrapped(needle, n) for needle, n in zip(EXACT_NEEDLES, CORRIDOR_NUMBERS)),
        ),
    ]

    instruction_hit_ops = [op for op in ops if op["instructionHits"]]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "exact-edge line/corridor numbers and gaps as local selector; no key derivation",
        "sourceReports": {"corridor": str(CORRIDOR_JSON.relative_to(ROOT))},
        "exactNeedles": EXACT_NEEDLES,
        "lineFacts": {
            "pageLineNumbers": PAGE_LINE_NUMBERS,
            "corridorNumbers": CORRIDOR_NUMBERS,
            "gapNumbers": GAP_NUMBERS,
            "exactRecords": exact_records,
        },
        "operations": ops,
        "operationsWithInstructionHits": instruction_hit_ops,
        "assessment": [
            "A1Z26 number streams are short fragments (`YAF`, `GIN`, `BE`) and do not read as an instruction.",
            "Words 2 and 5 from the exact lines produce ordinary corridor fragments (`billion that`, `Volcano pay`, `because shitcoiner`).",
            "The gap walk only restates the known locator path from `should sell` to `Volcano Bonds` to `shitcoiner at heart`.",
            "Wrapped line numbers and interval word indexes produce ordinary text, not a rule naming word, letter, key, mirror, or direction.",
        ],
        "nextMove": "Close exact-edge line/corridor numbers and gaps as a direct numeric selector. Keep the 2/5 gaps only as structural locator evidence for the p76 lower corridor.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Exact-Edge Line/Gap Selector",
        "",
        "Scope: test whether the exact-edge line numbers `25,27,32`, corridor numbers `7,9,14`, and gaps `2,5` act as a simple local selector inside the page-76 corridor. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Exact trio: `{exact_stream}`",
        f"- Page line numbers: `{PAGE_LINE_NUMBERS}`",
        f"- Corridor numbers: `{CORRIDOR_NUMBERS}`",
        f"- Gap numbers: `{GAP_NUMBERS}`",
        "",
        "## Operations",
        "",
        "| operation | reason | output | instruction hits | letters |",
        "|---|---|---|---|---:|",
    ]
    for op in ops:
        lines.append(
            f"| `{op['name']}` | {op['reason']} | `{op['outputCompact']}` | `{op['instructionHits']}` | {op['letterLength']} |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("instruction-hit operations:", len(instruction_hit_ops))
    print("gap words on exact lines:", ops[2]["outputCompact"])


if __name__ == "__main__":
    main()
