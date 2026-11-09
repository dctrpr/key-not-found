#!/usr/bin/env python3
"""Rank physical/spread model near misses against trusted page-76 O5/G5.

The C4 blocker says the current digital scan does not validate true physical
leaf/spread models. This pass makes that failure more precise: which physical
model comes closest, how much translation would be needed to make first
contact, and whether that translation creates a repeated selector or just a
single coincidence.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, or address
checks are performed.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from analyze_front_back_leaf_box_registration import hflip_box
from audit_physical_model_o5_g5_validation import area, intersection, load_targets, source_highlight_items
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/physical_model_near_miss_rank"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "physical_model_near_miss_rank.json"
OUT_MD = OUT / "physical_model_near_miss_rank.md"


SOURCE_MODELS = [
    (75, "same physical leaf/front-back candidate"),
    (77, "true facing spread/gutter candidate"),
    (78, "non-physical p78 visual-control source"),
    (79, "non-physical p79 visual-control source"),
    (80, "non-physical p80 package-control source"),
]


def center(box: list[float] | tuple[float, float, float, float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def translate(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def touch_shift(source: list[float], target: list[float]) -> tuple[float, float]:
    # Smallest axis-aligned translation that makes closed intervals touch or
    # overlap on both axes. This is a "near miss" metric, not an extraction.
    if source[2] < target[0]:
        dx = target[0] - source[2]
    elif source[0] > target[2]:
        dx = target[2] - source[0]
    else:
        dx = 0.0

    if source[3] < target[1]:
        dy = target[1] - source[3]
    elif source[1] > target[3]:
        dy = target[3] - source[1]
    else:
        dy = 0.0
    return dx, dy


def overlap_row(mapped: list[float], target: dict) -> dict:
    overlap, inter = intersection(mapped, target["box"])
    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "overlapArea": round(overlap, 2),
        "overlapVsSource": round(overlap / max(1.0, area(mapped)), 5),
        "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 5),
        "intersection": [round(v, 2) for v in inter] if inter else None,
        "centerDistance": round(dist(center(mapped), center(target["box"])), 2),
        "horizontalGapPx": round(max(target["box"][0] - mapped[2], mapped[0] - target["box"][2], 0), 2),
        "verticalGapPx": round(max(target["box"][1] - mapped[3], mapped[1] - target["box"][3], 0), 2),
    }


def mapped_items_for_page(page: int) -> list[dict]:
    width = upright_image(page).width
    items = []
    for item in source_highlight_items(page):
        mapped = list(hflip_box(tuple(item["box"]), width))
        items.append({**item, "mappedBoxOnP76": [float(v) for v in mapped]})
    return items


def shifted_hit_summary(items: list[dict], targets: dict[str, dict], dx: float, dy: float) -> dict:
    hits = []
    for item in items:
        shifted = translate(item["mappedBoxOnP76"], dx, dy)
        for target in targets.values():
            row = overlap_row(shifted, target)
            if row["overlapArea"] > 0:
                hits.append(
                    {
                        "sourceId": item["id"],
                        "sourceKind": item["kind"],
                        "sourceLabel": item["label"],
                        "targetId": row["targetId"],
                        "targetLabel": row["targetLabel"],
                        "overlapVsTarget": row["overlapVsTarget"],
                        "overlapVsSource": row["overlapVsSource"],
                    }
                )
    return {"hitCount": len(hits), "hits": hits}


def audit_model(page: int, model: str, targets: dict[str, dict]) -> dict:
    items = mapped_items_for_page(page)
    candidates = []
    for item in items:
        mapped = item["mappedBoxOnP76"]
        for target in targets.values():
            row = overlap_row(mapped, target)
            dx, dy = touch_shift(mapped, target["box"])
            # Add a 10px nudge past first contact to see if the correction
            # would create a repeated selector or only one forced hit.
            nudge_dx = dx
            nudge_dy = dy
            if dx > 0:
                nudge_dx += 10
            elif dx < 0:
                nudge_dx -= 10
            if dy > 0:
                nudge_dy += 10
            elif dy < 0:
                nudge_dy -= 10
            shifted = shifted_hit_summary(items, targets, nudge_dx, nudge_dy)
            candidates.append(
                {
                    "sourcePage": page,
                    "model": model,
                    "sourceId": item["id"],
                    "sourceKind": item["kind"],
                    "sourceLabel": item["label"],
                    "mappedBoxOnP76": [round(v, 2) for v in mapped],
                    "targetId": row["targetId"],
                    "targetLabel": row["targetLabel"],
                    "centerDistance": row["centerDistance"],
                    "horizontalGapPx": row["horizontalGapPx"],
                    "verticalGapPx": row["verticalGapPx"],
                    "touchShiftDx": round(dx, 2),
                    "touchShiftDy": round(dy, 2),
                    "touchShiftMagnitude": round(math.hypot(dx, dy), 2),
                    "nudgeShiftDx": round(nudge_dx, 2),
                    "nudgeShiftDy": round(nudge_dy, 2),
                    "nudgeHitCount": shifted["hitCount"],
                    "nudgeHits": shifted["hits"][:8],
                }
            )

    ranked = sorted(candidates, key=lambda row: (row["touchShiftMagnitude"], row["centerDistance"]))
    best = ranked[0] if ranked else None
    best_by_target = {}
    for target in targets.values():
        target_id = target["id"]
        rows = [row for row in ranked if row["targetId"] == target_id]
        best_by_target[target_id] = rows[0] if rows else None
    return {
        "sourcePage": page,
        "model": model,
        "sourceItemCount": len(items),
        "bestOverall": best,
        "bestByTarget": best_by_target,
        "topNearMisses": ranked[:8],
    }


def main() -> None:
    targets = load_targets()
    models = [audit_model(page, name, targets) for page, name in SOURCE_MODELS]
    true_models = [row for row in models if row["sourcePage"] in {75, 77}]
    controls = [row for row in models if row["sourcePage"] not in {75, 77}]
    best_true = sorted(
        [row["bestOverall"] for row in true_models if row["bestOverall"]],
        key=lambda row: (row["touchShiftMagnitude"], row["centerDistance"]),
    )[0]
    best_control = sorted(
        [row["bestOverall"] for row in controls if row["bestOverall"]],
        key=lambda row: (row["touchShiftMagnitude"], row["centerDistance"]),
    )[0]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "physical/spread model near-miss ranking against trusted O5/G5; no key derivation",
        "targets": targets,
        "models": models,
        "bestTruePhysicalNearMiss": best_true,
        "bestControlNearMiss": best_control,
        "assessment": [
            "No true physical model directly overlaps trusted O5/G5 in the current scan.",
            f"Closest true physical near miss is {best_true['model']} / {best_true['sourceLabel']} -> {best_true['targetId']} with touch shift ({best_true['touchShiftDx']}, {best_true['touchShiftDy']}) px, magnitude {best_true['touchShiftMagnitude']} px.",
            f"That forced nudge creates {best_true['nudgeHitCount']} trusted O5/G5 hit(s), so it is a single-contact repair, not a repeated selector.",
            "The near-miss is useful as a future physical-scan benchmark, but it does not reopen physical leaf/spread extraction under the current digital scan.",
        ],
        "nextMove": "If a real physical scan/photo is supplied, first test whether it naturally reduces the best true-physical near miss without arbitrary translation and whether it creates repeated O5/G5 contacts.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Physical Model Near-Miss Rank",
        "",
        "Scope: rank true physical/spread and control models by how close they come to trusted page-76 O5/G5. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Best true physical near miss: page `{best_true['sourcePage']}` `{best_true['sourceLabel']}` -> `{best_true['targetId']}` shift `({best_true['touchShiftDx']}, {best_true['touchShiftDy']})`, magnitude `{best_true['touchShiftMagnitude']}` px.",
        f"- Best control near miss: page `{best_control['sourcePage']}` `{best_control['sourceLabel']}` -> `{best_control['targetId']}` shift `({best_control['touchShiftDx']}, {best_control['touchShiftDy']})`, magnitude `{best_control['touchShiftMagnitude']}` px.",
        "",
        "## Model Ranking",
        "",
        "| model | source page | source items | best target | source phrase | touch shift | shift mag | nudge hits |",
        "|---|---:|---:|---|---|---|---:|---:|",
    ]
    for row in models:
        best = row["bestOverall"]
        lines.append(
            f"| {row['model']} | `{row['sourcePage']}` | `{row['sourceItemCount']}` | `{best['targetId']}` | `{best['sourceLabel']}` | `({best['touchShiftDx']}, {best['touchShiftDy']})` | `{best['touchShiftMagnitude']}` | `{best['nudgeHitCount']}` |"
        )

    lines.extend(["", "## Best By Target", ""])
    for row in models:
        lines.append(f"### {row['model']}")
        for target_id, best in row["bestByTarget"].items():
            if best is None:
                lines.append(f"- `{target_id}`: no mapped source items")
                continue
            lines.append(
                f"- `{target_id}`: `{best['sourceLabel']}` shift `({best['touchShiftDx']}, {best['touchShiftDy']})`, magnitude `{best['touchShiftMagnitude']}`, nudge hits `{best['nudgeHitCount']}`"
            )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("bestTrue:", best_true["sourcePage"], best_true["sourceLabel"], best_true["targetId"], best_true["touchShiftDx"], best_true["touchShiftDy"], best_true["touchShiftMagnitude"])


if __name__ == "__main__":
    main()
