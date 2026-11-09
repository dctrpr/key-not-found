#!/usr/bin/env python3
"""Inspect the high-res visual boundary where the repaired p78 frame hits G5/O5."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "g5_o5_highres_boundary_cut"

PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
TRICONTACT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
PRIORITY_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"

G5_TEXT = "Volcano Bonds"
O5_TEXT = "shitcoiner at heart."

INSTRUCTION_TERMS = {
    "read",
    "take",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "top",
    "bottom",
    "inside",
    "outside",
    "word",
    "letter",
    "line",
    "key",
    "private",
    "seed",
    "wif",
    "address",
    "index",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def instruction_hits(text: str) -> list[str]:
    return sorted(set(re.findall(r"[a-z]+", text.lower())) & INSTRUCTION_TERMS)


def split_text_at_x(text: str, box: list[float], x: float) -> dict[str, Any]:
    x0, _y0, x1, _y1 = box
    width = max(1.0, x1 - x0)
    ratio = min(1.0, max(0.0, (x - x0) / width))
    idx = round(ratio * len(text))
    return {
        "ratio": round(ratio, 4),
        "index": idx,
        "left": text[:idx],
        "right": text[idx:],
        "combined": f"{text[:idx]}|{text[idx:]}",
    }


def detect_dark_glyph_groups(image: Image.Image, box: list[int]) -> dict[str, Any]:
    crop = image.crop(tuple(box)).convert("RGB")
    width, height = crop.size
    pixels = crop.load()
    col_counts = []
    dark_points = []
    for x in range(width):
        count = 0
        for y in range(height):
            r, g, b = pixels[x, y]
            if r < 80 and g < 80 and b < 80:
                count += 1
                dark_points.append((x, y))
        col_counts.append(count)

    if not dark_points:
        return {"inkBox": None, "groups": [], "gaps": [], "largeGaps": []}

    xs = [p[0] for p in dark_points]
    ys = [p[1] for p in dark_points]
    ink_box = [box[0] + min(xs), box[1] + min(ys), box[0] + max(xs) + 1, box[1] + max(ys) + 1]

    groups = []
    in_group = False
    start = last = 0
    gap = 0
    for i, count in enumerate(col_counts):
        if count:
            if not in_group:
                start = i
                in_group = True
            last = i
            gap = 0
        elif in_group:
            gap += 1
            if gap >= 3:
                groups.append([box[0] + start, box[0] + last + 1])
                in_group = False
                gap = 0
    if in_group:
        groups.append([box[0] + start, box[0] + last + 1])

    gaps = []
    for left, right in zip(groups, groups[1:]):
        gaps.append({"from": left[1], "to": right[0], "width": right[0] - left[1]})

    return {
        "inkBox": ink_box,
        "groups": [{"x0": g[0], "x1": g[1], "width": g[1] - g[0]} for g in groups],
        "gaps": gaps,
        "largeGaps": [gap for gap in gaps if gap["width"] >= 14],
    }


def line_relation(x: float, groups: list[dict[str, int]], gaps: list[dict[str, int]]) -> dict[str, Any]:
    for index, group in enumerate(groups, start=1):
        if group["x0"] <= x <= group["x1"]:
            return {
                "type": "inside_glyph_group",
                "groupIndex": index,
                "group": group,
                "distanceToLeft": round(x - group["x0"], 2),
                "distanceToRight": round(group["x1"] - x, 2),
            }
    for index, gap in enumerate(gaps, start=1):
        if gap["from"] <= x <= gap["to"]:
            return {
                "type": "inside_gap",
                "gapIndex": index,
                "gap": gap,
                "distanceToLeftGlyph": round(x - gap["from"], 2),
                "distanceToRightGlyph": round(gap["to"] - x, 2),
                "isLargeWordGap": gap["width"] >= 14,
            }

    nearest = None
    for gap in gaps:
        dist = min(abs(x - gap["from"]), abs(x - gap["to"]))
        if nearest is None or dist < nearest["distance"]:
            nearest = {"gap": gap, "distance": round(dist, 2)}
    return {"type": "outside_groups", "nearestGap": nearest}


def draw_overlay(image: Image.Image, frame: list[float], g5: list[float], o5: list[float], glyphs: dict[str, Any]) -> str:
    crop_box = [700, 2480, 1765, 3045]
    crop = image.crop(crop_box).convert("RGB")
    draw = ImageDraw.Draw(crop, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    def local(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    frame_l = local(frame)
    g5_l = local(g5)
    o5_l = local(o5)
    draw.rectangle(frame_l, outline=(255, 40, 40, 255), width=5)
    draw.rectangle(g5_l, outline=(30, 30, 30, 255), width=5)
    draw.rectangle(o5_l, outline=(255, 128, 0, 255), width=5)

    x = frame[0] - crop_box[0]
    draw.line([(x, 0), (x, crop.size[1])], fill=(0, 180, 255, 255), width=4)
    draw.text((x + 8, 8), "frame left x=1196", fill=(0, 180, 255, 255), font=font)
    draw.text((g5_l[0], max(0, g5_l[1] - 26)), "G5: Volcano Bonds", fill=(20, 20, 20, 255), font=small)
    draw.text((o5_l[0], max(0, o5_l[1] - 26)), "O5: shitcoiner at heart", fill=(255, 128, 0, 255), font=small)

    for group in glyphs.get("groups", []):
        draw.rectangle(
            [group["x0"] - crop_box[0], o5[1] - crop_box[1], group["x1"] - crop_box[0], o5[3] - crop_box[1]],
            outline=(0, 255, 80, 170),
            width=2,
        )
    for gap in glyphs.get("largeGaps", []):
        draw.rectangle(
            [gap["from"] - crop_box[0], o5[1] - crop_box[1], gap["to"] - crop_box[0], o5[3] - crop_box[1]],
            fill=(0, 180, 255, 90),
        )

    out = OUT_DIR / "g5_o5_highres_boundary_cut_overlay.jpg"
    crop.save(out, quality=92)
    return str(out.relative_to(ROOT))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(PAGE76).convert("RGB")
    tri = load_json(TRICONTACT_JSON)
    priority = load_json(PRIORITY_JSON)
    record = next(r for r in tri["records"] if r["name"] == "g5_edge_touch")
    frame = record["frame"]
    frame_left_x = frame[0]
    grid_left_x = 1194.0

    g5_box = tri["targets"]["G5"]["box"]
    o5_box = tri["targets"]["O5"]["box"]
    glyphs = detect_dark_glyph_groups(image, [round(v) for v in o5_box])
    relation_exact = line_relation(frame_left_x, glyphs["groups"], glyphs["gaps"])
    relation_grid = line_relation(grid_left_x, glyphs["groups"], glyphs["gaps"])

    split_exact = split_text_at_x(O5_TEXT, o5_box, frame_left_x)
    split_grid = split_text_at_x(O5_TEXT, o5_box, grid_left_x)
    g5_split = split_text_at_x(G5_TEXT, g5_box, frame_left_x)

    word_gap_distances = []
    for gap in glyphs["largeGaps"]:
        if frame_left_x < gap["from"]:
            dist = gap["from"] - frame_left_x
        elif frame_left_x > gap["to"]:
            dist = frame_left_x - gap["to"]
        else:
            dist = 0
        word_gap_distances.append({"gap": gap, "distanceFromFrameLeft": round(dist, 2)})

    streams = {
        "g5LeftOfFrame": G5_TEXT,
        "g5RightOfFrame": "",
        "o5ApproxSplitAtExactFrame": split_exact["combined"],
        "o5ApproxSplitAtGridFrame": split_grid["combined"],
        "o5ExactRightSide": split_exact["right"],
        "o5GridRightSide": split_grid["right"],
        "combinedExact": f"{G5_TEXT} | {split_exact['right']}",
        "combinedGrid": f"{G5_TEXT} | {split_grid['right']}",
    }

    overlay = draw_overlay(image, frame, g5_box, o5_box, glyphs)

    assessment = [
        "The repaired p78 frame left edge exactly coincides with the trusted G5 right boundary, so G5 is an endpoint registration contact.",
        "The same vertical edge cuts through O5 inside the word 'shitcoiner', not at a large visual word gap.",
        "The exact dx=-38 line lands in a small glyph gap near the approximate split 'shitc|oiner at heart.'; the dx=-40 grid variant is inside the same glyph cluster and only weakly supports a 'shit|coiner' visual snap.",
        "The nearest large O5 word gaps are the spaces after 'shitcoiner' and after 'at'; the frame edge is far from both, so this is not a clean word-boundary selector.",
        "This preserves the G5/O5 pair as source-registration evidence but closes side-specific high-res boundary cutting as a standalone extraction unit.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "high-res G5/O5 visual boundary cut audit; no key derivation",
        "sources": {
            "page76": str(PAGE76.relative_to(ROOT)),
            "triContact": str(TRICONTACT_JSON.relative_to(ROOT)),
            "priorityCropPack": str(PRIORITY_JSON.relative_to(ROOT)),
        },
        "overlay": overlay,
        "frame": {"scenario": record["name"], "box": frame, "leftX": frame_left_x, "gridLeftX": grid_left_x},
        "targets": {
            "G5": {"label": G5_TEXT, "box": g5_box, "splitAtFrameLeft": g5_split},
            "O5": {
                "label": O5_TEXT,
                "box": o5_box,
                "glyphs": glyphs,
                "lineRelationExact": relation_exact,
                "lineRelationGrid": relation_grid,
                "splitAtExactFrame": split_exact,
                "splitAtGridFrame": split_grid,
                "wordGapDistances": word_gap_distances,
            },
        },
        "streams": streams,
        "instructionHits": {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)},
        "assessment": assessment,
        "decision": "Do not use the G5/O5 side cut as extraction evidence; it is not a clean word/letter boundary under the current high-res scan.",
        "nextMove": "Inspect the high-res visual highlight boundaries for the broader four-anchor O-B-B-O set, looking only for exact boundary coincidences before any text extraction.",
    }

    (OUT_DIR / "g5_o5_highres_boundary_cut.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# G5/O5 High-Res Boundary Cut",
        "",
        "Scope: inspect whether the repaired p78 frame's high-res visual edge creates a side-specific extraction unit at G5/O5. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{overlay}`",
        f"- Frame scenario: `{record['name']}`; frame left x: `{frame_left_x}`; grid left x: `{grid_left_x}`",
        f"- G5 box: `{g5_box}` / text `{G5_TEXT}`",
        f"- O5 box: `{o5_box}` / text `{O5_TEXT}`",
        "",
        "## O5 Pixel Boundary",
        "",
        f"- O5 dark-glyph ink box: `{glyphs['inkBox']}`",
        f"- O5 glyph groups: `{glyphs['groups']}`",
        f"- O5 large word-like gaps: `{glyphs['largeGaps']}`",
        f"- Exact frame relation: `{relation_exact}`",
        f"- Grid-frame relation: `{relation_grid}`",
        f"- Distance from exact frame edge to large word gaps: `{word_gap_distances}`",
        "",
        "## Approximate Text Splits",
        "",
        "| cut | split | right side | note |",
        "|---|---|---|---|",
        f"| G5 at exact frame | `{G5_TEXT}|` | `` | frame touches G5 right endpoint |",
        f"| O5 at exact dx=-38 frame | `{split_exact['combined']}` | `{split_exact['right']}` | proportional text estimate; line is in a small intra-word glyph gap |",
        f"| O5 at grid dx=-40 frame | `{split_grid['combined']}` | `{split_grid['right']}` | proportional text estimate; line is inside/near the same glyph cluster |",
        "",
        "## Streams Checked",
        "",
    ]
    for name, value in streams.items():
        hits = instruction_hits(value)
        lines.append(f"- `{name}` hits={hits or 'none'}: `{value}`")

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            f"- Next move: {result['nextMove']}",
            "",
        ]
    )
    (OUT_DIR / "g5_o5_highres_boundary_cut.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
