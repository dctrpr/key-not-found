#!/usr/bin/env python3
"""Check reflected p78 frame edges against lower page-76 visual marks.

The previous frame pass only read text candidates. This pass adds the known
page-76 non-text marks from the lower corridor, so the unused right/bottom
edges of the reflected p78 graphic are tested as visual registration surfaces.
It does not generate key candidates, hashes, seed phrases, or addresses.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json"
MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_frame_visual_marks"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_visual_marks.json"
OUT_MD = OUT / "p78_frame_visual_marks.md"
OUT_OVERLAY = OUT / "p78_frame_visual_marks_overlay.jpg"


def overlap_len(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    if box[2] <= box[0] or box[3] <= box[1]:
        return None
    return box


def point_box_distance(point: tuple[float, float], box: list[float]) -> float:
    x, y = point
    dx = max(box[0] - x, 0, x - box[2])
    dy = max(box[1] - y, 0, y - box[3])
    return math.hypot(dx, dy)


def edge_contacts(frame: list[float], box: list[float], adjacent_px: float = 60.0) -> list[dict]:
    left_x, top_y, right_x, bottom_y = frame
    out = []
    horizontal_overlap = overlap_len(left_x, right_x, box[0], box[2])
    vertical_overlap = overlap_len(top_y, bottom_y, box[1], box[3])

    if box[1] <= top_y <= box[3] and horizontal_overlap > 0:
        out.append({"edge": "top", "relation": "cuts", "distancePx": 0.0, "alongOverlapPx": round(horizontal_overlap, 2)})
    elif horizontal_overlap > 0 and 0 < abs(box[3] - top_y) <= adjacent_px:
        out.append({"edge": "top", "relation": "above-adjacent", "distancePx": round(abs(box[3] - top_y), 2), "alongOverlapPx": round(horizontal_overlap, 2)})
    elif horizontal_overlap > 0 and 0 < abs(box[1] - top_y) <= adjacent_px:
        out.append({"edge": "top", "relation": "below-adjacent", "distancePx": round(abs(box[1] - top_y), 2), "alongOverlapPx": round(horizontal_overlap, 2)})

    if box[0] <= left_x <= box[2] and vertical_overlap > 0:
        out.append({"edge": "left", "relation": "cuts", "distancePx": 0.0, "alongOverlapPx": round(vertical_overlap, 2)})
    elif vertical_overlap > 0 and 0 < abs(box[2] - left_x) <= adjacent_px:
        out.append({"edge": "left", "relation": "right-adjacent", "distancePx": round(abs(box[2] - left_x), 2), "alongOverlapPx": round(vertical_overlap, 2)})
    elif vertical_overlap > 0 and 0 < abs(box[0] - left_x) <= adjacent_px:
        out.append({"edge": "left", "relation": "left-adjacent", "distancePx": round(abs(box[0] - left_x), 2), "alongOverlapPx": round(vertical_overlap, 2)})

    if box[1] <= bottom_y <= box[3] and horizontal_overlap > 0:
        out.append({"edge": "bottom", "relation": "cuts", "distancePx": 0.0, "alongOverlapPx": round(horizontal_overlap, 2)})
    elif horizontal_overlap > 0 and 0 < abs(box[1] - bottom_y) <= adjacent_px:
        out.append({"edge": "bottom", "relation": "below-adjacent", "distancePx": round(abs(box[1] - bottom_y), 2), "alongOverlapPx": round(horizontal_overlap, 2)})
    elif horizontal_overlap > 0 and 0 < abs(box[3] - bottom_y) <= adjacent_px:
        out.append({"edge": "bottom", "relation": "above-adjacent", "distancePx": round(abs(box[3] - bottom_y), 2), "alongOverlapPx": round(horizontal_overlap, 2)})

    if box[0] <= right_x <= box[2] and vertical_overlap > 0:
        out.append({"edge": "right", "relation": "cuts", "distancePx": 0.0, "alongOverlapPx": round(vertical_overlap, 2)})
    elif vertical_overlap > 0 and 0 < abs(box[0] - right_x) <= adjacent_px:
        out.append({"edge": "right", "relation": "right-adjacent", "distancePx": round(abs(box[0] - right_x), 2), "alongOverlapPx": round(vertical_overlap, 2)})
    elif vertical_overlap > 0 and 0 < abs(box[2] - right_x) <= adjacent_px:
        out.append({"edge": "right", "relation": "left-adjacent", "distancePx": round(abs(box[2] - right_x), 2), "alongOverlapPx": round(vertical_overlap, 2)})

    return out


def corner_distances(frame: list[float], box: list[float]) -> dict[str, float]:
    corners = {
        "topLeft": (frame[0], frame[1]),
        "topRight": (frame[2], frame[1]),
        "bottomRight": (frame[2], frame[3]),
        "bottomLeft": (frame[0], frame[3]),
    }
    return {name: round(point_box_distance(point, box), 2) for name, point in corners.items()}


def load_text_edge_summary() -> dict[str, list[str]]:
    edge = json.loads(EDGE_JSON.read_text())
    side_hits: dict[str, list[str]] = {"top": [], "left": [], "right": [], "bottom": []}
    for record in edge["records"]:
        label = record["label"]
        for contact in record.get("edgeContacts", []):
            side_hits[contact["edge"]].append(f"{label} ({contact['relation']})")
    return side_hits


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    x, y = xy
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 4
    draw.rectangle([bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(frame: list[float], mark_records: list[dict], text_side_summary: dict[str, list[str]]) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [700, 2320, 2544, 3205]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    def tr(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    draw.rectangle(tr(frame), outline=(255, 0, 0), width=5)
    draw_label(draw, (int(frame[0] - crop_box[0] + 8), int(frame[1] - crop_box[1] + 8)), "p78 reflected frame", (255, 0, 0))

    for record in mark_records:
        color = (210, 0, 210) if record["classification"] == "standalone-mark" else (80, 80, 80)
        draw.rectangle(tr(record["box"]), outline=color, width=4)
        label = f"M{record['index']} {record['classification']}"
        draw_label(draw, (int(record["box"][0] - crop_box[0]), int(record["box"][1] - crop_box[1] - 28)), label, color)

    side_positions = {
        "top": (int(frame[0] - crop_box[0] + 260), int(frame[1] - crop_box[1] - 34)),
        "left": (int(frame[0] - crop_box[0] - 420), int(frame[1] - crop_box[1] + 190)),
        "right": (int(frame[2] - crop_box[0] + 12), int(frame[1] - crop_box[1] + 235)),
        "bottom": (int(frame[0] - crop_box[0] + 230), int(frame[3] - crop_box[1] + 14)),
    }
    for side, items in text_side_summary.items():
        if not items:
            continue
        label = side + ": " + " | ".join(items[:3])
        draw_label(draw, side_positions[side], label[:80], (0, 90, 180))

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    edge = json.loads(EDGE_JSON.read_text())
    marks = json.loads(MARKS_JSON.read_text())
    frame = edge["reflectedP78BoxOnP76"]

    mark_records = []
    for mark in marks["analyses"]:
        box = mark["box"]
        inter = intersection(frame, box)
        inter_area = area(inter) if inter else 0.0
        corners = corner_distances(frame, box)
        nearest_corner = min(corners.items(), key=lambda item: item[1])
        contacts = edge_contacts(frame, box)
        mark_records.append(
            {
                "index": mark["index"],
                "classification": mark["classification"],
                "note": mark.get("note", ""),
                "box": box,
                "intersection": inter,
                "overlapFracOfMark": round(inter_area / area(box), 4) if area(box) else 0.0,
                "overlapFracOfFrame": round(inter_area / area(frame), 4) if area(frame) else 0.0,
                "edgeContacts": contacts,
                "cornerDistancesPx": corners,
                "nearestCorner": [nearest_corner[0], nearest_corner[1]],
                "axis": mark.get("axis"),
                "rowHits": mark.get("rowHits"),
            }
        )

    text_side_summary = load_text_edge_summary()
    visual_side_summary: dict[str, list[str]] = {"top": [], "left": [], "right": [], "bottom": []}
    for record in mark_records:
        for contact in record["edgeContacts"]:
            visual_side_summary[contact["edge"]].append(
                f"M{record['index']} {record['classification']} ({contact['relation']}, {contact['alongOverlapPx']}px)"
            )

    build_overlay(frame, mark_records, text_side_summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "reflected p78 frame edges against known lower page-76 visual marks; no key derivation",
        "reflectedP78BoxOnP76": frame,
        "textSideSummaryFromPriorAudit": text_side_summary,
        "visualSideSummary": visual_side_summary,
        "markRecords": mark_records,
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "keyFindings": {
            "rightEdgeCutsStandaloneMarkM3": any(
                record["index"] == 3 and any(c["edge"] == "right" and c["relation"] == "cuts" for c in record["edgeContacts"])
                for record in mark_records
            ),
            "bottomEdgeAdjacentStandaloneMarkM4": any(
                record["index"] == 4 and any(c["edge"] == "bottom" and c["relation"] == "below-adjacent" for c in record["edgeContacts"])
                for record in mark_records
            ),
        },
        "assessment": [
            "The previous text-only frame read missed the unused right edge: the reflected p78 frame right side cuts true standalone mark M3 by a long vertical overlap.",
            "M4 is not cut by the frame, but sits just below the bottom edge with a 53px vertical gap and broad horizontal overlap.",
            "The frame is therefore not only a text-frame: top/left/bottom relate to corridor text, while the right/lower side also registers lower-right visual marks.",
            "This strengthens the p78 frame as an orientation/registration object, but still does not specify a word/letter extraction unit.",
        ],
        "nextMove": "Inspect M3 itself as a frame-side marker: compare its axis/ray with the reflected p78 right edge and test only simple adjacent-row labels, not key derivation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P78 Frame Visual Marks",
        "",
        "Scope: add known lower page-76 visual marks to the reflected p78 frame-edge audit. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Reflected p78 frame on p76: `{frame}`",
        f"- Overlay: `{result['overlay']}`",
        "",
        "## Side Summary",
        "",
        "| side | text contacts from prior audit | visual-mark contacts |",
        "|---|---|---|",
    ]
    for side in ["top", "left", "right", "bottom"]:
        lines.append(
            f"| `{side}` | {'; '.join(text_side_summary.get(side, [])) or '-'} | {'; '.join(visual_side_summary.get(side, [])) or '-'} |"
        )

    lines.extend(["", "## Mark Contacts", "", "| mark | class | edge contacts | overlap of mark | nearest frame corner |", "|---|---|---|---:|---|"])
    for record in mark_records:
        contacts = "; ".join(f"{c['edge']} {c['relation']} {c['alongOverlapPx']}px d={c['distancePx']}px" for c in record["edgeContacts"]) or "-"
        lines.append(
            f"| `M{record['index']}` | `{record['classification']}` | {contacts} | `{record['overlapFracOfMark']}` | `{record['nearestCorner'][0]}` `{record['nearestCorner'][1]}px` |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("right edge cuts M3:", result["keyFindings"]["rightEdgeCutsStandaloneMarkM3"])
    print("bottom edge adjacent M4:", result["keyFindings"]["bottomEdgeAdjacentStandaloneMarkM4"])


if __name__ == "__main__":
    main()
