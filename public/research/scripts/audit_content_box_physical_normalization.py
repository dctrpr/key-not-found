#!/usr/bin/env python3
"""Test content-box-normalized physical reflection against page-76 O5/G5.

The simple physical model reflects boxes across the full page width. If the
current digital scan has crop/trim offsets, a lower-parameter alternative is to
normalize each page to its visible ink/content bounding box before mirroring.
This pass asks whether that more forgiving registration naturally fixes the
p77 -> O5 near miss or creates repeated trusted contacts.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from analyze_front_back_leaf_box_registration import hflip_box
from audit_physical_model_o5_g5_validation import area, intersection, load_targets, source_highlight_items
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/content_box_physical_normalization"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "content_box_physical_normalization.json"
OUT_MD = OUT / "content_box_physical_normalization.md"
OUT_OVERLAY = OUT / "content_box_physical_normalization_overlay.jpg"

SOURCE_MODELS = [
    (75, "same physical leaf/front-back candidate"),
    (77, "true facing spread/gutter candidate"),
    (78, "non-physical p78 visual-control source"),
    (79, "non-physical p79 visual-control source"),
    (80, "non-physical p80 package-control source"),
]


def content_bbox(img: Image.Image) -> list[float]:
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    # Detect visible ink and colored layout while ignoring near-white paper.
    dark = np.min(arr, axis=2) < 235
    saturated = (np.max(arr, axis=2) - np.min(arr, axis=2)) > 28
    non_white = dark | saturated
    # Ignore the outermost few pixels so a scan edge cannot define the bbox.
    non_white[:8, :] = False
    non_white[-8:, :] = False
    non_white[:, :8] = False
    non_white[:, -8:] = False
    ys, xs = np.where(non_white)
    if len(xs) == 0:
        return [0.0, 0.0, float(img.width), float(img.height)]
    return [float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1)]


def center(box: list[float] | tuple[float, float, float, float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def touch_shift(source: list[float], target: list[float]) -> tuple[float, float]:
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


def normalized_hflip_box(box: list[float], src_bbox: list[float], dst_bbox: list[float]) -> list[float]:
    sx1, sy1, sx2, sy2 = src_bbox
    dx1, dy1, dx2, dy2 = dst_bbox
    sw = max(1.0, sx2 - sx1)
    sh = max(1.0, sy2 - sy1)
    dw = max(1.0, dx2 - dx1)
    dh = max(1.0, dy2 - dy1)

    # Reflect the normalized x interval; map y by normalized content position.
    nx1 = (box[0] - sx1) / sw
    nx2 = (box[2] - sx1) / sw
    ny1 = (box[1] - sy1) / sh
    ny2 = (box[3] - sy1) / sh
    return [
        dx1 + (1.0 - nx2) * dw,
        dy1 + ny1 * dh,
        dx1 + (1.0 - nx1) * dw,
        dy1 + ny2 * dh,
    ]


def row_for(mapped: list[float], target: dict) -> dict:
    overlap, inter = intersection(mapped, target["box"])
    dx, dy = touch_shift(mapped, target["box"])
    return {
        "targetId": target["id"],
        "targetLabel": target["label"],
        "overlapArea": round(overlap, 2),
        "overlapVsSource": round(overlap / max(1.0, area(mapped)), 5),
        "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 5),
        "intersection": [round(v, 2) for v in inter] if inter else None,
        "centerDistance": round(dist(center(mapped), center(target["box"])), 2),
        "touchShiftDx": round(dx, 2),
        "touchShiftDy": round(dy, 2),
        "touchShiftMagnitude": round(math.hypot(dx, dy), 2),
    }


def mapped_rows_for_page(page: int, mode: str, page_bboxes: dict[int, list[float]], target_bbox: list[float]) -> list[dict]:
    width = upright_image(page).width
    rows = []
    for item in source_highlight_items(page):
        if mode == "full_page_hflip":
            mapped = [float(v) for v in hflip_box(tuple(item["box"]), width)]
        elif mode == "content_box_normalized_hflip":
            mapped = normalized_hflip_box(item["box"], page_bboxes[page], target_bbox)
        else:
            raise ValueError(mode)
        rows.append({**item, "mappedBoxOnP76": [round(v, 2) for v in mapped]})
    return rows


def audit_model(page: int, label: str, mode: str, targets: dict[str, dict], page_bboxes: dict[int, list[float]]) -> dict:
    target_bbox = page_bboxes[76]
    items = mapped_rows_for_page(page, mode, page_bboxes, target_bbox)
    checks = []
    hits = []
    for item in items:
        for target in targets.values():
            row = row_for(item["mappedBoxOnP76"], target)
            record = {
                "sourcePage": page,
                "model": label,
                "mode": mode,
                "sourceId": item["id"],
                "sourceKind": item["kind"],
                "sourceLabel": item["label"],
                "mappedBoxOnP76": item["mappedBoxOnP76"],
                **row,
            }
            checks.append(record)
            if row["overlapArea"] > 0:
                hits.append(record)
    ranked = sorted(checks, key=lambda item: (item["touchShiftMagnitude"], item["centerDistance"]))
    return {
        "sourcePage": page,
        "model": label,
        "mode": mode,
        "sourceItemCount": len(items),
        "directHitCount": len(hits),
        "directHits": hits,
        "bestOverall": ranked[0] if ranked else None,
        "bestByTarget": {
            target_id: next((row for row in ranked if row["targetId"] == target["id"]), None)
            for target_id, target in targets.items()
        },
        "topNearMisses": ranked[:8],
    }


def best_true(models: list[dict], mode: str) -> dict:
    rows = [model["bestOverall"] for model in models if model["mode"] == mode and model["sourcePage"] in {75, 77}]
    return sorted(rows, key=lambda item: (item["touchShiftMagnitude"], item["centerDistance"]))[0]


def draw_overlay(targets: dict[str, dict], model_rows: list[dict]) -> None:
    img = upright_image(76).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    colors = {
        "O5": (255, 120, 0, 210),
        "G5_trusted": (0, 90, 255, 210),
        "full_page_hflip": (255, 0, 0, 160),
        "content_box_normalized_hflip": (0, 160, 60, 170),
    }
    for target in targets.values():
        draw.rectangle(target["box"], outline=colors[target["id"]], width=5)
        draw.text((target["box"][0], target["box"][1] - 22), target["id"], fill=colors[target["id"]])
    for row in model_rows:
        box = row["mappedBoxOnP76"]
        draw.rectangle(box, outline=colors[row["mode"]], width=4)
        draw.text((box[0], box[1] - 18), f"{row['sourcePage']} {row['sourceLabel'][:28]}", fill=colors[row["mode"]])
    img.save(OUT_OVERLAY, quality=92)


def main() -> None:
    targets = load_targets()
    page_bboxes = {page: [round(v, 2) for v in content_bbox(upright_image(page))] for page in [75, 76, 77, 78, 79, 80]}
    models = []
    for page, label in SOURCE_MODELS:
        for mode in ["full_page_hflip", "content_box_normalized_hflip"]:
            models.append(audit_model(page, label, mode, targets, page_bboxes))

    baseline_best = best_true(models, "full_page_hflip")
    normalized_best = best_true(models, "content_box_normalized_hflip")
    p77_baseline = next(model for model in models if model["sourcePage"] == 77 and model["mode"] == "full_page_hflip")
    p77_normalized = next(model for model in models if model["sourcePage"] == 77 and model["mode"] == "content_box_normalized_hflip")
    p77_o5_baseline = p77_baseline["bestByTarget"]["O5"]
    p77_o5_normalized = p77_normalized["bestByTarget"]["O5"]

    overlay_rows = [p77_o5_baseline, p77_o5_normalized]
    draw_overlay(targets, overlay_rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "content-box-normalized physical reflection against trusted page-76 O5/G5; no key derivation",
        "contentBBoxes": page_bboxes,
        "targets": targets,
        "models": models,
        "comparison": {
            "baselineBestTruePhysical": baseline_best,
            "normalizedBestTruePhysical": normalized_best,
            "p77ToO5Baseline": p77_o5_baseline,
            "p77ToO5Normalized": p77_o5_normalized,
            "p77ToO5ShiftMagnitudeChange": round(
                p77_o5_normalized["touchShiftMagnitude"] - p77_o5_baseline["touchShiftMagnitude"], 2
            ),
            "p77DirectHitCountBaseline": p77_baseline["directHitCount"],
            "p77DirectHitCountNormalized": p77_normalized["directHitCount"],
        },
        "assessment": [
            "Content-box normalization is a plausible crop/trim repair, but it does not create direct trusted O5/G5 contacts for the true physical p75/p77 models.",
            f"For the active p77 `It does this by monetizing` -> O5 near miss, the required shift changes from {p77_o5_baseline['touchShiftMagnitude']} px to {p77_o5_normalized['touchShiftMagnitude']} px.",
            f"p77 direct trusted-hit count remains {p77_normalized['directHitCount']} after normalization.",
            "This keeps C4 failed under the current scan and keeps physical/source acquisition as the dependency.",
        ],
        "nextMove": "If a new physical/original-layout source appears, run this same full-page vs content-box benchmark first; do not treat content-box normalization as extraction material by itself.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Content-Box Physical Normalization",
        "",
        "Scope: test whether content-box-normalized physical reflection fixes the p77 -> O5 near miss or creates repeated trusted O5/G5 contacts. No key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY.relative_to(ROOT)}`",
        "",
        "## Content Boxes",
        "",
        "| page | content bbox |",
        "|---:|---|",
    ]
    for page in sorted(page_bboxes):
        lines.append(f"| `{page}` | `{page_bboxes[page]}` |")

    lines.extend(
        [
            "",
            "## True Physical Comparison",
            "",
            f"- Baseline best true physical: page `{baseline_best['sourcePage']}` `{baseline_best['sourceLabel']}` -> `{baseline_best['targetId']}`, shift `{baseline_best['touchShiftMagnitude']}` px.",
            f"- Normalized best true physical: page `{normalized_best['sourcePage']}` `{normalized_best['sourceLabel']}` -> `{normalized_best['targetId']}`, shift `{normalized_best['touchShiftMagnitude']}` px.",
            f"- Active p77 -> O5 baseline shift: `{p77_o5_baseline['touchShiftMagnitude']}` px.",
            f"- Active p77 -> O5 normalized shift: `{p77_o5_normalized['touchShiftMagnitude']}` px.",
            f"- Shift change: `{result['comparison']['p77ToO5ShiftMagnitudeChange']}` px.",
            f"- p77 direct hits after normalization: `{p77_normalized['directHitCount']}`.",
            "",
            "## Model Ranking",
            "",
            "| mode | model | page | direct hits | best target | source phrase | shift |",
            "|---|---|---:|---:|---|---|---:|",
        ]
    )
    for model in models:
        best = model["bestOverall"]
        lines.append(
            f"| `{model['mode']}` | {model['model']} | `{model['sourcePage']}` | `{model['directHitCount']}` | `{best['targetId']}` | `{best['sourceLabel']}` | `{best['touchShiftMagnitude']}` |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("p77 baseline shift:", p77_o5_baseline["touchShiftMagnitude"])
    print("p77 normalized shift:", p77_o5_normalized["touchShiftMagnitude"])
    print("p77 normalized direct hits:", p77_normalized["directHitCount"])


if __name__ == "__main__":
    main()
