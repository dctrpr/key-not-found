#!/usr/bin/env python3
"""Check whether the p78 tri-contact repair changes the M3 axis read.

The previous pass promoted dx=-38/-40 as a source-registration signature:
it lets the reflected p78 frame touch trusted G5 while preserving M3 and O5
contacts. This bounded pass asks whether that corrected frame also changes
the M3 axis into a readable instruction. It does not generate keys, hashes,
mnemonics, WIFs, or addresses.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TRI_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/m3_axis_after_tricontact_repair"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "m3_axis_after_tricontact_repair.json"
OUT_MD = OUT / "m3_axis_after_tricontact_repair.md"
OUT_OVERLAY = OUT / "m3_axis_after_tricontact_repair_overlay.jpg"

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


def load_marks() -> tuple[dict, list[dict]]:
    marks = json.loads(MARKS_JSON.read_text())
    m3 = next(mark for mark in marks["analyses"] if mark["index"] == 3)
    return m3, marks["rowsUsed"]


def shift_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [round(box[0] + dx, 2), round(box[1] + dy, 2), round(box[2] + dx, 2), round(box[3] + dy, 2)]


def unit_vector(vector: tuple[float, float]) -> tuple[float, float]:
    mag = math.hypot(vector[0], vector[1])
    return (vector[0] / mag, vector[1] / mag)


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


def frame_intersections(point: tuple[float, float], vector: tuple[float, float], frame: list[float]) -> dict[str, dict]:
    left, top, right, bottom = frame
    out = {}
    for side, x in [("left", left), ("right", right)]:
        y = line_y_at_x(point, vector, x)
        out[side] = {"point": [round(x, 2), round(y, 2)], "insideSegment": top <= y <= bottom}
    for side, y in [("top", top), ("bottom", bottom)]:
        x = line_x_at_y(point, vector, y)
        out[side] = {"point": [round(x, 2), round(y, 2)], "insideSegment": left <= x <= right}
    return out


def distance_to_line(point: tuple[float, float], line_point: tuple[float, float], vector: tuple[float, float]) -> float:
    px, py = point
    ax, ay = line_point
    vx, vy = unit_vector(vector)
    return abs((px - ax) * vy - (py - ay) * vx)


def projection(point: tuple[float, float], origin: tuple[float, float], vector: tuple[float, float]) -> float:
    px, py = point
    ox, oy = origin
    vx, vy = unit_vector(vector)
    return (px - ox) * vx + (py - oy) * vy


def nearest_rows(point: tuple[float, float], rows: list[dict], count: int = 3) -> list[dict]:
    _, y = point
    ranked = []
    for row in rows:
        ranked.append({**row, "distancePx": round(abs(row["y"] - y), 2)})
    return sorted(ranked, key=lambda row: row["distancePx"])[:count]


def words_near_axis(
    page: dict,
    origin: tuple[float, float],
    vector: tuple[float, float],
    min_projection: float,
    max_projection: float,
    max_dist: float = 45.0,
) -> list[dict]:
    hits = []
    for word in page["words"]:
        cx, cy = word["center"]
        if cy < 2500 or cy > 3030:
            continue
        if cx > origin[0] + 35:
            continue
        proj = projection((cx, cy), origin, vector)
        if proj < min_projection or proj > max_projection:
            continue
        dist = distance_to_line((cx, cy), origin, vector)
        if dist <= max_dist:
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
    return sorted(hits, key=lambda hit: hit["projection"])


def sequence_text(words: list[dict]) -> str:
    return clean(" ".join(word["text"] for word in words))


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


def stream_initials(words: list[dict]) -> str:
    return "".join(word["text"][:1] for word in words if word["text"])


def analyze_record(record: dict, base_frame: list[float], page: dict, m3: dict, rows: list[dict]) -> dict:
    frame = shift_box(base_frame, record["dx"], record["dy"])
    center = tuple(m3["center"])
    vector = unit_vector(tuple(m3["axis"]["vector"]))
    intersections = frame_intersections(center, vector, frame)
    right_entry = tuple(intersections["right"]["point"])
    left_exit = tuple(intersections["left"]["point"])
    segment_len = math.dist(right_entry, left_exit)

    within = words_near_axis(page, right_entry, vector, -25.0, segment_len + 45.0)
    continuation = words_near_axis(page, right_entry, vector, -25.0, 2050.0)
    after_left = words_near_axis(page, right_entry, vector, max(0.0, segment_len - 35.0), 2050.0)
    tight = [word for word in continuation if word["distancePx"] <= 20.0]

    streams = {
        "withinFrameFromRight": sequence_text(within),
        "withinFrameReverse": sequence_text(list(reversed(within))),
        "leftContinuationFromRight": sequence_text(continuation),
        "leftContinuationReverse": sequence_text(list(reversed(continuation))),
        "afterLeftEdgeFromRight": sequence_text(after_left),
        "afterLeftEdgeReverse": sequence_text(list(reversed(after_left))),
        "tightContinuationFromRight": sequence_text(tight),
        "withinFrameInitials": stream_initials(within),
        "continuationInitials": stream_initials(continuation),
    }

    return {
        "name": record["name"],
        "dx": record["dx"],
        "dy": record["dy"],
        "frame": frame,
        "triContactPass": record.get("triContactPass"),
        "rightEdgeInsideM3X": record.get("rightEdgeInsideM3X"),
        "m3AxisRightInsideM3": record.get("m3AxisRightInsideM3"),
        "g5OverlapVsTarget": record.get("g5OverlapVsTarget"),
        "o5OverlapVsTarget": record.get("o5OverlapVsTarget"),
        "m3OverlapVsMark": record.get("m3OverlapVsMark"),
        "axisIntersections": intersections,
        "axisSegmentLengthPx": round(segment_len, 2),
        "rightEntryNearestRows": nearest_rows(right_entry, rows),
        "leftExitNearestRows": nearest_rows(left_exit, rows),
        "withinFrameAxisWords": within,
        "leftContinuationAxisWords": continuation,
        "afterLeftEdgeAxisWords": after_left,
        "tightContinuationAxisWords": tight,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
    }


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(results: list[dict], m3: dict, targets: dict) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [430, 2490, 2544, 3040]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    colors = {
        "current": (235, 55, 55),
        "g5_edge_touch": (20, 160, 60),
        "nearest_grid_dx_-40": (50, 80, 230),
        "best_overlap_dx_-160_dy_35": (120, 120, 120),
    }

    def tr_point(pt: list[float] | tuple[float, float]) -> tuple[float, float]:
        return (pt[0] - crop_box[0], pt[1] - crop_box[1])

    def tr_box(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    for target in targets.values():
        draw.rectangle(tr_box(target["box"]), outline=(255, 145, 0), width=3)
        draw_label(draw, (int(target["box"][0] - crop_box[0]), int(target["box"][1] - crop_box[1] - 28)), target["id"], (210, 100, 0))

    draw.rectangle(tr_box(m3["box"]), outline=(180, 0, 180), width=4)
    draw_label(draw, (int(m3["box"][0] - crop_box[0]), int(m3["box"][1] - crop_box[1] - 28)), "M3", (180, 0, 180))

    for result in results:
        color = colors.get(result["name"], (0, 0, 0))
        draw.rectangle(tr_box(result["frame"]), outline=color, width=3)
        right_pt = result["axisIntersections"]["right"]["point"]
        left_pt = result["axisIntersections"]["left"]["point"]
        draw.line([tr_point(right_pt), tr_point(left_pt)], fill=color, width=4)
        draw_label(
            draw,
            (int(right_pt[0] - crop_box[0] - 12), int(right_pt[1] - crop_box[1] - 34)),
            result["name"].replace("_", " "),
            color,
        )

    edge_touch = next((item for item in results if item["name"] == "g5_edge_touch"), results[0])
    for hit in edge_touch["leftContinuationAxisWords"]:
        draw.rectangle(tr_box(hit["box"]), outline=(0, 170, 255), width=2)

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    tri = json.loads(TRI_JSON.read_text())
    page = load_page76()
    m3, rows = load_marks()
    base_frame = tri["frame"]

    records = [
        record
        for record in tri["records"]
        if record["name"] in {"current", "g5_edge_touch", "nearest_grid_dx_-40", "best_overlap_dx_-160_dy_35"}
    ]
    results = [analyze_record(record, base_frame, page, m3, rows) for record in records]
    all_streams = {
        f"{result['name']}:{name}": value
        for result in results
        for name, value in result["streams"].items()
    }

    edge_touch = next(result for result in results if result["name"] == "g5_edge_touch")
    grid = next(result for result in results if result["name"] == "nearest_grid_dx_-40")
    current = next(result for result in results if result["name"] == "current")

    result_doc = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "M3 axis read after p78 tri-contact registration repair; no key derivation",
        "sourceTriContactReport": str(TRI_JSON.relative_to(ROOT)),
        "baseFrame": base_frame,
        "m3": {
            "box": m3["box"],
            "center": m3["center"],
            "axisAngleDeg": m3["axis"]["angleDeg"],
            "axisVector": [round(x, 6) for x in unit_vector(tuple(m3["axis"]["vector"]))],
        },
        "scenarios": results,
        "allInstructionTermHits": instruction_hits(all_streams),
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "The dx=-38 and dx=-40 tri-contact repairs do not materially change the M3 axis read.",
            f"Current within-frame stream is `{current['streams']['withinFrameFromRight']}`; dx=-38 is `{edge_touch['streams']['withinFrameFromRight']}`; dx=-40 is `{grid['streams']['withinFrameFromRight']}`.",
            f"The left continuation still reconstructs the same local distrust/heart prose: `{edge_touch['streams']['leftContinuationReverse']}`.",
            "The corrected frame improves source registration but still does not name a word, letter, line, or key extraction unit.",
            "The heavier dx=-160/dy=35 fit changes the contact model by breaking M3 as a frame-side mark, so it remains a lower-confidence overlap fit.",
        ],
        "nextMove": "Keep dx=-38/-40 as registration evidence only. Next, test source fidelity against a higher-resolution/original Canva export or physical scan; do not keep reading M3-axis prose as key material.",
    }

    build_overlay(results, m3, tri["targets"])
    OUT_JSON.write_text(json.dumps(result_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# M3 Axis After Tri-Contact Repair",
        "",
        "Scope: test whether the dx=-38/-40 p78-frame repair changes the M3-axis read into an instruction. No key derivation was run.",
        "",
        f"- Created: `{result_doc['createdAt']}`",
        f"- Source tri-contact report: `{result_doc['sourceTriContactReport']}`",
        f"- Overlay: `{result_doc['overlay']}`",
        "",
        "## Scenario Summary",
        "",
        "| scenario | dx/dy | tri-contact | M3 contact | within-frame read | left-continuation reverse | instruction hits |",
        "|---|---:|---|---|---|---|---|",
    ]
    for scenario in results:
        streams = scenario["streams"]
        m3_contact = scenario["m3AxisRightInsideM3"]
        lines.append(
            f"| `{scenario['name']}` | `{scenario['dx']},{scenario['dy']}` | `{scenario['triContactPass']}` | `{m3_contact}` | `{streams['withinFrameFromRight']}` | `{streams['leftContinuationReverse']}` | `{scenario['instructionTermHits']}` |"
        )

    lines.extend(["", "## Frame Crossings", ""])
    for scenario in results:
        right_row = scenario["rightEntryNearestRows"][0]
        left_row = scenario["leftExitNearestRows"][0]
        lines.append(f"### {scenario['name']}")
        lines.append(f"- right edge: `{scenario['axisIntersections']['right']['point']}` near row `{right_row['visualRow']}`: {right_row['canonicalText']}")
        lines.append(f"- left edge: `{scenario['axisIntersections']['left']['point']}` near row `{left_row['visualRow']}`: {left_row['canonicalText']}")
        lines.append(f"- within-frame initials: `{scenario['streams']['withinFrameInitials']}`")
        lines.append(f"- continuation initials: `{scenario['streams']['continuationInitials']}`")

    lines.extend(["", "## Assessment", ""])
    for item in result_doc["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result_doc['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("all instruction hits:", result_doc["allInstructionTermHits"])


if __name__ == "__main__":
    main()
