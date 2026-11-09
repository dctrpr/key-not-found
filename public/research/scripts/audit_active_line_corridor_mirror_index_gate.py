#!/usr/bin/env python3
"""Test active page-line/corridor indexes under simple mirror axes.

This bounded pass checks whether the locked active indexes
`22 25 27 32` / `4 7 9 14` become a clean selector when mirrored around
candidate half-integer axes in the page-76 lower-corridor line grid. It does
not perform OCR, extraction, hashing, key derivation, seed/WIF checks, address
checks, or broad candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from itertools import combinations_with_replacement
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
OUT = ROOT / "analysis_outputs/source_audit/active_line_corridor_mirror_index_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_line_corridor_mirror_index_gate.json"
OUT_MD = OUT / "active_line_corridor_mirror_index_gate.md"
OUT_SHEET = OUT / "active_line_corridor_mirror_index_gate_sheet.jpg"

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


def axis_values(values: list[int]) -> list[float]:
    axes = {(a + b) / 2.0 for a, b in combinations_with_replacement(values, 2)}
    return sorted(axes)


def exact_int(value: float) -> int | None:
    rounded = round(value)
    return rounded if abs(value - rounded) < 1e-9 else None


def evaluate_domain(
    domain: str,
    values: list[int],
    row_by_value: dict[int, dict[str, Any]],
    active_records: list[dict[str, Any]],
    active_key: str,
) -> dict[str, Any]:
    active_by_value: dict[int, list[dict[str, Any]]] = {}
    for active in active_records:
        active_by_value.setdefault(active[active_key], []).append(active)

    rows = []
    for axis in axis_values(values):
        hits = []
        reflected_texts = []
        for active in active_records:
            src_value = active[active_key]
            reflected = exact_int(2.0 * axis - src_value)
            if reflected is None or reflected not in row_by_value:
                hits.append(
                    {
                        "from": active["id"],
                        "fromValue": src_value,
                        "reflectedValue": reflected,
                        "hitKind": "out_of_range",
                        "text": "",
                    }
                )
                continue
            row = row_by_value[reflected]
            targets = active_by_value.get(reflected, [])
            hit_kind = "active" if targets else ("highlighted_control" if row.get("highlights") else "plain_control")
            reflected_texts.append(row["text"])
            hits.append(
                {
                    "from": active["id"],
                    "fromValue": src_value,
                    "reflectedValue": reflected,
                    "hitKind": hit_kind,
                    "activeTargetsAtReflectedValue": [target["id"] for target in targets],
                    "text": row["text"],
                    "initial": row["initial"],
                    "lastInitial": row["lastInitial"],
                    "highlights": row.get("highlights", []),
                }
            )
        active_hit_count = sum(1 for hit in hits if hit["hitKind"] == "active")
        control_hit_count = sum(1 for hit in hits if hit["hitKind"].endswith("control"))
        highlighted_control_hit_count = sum(1 for hit in hits if hit["hitKind"] == "highlighted_control")
        strict_hits = sorted(set(STRICT_TERMS.findall(" ".join(reflected_texts))))
        rows.append(
            {
                "domain": domain,
                "axis": axis,
                "hits": hits,
                "activeHitCount": active_hit_count,
                "controlHitCount": control_hit_count,
                "highlightedControlHitCount": highlighted_control_hit_count,
                "strictInstructionHits": strict_hits,
                "initialStream": "".join(hit.get("initial", "") for hit in hits if hit.get("initial")),
                "lastInitialStream": "".join(hit.get("lastInitial", "") for hit in hits if hit.get("lastInitial")),
            }
        )
    rows.sort(key=lambda row: (-row["activeHitCount"], row["highlightedControlHitCount"], row["axis"]))
    return {
        "domain": domain,
        "axisCount": len(rows),
        "maxActiveHitCount": max(row["activeHitCount"] for row in rows),
        "allFourAxisCount": sum(1 for row in rows if row["activeHitCount"] == 4),
        "threePlusAxisCount": sum(1 for row in rows if row["activeHitCount"] >= 3),
        "strictInstructionAxisCount": sum(1 for row in rows if row["strictInstructionHits"]),
        "topAxes": rows[:10],
    }


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1500, 980
    img = Image.new("RGB", (width, height), (13, 16, 21))
    draw = ImageDraw.Draw(img)
    title = font(30)
    normal = font(18)
    small = font(14)
    mono = font(14)
    draw.text((40, 30), "Active Line/Corridor Mirror-Index Gate", fill=(242, 245, 249), font=title)
    draw.text(
        (40, 75),
        "Discrete mirror test over page-76 lower-corridor line indexes and corridor indexes.",
        fill=(180, 190, 202),
        font=normal,
    )
    summary = result["summary"]
    y = 120
    for line in [
        f"page-line axes: {summary['pageLineAxisCount']} | all-four: {summary['pageLineAllFourAxisCount']} | three-plus: {summary['pageLineThreePlusAxisCount']}",
        f"corridor axes: {summary['corridorAxisCount']} | all-four: {summary['corridorAllFourAxisCount']} | three-plus: {summary['corridorThreePlusAxisCount']}",
        f"best page-line axis: {summary['bestPageLineAxis']} | best corridor axis: {summary['bestCorridorAxis']}",
        f"strict instruction axis hits: {summary['strictInstructionAxisHits']}",
    ]:
        draw.text((40, y), line, fill=(205, 213, 222), font=mono)
        y += 24

    records = result["corridorRows"]
    table_x = 40
    table_y = 245
    row_h = 42
    draw.text((table_x, table_y - 34), "Lower-Corridor Rows", fill=(242, 245, 249), font=normal)
    for idx, row in enumerate(records):
        y0 = table_y + idx * row_h
        active = row["activeTargets"]
        highlighted = row["highlights"]
        fill = (31, 37, 48) if idx % 2 == 0 else (24, 29, 39)
        if active:
            fill = (70, 57, 29) if any("buying" in a or "shitcoiner" in a for a in active) else (55, 61, 70)
        elif highlighted:
            fill = (42, 36, 45)
        draw.rectangle((table_x, y0, width - 40, y0 + row_h - 2), fill=fill)
        label = f"L{row['lineIndex']:02d} C{row['corridorIndex']:02d}"
        draw.text((table_x + 12, y0 + 11), label, fill=(245, 248, 252), font=mono)
        draw.text((table_x + 105, y0 + 11), row["text"][:112], fill=(218, 225, 234), font=small)
        if active:
            draw.text((width - 350, y0 + 11), ",".join(active), fill=(255, 190, 91), font=mono)
        elif highlighted:
            draw.text((width - 350, y0 + 11), "; ".join(highlighted)[:38], fill=(180, 190, 202), font=mono)

    y = table_y + len(records) * row_h + 34
    draw.text((40, y), "Top Mirror Axes", fill=(242, 245, 249), font=normal)
    y += 32
    for domain in ["pageLine", "corridorIndex"]:
        draw.text((40, y), domain, fill=(255, 207, 90), font=normal)
        y += 25
        for axis in result["domains"][domain]["topAxes"][:4]:
            hits = " | ".join(f"{hit['from']}->{hit['reflectedValue']}:{hit['hitKind']}" for hit in axis["hits"])
            line = f"axis {axis['axis']}: active={axis['activeHitCount']} ctrl={axis['controlHitCount']} init={axis['initialStream']} :: {hits}"
            draw.text((65, y), line[:150], fill=(190, 199, 210), font=mono)
            y += 22
        y += 12

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    corridor = load_json(CORRIDOR_JSON)
    active = load_json(ACTIVE_JSON)
    records = corridor["records"]
    active_records = active["records"]

    active_by_line: dict[int, list[str]] = {}
    active_by_corridor: dict[int, list[str]] = {}
    for row in active_records:
        active_by_line.setdefault(row["pageLine"], []).append(row["id"])
        active_by_corridor.setdefault(row["corridorIndex"], []).append(row["id"])

    corridor_rows = []
    for row in records:
        corridor_rows.append(
            {
                **row,
                "activeTargets": active_by_line.get(row["lineIndex"], []),
            }
        )

    line_by_value = {row["lineIndex"]: row for row in records}
    corridor_by_value = {row["corridorIndex"]: row for row in records}
    page_line_result = evaluate_domain(
        "pageLine",
        [row["lineIndex"] for row in records],
        line_by_value,
        active_records,
        "pageLine",
    )
    corridor_result = evaluate_domain(
        "corridorIndex",
        [row["corridorIndex"] for row in records],
        corridor_by_value,
        active_records,
        "corridorIndex",
    )
    best_page = page_line_result["topAxes"][0]
    best_corridor = corridor_result["topAxes"][0]
    summary = {
        "pageLineAxisCount": page_line_result["axisCount"],
        "corridorAxisCount": corridor_result["axisCount"],
        "pageLineAllFourAxisCount": page_line_result["allFourAxisCount"],
        "corridorAllFourAxisCount": corridor_result["allFourAxisCount"],
        "pageLineThreePlusAxisCount": page_line_result["threePlusAxisCount"],
        "corridorThreePlusAxisCount": corridor_result["threePlusAxisCount"],
        "bestPageLineAxis": best_page["axis"],
        "bestPageLineActiveHitCount": best_page["activeHitCount"],
        "bestCorridorAxis": best_corridor["axis"],
        "bestCorridorActiveHitCount": best_corridor["activeHitCount"],
        "strictInstructionAxisHits": page_line_result["strictInstructionAxisCount"]
        + corridor_result["strictInstructionAxisCount"],
        "selectorUnlocked": False,
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active line/corridor mirror-index gate; no OCR, extraction, hashing, or key derivation",
        "inputs": {
            "page76LineLevelCorridor": rel(CORRIDOR_JSON),
            "activeLineUnitReconciliation": rel(ACTIVE_JSON),
        },
        "activeIndexes": {
            "pageLines": [row["pageLine"] for row in active_records],
            "corridorIndexes": [row["corridorIndex"] for row in active_records],
            "visualStateOrder": "".join(row["visualState"] for row in active_records),
        },
        "corridorRows": corridor_rows,
        "domains": {
            "pageLine": page_line_result,
            "corridorIndex": corridor_result,
        },
        "summary": summary,
        "assessment": [
            "No discrete page-line or corridor-index mirror axis maps all four locked active targets back onto active targets.",
            "The best page-line and corridor axes both hit three active targets, but only by using the G5 line/corridor as the mirror center: O4<->O5 and G5 self-hit while B4 maps to the non-active Novogratz line.",
            "The mirrored streams repeat ordinary corridor prose and contain no strict unit/order instruction terms.",
        ],
        "decision": {
            "activeLineCorridorMirrorIndexGate": "line_corridor_mirror_indexes_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Keep active page-line and corridor indexes as locator/source-validation evidence only unless a clue names a line/corridor mirror axis plus a unit/order rule.",
        },
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md = [
        "# Active Line/Corridor Mirror-Index Gate",
        "",
        "Scope: mirror the locked active page-line and corridor indexes across candidate half-integer axes in the page-76 lower-corridor grid. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Active page lines: `{' '.join(map(str, result['activeIndexes']['pageLines']))}`.",
        f"- Active corridor indexes: `{' '.join(map(str, result['activeIndexes']['corridorIndexes']))}`.",
        f"- Page-line axes tested: `{summary['pageLineAxisCount']}`.",
        f"- Corridor axes tested: `{summary['corridorAxisCount']}`.",
        f"- Page-line all-four active axes: `{summary['pageLineAllFourAxisCount']}`.",
        f"- Corridor all-four active axes: `{summary['corridorAllFourAxisCount']}`.",
        f"- Page-line three-plus active axes: `{summary['pageLineThreePlusAxisCount']}`.",
        f"- Corridor three-plus active axes: `{summary['corridorThreePlusAxisCount']}`.",
        f"- Best page-line axis: `{summary['bestPageLineAxis']}` with `{summary['bestPageLineActiveHitCount']}` active hits.",
        f"- Best corridor axis: `{summary['bestCorridorAxis']}` with `{summary['bestCorridorActiveHitCount']}` active hits.",
        f"- Strict instruction axis hits: `{summary['strictInstructionAxisHits']}`.",
        "",
        "## Best Axes",
        "",
    ]
    for domain in ["pageLine", "corridorIndex"]:
        top = result["domains"][domain]["topAxes"][0]
        hits = ", ".join(
            f"{hit['from']}->{hit['reflectedValue']} {hit['hitKind']} `{hit.get('text', '')}`"
            for hit in top["hits"]
        )
        md.append(
            f"- `{domain}` axis `{top['axis']}`: active hits `{top['activeHitCount']}`, controls `{top['controlHitCount']}`, initial stream `{top['initialStream']}`; {hits}"
        )
    md.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote active line/corridor mirror indexes as a selector.",
            "- No tested axis maps all four active targets back to active targets.",
            "- The best axis is centered on G5: it maps O4 to O5 and G5 to itself, but maps B4 to the non-active `Novogratz` corridor line.",
            "- Reopen only if a new source/clue names line/corridor mirroring and a specific unit/order rule.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
