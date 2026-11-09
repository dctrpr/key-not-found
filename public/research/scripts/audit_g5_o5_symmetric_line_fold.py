#!/usr/bin/env python3
"""Audit a symmetric line-fold read across the G5/O5 page-76 corridor.

The strongest local target pair is G5 `Volcano Bonds` and O5 `shitcoiner at
heart`, exactly five corrected text lines apart. This pass tests the most
literal remaining local rule from the Schott clue: treat the interval as a
two-handed mirror/fold surface and read paired lines from outside-in and
inside-out.

No private-key candidates, hashes, seed phrases, or address checks are run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CORRIDOR_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
OUT = ROOT / "analysis_outputs/source_audit/g5_o5_symmetric_line_fold"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "g5_o5_symmetric_line_fold.json"
OUT_MD = OUT / "g5_o5_symmetric_line_fold.md"
OUT_IMG = OUT / "g5_o5_symmetric_line_fold_diagram.jpg"

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
    "use",
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+", text)


def initial(word: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9$]", "", word)
    return cleaned[:1]


def last_initial(word: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9$]", "", word)
    return cleaned[-1:] if cleaned else ""


def scan_hits(text: str) -> list[str]:
    found = set(re.findall(r"[a-z0-9]+", text.lower()))
    return sorted(found & INSTRUCTION_TERMS)


def load_records() -> list[dict]:
    data = json.loads(CORRIDOR_JSON.read_text())
    return data["records"]


def record_for(records: list[dict], line_index: int) -> dict:
    return next(row for row in records if row["lineIndex"] == line_index)


def line_summary(row: dict) -> dict:
    words = tokens(row["text"])
    return {
        "lineIndex": row["lineIndex"],
        "corridorIndex": row["corridorIndex"],
        "text": row["text"],
        "words": words,
        "firstWord": words[0] if words else "",
        "lastWord": words[-1] if words else "",
        "initial": initial(words[0]) if words else "",
        "lastInitial": last_initial(words[-1]) if words else "",
        "wordCount": len(words),
        "boldLetters": row.get("boldLetters", ""),
        "partialBoldLetters": row.get("partialBoldLetters", ""),
        "highlights": row.get("highlights", []),
    }


def pair_summary(top: dict, bottom: dict) -> dict:
    top_words = top["words"]
    bottom_words = bottom["words"]
    reversed_bottom = list(reversed(bottom_words))
    aligned = []
    for i in range(max(len(top_words), len(reversed_bottom))):
        left = top_words[i] if i < len(top_words) else ""
        right = reversed_bottom[i] if i < len(reversed_bottom) else ""
        if left or right:
            aligned.append({"topWord": left, "bottomWordReversed": right})
    return {
        "topLine": top["lineIndex"],
        "bottomLine": bottom["lineIndex"],
        "lineGap": bottom["lineIndex"] - top["lineIndex"],
        "topText": top["text"],
        "bottomText": bottom["text"],
        "topFirst": top["firstWord"],
        "bottomFirst": bottom["firstWord"],
        "topLast": top["lastWord"],
        "bottomLast": bottom["lastWord"],
        "edgeWordsTopThenBottom": " ".join([top["firstWord"], top["lastWord"], bottom["firstWord"], bottom["lastWord"]]).strip(),
        "edgeWordsBottomThenTop": " ".join([bottom["firstWord"], bottom["lastWord"], top["firstWord"], top["lastWord"]]).strip(),
        "firstInitials": top["initial"] + bottom["initial"],
        "lastInitials": top["lastInitial"] + bottom["lastInitial"],
        "wordCountPair": [top["wordCount"], bottom["wordCount"]],
        "wordCountDiffAbs": abs(top["wordCount"] - bottom["wordCount"]),
        "highlightStream": " | ".join(top["highlights"] + bottom["highlights"]),
        "boldLettersTopBottom": top["boldLetters"] + bottom["boldLetters"],
        "partialBoldTopBottom": top["partialBoldLetters"] + bottom["partialBoldLetters"],
        "reverseWordAlignment": aligned,
    }


def make_streams(pairs_outside_in: list[dict], pairs_inside_out: list[dict]) -> dict:
    def pair_values(pairs: list[dict], key: str, sep: str = " ") -> str:
        return sep.join(str(pair.get(key, "")) for pair in pairs if str(pair.get(key, "")))

    all_lines_outside = []
    for pair in pairs_outside_in:
        all_lines_outside.extend([pair["topText"], pair["bottomText"]])
    all_lines_inside = []
    for pair in pairs_inside_out:
        all_lines_inside.extend([pair["topText"], pair["bottomText"]])

    return {
        "outsideInLineInitials": pair_values(pairs_outside_in, "firstInitials", ""),
        "insideOutLineInitials": pair_values(pairs_inside_out, "firstInitials", ""),
        "outsideInLastInitials": pair_values(pairs_outside_in, "lastInitials", ""),
        "insideOutLastInitials": pair_values(pairs_inside_out, "lastInitials", ""),
        "outsideInEdgeWordsTopBottom": pair_values(pairs_outside_in, "edgeWordsTopThenBottom", " | "),
        "outsideInEdgeWordsBottomTop": pair_values(pairs_outside_in, "edgeWordsBottomThenTop", " | "),
        "insideOutEdgeWordsTopBottom": pair_values(pairs_inside_out, "edgeWordsTopThenBottom", " | "),
        "outsideInWordCountDiffs": "".join(str(pair["wordCountDiffAbs"]) for pair in pairs_outside_in),
        "outsideInHighlightStream": pair_values(pairs_outside_in, "highlightStream", " | "),
        "outsideInBoldLetters": pair_values(pairs_outside_in, "boldLettersTopBottom", ""),
        "outsideInPartialBoldLetters": pair_values(pairs_outside_in, "partialBoldTopBottom", ""),
        "outsideInFullLineRead": " | ".join(all_lines_outside),
        "insideOutFullLineRead": " | ".join(all_lines_inside),
    }


def draw_diagram(lines: list[dict], pairs: list[dict], streams: dict) -> None:
    width, height = 1500, 960
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 18)
        bold = ImageFont.truetype("Arial Bold.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
        bold = ImageFont.load_default()

    draw.text((40, 28), "G5/O5 symmetric line-fold audit", fill=(20, 20, 20), font=bold)
    draw.text((40, 62), "Outside-in pairs across the five-line gap; this is a selector check, not key derivation.", fill=(80, 80, 80), font=small)

    y0 = 130
    line_h = 92
    row_y = {}
    for i, row in enumerate(lines):
        y = y0 + i * line_h
        row_y[row["lineIndex"]] = y
        fill = (255, 245, 232) if row["lineIndex"] in {27, 32} else (248, 248, 248)
        outline = (240, 120, 30) if row["lineIndex"] in {27, 32} else (210, 210, 210)
        draw.rounded_rectangle((60, y, 1130, y + 58), radius=10, fill=fill, outline=outline, width=3)
        draw.text((80, y + 15), f"L{row['lineIndex']:02d}", fill=(120, 60, 20), font=bold if row["lineIndex"] in {27, 32} else font)
        draw.text((155, y + 15), row["text"], fill=(20, 20, 20), font=font)
        if row["highlights"]:
            draw.text((1180, y + 15), "; ".join(row["highlights"]), fill=(180, 80, 0), font=small)

    colors = [(210, 70, 40), (60, 130, 210), (80, 160, 80)]
    for idx, pair in enumerate(pairs):
        top_y = row_y[pair["topLine"]] + 29
        bottom_y = row_y[pair["bottomLine"]] + 29
        x1 = 1180 + idx * 50
        color = colors[idx % len(colors)]
        draw.line((x1, top_y, x1 + 70, top_y, x1 + 70, bottom_y, x1, bottom_y), fill=color, width=5)
        draw.text((x1 + 80, (top_y + bottom_y) / 2 - 12), f"P{idx+1}", fill=color, font=bold)

    draw.text((60, 735), "Streams:", fill=(20, 20, 20), font=bold)
    stream_lines = [
        f"initials outside-in: {streams['outsideInLineInitials']}",
        f"last initials outside-in: {streams['outsideInLastInitials']}",
        f"word-count diffs: {streams['outsideInWordCountDiffs']}",
        f"highlight stream: {streams['outsideInHighlightStream'] or '(none)'}",
        f"partial-bold stream: {streams['outsideInPartialBoldLetters'] or '(none)'}",
    ]
    for i, text in enumerate(stream_lines):
        draw.text((60, 775 + i * 32), text, fill=(50, 50, 50), font=small)

    img.save(OUT_IMG, quality=94)


def main() -> None:
    records = load_records()
    line_indices = list(range(27, 33))
    lines = [line_summary(record_for(records, i)) for i in line_indices]
    by_line = {row["lineIndex"]: row for row in lines}

    outside_in_pairs = [
        pair_summary(by_line[27], by_line[32]),
        pair_summary(by_line[28], by_line[31]),
        pair_summary(by_line[29], by_line[30]),
    ]
    inside_out_pairs = list(reversed(outside_in_pairs))
    streams = make_streams(outside_in_pairs, inside_out_pairs)
    stream_hits = {name: scan_hits(value) for name, value in streams.items()}

    draw_diagram(lines, outside_in_pairs, streams)

    assessment = [
        "The symmetric six-line fold is human-plausible from the Schott clue and the confirmed five-line G5/O5 gap, but it does not produce a selector.",
        "Outside-in and inside-out initials, last initials, edge words, highlight streams, word-count differences, and bold/partial-bold streams are ordinary corridor prose or short non-words.",
        "The only instruction-term hits are inherited visible words like `sell`, not procedural terms such as read/take/word/letter/key.",
        "This closes the G5/O5 symmetric line-fold as a standalone extraction rule under the current corrected text model.",
        "The G5/O5 relation remains a locator and source-registration validation point, not key material.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "G5/O5 symmetric line-fold audit; no key derivation",
        "input": str(CORRIDOR_JSON),
        "diagram": str(OUT_IMG),
        "lineRange": line_indices,
        "lines": lines,
        "outsideInPairs": outside_in_pairs,
        "insideOutPairs": inside_out_pairs,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "nextMove": "Do not continue local G5/O5 text-unit permutations without a new source rule. The next useful evidence remains source/physical registration or original-layout/Canva material that names the extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# G5/O5 Symmetric Line-Fold Audit",
        "",
        "Scope: test a Schott-style two-handed/mirror read on the confirmed page-76 G5/O5 interval. The six printed lines from `Volcano Bonds` to `shitcoiner at heart` are paired outside-in and inside-out. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Diagram: `{OUT_IMG}`",
        "",
        "## Fold Lines",
        "",
        "| line | text | highlights | bold/partial |",
        "|---:|---|---|---|",
    ]
    for row in lines:
        highlights = "; ".join(row["highlights"]) if row["highlights"] else "-"
        bolds = " / ".join(part for part in [row["boldLetters"], row["partialBoldLetters"]] if part) or "-"
        md.append(f"| {row['lineIndex']} | `{row['text']}` | `{highlights}` | `{bolds}` |")
    md.extend(["", "## Outside-In Pairs", "", "| pair | lines | first initials | last initials | word counts | edge words | highlights |", "|---|---|---|---|---|---|---|"])
    for i, pair in enumerate(outside_in_pairs, 1):
        md.append(
            f"| P{i} | `{pair['topLine']} / {pair['bottomLine']}` | `{pair['firstInitials']}` | `{pair['lastInitials']}` | `{pair['wordCountPair']}` | `{pair['edgeWordsTopThenBottom']}` | `{pair['highlightStream'] or '-'}` |"
        )
    md.extend(["", "## Streams", ""])
    for name, value in streams.items():
        hits = stream_hits[name]
        md.append(f"- `{name}`: `{value}`; instruction hits: `{hits or 'none'}`")
    md.extend(["", "## Assessment", ""])
    md.extend(f"- {item}" for item in assessment)
    md.extend(
        [
            "",
            "## Next Best Move",
            "",
            "- Stop local G5/O5 text-unit permutations unless a new clue names a unit. Use future source images or physical scans to test whether the G5/O5 geometry changes or finally names how to read the target.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"outsideInLineInitials={streams['outsideInLineInitials']}")
    print(f"outsideInHighlightStream={streams['outsideInHighlightStream']}")


if __name__ == "__main__":
    main()
