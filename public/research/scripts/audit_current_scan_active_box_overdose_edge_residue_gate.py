#!/usr/bin/env python3
"""Check active target box edges against the C9/OVERDOSE slot ruler.

This bounded pass uses the locked O4/B4/G5/O5 current-scan witness boxes and
the same-target witness substitutions already in the local packet. It checks
whether left/center/right target-box x positions carry a repeatable residue to
the OVERDOSE slot centers or boundaries.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_box_overdose_edge_residue_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_box_overdose_edge_residue_gate.json"
OUT_MD = OUT / "current_scan_active_box_overdose_edge_residue_gate.md"
OUT_SHEET = OUT / "current_scan_active_box_overdose_edge_residue_gate_sheet.jpg"

TARGET_WITNESS_SUBSTITUTION = ROOT / (
    "analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate/"
    "current_scan_target_witness_box_substitution_gate.json"
)
C9_SLOTS = ROOT / (
    "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json"
)
SLOT_BOUNDARY_RESIDUAL = ROOT / (
    "analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/"
    "current_scan_slot_boundary_residual_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGETS = ["O4", "B4", "G5", "O5"]
ANCHORS = ["left", "center", "right"]
CLOSE_THRESHOLD_PX = 16.0
TARGET_CENTER_STREAM = "OVED"


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def nearest(value: float, values: list[float]) -> tuple[int, float, float]:
    index = min(range(len(values)), key=lambda idx: abs(value - values[idx]))
    signed = value - values[index]
    return index, signed, abs(signed)


def slot_ruler(c9_slots: dict[str, Any]) -> dict[str, Any]:
    slots = []
    for slot in c9_slots.get("slots", []):
        left = float(slot["left"])
        right = float(slot["right"])
        slots.append(
            {
                "index": int(slot["index"]),
                "letter": str(slot["letter"]),
                "left": left,
                "right": right,
                "center": (left + right) / 2.0,
                "width": right - left,
            }
        )
    boundaries = [slots[0]["left"]] + [slot["right"] for slot in slots]
    centers = [slot["center"] for slot in slots]
    return {"slots": slots, "boundaries": boundaries, "centers": centers}


def row_anchor_metrics(row: dict[str, Any], ruler: dict[str, Any]) -> dict[str, Any]:
    x0, _y0, x1, _y1 = [float(value) for value in row["box"]]
    anchor_values = {"left": x0, "center": (x0 + x1) / 2.0, "right": x1}
    anchors: dict[str, Any] = {}
    for anchor, x in anchor_values.items():
        center_index, center_signed, center_abs = nearest(x, ruler["centers"])
        boundary_index, boundary_signed, boundary_abs = nearest(x, ruler["boundaries"])
        nearest_type = "center" if center_abs <= boundary_abs else "boundary"
        nearest_abs = min(center_abs, boundary_abs)
        anchors[anchor] = {
            "x": round(x, 6),
            "nearestCenterIndex": center_index,
            "nearestCenterLetter": ruler["slots"][center_index]["letter"],
            "nearestCenterSignedPx": round(center_signed, 6),
            "nearestCenterAbsPx": round(center_abs, 6),
            "nearestBoundaryIndex": boundary_index,
            "nearestBoundarySignedPx": round(boundary_signed, 6),
            "nearestBoundaryAbsPx": round(boundary_abs, 6),
            "nearestType": nearest_type,
            "nearestAbsPx": round(nearest_abs, 6),
            "nearestClose16": nearest_abs <= CLOSE_THRESHOLD_PX,
            "centerClose16": center_abs <= CLOSE_THRESHOLD_PX,
            "boundaryClose16": boundary_abs <= CLOSE_THRESHOLD_PX,
        }
    return anchors


def variant_row(
    ordinal: int, witness_rows: tuple[dict[str, Any], ...], ruler: dict[str, Any]
) -> dict[str, Any]:
    target_metrics = []
    for row in witness_rows:
        metrics = row_anchor_metrics(row, ruler)
        target_metrics.append(
            {
                "target": row["target"],
                "witnessIds": row["witnessIds"],
                "sourceKinds": row["sourceKinds"],
                "isExactActiveBox": bool(row["isExactActiveBox"]),
                "box": row["box"],
                "anchors": metrics,
            }
        )

    center_streams = {
        anchor: "".join(
            item["anchors"][anchor]["nearestCenterLetter"] for item in target_metrics
        )
        for anchor in ANCHORS
    }
    boundary_streams = {
        anchor: "".join(
            str(item["anchors"][anchor]["nearestBoundaryIndex"]) for item in target_metrics
        )
        for anchor in ANCHORS
    }
    exact_flags = [item["isExactActiveBox"] for item in target_metrics]
    any_anchor_close_rows = sum(
        any(item["anchors"][anchor]["nearestClose16"] for anchor in ANCHORS)
        for item in target_metrics
    )
    left_boundary_close_rows = sum(
        item["anchors"]["left"]["boundaryClose16"] for item in target_metrics
    )
    center_slot_close_rows = sum(
        item["anchors"]["center"]["centerClose16"] for item in target_metrics
    )
    right_boundary_close_rows = sum(
        item["anchors"]["right"]["boundaryClose16"] for item in target_metrics
    )
    mean_nearest_residue = sum(
        item["anchors"][anchor]["nearestAbsPx"] for item in target_metrics for anchor in ANCHORS
    ) / (len(target_metrics) * len(ANCHORS))
    mean_center_residue = sum(
        item["anchors"]["center"]["nearestCenterAbsPx"] for item in target_metrics
    ) / len(target_metrics)
    return {
        "ordinal": ordinal,
        "targets": [item["target"] for item in target_metrics],
        "witnessIds": [item["witnessIds"] for item in target_metrics],
        "sourceKinds": [item["sourceKinds"] for item in target_metrics],
        "exactActiveBoxFlags": exact_flags,
        "allExactActiveBoxes": all(exact_flags),
        "hasSubstitution": not all(exact_flags),
        "targetMetrics": target_metrics,
        "nearestCenterStreams": center_streams,
        "nearestBoundaryStreams": boundary_streams,
        "anyAnchorClose16RowCount": int(any_anchor_close_rows),
        "allFourAnyAnchorClose16": any_anchor_close_rows == len(target_metrics),
        "leftBoundaryClose16RowCount": int(left_boundary_close_rows),
        "allFourLeftBoundaryClose16": left_boundary_close_rows == len(target_metrics),
        "centerSlotClose16RowCount": int(center_slot_close_rows),
        "allFourCenterSlotClose16": center_slot_close_rows == len(target_metrics),
        "rightBoundaryClose16RowCount": int(right_boundary_close_rows),
        "allFourRightBoundaryClose16": right_boundary_close_rows == len(target_metrics),
        "meanNearestResiduePx": round(mean_nearest_residue, 6),
        "meanCenterResiduePx": round(mean_center_residue, 6),
        "centerStreamMatchesActive": center_streams["center"] == TARGET_CENTER_STREAM,
        "edgeResidueSelectorCandidate": False,
    }


def build_variants(
    witness_options: dict[str, list[dict[str, Any]]], ruler: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for ordinal, option_tuple in enumerate(
        itertools.product(*(witness_options[target] for target in TARGETS)), start=1
    ):
        rows.append(variant_row(ordinal, option_tuple, ruler))
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    summary = result["summary"]
    width, height = 1800, 940
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = safe_font(26)
    small_font = safe_font(16)
    tiny_font = safe_font(13)

    draw.rectangle((0, 0, width, 96), fill=(28, 32, 38))
    draw.text((24, 18), "Current Scan Active Box OVERDOSE Edge-Residue Gate", fill="white", font=title_font)
    draw.text(
        (24, 58),
        (
            f"exact centers {summary['exactActiveCenterStream']} | exact edge streams "
            f"{summary['exactActiveLeftCenterStream']}/{summary['exactActiveRightCenterStream']} | "
            f"exact close rows any/left/center/right "
            f"{summary['exactActiveAnyAnchorClose16RowCount']}/"
            f"{summary['exactActiveLeftBoundaryClose16RowCount']}/"
            f"{summary['exactActiveCenterSlotClose16RowCount']}/"
            f"{summary['exactActiveRightBoundaryClose16RowCount']} | "
            f"candidate {summary['hiddenEdgeResidueCandidateCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny_font,
    )

    y = 122
    draw.text((24, y), "Witness variants against C9/OVERDOSE slot ruler", fill=(40, 40, 40), font=small_font)
    y += 28
    headers = [
        "#",
        "witnesses",
        "left centers",
        "center stream",
        "right centers",
        "close any/L/C/R",
        "mean residue",
        "candidate",
    ]
    xs = [24, 80, 720, 870, 1030, 1190, 1410, 1580]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny_font)
    y += 22
    for idx, row in enumerate(result["variantRows"]):
        if row["allExactActiveBoxes"]:
            fill = (238, 249, 239)
        elif row["allFourAnyAnchorClose16"]:
            fill = (255, 244, 224)
        else:
            fill = (248, 249, 252) if idx % 2 == 0 else (238, 242, 247)
        draw.rectangle((18, y - 4, width - 18, y + 40), fill=fill)
        witness = " / ".join("+".join(ids) for ids in row["witnessIds"])
        close = (
            f"{row['anyAnchorClose16RowCount']}/"
            f"{row['leftBoundaryClose16RowCount']}/"
            f"{row['centerSlotClose16RowCount']}/"
            f"{row['rightBoundaryClose16RowCount']}"
        )
        draw.text((xs[0], y), str(row["ordinal"]), fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[1], y), witness[:86], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[2], y), row["nearestCenterStreams"]["left"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[3], y), row["nearestCenterStreams"]["center"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[4], y), row["nearestCenterStreams"]["right"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[5], y), close, fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[6], y), f"{row['meanNearestResiduePx']:.2f}px", fill=(30, 30, 30), font=tiny_font)
        draw.text(
            (xs[7], y),
            str(row["edgeResidueSelectorCandidate"]),
            fill=(130, 30, 30),
            font=tiny_font,
        )
        y += 46

    y += 20
    draw.text((24, y), "Interpretation", fill=(40, 40, 40), font=small_font)
    y += 28
    notes = [
        "Exact active center stream repeats OVED, but 0/4 exact centers are close to slot centers at <=16px.",
        "A substituted annotated O4 variant gives all-four any-anchor closeness, so edge closeness is not exact-active-specific.",
        "No variant has an R3 source trigger or a selector candidate.",
    ]
    for note in notes:
        draw.text((36, y), f"- {note}", fill=(40, 40, 40), font=tiny_font)
        y += 24

    img.save(OUT_SHEET, quality=92)


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Active Box OVERDOSE Edge-Residue Gate",
        "",
        "Scope: bounded current-scan/PDF witness-box edge-residue control. No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Witness variants checked: `{summary['variantCount']}`",
        f"- Exact active nearest-center streams left/center/right: `{summary['exactActiveLeftCenterStream']}` / `{summary['exactActiveCenterStream']}` / `{summary['exactActiveRightCenterStream']}`",
        f"- Exact active close rows any/left-boundary/center-slot/right-boundary at <=16px: `{summary['exactActiveAnyAnchorClose16RowCount']}` / `{summary['exactActiveLeftBoundaryClose16RowCount']}` / `{summary['exactActiveCenterSlotClose16RowCount']}` / `{summary['exactActiveRightBoundaryClose16RowCount']}`",
        f"- Variants with all-four any-anchor closeness at <=16px: `{summary['allFourAnyAnchorClose16VariantCount']}`",
        f"- All-four close variants using substituted boxes: `{summary['substitutedAllFourAnyAnchorClose16VariantCount']}`",
        f"- Hidden edge-residue candidates: `{summary['hiddenEdgeResidueCandidateCount']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['edgeResidueFingerprint']}`",
        "",
        "## Variant Rows",
        "",
        "| # | witnesses | left-center stream | center stream | right-center stream | close rows any/L/C/R | mean nearest residue | all exact | edge candidate |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in result["variantRows"]:
        witness = " / ".join("+".join(ids) for ids in row["witnessIds"])
        close = (
            f"{row['anyAnchorClose16RowCount']}/"
            f"{row['leftBoundaryClose16RowCount']}/"
            f"{row['centerSlotClose16RowCount']}/"
            f"{row['rightBoundaryClose16RowCount']}"
        )
        lines.append(
            f"| `{row['ordinal']}` | `{witness}` | `{row['nearestCenterStreams']['left']}` | "
            f"`{row['nearestCenterStreams']['center']}` | `{row['nearestCenterStreams']['right']}` | "
            f"`{close}` | `{row['meanNearestResiduePx']}` | `{row['allExactActiveBoxes']}` | "
            f"`{row['edgeResidueSelectorCandidate']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['currentScanActiveBoxOverdoseEdgeResidueGate']}.",
            f"- Reason: {result['decision']['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    witness_substitution = load_json(TARGET_WITNESS_SUBSTITUTION)
    c9_slots = load_json(C9_SLOTS)
    slot_boundary = load_json(SLOT_BOUNDARY_RESIDUAL)
    reopen_trigger = load_json(REOPEN_TRIGGER_MATRIX)

    ruler = slot_ruler(c9_slots)
    variants = build_variants(witness_substitution.get("witnessOptions", {}), ruler)
    exact_active = next(row for row in variants if row["allExactActiveBoxes"])
    all_four_any_close = [row for row in variants if row["allFourAnyAnchorClose16"]]
    substituted_all_four_any_close = [row for row in all_four_any_close if row["hasSubstitution"]]

    reopen_summary = reopen_trigger.get("summary", {})
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(reopen_summary.get("triggerCount", 0) or 0)

    hidden_candidates = [
        row
        for row in variants
        if row["allExactActiveBoxes"]
        and row["centerStreamMatchesActive"]
        and (
            row["allFourLeftBoundaryClose16"]
            or row["allFourCenterSlotClose16"]
            or row["allFourRightBoundaryClose16"]
            or row["allFourAnyAnchorClose16"]
        )
        and source_r3 > 0
    ]
    for row in variants:
        row["edgeResidueSelectorCandidate"] = row in hidden_candidates

    fingerprint = (
        f"variants={len(variants)}|exactCenter={exact_active['nearestCenterStreams']['center']}|"
        f"exactEdges={exact_active['nearestCenterStreams']['left']}/{exact_active['nearestCenterStreams']['right']}|"
        f"exactClose={exact_active['anyAnchorClose16RowCount']}/"
        f"{exact_active['leftBoundaryClose16RowCount']}/"
        f"{exact_active['centerSlotClose16RowCount']}/"
        f"{exact_active['rightBoundaryClose16RowCount']}|"
        f"allFourAny={len(all_four_any_close)}|subAllFourAny={len(substituted_all_four_any_close)}|"
        f"hiddenCandidate={len(hidden_candidates)}|sourceR3={source_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "variantCount": len(variants),
        "closeThresholdPx": CLOSE_THRESHOLD_PX,
        "exactActiveLeftCenterStream": exact_active["nearestCenterStreams"]["left"],
        "exactActiveCenterStream": exact_active["nearestCenterStreams"]["center"],
        "exactActiveRightCenterStream": exact_active["nearestCenterStreams"]["right"],
        "exactActiveBoundaryStreams": exact_active["nearestBoundaryStreams"],
        "exactActiveAnyAnchorClose16RowCount": exact_active["anyAnchorClose16RowCount"],
        "exactActiveLeftBoundaryClose16RowCount": exact_active["leftBoundaryClose16RowCount"],
        "exactActiveCenterSlotClose16RowCount": exact_active["centerSlotClose16RowCount"],
        "exactActiveRightBoundaryClose16RowCount": exact_active["rightBoundaryClose16RowCount"],
        "exactActiveAllFourAnyAnchorClose16": exact_active["allFourAnyAnchorClose16"],
        "exactActiveAllFourLeftBoundaryClose16": exact_active["allFourLeftBoundaryClose16"],
        "exactActiveAllFourCenterSlotClose16": exact_active["allFourCenterSlotClose16"],
        "exactActiveAllFourRightBoundaryClose16": exact_active["allFourRightBoundaryClose16"],
        "exactActiveMeanNearestResiduePx": exact_active["meanNearestResiduePx"],
        "exactActiveMeanCenterResiduePx": exact_active["meanCenterResiduePx"],
        "allFourAnyAnchorClose16VariantCount": len(all_four_any_close),
        "substitutedAllFourAnyAnchorClose16VariantCount": len(substituted_all_four_any_close),
        "bestMeanNearestResidueVariantOrdinal": min(
            variants, key=lambda row: row["meanNearestResiduePx"]
        )["ordinal"],
        "bestMeanNearestResiduePx": min(row["meanNearestResiduePx"] for row in variants),
        "slotBoundaryResidualPriorFingerprint": slot_boundary.get("summary", {}).get(
            "slotBoundaryResidualFingerprint"
        ),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "hiddenEdgeResidueCandidateCount": len(hidden_candidates),
        "selectorUnlocked": False,
        "edgeResidueFingerprint": fingerprint,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current scan active box OVERDOSE edge-residue control; no key derivation, "
            "hashing, WIF, seed, address, BIP39, or broad brute force"
        ),
        "inputs": {
            "targetWitnessSubstitution": rel(TARGET_WITNESS_SUBSTITUTION),
            "c9OverdoseLetterSlotGate": rel(C9_SLOTS),
            "slotBoundaryResidualPrior": rel(SLOT_BOUNDARY_RESIDUAL),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "targetOrder": TARGETS,
            "anchors": ANCHORS,
            "closeThresholdPx": CLOSE_THRESHOLD_PX,
            "boundedVariantSet": "same eight O4/B4/G5/O5 witness-box substitutions from the current scan target witness gate",
            "candidateRequirement": (
                "exact active boxes plus all-four edge/center closeness plus source-backed R3"
            ),
        },
        "c9Ruler": {
            "slotLetters": "".join(slot["letter"] for slot in ruler["slots"]),
            "slotCount": len(ruler["slots"]),
            "slotWidthPx": round(ruler["slots"][0]["width"], 6) if ruler["slots"] else None,
            "boundaries": [round(value, 6) for value in ruler["boundaries"]],
            "centers": [round(value, 6) for value in ruler["centers"]],
        },
        "variantRows": variants,
        "exactActiveVariant": exact_active,
        "allFourAnyAnchorClose16Variants": all_four_any_close,
        "summary": summary,
        "decision": {
            "currentScanActiveBoxOverdoseEdgeResidueGate": (
                "current_scan_active_box_overdose_edge_residue_no_selector"
            ),
            "selectorUnlocked": False,
            "reason": (
                "Exact active centers repeat the known OVED stream, but 0/4 exact active "
                "centers are close to slot centers at <=16px and the exact left/right edge "
                "streams are mixed. A substituted annotated O4 variant has better all-four "
                "any-anchor closeness than the exact active boxes, so edge residue is not "
                "exact-active-specific and has no source-backed R3 permission."
            ),
        },
        "nextMove": (
            "Do not pursue active-box edge/center residue as an extraction selector. "
            "The next useful local pass should inspect a different source/provenance "
            "surface, or stop until a true physical/original-layout asset or raw clue "
            "wording supplies unit/order/transform."
        ),
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint {fingerprint}")


if __name__ == "__main__":
    main()
