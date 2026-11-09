#!/usr/bin/env python3
"""Check whether the unique page-75 adjacent R-K-Y run is mirror-selected.

The repaired page-76 exact-edge signature made the unique adjacent R-K-Y style
run on page 75 worth checking. The direct leaf test failed, so this audit asks
whether the original page79->page75 reflected-highlight system actually lands
on that page-75 R-K-Y run.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE75 = ROOT / "analysis_outputs/3d_article_map/page_75_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/page75_rky_reflection_selection"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page75_rky_reflection_selection.json"
OUT_MD = OUT / "page75_rky_reflection_selection.md"
OUT_OVERLAY = OUT / "page75_rky_reflection_selection_overlay.jpg"

SOURCE_GROUPS = [
    {
        "id": "p75_R",
        "style": "R",
        "label": "epithet / proof of stake / mEthereum lab",
        "wordIndexes": list(range(195, 206)),
        "sourceText": "epithet. Now he's slinging proof of stake at the mEthereum lab.",
    },
    {
        "id": "p75_K",
        "style": "K",
        "label": "Don't fall for shitcoinery.",
        "wordIndexes": list(range(206, 210)),
        "sourceText": "Don't fall for shitcoinery.",
    },
    {
        "id": "p75_Y",
        "style": "Y",
        "label": "Keep your dignity.",
        "wordIndexes": list(range(210, 213)),
        "sourceText": "Keep your dignity.",
    },
]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def union_box(boxes: list[list[float]]) -> list[float]:
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def box_gap(a: list[float], b: list[float]) -> tuple[float, float]:
    horizontal = max(b[0] - a[2], a[0] - b[2], 0.0)
    vertical = max(b[1] - a[3], a[1] - b[3], 0.0)
    return round(horizontal, 2), round(vertical, 2)


def load_data() -> dict:
    return json.loads(MAP_JSON.read_text())


def load_source_groups(data: dict) -> list[dict]:
    page75 = next(page for page in data["pages"] if page["page"] == 75)
    words = {word["index"]: word for word in page75["words"]}
    groups = []
    for spec in SOURCE_GROUPS:
        selected = [words[index] for index in spec["wordIndexes"] if index in words]
        groups.append(
            {
                **spec,
                "ocrText": " ".join(word["text"] for word in selected),
                "box": union_box([word["box"] for word in selected]),
                "wordBoxes": [word["box"] for word in selected],
            }
        )
    return groups


def reflection_rows(data: dict) -> list[dict]:
    rows = []
    for reflection in data["reflections"]:
        if reflection.get("target") != 75:
            continue
        rows.append(
            {
                "id": reflection["id"],
                "sourcePage": reflection["source"],
                "targetPage": reflection["target"],
                "targetBox": [float(v) for v in reflection["targetBox"]],
                "text": reflection.get("text", ""),
                "sourceBox": reflection.get("sourceBox"),
            }
        )
    return rows


def score_reflections(groups: list[dict], reflections: list[dict]) -> list[dict]:
    rows = []
    for group in groups:
        checks = []
        for reflection in reflections:
            inter = intersection(group["box"], reflection["targetBox"])
            overlap = area(inter) if inter else 0.0
            hgap, vgap = box_gap(group["box"], reflection["targetBox"])
            checks.append(
                {
                    "reflectionId": reflection["id"],
                    "sourcePage": reflection["sourcePage"],
                    "reflectionText": reflection["text"],
                    "reflectionTargetBox": reflection["targetBox"],
                    "intersection": inter,
                    "overlapArea": round(overlap, 2),
                    "overlapVsGroup": round(overlap / max(1.0, area(group["box"])), 5),
                    "overlapVsReflection": round(overlap / max(1.0, area(reflection["targetBox"])), 5),
                    "centerDistance": round(math.dist(center(group["box"]), center(reflection["targetBox"])), 2),
                    "horizontalGapPx": hgap,
                    "verticalGapPx": vgap,
                    "nearMiss": overlap == 0 and hgap <= 60 and vgap <= 60,
                }
            )
        rows.append(
            {
                "id": group["id"],
                "style": group["style"],
                "label": group["label"],
                "ocrText": group["ocrText"],
                "box": group["box"],
                "overlapChecks": sorted(checks, key=lambda row: (row["overlapArea"] == 0, row["verticalGapPx"] + row["horizontalGapPx"], row["centerDistance"])),
                "directOverlapCount": sum(1 for row in checks if row["overlapArea"] > 0),
                "nearMissCount": sum(1 for row in checks if row["nearMiss"]),
            }
        )
    return rows


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(groups: list[dict], reflections: list[dict]) -> None:
    im = Image.open(PAGE75).convert("RGB")
    crop_box = [400, 1900, 2440, 2545]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    def tr(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    for reflection in reflections:
        box = reflection["targetBox"]
        if box[3] < crop_box[1] or box[1] > crop_box[3]:
            continue
        draw.rectangle(tr(box), outline=(55, 115, 230), width=3)
        draw_label(draw, (int(box[0] - crop_box[0]), int(box[1] - crop_box[1] - 24)), reflection["id"], (55, 115, 230))

    colors = {"R": (30, 30, 30), "K": (0, 110, 170), "Y": (255, 130, 0)}
    for group in groups:
        color = colors[group["style"]]
        draw.rectangle(tr(group["box"]), outline=color, width=5)
        draw_label(draw, (int(group["box"][0] - crop_box[0]), int(group["box"][1] - crop_box[1] + 5)), f"{group['style']} {group['label']}", color)

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    data = load_data()
    groups = load_source_groups(data)
    reflections = reflection_rows(data)
    scored = score_reflections(groups, reflections)
    direct_total = sum(row["directOverlapCount"] for row in scored)
    near_total = sum(row["nearMissCount"] for row in scored)
    r_nearest = next(row for row in scored if row["id"] == "p75_R")["overlapChecks"][0]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "test whether page79->page75 reflected-highlight boxes select the unique page-75 adjacent R-K-Y run; no key derivation",
        "sourceGroups": groups,
        "reflectionsConsidered": reflections,
        "groupReflectionScores": scored,
        "directOverlapTotal": direct_total,
        "nearMissTotal": near_total,
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "The page79->page75 reflected-highlight system does not directly select the unique page-75 adjacent R-K-Y run.",
            f"Direct overlaps across the three R-K-Y groups: `{direct_total}`.",
            f"Near misses across the three R-K-Y groups: `{near_total}`; the only meaningful near miss is the regular R group sitting just below reflection `{r_nearest['reflectionId']}`.",
            f"That nearest reflected box selects earlier prose (`{r_nearest['reflectionText'][:90]}`), not the `epithet/proof-of-stake` R group itself.",
            "K (`Don't fall for shitcoinery`) and Y (`Keep your dignity`) are not selected by the page79->page75 reflection boxes.",
        ],
        "nextMove": "Close the unique page-75 R-K-Y run as mirror-selected evidence under the current map. Keep focus on the p76 repaired exact-edge trio and source/physical validation.",
    }

    build_overlay(groups, reflections)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-75 R-K-Y Reflection Selection",
        "",
        "Scope: check whether page79->page75 reflected-highlight boxes select the unique adjacent page-75 `R-K-Y` style run. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        f"- Direct overlap total: `{direct_total}`",
        f"- Near-miss total: `{near_total}`",
        "",
        "## R-K-Y Groups",
        "",
        "| style | label | OCR text | box | direct overlaps | near misses | nearest reflected box |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in scored:
        nearest = row["overlapChecks"][0]
        lines.append(
            f"| `{row['style']}` | {row['label']} | `{row['ocrText']}` | `{row['box']}` | {row['directOverlapCount']} | {row['nearMissCount']} | `{nearest['reflectionId']}` gap h/v `{nearest['horizontalGapPx']}/{nearest['verticalGapPx']}` text `{nearest['reflectionText'][:80]}` |"
        )

    lines.extend(["", "## Best Checks", ""])
    for row in scored:
        lines.append(f"### {row['style']} {row['label']}")
        lines.extend(["", "| reflection | overlap group | overlap reflection | hgap | vgap | distance | text |", "|---|---:|---:|---:|---:|---:|---|"])
        for check in row["overlapChecks"][:5]:
            lines.append(
                f"| `{check['reflectionId']}` | `{check['overlapVsGroup']}` | `{check['overlapVsReflection']}` | `{check['horizontalGapPx']}` | `{check['verticalGapPx']}` | `{check['centerDistance']}` | `{check['reflectionText'][:90]}` |"
            )
        lines.append("")

    lines.extend(["## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("direct overlap total:", direct_total)
    print("near miss total:", near_total)


if __name__ == "__main__":
    main()
