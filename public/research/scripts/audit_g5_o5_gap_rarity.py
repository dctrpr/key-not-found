#!/usr/bin/env python3
"""Audit whether the G5/O5 3/5/5 gap pattern is special.

This compares the known page-76 corridor anchors by sentence row, page line,
and corridor index. It is a structural/geometry check only: no key derivation,
hashing, BIP39, WIF, seed, or address checks are run.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/plain_text_transcript/g5_o5_gap_rarity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "g5_o5_gap_rarity.json"
OUT_MD = OUT / "g5_o5_gap_rarity.md"

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

ANCHORS = [
    {"id": "S43_EL", "label": "El Salvador", "sentence": 43, "line": 20, "corridor": 2, "style": "plain"},
    {"id": "S43_IMF", "label": "IMF on Twitter", "sentence": 43, "line": 21, "corridor": 3, "style": "plain"},
    {"id": "O4_DIP", "label": "buying the dip", "sentence": 44, "line": 22, "corridor": 4, "style": "orange"},
    {"id": "G4_1B", "label": "$1 billion", "sentence": 45, "line": 25, "corridor": 7, "style": "grey"},
    {"id": "G5_VOLCANO", "label": "Volcano Bonds", "sentence": 45, "line": 27, "corridor": 9, "style": "grey"},
    {"id": "B_IMF", "label": "IMF loan", "sentence": 45, "line": 27, "corridor": 9, "style": "bold"},
    {"id": "B_MIKE", "label": "Mike", "sentence": 46, "line": 28, "corridor": 10, "style": "bold"},
    {"id": "B_NOVO", "label": "Novogratz", "sentence": 46, "line": 29, "corridor": 11, "style": "bold_partial"},
    {"id": "B_TRUST", "label": "trust that guy", "sentence": 47, "line": 31, "corridor": 13, "style": "bold_partial"},
    {"id": "O5_HEART", "label": "shitcoiner at heart", "sentence": 48, "line": 32, "corridor": 14, "style": "orange"},
]


def instruction_hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def pair_rows() -> list[dict]:
    rows = []
    for i, left in enumerate(ANCHORS):
        for right in ANCHORS[i + 1 :]:
            gaps = {
                "sentence": right["sentence"] - left["sentence"],
                "line": right["line"] - left["line"],
                "corridor": right["corridor"] - left["corridor"],
            }
            rows.append(
                {
                    "left": left["id"],
                    "right": right["id"],
                    "leftLabel": left["label"],
                    "rightLabel": right["label"],
                    "stylePair": f"{left['style']}->{right['style']}",
                    "gapTriple": f"{gaps['sentence']}/{gaps['line']}/{gaps['corridor']}",
                    "gaps": gaps,
                    "isG5O5": left["id"] == "G5_VOLCANO" and right["id"] == "O5_HEART",
                    "sameCoordinateAsG5": left["sentence"] == 45 and left["line"] == 27 and left["corridor"] == 9,
                }
            )
    return rows


def main() -> None:
    pairs = pair_rows()
    triple_counts = Counter(row["gapTriple"] for row in pairs)
    style_triple_counts = Counter(f"{row['stylePair']} {row['gapTriple']}" for row in pairs)
    g5o5 = next(row for row in pairs if row["isG5O5"])
    same_triple = [row for row in pairs if row["gapTriple"] == g5o5["gapTriple"]]
    same_style_triple = [
        row
        for row in pairs
        if row["gapTriple"] == g5o5["gapTriple"] and row["stylePair"] == g5o5["stylePair"]
    ]
    streams = {
        "g5o5GapTriple": g5o5["gapTriple"],
        "sameGapPairs": " | ".join(f"{row['leftLabel']}->{row['rightLabel']}" for row in same_triple),
        "sameStyleGapPairs": " | ".join(f"{row['leftLabel']}->{row['rightLabel']}" for row in same_style_triple),
        "allGapTriplesByPair": " ; ".join(f"{row['left']}->{row['right']}={row['gapTriple']}" for row in pairs),
        "gapTripleFrequency": " ; ".join(f"{triple}:{count}" for triple, count in sorted(triple_counts.items())),
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)}

    assessment = [
        "The G5/O5 locator gap is sentence/page-line/corridor `3/5/5`.",
        "The exact `3/5/5` gap is shared by `IMF loan -> shitcoiner at heart` because `IMF` sits on the same printed line as `Volcano Bonds`.",
        "Within grey-to-orange pairs, `Volcano Bonds -> shitcoiner at heart` is the only `3/5/5` pair, while `$1 billion -> shitcoiner at heart` is `3/7/7`.",
        "This makes `3/5/5` useful as a locator tied to line 27 -> 32, but not a unique extraction instruction.",
        "No gap-frequency or pair-label stream names a procedural unit.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "G5/O5 gap-rarity audit across page-76 corridor anchors; no key derivation, hashing, BIP39, WIF, seed, or address checks",
        "anchors": ANCHORS,
        "pairCount": len(pairs),
        "g5o5": g5o5,
        "gapTripleCounts": dict(sorted(triple_counts.items())),
        "styleGapTripleCounts": dict(sorted(style_triple_counts.items())),
        "sameGapPairs": same_triple,
        "sameStyleGapPairs": same_style_triple,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "decision": "Treat the `3/5/5` G5/O5 gap as locator evidence only, not as an extraction rule.",
        "nextMove": "Reopen gap arithmetic only if a future source/clue explicitly names gap, line, sentence, or count units.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# G5/O5 Gap Rarity Audit",
        "",
        "Scope: compare the G5/O5 `3/5/5` gap against nearby page-76 corridor anchors. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Anchor count: `{len(ANCHORS)}`",
        f"- Pair count: `{len(pairs)}`",
        f"- G5/O5 gap triple: `{g5o5['gapTriple']}`",
        f"- Same-gap pair count: `{len(same_triple)}`",
        f"- Same style+gap pair count: `{len(same_style_triple)}`",
        "",
        "## Same `3/5/5` Gap Pairs",
        "",
        "| left | right | style pair | gap | note |",
        "|---|---|---|---|---|",
    ]
    for row in same_triple:
        note = "G5/O5" if row["isG5O5"] else "same printed coordinate as G5" if row["sameCoordinateAsG5"] else ""
        lines.append(f"| `{row['leftLabel']}` | `{row['rightLabel']}` | `{row['stylePair']}` | `{row['gapTriple']}` | {note} |")

    lines.extend(["", "## All Target Pair Gaps", "", "| left | right | style pair | gap |", "|---|---|---|---|"])
    for row in pairs:
        if row["left"] in {"G4_1B", "G5_VOLCANO", "B_IMF", "O4_DIP"} and row["right"] in {
            "O5_HEART",
            "B_TRUST",
            "B_NOVO",
        }:
            lines.append(f"| `{row['leftLabel']}` | `{row['rightLabel']}` | `{row['stylePair']}` | `{row['gapTriple']}` |")

    lines.extend(["", "## Streams", "", "| stream | value | instruction hits |", "|---|---|---|"])
    for name, value in streams.items():
        display = value if len(value) < 240 else value[:240] + "..."
        lines.append(f"| `{name}` | `{display}` | `{stream_hits.get(name, [])}` |")

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("sameGapPairs:", len(same_triple))
    print("streamInstructionHits:", stream_hits)


if __name__ == "__main__":
    main()
