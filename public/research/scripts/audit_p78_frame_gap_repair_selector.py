#!/usr/bin/env python3
"""Test the tempting p78-frame gap repair as a selector.

The trusted G5 box sits 38px left of the current reflected p78 frame. A dx=-40
shift is the smallest repair that makes the frame touch/overlap G5 while still
clipping O5. This script tests whether that repaired frame produces a cleaner
instruction stream than the current frame.

No key derivation is performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json"
SENS_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_frame_gap_repair_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_gap_repair_selector.json"
OUT_MD = OUT / "p78_frame_gap_repair_selector.md"
OUT_OVERLAY = OUT / "p78_frame_gap_repair_selector_overlay.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "word",
    "letter",
    "line",
    "left",
    "right",
    "mirror",
    "fold",
    "key",
    "private",
    "first",
    "last",
    "middle",
    "down",
    "up",
]


def shift(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def edge_contacts(frame: list[float], target: list[float], tolerance: float = 55.0) -> list[dict]:
    x1, y1, x2, y2 = frame
    tx1, ty1, tx2, ty2 = target
    contacts = []
    vertical_overlap = max(0.0, min(y2, ty2) - max(y1, ty1))
    horizontal_overlap = max(0.0, min(x2, tx2) - max(x1, tx1))

    for edge, x in [("left", x1), ("right", x2)]:
        if ty2 >= y1 and ty1 <= y2:
            if tx1 <= x <= tx2:
                relation = "cuts"
                dist = 0.0
            elif tx2 < x:
                relation = "right-adjacent"
                dist = x - tx2
            else:
                relation = "left-adjacent"
                dist = tx1 - x
            if dist <= tolerance:
                contacts.append(
                    {
                        "edge": edge,
                        "relation": relation,
                        "distancePx": round(dist, 2),
                        "alongOverlapPx": round(vertical_overlap, 2),
                    }
                )

    for edge, y in [("top", y1), ("bottom", y2)]:
        if tx2 >= x1 and tx1 <= x2:
            if ty1 <= y <= ty2:
                relation = "cuts"
                dist = 0.0
            elif ty2 < y:
                relation = "below-adjacent"
                dist = y - ty2
            else:
                relation = "above-adjacent"
                dist = ty1 - y
            if dist <= tolerance:
                contacts.append(
                    {
                        "edge": edge,
                        "relation": relation,
                        "distancePx": round(dist, 2),
                        "alongOverlapPx": round(horizontal_overlap, 2),
                    }
                )
    return contacts


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def initials(labels: list[str]) -> str:
    out = []
    for label in labels:
        ws = words(label)
        out.append(ws[0][0] if ws else "")
    return "".join(out)


def lasts(labels: list[str]) -> str:
    out = []
    for label in labels:
        ws = words(label)
        out.append(ws[-1][-1] if ws else "")
    return "".join(out)


def hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if term in low]


def analyze_frame(name: str, frame: list[float], records: list[dict]) -> dict:
    rows = []
    for rec in records:
        target = [float(v) for v in rec["box"]]
        inter = intersection(frame, target)
        contacts = edge_contacts(frame, target)
        overlap = area(inter) if inter else 0.0
        if overlap > 0 or contacts:
            rows.append(
                {
                    "id": rec["id"],
                    "label": rec["label"],
                    "box": target,
                    "intersection": inter,
                    "overlapVsTarget": round(overlap / max(1.0, area(target)), 5),
                    "contacts": contacts,
                    "top": target[1],
                    "left": target[0],
                }
            )
    top_down = sorted(rows, key=lambda row: (row["top"], row["left"]))
    labels = [row["label"] for row in top_down]
    cut_labels = [row["label"] for row in top_down if row["overlapVsTarget"] > 0]
    streams = {
        "topDownLabels": " | ".join(labels),
        "topDownInitials": initials(labels),
        "topDownLasts": lasts(labels),
        "cutLabels": " | ".join(cut_labels),
        "cutInitials": initials(cut_labels),
        "cutLasts": lasts(cut_labels),
        "minimalCornerLike": " | ".join([labels[0], "Volcano Bonds", labels[-1]]) if labels else "",
    }
    stream_hits = {key: hits(value) for key, value in streams.items()}
    return {
        "name": name,
        "frame": frame,
        "eventCount": len(rows),
        "events": top_down,
        "streams": streams,
        "streamInstructionHits": stream_hits,
    }


def draw_overlay(current: list[float], repaired: list[float], records: list[dict]) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [700, 2320, 2300, 3030]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)

    def tr(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    def label(xy, text, fill):
        try:
            font = ImageFont.truetype("Arial.ttf", 22)
        except OSError:
            font = ImageFont.load_default()
        x, y = xy
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
        draw.text((x, y), text, fill=fill, font=font)

    draw.rectangle(tr(current), outline=(255, 0, 0), width=4)
    draw.rectangle(tr(repaired), outline=(0, 160, 60), width=4)
    label((int(current[0] - crop_box[0]), int(current[1] - crop_box[1] + 8)), "current", (255, 0, 0))
    label((int(repaired[0] - crop_box[0]), int(repaired[1] - crop_box[1] + 38)), "dx=-40 repair", (0, 160, 60))
    for rec in records:
        if rec["id"] in {"G5", "O5", "should_sell", "trust_guy"}:
            color = (0, 80, 255) if rec["id"] == "G5" else (255, 120, 0) if rec["id"] == "O5" else (100, 100, 100)
            box = [float(v) for v in rec["box"]]
            draw.rectangle(tr(box), outline=color, width=3)
            label((int(box[0] - crop_box[0]), int(box[1] - crop_box[1] - 26)), rec["id"], color)
    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    edge = json.loads(EDGE_JSON.read_text())
    sens = json.loads(SENS_JSON.read_text())
    records = edge["records"]
    current = [float(v) for v in sens["frame"]]
    repaired = shift(current, -40, 0)
    best_heavy = shift(current, -160, 35)
    analyses = [
        analyze_frame("current", current, records),
        analyze_frame("nearest_g5_touch_dx_minus_40", repaired, records),
        analyze_frame("heavy_best_overlap_dx_minus_160_dy_35", best_heavy, records),
    ]
    draw_overlay(current, repaired, records)

    assessment = [
        "The smallest G5-gap repair (dx=-40) makes trusted G5 a true frame cut but does not create an instruction stream.",
        "The repaired top-down stream remains corridor prose: should sell, earnings, G5, pay/IMF, tagged Mike, could sell, trust guy, O5.",
        "The repair changes geometry confidence, not extraction semantics; it still does not name word/letter/line/key/mirror.",
        "A heavier shift can increase overlaps, but that is arbitrary local fitting and should not be promoted without an external source transform.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "test whether the dx=-40 p78-frame G5-gap repair becomes a selector; no key derivation",
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "analyses": analyses,
        "assessment": assessment,
        "nextMove": "Close the local p78-frame gap-repair selector. Use dx=-40 only as a validation signature for a new source/physical registration, not as an extraction rule.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P78 Frame Gap-Repair Selector",
        "",
        "Scope: test whether the smallest trusted-G5 gap repair turns the p78 frame into a clean selector. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        "",
    ]
    for analysis in analyses:
        lines.extend(
            [
                f"## {analysis['name']}",
                "",
                f"- Frame: `{analysis['frame']}`",
                f"- Event count: `{analysis['eventCount']}`",
            ]
        )
        for key, value in analysis["streams"].items():
            hit_text = ", ".join(analysis["streamInstructionHits"][key]) if analysis["streamInstructionHits"][key] else "none"
            lines.append(f"- `{key}` hits={hit_text}: `{value}`")
        lines.extend(["", "| order | id | label | overlap | contacts |", "|---:|---|---|---:|---|"])
        for i, event in enumerate(analysis["events"], 1):
            contacts = "; ".join(f"{c['edge']} {c['relation']} {c['distancePx']}px" for c in event["contacts"]) or "-"
            lines.append(f"| {i} | `{event['id']}` | {event['label']} | `{event['overlapVsTarget']}` | {contacts} |")
        lines.append("")

    lines.extend(["## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    for analysis in analyses:
        print(analysis["name"], analysis["streams"]["topDownInitials"], analysis["streamInstructionHits"]["topDownLabels"])


if __name__ == "__main__":
    main()
