#!/usr/bin/env python3
"""Control active line/corridor indexes against OVERDOSE slots.

This bounded geometry/index pass checks whether the active O4/B4/G5/O5 page
line and corridor indexes provide a non-arbitrary rule for the measured
OVERDOSE slot indexes. It records guardrail status only; it does not derive key
material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_active_index_slot_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_active_index_slot_control.json"
OUT_MD = OUT / "source_packet_active_index_slot_control.md"
OUT_SHEET = OUT / "source_packet_active_index_slot_control_sheet.jpg"

INPUTS = {
    "source_packet_active_target_authority_crosscheck": ROOT
    / "analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck/"
    "source_packet_active_target_authority_crosscheck.json",
    "source_packet_active_format_stream_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_format_stream_control/"
    "source_packet_active_format_stream_control.json",
    "c9_overdose_letter_slot_gate": ROOT
    / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/"
    "c9_overdose_letter_slot_gate.json",
    "c9_grey_black_over_slot_control": ROOT
    / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/"
    "c9_grey_black_over_slot_control.json",
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "source_packet_orientation_control_quartets": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def mod_affine_fits(xs: list[int], ys: list[int], mod: int) -> list[dict]:
    fits = []
    for a in range(mod):
        for b in range(mod):
            if all((a * x + b) % mod == y for x, y in zip(xs, ys)):
                fits.append({"a": a, "b": b, "formula": f"({a}*x+{b}) mod {mod}"})
    return fits


def mod_affine_2d_fits(lines: list[int], corridors: list[int], ys: list[int], mod: int) -> list[dict]:
    fits = []
    for a in range(mod):
        for b in range(mod):
            for c in range(mod):
                if all((a * line + b * corr + c) % mod == y for line, corr, y in zip(lines, corridors, ys)):
                    fits.append(
                        {
                            "a": a,
                            "b": b,
                            "c": c,
                            "formula": f"({a}*line+{b}*corr+{c}) mod {mod}",
                        }
                    )
    return fits


def forward_gaps(values: list[int], mod: int | None = None) -> list[int]:
    gaps = []
    for left, right in zip(values, values[1:]):
        gap = right - left
        if mod is not None:
            gap %= mod
        gaps.append(gap)
    return gaps


def rotations(items: list[str]) -> list[list[str]]:
    return [items[i:] + items[:i] for i in range(len(items))]


def draw_sheet(summary: dict, active_rows: list[dict], check_rows: list[dict]) -> None:
    width, height = 1740, 940
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
    draw.text((24, 18), "Active Index / OVERDOSE Slot Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"line fits {summary['lineToSlotAffineFitCount']} | "
            f"corr fits {summary['corridorToSlotAffineFitCount']} | "
            f"2D fits {summary['lineCorridorToSlotAffineFitCount']} | "
            f"selectors {int(summary['selectorUnlocked'])}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Active rows", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 120, 260, 390, 510, 650, 800]
    headers = ["id", "line", "corridor", "state", "slot", "letter", "phrase"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(active_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 36), fill=fill)
        draw.text((xs[0], y), row["shortId"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), str(row["pageLine"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), str(row["corridorIndex"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["visualState"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), str(row["centerSlotIndex"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), row["centerSlotLetter"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), row["label"][:72], fill=(70, 70, 70), font=tiny)
        y += 42

    y += 22
    draw.text((24, y), "Checks", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 410, 610, 800]
    for x, header in zip(xs, ["check", "status", "value", "meaning"]):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(check_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        draw.text((xs[0], y), row["check"][:48], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["status"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), str(row["value"])[:24], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["meaning"][:100], fill=(70, 70, 70), font=tiny)
        y += 48

    y += 16
    draw.text((24, y), summary["indexSlotFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    data = {name: load_json(path) for name, path in INPUTS.items()}
    authority = data["source_packet_active_target_authority_crosscheck"]
    format_stream = data["source_packet_active_format_stream_control"]
    c9 = data["c9_overdose_letter_slot_gate"]
    grey_black = data["c9_grey_black_over_slot_control"]
    mirrored = data["c9_mirrored_header_glyph_gate"]
    orientation = data["source_packet_orientation_control_quartets"]
    reopen = data["source_packet_reopen_trigger_matrix"]

    authority_rows = {row.get("shortId"): row for row in authority.get("targetRows", [])}
    c9_rows = {row.get("shortId"): row for row in c9.get("activeRows", [])}
    active_rows = []
    for short_id in ["O4", "B4", "G5", "O5"]:
        row = dict(authority_rows.get(short_id, {}))
        row.update(c9_rows.get(short_id, {}))
        active_rows.append(row)

    line_order_ids = [row["shortId"] for row in sorted(active_rows, key=lambda row: row["pageLine"])]
    slot_order_ids = [row["shortId"] for row in sorted(active_rows, key=lambda row: row["centerSlotIndex"])]
    x_order_ids = [row["shortId"] for row in sorted(active_rows, key=lambda row: row["centerX"])]
    lines = [int(row["pageLine"]) for row in active_rows]
    corridors = [int(row["corridorIndex"]) for row in active_rows]
    slots = [int(row["centerSlotIndex"]) for row in active_rows]
    states = [row["visualState"] for row in active_rows]

    line_to_slot_fits = mod_affine_fits(lines, slots, 8)
    corridor_to_slot_fits = mod_affine_fits(corridors, slots, 8)
    line_corr_to_slot_fits = mod_affine_2d_fits(lines, corridors, slots, 8)
    line_parity_state = ["Y" if value % 2 == 0 else "K" for value in lines]
    corridor_parity_state = ["Y" if value % 2 == 0 else "K" for value in corridors]
    slot_parity_state = ["Y" if value % 2 == 0 else "K" for value in slots]
    line_gaps = forward_gaps(lines)
    corridor_gaps = forward_gaps(corridors)
    slot_gaps_mod8 = forward_gaps(slots, 8)
    slot_order_is_rotation = slot_order_ids in rotations(line_order_ids)
    slot_order_rotation_index = rotations(line_order_ids).index(slot_order_ids) if slot_order_is_rotation else None

    orientation_summary = orientation.get("summary", {})
    grey_summary = grey_black.get("summary", {})
    mirrored_summary = mirrored.get("summary", {})
    reopen_summary = reopen.get("summary", {})
    format_summary = format_stream.get("summary", {})

    check_rows = [
        {
            "check": "line index -> slot index mod 8",
            "status": "fail",
            "value": len(line_to_slot_fits),
            "meaning": "no simple affine mapping from readable page line to OVERDOSE center slot",
        },
        {
            "check": "corridor index -> slot index mod 8",
            "status": "fail",
            "value": len(corridor_to_slot_fits),
            "meaning": "no simple affine mapping from corridor index to OVERDOSE center slot",
        },
        {
            "check": "line+corridor -> slot index mod 8",
            "status": "fail",
            "value": len(line_corr_to_slot_fits),
            "meaning": "line and corridor share a constant offset and still do not fit slot indexes",
        },
        {
            "check": "line/corridor gaps vs slot gaps",
            "status": "fail",
            "value": f"{line_gaps}/{slot_gaps_mod8}",
            "meaning": "line/corridor gap phase 3/2/5 does not match OVERDOSE slot-gap phase 4/1/2",
        },
        {
            "check": "line/corridor parity -> Y/K",
            "status": "pass-as-validation-only",
            "value": "".join(line_parity_state),
            "meaning": "parity reproduces YKKY but has no source-backed unit/order wording",
        },
        {
            "check": "slot parity -> Y/K",
            "status": "fail",
            "value": "".join(slot_parity_state),
            "meaning": "OVERDOSE center-slot parity does not reproduce active color state",
        },
        {
            "check": "slot/x order rotation of line order",
            "status": "partial-context",
            "value": f"rotation={slot_order_rotation_index}",
            "meaning": "slot/x order is a one-step rotation of line order, but no source names rotate/start point",
        },
        {
            "check": "YKKY full-page controls",
            "status": "control",
            "value": orientation_summary.get("fullPageYkYkkyCombinationCount"),
            "meaning": "YKKY has multiple non-active full-page combinations",
        },
        {
            "check": "p75 OVER control",
            "status": "control",
            "value": grey_summary.get("controlSingleRowOverCount"),
            "meaning": "the active B4/G5 OVER signal has a non-active p75 lower-frame control",
        },
        {
            "check": "source-backed R3 / triggers",
            "status": "fail",
            "value": f"{format_summary.get('sourceBackedR3BridgeHitCount')}/{reopen_summary.get('satisfiedTriggerCount')}",
            "meaning": "no source-backed unit/order bridge or satisfied reopen trigger licenses the index relation",
        },
    ]

    selector_unlocked = (
        bool(line_to_slot_fits or corridor_to_slot_fits or line_corr_to_slot_fits)
        and format_summary.get("sourceBackedR3BridgeHitCount", 0) > 0
        and reopen_summary.get("satisfiedTriggerCount", 0) > 0
    )

    summary = {
        "activeTargetCount": len(active_rows),
        "lineOrder": " ".join(line_order_ids),
        "slotOrder": " ".join(slot_order_ids),
        "xOrder": " ".join(x_order_ids),
        "slotOrderIsLineOrderRotation": slot_order_is_rotation,
        "slotOrderRotationIndex": slot_order_rotation_index,
        "pageLines": " ".join(str(value) for value in lines),
        "corridorIndexes": " ".join(str(value) for value in corridors),
        "centerSlotIndexes": " ".join(str(value) for value in slots),
        "centerSlotLetters": "".join(row.get("centerSlotLetter", "") for row in active_rows),
        "lineGaps": "/".join(str(value) for value in line_gaps),
        "corridorGaps": "/".join(str(value) for value in corridor_gaps),
        "slotGapsMod8": "/".join(str(value) for value in slot_gaps_mod8),
        "lineToSlotAffineFitCount": len(line_to_slot_fits),
        "corridorToSlotAffineFitCount": len(corridor_to_slot_fits),
        "lineCorridorToSlotAffineFitCount": len(line_corr_to_slot_fits),
        "lineParityStateStream": "".join(line_parity_state),
        "corridorParityStateStream": "".join(corridor_parity_state),
        "slotParityStateStream": "".join(slot_parity_state),
        "activeVisualStateOrder": "".join(states),
        "fullPageYkYkkyCombinationCount": orientation_summary.get("fullPageYkYkkyCombinationCount"),
        "fullPageYkSlidingYkkyCount": orientation_summary.get("fullPageYkSlidingYkkyCount"),
        "controlSingleRowOverCount": grey_summary.get("controlSingleRowOverCount"),
        "p75ControlMatchesActiveBlackCount": mirrored_summary.get("p75ControlMatchesActiveBlackCount"),
        "mirrorVariantCount": mirrored_summary.get("variantCount"),
        "sourceBackedR3BridgeHitCount": format_summary.get("sourceBackedR3BridgeHitCount"),
        "selectorPermissionCorrectionCount": format_summary.get("selectorPermissionCorrectionCount"),
        "satisfiedReopenTriggerCount": reopen_summary.get("satisfiedTriggerCount"),
        "triggerCount": reopen_summary.get("triggerCount"),
        "selectorUnlocked": selector_unlocked,
    }
    summary["indexSlotFingerprint"] = (
        f"targets={summary['activeTargetCount']}|lineSlotFits={summary['lineToSlotAffineFitCount']}|"
        f"corrSlotFits={summary['corridorToSlotAffineFitCount']}|"
        f"lineCorrSlotFits={summary['lineCorridorToSlotAffineFitCount']}|"
        f"lineParity={summary['lineParityStateStream']}|slotParity={summary['slotParityStateStream']}|"
        f"slotRot={summary['slotOrderRotationIndex']}|slotGaps={summary['slotGapsMod8']}|"
        f"ykky={summary['fullPageYkYkkyCombinationCount']}|p75Over={summary['controlSingleRowOverCount']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(selector_unlocked)}"
    )

    decision = {
        "sourcePacketActiveIndexSlotControl": "index_slot_geometry_controlled_no_selector",
        "selectorUnlocked": selector_unlocked,
        "reason": (
            "Readable line/corridor parity reproduces YKKY, but line/corridor indexes "
            "do not map to OVERDOSE slot indexes under simple modulo-8 affine rules. "
            "The x/slot-order rotation has no source-named start/rotation rule and the "
            "active OVER signal remains controlled."
        ),
        "nextMove": (
            "Keep line/corridor parity, slot rotation, and slot-gap observations as "
            "source-validation descriptors only. Reopen extraction only with distinct "
            "source-backed unit/order wording."
        ),
    }

    payload = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active line/corridor index to OVERDOSE slot control; no extraction or candidate generation",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "activeRows": active_rows,
        "checkRows": check_rows,
        "lineToSlotFits": line_to_slot_fits,
        "corridorToSlotFits": corridor_to_slot_fits,
        "lineCorridorToSlotFits": line_corr_to_slot_fits,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Active Index Slot Control",
                "",
                f"- Active targets checked: `{summary['activeTargetCount']}`.",
                f"- Line/corridor/line+corridor modulo-8 slot fits: `{summary['lineToSlotAffineFitCount']}` / `{summary['corridorToSlotAffineFitCount']}` / `{summary['lineCorridorToSlotAffineFitCount']}`.",
                f"- Line/corridor parity state: `{summary['lineParityStateStream']}` / `{summary['corridorParityStateStream']}`.",
                f"- Slot parity state: `{summary['slotParityStateStream']}`.",
                f"- Line/corridor gaps vs slot gaps: `{summary['lineGaps']}` / `{summary['slotGapsMod8']}`.",
                f"- Slot order rotation index: `{summary['slotOrderRotationIndex']}`.",
                f"- Full-page YKKY combinations: `{summary['fullPageYkYkkyCombinationCount']}`.",
                f"- p75 OVER controls: `{summary['controlSingleRowOverCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['indexSlotFingerprint']}`.",
                "",
                "Decision: keep active index/slot relations as validation descriptors only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    draw_sheet(summary, active_rows, check_rows)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(summary["indexSlotFingerprint"])


if __name__ == "__main__":
    main()
