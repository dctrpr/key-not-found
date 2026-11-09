#!/usr/bin/env python3
"""Test whether active target geometry depends on a single box witness.

This bounded pass does not generate key material or try extraction. It swaps
every available current-scan/PDF witness box for the same O4/B4/G5/O5 target
phrases, then checks whether the active line-gap and OVERDOSE-slot fingerprint
survives substitutions.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_target_witness_box_substitution_gate.json"
OUT_MD = OUT / "current_scan_target_witness_box_substitution_gate.md"
OUT_SHEET = OUT / "current_scan_target_witness_box_substitution_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HIGHLIGHT_AUDIT = ROOT / "analysis_outputs/highlight_audit/highres_highlight_audit.json"
C9_SLOTS = ROOT / (
    "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGETS = ["O4", "B4", "G5", "O5"]
TARGET_STATE_STREAM = "YKKY"
TARGET_COLOR_STREAM = "OBBO"
TARGET_LINE_GAPS = [3, 2, 5]
TARGET_SLOT_STREAM = "OVED"
HIGHLIGHT_WITNESS_IDS = {
    "O4": ["p76_orange_4", "annotated_13_orange"],
    "B4": ["annotated_14_grey"],
    "G5": ["annotated_15_grey"],
    "O5": ["p76_orange_5"],
}
STATE_BY_TARGET = {"O4": "Y", "B4": "K", "G5": "K", "O5": "Y"}
COLOR_BY_TARGET = {"O4": "O", "B4": "B", "G5": "B", "O5": "O"}


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def center(box: list[float]) -> tuple[float, float]:
    return ((float(box[0]) + float(box[2])) / 2.0, (float(box[1]) + float(box[3])) / 2.0)


def slot_for_x(slots: list[dict[str, Any]], x: float) -> dict[str, Any]:
    for slot in slots:
        if float(slot["left"]) <= x < float(slot["right"]):
            return {"index": int(slot["index"]), "letter": str(slot["letter"]), "inside": True}
    nearest = min(
        slots,
        key=lambda slot: min(abs(x - float(slot["left"])), abs(x - float(slot["right"]))),
    )
    return {"index": int(nearest["index"]), "letter": str(nearest["letter"]), "inside": False}


def fit_line_pitch(active_rows: list[dict[str, Any]]) -> dict[str, Any]:
    xs = [float(row["pageLine"]) for row in active_rows]
    ys = [center(row["box"])[1] for row in active_rows]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean
    residuals = [round(y - (slope * x + intercept), 6) for x, y in zip(xs, ys)]
    return {"slopePxPerLine": slope, "interceptPx": intercept, "activeResidualsPx": residuals}


def all_highlight_rows(highlight_audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for collection in ["visualOrangeRows", "annotatedColorRows"]:
        for row in highlight_audit.get(collection, []):
            if row.get("id"):
                rows[str(row["id"])] = row
    return rows


def same_box(left: list[float], right: list[float]) -> bool:
    return all(abs(float(a) - float(b)) < 1e-6 for a, b in zip(left, right))


def witness_options(
    active_index: dict[str, Any], highlight_audit: dict[str, Any], slots: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    active_by_short = {row["shortId"]: row for row in active_index.get("activeRows", [])}
    highlight_by_id = all_highlight_rows(highlight_audit)
    options: dict[str, list[dict[str, Any]]] = {}

    for target in TARGETS:
        rows: list[dict[str, Any]] = []
        active = active_by_short[target]
        active_box = [float(v) for v in active["box"]]
        rows.append(
            {
                "target": target,
                "witnessIds": [f"{target}_active_index"],
                "sourceKinds": ["active_index_slot"],
                "label": active.get("phrase", ""),
                "box": active_box,
                "isExactActiveBox": True,
                "pageLine": int(active["pageLine"]),
                "corridorIndex": int(active["corridorIndex"]),
            }
        )
        for witness_id in HIGHLIGHT_WITNESS_IDS[target]:
            row = highlight_by_id.get(witness_id)
            if not row or not row.get("box"):
                continue
            box = [float(v) for v in row["box"]]
            duplicate = next((existing for existing in rows if same_box(existing["box"], box)), None)
            if duplicate:
                duplicate["witnessIds"].append(witness_id)
                duplicate["sourceKinds"].append(str(row.get("kind", "unknown")))
                continue
            rows.append(
                {
                    "target": target,
                    "witnessIds": [witness_id],
                    "sourceKinds": [str(row.get("kind", "unknown"))],
                    "label": row.get("expected") or row.get("ocrText") or active.get("phrase", ""),
                    "box": box,
                    "isExactActiveBox": False,
                    "pageLine": None,
                    "corridorIndex": None,
                }
            )

        for row in rows:
            cx, cy = center(row["box"])
            slot = slot_for_x(slots, cx)
            row.update(
                {
                    "centerX": round(cx, 3),
                    "centerY": round(cy, 3),
                    "visualState": STATE_BY_TARGET[target],
                    "colorCode": COLOR_BY_TARGET[target],
                    "slotIndex": slot["index"],
                    "slotLetter": slot["letter"],
                    "slotInside": slot["inside"],
                }
            )
        options[target] = rows
    return options


def variant_row(
    ordinal: int, option_tuple: tuple[dict[str, Any], ...], line_pitch_px: float
) -> dict[str, Any]:
    y_gaps_px = [
        round(float(b["centerY"]) - float(a["centerY"]), 3)
        for a, b in zip(option_tuple, option_tuple[1:])
    ]
    estimated_line_gaps = [int(round(gap / line_pitch_px)) for gap in y_gaps_px]
    slot_stream = "".join(row["slotLetter"] for row in option_tuple)
    exact_flags = [bool(row["isExactActiveBox"]) for row in option_tuple]
    state_stream = "".join(row["visualState"] for row in option_tuple)
    color_stream = "".join(row["colorCode"] for row in option_tuple)
    return {
        "ordinal": ordinal,
        "targets": [row["target"] for row in option_tuple],
        "witnessIds": [row["witnessIds"] for row in option_tuple],
        "sourceKinds": [row["sourceKinds"] for row in option_tuple],
        "exactActiveBoxFlags": exact_flags,
        "exactActiveBoxCount": sum(exact_flags),
        "centerXs": [row["centerX"] for row in option_tuple],
        "centerYs": [row["centerY"] for row in option_tuple],
        "visualStateStream": state_stream,
        "colorStream": color_stream,
        "slotIndexes": [row["slotIndex"] for row in option_tuple],
        "slotStream": slot_stream,
        "yGapsPx": y_gaps_px,
        "estimatedLineGaps": estimated_line_gaps,
        "matchesStateStream": state_stream == TARGET_STATE_STREAM,
        "matchesColorStream": color_stream == TARGET_COLOR_STREAM,
        "matchesLineGapEstimate": estimated_line_gaps == TARGET_LINE_GAPS,
        "matchesSlotStream": slot_stream == TARGET_SLOT_STREAM,
        "matchesCombinedFingerprint": (
            state_stream == TARGET_STATE_STREAM
            and color_stream == TARGET_COLOR_STREAM
            and estimated_line_gaps == TARGET_LINE_GAPS
            and slot_stream == TARGET_SLOT_STREAM
        ),
        "allExactActiveBoxes": all(exact_flags),
        "hasAnnotatedSubstitution": not all(exact_flags),
    }


def build_variants(
    options: dict[str, list[dict[str, Any]]], line_pitch_px: float
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ordinal, option_tuple in enumerate(
        itertools.product(*(options[target] for target in TARGETS)), start=1
    ):
        rows.append(variant_row(ordinal, option_tuple, line_pitch_px))
    return rows


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_sheet(
    options: dict[str, list[dict[str, Any]]], variants: list[dict[str, Any]], summary: dict[str, Any]
) -> None:
    width, height = 1750, 980
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = font(26)
    small_font = font(16)
    tiny_font = font(13)

    draw.rectangle((0, 0, width, 96), fill=(28, 32, 38))
    draw.text((24, 18), "Current Scan Target Witness Box Substitution Gate", fill="white", font=title_font)
    draw.text(
        (24, 58),
        (
            f"target witness variants {summary['geometryVariantCount']} | line-gap hits "
            f"{summary['lineGapHitCount']} | slot hits {summary['slotStreamHitCount']} | "
            f"combined {summary['combinedFingerprintHitCount']} | fingerprint {summary['witnessBoxSubstitutionFingerprint']}"
        ),
        fill=(230, 230, 230),
        font=tiny_font,
    )

    y = 122
    draw.text((24, y), "Per-target witness boxes", fill=(40, 40, 40), font=small_font)
    y += 28
    headers = ["target", "witness ids", "slot", "center", "exact?", "label"]
    xs = [24, 130, 520, 610, 790, 900]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny_font)
    y += 22
    rows = [row for target in TARGETS for row in options[target]]
    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (238, 242, 247)
        outline = (242, 164, 54) if row["isExactActiveBox"] else None
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill, outline=outline)
        draw.text((xs[0], y), row["target"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[1], y), " + ".join(row["witnessIds"])[:44], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[2], y), f"{row['slotLetter']}{row['slotIndex']}", fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[3], y), f"{row['centerX']:.1f},{row['centerY']:.1f}", fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[4], y), str(row["isExactActiveBox"]), fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[5], y), str(row.get("label", ""))[:100], fill=(30, 30, 30), font=tiny_font)
        y += 44

    y += 24
    draw.text((24, y), "Geometry variants", fill=(40, 40, 40), font=small_font)
    y += 28
    headers = ["#", "witnesses", "gaps", "slots", "exact boxes", "combined?"]
    xs = [24, 90, 830, 990, 1110, 1280]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny_font)
    y += 22
    for idx, row in enumerate(variants):
        fill = (238, 249, 239) if row["matchesCombinedFingerprint"] else (248, 249, 252) if idx % 2 == 0 else (238, 242, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        witness = " / ".join("+".join(ids) for ids in row["witnessIds"])
        draw.text((xs[0], y), str(row["ordinal"]), fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[1], y), witness[:94], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[2], y), "/".join(map(str, row["estimatedLineGaps"])), fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[3], y), row["slotStream"], fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[4], y), f"{row['exactActiveBoxCount']}/4", fill=(30, 30, 30), font=tiny_font)
        draw.text((xs[5], y), str(row["matchesCombinedFingerprint"]), fill=(25, 105, 50) if row["matchesCombinedFingerprint"] else (130, 30, 30), font=tiny_font)
        y += 44

    img.save(OUT_SHEET, quality=92)


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Target Witness Box Substitution Gate",
        "",
        "Scope: bounded current-scan/PDF witness-box substitution control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Unique per-target geometry variants: `{summary['geometryVariantCount']}`",
        f"- Per-target option counts: `{summary['perTargetOptionCounts']}`",
        f"- Line-gap `3/2/5` hits: `{summary['lineGapHitCount']}`",
        f"- Slot-stream `OVED` hits: `{summary['slotStreamHitCount']}`",
        f"- Combined fingerprint hits: `{summary['combinedFingerprintHitCount']}`",
        f"- Combined hits using substituted/non-exact boxes: `{summary['combinedSubstitutedHitCount']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['witnessBoxSubstitutionFingerprint']}`",
        "",
        "## Witness Options",
        "",
        "| target | witness ids | state/color | slot | center | exact active box | label |",
        "|---|---|---|---|---|---|---|",
    ]
    for target in TARGETS:
        for row in result["witnessOptions"][target]:
            label = str(row.get("label", "")).replace("|", "/")
            lines.append(
                f"| `{target}` | `{' + '.join(row['witnessIds'])}` | `{row['visualState']}/{row['colorCode']}` | "
                f"`{row['slotLetter']}{row['slotIndex']}` | `{row['centerX']},{row['centerY']}` | "
                f"`{row['isExactActiveBox']}` | {label} |"
            )

    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| # | witnesses | line gaps | slots | exact boxes | combined hit |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in result["variantRows"]:
        witness = " / ".join("+".join(ids) for ids in row["witnessIds"])
        lines.append(
            f"| `{row['ordinal']}` | `{witness}` | `{'/'.join(map(str, row['estimatedLineGaps']))}` | "
            f"`{row['slotStream']}` | `{row['exactActiveBoxCount']}/4` | `{row['matchesCombinedFingerprint']}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']['currentScanTargetWitnessBoxSubstitutionGate']}.",
            f"- Reason: {result['decision']['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    highlight_audit = load_json(HIGHLIGHT_AUDIT)
    c9_slots = load_json(C9_SLOTS)
    reopen_trigger = load_json(REOPEN_TRIGGER_MATRIX)
    slots = c9_slots.get("slots", [])

    active_rows = [
        row for row in active_index.get("activeRows", []) if row.get("shortId") in TARGETS
    ]
    active_rows.sort(key=lambda row: TARGETS.index(row["shortId"]))
    line_fit = fit_line_pitch(active_rows)
    options = witness_options(active_index, highlight_audit, slots)
    variants = build_variants(options, line_fit["slopePxPerLine"])

    combined_hits = [row for row in variants if row["matchesCombinedFingerprint"]]
    combined_substituted = [
        row for row in combined_hits if row["hasAnnotatedSubstitution"] or not row["allExactActiveBoxes"]
    ]
    line_gap_hits = [row for row in variants if row["matchesLineGapEstimate"]]
    slot_hits = [row for row in variants if row["matchesSlotStream"]]
    both_line_slot_hits = [
        row for row in variants if row["matchesLineGapEstimate"] and row["matchesSlotStream"]
    ]

    reopen_summary = reopen_trigger.get("summary", {})
    source_r3 = int(reopen_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied_triggers = int(reopen_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(reopen_summary.get("triggerCount", 0) or 0)
    selector_unlocked = False
    fingerprint = (
        f"options={','.join(f'{target}:{len(options[target])}' for target in TARGETS)}|"
        f"variants={len(variants)}|line325={len(line_gap_hits)}|slotOVED={len(slot_hits)}|"
        f"lineAndSlot={len(both_line_slot_hits)}|combined={len(combined_hits)}|"
        f"subCombined={len(combined_substituted)}|sourceR3={source_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "geometryVariantCount": len(variants),
        "perTargetOptionCounts": ", ".join(f"{target}:{len(options[target])}" for target in TARGETS),
        "targetStateStream": TARGET_STATE_STREAM,
        "targetColorStream": TARGET_COLOR_STREAM,
        "targetLineGaps": "/".join(map(str, TARGET_LINE_GAPS)),
        "targetSlotStream": TARGET_SLOT_STREAM,
        "lineGapHitCount": len(line_gap_hits),
        "slotStreamHitCount": len(slot_hits),
        "lineGapAndSlotHitCount": len(both_line_slot_hits),
        "combinedFingerprintHitCount": len(combined_hits),
        "combinedSubstitutedHitCount": len(combined_substituted),
        "allExactActiveBoxCombinedHitCount": sum(1 for row in combined_hits if row["allExactActiveBoxes"]),
        "fittedLinePitchPx": round(line_fit["slopePxPerLine"], 6),
        "fittedLineInterceptPx": round(line_fit["interceptPx"], 6),
        "activeLineFitResidualsPx": line_fit["activeResidualsPx"],
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector_unlocked,
        "witnessBoxSubstitutionFingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current scan target witness-box substitution control; no key derivation, "
            "hashing, WIF, seed, address, or broad brute force"
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "highlightAudit": rel(HIGHLIGHT_AUDIT),
            "c9Slots": rel(C9_SLOTS),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "method": {
            "targetOrder": TARGETS,
            "substitutedWitnessIds": HIGHLIGHT_WITNESS_IDS,
            "lineGapEstimate": "least-squares active pageLine-to-centerY fit, then rounded y gaps",
            "combinedFingerprint": "YKKY state, OBBO color, line gaps 3/2/5, C9 center-slot stream OVED",
        },
        "witnessOptions": options,
        "variantRows": variants,
        "combinedFingerprintHits": combined_hits,
        "summary": summary,
        "decision": {
            "currentScanTargetWitnessBoxSubstitutionGate": (
                "keep_exact_target_boxes_as_registration_authority_only"
            ),
            "reason": (
                "Only the exact active target boxes preserve both line gaps 3/2/5 and "
                "C9 slot stream OVED. Annotation substitutions break either slot stream "
                "or line-gap phase, so they do not create a hidden selector or an alternate "
                "read path."
            ),
            "selectorUnlocked": selector_unlocked,
        },
        "nextMove": (
            "Use exact active boxes plus visual duplicate boxes as future source-validation "
            "witnesses; treat broad annotation boxes as text-authority/context witnesses, "
            "not geometry selectors."
        ),
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(options, variants, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint {fingerprint}")


if __name__ == "__main__":
    main()
