#!/usr/bin/env python3
"""Refresh the active puzzle-path readiness gate.

This is a synthesis/checklist pass, not a key-search pass. It ingests the most
recent local audits and asks which active paths have all four ingredients needed
for a defensible extraction rule:

1. source layer
2. target region
3. ordering
4. extraction unit

No OCR extraction, hashing, mnemonics, WIFs, addresses, or key candidates are
generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/active_path_readiness_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_path_readiness_gate.json"
OUT_MD = OUT / "active_path_readiness_gate.md"

INPUTS = {
    "page76TargetConvergence": ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json",
    "selectorGapMap": ROOT / "analysis_outputs/source_audit/selector_gap_map.json",
    "sourceRegistrationAcceptance": ROOT / "analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.json",
    "sourceValidationGate": ROOT / "analysis_outputs/source_audit/source_validation_gate/source_validation_gate.json",
    "comparisonPdfSourceGate": ROOT / "analysis_outputs/source_audit/comparison_pdf_source_gate/comparison_pdf_source_gate.json",
    "bodyHighlighterGrammar": ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json",
    "typographySourceProvenance": ROOT / "analysis_outputs/source_audit/typography_source_provenance.json",
    "xxWireSimilarityOverfit": ROOT / "analysis_outputs/source_audit/xx_wire_similarity_overfit/xx_wire_similarity_overfit.json",
    "repairedFrameFontStates": ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def status(has_source: bool, has_target: bool, has_order: bool, has_unit: bool, blocked: bool = False) -> str:
    if blocked:
        return "closed"
    if has_source and has_target and has_order and has_unit:
        return "ready_for_low_parameter_extraction"
    if has_source and has_target and has_order:
        return "blocked_on_unit"
    if has_source and has_target:
        return "blocked_on_order_and_unit"
    if has_source:
        return "support_only"
    return "closed"


def yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> None:
    data = {name: load(path) for name, path in INPUTS.items()}

    convergence = data["page76TargetConvergence"]
    ranking = convergence.get("ranking", [])
    top_targets = []
    for item in ranking[:3]:
        top_targets.append(
            {
                "id": item.get("id") or item.get("target"),
                "label": item.get("label"),
                "score": item.get("score"),
                "independentLayers": item.get("independentLayers") or item.get("independentLayerCount"),
            }
        )

    comparison = data["comparisonPdfSourceGate"]
    typography = data["typographySourceProvenance"]
    body_grammar = data["bodyHighlighterGrammar"]
    xx = data["xxWireSimilarityOverfit"]
    frame = data["repairedFrameFontStates"]
    source_acceptance = data["sourceRegistrationAcceptance"]

    issue27_summary = next(
        (s for s in body_grammar.get("summaries", []) if s.get("source") == "issue27"),
        {},
    )
    typeka_docm = next(
        (d for d in typography.get("docms", []) if d.get("label") == "article_with_fonts"),
        {},
    )
    exact_frame = next(
        (s for s in frame.get("scenarios", []) if s.get("name") == "g5_edge_touch_dx_minus_38"),
        {},
    )

    paths = [
        {
            "name": "G5/O5 lower-corridor pair",
            "sourceLayer": "page-76 self-mirror + p78 frame/graphic + p80 dosage/symptom support",
            "targetRegion": "G5 Volcano Bonds / O5 shitcoiner at heart",
            "ordering": "partial: top-down frame and G5/O5 pair order exist, but no source says which to read first",
            "extractionUnit": "missing",
            "hasSource": True,
            "hasTarget": True,
            "hasOrder": False,
            "hasUnit": False,
            "evidence": "Strongest convergence target pair; still lacks word/letter/edge/font-state rule.",
        },
        {
            "name": "repaired p78 frame exact-edge trio",
            "sourceLayer": "p78 reflected frame, dx -38/-40 registration signature",
            "targetRegion": "should sell | Volcano Bonds | shitcoiner at heart",
            "ordering": "top-down exact-edge order exists",
            "extractionUnit": "missing",
            "hasSource": True,
            "hasTarget": True,
            "hasOrder": True,
            "hasUnit": False,
            "evidence": "Clean R-K-Y signature, initials sVs and lasts lst; instruction hits remain empty.",
        },
        {
            "name": "body orange/grey highlight grammar",
            "sourceLayer": "Issue 24 visible orange/grey body highlights",
            "targetRegion": "page 76 highlighted corridor",
            "ordering": "partial: print reading order exists, reflected-hit order exists, neither is named by clue",
            "extractionUnit": "missing",
            "hasSource": True,
            "hasTarget": True,
            "hasOrder": False,
            "hasUnit": False,
            "evidence": f"Issue 27 control weakens house-style explanation: issue27 max score {issue27_summary.get('maxGrammarScore')} with sustained pages {issue27_summary.get('sustainedGrammarPages')}.",
        },
        {
            "name": "Typeka / Typeka Mix font state",
            "sourceLayer": "Article with Fonts.docm formatting witness",
            "targetRegion": "only after page-76 geometry selects text",
            "ordering": "DOCM run order exists but no clue selects it",
            "extractionUnit": "font state exists, but no rule says to use it",
            "hasSource": True,
            "hasTarget": False,
            "hasOrder": False,
            "hasUnit": False,
            "evidence": f"Article with Fonts records Typeka states {typeka_docm.get('typekaFontChars')}; PDFs do not expose usable Typeka metadata.",
        },
        {
            "name": "comparison PDFs",
            "sourceLayer": "style-only controls",
            "targetRegion": "none for Issue 24 extraction",
            "ordering": "none",
            "extractionUnit": "none",
            "hasSource": False,
            "hasTarget": False,
            "hasOrder": False,
            "hasUnit": False,
            "blocked": True,
            "evidence": f"Promoted for extraction geometry: {comparison.get('promotedForExtractionGeometry')}.",
        },
        {
            "name": "XX / barbed-wire / FUCK spill geometry",
            "sourceLayer": "Canva note + p78/p79 graphic objects",
            "targetRegion": "orientation/source registration only",
            "ordering": "none after local tests",
            "extractionUnit": "none",
            "hasSource": True,
            "hasTarget": False,
            "hasOrder": False,
            "hasUnit": False,
            "blocked": True,
            "evidence": f"Forced-fit decision: {xx.get('decision')}",
        },
        {
            "name": "future physical/original-layout source",
            "sourceLayer": "not yet acquired",
            "targetRegion": "must validate O5/G5, zero/#0, p79 pills, and repaired p78 frame",
            "ordering": "unknown",
            "extractionUnit": "unknown",
            "hasSource": False,
            "hasTarget": True,
            "hasOrder": False,
            "hasUnit": False,
            "evidence": "Only path that can change geometry/source truth without another local overfit.",
            "externalDependency": True,
        },
    ]
    for path in paths:
        if path.get("externalDependency"):
            path["status"] = "external_dependency"
        else:
            path["status"] = status(
                path["hasSource"],
                path["hasTarget"],
                path["hasOrder"],
                path["hasUnit"],
                path.get("blocked", False),
            )

    ready = [p for p in paths if p["status"] == "ready_for_low_parameter_extraction"]
    blocked_on_unit = [p for p in paths if p["status"] == "blocked_on_unit"]
    open_support = [p for p in paths if p["status"] in {"blocked_on_order_and_unit", "support_only"}]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active-path readiness gate; no OCR/key derivation",
        "inputs": {name: str(path.relative_to(ROOT)) for name, path in INPUTS.items()},
        "topConvergenceTargets": top_targets,
        "paths": paths,
        "readyCount": len(ready),
        "blockedOnUnitCount": len(blocked_on_unit),
        "openSupportCount": len(open_support),
        "sourceAcceptanceDecision": source_acceptance.get("decision"),
        "decision": "No current path has all four requirements for extraction. The closest path is the repaired p78 exact-edge trio, but it is still blocked on the extraction unit.",
        "nextMove": "Do not generate key candidates. Either acquire better source/physical/original-layout evidence, or test only a new explicit human rule that names source layer, target, order, and unit before running.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Path Readiness Gate",
        "",
        "Scope: refresh the active puzzle-path checklist after recent source/style/font/graphic closures. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Ready paths: `{result['readyCount']}`",
        f"- Blocked on extraction unit: `{result['blockedOnUnitCount']}`",
        "",
        "## Top Convergence Targets",
        "",
    ]
    for item in top_targets:
        lines.append(
            f"- `{item['id']}` {item['label']}: score `{item['score']}`, independent layers `{item['independentLayers']}`"
        )
    lines.extend(
        [
            "",
            "## Path Readiness",
            "",
            "| path | source | target | order | unit | status | evidence |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for path in paths:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{path['name']}`",
                    yes(path["hasSource"]),
                    yes(path["hasTarget"]),
                    yes(path["hasOrder"]),
                    yes(path["hasUnit"]),
                    f"`{path['status']}`",
                    str(path["evidence"]).replace("|", "/"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            "- The repaired exact-edge trio is the nearest thing to an actionable local path because it has source layer, target, and order, but it still lacks a source-backed unit.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("readyCount:", result["readyCount"])
    print("blockedOnUnitCount:", result["blockedOnUnitCount"])


if __name__ == "__main__":
    main()
