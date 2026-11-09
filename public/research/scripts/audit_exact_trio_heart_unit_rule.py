#!/usr/bin/env python3
"""Test the literal `heart` unit rule on the repaired exact-edge trio.

The active readiness gate says the closest local path has source, target, and
order:

    should sell | Volcano Bonds | shitcoiner at heart

but lacks an extraction unit. This bounded pass treats the printed word
`heart` as a literal unit clue and extracts middle/heart letters from only this
exact trio. It does not derive keys, hashes, mnemonics, WIFs, or addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/exact_trio_heart_unit_rule"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "exact_trio_heart_unit_rule.json"
OUT_MD = OUT / "exact_trio_heart_unit_rule.md"

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
    "down",
    "up",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def letters(text: str) -> str:
    return "".join(words(text)).lower()


def heart_chars(text: str, width: int = 1) -> str:
    s = letters(text)
    if not s:
        return ""
    mid = len(s) // 2
    if width == 1:
        return s[mid] if len(s) % 2 else s[mid - 1 : mid + 1]
    start = max(0, mid - width // 2)
    end = min(len(s), start + width)
    return s[start:end]


def heart_window_variants(text: str, width: int = 4) -> dict[str, str]:
    s = letters(text)
    if not s:
        return {"leftBiased": "", "rightBiased": ""}
    mid = len(s) // 2
    left_start = max(0, mid - width // 2)
    right_start = max(0, mid - (width // 2) + (0 if len(s) % 2 else 1))
    return {
        "leftBiased": s[left_start : min(len(s), left_start + width)],
        "rightBiased": s[right_start : min(len(s), right_start + width)],
    }


def middle_words(text: str) -> list[str]:
    ws = words(text)
    if not ws:
        return []
    mid = len(ws) // 2
    if len(ws) % 2:
        return [ws[mid]]
    return [ws[mid - 1], ws[mid]]


def per_word_hearts(text: str) -> list[str]:
    out = []
    for word in words(text):
        out.append(heart_chars(word))
    return out


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def main() -> None:
    rows = []
    for phrase in TRIO:
        row = {
            "phrase": phrase,
            "words": words(phrase),
            "letters": letters(phrase),
            "letterCount": len(letters(phrase)),
            "middleWordOrWords": middle_words(phrase),
            "heartCharsWidth1": heart_chars(phrase, 1),
            "heartCharsWidth3": heart_chars(phrase, 3),
            "heartCharsWidth4": heart_chars(phrase, 4),
            "heartWidth4Variants": heart_window_variants(phrase, 4),
            "perWordHearts": per_word_hearts(phrase),
        }
        rows.append(row)

    streams = {
        "middleWordsForward": " ".join(" ".join(row["middleWordOrWords"]) for row in rows),
        "middleWordsReverse": " ".join(" ".join(row["middleWordOrWords"]) for row in reversed(rows)),
        "phraseHeartWidth1Forward": "".join(row["heartCharsWidth1"] for row in rows),
        "phraseHeartWidth1Reverse": "".join(row["heartCharsWidth1"] for row in reversed(rows)),
        "phraseHeartWidth3Forward": "".join(row["heartCharsWidth3"] for row in rows),
        "phraseHeartWidth3Reverse": "".join(row["heartCharsWidth3"] for row in reversed(rows)),
        "phraseHeartWidth4Forward": "".join(row["heartCharsWidth4"] for row in rows),
        "phraseHeartWidth4Reverse": "".join(row["heartCharsWidth4"] for row in reversed(rows)),
        "perWordHeartsForward": " ".join(" ".join(row["perWordHearts"]) for row in rows),
        "perWordHeartsReverse": " ".join(" ".join(row["perWordHearts"]) for row in reversed(rows)),
        "shitcoinerHeartLeftBiased4": heart_window_variants("shitcoiner", 4)["leftBiased"],
        "shitcoinerHeartRightBiased4": heart_window_variants("shitcoiner", 4)["rightBiased"],
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}

    assessment = [
        "The literal `heart` unit is locally justified only because the exact-edge trio contains `shitcoiner at heart`.",
        "Middle/heart extraction from the exact trio produces fragments such as `ldnoe`, `ldsnobner`, and `uldsanobiner`, plus ambiguous center windows from `shitcoiner`.",
        "A right-biased 4-letter heart of `shitcoiner` gives `coin`, while the left-biased 4-letter heart gives `tcoi`; that ambiguity makes it thematic support, not a defensible selector.",
        "The rule does not supply the missing extraction unit for page-76 key material; it only explains why O5 keeps acting as semantic support.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "literal heart/middle-unit test on repaired exact-edge trio; no key derivation",
        "sourcePath": "repaired p78 exact-edge trio",
        "trio": TRIO,
        "rows": rows,
        "streams": streams,
        "instructionHits": stream_hits,
        "assessment": assessment,
        "decision": "Close literal heart extraction from the exact trio as a selector. Preserve the ambiguous `coin`/`tcoi` heart of `shitcoiner` as thematic support only.",
        "nextMove": "The closest local path remains blocked on a source-backed unit. Continue with source/original-layout/physical evidence or a new explicit rule, not local key candidates.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Exact Trio Heart-Unit Rule",
        "",
        "Scope: test the printed word `heart` as a literal middle-letter unit on the repaired exact-edge trio only. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Trio: `{' | '.join(TRIO)}`",
        "",
        "## Phrase Hearts",
        "",
        "| phrase | words | letters | middle word(s) | heart width 1/2 | heart width 3 | heart width 4 | width-4 variants | per-word hearts |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['phrase']}` | `{row['words']}` | `{row['letters']}` | `{row['middleWordOrWords']}` | `{row['heartCharsWidth1']}` | `{row['heartCharsWidth3']}` | `{row['heartCharsWidth4']}` | `{row['heartWidth4Variants']}` | `{row['perWordHearts']}` |"
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
    print("instructionHits:", stream_hits)
    print("shitcoinerHeartLeftBiased4:", streams["shitcoinerHeartLeftBiased4"])
    print("shitcoinerHeartRightBiased4:", streams["shitcoinerHeartRightBiased4"])


if __name__ == "__main__":
    main()
