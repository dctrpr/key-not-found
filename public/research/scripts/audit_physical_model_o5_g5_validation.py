#!/usr/bin/env python3
"""Validate physical mirror/spread assumptions against trusted O5/G5 boxes.

This pass uses the current best scan and the corrected lower-page trusted boxes:

- O5: page-76 orange `shitcoiner at heart`
- G5: trusted high-res `Volcano Bonds` from lower_page76_mark_pointers

It checks whether true physical models (front/back leaf and facing spread) hit
those targets, and whether the older projected `p76_grey_5` crop accidentally
created the old B5/O5 self-mirror evidence. No key derivation is performed.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from analyze_front_back_leaf_box_registration import grey_items, hflip_box, orange_items
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
MANUAL_GREY_JSON = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
P78_GRAPHIC_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "physical_model_o5_g5_validation.json"
OUT_MD = OUT / "physical_model_o5_g5_validation.md"
OUT_OVERLAY = OUT / "physical_model_o5_g5_validation_overlay.jpg"


def area(box: list[float] | tuple[float, float, float, float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a, b) -> tuple[float, list[float] | None]:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0, None
    box = [x1, y1, x2, y2]
    return area(box), box


def center(box) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def distance(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def reflect_about_axis(box, axis_x: float) -> list[float]:
    return [2 * axis_x - box[2], box[1], 2 * axis_x - box[0], box[3]]


def overlap_record(source_label: str, source_box, target: dict, mapped_box=None) -> dict:
    mapped = list(mapped_box or source_box)
    overlap, inter = intersection(mapped, target["box"])
    return {
        "sourceLabel": source_label,
        "mappedBox": [round(v, 2) for v in mapped],
        "targetId": target["id"],
        "targetLabel": target["label"],
        "targetBox": target["box"],
        "intersection": [round(v, 2) for v in inter] if inter else None,
        "overlapArea": round(overlap, 2),
        "overlapVsSource": round(overlap / max(1.0, area(mapped)), 5),
        "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 5),
        "centerDistance": round(distance(center(mapped), center(target["box"])), 2),
        "horizontalGapPx": round(max(target["box"][0] - mapped[2], mapped[0] - target["box"][2], 0), 2),
        "verticalGapPx": round(max(target["box"][1] - mapped[3], mapped[1] - target["box"][3], 0), 2),
    }


def load_targets() -> dict[str, dict]:
    data = json.loads(MAP_JSON.read_text())
    page = next(row for row in data["pages"] if row["page"] == 76)
    o5 = next(h for h in page["highlights"] if h["id"] == "p76_orange_5")
    o5_target = {"id": "O5", "label": "shitcoiner at heart", "kind": "orange", "box": [float(v) for v in o5["box"]]}

    lower = json.loads(LOWER_MARKS_JSON.read_text())
    g5_box = None
    for item in lower["analyses"]:
        if "Volcano Bonds" in item.get("note", ""):
            g5_box = item["box"]
            break
    if g5_box is None:
        raise RuntimeError("trusted G5 Volcano Bonds box not found")
    g5_target = {"id": "G5_trusted", "label": "Volcano Bonds", "kind": "trusted-grey", "box": [float(v) for v in g5_box]}
    return {"O5": o5_target, "G5": g5_target}


def load_stale_manual_g5() -> dict:
    data = json.loads(MANUAL_GREY_JSON.read_text())
    row = next(item for item in data["rows"] if item["page"] == 76 and item["id"] == "p76_grey_5")
    return {
        "id": "p76_grey_5_stale",
        "label": row["expected"],
        "box": [float(v) for v in row["highresBox"]],
        "source": "manual_grey_highres_crops.json",
    }


def source_highlight_items(page: int) -> list[dict]:
    items = []
    for item in orange_items(page):
        items.append(
            {
                "id": item["id"],
                "sourcePage": page,
                "kind": "orange",
                "label": item["label"],
                "box": [float(v) for v in item["box"]],
            }
        )
    for item in grey_items(page):
        items.append(
            {
                "id": item["id"],
                "sourcePage": page,
                "kind": "grey",
                "label": item["label"],
                "box": [float(v) for v in item["box"]],
            }
        )
    return items


def audit_source_page(source_page: int, model: str, targets: dict[str, dict]) -> dict:
    width = upright_image(source_page).width
    rows = []
    for item in source_highlight_items(source_page):
        mapped = list(hflip_box(tuple(item["box"]), width))
        target_rows = [overlap_record(item["label"], item["box"], target, mapped) for target in targets.values()]
        rows.append(
            {
                **item,
                "mappedBoxOnP76": [round(v, 2) for v in mapped],
                "targetChecks": target_rows,
                "bestTargetDistance": min(row["centerDistance"] for row in target_rows),
                "hasOverlap": any(row["overlapArea"] > 0 for row in target_rows),
            }
        )
    overlaps = [row for row in rows if row["hasOverlap"]]
    nearest = sorted(rows, key=lambda row: row["bestTargetDistance"])[:8]
    return {
        "model": model,
        "sourcePage": source_page,
        "targetPage": 76,
        "sourceItemCount": len(rows),
        "overlapCount": len(overlaps),
        "overlaps": overlaps,
        "nearestItems": nearest,
    }


def p78_graphic_check(targets: dict[str, dict]) -> dict:
    data = json.loads(P78_GRAPHIC_JSON.read_text())
    box = [float(v) for v in data["reflectedBoxOnP76"]]
    return {
        "source": "p78 lower pull-quote reflected frame",
        "mappedBoxOnP76": box,
        "targetChecks": [overlap_record("p78 lower pull-quote frame", box, target, box) for target in targets.values()],
    }


def stale_vs_trusted_check(targets: dict[str, dict]) -> dict:
    stale = load_stale_manual_g5()
    trusted_g5 = targets["G5"]
    o5 = targets["O5"]
    axes = {
        "page_center": 1272.0,
        "old_orange_bbox_center_axis": 1322.0,
    }
    axis_rows = []
    for name, axis_x in axes.items():
        stale_reflected = reflect_about_axis(stale["box"], axis_x)
        trusted_reflected = reflect_about_axis(trusted_g5["box"], axis_x)
        axis_rows.append(
            {
                "axisName": name,
                "axisX": axis_x,
                "staleG5ToO5": overlap_record("stale projected p76_grey_5", stale["box"], o5, stale_reflected),
                "trustedG5ToO5": overlap_record("trusted Volcano Bonds", trusted_g5["box"], o5, trusted_reflected),
            }
        )
    return {
        "staleManualG5": stale,
        "trustedG5": trusted_g5,
        "o5": o5,
        "axisChecks": axis_rows,
    }


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(targets: dict[str, dict], stale_check: dict, p78_check: dict) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [650, 2350, 2300, 3060]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    def tr(box):
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    for target in targets.values():
        color = (255, 100, 0) if target["id"] == "O5" else (0, 70, 255)
        draw.rectangle(tr(target["box"]), outline=color, width=5)
        draw_label(draw, (int(target["box"][0] - crop_box[0]), int(target["box"][1] - crop_box[1] - 30)), target["id"], color)

    stale = stale_check["staleManualG5"]
    draw.rectangle(tr(stale["box"]), outline=(180, 0, 180), width=4)
    draw_label(draw, (int(stale["box"][0] - crop_box[0]), int(stale["box"][1] - crop_box[1] + 8)), "stale p76_grey_5", (180, 0, 180))

    axis_x = 1322.0
    draw.line((axis_x - crop_box[0], 0, axis_x - crop_box[0], crop.height), fill=(40, 160, 40), width=4)
    stale_ref = reflect_about_axis(stale["box"], axis_x)
    trusted_ref = reflect_about_axis(targets["G5"]["box"], axis_x)
    draw.rectangle(tr(stale_ref), outline=(255, 0, 180), width=3)
    draw.rectangle(tr(trusted_ref), outline=(0, 170, 255), width=3)
    draw.rectangle(tr(p78_check["mappedBoxOnP76"]), outline=(255, 0, 0), width=4)
    draw_label(draw, (int(p78_check["mappedBoxOnP76"][0] - crop_box[0]), int(p78_check["mappedBoxOnP76"][1] - crop_box[1] + 8)), "p78 frame", (255, 0, 0))
    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    targets = load_targets()
    physical_models = [
        audit_source_page(75, "same physical leaf front/back candidate: 75 -> 76", targets),
        audit_source_page(77, "true facing spread candidate: 77 -> 76", targets),
        audit_source_page(78, "non-physical control / known p78 visual source: 78 -> 76", targets),
        audit_source_page(79, "non-physical control / known p79 visual source: 79 -> 76", targets),
        audit_source_page(80, "non-physical control / package source: 80 -> 76", targets),
    ]
    p78_check = p78_graphic_check(targets)
    stale_check = stale_vs_trusted_check(targets)
    build_overlay(targets, stale_check, p78_check)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "physical/source model validation against trusted O5/G5; no key derivation",
        "targets": targets,
        "physicalModels": physical_models,
        "p78GraphicFrameCheck": p78_check,
        "staleVsTrustedG5": stale_check,
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "Using the trusted high-res G5 `Volcano Bonds` box, true physical page models do not naturally validate the O5/G5 pair on page 76.",
            "The old page-76 self-mirror B5/O5 result is driven by stale projected `p76_grey_5` geometry near O5, not by the trusted Volcano Bonds box at its actual page-76 location.",
            "The p78 graphic frame still supports the lower corridor: it overlaps O5 and sits adjacent to trusted G5, but it is not a true leaf/spread validation.",
            "This demotes page-76 G5/O5 self-mirror as exact geometry and keeps G5/O5 as semantic/corridor evidence only until source registration improves.",
        ],
        "nextMove": "Update future geometry tests to use only trusted lower boxes for G5. Re-run any high-value G5/O5 conclusions only when they depend on exact geometry; keep p78 frame/O5 endpoint as active orientation evidence.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Physical Model O5/G5 Validation",
        "",
        "Scope: validate physical leaf/spread assumptions against trusted O5/G5 page-76 boxes. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Target Boxes",
        "",
        f"- O5 `shitcoiner at heart`: `{targets['O5']['box']}`",
        f"- Trusted G5 `Volcano Bonds`: `{targets['G5']['box']}`",
        f"- Stale projected `p76_grey_5`: `{stale_check['staleManualG5']['box']}`",
        "",
        "## Physical / Source Model Checks",
        "",
        "| model | source page | source items | overlaps with trusted O5/G5 | nearest item summary |",
        "|---|---:|---:|---:|---|",
    ]
    for model in physical_models:
        nearest = model["nearestItems"][0] if model["nearestItems"] else None
        nearest_text = "-"
        if nearest:
            checks = sorted(nearest["targetChecks"], key=lambda row: row["centerDistance"])
            best = checks[0]
            nearest_text = f"{nearest['kind']} `{nearest['label']}` -> {best['targetId']} dist {best['centerDistance']}px"
        lines.append(
            f"| {model['model']} | `{model['sourcePage']}` | `{model['sourceItemCount']}` | `{model['overlapCount']}` | {nearest_text} |"
        )

    lines.extend(["", "## P78 Graphic Frame Check", ""])
    for row in p78_check["targetChecks"]:
        lines.append(
            f"- p78 frame -> `{row['targetId']}` `{row['targetLabel']}`: overlapVsTarget `{row['overlapVsTarget']}`, horizontalGap `{row['horizontalGapPx']}px`, verticalGap `{row['verticalGapPx']}px`, distance `{row['centerDistance']}px`"
        )

    lines.extend(["", "## Stale vs Trusted G5 Self-Mirror", ""])
    for row in stale_check["axisChecks"]:
        stale_row = row["staleG5ToO5"]
        trusted_row = row["trustedG5ToO5"]
        lines.append(f"### `{row['axisName']}` x=`{row['axisX']}`")
        lines.append(
            f"- stale projected `p76_grey_5` -> O5: overlapVsTarget `{stale_row['overlapVsTarget']}`, distance `{stale_row['centerDistance']}px`"
        )
        lines.append(
            f"- trusted G5 -> O5: overlapVsTarget `{trusted_row['overlapVsTarget']}`, distance `{trusted_row['centerDistance']}px`, verticalGap `{trusted_row['verticalGapPx']}px`"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("physical overlap counts:", [(m["sourcePage"], m["overlapCount"]) for m in physical_models])


if __name__ == "__main__":
    main()
