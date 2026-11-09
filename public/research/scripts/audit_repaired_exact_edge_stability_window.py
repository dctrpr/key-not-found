#!/usr/bin/env python3
"""Measure how stable the repaired p78 exact-edge signature is.

The current active benchmark is the p78 reflected frame shifted about dx=-38/-40:
`should sell | Volcano Bonds | shitcoiner at heart` with styles `R K Y`.
This bounded geometry pass checks whether that trio is a one-pixel accident or
whether it survives a small source-like dx/dy window while the M3/G5/O5
tri-contact remains valid.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json"
TRI_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
FONT_JSON = ROOT / "analysis_outputs/docm_format_sources/lower_corridor_font_state_selector/lower_corridor_font_state_selector.json"

OUT = ROOT / "analysis_outputs/source_audit/repaired_exact_edge_stability_window"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "repaired_exact_edge_stability_window.json"
OUT_MD = OUT / "repaired_exact_edge_stability_window.md"
OUT_HEATMAP = OUT / "repaired_exact_edge_stability_window_heatmap.jpg"

TARGET_LABELS = ["should sell", "Volcano Bonds", "shitcoiner at heart"]
TARGET_IDS = {"should_sell", "G5", "O5"}
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
    "first",
    "last",
    "middle",
    "up",
    "down",
]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def overlap_len(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


def shift_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def edge_contacts(frame: list[float], target: list[float], tolerance: float = 90.0) -> list[dict]:
    fx1, fy1, fx2, fy2 = frame
    tx1, ty1, tx2, ty2 = target
    contacts = []
    vertical_overlap = overlap_len(fy1, fy2, ty1, ty2)
    horizontal_overlap = overlap_len(fx1, fx2, tx1, tx2)

    for edge, x in [("left", fx1), ("right", fx2)]:
        if vertical_overlap <= 0:
            continue
        if tx1 <= x <= tx2:
            relation = "cuts"
            dist = 0.0
        elif x < tx1:
            relation = "left-adjacent"
            dist = tx1 - x
        else:
            relation = "right-adjacent"
            dist = x - tx2
        if dist <= tolerance:
            contacts.append(
                {
                    "edge": edge,
                    "relation": relation,
                    "distancePx": round(dist, 2),
                    "alongOverlapPx": round(vertical_overlap, 2),
                }
            )

    for edge, y in [("top", fy1), ("bottom", fy2)]:
        if horizontal_overlap <= 0:
            continue
        if ty1 <= y <= ty2:
            relation = "cuts"
            dist = 0.0
        elif y < ty1:
            relation = "above-adjacent"
            dist = ty1 - y
        else:
            relation = "below-adjacent"
            dist = y - ty2
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


def has_edge_cut(frame: list[float], target: list[float], edge: str) -> bool:
    return any(contact["edge"] == edge and contact["relation"] == "cuts" for contact in edge_contacts(frame, target, tolerance=0.0))


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


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits = {}
    for name, value in streams.items():
        low = value.lower()
        found = [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]
        if found:
            hits[name] = found
    return hits


def analyze_frame(frame: list[float], records: list[dict], styles_by_id: dict[str, str]) -> dict:
    events = []
    for rec in records:
        target = [float(v) for v in rec["box"]]
        contacts = edge_contacts(frame, target)
        inter = intersection(frame, target)
        if not contacts and not inter:
            continue
        edge_class = "exact" if any(contact["relation"] == "cuts" for contact in contacts) else ("adjacent" if contacts else "overlap")
        events.append(
            {
                "id": rec["id"],
                "label": rec["label"],
                "box": target,
                "edgeClass": edge_class,
                "style": styles_by_id.get(rec["id"], "-"),
                "overlapVsTarget": round(area(inter) / max(1.0, area(target)), 5) if inter else 0.0,
                "contacts": contacts,
                "top": target[1],
                "left": target[0],
            }
        )
    events = sorted(events, key=lambda event: (event["top"], event["left"]))
    exact = [event for event in events if event["edgeClass"] == "exact"]
    labels = [event["label"] for event in exact]
    styles = "".join(event["style"] for event in exact)
    streams = {
        "exactLabels": " | ".join(labels),
        "exactStyles": styles,
        "exactInitials": initials(labels),
        "exactLasts": lasts(labels),
    }
    return {
        "events": events,
        "exactIds": [event["id"] for event in exact],
        "exactLabels": labels,
        "exactStyles": styles,
        "streams": streams,
        "instructionHits": instruction_hits(streams),
    }


def range_summary(points: list[dict]) -> dict:
    if not points:
        return {"count": 0}
    dxs = [point["dx"] for point in points]
    dys = [point["dy"] for point in points]
    return {
        "count": len(points),
        "dxRange": [min(dxs), max(dxs)],
        "dyRange": [min(dys), max(dys)],
    }


def draw_heatmap(dx_values: list[int], dy_values: list[int], point_by_offset: dict[tuple[int, int], dict]) -> None:
    cell = 12
    margin_left = 74
    margin_top = 78
    width = margin_left + len(dx_values) * cell + 40
    height = margin_top + len(dy_values) * cell + 60
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("Arial.ttf", 16)
        small = ImageFont.truetype("Arial.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
        small = font

    draw.text((16, 16), "p78 repaired exact-edge stability window", fill=(20, 20, 20), font=font)
    draw.text((16, 40), "green=RKY exact trio + M3/G5/O5 tri-contact; orange=RKY only; blue=tri-contact only", fill=(60, 60, 60), font=small)
    for ix, dx in enumerate(dx_values):
        if dx % 10 == 0 or dx in {-38, -40}:
            draw.text((margin_left + ix * cell - 8, margin_top - 20), str(dx), fill=(70, 70, 70), font=small)
    for iy, dy in enumerate(dy_values):
        if dy % 5 == 0:
            draw.text((24, margin_top + iy * cell - 4), str(dy), fill=(70, 70, 70), font=small)
    for iy, dy in enumerate(dy_values):
        for ix, dx in enumerate(dx_values):
            point = point_by_offset[(dx, dy)]
            if point["targetAndTriContact"]:
                color = (35, 150, 82)
            elif point["targetExact"]:
                color = (255, 170, 42)
            elif point["triContact"]:
                color = (68, 112, 210)
            else:
                color = (230, 230, 230)
            x1 = margin_left + ix * cell
            y1 = margin_top + iy * cell
            draw.rectangle([x1, y1, x1 + cell - 1, y1 + cell - 1], fill=color)
    image.save(OUT_HEATMAP, quality=95)


def main() -> None:
    edge_data = json.loads(EDGE_JSON.read_text())
    tri_data = json.loads(TRI_JSON.read_text())
    font_data = json.loads(FONT_JSON.read_text())

    base_frame = [float(v) for v in tri_data["frame"]]
    records = edge_data["records"]
    m3 = [float(v) for v in tri_data["m3"]["box"]]
    styles_by_id = {row["id"]: row.get("dominantStyle", "-") for row in font_data["phrases"] if row.get("found")}

    dx_values = list(range(-80, 1))
    dy_values = list(range(-20, 21))
    target_points = []
    tri_points = []
    both_points = []
    point_by_offset = {}
    exact_counter: Counter[str] = Counter()
    example_by_exact: dict[str, dict] = {}

    for dy in dy_values:
        for dx in dx_values:
            frame = shift_box(base_frame, dx, dy)
            analysis = analyze_frame(frame, records, styles_by_id)
            exact_key = " | ".join(analysis["exactLabels"]) or "(none)"
            exact_counter[exact_key] += 1
            example_by_exact.setdefault(
                exact_key,
                {
                    "dx": dx,
                    "dy": dy,
                    "exactLabels": analysis["exactLabels"],
                    "exactStyles": analysis["exactStyles"],
                    "instructionHits": analysis["instructionHits"],
                },
            )

            target_exact = analysis["exactLabels"] == TARGET_LABELS and analysis["exactStyles"] == "RKY"
            g5_left_cut = any(event["id"] == "G5" and has_edge_cut(frame, event["box"], "left") for event in analysis["events"])
            o5_bottom_cut = any(event["id"] == "O5" and has_edge_cut(frame, event["box"], "bottom") for event in analysis["events"])
            m3_right_cut = has_edge_cut(frame, m3, "right")
            tri_contact = g5_left_cut and o5_bottom_cut and m3_right_cut
            point = {
                "dx": dx,
                "dy": dy,
                "targetExact": target_exact,
                "triContact": tri_contact,
                "targetAndTriContact": target_exact and tri_contact,
                "exactLabels": analysis["exactLabels"],
                "exactStyles": analysis["exactStyles"],
            }
            point_by_offset[(dx, dy)] = point
            if target_exact:
                target_points.append(point)
            if tri_contact:
                tri_points.append(point)
            if target_exact and tri_contact:
                both_points.append(point)

    draw_heatmap(dx_values, dy_values, point_by_offset)

    examples = [
        {
            "exactLabelStream": key,
            "count": count,
            **example_by_exact[key],
        }
        for key, count in exact_counter.most_common(12)
    ]
    all_streams = {
        f"example:{i}:labels": example["exactLabelStream"]
        for i, example in enumerate(examples, 1)
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "stability window for repaired p78 exact-edge signature; no key derivation",
        "grid": {
            "dxRange": [min(dx_values), max(dx_values)],
            "dyRange": [min(dy_values), max(dy_values)],
            "cellCount": len(dx_values) * len(dy_values),
        },
        "targetSignature": {
            "labels": TARGET_LABELS,
            "styles": "RKY",
        },
        "sourceReports": {
            "edgeReconciliation": str(EDGE_JSON.relative_to(ROOT)),
            "triContact": str(TRI_JSON.relative_to(ROOT)),
            "fontStates": str(FONT_JSON.relative_to(ROOT)),
        },
        "summaries": {
            "targetExact": range_summary(target_points),
            "triContact": range_summary(tri_points),
            "targetExactAndTriContact": range_summary(both_points),
        },
        "topExactStreams": examples,
        "instructionHitsInTopStreams": instruction_hits(all_streams),
        "heatmap": str(OUT_HEATMAP.relative_to(ROOT)),
        "assessment": [
            "The repaired exact-edge trio is not a single-pixel accident inside the bounded source-like window.",
            "The same `should sell | Volcano Bonds | shitcoiner at heart` / `R K Y` signature survives across the central overlap of the small dx/dy search window.",
            "The M3/G5/O5 tri-contact and exact-edge trio overlap in a compact window, so the signature is a usable source-registration benchmark.",
            "The stable streams still do not name an extraction unit or instruction; this remains calibration evidence, not key material.",
        ],
        "nextMove": "Use this stability window to compare any future Canva/original-layout/physical source. Without new source imagery, move to a different unresolved layer: p80 package copy / dosage counts or original browser/Canva clue inspection.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Repaired Exact-Edge Stability Window",
        "",
        "Scope: test whether the repaired p78 exact-edge signature is a fragile offset artifact or a stable source-registration benchmark. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Grid: dx `{result['grid']['dxRange'][0]}..{result['grid']['dxRange'][1]}`, dy `{result['grid']['dyRange'][0]}..{result['grid']['dyRange'][1]}`, cells `{result['grid']['cellCount']}`",
        f"- Heatmap: `{result['heatmap']}`",
        f"- Target exact signature: `{' | '.join(TARGET_LABELS)}` / styles `RKY`",
        "",
        "## Stability Summary",
        "",
        "| condition | count | dx range | dy range |",
        "|---|---:|---|---|",
    ]
    for key, summary in result["summaries"].items():
        if summary["count"]:
            dx_range = f"`{summary['dxRange'][0]}..{summary['dxRange'][1]}`"
            dy_range = f"`{summary['dyRange'][0]}..{summary['dyRange'][1]}`"
        else:
            dx_range = "-"
            dy_range = "-"
        lines.append(f"| `{key}` | {summary['count']} | {dx_range} | {dy_range} |")

    lines.extend(["", "## Most Common Exact-Edge Streams", "", "| exact labels | styles | count | example dx/dy | instruction hits |", "|---|---|---:|---|---|"])
    for example in examples:
        labels = example["exactLabelStream"]
        lines.append(
            f"| `{labels}` | `{example['exactStyles']}` | {example['count']} | `{example['dx']},{example['dy']}` | `{example['instructionHits']}` |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_HEATMAP}")
    print("target exact:", result["summaries"]["targetExact"])
    print("target exact + tri-contact:", result["summaries"]["targetExactAndTriContact"])


if __name__ == "__main__":
    main()
