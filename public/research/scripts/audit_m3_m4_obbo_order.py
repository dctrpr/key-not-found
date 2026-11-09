#!/usr/bin/env python3
"""Test whether M3/M4 standalone marks choose an order among OBBO anchors.

This is a bounded page-76 geometry audit. It ranks the four active anchors by
distance/projection relative to the M3/M4 mark centers and axes, and checks the
M3/M4 wedge membership. It does not generate keys, hashes, seed phrases, WIFs,
or addresses.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MARKS = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
ANCHORS = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT_DIR = ROOT / "analysis_outputs/source_audit/m3_m4_obbo_order"
OUT_JSON = OUT_DIR / "m3_m4_obbo_order.json"
OUT_MD = OUT_DIR / "m3_m4_obbo_order.md"
OUT_IMG = OUT_DIR / "m3_m4_obbo_order_overlay.jpg"


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
]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def unit(vector: list[float] | tuple[float, float]) -> tuple[float, float]:
    mag = math.hypot(vector[0], vector[1])
    return (vector[0] / mag, vector[1] / mag)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def distance_to_line(point: tuple[float, float], origin: tuple[float, float], vector: tuple[float, float]) -> float:
    px, py = point
    ox, oy = origin
    vx, vy = unit(vector)
    return abs((px - ox) * vy - (py - oy) * vx)


def projection(point: tuple[float, float], origin: tuple[float, float], vector: tuple[float, float]) -> float:
    px, py = point
    ox, oy = origin
    vx, vy = unit(vector)
    return (px - ox) * vx + (py - oy) * vy


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
) -> tuple[float, float] | None:
    x1, y1 = p1
    x2, y2 = p2
    vx1, vy1 = v1
    vx2, vy2 = v2
    cross = vx1 * vy2 - vy1 * vx2
    if abs(cross) < 1e-9:
        return None
    t = ((x2 - x1) * vy2 - (y2 - y1) * vx2) / cross
    return (x1 + t * vx1, y1 + t * vy1)


def between_axes(
    point: tuple[float, float],
    vertex: tuple[float, float],
    m3: dict[str, Any],
    m3_vec: tuple[float, float],
    m4: dict[str, Any],
    m4_vec: tuple[float, float],
) -> bool:
    x, y = point
    if x < vertex[0]:
        return False
    y3 = line_y(tuple(m3["center"]), m3_vec, x)
    y4 = line_y(tuple(m4["center"]), m4_vec, x)
    lo, hi = sorted([y3, y4])
    return lo <= y <= hi


def label_initials(records: list[dict[str, Any]]) -> str:
    out = []
    for record in records:
        parts = [part for part in record["label"].replace("$", "").split() if part]
        out.append("".join(part[0].lower() for part in parts))
    return " ".join(out)


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for key, value in streams.items():
        found = [term for term in INSTRUCTION_TERMS if f" {term} " in f" {value.lower()} "]
        if found:
            hits[key] = found
    return hits


def load_standalone_marks() -> tuple[dict[str, Any], dict[str, Any]]:
    data = json.loads(MARKS.read_text(encoding="utf-8"))
    m3 = next(item for item in data["analyses"] if item["index"] == 3)
    m4 = next(item for item in data["analyses"] if item["index"] == 4)
    return m3, m4


def load_anchors() -> list[dict[str, Any]]:
    data = json.loads(ANCHORS.read_text(encoding="utf-8"))
    return data["anchors"]


def draw_overlay(anchors: list[dict[str, Any]], m3: dict[str, Any], m4: dict[str, Any], m3_vec: tuple[float, float], m4_vec: tuple[float, float], vertex: tuple[float, float] | None) -> None:
    im = Image.open(PAGE76).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    label_font = font(24, True)
    small_font = font(18)

    crop = (360, 2108, 2544, 3218)

    def tr_box(box: list[float]) -> tuple[int, int, int, int]:
        return tuple(int(round(v)) for v in box)

    def tr_point(point: tuple[float, float]) -> tuple[int, int]:
        return (int(round(point[0])), int(round(point[1])))

    right_x = im.width
    left_x = 360
    for mark, vec, color, label in [
        (m3, m3_vec, (122, 35, 190, 235), "M3"),
        (m4, m4_vec, (35, 110, 210, 235), "M4"),
    ]:
        draw.rectangle(tr_box(mark["box"]), outline=color, width=6)
        draw.text((mark["box"][0], mark["box"][1] - 30), label, font=label_font, fill=color)
        p_left = (left_x, line_y(tuple(mark["center"]), vec, left_x))
        p_right = (right_x, line_y(tuple(mark["center"]), vec, right_x))
        draw.line([tr_point(p_left), tr_point(p_right)], fill=color, width=4)

    if vertex:
        draw.ellipse((vertex[0] - 10, vertex[1] - 10, vertex[0] + 10, vertex[1] + 10), fill=(255, 185, 0, 230))
        draw.text((vertex[0] + 12, vertex[1] - 10), "axis vertex", font=small_font, fill=(150, 85, 0, 255))

    for idx, anchor in enumerate(anchors, 1):
        color = (255, 145, 0, 240) if anchor["color"] == "orange" else (25, 32, 42, 240)
        draw.rectangle(tr_box(anchor["box"]), outline=color, width=5)
        draw.text((anchor["box"][0], anchor["box"][1] - 28), f"{idx}. {anchor['label']}", font=small_font, fill=color)

    composed = Image.alpha_composite(im, overlay).convert("RGB")
    composed.crop(crop).save(OUT_IMG, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    m3, m4 = load_standalone_marks()
    anchors = load_anchors()
    m3_vec = unit(m3["axis"]["vector"])
    m4_vec = unit(m4["axis"]["vector"])
    vertex = line_intersection(tuple(m3["center"]), m3_vec, tuple(m4["center"]), m4_vec)

    records = []
    for anchor in anchors:
        c = center(anchor["box"])
        rec = {
            "id": anchor["id"],
            "label": anchor["label"],
            "color": anchor["color"],
            "box": anchor["box"],
            "center": [round(c[0], 2), round(c[1], 2)],
            "distanceToM3Center": round(distance(c, tuple(m3["center"])), 2),
            "distanceToM4Center": round(distance(c, tuple(m4["center"])), 2),
            "distanceToM3Axis": round(distance_to_line(c, tuple(m3["center"]), m3_vec), 2),
            "distanceToM4Axis": round(distance_to_line(c, tuple(m4["center"]), m4_vec), 2),
            "projectionOnM3Axis": round(projection(c, tuple(m3["center"]), m3_vec), 2),
            "projectionOnM4Axis": round(projection(c, tuple(m4["center"]), m4_vec), 2),
            "insideM3M4Wedge": between_axes(c, vertex, m3, m3_vec, m4, m4_vec) if vertex else False,
        }
        rec["minAxisDistance"] = min(rec["distanceToM3Axis"], rec["distanceToM4Axis"])
        rec["minCenterDistance"] = min(rec["distanceToM3Center"], rec["distanceToM4Center"])
        records.append(rec)

    rankings = {
        "visualTopToBottom": sorted(records, key=lambda item: item["center"][1]),
        "nearestM3Center": sorted(records, key=lambda item: item["distanceToM3Center"]),
        "nearestM4Center": sorted(records, key=lambda item: item["distanceToM4Center"]),
        "nearestAnyCenter": sorted(records, key=lambda item: item["minCenterDistance"]),
        "nearestM3Axis": sorted(records, key=lambda item: item["distanceToM3Axis"]),
        "nearestM4Axis": sorted(records, key=lambda item: item["distanceToM4Axis"]),
        "nearestAnyAxis": sorted(records, key=lambda item: item["minAxisDistance"]),
        "m3ProjectionForward": sorted(records, key=lambda item: item["projectionOnM3Axis"]),
        "m4ProjectionForward": sorted(records, key=lambda item: item["projectionOnM4Axis"]),
    }

    streams = {
        name: " | ".join(record["label"] for record in ranking)
        for name, ranking in rankings.items()
    }
    streams.update({f"{name}Initials": label_initials(ranking) for name, ranking in rankings.items()})
    wedge = [record for record in records if record["insideM3M4Wedge"]]
    streams["insideWedge"] = " | ".join(record["label"] for record in wedge)
    streams["insideWedgeInitials"] = label_initials(wedge)

    draw_overlay(anchors, m3, m4, m3_vec, m4_vec, vertex)

    assessment = [
        "M3/M4 do not order all four O-B-B-O anchors.",
        "The M3/M4 wedge selects only the O5 endpoint (`shitcoiner at heart`) among the four anchors.",
        "Distance and projection rankings are dominated by geometry around the lower-right endpoint; they do not produce an instruction-like sequence.",
        "G5/Volcano Bonds is not chosen by the M3/M4 wedge; it remains part of the p78 frame/G5/O5 path, not the standalone mark path.",
        "M3/M4 should stay classified as endpoint/bracket evidence for O5, not as the final extraction-order rule.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bounded M3/M4 ordering audit over the four page-76 OBBO anchors; no key derivation",
        "sources": {
            "marks": str(MARKS.relative_to(ROOT)),
            "anchors": str(ANCHORS.relative_to(ROOT)),
        },
        "overlay": str(OUT_IMG.relative_to(ROOT)),
        "m3": {"box": m3["box"], "center": m3["center"], "axis": m3["axis"]},
        "m4": {"box": m4["box"], "center": m4["center"], "axis": m4["axis"]},
        "axisIntersectionVertex": [round(vertex[0], 2), round(vertex[1], 2)] if vertex else None,
        "anchorRecords": records,
        "streams": streams,
        "instructionHits": instruction_hits(streams),
        "assessment": assessment,
        "decision": "Do not use M3/M4 as an OBBO ordering selector; keep them as O5 endpoint/bracket evidence.",
        "nextMove": "Return to the p78 frame/G5/O5 source-registration path and ask what external/source rule supplies the extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# M3/M4 O-B-B-O Ordering Audit",
        "",
        "Scope: bounded M3/M4 ordering audit over the four page-76 OBBO anchors. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        f"- Axis intersection vertex: `{result['axisIntersectionVertex']}`",
        "",
        "## Anchor Metrics",
        "",
        "| anchor | color | M3 center | M4 center | M3 axis | M4 axis | inside wedge |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for record in records:
        lines.append(
            f"| `{record['label']}` | `{record['color']}` | `{record['distanceToM3Center']}` | "
            f"`{record['distanceToM4Center']}` | `{record['distanceToM3Axis']}` | "
            f"`{record['distanceToM4Axis']}` | `{record['insideM3M4Wedge']}` |"
        )
    lines.extend(["", "## Ordering Streams", ""])
    for key in [
        "visualTopToBottom",
        "nearestM3Center",
        "nearestM4Center",
        "nearestAnyAxis",
        "m3ProjectionForward",
        "m4ProjectionForward",
        "insideWedge",
    ]:
        lines.append(f"- `{key}`: `{streams[key]}`")
    lines.append(f"- Instruction hits: `{result['instructionHits']}`")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_IMG}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
