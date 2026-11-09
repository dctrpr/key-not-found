#!/usr/bin/env python3
"""Audit literal word operations from the repaired exact-edge trio.

The stable p78-frame signature selects:
    should sell | Volcano Bonds | shitcoiner at heart

This is meaningful English, so before abandoning it as direct key material this
pass checks a tiny set of human-readable operations suggested by the words:
`sell` as remove/interval, `heart` as middle/center, and `bond` as endpoints.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRIDOR_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
OUT = ROOT / "analysis_outputs/source_audit/exact_edge_literal_word_ops"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "exact_edge_literal_word_ops.json"
OUT_MD = OUT / "exact_edge_literal_word_ops.md"

EXACT = ["should sell", "Volcano Bonds", "shitcoiner at heart"]
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
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def letters(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text)


def center_chars(text: str) -> str:
    clean = letters(text)
    if not clean:
        return ""
    mid = len(clean) // 2
    if len(clean) % 2:
        return clean[mid]
    return clean[mid - 1 : mid + 1]


def word_centers(text: str) -> str:
    return "".join(center_chars(word) for word in words(text))


def endpoints(text: str) -> str:
    out = []
    for word in words(text):
        if len(word) == 1:
            out.append(word + word)
        else:
            out.append(word[0] + word[-1])
    return "".join(out)


def multiset_subtract(source: str, remove: str) -> str:
    remaining = Counter(letters(source).lower())
    for ch in letters(remove).lower():
        remaining[ch] -= 1
    out = []
    for ch in letters(source).lower():
        if remaining[ch] > 0:
            out.append(ch)
            remaining[ch] -= 1
    return "".join(out)


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def compact(text: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def find_record(records: list[dict], needle: str) -> dict:
    low = needle.lower()
    for record in records:
        if low in record["text"].lower():
            return record
    raise ValueError(needle)


def line_text(records: list[dict], start: int, end: int) -> str:
    rows = [record for record in records if start <= record["lineIndex"] <= end]
    return " | ".join(record["text"] for record in rows)


def word_at(record: dict, one_based: int) -> str:
    ws = words(record["text"])
    if 1 <= one_based <= len(ws):
        return ws[one_based - 1]
    return ""


def main() -> None:
    corridor = json.loads(CORRIDOR_JSON.read_text())
    records = corridor["records"]
    should_line = find_record(records, "should sell")
    volcano_line = find_record(records, "Volcano Bonds")
    heart_line = find_record(records, "shitcoiner at heart")
    could_sell_line = find_record(records, "could sell")

    exact_stream = " | ".join(EXACT)
    exact_no_spaces = letters(exact_stream)
    g5_o5_interval = line_text(records, volcano_line["lineIndex"], heart_line["lineIndex"])
    sell_interval = line_text(records, should_line["lineIndex"], could_sell_line["lineIndex"])
    g5_o5_middle_lines = line_text(records, volcano_line["lineIndex"] + 2, volcano_line["lineIndex"] + 3)

    operations = [
        {
            "name": "exact_stream",
            "reason": "read selected trio directly",
            "output": exact_stream,
        },
        {
            "name": "exact_reversed_words",
            "reason": "mirror-writing order reversal",
            "output": " | ".join(reversed(EXACT)),
        },
        {
            "name": "exact_reversed_chars",
            "reason": "literal mirror-writing character reversal",
            "output": exact_stream[::-1],
        },
        {
            "name": "word_centers",
            "reason": "`heart` as center letters of selected words",
            "output": word_centers(exact_stream),
        },
        {
            "name": "phrase_centers",
            "reason": "`heart` as center of each selected phrase",
            "output": "".join(center_chars(item) for item in EXACT),
        },
        {
            "name": "endpoints_bonded",
            "reason": "`bonds` as connect word endpoints",
            "output": endpoints(exact_stream),
        },
        {
            "name": "sell_remove_volcano_from_heart",
            "reason": "`sell` as remove/sell away Volcano Bonds letters from shitcoiner at heart",
            "output": multiset_subtract("shitcoiner at heart", "Volcano Bonds"),
        },
        {
            "name": "sell_remove_heart_from_volcano",
            "reason": "`sell` as remove/sell away shitcoiner-at-heart letters from Volcano Bonds",
            "output": multiset_subtract("Volcano Bonds", "shitcoiner at heart"),
        },
        {
            "name": "sell_remove_volcano_from_exact",
            "reason": "`sell` as remove/sell away the black-highlighted phrase from the exact stream",
            "output": multiset_subtract(exact_stream, "Volcano Bonds"),
        },
        {
            "name": "g5_o5_interval_full",
            "reason": "`Volcano Bonds` to `shitcoiner at heart` interval",
            "output": g5_o5_interval,
        },
        {
            "name": "g5_o5_interval_heart_lines",
            "reason": "`heart` as middle of the G5-to-O5 six-line interval",
            "output": g5_o5_middle_lines,
        },
        {
            "name": "sell_to_sell_interval",
            "reason": "from `should sell` to the next `could sell`",
            "output": sell_interval,
        },
        {
            "name": "line_index_words",
            "reason": "use exact phrase corridor indexes as same-line word positions",
            "output": " | ".join(
                [
                    word_at(should_line, should_line["corridorIndex"]),
                    word_at(volcano_line, volcano_line["corridorIndex"]),
                    word_at(heart_line, heart_line["corridorIndex"]),
                ]
            ),
        },
        {
            "name": "page_line_index_words",
            "reason": "use exact phrase page-line indexes as same-line word positions",
            "output": " | ".join(
                [
                    word_at(should_line, should_line["lineIndex"]),
                    word_at(volcano_line, volcano_line["lineIndex"]),
                    word_at(heart_line, heart_line["lineIndex"]),
                ]
            ),
        },
    ]

    for operation in operations:
        operation["outputCompact"] = compact(operation["output"])
        operation["instructionHits"] = instruction_hits(operation["output"])
        operation["lettersOnly"] = letters(operation["output"])
        operation["letterLength"] = len(operation["lettersOnly"])

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "literal-word operations from repaired exact-edge trio; no key derivation",
        "sourceReports": {
            "corridor": str(CORRIDOR_JSON.relative_to(ROOT)),
        },
        "exactTrio": EXACT,
        "lineFacts": {
            "shouldSell": {"lineIndex": should_line["lineIndex"], "corridorIndex": should_line["corridorIndex"], "text": should_line["text"]},
            "volcanoBonds": {"lineIndex": volcano_line["lineIndex"], "corridorIndex": volcano_line["corridorIndex"], "text": volcano_line["text"]},
            "shitcoinerAtHeart": {"lineIndex": heart_line["lineIndex"], "corridorIndex": heart_line["corridorIndex"], "text": heart_line["text"]},
            "couldSell": {"lineIndex": could_sell_line["lineIndex"], "corridorIndex": could_sell_line["corridorIndex"], "text": could_sell_line["text"]},
            "lineDifferences": [
                volcano_line["lineIndex"] - should_line["lineIndex"],
                heart_line["lineIndex"] - volcano_line["lineIndex"],
            ],
            "corridorDifferences": [
                volcano_line["corridorIndex"] - should_line["corridorIndex"],
                heart_line["corridorIndex"] - volcano_line["corridorIndex"],
            ],
        },
        "operations": operations,
        "operationsWithInstructionHits": [op for op in operations if op["instructionHits"]],
        "assessment": [
            "Literal `heart` operations select centers/middle lines but produce ordinary fragments, not a selector instruction.",
            "Literal `sell` operations as remove/interval produce letter debris or the ordinary corridor story, not a word/letter/key rule.",
            "The G5-to-O5 interval heart is the middle two lines around Novogratz / could sell, reinforcing the existing lower-corridor focus but not choosing an extraction unit.",
            "Using line/corridor indexes as same-line word positions is empty or ordinary text, not a clean rule.",
        ],
        "nextMove": "Close literal sell/heart/bond wordplay as a current-scan selector. Keep the exact-edge trio only as source-registration evidence unless a new source clue names one of these operations explicitly.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Exact-Edge Literal Word Operations",
        "",
        "Scope: test a tiny set of literal human-readable operations suggested by the repaired exact-edge trio: `should sell | Volcano Bonds | shitcoiner at heart`. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Exact trio: `{exact_stream}`",
        f"- Line indexes: should sell `{should_line['lineIndex']}`, Volcano Bonds `{volcano_line['lineIndex']}`, shitcoiner at heart `{heart_line['lineIndex']}`",
        f"- Corridor indexes: `{should_line['corridorIndex']}`, `{volcano_line['corridorIndex']}`, `{heart_line['corridorIndex']}`",
        f"- Line differences: `{result['lineFacts']['lineDifferences']}`",
        f"- Corridor differences: `{result['lineFacts']['corridorDifferences']}`",
        "",
        "## Operations",
        "",
        "| operation | reason | output | instruction hits | letters |",
        "|---|---|---|---|---:|",
    ]
    for op in operations:
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
    print("instruction-hit operations:", len(result["operationsWithInstructionHits"]))
    print("heart lines:", compact(g5_o5_middle_lines, 160))


if __name__ == "__main__":
    main()
