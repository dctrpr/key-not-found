#!/usr/bin/env python3
"""Test the literal `sell` removal rule on the repaired exact-edge trio.

The exact-edge trio is:

    should sell | Volcano Bonds | shitcoiner at heart

Because `should sell` is the only imperative-like phrase in the trio, this
bounded pass treats `sell` as "sell off/remove" and inspects only the exposed
word/phrase joins after removing the named middle phrase or the word `sell`.

No OCR extraction, key derivation, hashes, mnemonics, WIFs, or addresses are
generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/exact_trio_sell_removal_rule"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "exact_trio_sell_removal_rule.json"
OUT_MD = OUT / "exact_trio_sell_removal_rule.md"

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
    "sell",
    "down",
    "up",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def compact(texts: list[str]) -> str:
    return "".join("".join(words(text)).lower() for text in texts)


def initials(texts: list[str]) -> str:
    out = []
    for text in texts:
        ws = words(text)
        out.append(ws[0][0].lower() if ws else "")
    return "".join(out)


def lasts(texts: list[str]) -> str:
    out = []
    for text in texts:
        ws = words(text)
        out.append(ws[-1][-1].lower() if ws else "")
    return "".join(out)


def boundary(left: str, right: str) -> dict:
    lw = words(left)
    rw = words(right)
    if not lw or not rw:
        return {}
    left_word = lw[-1]
    right_word = rw[0]
    return {
        "leftWord": left_word,
        "rightWord": right_word,
        "lastFirst": left_word[-1].lower() + right_word[0].lower(),
        "firstLast": left_word[0].lower() + right_word[-1].lower(),
        "joinedWords": f"{left_word} {right_word}",
    }


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def main() -> None:
    scenarios = []

    remove_middle = [TRIO[0], TRIO[2]]
    scenarios.append(
        {
            "name": "sell_off_middle_phrase",
            "operation": "remove `Volcano Bonds` from the exact-edge trio",
            "remainingPhrases": remove_middle,
            "exposedBoundary": boundary(remove_middle[0], remove_middle[1]),
        }
    )

    remove_sell_word = ["should", TRIO[1], TRIO[2]]
    scenarios.append(
        {
            "name": "sell_off_sell_word",
            "operation": "remove the word `sell` from `should sell`",
            "remainingPhrases": remove_sell_word,
            "exposedBoundary": boundary(remove_sell_word[0], remove_sell_word[1]),
        }
    )

    remove_command_phrase = [TRIO[1], TRIO[2]]
    scenarios.append(
        {
            "name": "sell_off_command_phrase",
            "operation": "remove the whole `should sell` phrase",
            "remainingPhrases": remove_command_phrase,
            "exposedBoundary": boundary(remove_command_phrase[0], remove_command_phrase[1]),
        }
    )

    streams = {}
    for scenario in scenarios:
        name = scenario["name"]
        phrases = scenario["remainingPhrases"]
        b = scenario["exposedBoundary"] or {}
        streams[f"{name}_joined"] = " ".join(phrases)
        streams[f"{name}_compact"] = compact(phrases)
        streams[f"{name}_initials"] = initials(phrases)
        streams[f"{name}_lasts"] = lasts(phrases)
        streams[f"{name}_boundaryLastFirst"] = b.get("lastFirst", "")
        streams[f"{name}_boundaryFirstLast"] = b.get("firstLast", "")
        streams[f"{name}_boundaryWords"] = b.get("joinedWords", "")

    raw_hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}
    actionable_streams = {
        name: value
        for name, value in streams.items()
        if any(
            token in name
            for token in ["compact", "initials", "lasts", "boundaryLastFirst", "boundaryFirstLast"]
        )
    }
    hits = {
        name: instruction_hits(value)
        for name, value in actionable_streams.items()
        if instruction_hits(value)
    }

    assessment = [
        "The `sell` rule is locally justified only because `should sell` is part of the repaired exact-edge trio.",
        "Removing `Volcano Bonds`, removing `sell`, or removing the whole `should sell` phrase leaves ordinary phrase joins such as `sell shitcoiner`, `should Volcano`, and `Bonds shitcoiner`.",
        "The resulting initials, lasts, compact text, and exposed boundary pairs do not create a new instruction or extraction unit.",
        "This closes literal `sell off/remove` extraction from the exact trio as a standalone selector.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "literal sell/removal-unit test on repaired exact-edge trio; no key derivation",
        "sourcePath": "repaired p78 exact-edge trio",
        "trio": TRIO,
        "scenarios": scenarios,
        "streams": streams,
        "rawInstructionHits": raw_hits,
        "actionableInstructionHits": hits,
        "assessment": assessment,
        "decision": "Close literal sell/remove extraction from the exact trio as a selector.",
        "nextMove": "The exact trio remains registration evidence only until a source-backed unit/order is found.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Exact Trio Sell-Removal Rule",
        "",
        "Scope: test `sell` as a literal remove/sell-off operation on the repaired exact-edge trio. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Trio: `{' | '.join(TRIO)}`",
        "",
        "## Scenarios",
        "",
        "| scenario | operation | remaining phrases | exposed boundary |",
        "|---|---|---|---|",
    ]
    for scenario in scenarios:
        lines.append(
            f"| `{scenario['name']}` | {scenario['operation']} | `{scenario['remainingPhrases']}` | `{scenario['exposedBoundary']}` |"
        )
    lines.extend(["", "## Streams", "", "| stream | value | raw hits | actionable hits |", "|---|---|---|---|"])
    for name, value in streams.items():
        actionable = hits.get(name, []) if name in actionable_streams else []
        lines.append(f"| `{name}` | `{value}` | `{raw_hits.get(name, [])}` | `{actionable}` |")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("rawInstructionHits:", raw_hits)
    print("actionableInstructionHits:", hits)


if __name__ == "__main__":
    main()
