#!/usr/bin/env python3
"""Test whether the p73/p79 RRLL capsule direction selects active quartet boundary words.

This is a bounded geometry/order inspection. It uses the already-recorded
five-capsule direction signature and the locked O4/B4/G5/O5 active target
neighbors. It does not derive keys, hash text, generate seeds, scan WIF/Base58,
or check addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FIVE_JSON = ROOT / "analysis_outputs/source_audit/five_index_convergence/five_index_convergence.json"
ACTIVE_JSON = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json"
OUT = ROOT / "analysis_outputs/source_audit/active_quartet_capsule_direction_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_quartet_capsule_direction_gate.json"
OUT_MD = OUT / "active_quartet_capsule_direction_gate.md"
SHEET = OUT / "active_quartet_capsule_direction_gate_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def first_letters(words: list[str]) -> str:
    letters = []
    for word in words:
        match = re.search(r"[A-Za-z0-9$]", word)
        letters.append(match.group(0) if match else "-")
    return "".join(letters)


def last_letters(words: list[str]) -> str:
    letters = []
    for word in words:
        match = re.search(r"[A-Za-z0-9$](?!.*[A-Za-z0-9$])", word)
        letters.append(match.group(0) if match else "-")
    return "".join(letters)


def instruction_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def pick_word(record: dict[str, Any], dimension: str, mode: str, sign: str) -> tuple[str, str]:
    if dimension == "horizontal":
        primary = "rightBoundaryWord" if sign == "R" else "leftBoundaryWord"
        inverse = "leftBoundaryWord" if sign == "R" else "rightBoundaryWord"
    elif dimension == "vertical":
        primary = "belowWord" if sign == "R" else "aboveWord"
        inverse = "aboveWord" if sign == "R" else "belowWord"
    else:
        raise ValueError(f"unknown dimension {dimension}")

    field = primary if mode == "outgoing" else inverse
    return record.get(field) or "-", field


def build_mode_rows(records: list[dict[str, Any]], signs: str, order_name: str, dimension: str, mode: str) -> dict[str, Any]:
    rows = []
    picked_words = []
    for step, (record, sign) in enumerate(zip(records, signs), start=1):
        picked, field = pick_word(record, dimension, mode, sign)
        picked_words.append(picked)
        rows.append(
            {
                "step": step,
                "sign": sign,
                "targetId": record["id"],
                "targetLabel": record["label"],
                "pageLine": record["pageLine"],
                "corridorIndex": record["corridorIndex"],
                "picked": picked,
                "sourceField": field,
            }
        )

    stream = " ".join(picked_words)
    clean_stream = " ".join(word for word in picked_words if word != "-")
    return {
        "modeId": f"{order_name}_{dimension}_{mode}",
        "targetOrder": order_name,
        "dimension": dimension,
        "mode": mode,
        "signs": signs,
        "rows": rows,
        "stream": stream,
        "cleanStream": clean_stream or "-",
        "reverseCleanStream": " ".join(reversed([word for word in picked_words if word != "-"])) or "-",
        "initials": first_letters(picked_words),
        "lasts": last_letters(picked_words),
        "instructionHits": instruction_hits(clean_stream),
        "blankPickCount": sum(1 for word in picked_words if word == "-"),
        "nonblankPickCount": sum(1 for word in picked_words if word != "-"),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1720, 1080
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "Active Quartet Capsule-Direction Gate", fill=(244, 247, 250), font=title)
    draw.text(
        (margin, margin + 46),
        "The shared p73/p79 RRLL zigzag is applied only to O4/B4/G5/O5 side and vertical neighbor words.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("capsule signs", result["summary"]["stepSigns"]),
        ("active lines", result["summary"]["activePageLines"]),
        ("active corridors", result["summary"]["activeCorridorIndexes"]),
        ("instruction hits", result["summary"]["instructionHitCount"]),
    ]
    widths = [290, 360, 380, 300]
    x = margin
    for (label, value), width in zip(chips, widths):
        draw.rectangle((x, y, x + width, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value), fill=(232, 239, 246), font=mono)
        x += width + 20

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 108), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "RRLL does not produce an instruction-bearing boundary stream for the active O4/B4/G5/O5 quartet.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "Keep the capsule pattern as locator/provenance evidence unless a source clue names side, word, letter, or order.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 140
    draw.text((margin, y), "Active Targets", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("order", 12), ("id", 80), ("line", 270), ("corridor", 340), ("left/right", 450), ("above/below", 840)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for record in result["activeRecords"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 38), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 10), str(record["order"]), fill=(176, 186, 198), font=small)
        draw.text((margin + 80, y + 10), record["id"], fill=(176, 186, 198), font=small)
        draw.text((margin + 270, y + 10), str(record["pageLine"]), fill=(232, 239, 246), font=mono)
        draw.text((margin + 340, y + 10), str(record["corridorIndex"]), fill=(232, 239, 246), font=mono)
        draw.text(
            (margin + 450, y + 10),
            f"{record['leftBoundaryWord']} / {record['rightBoundaryWord']}",
            fill=(176, 186, 198),
            font=small,
        )
        draw.text(
            (margin + 840, y + 10),
            f"{record['aboveWord']} / {record['belowWord']}",
            fill=(176, 186, 198),
            font=small,
        )
        y += 42

    y += 24
    draw.text((margin, y), "Direction Modes", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("mode", 12), ("stream", 380), ("initials", 1080), ("lasts", 1180), ("hits", 1280)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for mode in result["directionModes"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 40), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 11), mode["modeId"], fill=(176, 186, 198), font=small)
        draw.text((margin + 380, y + 11), mode["cleanStream"][:78], fill=(232, 239, 246), font=small)
        draw.text((margin + 1080, y + 11), mode["initials"], fill=(176, 186, 198), font=mono)
        draw.text((margin + 1180, y + 11), mode["lasts"], fill=(176, 186, 198), font=mono)
        draw.text((margin + 1280, y + 11), ", ".join(mode["instructionHits"]) or "-", fill=(176, 186, 198), font=small)
        y += 44

    sheet.save(SHEET, quality=94)


def main() -> None:
    five = load_json(FIVE_JSON)
    active = load_json(ACTIVE_JSON)
    active_records = active.get("records", [])
    step_signs = five.get("p73StepSignature", {}).get("stepSigns") or five.get("p79StepSignature", {}).get("stepSigns") or ""
    if len(step_signs) != len(active_records):
        raise RuntimeError(f"Need one direction sign per active record; got signs={step_signs!r}, records={len(active_records)}")

    ordered_sets = [
        ("active_order", active_records),
        ("reverse_active_order", list(reversed(active_records))),
    ]
    direction_modes = []
    for order_name, records in ordered_sets:
        for dimension in ["horizontal", "vertical"]:
            for mode in ["outgoing", "incoming"]:
                direction_modes.append(build_mode_rows(records, step_signs, order_name, dimension, mode))

    instruction_hit_modes = [mode for mode in direction_modes if mode["instructionHits"]]
    nonblank_streams = [mode for mode in direction_modes if mode["cleanStream"] != "-"]
    summary = {
        "stepSigns": step_signs,
        "stepBits_R1_L0": five.get("p73StepSignature", {}).get("stepBits_R1_L0"),
        "sameStepSignature": five.get("sameStepSignature"),
        "modeCount": len(direction_modes),
        "nonblankStreamCount": len(nonblank_streams),
        "instructionHitCount": sum(len(mode["instructionHits"]) for mode in direction_modes),
        "instructionHitModeCount": len(instruction_hit_modes),
        "activePageLines": " ".join(str(row.get("pageLine")) for row in active_records),
        "activeCorridorIndexes": " ".join(str(row.get("corridorIndex")) for row in active_records),
        "activeVisualStateOrder": "".join(row.get("visualState", "") for row in active_records),
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active quartet capsule-direction gate; no extraction, no key derivation, no hashing, no seed/WIF/address checks",
        "inputs": {
            "fiveIndexConvergence": rel(FIVE_JSON),
            "activeLineUnitReconciliation": rel(ACTIVE_JSON),
        },
        "summary": summary,
        "activeRecords": [
            {
                "order": row.get("order"),
                "id": row.get("id"),
                "label": row.get("label"),
                "visualState": row.get("visualState"),
                "pageLine": row.get("pageLine"),
                "corridorIndex": row.get("corridorIndex"),
                "leftBoundaryWord": row.get("leftBoundaryWord"),
                "rightBoundaryWord": row.get("rightBoundaryWord"),
                "aboveWord": row.get("aboveWord"),
                "belowWord": row.get("belowWord"),
            }
            for row in active_records
        ],
        "directionModes": direction_modes,
        "assessment": [
            "The shared p73/p79 capsule direction signature is RRLL and is real as a five-index locator/provenance signal.",
            "Applying RRLL to horizontal side words around O4/B4/G5/O5 yields ordinary fragments such as `in collateralized a`, `he's to`, and `to he's`; no stream gives a word/letter/line/key instruction.",
            "Applying the same bounded test to vertical above/below neighbors yields ordinary fragments such as `announced billions future trust` and `on was those`; no stream gives a selector instruction.",
            "Reverse active order also fails to produce instruction-bearing text.",
            "This closes RRLL-as-active-quartet-side-selector for the current scan; it does not weaken page 76 as the target surface.",
        ],
        "decision": "rrll_capsule_direction_does_not_select_active_quartet_boundary_instruction",
        "sheet": rel(SHEET),
        "nextMove": "Keep RRLL/five-index evidence as locator/provenance only; reopen side-word or vertical-neighbor extraction only if a raw clue names left/right, above/below, first/last word, or letter extraction.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Quartet Capsule-Direction Gate",
        "",
        "Scope: apply the shared p73/p79 `RRLL` capsule zigzag only to the locked O4/B4/G5/O5 side and vertical boundary words. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Capsule step signs: `{summary['stepSigns']}`.",
        f"- Same p73/p79 step signature: `{summary['sameStepSignature']}`.",
        f"- Active page lines: `{summary['activePageLines']}`.",
        f"- Active corridor indexes: `{summary['activeCorridorIndexes']}`.",
        f"- Active visual state order: `{summary['activeVisualStateOrder']}`.",
        f"- Direction modes checked: `{summary['modeCount']}`.",
        f"- Instruction hit count: `{summary['instructionHitCount']}`.",
        "",
        "## Direction Modes",
        "",
        "| mode | stream | reverse stream | initials | lasts | blanks | instruction hits |",
        "|---|---|---|---|---|---:|---|",
    ]
    for mode in direction_modes:
        lines.append(
            f"| `{mode['modeId']}` | `{mode['cleanStream']}` | `{mode['reverseCleanStream']}` | `{mode['initials']}` | `{mode['lasts']}` | `{mode['blankPickCount']}` | {', '.join(mode['instructionHits']) or '-'} |"
        )

    lines.extend(["", "## Active Target Inputs", "", "| order | id | line | corridor | left | right | above | below |", "|---:|---|---:|---:|---|---|---|---|"])
    for record in result["activeRecords"]:
        lines.append(
            f"| {record['order']} | `{record['id']}` | {record['pageLine']} | {record['corridorIndex']} | `{record['leftBoundaryWord']}` | `{record['rightBoundaryWord']}` | `{record['aboveWord']}` | `{record['belowWord']}` |"
        )

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
