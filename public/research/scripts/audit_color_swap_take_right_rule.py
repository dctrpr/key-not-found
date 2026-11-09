#!/usr/bin/env python3
"""Test the literal "take/right" reading from the p79 color-swap filter.

The color-swap pass isolated p79 and surfaced only printed instruction-looking
terms from "That's right, Bitcoin will take". This script tests the bounded,
literal follow-up: take right-side / right-edge words from the selected page-76
contacts. It does not derive keys.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
COLOR_SWAP_JSON = ROOT / "analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
OUT = ROOT / "analysis_outputs/source_audit/color_swap_take_right_rule"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "color_swap_take_right_rule.json"
OUT_MD = OUT / "color_swap_take_right_rule.md"
OUT_IMG = OUT / "color_swap_take_right_rule_overlay.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "fold",
    "mirror",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "key",
    "private",
    "reverse",
    "order",
    "index",
    "next",
    "down",
]


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def instruction_hits(text: str) -> list[str]:
    words = set(norm(text).split())
    return [term for term in INSTRUCTION_TERMS if term in words]


def box_area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def overlaps_word(word: dict[str, Any], box: list[float], min_frac: float = 0.12) -> bool:
    inter = intersection([float(v) for v in word["box"]], box)
    if not inter:
        cx, cy = word["center"]
        return box[0] <= cx <= box[2] and box[1] <= cy <= box[3]
    return box_area(inter) / max(1.0, box_area([float(v) for v in word["box"]])) >= min_frac


def text_join(words: list[dict[str, Any]]) -> str:
    return " ".join(w["text"] for w in words)


def load_page76_words() -> list[dict[str, Any]]:
    data = json.loads(MAP_JSON.read_text(encoding="utf-8"))
    page = next(p for p in data["pages"] if p["page"] == 76)
    words = [w for w in page["words"] if w["text"].strip()]
    # Remove marginal labels unless they are explicitly selected by a box.
    return sorted(words, key=lambda w: (w["center"][1], w["center"][0]))


def group_rows(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for word in words:
        cx, cy = word["center"]
        if cy < 250 or cy > 3120:
            continue
        best = None
        best_dist = 10**9
        for row in rows:
            dist = abs(row["y"] - cy)
            if dist < best_dist:
                best = row
                best_dist = dist
        if best is None or best_dist > 34:
            rows.append({"y": cy, "words": [word]})
        else:
            best["words"].append(word)
            best["y"] = sum(w["center"][1] for w in best["words"]) / len(best["words"])
    for row in rows:
        row["words"].sort(key=lambda w: w["center"][0])
    rows.sort(key=lambda row: row["y"])
    return rows


def nearest_row(rows: list[dict[str, Any]], y: float) -> dict[str, Any] | None:
    if not rows:
        return None
    return min(rows, key=lambda row: abs(row["y"] - y))


def right_side_units(edge: dict[str, Any], words: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    target = [float(v) for v in edge["targetBox"]]
    inter = [float(v) for v in edge["intersection"]]
    reflected = [float(v) for v in edge["reflectedBox"]]
    y_mid = (inter[1] + inter[3]) / 2
    row = nearest_row(rows, y_mid)
    row_words = row["words"] if row else []

    target_words = [w for w in words if overlaps_word(w, target, 0.10)]
    intersection_words = [w for w in words if overlaps_word(w, inter, 0.10)]
    reflected_words = [w for w in words if overlaps_word(w, reflected, 0.10)]

    target_mid_x = (target[0] + target[2]) / 2
    target_right_half = [w for w in target_words if w["center"][0] >= target_mid_x]
    intersection_right = [w for w in row_words if w["center"][0] > inter[2] and w["center"][0] <= inter[2] + 420]
    reflected_right = [w for w in row_words if w["center"][0] > reflected[2] and w["center"][0] <= reflected[2] + 420]
    reflected_left = [w for w in row_words if reflected[0] - 420 <= w["center"][0] < reflected[0]]

    right_edge_word = []
    if target_words:
        right_edge_word = [max(target_words, key=lambda w: w["center"][0])]
    first_word_right_of_target = [w for w in row_words if w["center"][0] > target[2]][:1]

    return {
        "sourcePage": edge["sourcePage"],
        "transition": f"{edge['sourceKind']}->{edge['targetKind']}",
        "sourceLabel": edge["sourceLabel"],
        "targetId": edge["targetId"],
        "targetLabel": edge["targetLabel"],
        "rowY": round(float(row["y"]), 3) if row else None,
        "rowText": text_join(row_words),
        "intersectionWords": text_join(intersection_words),
        "targetWords": text_join(target_words),
        "targetRightHalf": text_join(target_right_half),
        "rightEdgeWord": text_join(right_edge_word),
        "firstWordRightOfTarget": text_join(first_word_right_of_target),
        "rightOfIntersection": text_join(intersection_right),
        "rightOfReflectedBox": text_join(reflected_right),
        "leftOfReflectedBox": text_join(reflected_left),
    }


def font(size: int = 24) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_overlay(edges: list[dict[str, Any]], records: list[dict[str, Any]]) -> None:
    img = upright_image(76).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    title_font = font(38)
    small = font(22)
    for edge, rec in zip(edges, records):
        tbox = [int(round(v)) for v in edge["targetBox"]]
        ibox = [int(round(v)) for v in edge["intersection"]]
        rbox = [int(round(v)) for v in edge["reflectedBox"]]
        color = (165, 0, 255, 210)
        target_color = (255, 95, 0, 255) if edge["targetKind"] == "orange" else (0, 190, 230, 255)
        draw.rectangle(tbox, outline=target_color, width=6)
        draw.rectangle(rbox, outline=color, width=4)
        draw.rectangle(ibox, outline=(40, 255, 70, 255), width=5)
        label = f"{edge['targetId']} right: {rec['rightEdgeWord'] or rec['targetRightHalf'] or '-'}"
        draw.text((tbox[0], max(0, tbox[1] - 26)), label, fill=target_color, font=small)
    draw.rectangle([0, 0, img.width, 90], fill=(255, 255, 255, 235))
    draw.text((28, 26), "Literal take-right audit on p79 color-swap contacts", fill=(20, 20, 20, 255), font=title_font)
    Image.alpha_composite(img, overlay).convert("RGB").save(OUT_IMG, quality=94)


def main() -> None:
    color_swap = json.loads(COLOR_SWAP_JSON.read_text(encoding="utf-8"))
    edges = [edge for edge in color_swap["selectedEdges"] if edge["sourcePage"] == 79]
    edges.sort(key=lambda edge: (edge["targetKind"], int(edge["targetIndex"]), -edge["score"]))

    words = load_page76_words()
    rows = group_rows(words)
    records = [right_side_units(edge, words, rows) for edge in edges]

    streams = {
        "intersectionWords": " | ".join(r["intersectionWords"] for r in records if r["intersectionWords"]),
        "targetRightHalf": " | ".join(r["targetRightHalf"] for r in records if r["targetRightHalf"]),
        "rightEdgeWords": " ".join(r["rightEdgeWord"] for r in records if r["rightEdgeWord"]),
        "firstWordsRightOfTarget": " ".join(r["firstWordRightOfTarget"] for r in records if r["firstWordRightOfTarget"]),
        "rightOfIntersections": " | ".join(r["rightOfIntersection"] for r in records if r["rightOfIntersection"]),
        "rightOfReflectedBoxes": " | ".join(r["rightOfReflectedBox"] for r in records if r["rightOfReflectedBox"]),
        "leftOfReflectedBoxes": " | ".join(r["leftOfReflectedBox"] for r in records if r["leftOfReflectedBox"]),
    }
    hits = {name: instruction_hits(value) for name, value in streams.items()}
    draw_overlay(edges, records)

    decision = (
        "Literal take-right operations on the p79 color-swap contacts produce ordinary upper-page-76 prose and short "
        "fragments such as `to`, `Bitcoin`, `money`, and `nonsense`. The streams do not contain a procedural read/take/"
        "word/letter/key instruction, so `take/right` remains printed phrase content rather than a usable rule."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Literal take-right/right-edge audit for p79 bidirectional color-swap contacts; no key derivation.",
        "input": str(COLOR_SWAP_JSON),
        "records": records,
        "streams": streams,
        "instructionHits": hits,
        "overlay": str(OUT_IMG),
        "decision": decision,
        "nextMove": "Do not keep drilling the upper p79 color-swap cluster locally. Return to lower-corridor source/physical registration or wait for a source clue that names color-swap/right-side extraction.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Color-Swap Take-Right Rule Audit",
        "",
        "Scope: test the only procedural-looking words from the p79 color-swap source phrase, `right` and `take`, as literal right-side/edge extraction on page 76. No key derivation, hashing, seed checking, WIF checking, address checking, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_IMG}`",
        f"- Selected p79 color-swap contacts: `{len(records)}`",
        "",
        "## Records",
        "",
        "| target | source phrase | target words | intersection | right edge | right of intersection |",
        "|---|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| `{rec['targetId']}` | `{rec['sourceLabel']}` | `{rec['targetWords']}` | "
            f"`{rec['intersectionWords']}` | `{rec['rightEdgeWord']}` | `{rec['rightOfIntersection']}` |"
        )
    lines.extend(["", "## Streams", ""])
    for name, value in streams.items():
        if not value:
            continue
        extra = f" | instruction hits: `{hits[name]}`" if hits[name] else ""
        lines.append(f"- `{name}`: `{value}`{extra}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {decision}",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
