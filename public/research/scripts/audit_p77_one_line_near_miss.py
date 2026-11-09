#!/usr/bin/env python3
"""Test whether the p77 -> O5 near miss is a real one-line physical rule.

The best true physical near miss sits just below O5 by about one printed line.
This pass quantizes that gap against the measured page-76 lower-corridor line
spacing and asks whether a "move one line up" rule creates a repeated selector
or only one repaired contact.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import math
import statistics
from datetime import datetime
from pathlib import Path

from analyze_front_back_leaf_box_registration import hflip_box
from audit_physical_model_o5_g5_validation import area, intersection, load_targets, source_highlight_items
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
LOWER_MARKS = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
NEAR_MISS = ROOT / "analysis_outputs/source_audit/physical_model_near_miss_rank/physical_model_near_miss_rank.json"
OUT = ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p77_one_line_near_miss.json"
OUT_MD = OUT / "p77_one_line_near_miss.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def translate(box: list[float], dx: float = 0.0, dy: float = 0.0) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def overlap_row(item: dict, mapped: list[float], target: dict, shift_name: str, dy: float) -> dict:
    overlap, inter = intersection(mapped, target["box"])
    return {
        "sourcePage": item["sourcePage"],
        "sourceId": item["id"],
        "sourceKind": item["kind"],
        "sourceLabel": item["label"],
        "shiftName": shift_name,
        "dy": round(dy, 2),
        "mappedBoxOnP76": [round(v, 2) for v in mapped],
        "targetId": target["id"],
        "targetLabel": target["label"],
        "overlapArea": round(overlap, 2),
        "overlapVsSource": round(overlap / max(1.0, area(mapped)), 5),
        "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 5),
        "intersection": [round(v, 2) for v in inter] if inter else None,
        "centerDistance": round(distance(center(mapped), center(target["box"])), 2),
    }


def page76_line_pitch() -> dict:
    data = load_json(LOWER_MARKS)
    rows = data["rowsUsed"]
    y_values = [float(row["y"]) for row in rows]
    deltas = [round(b - a, 2) for a, b in zip(y_values, y_values[1:])]
    return {
        "rowCount": len(rows),
        "firstCanonicalLine": rows[0]["canonicalLineIndex"],
        "lastCanonicalLine": rows[-1]["canonicalLineIndex"],
        "deltas": deltas,
        "median": round(statistics.median(deltas), 2),
        "mean": round(statistics.mean(deltas), 2),
        "min": round(min(deltas), 2),
        "max": round(max(deltas), 2),
        "rows": rows,
    }


def mapped_items(page: int) -> list[dict]:
    width = upright_image(page).width
    out = []
    for item in source_highlight_items(page):
        mapped = [float(v) for v in hflip_box(tuple(item["box"]), width)]
        out.append({**item, "mappedBoxOnP76": mapped})
    return out


def shifted_hits(page: int, shifts: dict[str, float], targets: dict[str, dict]) -> list[dict]:
    hits = []
    for item in mapped_items(page):
        for shift_name, dy in shifts.items():
            shifted = translate(item["mappedBoxOnP76"], dy=dy)
            for target in targets.values():
                row = overlap_row(item, shifted, target, shift_name, dy)
                if row["overlapArea"] > 0:
                    hits.append(row)
    return hits


def main() -> None:
    targets = load_targets()
    near = load_json(NEAR_MISS)["bestTruePhysicalNearMiss"]
    pitch = page76_line_pitch()
    baseline_gap = float(near["verticalGapPx"])
    content_gap = load_json(ROOT / "analysis_outputs/source_audit/content_box_physical_normalization/content_box_physical_normalization.json")[
        "comparison"
    ]["p77ToO5Normalized"]["touchShiftMagnitude"]

    shifts = {
        "one_line_up_median": -pitch["median"],
        "one_line_down_median": pitch["median"],
        "exact_gap_up_control": -baseline_gap,
        "content_box_gap_up_control": -float(content_gap),
    }
    true_hits = {page: shifted_hits(page, shifts, targets) for page in [75, 77]}

    p77_one_line_o5_hits = [
        hit
        for hit in true_hits[77]
        if hit["shiftName"] == "one_line_up_median" and hit["targetId"] == "O5"
    ]
    p77_exact_gap_hits = [
        hit
        for hit in true_hits[77]
        if hit["shiftName"] == "exact_gap_up_control" and hit["targetId"] == "O5"
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p77 physical near miss one-line quantization; no key derivation",
        "linePitch": pitch,
        "nearMiss": near,
        "gapVsLinePitch": {
            "baselineVerticalGapPx": round(baseline_gap, 2),
            "contentBoxVerticalGapPx": round(float(content_gap), 2),
            "medianLinePitchPx": pitch["median"],
            "baselineGapMinusMedianPitchPx": round(baseline_gap - pitch["median"], 2),
            "contentGapMinusMedianPitchPx": round(float(content_gap) - pitch["median"], 2),
        },
        "shiftsTested": {name: round(value, 2) for name, value in shifts.items()},
        "hitSummary": {
            "p75TotalHits": len(true_hits[75]),
            "p77TotalHits": len(true_hits[77]),
            "p77OneLineUpO5HitCount": len(p77_one_line_o5_hits),
            "p77ExactGapO5HitCount": len(p77_exact_gap_hits),
        },
        "hits": true_hits,
        "assessment": [
            "The p77 `It does this by monetizing` near miss is line-quantized: its 71.93 px vertical gap is close to the measured lower-corridor median line pitch of 73.73 px.",
            "However, applying a one-line-up shift to all p77 reflected highlights creates only a single trusted O5/G5 contact, not a repeated physical selector.",
            "The exact-gap control is merely a touch/repair control; it does not add an independent instruction or a second target hit.",
            "Because no source clue says `line up`, `one line`, or `move up`, this remains a physical-scan benchmark rather than extraction material.",
        ],
        "decision": "do_not_promote_one_line_shift_to_selector",
        "nextMove": "Use the 71.93 px / 73.73 px one-line relationship as a benchmark for future physical/source scans. A real source should make the contact natural and repeated, not require an invented line shift.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P77 One-Line Near-Miss Audit",
        "",
        "Scope: test whether the p77 -> O5 physical near miss is a stable one-line-up rule. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Baseline p77 -> O5 vertical gap: `{baseline_gap:.2f}` px.",
        f"- Content-box p77 -> O5 vertical gap: `{float(content_gap):.2f}` px.",
        f"- Page-76 lower-corridor median line pitch: `{pitch['median']}` px.",
        f"- Baseline gap minus median pitch: `{result['gapVsLinePitch']['baselineGapMinusMedianPitchPx']}` px.",
        f"- Content-box gap minus median pitch: `{result['gapVsLinePitch']['contentGapMinusMedianPitchPx']}` px.",
        "",
        "## Shift Hits",
        "",
        "| page | shift | hits | hit labels |",
        "|---:|---|---:|---|",
    ]
    for page in [75, 77]:
        for shift_name in shifts:
            rows = [hit for hit in true_hits[page] if hit["shiftName"] == shift_name]
            labels = "; ".join(f"{hit['sourceLabel']} -> {hit['targetId']} ({hit['overlapVsTarget']})" for hit in rows) or "-"
            lines.append(f"| `{page}` | `{shift_name}` | `{len(rows)}` | {labels} |")

    lines.extend(["", "## Line Pitch Deltas", "", f"- `{pitch['deltas']}`"])
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Decision: `{result['decision']}`.", "", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("median pitch:", pitch["median"])
    print("baseline gap:", baseline_gap)
    print("p77 one-line-up O5 hits:", len(p77_one_line_o5_hits))
    print("p77 total hits:", len(true_hits[77]))


if __name__ == "__main__":
    main()
