#!/usr/bin/env python3
"""Test the only adjacent R-K-Y style run on page 75 as a leaf clue for p76.

The repaired p78 frame exact-edge signature on page 76 has style order R-K-Y:
regular `should sell`, black `Volcano Bonds`, yellow `shitcoiner at heart`.
The DOCM rarity audit found only one adjacent R-K-Y style sequence in the
article, on page 75. Since pages 75/76 are a physical leaf pair, this pass asks
whether that unique page-75 adjacent R-K-Y sequence lands on the repaired p76
exact-edge trio under hold-to-light mirroring.

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
CONTACT_JSON = ROOT / "analysis_outputs/source_audit/tricontact_frame_contact_stability/tricontact_frame_contact_stability.json"
RKY_JSON = ROOT / "analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/page75_adjacent_rky_leaf_to_p76"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page75_adjacent_rky_leaf_to_p76.json"
OUT_MD = OUT / "page75_adjacent_rky_leaf_to_p76.md"
OUT_OVERLAY = OUT / "page75_adjacent_rky_leaf_to_p76_overlay.jpg"


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

TARGET_IDS = ["should_sell", "G5", "O5"]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def union_box(boxes: list[list[float]]) -> list[float]:
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def hflip_box(box: list[float], width: float) -> list[float]:
    return [round(width - box[2], 2), round(box[1], 2), round(width - box[0], 2), round(box[3], 2)]


def translate_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [round(box[0] + dx, 2), round(box[1] + dy, 2), round(box[2] + dx, 2), round(box[3] + dy, 2)]


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]


def gap(mapped: list[float], target: list[float]) -> tuple[float, float]:
    horizontal = max(target[0] - mapped[2], mapped[0] - target[2], 0.0)
    vertical = max(target[1] - mapped[3], mapped[1] - target[3], 0.0)
    return round(horizontal, 2), round(vertical, 2)


def load_page(page_no: int) -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == page_no)


def load_source_groups() -> list[dict]:
    page75 = load_page(75)
    words = {word["index"]: word for word in page75["words"]}
    groups = []
    for spec in SOURCE_GROUPS:
        selected = [words[idx] for idx in spec["wordIndexes"] if idx in words]
        groups.append(
            {
                **spec,
                "ocrText": " ".join(word["text"] for word in selected),
                "box": union_box([word["box"] for word in selected]),
                "wordBoxes": [word["box"] for word in selected],
            }
        )
    return groups


def load_targets() -> list[dict]:
    data = json.loads(CONTACT_JSON.read_text())
    scenario = next(row for row in data["scenarios"] if row["name"] == "g5_edge_touch_dx_minus_38")
    events = {event["id"]: event for event in scenario["events"]}
    out = []
    for target_id in TARGET_IDS:
        event = events[target_id]
        style = {"should_sell": "R", "G5": "K", "O5": "Y"}[target_id]
        out.append(
            {
                "id": target_id,
                "style": style,
                "label": event["label"],
                "box": [float(v) for v in event["box"]],
            }
        )
    return out


def pair_metrics(mapped: list[dict], targets: list[dict]) -> list[dict]:
    rows = []
    for src, target in zip(mapped, targets):
        inter = intersection(src["mappedBox"], target["box"])
        overlap = area(inter) if inter else 0.0
        hgap, vgap = gap(src["mappedBox"], target["box"])
        rows.append(
            {
                "sourceId": src["id"],
                "sourceStyle": src["style"],
                "sourceLabel": src["label"],
                "sourceOcrText": src["ocrText"],
                "mappedBox": src["mappedBox"],
                "targetId": target["id"],
                "targetStyle": target["style"],
                "targetLabel": target["label"],
                "targetBox": target["box"],
                "intersection": inter,
                "overlapArea": round(overlap, 2),
                "overlapVsSource": round(overlap / max(1.0, area(src["mappedBox"])), 5),
                "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 5),
                "centerDistance": round(math.dist(center(src["mappedBox"]), center(target["box"])), 2),
                "horizontalGapPx": hgap,
                "verticalGapPx": vgap,
            }
        )
    return rows


def analyze_transform(name: str, source_groups: list[dict], targets: list[dict], width: float, dx: float, dy: float) -> dict:
    mapped = []
    for group in source_groups:
        flipped = hflip_box(group["box"], width)
        mapped.append({**group, "hflipBox": flipped, "mappedBox": translate_box(flipped, dx, dy)})
    pairs = pair_metrics(mapped, targets)
    mean_distance = sum(row["centerDistance"] for row in pairs) / len(pairs)
    max_distance = max(row["centerDistance"] for row in pairs)
    overlap_pairs = [row for row in pairs if row["overlapArea"] > 0]
    return {
        "name": name,
        "dx": round(dx, 2),
        "dy": round(dy, 2),
        "mappedSources": mapped,
        "pairs": pairs,
        "overlapPairCount": len(overlap_pairs),
        "meanCenterDistancePx": round(mean_distance, 2),
        "maxCenterDistancePx": round(max_distance, 2),
        "totalOverlapVsTarget": round(sum(row["overlapVsTarget"] for row in pairs), 5),
    }


def bounded_best(source_groups: list[dict], targets: list[dict], width: float) -> tuple[float, float]:
    best = None
    for dx in range(-180, 181, 20):
        for dy in range(-180, 181, 20):
            analysis = analyze_transform("candidate", source_groups, targets, width, dx, dy)
            score = (-analysis["meanCenterDistancePx"], analysis["overlapPairCount"], -abs(dx) - abs(dy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
    assert best is not None
    return float(best[1]), float(best[2])


def unconstrained_centroid_shift(source_groups: list[dict], targets: list[dict], width: float) -> tuple[float, float]:
    diffs = []
    for group, target in zip(source_groups, targets):
        flipped = hflip_box(group["box"], width)
        fc = center(flipped)
        tc = center(target["box"])
        diffs.append((tc[0] - fc[0], tc[1] - fc[1]))
    return (
        sum(dx for dx, _ in diffs) / len(diffs),
        sum(dy for _, dy in diffs) / len(diffs),
    )


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(analyses: list[dict], targets: list[dict]) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [620, 2060, 2220, 3060]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)
    colors = {
        "raw_leaf_hflip": (230, 45, 45),
        "prior_leaf_best_dx_0_dy_minus_180": (120, 120, 120),
        "bounded_best_small_translation": (20, 145, 75),
        "unconstrained_centroid_fit": (150, 55, 190),
    }

    def tr(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    for target in targets:
        color = (255, 140, 0) if target["style"] == "Y" else (30, 80, 220) if target["style"] == "K" else (20, 20, 20)
        draw.rectangle(tr(target["box"]), outline=color, width=5)
        draw_label(draw, (int(target["box"][0] - crop_box[0]), int(target["box"][1] - crop_box[1] - 25)), f"target {target['style']} {target['label']}", color)

    # Draw only raw, bounded, and centroid to avoid clutter; prior leaf best is recorded in JSON/MD.
    for analysis in analyses:
        if analysis["name"] not in {"raw_leaf_hflip", "bounded_best_small_translation", "unconstrained_centroid_fit"}:
            continue
        color = colors[analysis["name"]]
        for src in analysis["mappedSources"]:
            draw.rectangle(tr(src["mappedBox"]), outline=color, width=3)
            draw_label(draw, (int(src["mappedBox"][0] - crop_box[0]), int(src["mappedBox"][1] - crop_box[1] + 3)), f"{analysis['name']} {src['style']}", color)

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    page75 = load_page(75)
    source_groups = load_source_groups()
    targets = load_targets()
    width = float(page75["width"])
    rky = json.loads(RKY_JSON.read_text())

    best_dx, best_dy = bounded_best(source_groups, targets, width)
    centroid_dx, centroid_dy = unconstrained_centroid_shift(source_groups, targets, width)
    analyses = [
        analyze_transform("raw_leaf_hflip", source_groups, targets, width, 0.0, 0.0),
        analyze_transform("prior_leaf_best_dx_0_dy_minus_180", source_groups, targets, width, 0.0, -180.0),
        analyze_transform("bounded_best_small_translation", source_groups, targets, width, best_dx, best_dy),
        analyze_transform("unconstrained_centroid_fit", source_groups, targets, width, centroid_dx, centroid_dy),
    ]

    raw = analyses[0]
    bounded = analyses[2]
    centroid = analyses[3]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-75 adjacent R-K-Y style sequence mirrored as physical leaf mate onto repaired p76 exact-edge trio; no key derivation",
        "sourceRkyRecord": {
            "source": str(RKY_JSON.relative_to(ROOT)),
            "adjacentPage75Window": next(row for row in rky["pageRecords"] if row["page"] == 75)["adjacentRkyWindows"][0],
        },
        "sourceGroups": source_groups,
        "targets": targets,
        "transforms": analyses,
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "The only adjacent R-K-Y style sequence is real, but it does not land on the repaired page-76 exact-edge trio under raw page75->page76 hold-to-light mirroring.",
            f"Raw hflip gives zero overlaps, mean center distance `{raw['meanCenterDistancePx']}` px, max `{raw['maxCenterDistancePx']}` px.",
            f"The bounded best small translation is dx=`{bounded['dx']}`, dy=`{bounded['dy']}`, at the edge of the allowed range; it creates only one weak/forced overlap, where the wide page-75 regular group covers `should sell`, while the K and Y groups still miss G5/O5.",
            f"An unconstrained centroid fit would require dx=`{centroid['dx']}`, dy=`{centroid['dy']}`, which is far outside the previously allowed physical crop-correction range and still does not create a clean human-readable registration.",
            "Therefore the page-75 adjacent R-K-Y rarity is a typography coincidence/provenance echo, not a physical leaf selector for the p76 repaired exact-edge trio under the current best scan.",
        ],
        "nextMove": "Keep p75 adjacent R-K-Y closed as a leaf selector. Continue using the p76 repaired exact-edge trio plus M3/O5/G5 tri-contact only as a benchmark for new source/physical material.",
    }

    build_overlay(analyses, targets)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-75 Adjacent R-K-Y Leaf Test",
        "",
        "Scope: test whether the only adjacent `R-K-Y` style sequence, on page 75, maps onto the repaired page-76 exact-edge trio under physical leaf mirroring. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Source And Target",
        "",
        "| role | style | label | OCR/source text | box |",
        "|---|---|---|---|---|",
    ]
    for group in source_groups:
        lines.append(f"| page75 source | `{group['style']}` | {group['label']} | `{group['ocrText']}` | `{group['box']}` |")
    for target in targets:
        lines.append(f"| page76 target | `{target['style']}` | {target['label']} | - | `{target['box']}` |")

    lines.extend(["", "## Transform Summary", "", "| transform | dx | dy | overlaps | mean distance | max distance | total target overlap |", "|---|---:|---:|---:|---:|---:|---:|"])
    for analysis in analyses:
        lines.append(
            f"| `{analysis['name']}` | `{analysis['dx']}` | `{analysis['dy']}` | {analysis['overlapPairCount']} | `{analysis['meanCenterDistancePx']}` | `{analysis['maxCenterDistancePx']}` | `{analysis['totalOverlapVsTarget']}` |"
        )

    lines.extend(["", "## Pair Details", ""])
    for analysis in analyses:
        lines.append(f"### {analysis['name']}")
        lines.extend(["", "| source -> target | distance | hgap | vgap | overlap source | overlap target |", "|---|---:|---:|---:|---:|---:|"])
        for row in analysis["pairs"]:
            lines.append(
                f"| `{row['sourceLabel']}` -> `{row['targetLabel']}` | `{row['centerDistance']}` | `{row['horizontalGapPx']}` | `{row['verticalGapPx']}` | `{row['overlapVsSource']}` | `{row['overlapVsTarget']}` |"
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
    print("raw overlaps:", raw["overlapPairCount"], "mean distance:", raw["meanCenterDistancePx"])
    print("bounded best:", best_dx, best_dy, "overlaps:", bounded["overlapPairCount"], "mean distance:", bounded["meanCenterDistancePx"])
    print("centroid fit:", round(centroid_dx, 2), round(centroid_dy, 2), "overlaps:", centroid["overlapPairCount"])


if __name__ == "__main__":
    main()
