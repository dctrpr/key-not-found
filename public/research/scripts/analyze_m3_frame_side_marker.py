#!/usr/bin/env python3
"""Inspect M3 as the active marker on the reflected p78 frame side.

This is a bounded geometry/readability pass. M3 is the true standalone mark
cut by the reflected p78 frame's right edge. We compare M3's stroke axis with
the frame edges and nearby page-76 rows. No key derivation, hashing, mnemonic,
or address checks are made.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json"
MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/m3_frame_side_marker"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "m3_frame_side_marker.json"
OUT_MD = OUT / "m3_frame_side_marker.md"
OUT_OVERLAY = OUT / "m3_frame_side_marker_overlay.jpg"

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


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def load_m3() -> dict:
    marks = json.loads(MARKS_JSON.read_text())
    return next(mark for mark in marks["analyses"] if mark["index"] == 3)


def load_rows() -> list[dict]:
    marks = json.loads(MARKS_JSON.read_text())
    return marks["rowsUsed"]


def line_y_at_x(point: tuple[float, float], vector: tuple[float, float], x: float) -> float:
    px, py = point
    vx, vy = vector
    if abs(vx) < 1e-9:
        return py
    t = (x - px) / vx
    return py + t * vy


def line_x_at_y(point: tuple[float, float], vector: tuple[float, float], y: float) -> float:
    px, py = point
    vx, vy = vector
    if abs(vy) < 1e-9:
        return px
    t = (y - py) / vy
    return px + t * vx


def line_intersections_with_frame(point: tuple[float, float], vector: tuple[float, float], frame: list[float]) -> dict[str, dict]:
    left, top, right, bottom = frame
    candidates = {}
    for side, x in [("left", left), ("right", right)]:
        y = line_y_at_x(point, vector, x)
        candidates[side] = {"point": [round(x, 2), round(y, 2)], "insideSegment": top <= y <= bottom}
    for side, y in [("top", top), ("bottom", bottom)]:
        x = line_x_at_y(point, vector, y)
        candidates[side] = {"point": [round(x, 2), round(y, 2)], "insideSegment": left <= x <= right}
    return candidates


def distance_to_line(point: tuple[float, float], line_point: tuple[float, float], vector: tuple[float, float]) -> float:
    px, py = point
    ax, ay = line_point
    vx, vy = vector
    # vector is unit-ish, but normalize defensively.
    mag = math.hypot(vx, vy)
    vx, vy = vx / mag, vy / mag
    return abs((px - ax) * vy - (py - ay) * vx)


def projection(point: tuple[float, float], origin: tuple[float, float], vector: tuple[float, float]) -> float:
    px, py = point
    ox, oy = origin
    vx, vy = vector
    mag = math.hypot(vx, vy)
    vx, vy = vx / mag, vy / mag
    return (px - ox) * vx + (py - oy) * vy


def nearest_rows(point: tuple[float, float], rows: list[dict], count: int = 4) -> list[dict]:
    x, y = point
    _ = x
    out = []
    for row in rows:
        out.append({**row, "distancePx": round(abs(row["y"] - y), 2)})
    return sorted(out, key=lambda row: row["distancePx"])[:count]


def row_words(page: dict, rows: list[dict], target_row: dict, y_tol: float = 24.0) -> list[dict]:
    y = target_row["y"]
    words = [w for w in page["words"] if abs(w["center"][1] - y) <= y_tol]
    return sorted(words, key=lambda w: w["center"][0])


def axis_word_hits(page: dict, origin: tuple[float, float], vector: tuple[float, float], max_dist: float = 45.0) -> list[dict]:
    hits = []
    for word in page["words"]:
        cx, cy = word["center"]
        if cy < 2550 or cy > 3025 or cx > origin[0] + 25:
            continue
        dist = distance_to_line((cx, cy), origin, vector)
        proj = projection((cx, cy), origin, vector)
        if proj >= -30 and dist <= max_dist:
            hits.append(
                {
                    "text": word["text"],
                    "token": word.get("token", ""),
                    "box": word["box"],
                    "center": word["center"],
                    "distancePx": round(dist, 2),
                    "projection": round(proj, 2),
                }
            )
    hits.sort(key=lambda hit: hit["projection"])
    return hits


def sequence_text(words: list[dict]) -> str:
    return clean(" ".join(w["text"] for w in words))


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits = {}
    for name, value in streams.items():
        found = [
            term
            for term in INSTRUCTION_TERMS
            if re.search(rf"\b{re.escape(term)}\b", value.lower())
        ]
        if found:
            hits[name] = found
    return hits


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(frame: list[float], m3: dict, axis_line: dict, axis_hits: list[dict]) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [1080, 2500, 2544, 3040]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    def tr_point(pt: list[float] | tuple[float, float]) -> tuple[float, float]:
        return (pt[0] - crop_box[0], pt[1] - crop_box[1])

    def tr_box(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    draw.rectangle(tr_box(frame), outline=(255, 0, 0), width=4)
    draw.rectangle(tr_box(m3["box"]), outline=(200, 0, 200), width=4)
    draw_label(draw, (int(m3["box"][0] - crop_box[0]), int(m3["box"][1] - crop_box[1] - 28)), "M3", (200, 0, 200))

    left_pt = axis_line["frameIntersections"]["left"]["point"]
    right_pt = axis_line["frameIntersections"]["right"]["point"]
    draw.line([tr_point(left_pt), tr_point(right_pt)], fill=(0, 180, 0), width=5)
    draw_label(draw, (int(right_pt[0] - crop_box[0] - 10), int(right_pt[1] - crop_box[1] - 34)), "axis enters frame", (0, 130, 0))
    draw_label(draw, (int(left_pt[0] - crop_box[0] + 6), int(left_pt[1] - crop_box[1] + 6)), "axis exits near trust row", (0, 130, 0))

    for hit in axis_hits[:12]:
        draw.rectangle(tr_box(hit["box"]), outline=(0, 120, 255), width=2)

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    edge = json.loads(EDGE_JSON.read_text())
    frame = edge["reflectedP78BoxOnP76"]
    m3 = load_m3()
    page = load_page76()
    rows = load_rows()

    center = tuple(m3["center"])
    vector = tuple(m3["axis"]["vector"])
    mag = math.hypot(vector[0], vector[1])
    unit = (vector[0] / mag, vector[1] / mag)

    intersections = line_intersections_with_frame(center, unit, frame)
    right_entry = tuple(intersections["right"]["point"])
    left_exit = tuple(intersections["left"]["point"])
    axis_hits = axis_word_hits(page, right_entry, unit)

    inside_rows = m3["rowHits"]["insideRows"]
    right_entry_rows = nearest_rows(right_entry, rows)
    left_exit_rows = nearest_rows(left_exit, rows)

    row_streams = {}
    for row in inside_rows:
        words = row_words(page, rows, row)
        row_streams[f"row{row['visualRow']}LeftToRight"] = sequence_text(words)
        row_streams[f"row{row['visualRow']}RightToLeft"] = sequence_text(list(reversed(words)))

    axis_order_text = sequence_text(axis_hits)
    axis_reverse_text = sequence_text(list(reversed(axis_hits)))
    tight_axis_hits = [hit for hit in axis_hits if hit["distancePx"] <= 20]
    tight_axis_text = sequence_text(tight_axis_hits)
    streams = {
        "axisOrderFromFrameRight": axis_order_text,
        "axisOrderReverse": axis_reverse_text,
        "tightAxisOrderFromFrameRight": tight_axis_text,
        **row_streams,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "M3 axis as p78 frame-side marker; no key derivation",
        "reflectedP78Frame": frame,
        "m3": {
            "box": m3["box"],
            "center": m3["center"],
            "axisAngleDeg": m3["axis"]["angleDeg"],
            "axisVector": [round(unit[0], 6), round(unit[1], 6)],
        },
        "axisLine": {
            "frameIntersections": intersections,
            "rightEntryNearestRows": right_entry_rows,
            "leftExitNearestRows": left_exit_rows,
        },
        "m3InsideRows": inside_rows,
        "axisWordHits": axis_hits,
        "tightAxisWordHits": tight_axis_hits,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "M3's main axis crosses the reflected p78 frame from the right edge to the left edge; it is a frame-side marker, not just a loose nearby mark.",
            "The right-edge entry is closest to the row `bunch to his Wall Street crony pals, but so far he`, while the left-edge exit is within a few pixels of the bottom of the `trust that guy` row.",
            "Axis-word reading recovers local corridor prose around `guy that trust ... because Maybe`; reversing it only reconstructs the visible `Maybe because ... trust that guy` neighborhood.",
            "No read/take/fold/mirror/word/letter/key instruction appears in the M3 row or axis streams.",
            "M3 therefore confirms the p78 frame orientation toward the distrust/heart corridor, but does not solve the extraction-unit problem.",
        ],
        "nextMove": "Compare M3 with M4 as a paired lower-right mark system; if they behave as paired brackets, test whether their axes bracket a row/phrase. Otherwise keep them as orientation evidence only.",
    }

    build_overlay(frame, m3, result["axisLine"], axis_hits)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# M3 Frame-Side Marker",
        "",
        "Scope: inspect M3 as the active mark cut by the reflected p78 frame right edge. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- M3 box: `{m3['box']}`",
        f"- M3 axis angle: `{m3['axis']['angleDeg']}°`",
        f"- Reflected p78 frame: `{frame}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Frame Crossings",
        "",
        "| frame side | crossing point | inside side segment | nearest row |",
        "|---|---:|---|---|",
    ]
    for side in ["right", "left", "top", "bottom"]:
        row = result["axisLine"]["frameIntersections"][side]
        nearest = nearest_rows(tuple(row["point"]), rows, 1)[0]
        lines.append(
            f"| `{side}` | `{row['point']}` | `{row['insideSegment']}` | row `{nearest['visualRow']}`: {nearest['canonicalText']} (`{nearest['distancePx']}px`) |"
        )

    lines.extend(["", "## Axis Word Read", ""])
    lines.append(f"- From frame-right along M3 axis: `{axis_order_text}`")
    lines.append(f"- Reverse: `{axis_reverse_text}`")
    lines.append(f"- Tight hits only (<=20px): `{tight_axis_text}`")
    lines.append(f"- Instruction-term hits: `{result['instructionTermHits']}`")

    lines.extend(["", "## M3 Inside Rows", ""])
    for row in inside_rows:
        lines.append(f"- row `{row['visualRow']}`: {row['canonicalText']}")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("instruction hits:", result["instructionTermHits"])


if __name__ == "__main__":
    main()
