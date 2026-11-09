#!/usr/bin/env python3
"""Score the current canonical scan against the refreshed C1-C9 benchmark.

This is a dry run of the source-registration acceptance test. It does not
extract text, derive keys, hash candidates, check mnemonics, WIFs, or addresses.
The goal is to define the current baseline so a future source/physical scan can
be judged by whether it improves the blocked constraints.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_acceptance_benchmark"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_acceptance_benchmark.json"
OUT_MD = OUT / "current_scan_acceptance_benchmark.md"

ACCEPTANCE = ROOT / "analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.json"
CACHE = ROOT / "analysis_outputs/source_audit/current_scan_cache_consistency/current_scan_cache_consistency.json"
CROP_FIDELITY = ROOT / "analysis_outputs/source_audit/priority_crop_pack_source_fidelity/priority_crop_pack_source_fidelity.json"
PHYSICAL = ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation.json"
CAPSULE = ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.json"
FIVE = ROOT / "analysis_outputs/source_audit/five_index_convergence/five_index_convergence.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    acceptance = load(ACCEPTANCE)
    cache = load(CACHE)
    crops = load(CROP_FIDELITY)
    physical = load(PHYSICAL)
    capsule = load(CAPSULE)
    five = load(FIVE)

    physical_overlap_total = sum(model["overlapCount"] for model in physical["physicalModels"])
    independent_sequence_hits = len(capsule.get("comparisonStrongFivePointSequenceMatches", []))
    witness_sequence_hits = len(capsule.get("lowResWitnessStrongFivePointSequenceMatches", []))

    rows = [
        {
            "id": "C1",
            "status": "PASS",
            "currentScanEvidence": "Trusted page-76 O5/G5 crop geometry is available and source-faithful.",
            "blocksExtraction": False,
            "futureImprovementNeeded": "Only if a future source gives cleaner manual boxes.",
        },
        {
            "id": "C2",
            "status": "PARTIAL",
            "currentScanEvidence": "p78 frame signature exists, including G5 near-edge and O5 bottom/left clip, but remains a registration signature.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "Independent physical/source layer should explain the same p78->p76 contact naturally.",
        },
        {
            "id": "C3",
            "status": "FAIL",
            "currentScanEvidence": "No source-backed word/letter/line/edge/font unit or ordering rule has been found.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "A clue/source must name the extraction unit before any key checks resume.",
        },
        {
            "id": "C4",
            "status": "FAIL",
            "currentScanEvidence": f"Current physical leaf/spread models produce total direct trusted O5/G5 overlaps={physical_overlap_total}.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "A true physical scan/photo should improve front/back, spread, fold, or bleed-through behavior.",
        },
        {
            "id": "C5",
            "status": "PARTIAL",
            "currentScanEvidence": f"Issue 24 and bitcoin4 witness preserve the five-capsule sequence; independent comparison sequence hits={independent_sequence_hits}.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "Need a source rule that maps the capsule chain to a text/selector unit.",
        },
        {
            "id": "C6",
            "status": "PARTIAL",
            "currentScanEvidence": f"Five repeats across p73/p79/p80/p76; p73/p79 step signature is {five['p73StepSignature']['stepSigns']} and p79-p73 offsets are {five['p79MinusP73IndexOffsets']}; instruction hits={five['instructionTermHits'] or 'none'}.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "Need source/clue wording that explains how five selects a word, letter, edge, or font state.",
        },
        {
            "id": "C7",
            "status": "PARTIAL",
            "currentScanEvidence": "Announcement/media evidence points to page-76 Bukele/volcano/IMF corridor, but does not add unit/order.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "Need exact media-order or source instruction beyond target confirmation.",
        },
        {
            "id": "C8",
            "status": "FAIL",
            "currentScanEvidence": "Canva remains a low-resolution investigator note board, not geometry truth.",
            "blocksExtraction": True,
            "futureImprovementNeeded": "Need original embedded Canva assets, higher-resolution export, browser capture, or physical source image.",
        },
        {
            "id": "C9",
            "status": "PASS",
            "currentScanEvidence": f"Desktop/project PDF are byte-identical={cache['projectDesktopByteIdentical']}; source-to-3D transform is {cache['summary']['sourceTo3dTransform']}; priority crop RMS range={crops['summary']['minRawRms']} to {crops['summary']['maxRawRms']}.",
            "blocksExtraction": False,
            "futureImprovementNeeded": "Always compare future source material in matching orientation.",
        },
    ]

    status_counts = {status: sum(1 for row in rows if row["status"] == status) for status in ["PASS", "PARTIAL", "FAIL"]}
    blocking = [row["id"] for row in rows if row["blocksExtraction"]]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current canonical scan scored against refreshed C1-C9 source-registration benchmark; no key derivation",
        "acceptanceBenchmark": str(ACCEPTANCE.relative_to(ROOT)),
        "statusCounts": status_counts,
        "blockingConstraints": blocking,
        "witnessSequenceHits": witness_sequence_hits,
        "independentComparisonSequenceHits": independent_sequence_hits,
        "rows": rows,
        "decision": "The current scan is a valid baseline and target/provenance witness, but extraction remains blocked by C3/C4/C8 and partial C2/C5/C6/C7.",
        "nextMove": "Future sources must improve at least one blocked constraint, especially C3 extraction unit or C4/C8 source quality, before any key-candidate work resumes.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Acceptance Benchmark",
        "",
        "Scope: score the current canonical scan against the refreshed C1-C9 source-registration benchmark. No key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Status counts: `PASS={status_counts['PASS']}`, `PARTIAL={status_counts['PARTIAL']}`, `FAIL={status_counts['FAIL']}`",
        f"- Blocking constraints: `{', '.join(blocking)}`",
        f"- Independent comparison five-sequence hits: `{independent_sequence_hits}`",
        f"- Lower-res Issue 24 witness five-sequence hits: `{witness_sequence_hits}`",
        "",
        "## C1-C9 Dry Run",
        "",
        "| id | status | current scan evidence | blocks extraction | future improvement needed |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | `{row['status']}` | {row['currentScanEvidence']} | `{row['blocksExtraction']}` | {row['futureImprovementNeeded']} |"
        )
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("statusCounts:", status_counts)
    print("blockingConstraints:", ",".join(blocking))


if __name__ == "__main__":
    main()
