#!/usr/bin/env python3
"""Build an explicit reopen-trigger matrix for source-packet visual evidence.

This bounded pass does not try another selector. It translates the current
visual/geometry false-positive guardrails into exact source observations that
would be sufficient to reopen extraction.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_reopen_trigger_matrix.json"
OUT_MD = OUT / "source_packet_reopen_trigger_matrix.md"
OUT_SHEET = OUT / "source_packet_reopen_trigger_matrix_sheet.jpg"

INPUTS = {
    "source_reopen_requirements": ROOT
    / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "future_source_validation_packet": ROOT
    / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "source_packet_handoff_integrity_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.json",
    "source_packet_false_positive_guardrail": ROOT
    / "analysis_outputs/source_audit/source_packet_false_positive_guardrail/"
    "source_packet_false_positive_guardrail.json",
    "source_packet_r3_bridge_audit": ROOT
    / "analysis_outputs/source_audit/source_packet_r3_bridge_audit/"
    "source_packet_r3_bridge_audit.json",
    "source_packet_color_profile_manifest": ROOT
    / "analysis_outputs/source_audit/source_packet_color_profile_manifest/"
    "source_packet_color_profile_manifest.json",
    "source_packet_frame_normalized_geometry": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/"
    "source_packet_frame_normalized_geometry.json",
    "source_packet_repaired_p78_frame_residual": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/"
    "source_packet_repaired_p78_frame_residual.json",
    "source_packet_repaired_frame_expansion_leakage": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/"
    "source_packet_repaired_frame_expansion_leakage.json",
}

TRIGGER_BLUEPRINTS = {
    "color_or_state_only": {
        "domain": "orange/black + bold state",
        "externalObservable": "A distinct source/original layout explicitly ties Y/K or orange/black order to a reading unit and preserves readable order 22/25/27/32.",
        "minimumArtifact": "original export/source layer or raw clue text; not a resaved scan",
        "acceptanceTest": "R1 distinct source + R3 unit/order + R4 readable/native orientation + controls do not reproduce the same color/order logic",
        "currentBlocker": "YKKY/OBBO is palindromic and full-page Y/K has four non-active controls.",
    },
    "native_unrotated_order": {
        "domain": "native/source orientation",
        "externalObservable": "Source provenance states native coordinate direction, or a fresh extraction proves the active quartet after the documented 180-degree transform.",
        "minimumArtifact": "native source image/PDF extraction with page orientation metadata",
        "acceptanceTest": "R4 orientation discipline; raw-native reversed order must not be accepted as a match",
        "currentBlocker": "Native raw order reverses to 32/27/25/22 and 14/9/7/4 unless rotated 180 degrees.",
    },
    "c9_frame_only": {
        "domain": "C9/Y-K frame",
        "externalObservable": "Source shows the C9/Y-K frame as an intentional reading boundary and names the units/order inside it.",
        "minimumArtifact": "original layout layer or source note with frame/read instruction",
        "acceptanceTest": "All four active targets inside, context leakage avoided, p75/frame controls fail under the same rule",
        "currentBlocker": "C9 frame fully contains the quartet but is broad, mirror-invariant, and source-validation only.",
    },
    "overdose_black_over": {
        "domain": "OVERDOSE glyph slots",
        "externalObservable": "Source explicitly links OVERDOSE glyph slots to active boxes and names which glyph/slot stream to read.",
        "minimumArtifact": "raw source clue, original layout annotation, or higher-fidelity source showing slot linkage",
        "acceptanceTest": "Active slot rule succeeds, p75 control no longer reproduces it, and R3 unit/order is explicit",
        "currentBlocker": "p75 control reproduces OVER-style slot streams; active mirrored variants are not unique.",
    },
    "p78_contact_or_dx_repair": {
        "domain": "folded/mirrored p78 frame geometry",
        "externalObservable": "Physical/original source naturally explains dx≈-38/-40 or shows the p78 frame shifted/cut in that position without manual tuning.",
        "minimumArtifact": "physical scan/photo/hold-to-light/spread/original layout source",
        "acceptanceTest": "R5 controlled improvement plus all active targets inside without artificial expansion",
        "currentBlocker": "dx repair improves G5/O5 residuals but still gives max full containment 0/4 and max partial 2/4.",
    },
    "p78_full_cover_leakage": {
        "domain": "p78 frame full-cover expansion",
        "externalObservable": "New source isolates O4/B4/G5/O5 as units without taking the full L22-L32 lower-corridor context band.",
        "minimumArtifact": "source crop/layer/physical transform that cleanly bounds only the active quartet",
        "acceptanceTest": "All four active targets isolated; non-target context and non-active format signals fall away",
        "currentBlocker": "Full cover spans 102 words, 92 non-target words, and four non-active format signals.",
    },
    "bold_or_annotation_only": {
        "domain": "bold/highlight/annotation witnesses",
        "externalObservable": "Source or provenance explicitly says to read/take/count bold, highlight, first/last, or a comparable format unit.",
        "minimumArtifact": "DOCM/source-layer instruction, raw clue, or original annotation source",
        "acceptanceTest": "R3 format unit/order is explicit and Markdown/user notes are not the sole evidence",
        "currentBlocker": "DOCM/high-res/crop-pack validate format only; line-level bold and annotations conflict or remain witness layers.",
    },
    "active_box_ocr_text": {
        "domain": "3D box OCR text",
        "externalObservable": "A source text layer supplies exact text inside the target boxes, or OCR is replaced by canonical text authority tied to a unit/order instruction.",
        "minimumArtifact": "source text extraction or authoritative transcript, not 3D box OCR alone",
        "acceptanceTest": "Exact O4/B4/G5/O5 text is source-backed and tied to R3 unit/order",
        "currentBlocker": "3D active-box OCR has 0/4 exact matches and 4/4 corrupted/misread target boxes.",
    },
    "loose_alignment": {
        "domain": "alignment tolerance",
        "externalObservable": "New source explains any shift beyond the current ±4px tolerance through provenance, scaling, crop, or physical registration.",
        "minimumArtifact": "source asset with measurable registration transform",
        "acceptanceTest": "Transform is natural, repeatable, improves source benchmarks, and passes R1-R5",
        "currentBlocker": "Future matches outside the current narrow tolerance are false positives unless the source explains the shift.",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def draw_sheet(summary: dict, rows: list[dict]) -> None:
    width, height = 1700, 980
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 92), fill=(24, 28, 35))
    draw.text((24, 20), "Source Packet Reopen Trigger Matrix", fill="white", font=title)
    draw.text(
        (24, 58),
        f"satisfied {summary['satisfiedTriggerCount']}/{summary['triggerCount']} | source R3 {summary['sourceBackedR3BridgeHitCount']} | fingerprint {summary['reopenTriggerFingerprint']}",
        fill=(230, 230, 230),
        font=tiny,
    )

    headers = ["visual class", "exact reopen trigger", "current blocker", "decision"]
    xs = [24, 300, 870, 1380]
    y = 124
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(70, 70, 70), font=small)
    y += 28

    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (236, 240, 246)
        draw.rectangle((18, y - 5, width - 18, y + 76), fill=fill)
        draw.text((xs[0], y), row["guardrailId"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[0], y + 18), row["domain"][:35], fill=(75, 75, 75), font=tiny)
        draw.text((xs[1], y), row["externalObservable"][:78], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y + 18), row["acceptanceTest"][:78], fill=(75, 75, 75), font=tiny)
        draw.text((xs[2], y), row["currentBlocker"][:70], fill=(90, 45, 35), font=tiny)
        draw.text((xs[2], y + 18), row["missingEvidence"][:70], fill=(90, 45, 35), font=tiny)
        draw.text((xs[3], y), row["decision"], fill=(120, 25, 25), font=tiny)
        draw.text((xs[3], y + 18), row["minimumArtifact"][:38], fill=(75, 75, 75), font=tiny)
        y += 86

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    reopen = load_json(INPUTS["source_reopen_requirements"])
    future = load_json(INPUTS["future_source_validation_packet"])
    handoff = load_json(INPUTS["source_packet_handoff_integrity_matrix"])
    guardrail = load_json(INPUTS["source_packet_false_positive_guardrail"])
    r3_bridge = load_json(INPUTS["source_packet_r3_bridge_audit"])
    color_profile = load_json(INPUTS["source_packet_color_profile_manifest"])
    frame_norm = load_json(INPUTS["source_packet_frame_normalized_geometry"])
    residual = load_json(INPUTS["source_packet_repaired_p78_frame_residual"])
    leakage = load_json(INPUTS["source_packet_repaired_frame_expansion_leakage"])

    r_gates = [gate.get("id") for gate in reopen.get("reopenGates", [])]
    c_conditions = [row.get("condition") for row in future.get("minimumReopenConditions", [])]
    source_r3 = r3_bridge.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)

    rows = []
    for guard in guardrail.get("guardrailRows", []):
        gid = guard.get("id")
        blueprint = TRIGGER_BLUEPRINTS[gid]
        rows.append(
            {
                "guardrailId": gid,
                "domain": blueprint["domain"],
                "temptingMatch": guard.get("temptingMatch"),
                "controlledBy": guard.get("controlledBy"),
                "requiredToReopen": guard.get("requiredToReopen", []),
                "externalObservable": blueprint["externalObservable"],
                "minimumArtifact": blueprint["minimumArtifact"],
                "acceptanceTest": blueprint["acceptanceTest"],
                "currentBlocker": blueprint["currentBlocker"],
                "missingEvidence": "R3 source-backed unit/order absent; R1-R5 not satisfied by current scan/local derivatives.",
                "r1r5Required": r_gates,
                "cConditionsTouched": c_conditions,
                "triggerSatisfiedNow": False,
                "decision": "wait_for_new_source_or_clue",
            }
        )

    summary = {
        "triggerCount": len(rows),
        "satisfiedTriggerCount": sum(1 for row in rows if row["triggerSatisfiedNow"]),
        "blockedTriggerCount": sum(1 for row in rows if not row["triggerSatisfiedNow"]),
        "r1r5GateCount": len(r_gates),
        "minimumConditionCount": len(c_conditions),
        "sourceBackedR3BridgeHitCount": source_r3,
        "derivedCorrectionBridgeWindowCount": r3_bridge.get("summary", {}).get(
            "derivedCorrectionBridgeWindowCount"
        ),
        "generatedUnitOrderPhraseCount": r3_bridge.get("summary", {}).get(
            "generatedUnitOrderPhraseCount"
        ),
        "guardrailStillBlockedCount": r3_bridge.get("summary", {}).get(
            "guardrailStillBlockedCount"
        ),
        "activeVisualStateOrder": guardrail.get("summary", {}).get("activeVisualStateOrder"),
        "activePageLines": guardrail.get("summary", {}).get("activePageLines"),
        "activeCorridorIndexes": guardrail.get("summary", {}).get("activeCorridorIndexes"),
        "handoffSelectorUnlockedCount": handoff.get("summary", {}).get(
            "selectorUnlockedCount"
        ),
        "handoffExtractionReadyGateCount": handoff.get("summary", {}).get(
            "extractionReadyGateCount"
        ),
        "colorProfileControlStateStream": color_profile.get("summary", {}).get(
            "overdoseControlClassifiedStateStream"
        ),
        "frameFullInsideActiveCount": frame_norm.get("summary", {}).get(
            "c9ActiveFullInsideCount"
        ),
        "residualMaxFullInsideActiveCount": residual.get("summary", {}).get(
            "maxFullInsideCount"
        ),
        "fullCoverLeakageWords": leakage.get("summary", {}).get(
            "fullCoverMinLineContextWordCount"
        ),
        "fullCoverLeakageNonTargetWords": leakage.get("summary", {}).get(
            "fullCoverMinLineContextNonTargetWordCount"
        ),
    }
    summary["reopenTriggerFingerprint"] = (
        f"triggers={summary['triggerCount']}"
        f"|satisfied={summary['satisfiedTriggerCount']}"
        f"|sourceR3={summary['sourceBackedR3BridgeHitCount']}"
        f"|states={summary['activeVisualStateOrder']}"
        f"|lines={str(summary['activePageLines']).replace(' ', '-')}"
        f"|corr={str(summary['activeCorridorIndexes']).replace(' ', '-')}"
        f"|guardrailsBlocked={summary['guardrailStillBlockedCount']}"
        f"|selectors={summary['handoffSelectorUnlockedCount']}"
    )

    decision = {
        "sourcePacketReopenTriggerMatrix": "no_current_reopen_trigger_satisfied",
        "reason": "Every visually tempting path now has an explicit source/provenance trigger, but none is satisfied by the current scan, local text layers, generated reports, or local source derivatives.",
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet reopen-trigger matrix; no OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "r1r5Gates": reopen.get("reopenGates", []),
        "minimumReopenConditions": future.get("minimumReopenConditions", []),
        "triggerRows": rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Use this matrix when a new source/photo/original export/clue arrives: score the observed source change against the exact trigger row before any selector or key work resumes.",
    }

    draw_sheet(summary, rows)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Reopen Trigger Matrix",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scope: {result['scope']}",
        f"- Decision: `{decision['sourcePacketReopenTriggerMatrix']}`",
        f"- Trigger count: `{summary['triggerCount']}`",
        f"- Satisfied now: `{summary['satisfiedTriggerCount']}`",
        f"- Source-backed R3 bridge hits: `{summary['sourceBackedR3BridgeHitCount']}`",
        f"- Guardrails still blocked: `{summary['guardrailStillBlockedCount']}`",
        f"- Active order/state: lines `{summary['activePageLines']}`, corridors `{summary['activeCorridorIndexes']}`, state `{summary['activeVisualStateOrder']}`",
        f"- Reopen trigger fingerprint: `{summary['reopenTriggerFingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Trigger Rows",
        "",
        "| guardrail | domain | exact external/source trigger | current blocker | decision |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['guardrailId']}` | {row['domain']} | {row['externalObservable']} | {row['currentBlocker']} | `{row['decision']}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Current local evidence supplies strong target-location and source-comparison benchmarks, not extraction permission.",
            "- The reopen condition is now concrete for each tempting visual mechanism: a distinct source/provenance artifact must add the missing R3 wording or materially explain the geometry while passing R1-R5.",
            "- Generated report prose, correction-report assessment text, and visual matches alone remain blocked.",
            "",
            "## Next Move",
            "",
            result["nextMove"],
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("reopenTriggerFingerprint:", summary["reopenTriggerFingerprint"])
    print("satisfiedTriggerCount:", summary["satisfiedTriggerCount"])


if __name__ == "__main__":
    main()
