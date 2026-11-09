#!/usr/bin/env python3
"""Synthesize confirmed target evidence into low-parameter rule candidates.

Recent passes have confirmed target/location evidence but repeatedly failed to
produce an extraction unit. This audit deliberately uses only confirmed active
objects (G5/O5, p78 frame, M3/M4 endpoint, bridge-normalized chain, Schott
mirror concept) and tests simple human-solvable orderings for instruction-like
language. It does not generate private keys, hashes, mnemonics, or addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/confirmed_target_rule_synthesis"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "confirmed_target_rule_synthesis.json"
OUT_MD = OUT / "confirmed_target_rule_synthesis.md"

TARGET_CONVERGENCE = ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json"
P78_FRAME = ROOT / "analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.json"
M3M4_BRACKET = ROOT / "analysis_outputs/source_audit/m3_m4_pair_bracket/m3_m4_pair_bracket.json"
BRIDGE_CHAIN = ROOT / "analysis_outputs/source_audit/page76_bridge_normalized_chain/page76_bridge_normalized_chain.json"
SOURCE_CLUES = ROOT / "analysis_outputs/external_clues/original_clue_provenance.json"

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
    "seed",
    "wif",
    "address",
    "index",
    "order",
]

UNIT_TERMS = ["line", "word", "letter", "char", "character", "number", "index", "key", "seed", "wif"]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def initials(text: str) -> str:
    return "".join(w[0].lower() for w in words(text) if w)


def lasts(text: str) -> str:
    return "".join(w[-1].lower() for w in words(text) if w)


def word_lengths(text: str) -> str:
    return ".".join(str(len(w)) for w in words(text))


def reverse_words(text: str) -> str:
    return " ".join(reversed(words(text)))


def reverse_chars(text: str) -> str:
    return text[::-1]


def instruction_hits(text: str) -> list[str]:
    value = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", value)]


def unit_hits(text: str) -> list[str]:
    value = text.lower()
    return [term for term in UNIT_TERMS if re.search(rf"\b{re.escape(term)}\b", value)]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def add_stream(rows: list[dict], name: str, source: str, operation: str, value: str, rationale: str) -> None:
    value = clean(value)
    rows.append(
        {
            "name": name,
            "source": source,
            "operation": operation,
            "value": value,
            "initials": initials(value),
            "lastLetters": lasts(value),
            "wordLengths": word_lengths(value),
            "reverseWords": reverse_words(value),
            "reverseChars": reverse_chars(value),
            "instructionHits": instruction_hits(value),
            "unitHits": unit_hits(value),
            "rationale": rationale,
        }
    )


def main() -> None:
    convergence = load_json(TARGET_CONVERGENCE)
    frame = load_json(P78_FRAME)
    bracket = load_json(M3M4_BRACKET)
    chain = load_json(BRIDGE_CHAIN)
    clues = load_json(SOURCE_CLUES)

    ranking = convergence["ranking"]
    top_labels = [f"{row['target']}:{row['label']}" for row in ranking[:5]]
    source_texts = {
        name: record.get("plainText", "")
        for name, record in clues.get("tweets", {}).items()
    }

    rows: list[dict] = []
    add_stream(
        rows,
        "convergenceRankTop5",
        "page76_target_convergence",
        "score order",
        " | ".join(top_labels),
        "Highest-supported page-76 targets in score order.",
    )
    add_stream(
        rows,
        "targetPairG5O5",
        "target convergence",
        "confirmed pair forward",
        "Volcano Bonds | shitcoiner at heart",
        "The strongest confirmed pair from self-mirror/convergence.",
    )
    add_stream(
        rows,
        "targetPairO5G5",
        "target convergence",
        "confirmed pair reverse",
        "shitcoiner at heart | Volcano Bonds",
        "Schott/mirror-compatible reversal of the confirmed pair.",
    )
    add_stream(
        rows,
        "minimalFrame",
        "p78_frame_order_read",
        "frame corner minimal path",
        frame["streams"]["minimalCornerFrame"],
        "Shortest p78 frame phrase path.",
    )
    add_stream(
        rows,
        "leftFrameTopDown",
        "p78_frame_order_read",
        "left edge top-to-bottom",
        frame["streams"]["leftEdgeTopToBottom"],
        "P78 reflected frame left edge in visual top-to-bottom order.",
    )
    add_stream(
        rows,
        "leftFrameBottomUp",
        "p78_frame_order_read",
        "left edge bottom-to-top",
        frame["streams"]["leftEdgeBottomToTop"],
        "Mirror/reverse of the p78 reflected frame left edge.",
    )
    add_stream(
        rows,
        "m3m4Bracket",
        "m3_m4_pair_bracket",
        "paired mark wedge",
        bracket["streams"]["bracketedWordsLeftToRight"],
        "Only text/highlight selected by the M3/M4 wedge.",
    )
    add_stream(
        rows,
        "m3m4BracketReverse",
        "m3_m4_pair_bracket",
        "paired mark wedge reversed",
        bracket["streams"]["bracketedWordsReverse"],
        "Reverse of M3/M4 wedge read.",
    )
    add_stream(
        rows,
        "bridgeStrictTerms",
        "page76_bridge_normalized_chain",
        "line-offset chain terms",
        chain["streams"]["strictPreferredTerms"],
        "Bridge-normalized page-76 locator chain.",
    )
    add_stream(
        rows,
        "bridgeStrictTermsReversed",
        "page76_bridge_normalized_chain",
        "line-offset chain terms reversed",
        chain["streams"]["strictPreferredTermsReversed"],
        "Mirror-compatible reversal of the bridge-normalized chain.",
    )
    add_stream(
        rows,
        "publicInstructionText",
        "original_clue_provenance",
        "original announcement + Schott clue",
        " | ".join(source_texts.values()),
        "Only archived public written instruction text.",
    )

    # Derived low-parameter transforms for confirmed pair only.
    pair = "Volcano Bonds shitcoiner at heart"
    add_stream(
        rows,
        "pairInitials",
        "confirmed pair",
        "first letters only",
        initials(pair),
        "Low-parameter first-letter extraction on G5/O5 only.",
    )
    add_stream(
        rows,
        "pairLastLetters",
        "confirmed pair",
        "last letters only",
        lasts(pair),
        "Low-parameter last-letter extraction on G5/O5 only.",
    )
    add_stream(
        rows,
        "pairWordLengths",
        "confirmed pair",
        "word lengths only",
        word_lengths(pair),
        "Low-parameter count extraction on G5/O5 only.",
    )

    positive_instruction_rows = [row for row in rows if row["instructionHits"]]
    positive_unit_rows = [row for row in rows if row["unitHits"]]
    actionable_rows = [
        row
        for row in rows
        if row["name"] != "publicInstructionText" and (row["instructionHits"] or row["unitHits"])
    ]

    assessment = [
        "Confirmed local target/order streams still do not name a source layer or extraction unit.",
        "The only instruction-like hits come from the archived public clue text itself: `private`, `key`, `encoded`, and Schott `mirror writing`.",
        "The confirmed visual system has converged on O5 and G5/O5, but all low-parameter text orderings remain ordinary corridor prose or short non-words.",
        "This is now a source-rule problem, not a local stream-generation problem.",
    ]
    next_move = (
        "Prioritize source/physical registration or exact original visual material. "
        "If forced to continue locally, audit true physical leaf/spread assumptions against the best scan using confirmed O5/G5 as validation points, not more p78 text streams."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "confirmed target/order synthesis; no key derivation",
        "inputs": {
            "targetConvergence": str(TARGET_CONVERGENCE.relative_to(ROOT)),
            "p78Frame": str(P78_FRAME.relative_to(ROOT)),
            "m3m4Bracket": str(M3M4_BRACKET.relative_to(ROOT)),
            "bridgeChain": str(BRIDGE_CHAIN.relative_to(ROOT)),
            "sourceClues": str(SOURCE_CLUES.relative_to(ROOT)),
        },
        "streamRows": rows,
        "positiveInstructionRows": positive_instruction_rows,
        "positiveUnitRows": positive_unit_rows,
        "actionableLocalRows": actionable_rows,
        "assessment": assessment,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Confirmed Target Rule Synthesis",
        "",
        "Scope: synthesize only confirmed active objects and test low-parameter mirror/frame orderings for instruction-like language. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Stream Tests",
        "",
        "| stream | operation | value | initials | unit/instruction hits |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        hits = ", ".join(row["instructionHits"] + row["unitHits"]) or "-"
        value = row["value"].replace("|", "\\|")
        lines.append(f"| `{row['name']}` | {row['operation']} | `{value}` | `{row['initials']}` | {hits} |")

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Local actionable streams with instruction/unit hits: `{len(actionable_rows)}`.",
            f"- Public-clue instruction rows: `{len(positive_instruction_rows)}` total, driven by the archived announcement/Schott clue text.",
            "- The public text gives target type and operation family (`private key`, `encoded`, `mirror writing`) but still does not name `line`, `word`, or `letter` for the confirmed page-76 objects.",
            "- Confirmed visual streams are stable target evidence, not extraction instructions.",
            "",
            "## Assessment",
            "",
        ]
    )
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {next_move}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("local actionable rows:", len(actionable_rows))


if __name__ == "__main__":
    main()
