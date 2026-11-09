#!/usr/bin/env python3
"""Cross-evidence audit for page-76 line-offset landings.

The line-offset rule has highlighted hits and #2/#4 misses. This checks
whether the miss-lines are actually unsupported, or whether other visual/source
layers also point at them.

No key candidates are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OFFSET_JSON = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json"
P78_WORD_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.json"
REFLECTED_GRAPH_JSON = ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json"
CONVERGENCE_JSON = ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json"
OUT = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "line_offset_landing_evidence.json"
OUT_MD = OUT / "line_offset_landing_evidence.md"


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def interesting_tokens(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "a",
        "to",
        "of",
        "in",
        "it",
        "is",
        "he",
        "she",
        "with",
        "for",
        "that",
        "this",
        "but",
        "so",
        "as",
        "be",
        "by",
        "on",
        "or",
        "an",
    }
    return {w for w in words(text) if len(w) >= 4 and w not in stop}


def overlap_terms(a: str, b: str) -> list[str]:
    return sorted(interesting_tokens(a) & interesting_tokens(b))


def p78_graphic_terms() -> dict[str, set[str]]:
    data = json.loads(P78_WORD_JSON.read_text())
    return {
        "p78_bbox_words": {row["token"].lower() for row in data.get("bboxWords", []) if len(row.get("token", "")) >= 4},
        "p78_dark_words": {row["token"].lower() for row in data.get("darkHits", []) if len(row.get("token", "")) >= 4},
        "p78_hole_words": {row["token"].lower() for row in data.get("holeHits", []) if len(row.get("token", "")) >= 4},
    }


def reflected_graph_hits(line_text: str) -> list[dict]:
    data = json.loads(REFLECTED_GRAPH_JSON.read_text())
    out = []
    for edge in data["edges"]:
        if edge.get("targetPage") != 76:
            continue
        terms = overlap_terms(line_text, edge.get("targetText", ""))
        if not terms:
            continue
        out.append(
            {
                "targetId": edge["targetId"],
                "sourcePage": edge["sourcePage"],
                "strength": edge["strength"],
                "terms": terms,
                "targetText": edge["targetText"],
            }
        )
    return out


def convergence_targets() -> dict[str, dict]:
    data = json.loads(CONVERGENCE_JSON.read_text())
    return {row["target"]: row for row in data["ranking"]}


def score_landing(row: dict, graphic_terms: dict[str, set[str]], convergence: dict[str, dict]) -> dict:
    text = row.get("targetText", "")
    tokens = interesting_tokens(text)
    layers = []
    evidence = []
    score = 0

    if row.get("targetUnits"):
        layers.append("highlight target")
        evidence.append(f"line lands on highlighted unit(s) {','.join(row['targetUnits'])}")
        score += 2
        for unit in row["targetUnits"]:
            normalized = {"O5": "O5", "B5": "G5"}.get(unit, unit)
            if normalized in convergence:
                target = convergence[normalized]
                layers.append("target convergence")
                evidence.append(f"{normalized} convergence score {target['score']}")
                score += min(3, target["independentLayerCount"])

    for layer, terms in graphic_terms.items():
        hit_terms = sorted(tokens & terms)
        if hit_terms:
            layers.append(layer)
            evidence.append(f"{layer} terms: {', '.join(hit_terms)}")
            score += 1 if layer == "p78_bbox_words" else 2

    graph = reflected_graph_hits(text)
    medium_plus = [g for g in graph if g["strength"] in {"medium", "strong"}]
    if medium_plus:
        layers.append("reflected highlight graph")
        sample = "; ".join(f"{g['targetId']} {g['strength']} terms={','.join(g['terms'])}" for g in medium_plus[:3])
        evidence.append(sample)
        score += min(3, len(medium_plus))

    return {
        "sourceId": row["sourceId"],
        "sourceIndex": row["sourceIndex"],
        "targetLine": row["targetLine"],
        "targetUnits": row.get("targetUnits", []),
        "targetText": text,
        "score": score,
        "layers": sorted(set(layers)),
        "evidence": evidence,
    }


def main() -> None:
    offset = json.loads(OFFSET_JSON.read_text())
    graphic_terms = p78_graphic_terms()
    convergence = convergence_targets()
    down_rows = [row for row in offset["landingRows"] if row.get("direction") == "down"]
    scored = [score_landing(row, graphic_terms, convergence) for row in down_rows]

    hits = [row for row in scored if row["targetUnits"]]
    misses = [row for row in scored if not row["targetUnits"]]
    supported_misses = [row for row in misses if row["score"] > 0]
    unsupported_misses = [row for row in misses if row["score"] == 0]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Cross-evidence audit for page-76 line-offset landing lines; no key derivation.",
        "graphicTermLayers": {key: sorted(value) for key, value in graphic_terms.items()},
        "scoredLandings": scored,
        "highlightHits": hits,
        "supportedMisses": supported_misses,
        "unsupportedMisses": unsupported_misses,
        "assessment": [
            "The #4 miss-lines are supported by the p78 graphic reflection band: O4+4 lands on `billions worth of future bitcoin earnings`, and B4+4 lands on the Novogratz/could-sell line.",
            "The #2 miss-lines are weak: O2+2 (`George Clinton...Martin Luther`) and B2+2 (`have dulled shitcoiners...`) do not receive the same cross-layer support in the currently logged evidence.",
            "This suggests the line-offset operation may select landing lines, not only highlighted boxes, but it still lacks a rule for which words or letters to extract.",
            "Do not promote the supported #4 misses into key material without a source rule specifying the unit.",
        ],
        "nextMove": "Inspect whether source/provenance layers around p78/p79/p80 explain why #4 lands in the p78 graphic band while #2 remains weak.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Line-Offset Landing Evidence Audit",
        "",
        "Scope: score each page-76 down-offset landing line against other logged visual/source evidence. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Landing Scores",
        "",
        "| source | target line | highlight target | score | layers | line text |",
        "|---|---:|---|---:|---|---|",
    ]
    for row in scored:
        units = ",".join(row["targetUnits"]) or "-"
        layers = ", ".join(row["layers"]) or "-"
        text = row["targetText"].replace("|", "\\|")
        md.append(f"| {row['sourceId']} +{row['sourceIndex']} | {row['targetLine']} | {units} | {row['score']} | {layers} | {text} |")

    md.extend(
        [
            "",
            "## Supported Misses",
            "",
        ]
    )
    if supported_misses:
        for row in supported_misses:
            md.append(f"- `{row['sourceId']} +{row['sourceIndex']}` -> line `{row['targetLine']}`: {row['targetText']}")
            for item in row["evidence"]:
                md.append(f"  - {item}")
    else:
        md.append("- None.")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- #4 is not a dead miss: both #4 landings sit in the p78 graphic reflection band.",
            "- #2 remains weak under current logged evidence.",
            "- The line-offset rule may be selecting landing lines rather than highlighted boxes, but no extraction unit is defined.",
            "- Next best move: inspect p78/p79/p80 source/provenance layers for why #4 connects to the p78 graphic band and whether #2 has a missing source layer.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
