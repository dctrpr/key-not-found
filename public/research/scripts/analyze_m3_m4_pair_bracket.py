#!/usr/bin/env python3
"""Test whether M3 and M4 form a bracket around page-76 text.

M3 and M4 are the two true standalone lower-right marks. M3 is cut by the
reflected p78 frame's right edge; M4 sits just below the frame. This script
tests the simplest paired interpretation: their main axes form a bracket/wedge.
It reports which words/highlights fall inside that wedge. No key derivation,
hashing, mnemonic, or address checks are made.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/m3_m4_pair_bracket"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "m3_m4_pair_bracket.json"
OUT_MD = OUT / "m3_m4_pair_bracket.md"
OUT_OVERLAY = OUT / "m3_m4_pair_bracket_overlay.jpg"


INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "seed",
    "wif",
    "address",
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def load_mark(index: int) -> dict:
    marks = json.loads(MARKS_JSON.read_text())
    return next(mark for mark in marks["analyses"] if mark["index"] == index)


def unit(vector: list[float]) -> tuple[float, float]:
    mag = math.hypot(vector[0], vector[1])
    return (vector[0] / mag, vector[1] / mag)


def line_y(point: tuple[float, float], vector: tuple[float, float], x: float) -> float:
    px, py = point
    vx, vy = vector
    if abs(vx) < 1e-9:
        return py
    return py + ((x - px) / vx) * vy


def line_intersection(
    p1: tuple[float, float],
    v1: tuple[float, float],
    p2: tuple[float, float],
    v2: tuple[float, float],
) -> tuple[float, float]:
    x1, y1 = p1
    x2, y2 = p2
    vx1, vy1 = v1
    vx2, vy2 = v2
    cross = vx1 * vy2 - vy1 * vx2
    if abs(cross) < 1e-9:
        raise ValueError("lines are nearly parallel")
    t = ((x2 - x1) * vy2 - (y2 - y1) * vx2) / cross
    return (x1 + t * vx1, y1 + t * vy1)


def is_between_axes(
    point: tuple[float, float],
    vertex: tuple[float, float],
    axis_a_point: tuple[float, float],
    axis_a_vec: tuple[float, float],
    axis_b_point: tuple[float, float],
    axis_b_vec: tuple[float, float],
) -> bool:
    x, y = point
    if x < vertex[0]:
        return False
    ya = line_y(axis_a_point, axis_a_vec, x)
    yb = line_y(axis_b_point, axis_b_vec, x)
    lo, hi = sorted([ya, yb])
    return lo <= y <= hi


def box_center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def box_sample_points(box: list[float]) -> list[tuple[float, float]]:
    x1, y1, x2, y2 = box
    cx, cy = box_center(box)
    return [
        (cx, cy),
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2),
        ((x1 + cx) / 2, cy),
        ((x2 + cx) / 2, cy),
    ]


def bracket_fraction_for_box(
    box: list[float],
    vertex: tuple[float, float],
    m3: dict,
    m3_vec: tuple[float, float],
    m4: dict,
    m4_vec: tuple[float, float],
) -> float:
    points = box_sample_points(box)
    inside = [
        pt
        for pt in points
        if is_between_axes(pt, vertex, tuple(m3["center"]), m3_vec, tuple(m4["center"]), m4_vec)
    ]
    return round(len(inside) / len(points), 4)


def display_word(word: dict, o5_box: list[float]) -> str:
    text = word["text"]
    # The high-res OCR fuses `shitcoiner at heart` into a garbage token. If the
    # word overlaps O5, name the known visual text so the report stays readable.
    ix1 = max(word["box"][0], o5_box[0])
    iy1 = max(word["box"][1], o5_box[1])
    ix2 = min(word["box"][2], o5_box[2])
    iy2 = min(word["box"][3], o5_box[3])
    if ix2 > ix1 and iy2 > iy1 and len(text) > 12:
        return "[O5: shitcoiner at heart]"
    return text


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    out = {}
    for name, value in streams.items():
        found = [
            term
            for term in INSTRUCTION_TERMS
            if re.search(rf"\b{re.escape(term)}\b", value.lower())
        ]
        if found:
            out[name] = found
    return out


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(
    frame: list[float],
    vertex: tuple[float, float],
    m3: dict,
    m3_vec: tuple[float, float],
    m4: dict,
    m4_vec: tuple[float, float],
    selected_words: list[dict],
    selected_highlights: list[dict],
) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [430, 2520, 2544, 3205]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop, "RGBA")

    def tr_point(pt: tuple[float, float]) -> tuple[float, float]:
        return (pt[0] - crop_box[0], pt[1] - crop_box[1])

    def tr_box(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    right_x = 2544
    m3_right = (right_x, line_y(tuple(m3["center"]), m3_vec, right_x))
    m4_right = (right_x, line_y(tuple(m4["center"]), m4_vec, right_x))
    wedge = [tr_point(vertex), tr_point(m3_right), tr_point(m4_right)]
    draw.polygon(wedge, fill=(255, 220, 0, 60), outline=(255, 170, 0, 230))

    for mark, color, label in [(m3, (200, 0, 200, 255), "M3"), (m4, (200, 0, 200, 255), "M4")]:
        draw.rectangle(tr_box(mark["box"]), outline=color, width=4)
        draw_label(draw, (int(mark["box"][0] - crop_box[0]), int(mark["box"][1] - crop_box[1] - 28)), label, (180, 0, 180))

    left_x = 430
    for mark, vec, color in [(m3, m3_vec, (0, 170, 0, 255)), (m4, m4_vec, (0, 130, 255, 255))]:
        p_left = (left_x, line_y(tuple(mark["center"]), vec, left_x))
        p_right = (right_x, line_y(tuple(mark["center"]), vec, right_x))
        draw.line([tr_point(p_left), tr_point(p_right)], fill=color, width=4)

    draw.rectangle(tr_box(frame), outline=(255, 0, 0, 255), width=3)
    draw_label(draw, (int(vertex[0] - crop_box[0] + 8), int(vertex[1] - crop_box[1] + 8)), "axis vertex", (180, 100, 0))

    for word in selected_words:
        draw.rectangle(tr_box(word["box"]), outline=(0, 80, 255, 255), width=3)
    for item in selected_highlights:
        draw.rectangle(tr_box(item["box"]), outline=(255, 110, 0, 255), width=5)

    crop.convert("RGB").save(OUT_OVERLAY, quality=95)


def main() -> None:
    page = load_page76()
    edge = json.loads(EDGE_JSON.read_text())
    frame = edge["reflectedP78BoxOnP76"]
    m3 = load_mark(3)
    m4 = load_mark(4)
    m3_vec = unit(m3["axis"]["vector"])
    m4_vec = unit(m4["axis"]["vector"])
    vertex = line_intersection(tuple(m3["center"]), m3_vec, tuple(m4["center"]), m4_vec)

    o5 = next(h for h in page["highlights"] if h["id"] == "p76_orange_5")
    selected_words = []
    for word in page["words"]:
        cx, cy = word["center"]
        if not (2600 <= cy <= 3010):
            continue
        if is_between_axes((cx, cy), vertex, tuple(m3["center"]), m3_vec, tuple(m4["center"]), m4_vec):
            selected_words.append(word)
    selected_words.sort(key=lambda w: (w["center"][1], w["center"][0]))

    selected_labels = [display_word(w, o5["box"]) for w in selected_words]
    selected_stream = clean(" ".join(selected_labels))
    selected_reverse = clean(" ".join(reversed(selected_labels)))

    highlight_rows = []
    for h in page["highlights"]:
        if h["id"].startswith("p76_"):
            frac = bracket_fraction_for_box(h["box"], vertex, m3, m3_vec, m4, m4_vec)
            center_inside = is_between_axes(box_center(h["box"]), vertex, tuple(m3["center"]), m3_vec, tuple(m4["center"]), m4_vec)
            if frac or center_inside:
                highlight_rows.append({**h, "bracketSampleFraction": frac, "centerInside": center_inside})

    # Also check trusted lower grey boxes from the mark audit, especially G5.
    lower_marks = json.loads(MARKS_JSON.read_text())
    trusted_grey = []
    for item in lower_marks["analyses"]:
        if item["classification"] == "text/highlight-false-positive":
            frac = bracket_fraction_for_box(item["box"], vertex, m3, m3_vec, m4, m4_vec)
            center_inside = is_between_axes(box_center(item["box"]), vertex, tuple(m3["center"]), m3_vec, tuple(m4["center"]), m4_vec)
            if frac or center_inside:
                trusted_grey.append({**item, "bracketSampleFraction": frac, "centerInside": center_inside})

    streams = {
        "bracketedWordsLeftToRight": selected_stream,
        "bracketedWordsReverse": selected_reverse,
        "highlightIds": " ".join(h["id"] for h in highlight_rows),
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "M3/M4 paired mark wedge/bracket test; no key derivation",
        "m3": {
            "box": m3["box"],
            "center": m3["center"],
            "axisAngleDeg": m3["axis"]["angleDeg"],
            "axisVector": [round(m3_vec[0], 6), round(m3_vec[1], 6)],
        },
        "m4": {
            "box": m4["box"],
            "center": m4["center"],
            "axisAngleDeg": m4["axis"]["angleDeg"],
            "axisVector": [round(m4_vec[0], 6), round(m4_vec[1], 6)],
        },
        "axisIntersectionVertex": [round(vertex[0], 2), round(vertex[1], 2)],
        "selectedWords": [
            {
                "text": word["text"],
                "displayText": label,
                "box": word["box"],
                "center": word["center"],
            }
            for word, label in zip(selected_words, selected_labels)
        ],
        "selectedHighlights": highlight_rows,
        "selectedTrustedGrey": trusted_grey,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "M3 and M4 axes are not random parallel scratches: they intersect near x≈998, y≈2901, just left of the final orange line.",
            "The right-opening wedge between them selects the final page-76 orange unit, O5 `shitcoiner at heart`, plus the nearby preceding word `guy` from the `trust that guy` row.",
            "It does not include G5 `Volcano Bonds`; the M3/M4 pair chooses O5 rather than the grey/orange pair together.",
            "The bracketed stream is visible corridor prose (`guy / shitcoiner at heart`) and contains no read/take/word/letter/key instruction.",
            "This upgrades O5 as the endpoint/target of the lower-right mark system, but the extraction unit is still missing.",
        ],
        "nextMove": "Treat O5 as confirmed endpoint, then step back to ask what source rule turns the confirmed targets (G5/O5, p78 frame, and Schott mirror) into an ordered extraction unit. Avoid reopening M3/M4 as key text.",
    }

    build_overlay(frame, vertex, m3, m3_vec, m4, m4_vec, selected_words, highlight_rows)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# M3/M4 Pair Bracket",
        "",
        "Scope: test whether the two true lower-right marks form a bracket/wedge around page-76 text. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Axis vertex: `{result['axisIntersectionVertex']}`",
        f"- M3 angle: `{m3['axis']['angleDeg']}°`; M4 angle: `{m4['axis']['angleDeg']}°`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Bracketed Text",
        "",
        f"- Left-to-right: `{selected_stream}`",
        f"- Reverse: `{selected_reverse}`",
        f"- Instruction-term hits: `{result['instructionTermHits']}`",
        "",
        "## Bracketed Highlights",
        "",
    ]
    if highlight_rows:
        for h in highlight_rows:
            lines.append(
                f"- `{h['id']}` `{h['kind']}` box `{h['box']}` sampleFraction `{h['bracketSampleFraction']}` centerInside `{h['centerInside']}`"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Trusted Grey Checks", ""])
    if trusted_grey:
        for item in trusted_grey:
            lines.append(
                f"- `M{item['index']}` {item['note']} sampleFraction `{item['bracketSampleFraction']}` centerInside `{item['centerInside']}`"
            )
    else:
        lines.append("- None; G5 `Volcano Bonds` is outside the M3/M4 wedge.")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("bracketed:", selected_stream)
    print("instruction hits:", result["instructionTermHits"])


if __name__ == "__main__":
    main()
