#!/usr/bin/env python3
"""Build a source-registration acceptance benchmark for the puzzle.

This consolidates the active geometry constraints into a pass/fail checklist.
It is intentionally not a key generator: the goal is to prevent more weak local
selector branches and define what a future source image or physical scan must
explain before extraction resumes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_registration_acceptance_test"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_registration_acceptance_test.json"
OUT_MD = OUT / "source_registration_acceptance_test.md"

SENS_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity.json"
PHYSICAL_JSON = ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation.json"
GAP_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_gap_repair_selector/p78_frame_gap_repair_selector.json"
CAPSULE_JSON = ROOT / "analysis_outputs/source_audit/opener_capsule_endpoint_selector/opener_capsule_endpoint_selector.json"
MEDIA_JSON = ROOT / "analysis_outputs/external_clues/announcement_media_order_selector/announcement_media_order_selector.json"
CANVA_JSON = ROOT / "analysis_outputs/external_clues/canva_thumbnail_export_audit.json"
CACHE_JSON = ROOT / "analysis_outputs/source_audit/current_scan_cache_consistency/current_scan_cache_consistency.json"
CROP_FIDELITY_JSON = ROOT / "analysis_outputs/source_audit/priority_crop_pack_source_fidelity/priority_crop_pack_source_fidelity.json"
FIVE_JSON = ROOT / "analysis_outputs/source_audit/five_index_convergence/five_index_convergence.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def status(ok: bool, partial: bool = False) -> str:
    if ok:
        return "PASS"
    if partial:
        return "PARTIAL"
    return "FAIL"


def main() -> None:
    sens = load(SENS_JSON)
    physical = load(PHYSICAL_JSON)
    gap = load(GAP_JSON)
    capsules = load(CAPSULE_JSON)
    media = load(MEDIA_JSON)
    canva = load(CANVA_JSON)
    cache = load(CACHE_JSON)
    crop_fidelity = load(CROP_FIDELITY_JSON)
    five = load(FIVE_JSON)

    current = sens["grid"]["current"]
    nearest = sens["grid"]["closestSimultaneousOverlaps"][0]
    physical_overlap_total = sum(model["overlapCount"] for model in physical["physicalModels"])
    gap_hits = []
    for analysis in gap["analyses"]:
        hits = []
        for value in analysis["streamInstructionHits"].values():
            hits.extend(value)
        gap_hits.extend(hits)
    capsule_thresholds = capsules["thresholds"]
    media_missing = media["missingExpectedLowerCorridorUnits"]
    canva_size = canva.get("thumbnailSize") or canva.get("sourceThumbnailSize") or [668, 376]
    five_hits = five.get("instructionTermHits", {})

    constraints = [
        {
            "id": "C1",
            "name": "trusted source boxes",
            "requirement": "Use trusted high-res O5 and corrected trusted G5, not stale projected p76_grey_5 geometry.",
            "currentStatus": "PASS",
            "evidence": "Trusted O5/G5 are now fixed: O5 [1040,2932,1661,2982], G5 [795,2544,1196,2592].",
            "acceptance": "Any future source transform must report target boxes against these trusted units or a clearly better manual source.",
        },
        {
            "id": "C2",
            "name": "p78 frame signature",
            "requirement": "Explain current O5 bottom/left clip, trusted G5 38px near-edge relation, and the dx=-40 repair without arbitrary local fitting.",
            "currentStatus": "PARTIAL",
            "evidence": f"Current O5 overlap={current['O5']['overlapVsTarget']}; G5 gap={current['G5']['horizontalGapPx']}px; nearest simultaneous repair dx={nearest['dx']}, dy={nearest['dy']}.",
            "acceptance": "A valid source registration should naturally make this signature coherent while preserving the same corridor.",
        },
        {
            "id": "C3",
            "name": "extraction unit",
            "requirement": "Name a word, letter, line, edge, pixel, font-state, or ordering unit before any key derivation.",
            "currentStatus": status(False),
            "evidence": f"Gap-repaired p78 streams produce instruction hits: {gap_hits or 'none'}.",
            "acceptance": "Must produce a human-readable instruction or checksum-valid compact key-like unit from a rule that follows from source/clue evidence.",
        },
        {
            "id": "C4",
            "name": "physical leaf/spread support",
            "requirement": "True physical page relationships should improve, not degrade, O5/G5 targeting.",
            "currentStatus": status(physical_overlap_total > 0),
            "evidence": f"Current best-scan physical models have total trusted O5/G5 direct overlaps={physical_overlap_total}.",
            "acceptance": "A physical scan/photo should show real front/back, spread, bleed-through, or fold behavior that selects the corridor.",
        },
        {
            "id": "C5",
            "name": "opener capsule provenance",
            "requirement": "Preserve the real p73->p79 five-capsule artwork reuse while avoiding loose forced M3/M4 assignment.",
            "currentStatus": "PARTIAL",
            "evidence": f"Current endpoint sequence={capsules['streams']['forcedMarkSequence']}; tight <=75px assigns {capsule_thresholds['75']['assignedCount']}/5, <=150px assigns {capsule_thresholds['150']['assignedCount']}/5.",
            "acceptance": "A new transform should place all five ordered capsules tightly on text/selector units, or provide an explicit clue for M3/M4 binary/index use.",
        },
        {
            "id": "C6",
            "name": "five-index locator",
            "requirement": "Preserve the repeated five system without treating five, RRLL, or 1100 as key material by itself.",
            "currentStatus": "PARTIAL",
            "evidence": f"Five repeats across p73/p79/p80/p76; p73/p79 step signature={five['p73StepSignature']['stepSigns']} / {five['p79StepSignature']['stepSigns']}; p79-p73 offsets={five['p79MinusP73IndexOffsets']}; instruction hits={five_hits or 'none'}.",
            "acceptance": "A future source/clue must explain how five selects a unit such as word/letter/edge/font before extraction resumes.",
        },
        {
            "id": "C7",
            "name": "announcement media coverage",
            "requirement": "Use public media sequence as target confirmation, not overclaim it as exact order.",
            "currentStatus": "PARTIAL",
            "evidence": f"Media order unique page-76 initials={media['streams']['page76UniqueInitials']}; missing units={', '.join(media_missing)}.",
            "acceptance": "Future use of media must add a new exact unit/order not already covered by page-76 Bukele/volcano targeting.",
        },
        {
            "id": "C8",
            "name": "Canva/source image quality",
            "requirement": "Do not use the 668x376 Canva thumbnail as geometry truth.",
            "currentStatus": status(False),
            "evidence": f"Current Canva witness is thumbnail-scale ({canva_size}) and documented as an investigator note board.",
            "acceptance": "Need original embedded assets, higher-resolution export, browser screenshot, or physical source image.",
        },
        {
            "id": "C9",
            "name": "orientation/source cache bridge",
            "requirement": "Compare future source images in the correct orientation before judging geometry.",
            "currentStatus": "PASS",
            "evidence": f"Current 3D/readable layer matches source/PDF after `{cache['summary']['sourceTo3dTransform']}`; priority crop RMS range={crop_fidelity['summary']['minRawRms']} to {crop_fidelity['summary']['maxRawRms']}.",
            "acceptance": "Use readable/upright geometry or rotate native source/PDF images 180 degrees before applying page-76 crop coordinates.",
        },
    ]

    witnesses = [
        {
            "name": "current best high-res magazine.pdf",
            "status": "PARTIAL",
            "passes": ["C1", "C2-partial", "C5-provenance", "C6-locator", "C7-targeting", "C9"],
            "fails": ["C3", "C4", "C8"],
            "verdict": "Good for target discovery and source provenance; insufficient for precise extraction.",
        },
        {
            "name": "current p78 dx=-40 local repair",
            "status": "FAIL_AS_SELECTOR",
            "passes": ["C2-partial"],
            "fails": ["C3"],
            "verdict": "Useful only as a future registration signature; it does not change the instruction-free phrase stream.",
        },
        {
            "name": "Canva 668x376 note board",
            "status": "FAIL_GEOMETRY_TRUTH",
            "passes": ["C7-targeting"],
            "fails": ["C8"],
            "verdict": "Orientation/provenance clue only; too small and secondary for measurement.",
        },
        {
            "name": "announcement media sequence",
            "status": "PARTIAL",
            "passes": ["C7-targeting"],
            "fails": ["C3"],
            "verdict": "Confirms page 76/Bukele/volcano area, but not exact order or unit.",
        },
        {
            "name": "future physical/source scan",
            "status": "REQUIRED_NEXT",
            "passes": [],
            "fails": [],
            "verdict": "Highest-value missing evidence: must be tested against C1-C9 before new extraction.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-registration acceptance benchmark; no key derivation",
        "constraints": constraints,
        "witnesses": witnesses,
        "decision": "Do not promote new local geometry streams unless they pass C2/C3 and explain C6; current local sources fail the extraction-unit requirement.",
        "nextMove": "Acquire or inspect a better source image/physical scan, then score it against this benchmark before extracting words/letters.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Registration Acceptance Test",
        "",
        "Scope: consolidate active geometry/source constraints into a pass/fail benchmark. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Constraints",
        "",
        "| id | name | status | requirement | current evidence | acceptance test |",
        "|---|---|---|---|---|---|",
    ]
    for c in constraints:
        lines.append(
            f"| {c['id']} | {c['name']} | `{c['currentStatus']}` | {c['requirement']} | {c['evidence']} | {c['acceptance']} |"
        )

    lines.extend(["", "## Witness Verdicts", "", "| witness | status | verdict |", "|---|---|---|"])
    for w in witnesses:
        lines.append(f"| {w['name']} | `{w['status']}` | {w['verdict']} |")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("decision:", result["decision"])


if __name__ == "__main__":
    main()
