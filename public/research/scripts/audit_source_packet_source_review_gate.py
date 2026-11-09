#!/usr/bin/env python3
"""Dry-run the current source packet against the future source-review gates.

This is a bounded gate-order pass. It consolidates the latest geometry,
orientation, color, OVERDOSE, folded-frame, and R3/reopen reports into one
review sequence for future source/original-layout evidence. It does not
extract text or generate key candidates.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_source_review_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_source_review_gate.json"
OUT_MD = OUT / "source_packet_source_review_gate.md"
OUT_SHEET = OUT / "source_packet_source_review_gate_sheet.jpg"

INPUTS = {
    "source_reopen_requirements": ROOT
    / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "future_source_validation_packet": ROOT
    / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "source_acquisition_packet_integrity": ROOT
    / "analysis_outputs/source_audit/source_acquisition_packet_integrity/"
    "source_acquisition_packet_integrity.json",
    "future_source_rubric_current_stack_dry_run": ROOT
    / "analysis_outputs/source_audit/future_source_rubric_current_stack_dry_run/"
    "future_source_rubric_current_stack_dry_run.json",
    "source_packet_handoff_integrity_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.json",
    "source_packet_false_positive_guardrail": ROOT
    / "analysis_outputs/source_audit/source_packet_false_positive_guardrail/"
    "source_packet_false_positive_guardrail.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
    "source_packet_orientation_disambiguator": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_disambiguator/"
    "source_packet_orientation_disambiguator.json",
    "source_packet_orientation_control_quartets": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json",
    "source_packet_r3_bridge_audit": ROOT
    / "analysis_outputs/source_audit/source_packet_r3_bridge_audit/"
    "source_packet_r3_bridge_audit.json",
    "source_packet_geometric_fingerprint": ROOT
    / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/"
    "source_packet_geometric_fingerprint.json",
    "source_packet_frame_normalized_geometry": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/"
    "source_packet_frame_normalized_geometry.json",
    "source_packet_color_profile_manifest": ROOT
    / "analysis_outputs/source_audit/source_packet_color_profile_manifest/"
    "source_packet_color_profile_manifest.json",
    "source_packet_repaired_p78_frame_residual": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/"
    "source_packet_repaired_p78_frame_residual.json",
    "source_packet_repaired_frame_expansion_leakage": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/"
    "source_packet_repaired_frame_expansion_leakage.json",
    "c9_grey_black_over_slot_control": ROOT
    / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/"
    "c9_grey_black_over_slot_control.json",
    "c9_over_slot_tolerance_gate": ROOT
    / "analysis_outputs/source_audit/c9_over_slot_tolerance_gate/"
    "c9_over_slot_tolerance_gate.json",
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "c9_active_format_witness_reconciliation": ROOT
    / "analysis_outputs/source_audit/c9_active_format_witness_reconciliation/"
    "c9_active_format_witness_reconciliation.json",
}

GATE_ORDER = ["R1", "R2", "R3", "R4", "R5"]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def gate_pass(gates: dict[str, str], gate: str) -> bool:
    return gates.get(gate) == "PASS"


def row(
    path: str,
    role: str,
    gates: dict[str, str],
    evidence: str,
    blocker: str,
    next_step: str,
    source_reports: list[str],
) -> dict:
    strict_passes = [gate for gate in GATE_ORDER if gate_pass(gates, gate)]
    strict_failures = [gate for gate in GATE_ORDER if gates.get(gate) != "PASS"]
    return {
        "path": path,
        "role": role,
        "gates": gates,
        "strictPasses": strict_passes,
        "failedStrictGates": strict_failures,
        "r3Pass": gates.get("R3") == "PASS",
        "extractionReady": all(gate_pass(gates, gate) for gate in GATE_ORDER),
        "evidence": evidence,
        "blocker": blocker,
        "next": next_step,
        "sourceReports": source_reports,
    }


def draw_sheet(summary: dict, rows: list[dict], protocol: list[dict]) -> None:
    width, height = 1820, 1040
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 96), fill=(25, 30, 38))
    draw.text((24, 18), "Source Packet Source-Review Gate", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"paths {summary['pathCount']} | ready {summary['extractionReadyCount']} | "
            f"R3 fails {summary['r3FailCount']} | fingerprint {summary['sourceReviewGateFingerprint']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Current paths against R1-R5", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["path", "R1", "R2", "R3", "R4", "R5", "blocker"]
    xs = [24, 410, 480, 550, 620, 690, 780]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, item in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (236, 240, 246)
        draw.rectangle((18, y - 4, width - 18, y + 58), fill=fill)
        draw.text((xs[0], y), item["path"][:48], fill=(30, 30, 30), font=tiny)
        for gate_idx, gate in enumerate(GATE_ORDER, start=1):
            value = item["gates"].get(gate, "FAIL")
            color = (25, 110, 55) if value == "PASS" else (120, 80, 30) if value == "PARTIAL" else (145, 35, 25)
            draw.text((xs[gate_idx], y), value, fill=color, font=tiny)
        draw.text((xs[6], y), item["blocker"][:118], fill=(70, 70, 70), font=tiny)
        draw.text((xs[6], y + 18), item["evidence"][:118], fill=(70, 70, 70), font=tiny)
        y += 66

    y += 18
    draw.text((24, y), "Future-source review protocol", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["step", "gate", "required observation", "current baseline"]
    xs = [24, 90, 190, 1060]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for item in protocol:
        draw.rectangle((18, y - 4, width - 18, y + 54), fill=(248, 249, 252))
        draw.text((xs[0], y), str(item["step"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), item["gate"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), item["requiredObservation"][:116], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), item["currentBaseline"][:96], fill=(75, 75, 75), font=tiny)
        y += 62

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    data = {name: load_json(path) for name, path in INPUTS.items()}
    reopen_gates = data["source_reopen_requirements"].get("reopenGates", [])
    min_conditions = data["future_source_validation_packet"].get("minimumReopenConditions", [])
    handoff_summary = data["source_packet_handoff_integrity_matrix"].get("summary", {})
    guardrail_summary = data["source_packet_false_positive_guardrail"].get("summary", {})
    trigger_summary = data["source_packet_reopen_trigger_matrix"].get("summary", {})
    orientation_summary = data["source_packet_orientation_disambiguator"].get("summary", {})
    control_summary = data["source_packet_orientation_control_quartets"].get("summary", {})
    r3_summary = data["source_packet_r3_bridge_audit"].get("summary", {})
    rubric_summary = data["future_source_rubric_current_stack_dry_run"].get("summary", {})
    geom_summary = data["source_packet_geometric_fingerprint"].get("summary", {})
    frame_summary = data["source_packet_frame_normalized_geometry"].get("summary", {})
    color_summary = data["source_packet_color_profile_manifest"].get("summary", {})
    residual_summary = data["source_packet_repaired_p78_frame_residual"].get("summary", {})
    leakage_summary = data["source_packet_repaired_frame_expansion_leakage"].get("summary", {})
    grey_over_summary = data["c9_grey_black_over_slot_control"].get("summary", {})
    over_tol_summary = data["c9_over_slot_tolerance_gate"].get("summary", {})
    mirrored_summary = data["c9_mirrored_header_glyph_gate"].get("summary", {})
    witness_summary = data["c9_active_format_witness_reconciliation"].get("summary", {})

    rows = [
        row(
            "current scan and local derivatives",
            "baseline/source",
            {"R1": "FAIL", "R2": "PARTIAL", "R3": "FAIL", "R4": "PARTIAL", "R5": "FAIL"},
            f"rubric paths={rubric_summary.get('pathCount')}; all fail R3={rubric_summary.get('allCurrentPathsFailR3')}",
            "not physically/original-layout distinct; no source-backed unit/order",
            "Only score materially new physical/original-layout/source evidence.",
            ["future_source_rubric_current_stack_dry_run"],
        ),
        row(
            "active O4/B4/G5/O5 geometry",
            "page-76 locator",
            {"R1": "FAIL", "R2": "PASS", "R3": "FAIL", "R4": "PASS", "R5": "PARTIAL"},
            f"lines {geom_summary.get('activePageLines')}; gaps {geom_summary.get('pageLineGaps')}; signs {geom_summary.get('dxSignStream')}/{geom_summary.get('dySignStream')}",
            "strong locator; no extraction unit/order",
            "Use as validation target after a new source passes R1/R3.",
            ["source_packet_geometric_fingerprint", "source_packet_orientation_disambiguator"],
        ),
        row(
            "Y/K frame plus orientation controls",
            "frame/color benchmark",
            {"R1": "FAIL", "R2": "PASS", "R3": "FAIL", "R4": "PASS", "R5": "PARTIAL"},
            f"YKKY combos {control_summary.get('fullPageYkYkkyCombinationCount')}/70; contiguous windows {control_summary.get('fullPageYkSlidingYkkyCount')}/5",
            "pattern-only YKKY is controlled; geometry is still registration evidence only",
            "Require source wording that names the Y/K frame or active quartet order.",
            ["source_packet_orientation_control_quartets", "source_packet_frame_normalized_geometry"],
        ),
        row(
            "C9 / OVERDOSE layout mechanics",
            "glyph/slot benchmark",
            {"R1": "FAIL", "R2": "PARTIAL", "R3": "FAIL", "R4": "PASS", "R5": "FAIL"},
            f"C9 inside {frame_summary.get('c9ActiveFullInsideCount')}/4; p75 control matches mirrored variants {mirrored_summary.get('controlMatchesActiveBlackStreamCount')}",
            "OVER/slot effects are controlled by p75 and mirrored/header variants",
            "Only reopen if source explicitly links OVERDOSE slots to active boxes and controls fail.",
            [
                "source_packet_frame_normalized_geometry",
                "c9_grey_black_over_slot_control",
                "c9_over_slot_tolerance_gate",
                "c9_mirrored_header_glyph_gate",
            ],
        ),
        row(
            "folded/reflected p78 frame repair",
            "fold geometry benchmark",
            {"R1": "FAIL", "R2": "PARTIAL", "R3": "FAIL", "R4": "PASS", "R5": "FAIL"},
            f"max full inside {residual_summary.get('maxFullInsideActiveCount')}/4; full-cover leakage {leakage_summary.get('fullCoverWordCount')}/{leakage_summary.get('fullCoverNonTargetWordCount')}",
            "dx repair improves residuals but all-four isolation requires a context-leaky expansion",
            "Only reopen if a physical/original source naturally explains the transform.",
            ["source_packet_repaired_p78_frame_residual", "source_packet_repaired_frame_expansion_leakage"],
        ),
        row(
            "bold/highlight witness stack",
            "format authority",
            {"R1": "FAIL", "R2": "PARTIAL", "R3": "FAIL", "R4": "PASS", "R5": "FAIL"},
            f"DOCM/high-res/crop authority; line-level exact bold matches {witness_summary.get('lineLevelExactBoldTargetMatchCount')}",
            "format witnesses disagree or remain authority layers; no instruction says read bold/highlight",
            "Only reopen if source/provenance says read, take, count, or order format units.",
            ["c9_active_format_witness_reconciliation", "source_packet_color_profile_manifest"],
        ),
        row(
            "archived clue/provenance wording",
            "external clue",
            {"R1": "PARTIAL", "R2": "PARTIAL", "R3": "FAIL", "R4": "PASS", "R5": "FAIL"},
            f"source-backed R3 hits {r3_summary.get('sourceBackedR3BridgeHitCount')}; reopen triggers satisfied {trigger_summary.get('satisfiedTriggerCount')}",
            "no raw/raw-like clue names the extraction unit/order",
            "Search only for source wording naming word/letter/line/edge/font/order.",
            ["source_packet_r3_bridge_audit", "source_packet_reopen_trigger_matrix"],
        ),
    ]

    protocol = [
        {
            "step": 1,
            "gate": "R1",
            "requiredObservation": "Confirm the item is materially new physical/original-layout/source evidence, not a duplicate or resaved current scan.",
            "currentBaseline": "current local sources fail R1",
        },
        {
            "step": 2,
            "gate": "R4",
            "requiredObservation": "Normalize orientation: readable/upright O4/B4/G5/O5 must preserve lines 22/25/27/32, corridors 4/7/9/14, dx/dy -++/+++.",
            "currentBaseline": orientation_summary.get("orientationDisambiguatorFingerprint"),
        },
        {
            "step": 3,
            "gate": "pattern-control",
            "requiredObservation": "Reject matches that only reproduce YKKY/OBBO/OVER; require the stricter contiguous Y/K window and 3/2/5 line-gap controls.",
            "currentBaseline": control_summary.get("orientationControlQuartetFingerprint"),
        },
        {
            "step": 4,
            "gate": "R2/R5",
            "requiredObservation": "Show target preservation and controlled improvement without broad context leakage or p75/OVERDOSE control reproduction.",
            "currentBaseline": f"handoff gates {handoff_summary.get('gateCount')}; selectors {handoff_summary.get('selectorUnlockedCount')}",
        },
        {
            "step": 5,
            "gate": "R3",
            "requiredObservation": "Find source-backed wording or layout that names the extraction unit/order before any selector/key checks resume.",
            "currentBaseline": f"source R3 {r3_summary.get('sourceBackedR3BridgeHitCount')}; triggers {trigger_summary.get('satisfiedTriggerCount')}/{trigger_summary.get('triggerCount')}",
        },
    ]

    summary = {
        "pathCount": len(rows),
        "extractionReadyCount": sum(1 for item in rows if item["extractionReady"]),
        "r3FailCount": sum(1 for item in rows if not item["r3Pass"]),
        "r1FailCount": sum(1 for item in rows if item["gates"].get("R1") == "FAIL"),
        "r4PassCount": sum(1 for item in rows if item["gates"].get("R4") == "PASS"),
        "handoffGateCount": handoff_summary.get("gateCount"),
        "handoffSelectorUnlockedCount": handoff_summary.get("selectorUnlockedCount"),
        "hardRejectWithoutR3Count": guardrail_summary.get("hardRejectWithoutR3Count"),
        "satisfiedReopenTriggerCount": trigger_summary.get("satisfiedTriggerCount"),
        "sourceBackedR3BridgeHitCount": r3_summary.get("sourceBackedR3BridgeHitCount"),
        "orientationModeAcceptedCount": orientation_summary.get("acceptedOrientationModeCount"),
        "orientationControlYkkyCombinationCount": control_summary.get("fullPageYkYkkyCombinationCount"),
        "orientationControlYkkyNonExactCount": control_summary.get("fullPageYkYkkyNonExactCombinationCount"),
        "c9ActiveFullInsideCount": frame_summary.get("c9ActiveFullInsideCount"),
        "p78MaxFullInsideActiveCount": residual_summary.get("maxFullInsideActiveCount"),
        "fullCoverLeakageWordCount": leakage_summary.get("fullCoverWordCount"),
        "activeYOrangeRatioRange": color_summary.get("activeYOrangeRatioRange"),
        "activeKDarkRatioRange": color_summary.get("activeKDarkRatioRange"),
        "overControlCanonicalActiveOverCount": over_tol_summary.get("canonicalActiveOverCount"),
        "greyBlackControlOverSpan": grey_over_summary.get("controlGreyBlackOverSpan"),
    }
    summary["sourceReviewGateFingerprint"] = (
        f"paths={summary['pathCount']}|ready={summary['extractionReadyCount']}|"
        f"r3Fail={summary['r3FailCount']}|R1Fail={summary['r1FailCount']}|"
        f"R4Pass={summary['r4PassCount']}|triggers={summary['satisfiedReopenTriggerCount']}/"
        f"{trigger_summary.get('triggerCount')}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"YKKY={summary['orientationControlYkkyCombinationCount']}|selectors={summary['handoffSelectorUnlockedCount']}"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current source-packet source-review gate dry run; no OCR extraction, key candidates, "
            "hashing, WIF, seed, address, BIP39, or broad brute force"
        ),
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "reopenGates": reopen_gates,
        "minimumReopenConditions": min_conditions,
        "protocol": protocol,
        "rows": rows,
        "summary": summary,
        "decision": {
            "sourcePacketSourceReviewGate": "current-stack-not-extraction-ready",
            "ruledOut": [
                "using the current scan or local derivatives as new source evidence",
                "accepting YKKY/OBBO/OVERDOSE pattern matches without the stricter geometry and R3",
                "reopening selector/key work from source-registration benchmarks alone",
            ],
            "retained": [
                "readable/upright orientation normalization",
                "orientation-control quartet guardrail",
                "R1-R5 plus exact reopen trigger order for future source review",
            ],
            "nextMove": (
                "Future review should begin with this gate order: R1 distinct source, R4 orientation, "
                "pattern controls, R2/R5 preservation and controlled improvement, then R3 unit/order. "
                "If R3 remains absent, stop before selector/key work."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(summary, rows, protocol)

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Source-Review Gate",
        "",
        "Scope: dry-run the current source packet against the future source-review gates. No OCR extraction, key candidates, hashes, WIF, seed, address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{summary['sourceReviewGateFingerprint']}`",
        "",
        "## Summary",
        "",
        f"- Candidate current paths tested: `{summary['pathCount']}`.",
        f"- Extraction-ready current paths: `{summary['extractionReadyCount']}`.",
        f"- Paths failing R3: `{summary['r3FailCount']}`.",
        f"- Paths failing R1: `{summary['r1FailCount']}`.",
        f"- Paths passing R4 orientation discipline: `{summary['r4PassCount']}`.",
        f"- Source-backed R3 bridge hits: `{summary['sourceBackedR3BridgeHitCount']}`.",
        f"- Satisfied reopen triggers: `{summary['satisfiedReopenTriggerCount']}` / `{trigger_summary.get('triggerCount')}`.",
        f"- Handoff selector unlocks: `{summary['handoffSelectorUnlockedCount']}`.",
        "",
        "## Path Matrix",
        "",
        "| path | R1 | R2 | R3 | R4 | R5 | blocker |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in rows:
        gates = item["gates"]
        lines.append(
            f"| {item['path']} | `{gates['R1']}` | `{gates['R2']}` | `{gates['R3']}` | `{gates['R4']}` | `{gates['R5']}` | {item['blocker']} |"
        )

    lines.extend(["", "## Future Source Review Protocol", ""])
    for item in protocol:
        lines.append(
            f"- Step {item['step']} `{item['gate']}`: {item['requiredObservation']} Current baseline: `{item['currentBaseline']}`."
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The current stack is not extraction-ready: every tested path fails R3, and no path passes all R1-R5 gates.",
            "- The active geometry and orientation controls remain useful future-source validation benchmarks, not current key material.",
            "- Future evidence should stop at this gate if it lacks source-backed unit/order wording.",
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", summary["sourceReviewGateFingerprint"])


if __name__ == "__main__":
    main()
