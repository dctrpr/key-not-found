#!/usr/bin/env python3
"""Audit false-positive source-match modes for the current handoff stack.

This bounded pass turns the source handoff matrix into practical rejection
rules for future source comparisons. It identifies visually tempting match
classes that are already controlled or ambiguous: color-only YKKY/OBBO,
C9/OVERDOSE frame matches, repaired p78 contacts, bold/highlight witnesses,
native unrotated order, and 3D OCR text.

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
OUT = ROOT / "analysis_outputs/source_audit/source_packet_false_positive_guardrail"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_false_positive_guardrail.json"
OUT_MD = OUT / "source_packet_false_positive_guardrail.md"
OUT_SHEET = OUT / "source_packet_false_positive_guardrail_sheet.jpg"

REPORTS = {
    "handoff": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.json",
    "order_trap": ROOT
    / "analysis_outputs/source_audit/page76_active_order_orientation_trap/"
    "page76_active_order_orientation_trap.json",
    "yk_sync": ROOT
    / "analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/"
    "source_packet_yk_frame_benchmark_sync.json",
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


def guardrail(
    guardrail_id: str,
    tempting_match: str,
    controlled_by: str,
    reject_reason: str,
    required_to_reopen: list[str],
    severity: str = "hard_reject_without_r3",
) -> dict[str, Any]:
    return {
        "id": guardrail_id,
        "temptingMatch": tempting_match,
        "controlledBy": controlled_by,
        "rejectReason": reject_reason,
        "requiredToReopen": required_to_reopen,
        "severity": severity,
    }


def build_guardrails(data: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    order = data["order_trap"]["summary"]
    yk = data["yk_sync"]["summary"]
    frame = data["frame_normalized"]["summary"]
    color = data["color_profile"]["summary"]
    residual = data["repaired_residual"]["summary"]
    leakage = data["expansion_leakage"]["summary"]
    witness = data["format_witness"]["summary"]
    header = data["header_glyph"]["summary"]
    mirrored = data["mirrored_header"]["summary"]
    box_ocr = data["box_ocr"]["summary"]
    handoff = data["handoff"]["summary"]

    return [
        guardrail(
            "color_or_state_only",
            f"OBBO/YKKY color-state match: color palindrome={order['colorPatternIsPalindrome']}, visual palindrome={order['visualStatePatternIsPalindrome']}",
            f"full-page Y/K non-active controls={yk['fullPageYkNonActiveGroupCount']}; OVERDOSE controls={color['overdoseControlClassifiedStateStream']}",
            "Color/state alone cannot prove orientation or extraction order.",
            [
                "line order 22/25/27/32",
                "corridor order 4/7/9/14",
                "source-backed unit/order wording",
            ],
        ),
        guardrail(
            "native_unrotated_order",
            f"Native raw order {order['nativeUnnormalizedPageLines']} or {order['nativeUnnormalizedCorridorIndexes']}",
            f"readable/upright order {order['uprightPageLines']} / {order['uprightCorridorIndexes']}",
            "A visually matched native source that is not rotated 180 degrees reverses line/corridor order.",
            [
                "rotate native source images 180 degrees",
                "recover readable/upright active order",
                "reject raw-native reversed order as orientation error",
            ],
        ),
        guardrail(
            "c9_frame_only",
            f"C9/Y-K frame contains active targets {frame['c9ActiveFullInsideCount']}/4",
            "C9 is broad, horizontally mirror-invariant, and source-validation only",
            "Frame containment is a benchmark, not a selector.",
            [
                "source wording that names the frame as a reading boundary",
                "unit/order wording inside or tied to the frame",
                "controls must fail under the same rule",
            ],
        ),
        guardrail(
            "overdose_black_over",
            f"Active black OVER projections={header['activeBlackOverProjectionCount']}",
            f"p75 control OVER projections={header['p75ControlOverProjectionCount']}; mirrored p75 matches active={mirrored['p75ControlMatchesActiveBlackCount']}/{mirrored['variantCount']}",
            "OVER/REVO/DOSE-style slot matches are controlled by p75 and have no instruction wording.",
            [
                "raw/source instruction tying OVERDOSE glyph slots to active boxes",
                "control pages must not reproduce the same slot stream",
                "explicit unit/order extraction wording",
            ],
        ),
        guardrail(
            "p78_contact_or_dx_repair",
            f"repaired p78 max partial={residual['maxPartialHitCount']}/4; max full={residual['maxFullInsideCount']}/4",
            f"B4/O4 need touch expansions {residual['minimumRepairedB4TouchLeftExpansionPx']}/{residual['minimumRepairedO4TouchTopExpansionPx']} px",
            "dx repair improves residual contact but does not cover the active quartet.",
            [
                "source-backed reason for dx repair",
                "all four active boxes inside without context-band leakage",
                "unit/order wording",
            ],
        ),
        guardrail(
            "p78_full_cover_leakage",
            f"full-cover repair spans {leakage['fullCoverMinLineContextWordCount']} words",
            f"non-target words={leakage['fullCoverMinLineContextNonTargetWordCount']}; hard hits={leakage['fullCoverHardInstructionHitCount']}",
            "Forcing coverage takes the whole lower-corridor context band.",
            [
                "new source must avoid L22-L32 context-band leakage",
                "new source must isolate target units",
                "hard instruction wording must be present",
            ],
        ),
        guardrail(
            "bold_or_annotation_only",
            f"format pass={witness['formatAuthorityPassCount']}; line-bold exact={witness['lineLevelExactBoldMatchCount']}/4",
            f"witness conflicts={witness['witnessConflictCount']}; Markdown/notes are witness layers",
            "Bold/highlight witnesses validate formatting but do not supply a unit/order selector.",
            [
                "DOCM/high-res/crop-pack agreement",
                "source-backed unit/order wording",
                "do not rely on Markdown bold or annotated notes alone",
            ],
        ),
        guardrail(
            "active_box_ocr_text",
            f"active box exact OCR matches={box_ocr['exactBoxMatchCount']}/4",
            f"corrupted/misread boxes={box_ocr['corruptedOrMisreadBoxCount']}/4; usable={box_ocr['usableForTextExtraction']}",
            "3D map OCR inside target boxes is not text authority.",
            [
                "use canonical plain text + DOCM text + Markdown transcript",
                "use 3D OCR only as geometry witness",
                "do not extract key text from corrupted target-box OCR",
            ],
        ),
        guardrail(
            "loose_alignment",
            f"common shift tolerance={handoff['commonShiftTolerancePx']} px",
            "alignment first pad failure is already below loose visual matching",
            "A future source match that only works outside the current narrow tolerance is a false positive unless explained.",
            [
                "explain any shift larger than current tolerance",
                "preserve line/corridor order and visual state",
                "pass all R1-R5 source-reopen gates",
            ],
        ),
    ]


def draw_sheet(result: dict[str, Any]) -> None:
    width = 1460
    height = 860
    sheet = Image.new("RGB", (width, height), (13, 16, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((28, 22), "Source Packet False-Positive Guardrail", fill=(242, 246, 250), font=title)
    draw.text(
        (28, 60),
        "Tempting visual matches that remain invalid without source-backed unit/order wording.",
        fill=(184, 194, 205),
        font=normal,
    )

    x = 28
    y = 120
    row_h = 74
    col_id = 250
    col_match = 365
    col_control = 380
    col_reason = 380
    draw.text((x, y - 28), "Guardrail", fill=(240, 244, 248), font=small)
    draw.text((x + col_id, y - 28), "Tempting match", fill=(240, 244, 248), font=small)
    draw.text((x + col_id + col_match, y - 28), "Control / ambiguity", fill=(240, 244, 248), font=small)
    draw.text((x + col_id + col_match + col_control, y - 28), "Reject reason", fill=(240, 244, 248), font=small)

    for guard in result["guardrailRows"]:
        color = (255, 183, 86)
        draw.rounded_rectangle([x, y, width - 28, y + row_h - 10], radius=5, fill=(24, 29, 36), outline=(50, 60, 72))
        draw.text((x + 12, y + 12), guard["id"][:26], fill=color, font=mono)
        draw.text((x + col_id, y + 12), guard["temptingMatch"][:48], fill=(226, 232, 240), font=small)
        draw.text((x + col_id, y + 34), guard["temptingMatch"][48:96], fill=(156, 166, 176), font=small)
        draw.text((x + col_id + col_match, y + 12), guard["controlledBy"][:52], fill=(226, 232, 240), font=small)
        draw.text((x + col_id + col_match, y + 34), guard["controlledBy"][52:104], fill=(156, 166, 176), font=small)
        draw.text((x + col_id + col_match + col_control, y + 12), guard["rejectReason"][:54], fill=(226, 232, 240), font=small)
        draw.text((x + col_id + col_match + col_control, y + 34), guard["rejectReason"][54:108], fill=(156, 166, 176), font=small)
        y += row_h

    summary_y = height - 86
    draw.text((28, summary_y), f"Fingerprint: {result['summary']['falsePositiveGuardrailFingerprint']}", fill=(226, 232, 240), font=mono)
    draw.text(
        (28, summary_y + 30),
        f"Guardrails: {result['summary']['guardrailCount']}  Hard rejects without R3: {result['summary']['hardRejectWithoutR3Count']}  Selector unlocks: {result['summary']['selectorUnlockedCount']}",
        fill=(226, 232, 240),
        font=mono,
    )
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    data = {name: load_json(path) for name, path in REPORTS.items()}
    guardrails = build_guardrails(data)
    hard_rejects = [row for row in guardrails if row["severity"] == "hard_reject_without_r3"]
    required_terms = sorted({item for row in guardrails for item in row["requiredToReopen"]})
    active_state = data["handoff"]["summary"]["activeVisualStateOrder"]
    active_lines = data["handoff"]["summary"]["activePageLines"]
    active_corridors = data["handoff"]["summary"]["activeCorridorIndexes"]
    fingerprint = (
        f"guardrails={len(guardrails)}|hardReject={len(hard_rejects)}|"
        f"states={active_state}|lines={active_lines.replace(' ', '-')}|"
        f"corr={active_corridors.replace(' ', '-')}|"
        f"selectorUnlocks=0|requiresR3=1"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "source-packet false-positive guardrail audit; no OCR, extraction, key derivation, hashing, "
            "seed/WIF/address checks, BIP39 checks, or broad candidate generation"
        ),
        "inputs": {name: rel(path) for name, path in REPORTS.items()},
        "guardrailRows": guardrails,
        "summary": {
            "guardrailCount": len(guardrails),
            "hardRejectWithoutR3Count": len(hard_rejects),
            "selectorUnlockedCount": 0,
            "activeVisualStateOrder": active_state,
            "activePageLines": active_lines,
            "activeCorridorIndexes": active_corridors,
            "requiredToReopenUniqueCount": len(required_terms),
            "requiredToReopenUnique": required_terms,
            "falsePositiveGuardrailFingerprint": fingerprint,
            "selectorUnlocked": False,
        },
        "decision": {
            "sourcePacketFalsePositiveGuardrail": "reject-visual-only-matches",
            "reason": (
                "The current stack has several visually tempting matches, but each is already controlled, ambiguous, "
                "or context-leaky. Future source comparisons must not pass on color/frame/OVERDOSE/bold/partial-contact "
                "signals alone; they need the exact active order plus source-backed R3 unit/order wording."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Use these guardrails with the handoff integrity matrix when reviewing any new source asset. "
            "Do not reopen extraction for visual-only matches."
        ),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet False-Positive Guardrail",
        "",
        "Scope: identify visually tempting future source-match classes that must be rejected without source-backed unit/order wording. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Guardrail count: `{result['summary']['guardrailCount']}`",
        f"- Hard rejects without R3: `{result['summary']['hardRejectWithoutR3Count']}`",
        f"- Selector unlocks: `{result['summary']['selectorUnlockedCount']}`",
        f"- Active visual-state order: `{active_state}`",
        f"- Active page lines: `{active_lines}`",
        f"- Active corridor indexes: `{active_corridors}`",
        f"- False-positive guardrail fingerprint: `{fingerprint}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## Guardrail Rows",
        "",
        "| id | tempting match | controlled by | reject reason | required to reopen |",
        "|---|---|---|---|---|",
    ]
    for guard in guardrails:
        lines.append(
            f"| `{guard['id']}` | {guard['temptingMatch']} | {guard['controlledBy']} | {guard['rejectReason']} | {'; '.join(guard['requiredToReopen'])} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Reject visual-only matches for future source comparison.",
            "- Color/state, native raw order, C9 frame containment, OVERDOSE slot spelling, repaired p78 contacts, bold/highlight witness state, and 3D target-box OCR each have an existing control or ambiguity.",
            "- A future source can reopen extraction only if it preserves the active order/visual state and supplies source-backed R3 unit/order wording.",
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
    print("falsePositiveGuardrailFingerprint:", fingerprint)
    print("selectorUnlocked:", result["summary"]["selectorUnlocked"])


if __name__ == "__main__":
    main()
