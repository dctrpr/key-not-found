#!/usr/bin/env python3
"""Focused local-unit audit for the narrowed page-76 G5/O5 pair.

The convergence audit says the strongest local target is:
G5/B5: "Volcano Bonds"
O5:    "shitcoiner at heart."

This script tests low-parameter, human-plausible units around that pair:
omitted overlap characters, adjacent words, line/word positions, the shared
index 5, and 5/6 dosage-style picks. It does not generate private-key
candidates or run hashes.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
PAIR_JSON = ROOT / "analysis_outputs/source_audit/page76_b5_o5_pair/page76_b5_o5_pair.json"
OUT = ROOT / "analysis_outputs/source_audit/g5_o5_local_unit_rules"
OUT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT / "g5_o5_local_unit_rules.json"
OUT_MD = OUT / "g5_o5_local_unit_rules.md"

INSTRUCTION_TERMS = {
    "read",
    "take",
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
    "down",
    "up",
    "above",
    "below",
    "next",
    "previous",
    "before",
    "after",
}


def load_page76() -> dict:
    data = json.loads(CANONICAL.read_text())
    return next(page for page in data["pages"].values() if page.get("articlePage") == 76)


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def find_phrase(words: list[dict], phrase_words: list[str]) -> list[dict]:
    target = [normalize(w) for w in phrase_words]
    for i in range(0, len(words) - len(target) + 1):
        if [normalize(w["text"]) for w in words[i : i + len(target)]] == target:
            return words[i : i + len(target)]
    raise RuntimeError(f"phrase not found: {' '.join(phrase_words)}")


def line_words(words: list[dict], line_index: int) -> list[dict]:
    return [w for w in words if w["lineIndex"] == line_index]


def word_label(word: dict | None) -> str:
    return word["text"] if word else ""


def window(words: list[dict], start: int, end: int) -> list[dict]:
    return words[max(0, start) : min(len(words), end)]


def scan_instruction_terms(text: str) -> list[str]:
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    return sorted(tokens & INSTRUCTION_TERMS)


def one_based(index: int) -> int:
    return index + 1


def nth_word(words: list[dict], n: int) -> dict | None:
    if 1 <= n <= len(words):
        return words[n - 1]
    return None


def nth_after(words: list[dict], word_index: int, n: int) -> dict | None:
    idx = word_index + n
    return words[idx] if 0 <= idx < len(words) else None


def nth_before(words: list[dict], word_index: int, n: int) -> dict | None:
    idx = word_index - n
    return words[idx] if 0 <= idx < len(words) else None


def phrase_summary(name: str, phrase_words: list[dict], all_words: list[dict]) -> dict:
    first = phrase_words[0]
    last = phrase_words[-1]
    lw = line_words(all_words, first["lineIndex"])
    line_pos = [lw.index(w) for w in phrase_words]
    text = " ".join(w["text"] for w in phrase_words)
    return {
        "name": name,
        "text": text,
        "lineIndex0": first["lineIndex"],
        "lineIndex1": one_based(first["lineIndex"]),
        "wordIndex0": [w["wordIndex"] for w in phrase_words],
        "wordIndex1": [one_based(w["wordIndex"]) for w in phrase_words],
        "lineWordPosition0": line_pos,
        "lineWordPosition1": [one_based(i) for i in line_pos],
        "letters": "".join(w["letters"] for w in phrase_words),
        "wordLengths": [len(w["letters"]) for w in phrase_words],
        "initials": "".join(w["letters"][:1] for w in phrase_words if w["letters"]),
        "lastLetters": "".join(w["letters"][-1:] for w in phrase_words if w["letters"]),
        "lineWords": [w["text"] for w in lw],
        "contextBefore6": [w["text"] for w in window(all_words, first["wordIndex"] - 6, first["wordIndex"])],
        "contextAfter6": [w["text"] for w in window(all_words, last["wordIndex"] + 1, last["wordIndex"] + 7)],
        "lineText": " ".join(w["text"] for w in lw),
    }


def main() -> None:
    page = load_page76()
    words = page["words"]
    pair = json.loads(PAIR_JSON.read_text())

    g5_words = find_phrase(words, ["Volcano", "Bonds"])
    o5_words = find_phrase(words, ["shitcoiner", "at", "heart"])
    g5 = phrase_summary("G5", g5_words, words)
    o5 = phrase_summary("O5", o5_words, words)

    g5_first, g5_last = g5_words[0], g5_words[-1]
    o5_first, o5_last = o5_words[0], o5_words[-1]

    overlap_rows = pair["rows"]
    omitted_units = []
    selected_units = []
    for row in overlap_rows:
        source = row["sourceOriginalTextEstimate"]
        target = row["targetTextEstimate"]
        omitted_units.append(
            {
                "direction": f"{row['sourceId']}->{row['targetId']}",
                "sourceOmittedRightApprox": source["omittedRightApprox"],
                "targetOmittedRightApprox": target["omittedRightApprox"],
                "combined": source["omittedRightApprox"] + target["omittedRightApprox"],
                "combinedReverse": (source["omittedRightApprox"] + target["omittedRightApprox"])[::-1],
            }
        )
        selected_units.append(
            {
                "direction": f"{row['sourceId']}->{row['targetId']}",
                "sourceSelectedApprox": source["selectedApprox"],
                "targetSelectedApprox": target["selectedApprox"],
            }
        )

    g5_line = line_words(words, g5_first["lineIndex"])
    o5_line = line_words(words, o5_first["lineIndex"])
    dosage_line_picks = {
        "g5LineWord5": word_label(nth_word(g5_line, 5)),
        "g5LineWord6": word_label(nth_word(g5_line, 6)),
        "o5LineWord5": word_label(nth_word(o5_line, 5)),
        "o5LineWord6": word_label(nth_word(o5_line, 6)),
    }
    dosage_adjacent_picks = {
        "fifthAfterG5Phrase": word_label(nth_after(words, g5_last["wordIndex"], 5)),
        "sixthAfterG5Phrase": word_label(nth_after(words, g5_last["wordIndex"], 6)),
        "fifthBeforeO5Phrase": word_label(nth_before(words, o5_first["wordIndex"], 5)),
        "sixthBeforeO5Phrase": word_label(nth_before(words, o5_first["wordIndex"], 6)),
        "fifthBeforeG5Phrase": word_label(nth_before(words, g5_first["wordIndex"], 5)),
        "sixthBeforeG5Phrase": word_label(nth_before(words, g5_first["wordIndex"], 6)),
    }

    structural = {
        "lineGapO5MinusG5": o5_first["lineIndex"] - g5_first["lineIndex"],
        "globalWordGapStartToStart": o5_first["wordIndex"] - g5_first["wordIndex"],
        "globalWordGapEndToStartExclusive": o5_first["wordIndex"] - g5_last["wordIndex"] - 1,
        "g5LinePlus5": g5_first["lineIndex"] + 5,
        "g5LinePlus5MatchesO5Line": g5_first["lineIndex"] + 5 == o5_first["lineIndex"],
        "boxIndex": 5,
        "doseNumbersSeenNearby": [5, 6],
    }

    candidate_units = {
        "omittedOverlapCombined": [u["combined"] for u in omitted_units],
        "omittedOverlapCombinedReverse": [u["combinedReverse"] for u in omitted_units],
        "selectedOverlapPairs": selected_units,
        "phraseInitials": g5["initials"] + o5["initials"],
        "phraseLastLetters": g5["lastLetters"] + o5["lastLetters"],
        "wordLengths": g5["wordLengths"] + o5["wordLengths"],
        "dosageLinePicks": dosage_line_picks,
        "dosageAdjacentPicks": dosage_adjacent_picks,
    }

    searchable_text = " ".join(
        [
            g5["lineText"],
            o5["lineText"],
            " ".join(g5["contextBefore6"] + g5["contextAfter6"]),
            " ".join(o5["contextBefore6"] + o5["contextAfter6"]),
            " ".join(str(v) for v in dosage_line_picks.values()),
            " ".join(str(v) for v in dosage_adjacent_picks.values()),
            " ".join(u["combined"] for u in omitted_units),
        ]
    )
    instruction_hits = scan_instruction_terms(searchable_text)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Focused local-unit audit for page-76 G5/O5 pair; no key derivation.",
        "g5": g5,
        "o5": o5,
        "structural": structural,
        "omittedUnits": omitted_units,
        "candidateUnits": candidate_units,
        "instructionTermHits": instruction_hits,
        "assessment": [
            "The omitted-overlap unit is only `s.` or `.s`, caused by broad phrase overlap; it is too small and not instruction-like.",
            "The shared index 5 is structurally meaningful: line 27 + 5 = line 32, so the fifth line below `Volcano Bonds` is the `shitcoiner at heart` line.",
            "Using 5/6 as simple word selectors gives ordinary local words such as `pay/off`, `shitcoiner/at`, `IMF/loan`, and `guy/that`.",
            "Adjacent words and local line/word numbers do not reveal a read/take/fold/mirror/word/letter/key instruction.",
            "This keeps G5/O5 as target confirmation, not extraction material.",
        ],
        "nextMove": "Treat the 5-line relationship as a locator. The missing rule must come from source/provenance or physical registration, not from the obvious local text units around G5/O5.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# G5/O5 Local Unit Rules Audit",
        "",
        "Scope: test whether the narrowed page-76 pair provides a simple extraction unit through omitted overlap characters, adjacent words, line/word positions, or the visible 5/6 dosage numbers. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Pair",
        "",
        f"- G5: `{g5['text']}` on line `{g5['lineIndex0']}` zero-based / `{g5['lineIndex1']}` one-based, word positions `{g5['wordIndex1']}` one-based.",
        f"- O5: `{o5['text']}` on line `{o5['lineIndex0']}` zero-based / `{o5['lineIndex1']}` one-based, word positions `{o5['wordIndex1']}` one-based.",
        f"- Line gap: `{structural['lineGapO5MinusG5']}`.",
        f"- G5 line + 5 equals O5 line: `{structural['g5LinePlus5MatchesO5Line']}`.",
        "",
        "## Local Units",
        "",
        "| unit | result |",
        "|---|---|",
        f"| omitted overlap | `{', '.join(candidate_units['omittedOverlapCombined'])}` / reverse `{', '.join(candidate_units['omittedOverlapCombinedReverse'])}` |",
        f"| initials | `{candidate_units['phraseInitials']}` |",
        f"| last letters | `{candidate_units['phraseLastLetters']}` |",
        f"| word lengths | `{candidate_units['wordLengths']}` |",
        f"| line word 5/6 | G5 `{dosage_line_picks['g5LineWord5']}/{dosage_line_picks['g5LineWord6']}`, O5 `{dosage_line_picks['o5LineWord5']}/{dosage_line_picks['o5LineWord6']}` |",
        f"| after/before phrase 5/6 | after G5 `{dosage_adjacent_picks['fifthAfterG5Phrase']}/{dosage_adjacent_picks['sixthAfterG5Phrase']}`, before O5 `{dosage_adjacent_picks['fifthBeforeO5Phrase']}/{dosage_adjacent_picks['sixthBeforeO5Phrase']}` |",
        "",
        "## Context",
        "",
        f"- G5 line: `{g5['lineText']}`",
        f"- O5 line: `{o5['lineText']}`",
        f"- G5 context before: `{' '.join(g5['contextBefore6'])}`",
        f"- G5 context after: `{' '.join(g5['contextAfter6'])}`",
        f"- O5 context before: `{' '.join(o5['contextBefore6'])}`",
        f"- O5 context after: `{' '.join(o5['contextAfter6']) or '(none)'}`",
        "",
        "## Assessment",
        "",
        "- The cleanest structural fact is the five-line locator: `Volcano Bonds` is exactly five text lines above `shitcoiner at heart` in the corrected page-76 model.",
        "- That explains why repeated 5/dosage/symptom evidence keeps pointing here, but it does not provide the final extraction unit.",
        "- Omitted characters, adjacent words, initials, endings, word lengths, and simple 5/6 word picks do not produce an instruction.",
        "- Next best move: look for a source/provenance or physical-registration clue that says what to extract from the already-located G5/O5 target.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
