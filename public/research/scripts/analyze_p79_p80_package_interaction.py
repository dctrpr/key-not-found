#!/usr/bin/env python3
"""Drill into the p79/p80 package-label spread interaction.

The spread reconciliation pass found exactly two meaningful p79/p80 raw hflip
hits: page 80 medicine/package labels land on the page 79 sentence
"Everyone will live their own experience in the rabbit hole.". This pass asks
whether those hits select useful sub-spans or only reinforce the OVERDOSE
medicine theme.

No key candidates are generated.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from analyze_front_back_leaf_box_registration import (
    center,
    hflip_box,
    intersection,
    orange_items,
)
from highres_reflection_extract import ensure_highres_sources, upright_image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/p79_p80_package_interaction"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p79_p80_package_interaction.json"
OUT_MD = OUT / "p79_p80_package_interaction.md"
OUT_IMG = OUT / "p79_p80_package_interaction_sheet.jpg"


def frac_span(inner: tuple[float, float, float, float], outer: tuple[float, float, float, float]) -> dict:
    ix1, iy1, ix2, iy2 = inner
    ox1, oy1, ox2, oy2 = outer
    ow = ox2 - ox1
    oh = oy2 - oy1
    return {
        "x": [round((ix1 - ox1) / ow, 4), round((ix2 - ox1) / ow, 4)] if ow else [None, None],
        "y": [round((iy1 - oy1) / oh, 4), round((iy2 - oy1) / oh, 4)] if oh else [None, None],
    }


def mirror_source_x_fraction(reflected_fraction: list[float]) -> list[float]:
    left, right = reflected_fraction
    return [round(1 - right, 4), round(1 - left, 4)]


def approx_text_span(text: str, x_fraction: list[float]) -> dict:
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


def approx_multiline_y(label: str, y_fraction: list[float]) -> dict:
    lines = [part.strip() for part in label.split("/") if part.strip()]
    if not lines:
        return {"lines": [], "lineRangeEstimate": [0, 0], "selectedLinesApprox": []}
    n = len(lines)
    start = max(0, min(n, math.floor(y_fraction[0] * n)))
    end = max(start + 1, min(n, math.ceil(y_fraction[1] * n)))
    return {
        "lines": lines,
        "lineRangeEstimate": [start, end],
        "selectedLinesApprox": lines[start:end],
    }


def item_by_index(items: list[dict], index: int) -> dict:
    for item in items:
        if item["index"] == index:
            return item
    raise RuntimeError(f"missing orange item index {index}")


def analyze_source_to_target(source: dict, target: dict, source_width: int) -> dict | None:
    flipped = hflip_box(source["box"], source_width)
    inter = intersection(flipped, target["box"])
    if not inter:
        return None
    reflected_fraction = frac_span(inter, flipped)
    source_original_x = mirror_source_x_fraction(reflected_fraction["x"])
    target_fraction = frac_span(inter, target["box"])
    sx, sy = center(flipped)
    tx, ty = center(target["box"])
    return {
        "sourceId": source["id"],
        "sourcePage": source["page"],
        "sourceIndex": source["index"],
        "sourceLabel": source["label"],
        "sourceBox": source["box"],
        "hflipBox": flipped,
        "targetId": target["id"],
        "targetPage": target["page"],
        "targetIndex": target["index"],
        "targetLabel": target["label"],
        "targetBox": target["box"],
        "intersection": inter,
        "centerDistance": round(((sx - tx) ** 2 + (sy - ty) ** 2) ** 0.5, 2),
        "sourceReflectedFraction": reflected_fraction,
        "sourceOriginalXFractionEstimate": source_original_x,
        "sourceTextEstimate": approx_text_span(source["label"], source_original_x),
        "sourceLineEstimateFromY": approx_multiline_y(source["label"], reflected_fraction["y"]),
        "targetFraction": target_fraction,
        "targetTextEstimate": approx_text_span(target["label"], target_fraction["x"]),
        "targetLineEstimateFromY": approx_multiline_y(target["label"], target_fraction["y"]),
    }


def draw_sheet(rows_80_to_79: list[dict], rows_79_to_80: list[dict]) -> None:
    ensure_highres_sources()
    p79 = upright_image(79).convert("RGBA")
    p80 = upright_image(80).convert("RGBA")
    panels = []
    for title, img, rows, is_target_p79 in (
        ("p80 labels reflected onto p79", p79, rows_80_to_79, True),
        ("p79 sentence reflected onto p80", p80, rows_79_to_80, False),
    ):
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for row in rows:
            mapped = tuple(int(round(v)) for v in row["hflipBox"])
            target = tuple(int(round(v)) for v in row["targetBox"])
            inter = tuple(int(round(v)) for v in row["intersection"])
            draw.rectangle(mapped, outline=(190, 0, 255, 230), width=5)
            draw.rectangle(target, outline=(255, 100, 0, 255), width=5)
            draw.rectangle(inter, fill=(40, 220, 90, 150), outline=(0, 120, 40, 255), width=4)
            draw.text((target[0], max(0, target[1] - 28)), f"target O{row['targetIndex']}", fill=(255, 100, 0, 255))
            draw.text((mapped[0], max(0, mapped[1] - 28)), f"reflected O{row['sourceIndex']}", fill=(190, 0, 255, 255))
        combined = Image.alpha_composite(img, overlay).convert("RGB")
        crop = combined.crop((430, 1600, 2140, 2220)) if is_target_p79 else combined.crop((760, 1600, 1800, 2220))
        header = Image.new("RGB", (crop.width, 54), (248, 248, 248))
        hdraw = ImageDraw.Draw(header)
        hdraw.text((16, 18), title, fill=(20, 20, 20))
        panel = Image.new("RGB", (crop.width, crop.height + header.height), (255, 255, 255))
        panel.paste(header, (0, 0))
        panel.paste(crop, (0, header.height))
        panels.append(panel)
    width = max(panel.width for panel in panels)
    height = sum(panel.height for panel in panels) + 24
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for panel in panels:
        sheet.paste(panel, (0, y))
        y += panel.height + 24
    sheet.save(OUT_IMG, quality=94)


def main() -> None:
    ensure_highres_sources()
    p79_orange = orange_items(79)
    p80_orange = orange_items(80)
    p79_o4 = item_by_index(p79_orange, 4)
    p80_o1 = item_by_index(p80_orange, 1)
    p80_o2 = item_by_index(p80_orange, 2)

    width_80 = upright_image(80).width
    width_79 = upright_image(79).width
    rows_80_to_79 = [
        analyze_source_to_target(p80_o1, p79_o4, width_80),
        analyze_source_to_target(p80_o2, p79_o4, width_80),
    ]
    rows_79_to_80 = [
        analyze_source_to_target(p79_o4, p80_o1, width_79),
        analyze_source_to_target(p79_o4, p80_o2, width_79),
    ]
    rows_80_to_79 = [row for row in rows_80_to_79 if row]
    rows_79_to_80 = [row for row in rows_79_to_80 if row]
    draw_sheet(rows_80_to_79, rows_79_to_80)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p79/p80 package-label interaction drilldown; raw hflip only; no key derivation",
        "sheet": str(OUT_IMG),
        "p80ToP79": rows_80_to_79,
        "p79ToP80": rows_79_to_80,
        "assessment": [
            "Both page-80 package labels hit only one page-79 target: the sentence Everyone will live their own experience in the rabbit hole.",
            "The target spans are broad sentence fragments, not narrow word/letter selections.",
            "The vertical p80 package hits are bottom strips of the package boxes, plausibly the lower label lines, so they reinforce the medicine/SHITCOINS theme rather than defining an extraction unit.",
            "Do not use p80 package labels as direct key text or numeric index streams without a new rule.",
        ],
        "nextMove": "Keep p79/p80 as OVERDOSE provenance/theme evidence. Next useful move is to search for an explicit source rule that maps the p73 five-capsule order or p80 dosage labels onto page 76.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# P79/P80 Package Interaction Drilldown",
        "",
        "Scope: inspect the two raw hflip interactions between page 80 medicine/package labels and page 79 end text. No key candidates are generated.",
        "",
        f"- Sheet: `{OUT_IMG}`",
        "",
        "## P80 Labels Reflected Onto P79",
        "",
    ]
    for row in rows_80_to_79:
        tgt = row["targetTextEstimate"]
        src_line = row["sourceLineEstimateFromY"]
        md.extend(
            [
                f"### p80 O{row['sourceIndex']} -> p79 O{row['targetIndex']}",
                "",
                f"- Source label: `{row['sourceLabel']}`",
                f"- Source y-span estimate: `{row['sourceReflectedFraction']['y']}` -> `{src_line['selectedLinesApprox']}`",
                f"- Target sentence span estimate: `{row['targetFraction']['x']}` -> `{tgt['selectedApprox']}`",
                f"- Center distance: `{row['centerDistance']}` px",
                "",
            ]
        )
    md.extend(["## P79 Sentence Reflected Onto P80", ""])
    for row in rows_79_to_80:
        src = row["sourceTextEstimate"]
        tgt_line = row["targetLineEstimateFromY"]
        md.extend(
            [
                f"### p79 O{row['sourceIndex']} -> p80 O{row['targetIndex']}",
                "",
                f"- Source sentence span estimate: `{row['sourceOriginalXFractionEstimate']}` -> `{src['selectedApprox']}`",
                f"- Target label: `{row['targetLabel']}`",
                f"- Target y-span estimate: `{row['targetFraction']['y']}` -> `{tgt_line['selectedLinesApprox']}`",
                f"- Center distance: `{row['centerDistance']}` px",
                "",
            ]
        )
    md.extend(
        [
            "## Assessment",
            "",
            "- The package layer is real enough to preserve as theme/provenance: both p80 labels hit the same p79 orange sentence under raw hflip.",
            "- It does not give a clean extraction unit. The p79 spans are broad fragments from the middle of one sentence, and the p80 hits are lower strips of multi-line package labels.",
            "- Treat `5 SYMPTOM RELIEF` / `6 FL OZ` as OVERDOSE/dosage evidence, not as direct page-76 key material.",
            "",
            "## Next Best Move",
            "",
            "- Look for an explicit rule that tells how the p73 five-capsule order or p80 dosage/package labels should be applied to page 76. Do not promote the p79/p80 overlap by itself.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
