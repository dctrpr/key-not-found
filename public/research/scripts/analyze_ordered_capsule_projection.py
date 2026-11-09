#!/usr/bin/env python3
"""Project the ordered p73->p79 capsule sequence onto page 76.

The previous pass showed p73 opener capsules fit p79 orange boxes 6-10 almost
perfectly. This pass uses that order, applies the best known p79->p76 mirror
registration, and checks whether the ordered capsule sequence lands on page-76
text/highlight targets or only on non-text art marks.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from analyze_highres_page76_mirror_selector import (
    PAGE76_ORANGE_LABELS,
    area,
    attach_labels,
    center,
    hflip_box,
    intersection,
    manual_page76_grey_boxes,
)
from analyze_page76_nontext_marks import page76_nontext_marks
from analyze_registered_76_79_selector import BEST_TRANSFORM, transform_box
from highres_reflection_extract import ensure_highres_sources, orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/ordered_capsule_projection"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "ordered_capsule_projection.json"
OUT_MD = OUT / "ordered_capsule_projection.md"
OUT_IMG = OUT / "ordered_capsule_projection_overlay.jpg"
OUT_CROP = OUT / "ordered_capsule_projection_crop.jpg"


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.dist(a, b)


def annotate_projection(target_img: Image.Image, target_orange: list[dict], target_grey: list[dict], marks: list[dict], ordered: list[dict]) -> None:
    out = target_img.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for item in target_orange:
        draw.rectangle(item["box"], outline=(255, 100, 0, 210), width=5)
        draw.text((item["box"][0], max(0, item["box"][1] - 24)), f"O{item['index']}", fill=(255, 80, 0, 255))
    for item in target_grey:
        draw.rectangle(item["box"], outline=(0, 210, 255, 210), width=5)
        draw.text((item["box"][0], max(0, item["box"][1] - 24)), f"B{item['index']}", fill=(0, 170, 220, 255))
    for item in marks:
        draw.rectangle(item["box"], outline=(50, 220, 50, 210), width=6)
        draw.text((item["box"][0], max(0, item["box"][1] - 24)), f"M{item['index']}", fill=(20, 160, 40, 255))
    for item in ordered:
        box = item["mappedBox"]
        draw.rectangle(box, outline=(190, 0, 255, 240), width=6)
        draw.text((box[0], max(0, box[1] - 26)), f"C{item['capsuleOrder']}", fill=(190, 0, 255, 255))

    combined = Image.alpha_composite(out, overlay).convert("RGB")
    combined.save(OUT_IMG, quality=94)
    combined.crop((1600, 2350, 2544, 3264)).save(OUT_CROP, quality=94)


def main() -> None:
    ensure_highres_sources()
    target_img = upright_image(76)
    width, height = target_img.size

    target_orange = attach_labels(orange_boxes(76)[0], PAGE76_ORANGE_LABELS)
    target_grey = manual_page76_grey_boxes()
    marks = page76_nontext_marks()
    text_targets = [("orange", t) for t in target_orange] + [("grey", t) for t in target_grey]
    mark_targets = [("mark", m) for m in marks]

    p79_boxes, p79_size = orange_boxes(79)
    ordered = []
    for capsule_order, p79_index in enumerate(range(6, 11), 1):
        source_box = p79_boxes[p79_index - 1]
        hflipped = hflip_box(source_box, p79_size[0])
        mapped = transform_box(hflipped, width, height, BEST_TRANSFORM)
        mapped_center = center(mapped)

        text_hits = []
        for color, target in text_targets:
            inter = intersection(mapped, target["box"])
            if not inter:
                continue
            text_hits.append(
                {
                    "targetColor": color,
                    "targetIndex": target["index"],
                    "targetLabel": target["label"],
                    "overlapVsCapsule": round(area(inter) / area(mapped), 5),
                    "overlapVsTarget": round(area(inter) / area(target["box"]), 5),
                }
            )

        nearest = []
        for kind, target in text_targets + mark_targets:
            target_center = target["center"] if kind == "mark" else center(target["box"])
            nearest.append(
                {
                    "kind": kind,
                    "index": target["index"],
                    "label": target.get("label") or f"non-text mark area {target.get('area')}",
                    "center": tuple(round(v, 2) for v in target_center),
                    "distancePx": round(distance(mapped_center, target_center), 2),
                }
            )
        nearest.sort(key=lambda row: row["distancePx"])

        ordered.append(
            {
                "capsuleOrder": capsule_order,
                "p79OrangeBoxIndex": p79_index,
                "sourceBox": tuple(int(v) for v in source_box),
                "hflipBox": tuple(int(v) for v in hflipped),
                "mappedBox": tuple(int(v) for v in mapped),
                "mappedCenter": tuple(round(v, 2) for v in mapped_center),
                "textHighlightIntersections": text_hits,
                "nearestTargets": nearest[:5],
            }
        )

    mark_sequence = [
        next((n for n in item["nearestTargets"] if n["kind"] == "mark"), None)
        for item in ordered
    ]
    nearest_mark_pattern = "".join(f"M{n['index']}" for n in mark_sequence if n)
    total_text_hits = sum(len(item["textHighlightIntersections"]) for item in ordered)
    annotate_projection(target_img, target_orange, target_grey, marks, ordered)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "ordered visual projection only; no key derivation",
        "transform": BEST_TRANSFORM,
        "overlay": str(OUT_IMG),
        "crop": str(OUT_CROP),
        "targetOrange": target_orange,
        "targetGrey": target_grey,
        "targetNonTextMarks": marks,
        "orderedCapsuleProjection": ordered,
        "summary": {
            "orderedCapsules": len(ordered),
            "textHighlightIntersections": total_text_hits,
            "nearestMarkPattern": nearest_mark_pattern,
            "nearestMarkDistancesPx": [n["distancePx"] for n in mark_sequence if n],
        },
        "assessment": [
            "The p73-derived five-capsule order maps through p79 boxes 6-10 to lower-right page-76 art marks, not to the page-76 text/highlight corridor.",
            f"The nearest non-text mark pattern is {nearest_mark_pattern}; only the first projected capsule is close enough to be a strong mark hit under the current digital registration.",
            "There are no intersections with page-76 orange or grey text-highlight boxes.",
            "This closes the current high-res ordered-capsule projection as a direct page-76 letter selector, while keeping the five-capsule order active as provenance/order evidence if a physical-source transform changes the landing region.",
        ],
        "nextMove": "Do not derive keys from the ordered capsules. If continuing locally, test source/provenance or physical registration; otherwise use the five-capsule order only when a new rule puts it onto text.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Ordered Capsule Projection",
        "",
        "Scope: use the page-73 five-capsule order to order page-79 orange boxes 6-10, then project those five marks through the best known page-79 -> page-76 mirror registration. No key candidates are generated.",
        "",
        f"- Overlay: `{OUT_IMG}`",
        f"- Crop: `{OUT_CROP}`",
        f"- Transform: dx={BEST_TRANSFORM['dx']} dy={BEST_TRANSFORM['dy']} angle={BEST_TRANSFORM['angleDeg']} scale={BEST_TRANSFORM['scale']}",
        "",
        "## Summary",
        "",
        f"- Ordered capsule projections: `{len(ordered)}`",
        f"- Text/highlight intersections: `{total_text_hits}`",
        f"- Nearest non-text mark pattern: `{nearest_mark_pattern}`",
        "",
        "## Ordered Landing Points",
        "",
    ]
    for item in ordered:
        first = item["nearestTargets"][0]
        lines.append(
            f"- C{item['capsuleOrder']} / p79 box {item['p79OrangeBoxIndex']}: mapped={item['mappedBox']} center={item['mappedCenter']} nearest={first['kind']} {first['index']} distance={first['distancePx']} px"
        )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The five-capsule order maps to the lower-right page-76 art/brush region, not the Bukele/IMF/text corridor.",
            "- No projected capsule intersects a page-76 orange or grey text-highlight box under the current high-res digital registration.",
            "- The nearest-mark sequence is `M3 M3 M4 M4 M4`, but only C1 is a tight hit; the rest are too loose to act as a precise selector.",
            "- Close current high-res ordered-capsule projection as a direct letter/text selector. Keep the p73/p79 five-capsule order as provenance/order evidence only if a new physical transform or explicit rule moves it onto text.",
            "",
            "## Next Best Move",
            "",
            "- Stop local key derivation from these five pills. The next useful move is source/physical registration or a new source rule that tells us where the five-item order should be applied.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"wrote {OUT_CROP}")
    print(f"text_hits={total_text_hits} nearest_mark_pattern={nearest_mark_pattern}")


if __name__ == "__main__":
    main()
