#!/usr/bin/env python3
"""Build a concise selector-gap map from the current investigation artifacts.

The goal is to separate live evidence from closed mechanics and identify the
smallest missing rule needed before any more key-format work makes sense.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "selector_gap_map.json"
OUT_MD = OUT / "selector_gap_map.md"


FILES = {
    "graph": ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json",
    "registered": ROOT / "analysis_outputs/source_audit/registered_76_79_selector.json",
    "source_gap": ROOT / "analysis_outputs/source_audit/source_registration_gap.json",
    "typeka_provenance": ROOT / "analysis_outputs/source_audit/typography_source_provenance.json",
    "typeka_intersections": ROOT / "analysis_outputs/docm_format_sources/typeka_reflection_intersection_audit.json",
    "corridor_font_order": ROOT / "analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.json",
    "lower_marks": ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json",
    "dead_blacklist": ROOT / "analysis_outputs/dead_branch_blacklist.md",
}


def load_json(key: str) -> dict:
    return json.loads(FILES[key].read_text())


def closed_branch_count() -> int:
    text = FILES["dead_blacklist"].read_text()
    section = text.split("## Still Active", 1)[0]
    return len(re.findall(r"^- ", section, flags=re.MULTILINE))


def active_branch_count() -> int:
    text = FILES["dead_blacklist"].read_text()
    if "## Still Active" not in text:
        return 0
    section = text.split("## Still Active", 1)[1]
    return len(re.findall(r"^- ", section, flags=re.MULTILINE))


def main() -> None:
    graph = load_json("graph")
    registered = load_json("registered")
    source_gap = load_json("source_gap")
    provenance = load_json("typeka_provenance")
    typeka_intersections = load_json("typeka_intersections")
    corridor_font = load_json("corridor_font_order")
    lower_marks = load_json("lower_marks")

    graph_summary = graph["summary"]
    registered_summary = registered["summary"]
    strongest_registered = registered["meaningfulRegisteredEdges"][0]
    source_rows = source_gap["rows"]
    article_rows = [row for row in source_rows if row["page"] != 80]
    mean_geometry_delta = round(
        sum(row["contentVsHighlightDelta"]["meanPx"] for row in article_rows) / len(article_rows),
        2,
    )
    max_geometry_delta = max(row["contentVsHighlightDelta"]["maxPx"] for row in source_rows)
    article_docm = next(item for item in provenance["docms"] if item["label"] == "article_with_fonts")
    comparison_pdfs = [item for item in provenance["pdfs"] if item["label"] in {"issue26_comparison", "bitcoin3_comparison"}]
    true_lower_marks = [
        item for item in lower_marks["analyses"] if item["classification"] == "standalone-mark"
    ]

    evidence = [
        {
            "claim": "Page 76 is the current target surface.",
            "status": "strong",
            "support": f"{graph_summary['page76MediumPlusEdges']} of {graph_summary['mediumPlusEdges']} medium/strong reflected edges land on page 76.",
        },
        {
            "claim": "The strongest local registration is a row/region anchor, not a letter selector.",
            "status": "strong",
            "support": (
                f"p79 box {strongest_registered['sourceIndex']} maps to p76 black {strongest_registered['targetIndex']} "
                f"with target coverage {strongest_registered['overlapVsTarget']} and center distance {strongest_registered['centerDistance']} px, "
                f"but registered pattern is only {registered_summary['registeredPattern']}."
            ),
        },
        {
            "claim": "The current high-res scan is geometry truth; OCR/source variants are too distorted for final selection.",
            "status": "strong",
            "support": f"Source-registration audit shows mean content-vs-highlight delta {mean_geometry_delta} px on pages 75-79, with max {max_geometry_delta} px including p80 package-art mismatch.",
        },
        {
            "claim": "Typeka is a formatting witness, but not yet a selector.",
            "status": "medium",
            "support": (
                f"Article with Fonts.docm records {article_docm['typekaFontChars']}; "
                f"p76 target sequence {corridor_font['streams']['matchedTargetLayerCodes']} and Typeka streams have no instruction hits."
            ),
        },
        {
            "claim": "The local comparison PDFs cannot prove Typeka uniqueness.",
            "status": "strong",
            "support": (
                "Issue_26.pdf and bitcoin3.pdf have no embedded font rows and no usable extractable text; "
                f"image counts {[item['imageCounts'] for item in comparison_pdfs]}."
            ),
        },
        {
            "claim": "Lower p76 brush/X marks reinforce the corridor, but do not add order.",
            "status": "medium",
            "support": (
                f"{len(true_lower_marks)} true standalone marks; pointer reads return adjacent Novogratz/distrust/shitcoiner prose only."
            ),
        },
    ]

    missing_rule = {
        "description": "A human-solvable selector must still supply four things: source layer, target region, ordering, and extraction unit.",
        "requiredPieces": [
            {
                "piece": "source layer",
                "currentBest": "high-res page 76 corridor plus reflected 78/79 evidence",
                "gap": "No independent instruction says whether the source layer is highlight color, Typeka state, physical bleed-through, or Canva-marked registration.",
            },
            {
                "piece": "target region",
                "currentBest": "page-76 El Salvador/Bukele/IMF/$1 billion/Volcano corridor",
                "gap": "Region is strong, but it is too broad for key extraction.",
            },
            {
                "piece": "ordering",
                "currentBest": "78/79 page-pair balance and the p79-yellow -> p76-black calibration anchor",
                "gap": "No tested ordering stream creates readable instruction or checksum-like material.",
            },
            {
                "piece": "extraction unit",
                "currentBest": "line/phrase units, not letters",
                "gap": "No rule decides first/last/bold/Mix/highlight/below/above words.",
            },
        ],
    }

    next_moves = [
        {
            "rank": 1,
            "move": "Recover source-level instruction/provenance",
            "why": "Most local mechanics now identify a corridor but not the selector. The next useful evidence is Max's original clue wording/thread, higher-resolution Canva assets, or layout-source provenance.",
            "localAction": "Search only for source artifacts not already ingested; avoid generating more key candidates.",
        },
        {
            "rank": 2,
            "move": "Physical magazine/photo branch",
            "why": "If a real page curl, bleed-through, or print registration changes alignment, it can reopen geometry. The current digital scan does not.",
            "localAction": "Wait for new scan/photo before repeating fold/hold-to-light overlays.",
        },
        {
            "rank": 3,
            "move": "One-rule manual solve reconstruction",
            "why": "The public clue likely points to one human action. The remaining task is to write and test one explicit rule at a time against page 76, not broad transformations.",
            "localAction": "For each proposed rule, require source page, target box, ordering, extraction unit, and expected readable output before running anything.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "selector-gap synthesis from current local artifacts; no key derivation",
        "closedBranchCount": closed_branch_count(),
        "activeBranchCount": active_branch_count(),
        "evidence": evidence,
        "missingRule": missing_rule,
        "nextMoves": next_moves,
        "decision": "Pause broad local geometry/key loops unless new source evidence changes the premise.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Selector Gap Map",
        "",
        "Scope: synthesize the current local evidence and identify what is still missing before more key-format or geometry work is justified. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Closed branch count: `{result['closedBranchCount']}`",
        f"- Active branch count: `{result['activeBranchCount']}`",
        "",
        "## What Is Strong Now",
        "",
    ]
    for item in evidence:
        lines.append(f"- **{item['claim']}** Status: `{item['status']}`. {item['support']}")

    lines.extend(["", "## Missing Selector Rule", "", missing_rule["description"], ""])
    for piece in missing_rule["requiredPieces"]:
        lines.append(f"- `{piece['piece']}`: current best `{piece['currentBest']}`; gap: {piece['gap']}")

    lines.extend(["", "## Ranked Next Moves", ""])
    for move in next_moves:
        lines.append(f"{move['rank']}. **{move['move']}**: {move['why']} Local action: {move['localAction']}")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not run more broad hashing, key promotion, local fold geometry, Typeka-only streams, or mark-pointer tests without a new independent clue.",
            "- The live problem is not key format. It is the missing human-readable selector/provenance rule that chooses which page-76 corridor material matters and in what order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
