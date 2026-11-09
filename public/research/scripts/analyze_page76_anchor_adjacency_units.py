#!/usr/bin/env python3
"""Audit small adjacency units around the four active page-76 anchors.

This experiment asks whether the source-gated anchor boxes expose a simple
human-readable selector by taking adjacent words/lines around the anchors. It
does not generate key candidates, hashes, seed phrases, WIFs, or addresses.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
MARKS = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
TYPEKA = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json"
OVERLAY = ROOT / "analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units"
OUT_JSON = OUT_DIR / "page76_anchor_adjacency_units.json"
OUT_MD = OUT_DIR / "page76_anchor_adjacency_units.md"


ANCHORS = [
    {
        "id": "buying_dip",
        "label": "buying the dip",
        "color": "orange",
        "box": [1328, 2160, 1760, 2226],
        "canonicalLineIndex": 22,
    },
    {
        "id": "one_billion",
        "label": "$1 billion",
        "color": "black",
        "box": [430, 2400, 690, 2447],
        "canonicalLineIndex": 25,
    },
    {
        "id": "volcano_bonds",
        "label": "Volcano Bonds",
        "color": "black",
        "box": [795, 2544, 1196, 2592],
        "canonicalLineIndex": 27,
    },
    {
        "id": "shitcoiner_heart",
        "label": "shitcoiner at heart",
        "color": "orange",
        "box": [1040, 2932, 1661, 2982],
        "canonicalLineIndex": 32,
    },
]


def load_page76_words() -> list[dict[str, Any]]:
    data = json.loads(ARTICLE_MAP.read_text(encoding="utf-8"))
    page = next(page for page in data["pages"] if page["page"] == 76)
    return page["words"]


def load_rows() -> list[dict[str, Any]]:
    return json.loads(MARKS.read_text(encoding="utf-8"))["rowsUsed"]


def row_for_line(rows: list[dict[str, Any]], line_index: int) -> dict[str, Any]:
    return next(row for row in rows if row["canonicalLineIndex"] == line_index)


def words_on_row(words: list[dict[str, Any]], row_y: float, tol: float = 34.0) -> list[dict[str, Any]]:
    return sorted([word for word in words if abs(word["center"][1] - row_y) <= tol], key=lambda word: word["center"][0])


def text_join(words: list[dict[str, Any]], limit: int | None = None, reverse: bool = False) -> str:
    selected = words[::-1] if reverse else words
    if limit is not None:
        selected = selected[:limit]
    return " ".join(word["text"] for word in selected)


def nearest_word(words: list[dict[str, Any]], x: float) -> str:
    if not words:
        return ""
    return min(words, key=lambda word: abs(word["center"][0] - x))["text"]


def phrase_initials(text: str) -> str:
    return "".join(part[0].lower() for part in text.replace("$", "").split() if part and any(ch.isalnum() for ch in part))


def phrase_edges(text: str) -> str:
    cleaned = ["".join(ch.lower() for ch in part if ch.isalnum()) for part in text.split()]
    cleaned = [part for part in cleaned if part]
    if not cleaned:
        return ""
    return cleaned[0][0] + cleaned[-1][-1]


def audit_anchor(anchor: dict[str, Any], rows: list[dict[str, Any]], words: list[dict[str, Any]], typeka_by_id: dict[str, Any]) -> dict[str, Any]:
    row = row_for_line(rows, anchor["canonicalLineIndex"])
    same = words_on_row(words, row["y"])
    x1, y1, x2, y2 = anchor["box"]
    xmid = (x1 + x2) / 2
    left = [word for word in same if word["box"][2] < x1]
    right = [word for word in same if word["box"][0] > x2]
    inside = [word for word in same if not (word["box"][2] < x1 or word["box"][0] > x2)]

    above_rows = [candidate for candidate in rows if candidate["y"] < row["y"]]
    below_rows = [candidate for candidate in rows if candidate["y"] > row["y"]]
    above = above_rows[-1] if above_rows else None
    below = below_rows[0] if below_rows else None
    above_words = words_on_row(words, above["y"]) if above else []
    below_words = words_on_row(words, below["y"]) if below else []
    span_above = [word for word in above_words if x1 - 40 <= word["center"][0] <= x2 + 40]
    span_below = [word for word in below_words if x1 - 40 <= word["center"][0] <= x2 + 40]

    typeka = typeka_by_id[anchor["id"]]["docm"]
    return {
        "id": anchor["id"],
        "label": anchor["label"],
        "color": anchor["color"],
        "box": anchor["box"],
        "canonicalLineIndex": anchor["canonicalLineIndex"],
        "canonicalLine": row["canonicalText"],
        "docm": {
            "dominantFont": typeka.get("dominantFont"),
            "boldFraction": typeka.get("boldFraction"),
            "mixFraction": typeka.get("mixFraction"),
            "highlights": typeka.get("highlights"),
        },
        "sameLine": {
            "ocrInside": text_join(inside),
            "leftAll": text_join(left),
            "rightAll": text_join(right),
            "leftNearest4RightToLeft": text_join(left, limit=4, reverse=True),
            "rightNearest4": text_join(right, limit=4),
            "leftBoundaryWord": nearest_word(left, x1),
            "rightBoundaryWord": nearest_word(right, x2),
        },
        "vertical": {
            "aboveLineIndex": above["canonicalLineIndex"] if above else None,
            "aboveLine": above["canonicalText"] if above else "",
            "aboveSpanWords": text_join(span_above),
            "aboveCenterWord": nearest_word(above_words, xmid),
            "belowLineIndex": below["canonicalLineIndex"] if below else None,
            "belowLine": below["canonicalText"] if below else "",
            "belowSpanWords": text_join(span_below),
            "belowCenterWord": nearest_word(below_words, xmid),
        },
        "letterUnits": {
            "phraseInitials": phrase_initials(anchor["label"]),
            "phraseEdges": phrase_edges(anchor["label"]),
            "firstLetter": phrase_initials(anchor["label"])[:1],
            "lastLetter": phrase_edges(anchor["label"])[-1:] if phrase_edges(anchor["label"]) else "",
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    words = load_page76_words()
    rows = load_rows()
    typeka = json.loads(TYPEKA.read_text(encoding="utf-8"))
    typeka_by_id = {row["id"]: row for row in typeka["rows"]}
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    anchor_records = [audit_anchor(anchor, rows, words, typeka_by_id) for anchor in ANCHORS]
    visual_order = anchor_records
    black_then_orange = [record for record in anchor_records if record["color"] == "black"] + [record for record in anchor_records if record["color"] == "orange"]
    orange_then_black = [record for record in anchor_records if record["color"] == "orange"] + [record for record in anchor_records if record["color"] == "black"]

    streams = {
        "visualOrderColors": "".join(record["color"][0].upper() for record in visual_order),
        "visualOrderPhraseInitials": " ".join(record["letterUnits"]["phraseInitials"] for record in visual_order),
        "visualOrderPhraseEdges": " ".join(record["letterUnits"]["phraseEdges"] for record in visual_order),
        "visualOrderRightBoundaryWords": " | ".join(record["sameLine"]["rightBoundaryWord"] or "-" for record in visual_order),
        "visualOrderLeftBoundaryWords": " | ".join(record["sameLine"]["leftBoundaryWord"] or "-" for record in visual_order),
        "visualOrderAboveCenterWords": " | ".join(record["vertical"]["aboveCenterWord"] or "-" for record in visual_order),
        "visualOrderBelowCenterWords": " | ".join(record["vertical"]["belowCenterWord"] or "-" for record in visual_order),
        "blackThenOrangeInitials": " ".join(record["letterUnits"]["phraseInitials"] for record in black_then_orange),
        "orangeThenBlackInitials": " ".join(record["letterUnits"]["phraseInitials"] for record in orange_then_black),
    }

    assessment = [
        "Adjacency around the four anchors gives coherent local context but no instruction-like message.",
        "The only compact structure is the color order O-B-B-O and the paired highlight classes: black amount/bond anchors, orange action/identity anchors.",
        "Right-boundary words mostly reproduce prose continuation rather than a selector: buying dip has no right word, $1 billion points to in/bitcoin, Volcano Bonds points to to/pay, O5 has no right word.",
        "Vertical center probes land on ordinary corridor prose and do not form read/fold/mirror/page/line/word/letter instructions.",
        "This closes typography-adjacency as a standalone rule unless a new source tells us which side or edge to read.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-gated adjacency/unit audit around the four page-76 anchors; no key derivation",
        "sources": {
            "articleMap": str(ARTICLE_MAP.relative_to(ROOT)),
            "rows": str(MARKS.relative_to(ROOT)),
            "typeka": str(TYPEKA.relative_to(ROOT)),
            "overlay": str(OVERLAY.relative_to(ROOT)),
        },
        "anchors": anchor_records,
        "streams": streams,
        "assessment": assessment,
        "decision": "Do not promote anchor adjacency to extraction evidence; it is only a local context check.",
        "nextMove": "Use the O-B-B-O anchor structure as a comparison signature against OVERDOSE/package/pill layout mechanics, especially whether other Max articles use the same four-anchor pattern.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page 76 Anchor Adjacency Units",
        "",
        "Scope: small source-gated adjacency/unit audit around the four active page-76 anchors. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay source: `{result['sources']['overlay']}`",
        "",
        "## Anchor Reads",
        "",
        "| anchor | style | same-line left edge | same-line right edge | above center | below center |",
        "|---|---|---|---|---|---|",
    ]
    for record in anchor_records:
        style = f"{record['color']}; {record['docm']['dominantFont']}; bold {record['docm']['boldFraction']}; hl {record['docm']['highlights']}"
        lines.append(
            f"| `{record['label']}` | `{style}` | `{record['sameLine']['leftBoundaryWord'] or '-'}` | "
            f"`{record['sameLine']['rightBoundaryWord'] or '-'}` | `{record['vertical']['aboveCenterWord'] or '-'}` | "
            f"`{record['vertical']['belowCenterWord'] or '-'}` |"
        )
    lines.extend(["", "## Compact Streams", ""])
    for key, value in streams.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
