#!/usr/bin/env python3
"""Build a terminal coverage matrix for the current source packet.

This bounded inspection checks whether the requested focus areas are now
covered by explicit guardrails and whether any of them is extraction-ready. It
packages the current handoff without running selector/key permutations.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_terminal_coverage_matrix"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_terminal_coverage_matrix.json"
OUT_MD = OUT / "source_packet_terminal_coverage_matrix.md"
OUT_SHEET = OUT / "source_packet_terminal_coverage_matrix_sheet.jpg"

INPUTS = {
    "investigation_log": ROOT / "INVESTIGATION_LOG.md",
    "clue_ledger": ROOT / "CLUE_LEDGER.md",
    "article_3d_map_summary": ROOT / "analysis_outputs/3d_article_map/article_3d_map_data_summary.md",
    "user_annotated_transcript": ROOT / "analysis_outputs/3d_article_map/user_annotated_transcript.txt",
    "user_markdown_transcript": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "plain_correction_report": ROOT
    / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json",
    "missing_rule_frontier": ROOT
    / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json",
    "source_packet_source_review_gate": ROOT
    / "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
    "source_packet_false_positive_guardrail": ROOT
    / "analysis_outputs/source_audit/source_packet_false_positive_guardrail/"
    "source_packet_false_positive_guardrail.json",
    "source_packet_orientation_control_quartets": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json",
    "source_packet_fold_format_intersection_control": ROOT
    / "analysis_outputs/source_audit/source_packet_fold_format_intersection_control/"
    "source_packet_fold_format_intersection_control.json",
    "source_packet_overdose_transform_control": ROOT
    / "analysis_outputs/source_audit/source_packet_overdose_transform_control/"
    "source_packet_overdose_transform_control.json",
    "source_packet_r3_bridge_audit": ROOT
    / "analysis_outputs/source_audit/source_packet_r3_bridge_audit/"
    "source_packet_r3_bridge_audit.json",
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


def draw_sheet(summary: dict, rows: list[dict]) -> None:
    width, height = 1820, 980
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
    draw.text((24, 18), "Source Packet Terminal Coverage Matrix", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"covered {summary['coveredGuardrailCount']}/{summary['coverageAreaCount']} | "
            f"ready {summary['extractionReadyAreaCount']} | "
            f"sourceR3 {summary['sourceBackedR3BridgeHitCount']} | "
            f"selectors {summary['selectorUnlockedCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Coverage by requested focus area", fill=(45, 45, 45), font=small)
    y += 30
    headers = ["focus area", "guardrail", "ready", "current blocker"]
    xs = [24, 520, 900, 1000]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 58), fill=fill)
        guard_color = (25, 110, 55) if row["guardrailPresent"] else (145, 35, 25)
        ready_color = (25, 110, 55) if row["extractionReady"] else (145, 35, 25)
        draw.text((xs[0], y), row["focusArea"][:62], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), "present" if row["guardrailPresent"] else "missing", fill=guard_color, font=tiny)
        draw.text((xs[2], y), "yes" if row["extractionReady"] else "no", fill=ready_color, font=tiny)
        draw.text((xs[3], y), row["blocker"][:100], fill=(70, 70, 70), font=tiny)
        draw.text((xs[0], y + 20), row["evidence"][:138], fill=(80, 80, 80), font=tiny)
        y += 66

    y += 18
    draw.text((24, y), "Next move", fill=(45, 45, 45), font=small)
    y += 28
    draw.text((24, y), summary["recommendedNextMove"][:170], fill=(60, 60, 60), font=tiny)
    y += 24
    draw.text((24, y), summary["terminalCoverageFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    frontier = load_json(INPUTS["missing_rule_frontier"])
    review = load_json(INPUTS["source_packet_source_review_gate"])
    reopen = load_json(INPUTS["source_packet_reopen_trigger_matrix"])
    guardrail = load_json(INPUTS["source_packet_false_positive_guardrail"])
    orientation = load_json(INPUTS["source_packet_orientation_control_quartets"])
    fold_format = load_json(INPUTS["source_packet_fold_format_intersection_control"])
    overdose = load_json(INPUTS["source_packet_overdose_transform_control"])
    r3 = load_json(INPUTS["source_packet_r3_bridge_audit"])

    frontier_decision = frontier.get("decision", {})
    review_summary = review.get("summary", {})
    reopen_summary = reopen.get("summary", {})
    guardrail_summary = guardrail.get("summary", {})
    orientation_summary = orientation.get("summary", {})
    fold_summary = fold_format.get("summary", {})
    overdose_summary = overdose.get("summary", {})
    r3_summary = r3.get("summary", {})

    source_files = {
        name: file_status(path)
        for name, path in INPUTS.items()
        if name
        in {
            "investigation_log",
            "clue_ledger",
            "article_3d_map_summary",
            "user_annotated_transcript",
            "user_markdown_transcript",
            "plain_correction_report",
        }
    }

    rows = [
        {
            "focusArea": "latest log, ledger, transcript, correction, and generated reports",
            "guardrailPresent": all(item["present"] for item in source_files.values()),
            "extractionReady": False,
            "evidence": f"{len(source_files)} source/check files present; frontier loaded",
            "blocker": "orientation/source review still requires R1-R5 and R3 before extraction",
        },
        {
            "focusArea": "page-76 active target cluster O4/B4/G5/O5",
            "guardrailPresent": review_summary.get("pathCount", 0) >= 7,
            "extractionReady": review_summary.get("extractionReadyCount", 0) > 0,
            "evidence": (
                f"source-review paths {review_summary.get('pathCount')}, "
                f"ready {review_summary.get('extractionReadyCount')}, "
                f"R3 fails {review_summary.get('r3FailCount')}"
            ),
            "blocker": "cluster is a validation surface; no source-backed unit/order",
        },
        {
            "focusArea": "orange/black highlights and Y/K readable orientation",
            "guardrailPresent": orientation_summary.get("fullPageYkCombinationCount", 0) > 0,
            "extractionReady": orientation_summary.get("sourceBackedR3BridgeHitCount", 0) > 0,
            "evidence": (
                f"YKKY {orientation_summary.get('fullPageYkYkkyCombinationCount')}/"
                f"{orientation_summary.get('fullPageYkCombinationCount')}; "
                f"exact line-gap matches {orientation_summary.get('formatLineGapExactMatchCount')}"
            ),
            "blocker": "visual state alone is non-unique and supplies no extraction order",
        },
        {
            "focusArea": "folded/mirrored 3D geometry plus bold/highlight state",
            "guardrailPresent": fold_summary.get("intersectionGateCount", 0) > 0,
            "extractionReady": fold_summary.get("extractionReadyIntersectionCount", 0) > 0,
            "evidence": (
                f"gates {fold_summary.get('intersectionGateCount')}, "
                f"pass {fold_summary.get('passGateCount')}, "
                f"singleShiftAll4 {fold_summary.get('singleShiftAllFourCount')}, "
                f"non-target words {fold_summary.get('sliceNonTargetWordCountTotal')}"
            ),
            "blocker": "per-target shifts and broad row context; no fold/format unit/order",
        },
        {
            "focusArea": "OVERDOSE layout mechanics",
            "guardrailPresent": overdose_summary.get("glyphSequence") == "OVERDOSE",
            "extractionReady": overdose_summary.get("sourceBackedR3BridgeHitCount", 0) > 0,
            "evidence": (
                f"glyph delta {overdose_summary.get('headerGlyphMaxEdgeDeltaVsEqualSlotPx')}; "
                f"center {overdose_summary.get('activeCenterLineOrderStream')}/"
                f"{overdose_summary.get('activeCenterXOrderStream')}; "
                f"p75 mirrors {overdose_summary.get('p75MirrorVariantMatchCount')}/"
                f"{overdose_summary.get('mirrorVariantCount')}"
            ),
            "blocker": "active black OVER is controlled by p75/mirror/tolerance variants",
        },
        {
            "focusArea": "false-positive guardrail and reopen triggers",
            "guardrailPresent": guardrail_summary.get("hardRejectWithoutR3Count", 0) > 0
            and reopen_summary.get("triggerCount", 0) > 0,
            "extractionReady": reopen_summary.get("satisfiedTriggerCount", 0) > 0,
            "evidence": (
                f"hard rejects {guardrail_summary.get('hardRejectWithoutR3Count')}; "
                f"triggers satisfied {reopen_summary.get('satisfiedTriggerCount')}/"
                f"{reopen_summary.get('triggerCount')}"
            ),
            "blocker": "no current visual/source-packet trigger is satisfied",
        },
        {
            "focusArea": "source-backed R3 bridge",
            "guardrailPresent": r3_summary.get("authoritySourceCount", 0) > 0,
            "extractionReady": r3_summary.get("sourceBackedR3BridgeHitCount", 0) > 0,
            "evidence": (
                f"authority sources {r3_summary.get('authoritySourceCount')}; "
                f"target windows {r3_summary.get('authorityActiveTargetMentionCount')}; "
                f"sourceR3 {r3_summary.get('sourceBackedR3BridgeHitCount')}"
            ),
            "blocker": "local authoritative layers contain target words but no unit/order instruction",
        },
        {
            "focusArea": "next move and handoff discipline",
            "guardrailPresent": bool(frontier_decision.get("sourceReopenGate")),
            "extractionReady": False,
            "evidence": frontier_decision.get("highestValueNextMove", ""),
            "blocker": "next work is source/physical/original-layout validation, not local permutations",
        },
    ]

    covered = sum(1 for row in rows if row["guardrailPresent"])
    ready = sum(1 for row in rows if row["extractionReady"])
    selector_unlocked_count = sum(
        1
        for value in [
            review_summary.get("handoffSelectorUnlockedCount", 0) > 0,
            orientation_summary.get("selectorUnlockedCount", 0) > 0,
            fold_summary.get("selectorUnlockedCount", 0) > 0,
            overdose_summary.get("selectorUnlockedCount", 0) > 0,
            guardrail_summary.get("selectorUnlockedCount", 0) > 0,
        ]
        if value
    )

    summary = {
        "coverageAreaCount": len(rows),
        "coveredGuardrailCount": covered,
        "uncoveredGuardrailCount": len(rows) - covered,
        "extractionReadyAreaCount": ready,
        "sourceBackedR3BridgeHitCount": r3_summary.get("sourceBackedR3BridgeHitCount"),
        "satisfiedReopenTriggerCount": reopen_summary.get("satisfiedTriggerCount"),
        "selectorUnlockedCount": selector_unlocked_count,
        "currentFocusedLocalChecksBeforeThisReport": 103,
        "sourceFilesPresentCount": sum(1 for item in source_files.values() if item["present"]),
        "sourceFilesCheckedCount": len(source_files),
        "recommendedNextMove": frontier_decision.get("highestValueNextMove"),
        "sourceReopenGate": frontier_decision.get("sourceReopenGate"),
        "terminalCoverageFingerprint": (
            f"areas={len(rows)}|covered={covered}|ready={ready}"
            f"|sourceR3={r3_summary.get('sourceBackedR3BridgeHitCount')}"
            f"|triggers={reopen_summary.get('satisfiedTriggerCount')}/"
            f"{reopen_summary.get('triggerCount')}"
            f"|selectors={selector_unlocked_count}"
            f"|next=source-validation"
        ),
    }

    decision = {
        "sourcePacketTerminalCoverageMatrix": "covered_not_extraction_ready",
        "selectorUnlocked": False,
        "reason": (
            "Every requested focus area now has an explicit guardrail, but zero "
            "areas are extraction-ready because source-backed R3 and satisfied "
            "reopen triggers remain absent."
        ),
        "nextMove": (
            "Stop local selector/key permutations. Future work should inspect only "
            "a distinct source/photo/original export/clue through the R1-R5 "
            "source-review gate."
        ),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "terminal source-packet coverage inspection; no extraction, hashing, WIF, seed phrase, address, or key checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "sourceFileStatus": source_files,
        "coverageRows": rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Terminal Coverage Matrix",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scope: {result['scope']}.",
        "",
        "## Coverage",
        "",
        "| focus area | guardrail | extraction-ready | blocker |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['focusArea']} | `{row['guardrailPresent']}` | "
            f"`{row['extractionReady']}` | {row['blocker']} |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Guardrails present: `{summary['coveredGuardrailCount']}/{summary['coverageAreaCount']}`.",
            f"- Extraction-ready areas: `{summary['extractionReadyAreaCount']}`.",
            (
                "- Source-backed R3 hits / satisfied reopen triggers / selector unlocks: "
                f"`{summary['sourceBackedR3BridgeHitCount']}` / "
                f"`{summary['satisfiedReopenTriggerCount']}` / "
                f"`{summary['selectorUnlockedCount']}`."
            ),
            f"- Fingerprint: `{summary['terminalCoverageFingerprint']}`.",
            "",
            "## Decision",
            "",
            "- The requested focus areas are covered by guardrails, not by an extraction rule.",
            "- No current local branch should reopen selector/key work.",
            "- The next move remains distinct source/physical/original-layout validation through R1-R5.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    draw_sheet(summary, rows)

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", summary["terminalCoverageFingerprint"])


if __name__ == "__main__":
    main()
