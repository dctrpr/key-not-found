#!/usr/bin/env python3
"""Control-test the G5-centered line/corridor mirror near miss.

The previous index gate found the only notable near miss: a mirror axis at
page line 27 / corridor 9 maps O4 <-> O5 and G5 -> G5, but B4 maps to the
non-active Novogratz line. This pass asks whether requiring bold/highlighted
reflected rows rescues that near miss.

No OCR, extraction, hashing, key derivation, seed/WIF checks, address checks,
or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CORRIDOR_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
ACTIVE_JSON = (
    ROOT
    / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/"
    "active_line_unit_reconciliation.json"
)
MIRROR_JSON = (
    ROOT
    / "analysis_outputs/source_audit/active_line_corridor_mirror_index_gate/"
    "active_line_corridor_mirror_index_gate.json"
)
OUT = ROOT / "analysis_outputs/source_audit/g5_axis_bold_highlight_rescue_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "g5_axis_bold_highlight_rescue_gate.json"
OUT_MD = OUT / "g5_axis_bold_highlight_rescue_gate.md"
OUT_SHEET = OUT / "g5_axis_bold_highlight_rescue_gate_sheet.jpg"

STRICT_TERMS = re.compile(
    r"\b(read|take|first|last|letter|letters|word|words|line|lines|order|key|seed|private|wif|phrase)\b",
    re.I,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


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


def classify_row(row: dict[str, Any], active_ids: list[str]) -> dict[str, Any]:
    highlights = row.get("highlights", [])
    has_orange = any("orange" in value.lower() for value in highlights)
    has_grey = any("grey" in value.lower() for value in highlights)
    has_bold_flag = any("bold" in value.lower() for value in highlights) or bool(row.get("boldLetters"))
    if row.get("activeTargets"):
        role = "active"
    elif has_orange or has_grey:
        role = "highlight_control"
    elif has_bold_flag:
        role = "bold_control"
    else:
        role = "plain_control"
    if has_orange:
        style_code = "O"
    elif has_grey:
        style_code = "G"
    elif has_bold_flag:
        style_code = "B"
    else:
        style_code = "-"
    return {
        "role": role,
        "styleCode": style_code,
        "hasSignal": style_code != "-",
        "activeTargetIds": active_ids,
        "highlightLabels": highlights,
        "boldLetters": row.get("boldLetters", ""),
        "partialBoldLetters": row.get("partialBoldLetters", ""),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1500, 900
    img = Image.new("RGB", (width, height), (13, 16, 21))
    draw = ImageDraw.Draw(img)
    title = font(30)
    normal = font(18)
    small = font(14)
    mono = font(14)
    draw.text((40, 30), "G5 Axis Bold/Highlight Rescue Gate", fill=(242, 245, 249), font=title)
    draw.text(
        (40, 75),
        "Checks whether the G5-centered line/corridor mirror near miss is rescued by bold/highlight rows.",
        fill=(180, 190, 202),
        font=normal,
    )
    s = result["summary"]
    y = 125
    for line in [
        f"axis page line / corridor: {s['axisPageLine']} / {s['axisCorridorIndex']}",
        f"active hits: {s['activeHitCount']} | active misses: {s['activeMissCount']} | non-active signal hits: {s['nonActiveSignalHitCount']}",
        f"reflected style stream: {s['reflectedStyleStream']} | active-target stream: {s['reflectedActiveTargetStream']}",
        f"bold stream length: {s['boldStreamLength']} | partial-bold stream: {s['partialBoldStream'] or '-'}",
        f"strict instruction hits: {s['strictInstructionHitCount']}",
    ]:
        draw.text((40, y), line, fill=(205, 213, 222), font=mono)
        y += 24

    y = 245
    draw.text((40, y - 34), "Active-Order Reflections", fill=(242, 245, 249), font=normal)
    row_h = 66
    for idx, row in enumerate(result["activeOrderReflections"]):
        y0 = y + idx * row_h
        fill = (42, 46, 58)
        if row["reflected"]["role"] == "active":
            fill = (70, 57, 29)
        elif row["reflected"]["role"] != "plain_control":
            fill = (54, 45, 67)
        draw.rectangle((40, y0, width - 40, y0 + row_h - 4), fill=fill)
        left = f"{row['from']} L{row['fromPageLine']} C{row['fromCorridorIndex']}"
        right = f"-> L{row['reflectedPageLine']} C{row['reflectedCorridorIndex']} {row['reflected']['role']} {row['reflected']['styleCode']}"
        draw.text((60, y0 + 10), left, fill=(255, 207, 90), font=mono)
        draw.text((285, y0 + 10), right, fill=(218, 225, 234), font=mono)
        draw.text((60, y0 + 34), row["text"][:150], fill=(205, 213, 222), font=small)

    y += len(result["activeOrderReflections"]) * row_h + 38
    draw.text((40, y), "Signal Rows On G5 Axis", fill=(242, 245, 249), font=normal)
    y += 32
    for pair in result["signalPairs"][:12]:
        line = (
            f"L{pair['line']}<->L{pair['mirrorLine']} "
            f"C{pair['corridor']}<->C{pair['mirrorCorridor']} "
            f"{pair['sourceStyle']}->{pair['mirrorStyle']} {pair['sourceText'][:38]} | {pair['mirrorText'][:38]}"
        )
        draw.text((65, y), line[:150], fill=(190, 199, 210), font=mono)
        y += 22
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    corridor = load_json(CORRIDOR_JSON)
    active = load_json(ACTIVE_JSON)
    mirror = load_json(MIRROR_JSON)
    active_records = active["records"]
    records = corridor["records"]
    line_by_index = {row["lineIndex"]: row for row in records}
    row_by_corridor = {row["corridorIndex"]: row for row in records}
    active_by_line: dict[int, list[str]] = {}
    for row in active_records:
        active_by_line.setdefault(row["pageLine"], []).append(row["id"])
    for row in records:
        row["activeTargets"] = active_by_line.get(row["lineIndex"], [])

    axis_line = int(mirror["summary"]["bestPageLineAxis"])
    axis_corridor = int(mirror["summary"]["bestCorridorAxis"])

    reflected_rows = []
    for active_row in active_records:
        reflected_line = 2 * axis_line - active_row["pageLine"]
        reflected_corridor = 2 * axis_corridor - active_row["corridorIndex"]
        # The line and corridor axes are equivalent in this lower-corridor grid;
        # keep both fields explicit to make any future source comparison obvious.
        row = line_by_index[reflected_line]
        reflected_rows.append(
            {
                "from": active_row["id"],
                "fromLabel": active_row["label"],
                "fromPageLine": active_row["pageLine"],
                "fromCorridorIndex": active_row["corridorIndex"],
                "reflectedPageLine": reflected_line,
                "reflectedCorridorIndex": reflected_corridor,
                "text": row["text"],
                "initial": row["initial"],
                "lastInitial": row["lastInitial"],
                "reflected": classify_row(row, row.get("activeTargets", [])),
            }
        )

    signal_pairs = []
    seen = set()
    for row in records:
        if not classify_row(row, row.get("activeTargets", []))["hasSignal"]:
            continue
        mirror_line = 2 * axis_line - row["lineIndex"]
        mirror_corridor = 2 * axis_corridor - row["corridorIndex"]
        if mirror_line not in line_by_index or mirror_corridor not in row_by_corridor:
            continue
        key = tuple(sorted([row["lineIndex"], mirror_line]))
        if key in seen:
            continue
        seen.add(key)
        mirror_row = line_by_index[mirror_line]
        source_class = classify_row(row, row.get("activeTargets", []))
        mirror_class = classify_row(mirror_row, mirror_row.get("activeTargets", []))
        signal_pairs.append(
            {
                "line": row["lineIndex"],
                "corridor": row["corridorIndex"],
                "mirrorLine": mirror_line,
                "mirrorCorridor": mirror_corridor,
                "sourceStyle": source_class["styleCode"],
                "mirrorStyle": mirror_class["styleCode"],
                "sourceRole": source_class["role"],
                "mirrorRole": mirror_class["role"],
                "sourceText": row["text"],
                "mirrorText": mirror_row["text"],
            }
        )

    reflected_text = " ".join(row["text"] for row in reflected_rows)
    reflected_bold = "".join(row["reflected"]["boldLetters"] for row in reflected_rows)
    reflected_partial = "".join(row["reflected"]["partialBoldLetters"] for row in reflected_rows)
    strict_hits = sorted(set(STRICT_TERMS.findall(reflected_text)))
    active_hits = [row for row in reflected_rows if row["reflected"]["role"] == "active"]
    non_active_signal = [
        row for row in reflected_rows if row["reflected"]["hasSignal"] and row["reflected"]["role"] != "active"
    ]
    summary = {
        "axisPageLine": axis_line,
        "axisCorridorIndex": axis_corridor,
        "activeOrder": [row["from"] for row in reflected_rows],
        "activeHitCount": len(active_hits),
        "activeMissCount": len(reflected_rows) - len(active_hits),
        "nonActiveSignalHitCount": len(non_active_signal),
        "reflectedStyleStream": "".join(row["reflected"]["styleCode"] for row in reflected_rows),
        "reflectedRoleStream": "|".join(row["reflected"]["role"] for row in reflected_rows),
        "reflectedActiveTargetStream": "|".join(
            ",".join(row["reflected"]["activeTargetIds"]) or "-" for row in reflected_rows
        ),
        "initialStream": "".join(row["initial"] for row in reflected_rows),
        "lastInitialStream": "".join(row["lastInitial"] for row in reflected_rows),
        "boldStream": reflected_bold,
        "boldStreamLength": len(reflected_bold),
        "partialBoldStream": reflected_partial,
        "partialBoldStreamLength": len(reflected_partial),
        "signalPairCount": len(signal_pairs),
        "strictInstructionHits": strict_hits,
        "strictInstructionHitCount": len(strict_hits),
        "selectorUnlocked": False,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "G5-axis bold/highlight rescue gate; no OCR, extraction, hashing, or key derivation",
        "inputs": {
            "page76LineLevelCorridor": rel(CORRIDOR_JSON),
            "activeLineUnitReconciliation": rel(ACTIVE_JSON),
            "activeLineCorridorMirrorIndexGate": rel(MIRROR_JSON),
        },
        "summary": summary,
        "activeOrderReflections": reflected_rows,
        "signalPairs": signal_pairs,
        "assessment": [
            "The G5-centered axis keeps three active hits but only by accepting a non-active bold/partial-bold Novogratz line as B4's mirror.",
            "Requiring bold/highlighted rows does not rescue the near miss because the failed B4 reflection is itself a signal-bearing control.",
            "The reflected bold stream is ordinary corridor emphasis and contains no strict unit/order instruction terms.",
        ],
        "decision": {
            "g5AxisBoldHighlightRescueGate": "g5_axis_signal_filter_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Keep the G5-centered axis as a source-validation near miss only unless a clue explicitly names Novogratz/sell as a replacement for B4 or names a line/corridor mirror unit/order rule.",
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md = [
        "# G5 Axis Bold/Highlight Rescue Gate",
        "",
        "Scope: test whether the G5-centered page-line/corridor mirror near miss becomes a selector when constrained to bold/highlight-bearing reflected rows. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Axis page line / corridor: `{axis_line}` / `{axis_corridor}`.",
        f"- Active hits: `{summary['activeHitCount']}`.",
        f"- Active misses: `{summary['activeMissCount']}`.",
        f"- Non-active signal hits: `{summary['nonActiveSignalHitCount']}`.",
        f"- Reflected style stream: `{summary['reflectedStyleStream']}`.",
        f"- Reflected active-target stream: `{summary['reflectedActiveTargetStream']}`.",
        f"- Initial stream: `{summary['initialStream']}`.",
        f"- Last-initial stream: `{summary['lastInitialStream']}`.",
        f"- Bold stream length: `{summary['boldStreamLength']}`.",
        f"- Bold stream: `{summary['boldStream']}`.",
        f"- Partial-bold stream: `{summary['partialBoldStream'] or '-'}`.",
        f"- Strict instruction hits: `{summary['strictInstructionHitCount']}`.",
        "",
        "## Active-Order Reflections",
        "",
    ]
    for row in reflected_rows:
        md.append(
            f"- `{row['from']}` -> L`{row['reflectedPageLine']}`/C`{row['reflectedCorridorIndex']}` `{row['reflected']['role']}` `{row['reflected']['styleCode']}`: `{row['text']}`"
        )
    md.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote the G5-centered mirror axis via a bold/highlight rescue filter.",
            "- The B4 reflection remains the non-active `Novogratz in the tweet, figuring he could sell a` row; it is signal-bearing but not one of the locked active targets.",
            "- The reflected bold and initial streams are ordinary corridor material and supply no unit/order instruction.",
            "- Reopen only if a new source/clue explicitly names Novogratz/sell as a replacement for B4 or names a line/corridor mirror unit/order rule.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
