#!/usr/bin/env python3
"""Check exact/near boundary coincidences around the page-76 O-B-B-O anchors."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "obbo_highres_boundary_coincidences"

ANCHORS_JSON = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
TRICONTACT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
M3M4_JSON = ROOT / "analysis_outputs/source_audit/m3_m4_obbo_order/m3_m4_obbo_order.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

EXACT_PX = 6.0
NEAR_PX = 20.0


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def center(box: list[float]) -> tuple[float, float]:
    x0, y0, x1, y1 = box
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def boundaries(box: list[float]) -> dict[str, float]:
    x0, y0, x1, y1 = box
    cx, cy = center(box)
    return {
        "left": x0,
        "right": x1,
        "centerX": cx,
        "top": y0,
        "bottom": y1,
        "centerY": cy,
    }


def compare_entities(a: dict[str, Any], b: dict[str, Any]) -> list[dict[str, Any]]:
    hits = []
    a_bounds = boundaries(a["box"])
    b_bounds = boundaries(b["box"])
    for a_name, a_value in a_bounds.items():
        for b_name, b_value in b_bounds.items():
            same_axis = (a_name in {"left", "right", "centerX"} and b_name in {"left", "right", "centerX"}) or (
                a_name in {"top", "bottom", "centerY"} and b_name in {"top", "bottom", "centerY"}
            )
            if not same_axis:
                continue
            delta = abs(a_value - b_value)
            if delta <= NEAR_PX:
                hits.append(
                    {
                        "a": a["id"],
                        "aLabel": a["label"],
                        "aBoundary": a_name,
                        "b": b["id"],
                        "bLabel": b["label"],
                        "bBoundary": b_name,
                        "axis": "x" if a_name in {"left", "right", "centerX"} else "y",
                        "deltaPx": round(delta, 2),
                        "class": "exact" if delta <= EXACT_PX else "near",
                    }
                )
    return hits


def overlap_1d(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def frame_contact_records(anchors: list[dict[str, Any]], frame: list[float]) -> list[dict[str, Any]]:
    x0, y0, x1, y1 = frame
    records = []
    for anchor in anchors:
        ax0, ay0, ax1, ay1 = anchor["box"]
        horizontal_overlap = overlap_1d(ax0, ax1, x0, x1)
        vertical_overlap = overlap_1d(ay0, ay1, y0, y1)
        left_delta = abs(ax1 - x0)
        right_delta = abs(ax0 - x1)
        top_delta = abs(ay1 - y0)
        bottom_delta = abs(ay0 - y1)
        records.append(
            {
                "anchor": anchor["id"],
                "label": anchor["label"],
                "insideFrame": ax0 >= x0 and ax1 <= x1 and ay0 >= y0 and ay1 <= y1,
                "horizontalOverlapWithFrame": round(horizontal_overlap, 2),
                "verticalOverlapWithFrame": round(vertical_overlap, 2),
                "rightToFrameLeftDelta": round(left_delta, 2),
                "leftToFrameRightDelta": round(right_delta, 2),
                "bottomToFrameTopDelta": round(top_delta, 2),
                "topToFrameBottomDelta": round(bottom_delta, 2),
                "isExactBoundaryContact": min(left_delta, right_delta, top_delta, bottom_delta) <= EXACT_PX,
                "isNearBoundaryContact": min(left_delta, right_delta, top_delta, bottom_delta) <= NEAR_PX,
            }
        )
    return records


def draw_overlay(
    anchors: list[dict[str, Any]],
    frame: list[float],
    marks: list[dict[str, Any]],
    exact_hits: list[dict[str, Any]],
) -> str:
    image = Image.open(PAGE76).convert("RGB")
    crop_box = [320, 2080, 2300, 3060]
    crop = image.crop(crop_box)
    draw = ImageDraw.Draw(crop, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    def local(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    draw.rectangle(local(frame), outline=(255, 50, 50, 255), width=5)
    draw.text((local(frame)[0] + 8, local(frame)[1] + 8), "p78 frame dx=-38", fill=(255, 50, 50, 255), font=font)

    for anchor in anchors:
        color = (255, 128, 0, 210) if anchor["color"] == "orange" else (20, 20, 20, 210)
        box = local(anchor["box"])
        draw.rectangle(box, outline=color, width=5)
        draw.text((box[0], max(0, box[1] - 24)), f"{anchor['id']} {anchor['label']}", fill=color, font=small)
        bx = boundaries(anchor["box"])
        for x_name in ("left", "right", "centerX"):
            x = bx[x_name] - crop_box[0]
            draw.line([(x, box[1]), (x, box[3])], fill=color, width=1)
        for y_name in ("top", "bottom", "centerY"):
            y = bx[y_name] - crop_box[1]
            draw.line([(box[0], y), (box[2], y)], fill=color, width=1)

    for mark in marks:
        box = local(mark["box"])
        draw.rectangle(box, outline=(120, 70, 255, 220), width=4)
        draw.text((box[0], max(0, box[1] - 24)), mark["id"], fill=(120, 70, 255, 255), font=small)

    for hit in exact_hits:
        if hit["axis"] == "x":
            # draw the exact vertical boundary through crop
            entity = next(e for e in anchors + [{"id": "frame", "box": frame}] + marks if e["id"] == hit["a"])
            x = boundaries(entity["box"])[hit["aBoundary"]] - crop_box[0]
            draw.line([(x, 0), (x, crop.height)], fill=(0, 200, 255, 255), width=3)
        else:
            entity = next(e for e in anchors + [{"id": "frame", "box": frame}] + marks if e["id"] == hit["a"])
            y = boundaries(entity["box"])[hit["aBoundary"]] - crop_box[1]
            draw.line([(0, y), (crop.width, y)], fill=(0, 200, 255, 255), width=3)

    out = OUT_DIR / "obbo_highres_boundary_coincidences_overlay.jpg"
    crop.save(out, quality=92)
    return str(out.relative_to(ROOT))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anchor_data = load_json(ANCHORS_JSON)
    tri = load_json(TRICONTACT_JSON)
    m3m4 = load_json(M3M4_JSON)

    wanted = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]
    anchors = []
    for anchor in anchor_data["anchors"]:
        if anchor["id"] in wanted:
            anchors.append(
                {
                    "id": anchor["id"],
                    "label": anchor["label"],
                    "color": anchor["color"],
                    "box": [float(v) for v in anchor["box"]],
                }
            )
    anchors.sort(key=lambda item: wanted.index(item["id"]))

    frame_record = next(record for record in tri["records"] if record["name"] == "g5_edge_touch")
    frame = [float(v) for v in frame_record["frame"]]
    frame_entity = {"id": "frame_dx_minus_38", "label": "p78 frame dx=-38", "box": frame}

    marks = [
        {"id": "M3", "label": "standalone mark M3", "box": [float(v) for v in m3m4["m3"]["box"]]},
        {"id": "M4", "label": "standalone mark M4", "box": [float(v) for v in m3m4["m4"]["box"]]},
    ]

    entity_hits: list[dict[str, Any]] = []
    entities = anchors + [frame_entity] + marks
    for i, a in enumerate(entities):
        for b in entities[i + 1 :]:
            entity_hits.extend(compare_entities(a, b))

    exact_hits = [hit for hit in entity_hits if hit["class"] == "exact"]
    near_hits = [hit for hit in entity_hits if hit["class"] == "near"]
    frame_contacts = frame_contact_records(anchors, frame)

    overlay = draw_overlay(anchors, frame, marks, exact_hits)

    assessment = [
        "Two exact boundary coincidences appear in the active O-B-B-O field: B4/$1 billion top aligns with the repaired frame top within 2 px, and G5/Volcano Bonds right edge equals the repaired frame left edge.",
        "The B4/frame-top hit is only a row/guide alignment because B4 is horizontally outside the repaired frame; it is not a frame contact.",
        "The G5/frame-left hit is the only exact contact-style boundary coincidence.",
        "O5 is a near frame contact because the frame bottom crosses the O5 band, but it is not an exact top/bottom boundary coincidence.",
        "The other O-B-B-O anchors do not provide exact shared contact boundaries with each other, the repaired frame, or M3/M4 mark boxes under the current high-res coordinates.",
        "This means the four-anchor O-B-B-O structure is a corridor/signature, not a complete geometric boundary selector.",
        "Do not extract text from O-B-B-O boundary sides unless a new source clue supplies a boundary side/order.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "O-B-B-O high-res boundary coincidence audit; no text extraction/key derivation",
        "sources": {
            "anchors": str(ANCHORS_JSON.relative_to(ROOT)),
            "triContact": str(TRICONTACT_JSON.relative_to(ROOT)),
            "m3m4": str(M3M4_JSON.relative_to(ROOT)),
        },
        "overlay": overlay,
        "thresholds": {"exactPx": EXACT_PX, "nearPx": NEAR_PX},
        "anchors": anchors,
        "frame": frame_entity,
        "marks": marks,
        "exactBoundaryHits": exact_hits,
        "nearBoundaryHits": near_hits,
        "frameContacts": frame_contacts,
        "assessment": assessment,
        "decision": "Close O-B-B-O boundary coincidence as a standalone selector under the current scan.",
        "nextMove": "Use the four-anchor O-B-B-O only as a corridor signature; next bounded pass should inspect whether the 3D folded view reveals a non-boundary visual ordering cue, not another text/key stream.",
    }

    (OUT_DIR / "obbo_highres_boundary_coincidences.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# O-B-B-O High-Res Boundary Coincidences",
        "",
        "Scope: check whether the four active page-76 O-B-B-O anchors share exact visual boundaries with each other, the repaired p78 frame, or M3/M4. No text extraction, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{overlay}`",
        f"- Exact threshold: `{EXACT_PX}` px; near threshold: `{NEAR_PX}` px",
        "",
        "## Anchors",
        "",
        "| id | color | label | box |",
        "|---|---|---|---|",
    ]
    for anchor in anchors:
        lines.append(f"| `{anchor['id']}` | `{anchor['color']}` | `{anchor['label']}` | `{anchor['box']}` |")

    lines.extend(["", "## Exact Boundary Hits", "", "| a | boundary | b | boundary | axis | delta |", "|---|---|---|---|---|---:|"])
    if exact_hits:
        for hit in exact_hits:
            lines.append(
                f"| `{hit['a']}` | `{hit['aBoundary']}` | `{hit['b']}` | `{hit['bBoundary']}` | `{hit['axis']}` | `{hit['deltaPx']}` |"
            )
    else:
        lines.append("| - | - | - | - | - | - |")

    lines.extend(["", "## Near Boundary Hits", "", "| a | boundary | b | boundary | axis | delta | class |", "|---|---|---|---|---|---:|---|"])
    if near_hits:
        for hit in near_hits:
            lines.append(
                f"| `{hit['a']}` | `{hit['aBoundary']}` | `{hit['b']}` | `{hit['bBoundary']}` | `{hit['axis']}` | `{hit['deltaPx']}` | `{hit['class']}` |"
            )
    else:
        lines.append("| - | - | - | - | - | - | - |")

    lines.extend(["", "## Frame Contacts", "", "| anchor | label | exact contact | near contact | right->frame left | top->frame bottom |", "|---|---|---|---|---:|---:|"])
    for contact in frame_contacts:
        lines.append(
            f"| `{contact['anchor']}` | `{contact['label']}` | `{contact['isExactBoundaryContact']}` | `{contact['isNearBoundaryContact']}` | `{contact['rightToFrameLeftDelta']}` | `{contact['topToFrameBottomDelta']}` |"
        )

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            f"- Next move: {result['nextMove']}",
            "",
        ]
    )
    (OUT_DIR / "obbo_highres_boundary_coincidences.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
