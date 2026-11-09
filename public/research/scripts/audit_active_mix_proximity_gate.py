#!/usr/bin/env python3
"""Check whether nearby Typeka Mix islands select the active O4/B4/G5/O5 quartet.

This bounded pass uses the existing page-76 DOCM signal-group audit. It tests
whether Typeka Mix groups near the four locked active targets provide a clean
one-to-one selector, side rule, or instruction-bearing stream.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CORRIDOR_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.json"
ACTIVE_JSON = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json"
OUT = ROOT / "analysis_outputs/docm_format_sources/active_mix_proximity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_mix_proximity_gate.json"
OUT_MD = OUT / "active_mix_proximity_gate.md"
SHEET = OUT / "active_mix_proximity_gate_sheet.jpg"

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


def first_initial(text: str | None) -> str:
    if not text:
        return "-"
    m = re.search(r"[A-Za-z0-9$]", text)
    return m.group(0) if m else "-"


def hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def nearest_mix_rows(corridor: dict[str, Any], active: dict[str, Any]) -> list[dict[str, Any]]:
    active_order = [row["id"] for row in active["records"]]
    active_lines = {row["id"]: row["pageLine"] for row in active["records"]}
    active_corridors = {row["id"]: row["corridorIndex"] for row in active["records"]}
    active_visual = {row["id"]: row["visualState"] for row in active["records"]}
    wanted = set(active_order)
    groups = {row["targetId"]: row for row in corridor["targetNearestMix"] if row["targetId"] in wanted}

    rows = []
    for idx, target_id in enumerate(active_order, start=1):
        row = groups[target_id]
        prev_gap = None if row["prevMixGroup"] is None else row["targetGroup"] - row["prevMixGroup"]
        next_gap = None if row["nextMixGroup"] is None else row["nextMixGroup"] - row["targetGroup"]
        prev_i = first_initial(row["prevMixText"])
        target_i = first_initial(row["targetText"])
        next_i = first_initial(row["nextMixText"])
        triplet = f"{prev_i}{target_i}{next_i}"
        side_choice = "prev" if next_gap is None or (prev_gap is not None and prev_gap <= next_gap) else "next"
        chosen_mix = row["prevMixText"] if side_choice == "prev" else row["nextMixText"]
        chosen_group = row["prevMixGroup"] if side_choice == "prev" else row["nextMixGroup"]
        stream_text = " ".join(part for part in [row["prevMixText"], row["targetText"], row["nextMixText"]] if part)
        rows.append(
            {
                "order": idx,
                "targetId": target_id,
                "targetGroup": row["targetGroup"],
                "targetCode": row["targetCode"],
                "targetText": row["targetText"],
                "pageLine": active_lines[target_id],
                "corridorIndex": active_corridors[target_id],
                "visualState": active_visual[target_id],
                "prevMixGroup": row["prevMixGroup"],
                "prevMixText": row["prevMixText"],
                "prevGapGroups": prev_gap,
                "nextMixGroup": row["nextMixGroup"],
                "nextMixText": row["nextMixText"],
                "nextGapGroups": next_gap,
                "tripletInitials": triplet,
                "nearestSide": side_choice,
                "nearestMixGroup": chosen_group,
                "nearestMixText": chosen_mix,
                "instructionHits": hits(stream_text),
            }
        )
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1680, 1040
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(32)
    normal = font(18)
    small = font(13)
    mono = font(14)
    draw.text((margin, margin), "Active Typeka Mix Proximity Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, margin + 44),
        "Checks whether Typeka Mix islands around O4/B4/G5/O5 form a one-to-one selector.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("active targets", result["summary"]["activeTargetCount"]),
        ("unique nearest Mix groups", result["summary"]["uniqueNearestMixGroupCount"]),
        ("one-to-one Mix map", result["summary"]["oneToOneMixMap"]),
        ("instruction hits", result["summary"]["instructionHitCount"]),
    ]
    widths = [280, 360, 320, 260]
    x = margin
    for (label, value), w in zip(chips, widths):
        draw.rectangle((x, y, x + w, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value), fill=(232, 239, 246), font=mono)
        x += w + 18

    y += 92
    draw.rectangle((margin, y, sheet_w - margin, y + 102), fill=(40, 28, 18), outline=(111, 74, 30), width=2)
    draw.text((margin + 14, y + 12), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 42),
        "O4/B4/G5 share the same surrounding Typeka Mix anchors; O5 uses a different prior Mix anchor.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 70),
        "That is context/provenance, not a clean one-to-one font selector.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 136
    draw.text((margin, y), "Active Targets vs Nearest Mix", fill=(238, 243, 248), font=normal)
    y += 32
    headers = [
        ("target", 10),
        ("grp", 190),
        ("prev Mix", 260),
        ("gap", 600),
        ("next Mix", 670),
        ("gap", 1010),
        ("triplet", 1080),
        ("nearest", 1190),
    ]
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    for label, off in headers:
        draw.text((margin + off, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["rows"]:
        fill = (18, 22, 28) if row["order"] % 2 else (22, 26, 33)
        draw.rectangle((margin, y, sheet_w - margin, y + 54), fill=fill, outline=(48, 58, 70))
        draw.text((margin + 10, y + 9), row["targetId"], fill=(232, 239, 246), font=small)
        draw.text((margin + 190, y + 9), str(row["targetGroup"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 260, y + 9), str(row["prevMixText"] or "-")[:38], fill=(202, 211, 221), font=small)
        draw.text((margin + 600, y + 9), str(row["prevGapGroups"] or "-"), fill=(176, 186, 198), font=mono)
        draw.text((margin + 670, y + 9), str(row["nextMixText"] or "-")[:38], fill=(202, 211, 221), font=small)
        draw.text((margin + 1010, y + 9), str(row["nextGapGroups"] or "-"), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1080, y + 9), row["tripletInitials"], fill=(232, 239, 246), font=mono)
        draw.text((margin + 1190, y + 9), str(row["nearestMixText"] or "-")[:44], fill=(255, 219, 137), font=small)
        y += 56

    y += 24
    draw.text((margin, y), "Shared Anchor Counts", fill=(238, 243, 248), font=normal)
    y += 30
    for key, value in result["summary"]["nearestMixUsage"].items():
        draw.text((margin + 12, y), f"{key}: {value}", fill=(202, 211, 221), font=small)
        y += 22
    sheet.save(SHEET, quality=94)


def main() -> None:
    corridor = load_json(CORRIDOR_JSON)
    active = load_json(ACTIVE_JSON)
    rows = nearest_mix_rows(corridor, active)
    nearest_usage: dict[str, int] = {}
    for row in rows:
        key = row["nearestMixText"] or "-"
        nearest_usage[key] = nearest_usage.get(key, 0) + 1
    triplet_stream = " ".join(row["tripletInitials"] for row in rows)
    nearest_stream = " | ".join(row["nearestMixText"] or "-" for row in rows)
    prev_stream = " | ".join(row["prevMixText"] or "-" for row in rows)
    next_stream = " | ".join(row["nextMixText"] or "-" for row in rows)
    instruction_hit_terms = sorted({term for row in rows for term in row["instructionHits"]})

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active O4/B4/G5/O5 Typeka Mix proximity gate; no OCR or key derivation",
        "inputs": {
            "corridorFontOrderAudit": rel(CORRIDOR_JSON),
            "activeLineUnitReconciliation": rel(ACTIVE_JSON),
        },
        "rows": rows,
        "streams": {
            "tripletInitials": triplet_stream,
            "nearestMixText": nearest_stream,
            "prevMixText": prev_stream,
            "nextMixText": next_stream,
        },
        "summary": {
            "activeTargetCount": len(rows),
            "uniqueNearestMixGroupCount": len({row["nearestMixGroup"] for row in rows if row["nearestMixGroup"] is not None}),
            "uniquePrevMixGroupCount": len({row["prevMixGroup"] for row in rows if row["prevMixGroup"] is not None}),
            "uniqueNextMixGroupCount": len({row["nextMixGroup"] for row in rows if row["nextMixGroup"] is not None}),
            "nearestMixUsage": nearest_usage,
            "oneToOneMixMap": len(nearest_usage) == len(rows) and all(v == 1 for v in nearest_usage.values()),
            "sharedElMikeBandTargets": [row["targetId"] for row in rows if row["prevMixText"] == "El Salvador" and row["nextMixText"] == "Mike Novogratz"],
            "instructionHitCount": len(instruction_hit_terms),
            "instructionHits": instruction_hit_terms,
            "selectorUnlocked": False,
        },
        "assessment": [
            "Typeka Mix proximity does not map one-to-one onto the active quartet.",
            "O4, B4, and G5 are all bracketed by the same broad Mix anchors: `El Salvador` before and `Mike Novogratz` after.",
            "O5 is preceded by `I don't really trust that guy.` and has no following Mix anchor, so the active pattern is shared context plus endpoint, not four independent Mix pointers.",
            "The triplet and nearest-Mix streams contain no instruction terms.",
            "Keep Typeka Mix proximity as corridor/source-comparison evidence only unless a future raw clue names a font-state side or Mix-nearest rule.",
        ],
        "decision": {
            "activeMixProximityAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Reopen Typeka Mix proximity only if source wording names nearest Mix, previous/next font state, or a font-side extraction unit.",
        },
        "sheet": rel(SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Typeka Mix Proximity Gate",
        "",
        "Scope: test whether Typeka Mix islands near the locked O4/B4/G5/O5 targets create a clean selector. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Active targets: `{result['summary']['activeTargetCount']}`",
        f"- Unique nearest Typeka Mix groups: `{result['summary']['uniqueNearestMixGroupCount']}`",
        f"- One-to-one Mix map: `{result['summary']['oneToOneMixMap']}`",
        f"- Shared El/Mike band targets: `{', '.join(result['summary']['sharedElMikeBandTargets'])}`",
        f"- Instruction hit count: `{result['summary']['instructionHitCount']}`",
        "",
        "## Streams",
        "",
        f"- Triplet initials: `{triplet_stream}`",
        f"- Previous Mix stream: `{prev_stream}`",
        f"- Next Mix stream: `{next_stream}`",
        f"- Nearest Mix stream: `{nearest_stream}`",
        "",
        "## Active Rows",
        "",
        "| order | target | group | prev Mix | prev gap | next Mix | next gap | triplet | nearest Mix |",
        "|---:|---|---:|---|---:|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['order']} | `{row['targetId']}` | `{row['targetGroup']}` | "
            f"{row['prevMixText'] or '-'} | `{row['prevGapGroups'] or '-'}` | "
            f"{row['nextMixText'] or '-'} | `{row['nextGapGroups'] or '-'}` | "
            f"`{row['tripletInitials']}` | {row['nearestMixText'] or '-'} |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", ""])
    lines.append("- Typeka Mix proximity is closed as a current-scan selector.")
    lines.append("- Keep it as corridor/source-comparison evidence only; no selector was unlocked.")
    lines.append(f"- Next move: {result['decision']['nextMove']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("tripletInitials:", triplet_stream)
    print("nearestMixUsage:", nearest_usage)
    print("oneToOneMixMap:", result["summary"]["oneToOneMixMap"])
    print("instructionHitCount:", result["summary"]["instructionHitCount"])


if __name__ == "__main__":
    main()
