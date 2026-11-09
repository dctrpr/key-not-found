#!/usr/bin/env python3
"""Compare the page-76 O-B-B-O anchor signature against comparison layouts.

This uses existing body-highlighter component boxes and asks whether the active
page-76 sequence (orange, black, black, orange in the lower corridor) is common
in other Max/OVERDOSE article pages. It is a visual/style recurrence audit, not
an extraction or key-search branch.
"""

from __future__ import annotations

import itertools
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json"
ADJACENCY = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
OUT_DIR = ROOT / "analysis_outputs/comparison_articles/obbo_anchor_signature"
OUT_JSON = OUT_DIR / "obbo_anchor_signature.json"
OUT_MD = OUT_DIR / "obbo_anchor_signature.md"


# Active page-76 template from the trusted overlay/adjacency audit.
TEMPLATE = [
    {"id": "buying_dip", "color": "O", "box": [1328, 2160, 1760, 2226]},
    {"id": "one_billion", "color": "B", "box": [430, 2400, 690, 2447]},
    {"id": "volcano_bonds", "color": "B", "box": [795, 2544, 1196, 2592]},
    {"id": "shitcoiner_heart", "color": "O", "box": [1040, 2932, 1661, 2982]},
]
TEMPLATE_SIZE = [2544, 3264]


def norm_box(box: list[float], size: list[int]) -> dict[str, float]:
    w, h = size
    x1, y1, x2, y2 = box
    return {
        "cx": ((x1 + x2) / 2) / w,
        "cy": ((y1 + y2) / 2) / h,
        "bw": (x2 - x1) / w,
        "bh": (y2 - y1) / h,
    }


def box_center(box: list[float]) -> tuple[float, float]:
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def template_points() -> list[dict[str, float]]:
    return [norm_box(item["box"], TEMPLATE_SIZE) for item in TEMPLATE]


def page_components(record: dict[str, Any]) -> list[dict[str, Any]]:
    comps: list[dict[str, Any]] = []
    for box in record["orangeBoxes"]:
        comps.append({"color": "O", "box": box, "norm": norm_box(box, record["size"])})
    for box in record["darkBoxes"]:
        comps.append({"color": "B", "box": box, "norm": norm_box(box, record["size"])})
    comps.sort(key=lambda item: (item["norm"]["cy"], item["norm"]["cx"]))
    return comps


def quartet_signature(items: list[dict[str, Any]]) -> str:
    return "".join(item["color"] for item in items)


def quartet_score(items: list[dict[str, Any]], template: list[dict[str, float]]) -> dict[str, Any]:
    distances = []
    width_penalties = []
    lower_penalty = 0.0
    for item, target in zip(items, template):
        dx = item["norm"]["cx"] - target["cx"]
        dy = item["norm"]["cy"] - target["cy"]
        distances.append(math.sqrt(dx * dx + dy * dy))
        width_penalties.append(abs(item["norm"]["bw"] - target["bw"]))
        if item["norm"]["cy"] < 0.52:
            lower_penalty += 0.18
    score = sum(distances) + 0.25 * sum(width_penalties) + lower_penalty
    return {
        "score": round(score, 4),
        "positionDistance": round(sum(distances), 4),
        "widthPenalty": round(sum(width_penalties), 4),
        "lowerPenalty": round(lower_penalty, 4),
    }


def find_obbo(record: dict[str, Any], template: list[dict[str, float]]) -> list[dict[str, Any]]:
    comps = page_components(record)
    matches = []
    for combo in itertools.combinations(comps, 4):
        if quartet_signature(list(combo)) != "OBBO":
            continue
        score = quartet_score(list(combo), template)
        matches.append(
            {
                "score": score["score"],
                "scoreBreakdown": score,
                "boxes": [item["box"] for item in combo],
                "centers": [box_center(item["box"]) for item in combo],
                "normalizedCenters": [[round(item["norm"]["cx"], 3), round(item["norm"]["cy"], 3)] for item in combo],
            }
        )
    matches.sort(key=lambda item: item["score"])
    return matches


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grammar = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    adjacency = json.loads(ADJACENCY.read_text(encoding="utf-8"))
    template = template_points()

    page_results = []
    for record in grammar["pageRecords"]:
        matches = find_obbo(record, template)
        page_results.append(
            {
                "source": record["source"],
                "page": record["page"],
                "path": record["path"],
                "grammarScore": record["grammarScore"],
                "orangeLineBands": record["orangeLineBands"],
                "darkLineBands": record["darkLineBands"],
                "obboCount": len(matches),
                "bestObbo": matches[0] if matches else None,
            }
        )

    pages_with_obbo = [record for record in page_results if record["obboCount"]]
    pages_with_obbo.sort(key=lambda item: item["bestObbo"]["score"] if item["bestObbo"] else 999)
    independent = [record for record in pages_with_obbo if record["source"] != "issue24_toxic_af"]
    issue24 = [record for record in pages_with_obbo if record["source"] == "issue24_toxic_af"]
    exact_page76 = next((record for record in page_results if record["source"] == "issue24_toxic_af" and record["page"] == 4), None)

    assessment = [
        "The active page-76 anchor order is O-B-B-O, but OBBO as a color sequence is not unique by itself.",
        "When normalized position is included, Issue 24 page 4 is the expected closest match because it contains the trusted page-76 anchors.",
        "Independent comparison pages can produce OBBO only when they have enough colored body bands, but their best matches are weak layout/style recurrences rather than the lower page-76 amount/bond/action/identity corridor.",
        "OBBO should remain a local page-76 signature, not an extraction rule. It is useful for future source comparison only if the same four semantic anchors are present.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "visual recurrence audit for the page-76 O-B-B-O anchor signature using existing comparison body-highlighter boxes; no key derivation",
        "sources": {
            "bodyHighlighterGrammar": str(GRAMMAR.relative_to(ROOT)),
            "anchorAdjacency": str(ADJACENCY.relative_to(ROOT)),
        },
        "template": TEMPLATE,
        "templateCompactStreams": adjacency.get("streams", {}),
        "summary": {
            "pagesWithObbo": len(pages_with_obbo),
            "issue24PagesWithObbo": len(issue24),
            "independentPagesWithObbo": len(independent),
            "page76BestScore": exact_page76["bestObbo"]["score"] if exact_page76 and exact_page76["bestObbo"] else None,
            "bestIndependentScore": independent[0]["bestObbo"]["score"] if independent else None,
            "bestIndependent": {
                "source": independent[0]["source"],
                "page": independent[0]["page"],
                "score": independent[0]["bestObbo"]["score"],
            }
            if independent
            else None,
        },
        "closestMatches": pages_with_obbo[:12],
        "assessment": assessment,
        "decision": "Do not use OBBO alone as a selector; keep it as a source-comparison signature tied to the four page-76 semantic anchors.",
        "nextMove": "Inspect p80/package or pill-count mechanics only where they can choose among the four page-76 anchors; do not compare broad colored layout metrics further.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# O-B-B-O Anchor Signature Audit",
        "",
        "Scope: visual recurrence audit for the page-76 O-B-B-O anchor signature using existing body-highlighter boxes. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Body grammar source: `{result['sources']['bodyHighlighterGrammar']}`",
        f"- Anchor source: `{result['sources']['anchorAdjacency']}`",
        "",
        "## Summary",
        "",
        f"- Pages with an O-B-B-O sequence: `{result['summary']['pagesWithObbo']}`",
        f"- Issue 24 pages with O-B-B-O: `{result['summary']['issue24PagesWithObbo']}`",
        f"- Independent comparison pages with O-B-B-O: `{result['summary']['independentPagesWithObbo']}`",
        f"- Page-76/template best score: `{result['summary']['page76BestScore']}`",
        f"- Best independent score: `{result['summary']['bestIndependentScore']}`",
        "",
        "## Closest Matches",
        "",
        "| source | page | O-B-B-O count | best score | grammar score | normalized centers |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for record in pages_with_obbo[:12]:
        best = record["bestObbo"]
        lines.append(
            f"| `{record['source']}` | `{record['page']}` | `{record['obboCount']}` | `{best['score']}` | "
            f"`{record['grammarScore']}` | `{best['normalizedCenters']}` |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
