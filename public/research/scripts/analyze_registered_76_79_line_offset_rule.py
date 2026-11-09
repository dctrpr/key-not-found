#!/usr/bin/env python3
"""Test the registered 76/79 line pair as a line-offset / between-lines rule."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_ALIGNMENT = ROOT / "analysis_outputs/source_audit/registered_76_79_word_alignment.json"
OUT_MD = ROOT / "analysis_outputs/source_audit/registered_76_79_line_offset_rule.md"
OUT_JSON = ROOT / "analysis_outputs/source_audit/registered_76_79_line_offset_rule.json"

INSTRUCTION_TERMS = [
    "read",
    "fold",
    "mirror",
    "left",
    "right",
    "between",
    "line",
    "word",
    "letter",
    "key",
    "page",
    "dip",
    "down",
    "up",
    "reverse",
    "first",
    "last",
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", text)


def letters_only(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z]", text))


def initials(items: list[str]) -> str:
    return "".join(item[0] for item in items if item)


def lasts(items: list[str]) -> str:
    return "".join(item[-1] for item in items if item)


def length_mod(items: list[str]) -> str:
    return "".join(str(len(letters_only(item)) % 10) for item in items)


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if term in low]


def center_x(box: list[float] | tuple[float, ...]) -> float:
    return (box[0] + box[2]) / 2


def center_y(box: list[float] | tuple[float, ...]) -> float:
    return (box[1] + box[3]) / 2


def source_row_for(word: dict, midpoint: float) -> str:
    return "top" if center_y(word["mappedBox"]) < midpoint else "bottom"


def nearest_by_x(target: dict, source_words: list[dict]) -> dict | None:
    if not source_words:
        return None
    tx = center_x(target["box"])
    return min(source_words, key=lambda src: abs(center_x(src["mappedBox"]) - tx))


def exact_texts(data: dict) -> tuple[str, str]:
    source = " ".join(row["text"] for row in data["docmRuns"]["sourceP79"])
    target = " ".join(row["text"] for row in data["docmRuns"]["targetP76"])
    return source, target


def main() -> None:
    data = json.loads(WORD_ALIGNMENT.read_text())
    source_text, target_text = exact_texts(data)
    source_words_exact = words(source_text)
    target_words_exact = words(target_text)

    source_rows = data["sourceRowsAfterTransform"]
    target_rows = data["targetRows"]
    top_y = source_rows[0]["y"]
    bottom_y = source_rows[1]["y"]
    gap_mid = (top_y + bottom_y) / 2
    gap_height = bottom_y - top_y
    target_offsets = [
        {
            "targetText": row["text"],
            "targetY": row["y"],
            "deltaFromGapMid": round(row["y"] - gap_mid, 1),
            "deltaAsGapFraction": round((row["y"] - gap_mid) / gap_height, 4) if gap_height else None,
            "deltaFromTop": round(row["y"] - top_y, 1),
            "deltaFromBottom": round(row["y"] - bottom_y, 1),
        }
        for row in target_rows
    ]

    source_words = data["sourceWords"]
    top_sources = [w for w in source_words if source_row_for(w, gap_mid) == "top"]
    bottom_sources = [w for w in source_words if source_row_for(w, gap_mid) == "bottom"]
    first_target_row_y = target_rows[0]["y"]
    first_target_words = [
        w for w in data["targetWords"] if abs(center_y(w["box"]) - first_target_row_y) < 45
    ]
    first_target_words.sort(key=lambda w: center_x(w["box"]))
    sandwich = []
    for target in first_target_words:
        above = nearest_by_x(target, top_sources)
        below = nearest_by_x(target, bottom_sources)
        sandwich.append(
            {
                "target": target["text"],
                "above": above["text"] if above else None,
                "below": below["text"] if below else None,
                "aboveDx": round(center_x(target["box"]) - center_x(above["mappedBox"]), 1) if above else None,
                "belowDx": round(center_x(target["box"]) - center_x(below["mappedBox"]), 1) if below else None,
            }
        )

    streams = {
        "sourceInitials": initials(source_words_exact),
        "targetInitials": initials(target_words_exact),
        "sourceInitialsReversed": initials(list(reversed(source_words_exact))),
        "targetInitialsReversed": initials(list(reversed(target_words_exact))),
        "sourceLasts": lasts(source_words_exact),
        "targetLasts": lasts(target_words_exact),
        "sourceLengthMod10": length_mod(source_words_exact),
        "targetLengthMod10": length_mod(target_words_exact),
        "sandwichTargetInitials": initials([row["target"] for row in sandwich]),
        "sandwichAboveInitials": initials([row["above"] or "" for row in sandwich]),
        "sandwichBelowInitials": initials([row["below"] or "" for row in sandwich]),
        "sandwichAboveBelowInitialPairs": "".join(
            (row["above"][:1] if row["above"] else "") + (row["below"][:1] if row["below"] else "")
            for row in sandwich
        ),
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items()}

    result = {
        "source": str(WORD_ALIGNMENT),
        "exactSourceText": source_text,
        "exactTargetText": target_text,
        "sourceWords": source_words_exact,
        "targetWords": target_words_exact,
        "sourceWordCount": len(source_words_exact),
        "targetWordCount": len(target_words_exact),
        "sourceRowYs": [top_y, bottom_y],
        "targetOffsets": target_offsets,
        "gapMidpoint": round(gap_mid, 1),
        "gapHeight": round(gap_height, 1),
        "sandwichRows": sandwich,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": [
            "The first p76 grey target row sits almost exactly between the two transformed p79 source rows.",
            "This supports a literal 'between the lines' visual reading, but the between-lines text is normal article prose and not an instruction.",
            "Initials, lasts, length-mod streams, reversed order, and above/below sandwich initials do not produce instruction-like text.",
            "This keeps the 76/79 alignment active as registration evidence, but it does not solve the selector.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Registered 76/79 Line-Offset Rule Audit",
        "",
        "Scope: test whether the strongest registered 76/79 line pair gives a small `read between the lines` style selector. This uses only the one aligned anchor and does not derive keys.",
        "",
        "## Exact Text Pair",
        "",
        f"- p79 orange source: `{source_text}`",
        f"- p76 grey target: `{target_text}`",
        f"- Source words: {len(source_words_exact)}",
        f"- Target words: {len(target_words_exact)}",
        "",
        "## Vertical Offset",
        "",
        f"- Transformed p79 source row centers: `{top_y}` and `{bottom_y}`",
        f"- Source-row gap midpoint: `{gap_mid:.1f}`",
    ]
    for row in target_offsets:
        md.append(
            f"- p76 row `{row['targetText']}` y={row['targetY']} "
            f"deltaFromMid={row['deltaFromGapMid']} gapFraction={row['deltaAsGapFraction']}"
        )
    md.extend(["", "## Low-Parameter Text Streams", ""])
    for name, value in streams.items():
        hits = ",".join(stream_hits[name]) if stream_hits[name] else "none"
        md.append(f"- `{name}` hits={hits}: `{value}`")
    md.extend(["", "## Above / Target / Below Sandwich", ""])
    for row in sandwich:
        md.append(
            f"- `{row['above']}` / `{row['target']}` / `{row['below']}` "
            f"(dx above={row['aboveDx']}, below={row['belowDx']})"
        )
    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The geometry strongly supports a `between the lines` observation: the main p76 grey row is nearly centered in the vertical gap between the two transformed p79 source rows.",
            "- The actual between-lines text is `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense`, which is coherent article prose but not a visible instruction.",
            "- The exact-text streams and above/below sandwich initials do not produce readable selector language.",
            "- Conclusion: keep the 76/79 alignment as a registration clue, but do not promote this anchor into a direct text selector.",
            "- Next best move: test whether this same line-gap behavior recurs across other p76/p79 or p76/p78 highlight alignments; if it is unique, it may be a visual confirmation marker rather than extraction material.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
