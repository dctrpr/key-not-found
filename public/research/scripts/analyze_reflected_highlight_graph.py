#!/usr/bin/env python3
"""Summarize reflected-mask hits against exact high-res highlighted spans.

This is a geometry/selector audit. It treats reflected OCR/mask hits as
evidence for ordering or emphasis, not as private-key material.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_JSON = ROOT / "analysis_outputs/3d_article_map/exact_highres_reflection_geometry.json"
OUT_JSON = ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json"
OUT_MD = ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.md"


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text)


def initials(text: str) -> str:
    return "".join(w[0] for w in words(text) if w)


def clean(text: str, limit: int = 110) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def hit_strength(hit: dict) -> str:
    if hit["overlapVsReflection"] >= 0.7 and hit["overlapVsSpan"] >= 0.02:
        return "strong"
    if hit["overlapVsReflection"] >= 0.45 and hit["overlapVsSpan"] >= 0.01:
        return "medium"
    return "weak"


def main() -> None:
    with IN_JSON.open() as f:
        data = json.load(f)

    edges = []
    for row in data["rows"]:
        for hit in row.get("reflectionHits", []):
            edge = {
                "targetId": row["id"],
                "targetColor": row["color"],
                "targetPage": row["page"],
                "targetText": row["text"],
                "targetInitial": initials(row["text"])[:1],
                "sourcePage": hit["source"],
                "reflectionId": hit["reflectionId"],
                "reflectionText": hit["reflectionText"],
                "reflectionInitials": initials(hit["reflectionText"]),
                "overlapArea": hit["overlapArea"],
                "overlapVsSpan": hit["overlapVsSpan"],
                "overlapVsReflection": hit["overlapVsReflection"],
                "centerDistance": hit["centerDistance"],
                "strength": hit_strength(hit),
            }
            edges.append(edge)

    strong = [e for e in edges if e["strength"] == "strong"]
    medium_plus = [e for e in edges if e["strength"] in {"strong", "medium"}]
    page76 = [e for e in medium_plus if e["targetPage"] == 76]

    def sort_key(e: dict):
        color_rank = {"orange": 0, "grey_black": 1}.get(e["targetColor"], 2)
        return (e["targetPage"], color_rank, e["targetId"], e["sourcePage"], e["centerDistance"])

    page76_sorted = sorted(page76, key=sort_key)
    source_pattern = "".join(str(e["sourcePage"]) for e in page76_sorted)
    target_initials = "".join(e["targetInitial"] for e in page76_sorted)
    reflected_initials = "|".join(e["reflectionInitials"] for e in page76_sorted)

    by_target = defaultdict(list)
    for e in medium_plus:
        by_target[e["targetId"]].append(e)

    pair_counts = Counter((e["sourcePage"], e["targetPage"]) for e in medium_plus)
    result = {
        "source": str(IN_JSON),
        "summary": {
            "edges": len(edges),
            "strongEdges": len(strong),
            "mediumPlusEdges": len(medium_plus),
            "page76MediumPlusEdges": len(page76),
            "pairCounts": {f"{a}->{b}": n for (a, b), n in sorted(pair_counts.items())},
            "page76TargetInitials": target_initials,
            "page76SourcePagePattern": source_pattern,
            "page76ReflectedInitials": reflected_initials,
        },
        "edges": edges,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Reflected Highlight Graph",
        "",
        "Scope: exact high-res highlighted spans intersected by reflected OCR/mask hits. This checks whether geometry creates a clean ordering rule; it does not generate key candidates.",
        "",
        "## Summary",
        "",
        f"- Total reflected-hit edges: {len(edges)}",
        f"- Strong edges: {len(strong)}",
        f"- Medium-or-strong edges: {len(medium_plus)}",
        f"- Page-76 medium-or-strong edges: {len(page76)}",
        f"- Page-76 target initials by graph order: `{target_initials}`",
        f"- Page-76 source-page pattern by graph order: `{source_pattern}`",
        f"- Page-76 reflected-text initials by graph order: `{reflected_initials}`",
        "",
        "## Page Pair Counts",
        "",
    ]
    if pair_counts:
        for (src, tgt), count in sorted(pair_counts.items()):
            lines.append(f"- {src} -> {tgt}: {count}")
    else:
        lines.append("- None")

    lines.extend(["", "## Page 76 Medium+ Edges", ""])
    for e in page76_sorted:
        lines.append(
            f"- {e['strength']} {e['sourcePage']}->{e['targetPage']} "
            f"`{clean(e['reflectionText'], 70)}` -> {e['targetColor']} `{clean(e['targetText'], 80)}` "
            f"(span={e['overlapVsSpan']:.3f}, reflected={e['overlapVsReflection']:.3f}, dist={e['centerDistance']:.1f})"
        )

    lines.extend(["", "## Target Groups", ""])
    for target_id, group in sorted(by_target.items()):
        first = group[0]
        srcs = ",".join(str(e["sourcePage"]) for e in sorted(group, key=lambda x: (x["sourcePage"], x["centerDistance"])))
        strengths = ",".join(e["strength"][0].upper() for e in sorted(group, key=lambda x: (x["sourcePage"], x["centerDistance"])))
        lines.append(
            f"- {target_id} p{first['targetPage']} {first['targetColor']} `{clean(first['targetText'], 90)}`: "
            f"sources={srcs} strengths={strengths}"
        )

    lines.extend([
        "",
        "## Assessment",
        "",
        "- The reflected graph is concentrated on page 76, but the medium/strong edges repeat broad prose areas rather than producing a one-edge-per-highlight selector.",
        "- The page-76 graph-order stream is not readable as an instruction. Source-page ordering is dominated by repeated 79 and 78 hits, not a clean mirror/fold sequence.",
        "- The most meaningful evidence remains semantic: reflected text keeps landing near the El Salvador/Bukele/IMF/bitcoin-buying corridor. It is not yet precise enough for letter-level extraction.",
        "- Next best move: compare source scans/physical copy, or manually test one mirror-clue rule on the page-76 corridor only.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
