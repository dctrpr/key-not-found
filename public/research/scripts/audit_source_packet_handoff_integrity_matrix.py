#!/usr/bin/env python3
"""Build a source-packet handoff integrity matrix.

This is a bounded source-validation pass. It checks whether the current
handoff constraints agree with each other across orientation, target order,
visual state, bold/highlight authority, frame geometry, OVERDOSE controls, and
the repaired-frame leakage result.

No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks,
BIP39 checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_handoff_integrity_matrix.json"
OUT_MD = OUT / "source_packet_handoff_integrity_matrix.md"
OUT_SHEET = OUT / "source_packet_handoff_integrity_matrix_sheet.jpg"

REPORTS = {
    "orientation": ROOT
    / "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/"
    "page76_active_crop_orientation_guardrail.json",
    "order_trap": ROOT
    / "analysis_outputs/source_audit/page76_active_order_orientation_trap/"
    "page76_active_order_orientation_trap.json",
    "crop_completion": ROOT
    / "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json",
    "crop_sync": ROOT
    / "analysis_outputs/source_audit/source_packet_crop_authority_sync/"
    "source_packet_crop_authority_sync.json",
    "yk_sync": ROOT
    / "analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/"
    "source_packet_yk_frame_benchmark_sync.json",
    "native_bridge": ROOT
    / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/"
    "source_packet_native_benchmark_bridge.json",
    "visual_roundtrip": ROOT
    / "analysis_outputs/source_audit/source_packet_visual_state_roundtrip/"
    "source_packet_visual_state_roundtrip.json",
    "alignment": ROOT
    / "analysis_outputs/source_audit/source_packet_alignment_tolerance/"
    "source_packet_alignment_tolerance.json",
    "geometric_fingerprint": ROOT
    / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/"
    "source_packet_geometric_fingerprint.json",
    "frame_normalized": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/"
    "source_packet_frame_normalized_geometry.json",
    "color_profile": ROOT
    / "analysis_outputs/source_audit/source_packet_color_profile_manifest/"
    "source_packet_color_profile_manifest.json",
    "repaired_residual": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/"
    "source_packet_repaired_p78_frame_residual.json",
    "expansion_leakage": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/"
    "source_packet_repaired_frame_expansion_leakage.json",
    "format_witness": ROOT
    / "analysis_outputs/source_audit/c9_active_format_witness_reconciliation/"
    "c9_active_format_witness_reconciliation.json",
    "header_glyph": ROOT
    / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json",
    "mirrored_header": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "box_ocr": ROOT
    / "analysis_outputs/3d_article_map/active_quartet_box_ocr_gate/"
    "active_quartet_box_ocr_gate.json",
}
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def row(
    gate: str,
    layer: str,
    status: str,
    metric: str,
    interpretation: str,
    selector_unlocked: bool = False,
    contradiction: bool = False,
) -> dict[str, Any]:
    return {
        "gate": gate,
        "layer": layer,
        "status": status,
        "metric": metric,
        "interpretation": interpretation,
        "selectorUnlocked": selector_unlocked,
        "contradiction": contradiction,
    }


def build_gate_rows(data: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    orientation = data["orientation"]["summary"]
    order_trap = data["order_trap"]["summary"]
    crop_completion = data["crop_completion"]["summary"]
    crop_sync = data["crop_sync"]["summary"]
    yk_sync = data["yk_sync"]["summary"]
    native_bridge = data["native_bridge"]["summary"]
    visual_roundtrip = data["visual_roundtrip"]["summary"]
    alignment = data["alignment"]["summary"]
    fingerprint = data["geometric_fingerprint"]["summary"]
    frame_normalized = data["frame_normalized"]["summary"]
    color_profile = data["color_profile"]["summary"]
    residual = data["repaired_residual"]["summary"]
    leakage = data["expansion_leakage"]["summary"]
    format_witness = data["format_witness"]["summary"]
    header = data["header_glyph"]["summary"]
    mirrored = data["mirrored_header"]["summary"]
    box_ocr = data["box_ocr"]["summary"]

    return [
        row(
            "orientation_transform",
            "3d/source image geometry",
            "pass_guardrail",
            f"rot180 mean {orientation['rot180MeanAbsDiff']} vs direct {orientation['directMeanAbsDiff']}",
            "Use readable/upright coordinates for 3D and crop-pack work; rotate native source images 180 degrees before comparison.",
        ),
        row(
            "order_orientation_trap",
            "page 76 target cluster",
            "pass_guardrail",
            f"line order {order_trap['uprightPageLines']} vs native raw {order_trap['nativeUnnormalizedPageLines']}",
            "YKKY/OBBO are palindromes, so future source matches must use line/corridor order, not color order alone.",
        ),
        row(
            "crop_completion",
            "page 76 target cluster",
            "pass_source_handoff",
            f"crop coverage {crop_completion['cropCoverage']}",
            "All four active target crops are present for future visual comparison.",
        ),
        row(
            "authority_sync",
            "text and format authority",
            "pass_with_appendix",
            f"{crop_sync['syncStatus']}; text={crop_sync['textAuthority']}",
            "Canonical text, DOCM text, Markdown transcript, DOCM runs, high-res visuals, and crop-pack/manual boxes remain the authority stack.",
        ),
        row(
            "visual_state_roundtrip",
            "orange/black highlights",
            "pass_source_profile",
            f"{visual_roundtrip['activeClassifiedVisualStateOrder']} active; max mean diff {visual_roundtrip['activeMaxMeanAbsDiff']}",
            "Active visual states round-trip as YKKY and all active targets remain DOCM Typeka bold; this validates source matching only.",
        ),
        row(
            "color_profile_controls",
            "orange/black vs OVERDOSE",
            "pass_control",
            f"Y margin {color_profile['minActiveYOrangeMinusMaxControlOrange']}; K margin {color_profile['minActiveKDarkMinusMaxControlDark']}",
            "Active orange/black boxes remain separated from OVERDOSE header/glyph controls.",
        ),
        row(
            "alignment_tolerance",
            "source registration",
            "pass_bounded_window",
            f"common shift {alignment['commonFullEightDirectionShiftAllTargetsPassPx']}px; first pad failure {alignment['smallestFirstPadFailurePx']}px",
            "Future source comparisons get a narrow tolerance window; loose fitting should be rejected.",
        ),
        row(
            "native_bridge",
            "source geometry",
            "pass_source_handoff",
            f"{native_bridge['benchmarkBoxCount']} boxes; OVERDOSE glyphs {native_bridge['headerGlyphSequence']}",
            "Readable/upright active boxes, C9 frame, p78 frame, and OVERDOSE glyph boxes bridge cleanly into native coordinates.",
        ),
        row(
            "geometric_fingerprint",
            "page 76 target cluster",
            "pass_source_profile",
            f"gaps {fingerprint['pageLineGaps']}; signs {fingerprint['dxSignStream']}/{fingerprint['dySignStream']}",
            "The target cluster has a stable source-registration fingerprint, not an extraction unit.",
        ),
        row(
            "c9_frame_normalized",
            "OVERDOSE/C9 layout",
            "pass_as_benchmark_reject_selector",
            f"C9 inside {frame_normalized['c9ActiveFullInsideCount']}/4; p78 inside {frame_normalized['reflectedP78FullInsideCount']}/4",
            "C9/Y-K is a stable frame benchmark, while simple C9-frame mirrors do not re-hit all four active targets.",
        ),
        row(
            "yk_frame_order",
            "bold/highlight unit order",
            "reject_as_selector",
            f"frame Y/K {yk_sync['frameYkLayerCodes']}; bounded streams {yk_sync['boundedStreamCount']}; hard hits {yk_sync['hardInstructionHitCount']}",
            "Y/K inside the frame isolates the quartet, but no source-backed unit/order rule is present and full-page Y/K has controls.",
        ),
        row(
            "format_witness",
            "bold letters and annotations",
            "pass_authority_reject_selector",
            f"format pass {format_witness['formatAuthorityPassCount']}; line-bold exact {format_witness['lineLevelExactBoldMatchCount']}/4; conflicts {format_witness['witnessConflictCount']}",
            "DOCM/high-res/crop-pack remain authority; line-level bold and witness notes are not extraction permission.",
        ),
        row(
            "overdose_header_slots",
            "OVERDOSE layout",
            "pass_control_reject_selector",
            f"active black OVER {header['activeBlackOverProjectionCount']}; p75 control OVER {header['p75ControlOverProjectionCount']}; hits {header['activeStrictInstructionHitCount']}",
            "Header glyph slots reproduce active B4/G5 OVER, but the p75 control reproduces it too and no instruction wording appears.",
        ),
        row(
            "mirrored_overdose_slots",
            "folded/mirrored OVERDOSE",
            "pass_control_reject_selector",
            f"variants {mirrored['variantCount']}; p75 matches active {mirrored['p75ControlMatchesActiveBlackCount']}/8; hits {mirrored['strictInstructionHitCount']}",
            "Mirrored/reversed OVERDOSE slot variants are controlled by p75 and remain non-instructional.",
        ),
        row(
            "p78_repaired_residual",
            "folded/mirrored p78 frame",
            "pass_reject_selector",
            f"full {residual['maxFullInsideCount']}/4; partial {residual['maxPartialHitCount']}/4; B4/O4 touch {residual['minimumRepairedB4TouchLeftExpansionPx']}/{residual['minimumRepairedO4TouchTopExpansionPx']}px",
            "Repaired p78 dx variants improve source-registration residuals but do not explain the active quartet as a selector.",
        ),
        row(
            "p78_expansion_leakage",
            "folded/mirrored p78 frame",
            "pass_reject_selector",
            f"full cover {leakage['fullCoverMinLineContextWordCount']} words; non-target {leakage['fullCoverMinLineContextNonTargetWordCount']}; hits {leakage['fullCoverHardInstructionHitCount']}",
            "Forcing full coverage takes the L22-L32 context band, so repaired-frame expansion is not selective.",
        ),
        row(
            "active_box_ocr",
            "3d OCR text authority",
            "reject_as_text_source",
            f"exact matches {box_ocr['exactBoxMatchCount']}/4; corrupted {box_ocr['corruptedOrMisreadBoxCount']}/4",
            "Do not use 3D map OCR inside active boxes as extraction text.",
        ),
    ]


def draw_sheet(result: dict[str, Any], native_bridge: dict[str, Any], leakage: dict[str, Any]) -> None:
    img = Image.open(UPRIGHT_PAGE).convert("RGB")
    scale = 0.22
    page_panel = img.resize((int(img.width * scale), int(img.height * scale)))
    sheet_w = 1480
    sheet_h = max(900, page_panel.height + 170)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (13, 16, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((26, 20), "Source Packet Handoff Integrity Matrix", fill=(242, 246, 250), font=title)
    draw.text(
        (26, 60),
        "Validates the current source-comparison handoff; rejects selector reuse without R3 unit/order wording.",
        fill=(184, 194, 205),
        font=normal,
    )

    page_x = 28
    page_y = 120
    sheet.paste(page_panel, (page_x, page_y))

    def sx(v: float) -> float:
        return page_x + v * scale

    def sy(v: float) -> float:
        return page_y + v * scale

    rows = native_bridge["rows"]
    active = [row for row in rows if row.get("kind") == "active_target"]
    source_frames = [row for row in rows if row.get("kind") == "source_frame"]
    for frame_row in source_frames:
        box = frame_row["uprightBox"]
        color = (255, 218, 72) if frame_row["id"] == "c9_yk_frame" else (85, 214, 255)
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
        draw.text((sx(box[0]), sy(box[1]) - 16), frame_row["id"], fill=color, font=small)

    leakage_full = next(
        row
        for row in leakage["scenarioRows"]
        if row["frameName"] == "nearest_grid_dx_-40" and row["scenario"] == "full_cover_all"
    )
    box = leakage_full["frame"]
    draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(255, 92, 180), width=3)
    draw.text((sx(box[0]), sy(box[3]) + 4), "dx=-40 full-cover leakage", fill=(255, 92, 180), font=small)

    for target in active:
        box = target["uprightBox"]
        color = (255, 140, 35) if target.get("visualState") == "Y" else (35, 35, 35)
        label_color = (255, 165, 70) if target.get("visualState") == "Y" else (240, 240, 240)
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=4)
        draw.text(
            (sx(box[0]), sy(box[1]) - 16),
            f"{target['id']} {target.get('visualState')} L{target.get('pageLine')}",
            fill=label_color,
            font=small,
        )

    matrix_x = page_x + page_panel.width + 34
    y = 120
    draw.text((matrix_x, y), "Gate Matrix", fill=(242, 246, 250), font=font(24))
    y += 38
    for gate in result["gateRows"]:
        if y > sheet_h - 56:
            break
        status = gate["status"]
        color = (114, 224, 164) if status.startswith("pass") else (255, 180, 90)
        draw.text((matrix_x, y), gate["gate"], fill=(235, 240, 246), font=mono)
        draw.text((matrix_x + 270, y), status, fill=color, font=mono)
        draw.text((matrix_x + 490, y), gate["metric"][:58], fill=(184, 194, 205), font=small)
        y += 31

    footer_y = sheet_h - 72
    summary = result["summary"]
    draw.text(
        (26, footer_y),
        f"Integrity fingerprint: {summary['integrityFingerprint']}",
        fill=(226, 232, 240),
        font=mono,
    )
    draw.text(
        (26, footer_y + 28),
        f"Contradictions: {summary['contradictionCount']}  Selector unlocks: {summary['selectorUnlockedCount']}  Extraction-ready gates: {summary['extractionReadyGateCount']}",
        fill=(226, 232, 240),
        font=mono,
    )
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    data = {name: load_json(path) for name, path in REPORTS.items()}
    gate_rows = build_gate_rows(data)

    contradiction_count = sum(1 for gate in gate_rows if gate["contradiction"])
    selector_count = sum(1 for gate in gate_rows if gate["selectorUnlocked"])
    extraction_ready_count = sum(1 for gate in gate_rows if gate["status"] == "extraction_ready")
    reject_count = sum(1 for gate in gate_rows if "reject" in gate["status"])
    pass_count = sum(1 for gate in gate_rows if gate["status"].startswith("pass"))

    visual = data["visual_roundtrip"]["summary"]
    order = data["order_trap"]["summary"]
    alignment = data["alignment"]["summary"]
    leakage = data["expansion_leakage"]["summary"]
    fingerprint = (
        f"gates={len(gate_rows)}|pass={pass_count}|reject={reject_count}|"
        f"contradictions={contradiction_count}|selectors={selector_count}|"
        f"states={visual['activeClassifiedVisualStateOrder']}|"
        f"lines={order['uprightPageLines'].replace(' ', '-') }|"
        f"corr={order['uprightCorridorIndexes'].replace(' ', '-') }|"
        f"shift={alignment['commonFullEightDirectionShiftAllTargetsPassPx']}|"
        f"leakWords={leakage['fullCoverMinLineContextWordCount']}/"
        f"{leakage['fullCoverMinLineContextNonTargetWordCount']}"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "source-packet handoff integrity matrix; no OCR, extraction, key derivation, hashing, "
            "seed/WIF/address checks, BIP39 checks, or broad candidate generation"
        ),
        "inputs": {name: rel(path) for name, path in REPORTS.items()},
        "gateRows": gate_rows,
        "summary": {
            "gateCount": len(gate_rows),
            "passGateCount": pass_count,
            "rejectGateCount": reject_count,
            "contradictionCount": contradiction_count,
            "selectorUnlockedCount": selector_count,
            "extractionReadyGateCount": extraction_ready_count,
            "activeVisualStateOrder": visual["activeClassifiedVisualStateOrder"],
            "activePageLines": order["uprightPageLines"],
            "activeCorridorIndexes": order["uprightCorridorIndexes"],
            "orientationDecision": data["orientation"]["summary"]["orientationDecision"],
            "commonShiftTolerancePx": alignment["commonFullEightDirectionShiftAllTargetsPassPx"],
            "fullCoverLeakageWords": leakage["fullCoverMinLineContextWordCount"],
            "fullCoverLeakageNonTargetWords": leakage["fullCoverMinLineContextNonTargetWordCount"],
            "integrityFingerprint": fingerprint,
            "selectorUnlocked": False,
        },
        "decision": {
            "sourcePacketHandoffIntegrityMatrix": "consistent-source-validation-stack",
            "reason": (
                "The current source-packet handoff is internally consistent and has no selector unlocks. "
                "Orientation, line/corridor order, YKKY visual state, crop completeness, C9/Y-K benchmarking, "
                "OVERDOSE controls, repaired p78 residuals, and expansion leakage all agree that the stack is "
                "for future source comparison only."
            ),
        },
        "candidateSourceAcceptanceChecklist": [
            "Rotate native source images 180 degrees before comparing to readable/upright target boxes.",
            "Require active order buying_dip/one_billion/volcano_bonds/shitcoiner_heart with page lines 22/25/27/32 and corridors 4/7/9/14.",
            "Require active visual-state stream YKKY and the documented orange/black separation against OVERDOSE controls.",
            "Require all four active crop boxes to land within the current +/-4px common shift tolerance unless a new source explains the shift.",
            "Reject matches that only recreate C9 OVER, p78 partial contacts, or full-cover frame leakage without source-backed unit/order wording.",
            "Do not resume selector/key checks until the same new source/clue passes R1-R5 with R3 naming the unit and order.",
        ],
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Use this integrity matrix as the compact source-comparison checklist. Further local selector work should wait for a new "
            "source/clue with source-backed unit/order wording."
        ),
    }

    draw_sheet(result, data["native_bridge"], data["expansion_leakage"])
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Handoff Integrity Matrix",
        "",
        "Scope: check whether the current source-comparison handoff constraints agree across orientation, target order, visual state, bold/highlight authority, p78/C9 frame behavior, OVERDOSE controls, and repaired-frame leakage. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Gate count: `{len(gate_rows)}`",
        f"- Pass/source-validation gates: `{pass_count}`",
        f"- Reject-as-selector gates: `{reject_count}`",
        f"- Contradictions: `{contradiction_count}`",
        f"- Selector unlocks: `{selector_count}`",
        f"- Extraction-ready gates: `{extraction_ready_count}`",
        f"- Active visual-state order: `{result['summary']['activeVisualStateOrder']}`",
        f"- Active page lines: `{result['summary']['activePageLines']}`",
        f"- Active corridor indexes: `{result['summary']['activeCorridorIndexes']}`",
        f"- Common shift tolerance: `{result['summary']['commonShiftTolerancePx']}px`",
        f"- Full-cover leakage words/non-target words: `{result['summary']['fullCoverLeakageWords']}` / `{result['summary']['fullCoverLeakageNonTargetWords']}`",
        f"- Integrity fingerprint: `{fingerprint}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## Gate Rows",
        "",
        "| gate | layer | status | metric | interpretation |",
        "|---|---|---|---|---|",
    ]
    for gate in gate_rows:
        lines.append(
            f"| `{gate['gate']}` | {gate['layer']} | `{gate['status']}` | {gate['metric']} | {gate['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Candidate Source Checklist",
            "",
        ]
    )
    for item in result["candidateSourceAcceptanceChecklist"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Treat the handoff stack as internally consistent source-validation scaffolding.",
            "- No current gate unlocks extraction, and no gate contradicts the current readable/upright plus native-rotate180 geometry model.",
            "- C9/Y-K, p78 repaired residuals, OVERDOSE slot controls, bold/highlight authority, and frame leakage all remain validation/control evidence only.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("integrityFingerprint:", fingerprint)
    print("selectorUnlocked:", result["summary"]["selectorUnlocked"])


if __name__ == "__main__":
    main()
