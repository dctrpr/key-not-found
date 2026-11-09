#!/usr/bin/env python3
"""Drill into the one surviving page-76 self-mirror pair.

The previous page-76 self-mirror audit found exactly one repeatable pair:
B5 "Volcano Bonds" and O5 "shitcoiner at heart.". This script asks a
smaller question: does that overlap select a narrow word/letter span, or does
it cover most of both phrases and therefore function only as a local anchor?

No key candidates are generated.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from highres_reflection_extract import ensure_highres_sources, upright_image


ROOT = Path(__file__).resolve().parents[1]
SELF_JSON = ROOT / "analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror.json"
CANONICAL_JSON = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT = ROOT / "analysis_outputs/source_audit/page76_b5_o5_pair"
OUT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT / "page76_b5_o5_pair.json"
OUT_MD = OUT / "page76_b5_o5_pair.md"
OUT_IMG = OUT / "page76_b5_o5_pair_crop.jpg"

AXIS_NAME = "orange_bbox_center"


def frac_span(inner: list[float] | tuple[float, float, float, float], outer: list[float] | tuple[float, float, float, float]) -> dict:
    ix1, iy1, ix2, iy2 = inner
    ox1, oy1, ox2, oy2 = outer
    ow = ox2 - ox1
    oh = oy2 - oy1
    return {
        "x": [round((ix1 - ox1) / ow, 4), round((ix2 - ox1) / ow, 4)] if ow else [None, None],
        "y": [round((iy1 - oy1) / oh, 4), round((iy2 - oy1) / oh, 4)] if oh else [None, None],
    }


def mirror_source_x_fraction(reflected_fraction: list[float]) -> list[float]:
    """Convert a reflected-box x span back into the source phrase's x order."""
    left, right = reflected_fraction
    return [round(1 - right, 4), round(1 - left, 4)]


def approx_text_span(text: str, x_fraction: list[float]) -> dict:
    """Approximate selected characters from a horizontal box fraction.

    This is only a character-width approximation. It is useful for deciding
    whether a selection is narrow or broad, not for final extraction.
    """
    n = len(text)
    start = max(0, min(n, math.floor(x_fraction[0] * n)))
    end = max(start, min(n, math.ceil(x_fraction[1] * n)))
    return {
        "textLength": n,
        "charRangeEstimate": [start, end],
        "selectedApprox": text[start:end],
        "omittedLeftApprox": text[:start],
        "omittedRightApprox": text[end:],
    }


def page76_lines() -> list[dict]:
    data = json.loads(CANONICAL_JSON.read_text())
    for page in data["pages"].values():
        if page.get("articlePage") == 76:
            return page["lines"]
    raise RuntimeError("page 76 not found in canonical char model")


def extract_corridor(lines: list[dict]) -> list[dict]:
    wanted = []
    for row in lines:
        text = row["text"].rstrip("\n")
        if any(key in text for key in ("IMF", "Volcano", "Novogratz", "shitcoiner")):
            wanted.append(
                {
                    "lineIndex": row["lineIndex"],
                    "start": row["start"],
                    "end": row["end"],
                    "text": text,
                }
            )
    return wanted


def best_axis_edges() -> list[dict]:
    data = json.loads(SELF_JSON.read_text())
    for axis in data["axes"]:
        if axis["axisName"] == AXIS_NAME:
            return axis["meaningfulEdges"]
    raise RuntimeError(f"axis not found: {AXIS_NAME}")


def analyze_edge(edge: dict) -> dict:
    intersection = edge["intersection"]
    reflected_box = edge["reflectedBox"]
    target_box = edge["targetBox"]
    source_reflected_fraction = frac_span(intersection, reflected_box)
    source_original_x = mirror_source_x_fraction(source_reflected_fraction["x"])
    target_fraction = frac_span(intersection, target_box)
    return {
        "sourceId": edge["sourceId"],
        "sourceLabel": edge["sourceLabel"],
        "targetId": edge["targetId"],
        "targetLabel": edge["targetLabel"],
        "sourceBox": edge["sourceBox"],
        "reflectedBox": reflected_box,
        "targetBox": target_box,
        "intersection": intersection,
        "overlapVsSource": edge["overlapVsSource"],
        "overlapVsTarget": edge["overlapVsTarget"],
        "centerDistance": edge["centerDistance"],
        "sourceReflectedFraction": source_reflected_fraction,
        "sourceOriginalXFractionEstimate": source_original_x,
        "sourceOriginalTextEstimate": approx_text_span(edge["sourceLabel"], source_original_x),
        "targetFraction": target_fraction,
        "targetTextEstimate": approx_text_span(edge["targetLabel"], target_fraction["x"]),
    }


def draw_crop(rows: list[dict]) -> None:
    ensure_highres_sources()
    img = upright_image(76).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    colors = {
        "source": (0, 210, 230, 255),
        "reflected": (190, 0, 255, 230),
        "target": (255, 100, 0, 255),
        "intersection": (40, 220, 90, 150),
    }
    for row in rows:
        for key, label, color_key, width in (
            ("sourceBox", f"{row['sourceId']} source", "source", 4),
            ("reflectedBox", f"{row['sourceId']} reflected", "reflected", 4),
            ("targetBox", f"{row['targetId']} target", "target", 4),
        ):
            box = tuple(int(round(v)) for v in row[key])
            draw.rectangle(box, outline=colors[color_key], width=width)
            draw.text((box[0], max(0, box[1] - 22)), label, fill=colors[color_key])
        inter = tuple(int(round(v)) for v in row["intersection"])
        draw.rectangle(inter, fill=colors["intersection"], outline=(0, 120, 40, 255), width=3)
    combined = Image.alpha_composite(img, overlay).convert("RGB")
    combined.crop((880, 2840, 1780, 3045)).save(OUT_IMG, quality=94)


def main() -> None:
    edges = best_axis_edges()
    rows = [analyze_edge(edge) for edge in edges]
    lines = page76_lines()
    corridor = extract_corridor(lines)
    draw_crop(rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 B5/O5 local self-mirror pair drilldown; no key derivation",
        "axis": AXIS_NAME,
        "crop": str(OUT_IMG),
        "rows": rows,
        "canonicalCorridorLines": corridor,
        "assessment": [
            "The overlap covers roughly the first 89-91% of the phrase width in both directions.",
            "The target overlap is broad, not a narrow word/letter selector.",
            "The pair is best treated as a local semantic/registration anchor linking Volcano Bonds to shitcoiner at heart.",
            "Do not promote B5/O5 overlap to key material unless a new rule tells how to use this pair.",
        ],
        "nextMove": "Treat B5/O5 as an anchor inside the El Salvador corridor, then look for a source rule from p73/p79/p80 or physical registration that chooses an extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Page 76 B5/O5 Pair Drilldown",
        "",
        "Scope: inspect the single page-76 self-mirror pair found by the previous audit. No key candidates are generated.",
        "",
        f"- Axis: `{AXIS_NAME}`",
        f"- Crop: `{OUT_IMG}`",
        "",
        "## Pair Coverage",
        "",
    ]
    for row in rows:
        src_est = row["sourceOriginalTextEstimate"]
        tgt_est = row["targetTextEstimate"]
        md.extend(
            [
                f"### {row['sourceId']} -> {row['targetId']}",
                "",
                f"- Source: `{row['sourceLabel']}`",
                f"- Target: `{row['targetLabel']}`",
                f"- Overlap: source `{row['overlapVsSource']:.3f}`, target `{row['overlapVsTarget']:.3f}`, center distance `{row['centerDistance']:.1f}px`",
                f"- Source original x-span estimate: `{row['sourceOriginalXFractionEstimate']}` -> `{src_est['selectedApprox']}` (omits right approx `{src_est['omittedRightApprox']}`)",
                f"- Target x-span estimate: `{row['targetFraction']['x']}` -> `{tgt_est['selectedApprox']}` (omits right approx `{tgt_est['omittedRightApprox']}`)",
                "",
            ]
        )
    md.extend(
        [
            "## Canonical Page-76 Corridor",
            "",
        ]
    )
    for line in corridor:
        md.append(f"- line `{line['lineIndex']}`: {line['text']}")
    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- This pair does not provide a precise word or letter selector. The horizontal overlap covers nearly the whole phrase on both sides.",
            "- The most defensible reading is semantic/registration: `Volcano Bonds` is being paired with `shitcoiner at heart` inside the El Salvador/IMF corridor.",
            "- Keep this as a low-parameter anchor, but do not derive keys from it directly.",
            "",
            "## Next Best Move",
            "",
            "- Use this pair only if a source/provenance rule from p73/p79/p80 or a physical registration step says how to extract from the page-76 lower corridor.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
