#!/usr/bin/env python3
"""Rank page-76 target units by independent visual/source support.

This is a synthesis pass, not a key-generation pass. It records which page-76
phrases are supported by multiple independent puzzle layers, so future work can
focus on the most evidenced target instead of reopening every highlight equally.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_target_convergence"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "page76_target_convergence.json"
OUT_MD = OUT_DIR / "page76_target_convergence.md"

FILES = {
    "b5o5": ROOT / "analysis_outputs/source_audit/page76_b5_o5_pair/page76_b5_o5_pair.json",
    "p78_graphic": ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json",
    "p78_words": ROOT / "analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.json",
    "p78_chars": ROOT / "analysis_outputs/source_audit/p78_graphic_char_intersections/p78_graphic_char_intersections.json",
    "dose": ROOT / "analysis_outputs/source_audit/overdose_dose_number_selector/overdose_dose_number_selector.json",
    "symptoms": ROOT / "analysis_outputs/source_audit/p80_symptom_to_p76_units/p80_symptom_to_p76_units.json",
    "exact": ROOT / "analysis_outputs/3d_article_map/exact_highres_reflection_geometry.json",
    "graph": ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json",
}

TARGETS = {
    "O1": "Get some toxicity / Open your heart to Bitcoin",
    "O3": "by the rancid catnip of fiat money",
    "O4": "buying the dip",
    "G1": "Gotta be this way / post-1971 fiat money",
    "G3": "It's a stun gun to the genitals",
    "G4": "$1 billion",
    "G5": "Volcano Bonds",
    "O5": "shitcoiner at heart",
    "CORRIDOR": "lower El Salvador / IMF / Bukele / Mike / trust corridor",
}


def load(key: str) -> dict:
    return json.loads(FILES[key].read_text())


def add(evidence: dict[str, list[dict]], target: str, layer: str, support: str, weight: int = 1) -> None:
    evidence[target].append({"layer": layer, "support": support, "weight": weight})


def main() -> None:
    evidence: dict[str, list[dict]] = defaultdict(list)

    # Existing exact reflected-highlight graph: strongest broad page-76 geometry.
    exact = load("exact")
    for row in exact.get("page76Stable", []):
        text = row["text"].lower()
        sources = ",".join(str(s) for s in row.get("sources", []))
        hits = len(row.get("strongHits", []))
        support = f"{hits} strong reflected hit(s) from source page(s) {sources}"
        if "get some toxicity" in text:
            add(evidence, "O1", "exact reflected-highlight graph", support, 2)
        elif "rancid catnip" in text:
            add(evidence, "O3", "exact reflected-highlight graph", support, 2)
        elif "buying the dip" in text:
            add(evidence, "O4", "exact reflected-highlight graph", support, 2)
        elif "gotta be this way" in text:
            add(evidence, "G1", "exact reflected-highlight graph", support, 1)
        elif "stun gun" in text:
            add(evidence, "G3", "exact reflected-highlight graph", support, 1)
        elif "$1 billion" in text:
            add(evidence, "G4", "exact reflected-highlight graph", support, 2)

    graph = load("graph")
    summary = graph.get("summary", {})
    add(
        evidence,
        "CORRIDOR",
        "reflected-highlight graph summary",
        f"{summary.get('page76MediumPlusEdges')} medium/strong hits land on p76; pair counts {summary.get('pairCounts')}",
        2,
    )

    # B5/O5 self-mirror.
    b5o5 = load("b5o5")
    for row in b5o5.get("rows", []):
        add(
            evidence,
            "G5",
            "page-76 self-mirror",
            f"{row['sourceLabel']} reflects toward {row['targetLabel']} with overlapVsSource {row['overlapVsSource']}",
            3,
        )
        add(
            evidence,
            "O5",
            "page-76 self-mirror",
            f"{row['sourceLabel']} reflects toward {row['targetLabel']} with overlapVsTarget {row['overlapVsTarget']}",
            3,
        )

    # P78 graphic broad reflection and micro-intersections.
    p78_graphic = load("p78_graphic")
    for hit in p78_graphic.get("meaningfulIntersections", []):
        label = hit["label"].lower()
        target = "O5" if "shitcoiner" in label else "G5" if "volcano" in label else None
        if target:
            add(
                evidence,
                target,
                "p78 lower graphic mirror",
                f"bboxOverlapVsTarget {hit['bboxOverlapVsTarget']}, reflected-mask pixels {hit['reflectedMaskPixelsInsideTarget']}",
                2,
            )
    p78_words = load("p78_words")
    add(
        evidence,
        "CORRIDOR",
        "p78 graphic word intersections",
        f"bbox stream: {p78_words.get('bboxStream', '')}",
        1,
    )
    if "siukbeod" in p78_words.get("bboxStream", ""):
        add(evidence, "O5", "p78 graphic word intersections", "includes lower OCR blob for `shitcoiner at heart`", 1)
    if "pay off the IMF" in p78_words.get("bboxStream", ""):
        add(evidence, "G5", "p78 graphic word intersections", "intersects the `Volcano Bonds` / IMF line band", 1)

    p78_chars = load("p78_chars")
    add(
        evidence,
        "CORRIDOR",
        "p78 graphic character intersections",
        f"dark centers `{p78_chars['streams']['darkCenter']}`, hole centers `{p78_chars['streams']['holeCenter']}`",
        1,
    )

    # Dose/count layer.
    dose = load("dose")
    for selection in dose.get("selections", []):
        selected = selection.get("selected") or {}
        target_text = (selected.get("text") or "").lower()
        source = f"{selection.get('surface')} #{selection.get('number')}"
        if "shitcoiner at heart" in target_text:
            add(evidence, "O5", "OVERDOSE number selector", f"{source}: {selected.get('text')}", 2)
        elif "volcano bonds" in target_text:
            add(evidence, "G5", "OVERDOSE number selector", f"{source}: {selected.get('text')}", 2)
        elif "$1 billion" in target_text:
            add(evidence, "G4", "OVERDOSE number selector", f"{source}: {selected.get('text')}", 1)
        elif "bukele" in target_text or "volcano" in target_text:
            add(evidence, "CORRIDOR", "OVERDOSE number selector", f"{source}: {selected.get('text')}", 1)

    # P80 symptom layer.
    symptoms = load("symptoms")
    symptom_hits = symptoms.get("unorderedLexicalHits", {}).get("all", [])
    for hit in symptom_hits:
        text = (hit.get("unitText") or "").lower()
        symptom = hit.get("symptom")
        if "shitcoiner at heart" in text:
            add(evidence, "O5", "p80 symptom list", f"{symptom} hits {hit.get('unitText')}", 2)
        if "heart" in text and hit.get("unitId") == "p76_orange_1":
            add(evidence, "O1", "p80 symptom list", f"{symptom} weak lexical echo on {hit.get('unitText')}", 1)

    ranking = []
    for target, rows in evidence.items():
        layers = sorted({row["layer"] for row in rows})
        weight = sum(row["weight"] for row in rows)
        ranking.append(
            {
                "target": target,
                "label": TARGETS.get(target, target),
                "score": weight,
                "independentLayerCount": len(layers),
                "layers": layers,
                "evidence": rows,
            }
        )
    ranking.sort(key=lambda item: (-item["score"], -item["independentLayerCount"], item["target"]))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Rank page-76 target units by independent non-key evidence; no key derivation.",
        "ranking": ranking,
        "assessment": [
            "The lower p76 pair O5/G5 now has the densest independent support.",
            "O4/G4 remain strong semantic/geometry corridor anchors but have fewer independent selector-like layers.",
            "The remaining gap is still extraction unit/order, not target location.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Page 76 Target Convergence Audit",
        "",
        "Scope: rank page-76 target units by independent visual/source support. This is not a key-generation pass.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Ranking",
        "",
    ]
    for item in ranking:
        lines.append(
            f"- **{item['target']}** `{item['label']}`: score `{item['score']}`, "
            f"independent layers `{item['independentLayerCount']}`"
        )
        for ev in item["evidence"]:
            lines.append(f"  - {ev['layer']}: {ev['support']}")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The lower page-76 target pair is now the strongest convergence point:",
            "  - `G5` = `Volcano Bonds`",
            "  - `O5` = `shitcoiner at heart`",
            "- This pair is supported by page-76 self-mirror, p78 graphic reflection, p78 word/character banding, p80 symptom/dosage layers, and the broader El Salvador/IMF corridor.",
            "- The result is still not a solution. It says where to focus. The missing step is the rule that says what to extract from this pair and in what order.",
            "- Next best move: seek a provenance/instruction clue for the extraction unit, or test only very low-parameter rules that explicitly operate on the G5/O5 pair.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
