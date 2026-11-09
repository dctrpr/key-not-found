#!/usr/bin/env python3
"""Test the literal `Bonds` boundary-unit rule on the exact-edge trio.

The closest current local path is the repaired p78 exact-edge trio:

    should sell | Volcano Bonds | shitcoiner at heart

After the literal `heart` unit failed, this pass tests the other explicit unit
word inside the trio: `Bonds`. A conservative human-readable interpretation is
word/phrase bonds: the adjacent letters at word boundaries and phrase
boundaries. This pass does not derive keys, hashes, mnemonics, WIFs, or
addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/exact_trio_bond_boundary_rule"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "exact_trio_bond_boundary_rule.json"
OUT_MD = OUT / "exact_trio_bond_boundary_rule.md"

TRIO = ["should sell", "Volcano Bonds", "shitcoiner at heart"]
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
    "middle",
    "heart",
    "bond",
    "join",
    "edge",
    "down",
    "up",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def word_bonds(ws: list[str]) -> list[dict]:
    rows = []
    for idx in range(len(ws) - 1):
        left = ws[idx]
        right = ws[idx + 1]
        rows.append(
            {
                "leftWord": left,
                "rightWord": right,
                "lastFirst": left[-1].lower() + right[0].lower(),
                "firstLast": left[0].lower() + right[-1].lower(),
                "outside": left[0].lower() + right[-1].lower(),
                "inside": left[-1].lower() + right[0].lower(),
            }
        )
    return rows


def phrase_bonds(phrases: list[str]) -> list[dict]:
    rows = []
    phrase_words = [words(phrase) for phrase in phrases]
    for idx in range(len(phrase_words) - 1):
        left_phrase = phrase_words[idx]
        right_phrase = phrase_words[idx + 1]
        left = left_phrase[-1]
        right = right_phrase[0]
        rows.append(
            {
                "leftPhrase": phrases[idx],
                "rightPhrase": phrases[idx + 1],
                "leftWord": left,
                "rightWord": right,
                "lastFirst": left[-1].lower() + right[0].lower(),
                "firstLast": left[0].lower() + right[-1].lower(),
            }
        )
    return rows


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def main() -> None:
    phrase_rows = []
    for phrase in TRIO:
        ws = words(phrase)
        phrase_rows.append(
            {
                "phrase": phrase,
                "words": ws,
                "wordBonds": word_bonds(ws),
            }
        )
    p_bonds = phrase_bonds(TRIO)

    all_word_bonds = [bond for row in phrase_rows for bond in row["wordBonds"]]
    streams = {
        "wordBondInsideForward": "".join(b["inside"] for b in all_word_bonds),
        "wordBondInsideReverse": "".join(b["inside"] for b in reversed(all_word_bonds)),
        "wordBondOutsideForward": "".join(b["outside"] for b in all_word_bonds),
        "wordBondOutsideReverse": "".join(b["outside"] for b in reversed(all_word_bonds)),
        "phraseBondLastFirstForward": "".join(b["lastFirst"] for b in p_bonds),
        "phraseBondLastFirstReverse": "".join(b["lastFirst"] for b in reversed(p_bonds)),
        "phraseBondFirstLastForward": "".join(b["firstLast"] for b in p_bonds),
        "phraseBondFirstLastReverse": "".join(b["firstLast"] for b in reversed(p_bonds)),
        "wordBondPairsForward": " ".join(b["inside"] for b in all_word_bonds),
        "phraseBondPairsForward": " ".join(b["lastFirst"] for b in p_bonds),
        "allBondPairsForward": " ".join([b["inside"] for b in all_word_bonds] + [b["lastFirst"] for b in p_bonds]),
    }
    hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}

    assessment = [
        "The `Bonds` unit is locally justified only because `Volcano Bonds` is one of the exact-edge phrases.",
        "Word-boundary and phrase-boundary streams produce short fragments such as `dsobrath`, `slvsstat`, `lvss`, and `sobr`.",
        "No boundary stream creates an instruction term or a readable unit that would tell us what to extract next.",
        "This closes literal bond/boundary extraction from the exact trio as a standalone selector.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "literal Bonds/boundary-unit test on repaired exact-edge trio; no key derivation",
        "sourcePath": "repaired p78 exact-edge trio",
        "trio": TRIO,
        "phraseRows": phrase_rows,
        "phraseBonds": p_bonds,
        "streams": streams,
        "instructionHits": hits,
        "assessment": assessment,
        "decision": "Close literal bond/boundary extraction from the exact trio as a selector.",
        "nextMove": "The closest local path remains blocked on a source-backed extraction unit. Continue only with better source evidence or a new explicit rule.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Exact Trio Bond-Boundary Rule",
        "",
        "Scope: test `Bonds` as a literal word/phrase-boundary unit on the repaired exact-edge trio. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Trio: `{' | '.join(TRIO)}`",
        "",
        "## Word Bonds",
        "",
        "| phrase | word bond | inside last/first | outside first/last |",
        "|---|---|---|---|",
    ]
    for row in phrase_rows:
        for bond in row["wordBonds"]:
            lines.append(
                f"| `{row['phrase']}` | `{bond['leftWord']} / {bond['rightWord']}` | `{bond['inside']}` | `{bond['outside']}` |"
            )
    lines.extend(["", "## Phrase Bonds", "", "| phrase bond | last/first | first/last |", "|---|---|---|"])
    for bond in p_bonds:
        lines.append(
            f"| `{bond['leftPhrase']} -> {bond['rightPhrase']}` | `{bond['lastFirst']}` | `{bond['firstLast']}` |"
        )
    lines.extend(["", "## Streams", "", "| stream | value | instruction hits |", "|---|---|---|"])
    for name, value in streams.items():
        lines.append(f"| `{name}` | `{value}` | `{instruction_hits(value)}` |")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("instructionHits:", hits)


if __name__ == "__main__":
    main()
