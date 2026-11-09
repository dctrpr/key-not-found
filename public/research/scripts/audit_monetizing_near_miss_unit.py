#!/usr/bin/env python3
"""Pressure-test the p77 `It does this by monetizing` near miss as a C3 clue.

The previous physical-model pass found this phrase as the closest true
physical/spread near miss to page-76 O5, but it still required an arbitrary
vertical repair. This pass asks a narrower question: does the phrase itself,
or its immediate sentence context, name an extraction unit/order strongly
enough to satisfy the C3 "missing unit" blocker?

No key derivation, hashing, seed checks, WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/monetizing_near_miss_unit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "monetizing_near_miss_unit.json"
OUT_MD = OUT / "monetizing_near_miss_unit.md"

NEAR_MISS_JSON = ROOT / "analysis_outputs/source_audit/physical_model_near_miss_rank/physical_model_near_miss_rank.json"

EXTRACTION_TERMS = [
    "take",
    "read",
    "use",
    "select",
    "count",
    "index",
    "word",
    "words",
    "letter",
    "letters",
    "line",
    "lines",
    "row",
    "column",
    "edge",
    "font",
    "regular",
    "mix",
    "bold",
    "highlight",
    "orange",
    "grey",
    "gray",
    "black",
    "first",
    "last",
    "left",
    "right",
    "above",
    "below",
    "up",
    "down",
    "reverse",
    "mirror",
    "fold",
]

THEMATIC_TERMS = [
    "bitcoin",
    "monetizing",
    "demonetizes",
    "money",
    "peace",
    "love",
    "understanding",
    "war",
    "violence",
    "hatred",
    "state",
]

EXACT_PHRASE = "It does this by monetizing"
CONTEXT_SENTENCE = (
    "And as bitcoin starves shitcoins, fiat and gold to death, it simultaneously "
    "demonetizes war, violence, hatred and the state itself. It does this by "
    "monetizing, for the first time in human history, peace, love and understanding."
)

TARGETS = [
    {"id": "G5", "label": "Volcano Bonds", "kind": "trusted-grey"},
    {"id": "O5", "label": "shitcoiner at heart", "kind": "orange"},
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def lower_words(text: str) -> list[str]:
    return [word.lower() for word in words(text)]


def initials(text: str) -> str:
    return "".join(word[0].lower() for word in words(text) if word)


def endings(text: str) -> str:
    return "".join(word[-1].lower() for word in words(text) if word)


def reverse_words(text: str) -> str:
    return " ".join(reversed(words(text)))


def found_terms(text: str, terms: list[str]) -> list[str]:
    tokens = set(lower_words(text))
    return [term for term in terms if term in tokens]


def instruction_hits(text: str) -> list[str]:
    terms = [
        "take",
        "read",
        "use",
        "select",
        "word",
        "letter",
        "line",
        "edge",
        "font",
        "bold",
        "orange",
        "black",
        "grey",
        "first",
        "last",
        "left",
        "right",
        "reverse",
        "mirror",
        "fold",
        "key",
    ]
    lowered = text.lower()
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", lowered)]


def load_near_miss() -> dict:
    if not NEAR_MISS_JSON.exists():
        return {}
    return json.loads(NEAR_MISS_JSON.read_text(encoding="utf-8"))


def first_cue_outputs() -> list[dict]:
    rows = []
    for order_name, ordered in [
        ("G5 then O5", TARGETS),
        ("O5 then G5", list(reversed(TARGETS))),
    ]:
        first_words = [words(target["label"])[0] for target in ordered]
        first_letters = [words(target["label"])[0][0] for target in ordered]
        all_word_initials = [initials(target["label"]) for target in ordered]
        rows.append(
            {
                "order": order_name,
                "firstWords": " ".join(first_words),
                "firstLetters": "".join(first_letters),
                "targetWordInitials": " ".join(all_word_initials),
                "instructionHits": instruction_hits(" ".join(first_words + first_letters + all_word_initials)),
            }
        )
    return rows


def build_result() -> dict:
    near = load_near_miss()
    best = near.get("bestTruePhysicalNearMiss", {})

    exact_terms = found_terms(EXACT_PHRASE, EXTRACTION_TERMS)
    context_terms = found_terms(CONTEXT_SENTENCE, EXTRACTION_TERMS)
    exact_theme = found_terms(EXACT_PHRASE, THEMATIC_TERMS)
    context_theme = found_terms(CONTEXT_SENTENCE, THEMATIC_TERMS)

    exact_tests = [
        {
            "test": "exact phrase initials",
            "output": initials(EXACT_PHRASE),
            "instructionHits": instruction_hits(initials(EXACT_PHRASE)),
            "verdict": "not instruction-like",
        },
        {
            "test": "exact phrase endings",
            "output": endings(EXACT_PHRASE),
            "instructionHits": instruction_hits(endings(EXACT_PHRASE)),
            "verdict": "not instruction-like",
        },
        {
            "test": "exact phrase word reversal",
            "output": reverse_words(EXACT_PHRASE),
            "instructionHits": instruction_hits(reverse_words(EXACT_PHRASE)),
            "verdict": "still only ordinary prose",
        },
        {
            "test": "exact phrase character reversal",
            "output": EXACT_PHRASE[::-1],
            "instructionHits": instruction_hits(EXACT_PHRASE[::-1]),
            "verdict": "still no extraction unit",
        },
        {
            "test": "peace/love/understanding initials from immediate context",
            "output": initials("peace love understanding"),
            "instructionHits": instruction_hits(initials("peace love understanding")),
            "verdict": "thematic phrase only; no unit/order",
        },
    ]

    criteria = [
        {
            "criterion": "names an extraction unit",
            "status": "FAIL",
            "evidence": "Exact phrase contains no word/letter/line/edge/font/color/take/read/select term.",
        },
        {
            "criterion": "names an order or direction",
            "status": "WEAK",
            "evidence": "Immediate context contains `first time`, but it names historical timing, not which word/letter/line to take.",
        },
        {
            "criterion": "names a unique target object",
            "status": "FAIL",
            "evidence": "`Monetizing` is semantically related to both Volcano Bonds and shitcoiner/bitcoin language, but it does not choose one or define a unit.",
        },
        {
            "criterion": "survives physical/visual repetition check",
            "status": "FAIL",
            "evidence": f"Near-miss repair creates only {best.get('nudgeHitCount', 'unknown')} trusted O5/G5 hit, not a repeated selector.",
        },
        {
            "criterion": "produces instruction-like local outputs",
            "status": "FAIL",
            "evidence": "Initials/endings/reversal and first-cue target reads produce short thematic fragments, not procedural text.",
        },
    ]

    first_outputs = first_cue_outputs()
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C3 extraction-unit pressure test for p77 `It does this by monetizing`; no key derivation",
        "nearMissInput": {
            "sourcePhrase": best.get("sourceLabel", EXACT_PHRASE),
            "sourcePage": best.get("sourcePage"),
            "targetId": best.get("targetId"),
            "touchShiftDx": best.get("touchShiftDx"),
            "touchShiftDy": best.get("touchShiftDy"),
            "touchShiftMagnitude": best.get("touchShiftMagnitude"),
            "nudgeHitCount": best.get("nudgeHitCount"),
        },
        "phraseAudit": {
            "exactPhrase": EXACT_PHRASE,
            "contextSentence": CONTEXT_SENTENCE,
            "exactExtractionTerms": exact_terms,
            "contextExtractionTerms": context_terms,
            "exactThematicTerms": exact_theme,
            "contextThematicTerms": context_theme,
            "deicticTerms": found_terms(EXACT_PHRASE, ["it", "this"]),
        },
        "criteria": criteria,
        "lowParameterTests": exact_tests,
        "firstCueOutputs": first_outputs,
        "assessment": [
            "`It does this by monetizing` is a good semantic near miss because it sits close to O5 and echoes the money/Bitcoin theme.",
            "It does not satisfy C3: it does not name a concrete unit such as word, letter, line, font, color, edge, or direction.",
            "The only procedural-looking context word is `first`, but the phrase is `for the first time in human history`; applying `first` to G5/O5 yields ordinary target words/initials, not an instruction.",
            "Keep this phrase as a future physical-scan benchmark, not as extraction material under the current scan.",
        ],
        "decision": "do_not_promote_to_selector",
        "nextMove": "Only revisit if a physical/original-layout source makes the p77 phrase directly and repeatedly contact O5/G5, or if an external clue uses monetizing/first-time language as an explicit instruction.",
    }
    return result


def write_report(result: dict) -> None:
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    near = result["nearMissInput"]
    lines = [
        "# Monetizing Near-Miss Unit Audit",
        "",
        "Scope: pressure-test p77 `It does this by monetizing` as a possible C3 extraction-unit clue. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Near miss: page `{near['sourcePage']}` `{near['sourcePhrase']}` -> `{near['targetId']}`.",
        f"- Required touch shift: `({near['touchShiftDx']}, {near['touchShiftDy']})`, magnitude `{near['touchShiftMagnitude']}` px.",
        f"- Forced nudge trusted-hit count: `{near['nudgeHitCount']}`.",
        "",
        "## Phrase Audit",
        "",
        f"- Exact extraction terms: `{', '.join(result['phraseAudit']['exactExtractionTerms']) or 'none'}`.",
        f"- Context extraction terms: `{', '.join(result['phraseAudit']['contextExtractionTerms']) or 'none'}`.",
        f"- Exact thematic terms: `{', '.join(result['phraseAudit']['exactThematicTerms']) or 'none'}`.",
        f"- Context thematic terms: `{', '.join(result['phraseAudit']['contextThematicTerms']) or 'none'}`.",
        f"- Deictic terms in exact phrase: `{', '.join(result['phraseAudit']['deicticTerms']) or 'none'}`.",
        "",
        "## C3 Criteria",
        "",
        "| criterion | status | evidence |",
        "|---|---|---|",
    ]
    for item in result["criteria"]:
        lines.append(f"| {item['criterion']} | `{item['status']}` | {item['evidence']} |")

    lines.extend(["", "## Low-Parameter Checks", "", "| test | output | instruction hits | verdict |", "|---|---|---|---|"])
    for item in result["lowParameterTests"]:
        hits = ", ".join(item["instructionHits"]) or "none"
        lines.append(f"| {item['test']} | `{item['output']}` | `{hits}` | {item['verdict']} |")

    lines.extend(["", "## First-Cue Target Reads", "", "| order | first words | first letters | target word initials | instruction hits |", "|---|---|---|---|---|"])
    for item in result["firstCueOutputs"]:
        hits = ", ".join(item["instructionHits"]) or "none"
        lines.append(
            f"| {item['order']} | `{item['firstWords']}` | `{item['firstLetters']}` | `{item['targetWordInitials']}` | `{hits}` |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Decision: `{result['decision']}`.", "", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = build_result()
    write_report(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("decision:", result["decision"])
    print("exactExtractionTerms:", result["phraseAudit"]["exactExtractionTerms"])
    print("contextExtractionTerms:", result["phraseAudit"]["contextExtractionTerms"])


if __name__ == "__main__":
    main()
