#!/usr/bin/env python3
"""Explicit mirror-writing read rule on the supported page-76 corridor.

This is not a key search. It takes the page-76 reflected-highlight graph and
tests the literal mirror-writing operation: reverse the reflected source text at
character and word level, then inspect whether the paired source/target stream
produces a readable instruction.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_GRAPH = ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json"
IN_HIGHRES = ROOT / "analysis_outputs/source_audit/highres_page76_mirror_selector.json"
OUT_JSON = ROOT / "analysis_outputs/3d_article_map/page76_mirror_read_rule.json"
OUT_MD = ROOT / "analysis_outputs/3d_article_map/page76_mirror_read_rule.md"


SELECTOR_WORDS = [
    "READ",
    "TAKE",
    "USE",
    "LEFT",
    "RIGHT",
    "FIRST",
    "LAST",
    "WORD",
    "WORDS",
    "LETTER",
    "LETTERS",
    "PAGE",
    "LINE",
    "LINES",
    "MIRROR",
    "FOLD",
    "BACK",
    "REVERSE",
    "KEY",
    "PRIVATE",
    "SEED",
    "WALLET",
    "BUY",
    "DIP",
    "BILLION",
    "IMF",
    "SALVADOR",
    "VOLCANO",
    "BONDS",
]


def clean_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text)


def letters(text: str) -> str:
    return re.sub(r"[^A-Za-z]", "", text)


def reverse_chars(text: str) -> str:
    return text[::-1]


def reverse_words(text: str) -> str:
    return " ".join(reversed(clean_words(text)))


def initials(text: str) -> str:
    return "".join(w[0] for w in clean_words(text) if w)


def lasts(text: str) -> str:
    return "".join(w[-1] for w in clean_words(text) if w)


def selector_hits(text: str) -> list[str]:
    compact = letters(text).upper()
    return [w for w in SELECTOR_WORDS if w in compact]


def compact_preview(text: str, n: int = 100) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def main() -> None:
    with IN_GRAPH.open() as f:
        graph = json.load(f)
    with IN_HIGHRES.open() as f:
        highres = json.load(f)

    graph_edges = [
        e
        for e in graph["edges"]
        if e["targetPage"] == 76 and e["strength"] in {"strong", "medium"}
    ]

    # Keep the order spatial/reading-ish by target kind/index, then source page.
    kind_rank = {"orange": 0, "grey_black": 1, "black": 1}
    graph_edges.sort(
        key=lambda e: (
            kind_rank.get(e["targetColor"], 2),
            e["targetText"],
            e["sourcePage"],
            e["centerDistance"],
        )
    )

    rows = []
    for i, e in enumerate(graph_edges, 1):
        source = e["reflectionText"]
        target = e["targetText"]
        row = {
            "index": i,
            "sourcePage": e["sourcePage"],
            "targetColor": e["targetColor"],
            "source": source,
            "sourceReverseChars": reverse_chars(source),
            "sourceReverseWords": reverse_words(source),
            "target": target,
            "sourceInitials": initials(source),
            "sourceLasts": lasts(source),
            "targetInitials": initials(target),
            "targetLasts": lasts(target),
            "selectorHits": selector_hits(source + " " + target),
            "reversedSelectorHits": selector_hits(reverse_chars(source) + " " + target),
        }
        rows.append(row)

    streams = {
        "source_initials": "".join(r["sourceInitials"] for r in rows),
        "source_lasts": "".join(r["sourceLasts"] for r in rows),
        "target_initials": "".join(r["targetInitials"] for r in rows),
        "target_lasts": "".join(r["targetLasts"] for r in rows),
        "source_initials_reversed_edge_order": "".join(r["sourceInitials"] for r in reversed(rows)),
        "target_initials_reversed_edge_order": "".join(r["targetInitials"] for r in reversed(rows)),
        "source_pages": "".join(str(r["sourcePage"]) for r in rows),
    }

    grouped = defaultdict(list)
    for r in rows:
        grouped[r["target"]].append(r)

    # Include high-res-only meaningful edges as a cross-check; these are cleaner
    # geometrically but have less OCR text detail.
    highres_edges = highres.get("meaningfulEdges", [])

    result = {
        "source": {
            "graph": str(IN_GRAPH),
            "highres": str(IN_HIGHRES),
        },
        "summary": {
            "graphRows": len(rows),
            "highresRows": len(highres_edges),
            "streams": streams,
        },
        "rows": rows,
        "groupedByTarget": grouped,
        "highresEdges": highres_edges,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Page 76 Mirror Read Rule",
        "",
        "Scope: take only medium/strong reflected hits landing on page 76 and apply the literal mirror-writing read rule: reverse reflected source text by characters and by words. This checks for a readable instruction, not a key.",
        "",
        "## Summary",
        "",
        f"- Reflected graph rows: {len(rows)}",
        f"- High-res-only cross-check rows: {len(highres_edges)}",
        f"- Source-page stream: `{streams['source_pages']}`",
        f"- Source initials: `{streams['source_initials']}`",
        f"- Target initials: `{streams['target_initials']}`",
        f"- Source initials, reversed edge order: `{streams['source_initials_reversed_edge_order']}`",
        f"- Target initials, reversed edge order: `{streams['target_initials_reversed_edge_order']}`",
        "",
        "## Paired Reads",
        "",
    ]
    for target, group in grouped.items():
        lines.append(f"### Target: `{compact_preview(target, 120)}`")
        for r in group:
            hits = sorted(set(r["selectorHits"] + r["reversedSelectorHits"]))
            hit_text = ", ".join(hits) if hits else "none"
            lines.append(
                f"- p{r['sourcePage']} source `{compact_preview(r['source'], 90)}` -> "
                f"revWords `{compact_preview(r['sourceReverseWords'], 90)}`; selector words: {hit_text}"
            )
        lines.append("")

    lines.extend(
        [
            "## High-Res Cross-Check",
            "",
        ]
    )
    if highres_edges:
        for e in highres_edges:
            lines.append(
                f"- p{e['sourcePage']} `{compact_preview(e['sourceLabel'], 80)}` -> "
                f"p76 {e['targetColor']} `{compact_preview(e['targetLabel'], 80)}`"
            )
    else:
        lines.append("- No high-res-only rows.")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- Reversing the reflected source text by words or characters does not reveal an independent instruction like read/take/use/page/line/letter/key.",
            "- Selector-word hits are semantic words already visible in the corridor: buy, dip, IMF, Salvador, billion, etc.",
            "- The most robust reading remains semantic rather than procedural: energy/fiat/debt language points into page-76 buying/IMF/$1 billion material.",
            "- Next best move: do not keep transforming text streams. Either acquire/align a physical scan, or manually inspect the high-res page-76 corridor for non-text marks and line-level reading order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
