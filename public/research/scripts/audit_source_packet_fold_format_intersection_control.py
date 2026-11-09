#!/usr/bin/env python3
"""Audit whether folded 3D geometry plus format state unlocks extraction.

This bounded pass intersects the existing folded/mirrored 3D carrier evidence
with active bold/highlight authority and page-76 target-cluster controls. It
does not OCR, hash, derive keys, or generate candidates.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_fold_format_intersection_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_fold_format_intersection_control.json"
OUT_MD = OUT / "source_packet_fold_format_intersection_control.md"
OUT_SHEET = OUT / "source_packet_fold_format_intersection_control_sheet.jpg"

INPUTS = {
    "article_3d_map_summary": ROOT
    / "analysis_outputs/3d_article_map/article_3d_map_data_summary.md",
    "user_annotated_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "user_markdown_transcript": ROOT
    / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "plain_correction_report": ROOT
    / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
    "reflection_line_pitch_stack_gate": ROOT
    / "analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/"
    "reflection_line_pitch_stack_gate.json",
    "reflection_shifted_carrier_content_gate": ROOT
    / "analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate/"
    "reflection_shifted_carrier_content_gate.json",
    "fold_mirror_r3_gate_synthesis": ROOT
    / "analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/"
    "fold_mirror_r3_gate_synthesis.json",
    "page76_highlight_fold_axis_population_gate": ROOT
    / "analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate/"
    "page76_highlight_fold_axis_population_gate.json",
    "c9_active_format_witness_reconciliation": ROOT
    / "analysis_outputs/source_audit/c9_active_format_witness_reconciliation/"
    "c9_active_format_witness_reconciliation.json",
    "source_packet_orientation_control_quartets": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json",
    "source_packet_source_review_gate": ROOT
    / "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json",
    "source_packet_overdose_transform_control": ROOT
    / "analysis_outputs/source_audit/source_packet_overdose_transform_control/"
    "source_packet_overdose_transform_control.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def file_status(path: Path) -> dict:
    return {
        "present": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def status(ok: bool, partial: bool = False) -> str:
    if ok:
        return "PASS"
    if partial:
        return "PARTIAL"
    return "FAIL"


def draw_sheet(summary: dict, rows: list[dict]) -> None:
    width, height = 1760, 900
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

    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Folded 3D + Format Intersection Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"ready {summary['extractionReadyIntersectionCount']} | "
            f"single-shift all-four {summary['singleShiftAllFourCount']} | "
            f"non-target slice words {summary['sliceNonTargetWordCountTotal']} | "
            f"sourceR3 {summary['sourceBackedR3BridgeHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Intersection gates", fill=(45, 45, 45), font=small)
    y += 30
    headers = ["gate", "status", "observation", "blocker"]
    xs = [24, 430, 540, 1060]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 58), fill=fill)
        color = (
            (25, 110, 55)
            if row["status"] == "PASS"
            else (125, 85, 25)
            if row["status"] == "PARTIAL"
            else (145, 35, 25)
        )
        draw.text((xs[0], y), row["gate"][:48], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["status"], fill=color, font=tiny)
        draw.text((xs[2], y), row["observation"][:70], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["blocker"][:84], fill=(70, 70, 70), font=tiny)
        y += 66

    y += 16
    draw.text((24, y), "Decision", fill=(45, 45, 45), font=small)
    y += 28
    draw.text((24, y), summary["foldFormatIntersectionFingerprint"], fill=(45, 45, 45), font=tiny)
    y += 24
    draw.text(
        (24, y),
        "Fold/format intersection remains source-validation context only; no unit/order selector is supplied.",
        fill=(70, 70, 70),
        font=tiny,
    )
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    reflection = load_json(INPUTS["reflection_line_pitch_stack_gate"])
    carrier = load_json(INPUTS["reflection_shifted_carrier_content_gate"])
    fold_r3 = load_json(INPUTS["fold_mirror_r3_gate_synthesis"])
    axis = load_json(INPUTS["page76_highlight_fold_axis_population_gate"])
    format_witness = load_json(INPUTS["c9_active_format_witness_reconciliation"])
    orientation = load_json(INPUTS["source_packet_orientation_control_quartets"])
    review = load_json(INPUTS["source_packet_source_review_gate"])
    overdose = load_json(INPUTS["source_packet_overdose_transform_control"])
    correction = load_json(INPUTS["plain_correction_report"])

    reflection_summary = reflection.get("summary", {})
    carrier_summary = carrier.get("summary", {})
    axis_summary = axis.get("summary", {})
    format_summary = format_witness.get("summary", {})
    orientation_summary = orientation.get("summary", {})
    review_summary = review.get("summary", {})
    overdose_summary = overdose.get("summary", {})

    correction_outputs = correction.get("outputs", {}) if isinstance(correction.get("outputs"), dict) else {}
    source_inputs = {
        "article_3d_map_summary": file_status(INPUTS["article_3d_map_summary"]),
        "user_annotated_transcript": file_status(INPUTS["user_annotated_transcript"]),
        "user_markdown_transcript": file_status(INPUTS["user_markdown_transcript"]),
        "plain_correction_report": file_status(INPUTS["plain_correction_report"]),
        "plain_correction_outputKeys": list(correction_outputs.keys()),
    }

    rows = [
        {
            "gate": "global folded operation covers all four targets",
            "status": status(reflection_summary.get("singleShiftAllFourCount", 0) > 0),
            "observation": (
                f"carriers {reflection_summary.get('allFourActiveCarrierCount')} but "
                f"single global shifts {reflection_summary.get('singleShiftAllFourCount')}"
            ),
            "blocker": "all-four contact requires per-target shifting, not a single fold/read rule",
        },
        {
            "gate": "shifted carrier content isolates targets",
            "status": status(carrier_summary.get("targetPhraseIsolatedSliceCount", 0) > 0),
            "observation": (
                f"{carrier_summary.get('activeSliceCount')} slices, "
                f"{carrier_summary.get('sliceNonTargetWordCountTotal')} non-target words"
            ),
            "blocker": "row slices are broad context, not target-only extraction units",
        },
        {
            "gate": "fold/highlight population gives active axis",
            "status": status(axis_summary.get("allFourActiveAxisCount", 0) > 0),
            "observation": (
                f"{axis_summary.get('axisCandidateCount')} axes, all-four "
                f"{axis_summary.get('allFourActiveAxisCount')}, non-tautological two-active "
                f"{axis_summary.get('nonTautologicalTwoActiveAxisCount')}"
            ),
            "blocker": "no non-tautological fold axis selects the active quartet",
        },
        {
            "gate": "format authority agrees enough for validation",
            "status": status(
                format_summary.get("formatAuthorityPassCount", 0) == 4,
                partial=format_summary.get("formatAuthorityPassCount", 0) > 0,
            ),
            "observation": (
                f"authority pass {format_summary.get('formatAuthorityPassCount')}/4, "
                f"witness conflicts {format_summary.get('witnessConflictCount')}"
            ),
            "blocker": "format authority validates targets but does not define unit/order",
        },
        {
            "gate": "bold/markdown/annotation layer supplies selector",
            "status": status(format_summary.get("selectorUnlocked")),
            "observation": (
                f"line-bold matches {format_summary.get('lineLevelExactBoldMatchCount')}, "
                f"markdown phrase matches {format_summary.get('markdownBoldContainsPhraseCount')}"
            ),
            "blocker": "line-level bold, Markdown, and annotations remain witness/context layers",
        },
        {
            "gate": "active orientation controls are selective",
            "status": status(
                orientation_summary.get("formatLineGapExactMatchCount") == 1,
                partial=orientation_summary.get("fullPageYkYkkyCombinationCount", 0) > 1,
            ),
            "observation": (
                f"YKKY {orientation_summary.get('fullPageYkYkkyCombinationCount')}/"
                f"{orientation_summary.get('fullPageYkCombinationCount')}; line-gap exact "
                f"{orientation_summary.get('formatLineGapExactMatchCount')}"
            ),
            "blocker": "selective geometry is source-registration only without R3",
        },
        {
            "gate": "OVERDOSE mechanics independently confirm order",
            "status": status(overdose_summary.get("sourceBackedR3BridgeHitCount", 0) > 0),
            "observation": (
                f"centers {overdose_summary.get('activeCenterLineOrderStream')}/"
                f"{overdose_summary.get('activeCenterXOrderStream')}; p75 mirrors "
                f"{overdose_summary.get('p75MirrorVariantMatchCount')}/"
                f"{overdose_summary.get('mirrorVariantCount')}"
            ),
            "blocker": "OVERDOSE black OVER remains controlled by p75 and variants",
        },
        {
            "gate": "source-review R3 unlock",
            "status": status(review_summary.get("sourceBackedR3BridgeHitCount", 0) > 0),
            "observation": (
                f"ready {review_summary.get('extractionReadyCount')}, "
                f"R3 failures {review_summary.get('r3FailCount')}, "
                f"triggers {review_summary.get('satisfiedReopenTriggerCount')}/9"
            ),
            "blocker": "no distinct source/provenance wording names extraction unit/order",
        },
    ]

    extraction_ready = all(row["status"] == "PASS" for row in rows)
    selector_unlocked_count = sum(
        1
        for value in [
            reflection_summary.get("selectorUnlocked"),
            carrier_summary.get("selectorUnlocked"),
            axis_summary.get("selectorUnlocked"),
            format_summary.get("selectorUnlocked"),
            review_summary.get("handoffSelectorUnlockedCount", 0) > 0,
        ]
        if value
    )

    summary = {
        "intersectionGateCount": len(rows),
        "passGateCount": sum(1 for row in rows if row["status"] == "PASS"),
        "partialGateCount": sum(1 for row in rows if row["status"] == "PARTIAL"),
        "failGateCount": sum(1 for row in rows if row["status"] == "FAIL"),
        "extractionReadyIntersectionCount": 1 if extraction_ready else 0,
        "allFourActiveCarrierCount": reflection_summary.get("allFourActiveCarrierCount"),
        "singleShiftAllFourCount": reflection_summary.get("singleShiftAllFourCount"),
        "strictInstructionHitCount": (
            reflection_summary.get("strictInstructionHitCount", 0)
            + carrier_summary.get("strictInstructionHitCount", 0)
            + axis_summary.get("strictInstructionAxisHits", 0)
        ),
        "activeSliceCount": carrier_summary.get("activeSliceCount"),
        "sliceWordCountTotal": carrier_summary.get("sliceWordCountTotal"),
        "sliceNonTargetWordCountTotal": carrier_summary.get("sliceNonTargetWordCountTotal"),
        "targetPhraseIsolatedSliceCount": carrier_summary.get("targetPhraseIsolatedSliceCount"),
        "uniqueInferredBaseLines": carrier_summary.get("uniqueInferredBaseLines"),
        "activeLineGapPattern": carrier_summary.get("activeLineGapPattern"),
        "allCarrierShiftGapsMatchPageLineGaps": carrier_summary.get(
            "allCarrierShiftGapsMatchPageLineGaps"
        ),
        "axisCandidateCount": axis_summary.get("axisCandidateCount"),
        "allFourActiveAxisCount": axis_summary.get("allFourActiveAxisCount"),
        "nonTautologicalTwoActiveAxisCount": axis_summary.get("nonTautologicalTwoActiveAxisCount"),
        "formatAuthorityPassCount": format_summary.get("formatAuthorityPassCount"),
        "witnessConflictCount": format_summary.get("witnessConflictCount"),
        "lineLevelExactBoldMatchCount": format_summary.get("lineLevelExactBoldMatchCount"),
        "markdownBoldContainsPhraseCount": format_summary.get("markdownBoldContainsPhraseCount"),
        "orientationYkkyCombinationCount": orientation_summary.get(
            "fullPageYkYkkyCombinationCount"
        ),
        "orientationFormatLineGapExactMatchCount": orientation_summary.get(
            "formatLineGapExactMatchCount"
        ),
        "overdoseControlFingerprint": overdose_summary.get("overdoseTransformControlFingerprint"),
        "sourceReviewExtractionReadyCount": review_summary.get("extractionReadyCount"),
        "sourceBackedR3BridgeHitCount": review_summary.get("sourceBackedR3BridgeHitCount"),
        "satisfiedReopenTriggerCount": review_summary.get("satisfiedReopenTriggerCount"),
        "selectorUnlockedCount": selector_unlocked_count,
        "foldMirrorR3Decision": fold_r3.get("decision"),
        "foldFormatIntersectionFingerprint": (
            f"gates={len(rows)}|pass={sum(1 for row in rows if row['status'] == 'PASS')}"
            f"|partial={sum(1 for row in rows if row['status'] == 'PARTIAL')}"
            f"|singleShiftAll4={reflection_summary.get('singleShiftAllFourCount')}"
            f"|carrierNonTarget={carrier_summary.get('sliceNonTargetWordCountTotal')}"
            f"|isolated={carrier_summary.get('targetPhraseIsolatedSliceCount')}"
            f"|axesAll4={axis_summary.get('allFourActiveAxisCount')}"
            f"|formatPass={format_summary.get('formatAuthorityPassCount')}"
            f"|formatConflicts={format_summary.get('witnessConflictCount')}"
            f"|sourceR3={review_summary.get('sourceBackedR3BridgeHitCount')}"
            f"|selectors={selector_unlocked_count}"
        ),
    }

    decision = {
        "sourcePacketFoldFormatIntersectionControl": "fold_format_intersection_no_selector",
        "selectorUnlocked": False,
        "reason": (
            "Folded 3D carriers, page-76 highlight axes, and active format state "
            "do not combine into a source-backed unit/order rule. The only pass is "
            "format authority for source comparison; geometry and R3 gates fail."
        ),
        "nextMove": (
            "Use this as the folded-geometry/format guardrail in future source "
            "review. Do not reopen selector/key work unless a distinct source "
            "names a fold/reflection/format operation and passes R1-R5."
        ),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "folded 3D geometry plus bold/highlight intersection control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "sourceInputStatus": source_inputs,
        "intersectionRows": rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Fold/Format Intersection Control",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scope: {result['scope']}.",
        "",
        "## Findings",
        "",
        (
            "- Folded/reflected carriers touching all four active targets: "
            f"`{summary['allFourActiveCarrierCount']}`; single global all-four shifts: "
            f"`{summary['singleShiftAllFourCount']}`."
        ),
        (
            "- Shifted carrier slices: "
            f"`{summary['activeSliceCount']}` active slices, "
            f"`{summary['sliceWordCountTotal']}` total words, "
            f"`{summary['sliceNonTargetWordCountTotal']}` non-target words, "
            f"`{summary['targetPhraseIsolatedSliceCount']}` target-isolated slices."
        ),
        (
            "- Fold/highlight axes tested: "
            f"`{summary['axisCandidateCount']}`; all-four active axes: "
            f"`{summary['allFourActiveAxisCount']}`; non-tautological two-active axes: "
            f"`{summary['nonTautologicalTwoActiveAxisCount']}`."
        ),
        (
            "- Format authority passes: "
            f"`{summary['formatAuthorityPassCount']}/4`; witness conflicts: "
            f"`{summary['witnessConflictCount']}`."
        ),
        (
            "- Intersection gates pass/partial/fail: "
            f"`{summary['passGateCount']}` / `{summary['partialGateCount']}` / "
            f"`{summary['failGateCount']}`."
        ),
        (
            "- Source-backed R3 hits / satisfied reopen triggers / selector unlocks: "
            f"`{summary['sourceBackedR3BridgeHitCount']}` / "
            f"`{summary['satisfiedReopenTriggerCount']}` / "
            f"`{summary['selectorUnlockedCount']}`."
        ),
        f"- Fingerprint: `{summary['foldFormatIntersectionFingerprint']}`.",
        "",
        "## Decision",
        "",
        "- Do not promote folded 3D geometry plus bold/highlight state as a selector.",
        "- Keep the combination as source-validation context only.",
        "- Reopen only if a distinct source names the fold/reflection/format operation and provides a unit/order rule that passes R1-R5.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    draw_sheet(summary, rows)

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", summary["foldFormatIntersectionFingerprint"])


if __name__ == "__main__":
    main()
