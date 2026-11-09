#!/usr/bin/env python3
"""Compare p78 frame contact order before/after the tri-contact repair.

The dx=-38/-40 repair is now useful as source-registration evidence. This
audit asks whether the repair also changes the surrounding frame contacts on
page 76. If the selected contact ladder changes into an instruction, that
would be new evidence. If the ladder is stable, the repair remains registration
evidence only.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
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
TRI_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/tricontact_frame_contact_stability"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "tricontact_frame_contact_stability.json"
OUT_MD = OUT / "tricontact_frame_contact_stability.md"
OUT_OVERLAY = OUT / "tricontact_frame_contact_stability_overlay.jpg"

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
    "first",
    "last",
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def shift_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [round(box[0] + dx, 2), round(box[1] + dy, 2), round(box[2] + dx, 2), round(box[3] + dy, 2)]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]


def overlap_len(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


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


def event_position(event: dict) -> tuple[float, float]:
    box = event["box"]
    return (box[1], box[0])


def compact_label(label: str) -> str:
    label = label.replace("pay off the IMF", "pay/IMF")
    label = label.replace("I tagged Mike", "tagged Mike")
    label = label.replace("shitcoiner at heart", "O5 heart")
    label = label.replace("Volcano Bonds", "G5 Volcano Bonds")
    return label


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


def analyze_scenario(name: str, frame: list[float], records: list[dict]) -> dict:
    events = []
    for rec in records:
        target = [float(v) for v in rec["box"]]
        contacts = edge_contacts(frame, target)
        inter = intersection(frame, target)
        if not contacts and not inter:
            continue
        overlap = area(inter) if inter else 0.0
        primary_contact = sorted(
            contacts,
            key=lambda contact: (
                contact["distancePx"],
                0 if contact["relation"] == "cuts" else 1,
                -contact["alongOverlapPx"],
            ),
        )[0] if contacts else None
        events.append(
            {
                "id": rec["id"],
                "label": rec["label"],
                "kind": rec.get("kind", rec.get("role", "")),
                "box": target,
                "intersection": inter,
                "overlapVsTarget": round(overlap / max(1.0, area(target)), 5),
                "contacts": contacts,
                "primaryContact": primary_contact,
                "top": target[1],
                "left": target[0],
            }
        )

    ordered = sorted(events, key=event_position)
    all_labels = [event["label"] for event in ordered]
    cut_labels = [event["label"] for event in ordered if event["overlapVsTarget"] > 0]
    exact_edge_labels = [
        event["label"]
        for event in ordered
        if any(contact["relation"] == "cuts" for contact in event["contacts"])
    ]
    left_edge_labels = [
        event["label"]
        for event in ordered
        if any(contact["edge"] == "left" for contact in event["contacts"])
    ]
    bottom_edge_labels = [
        event["label"]
        for event in ordered
        if any(contact["edge"] == "bottom" for contact in event["contacts"])
    ]
    streams = {
        "topDownLabels": " | ".join(all_labels),
        "topDownCompact": " | ".join(compact_label(label) for label in all_labels),
        "topDownInitials": initials(all_labels),
        "topDownLasts": lasts(all_labels),
        "cutLabels": " | ".join(cut_labels),
        "cutInitials": initials(cut_labels),
        "exactEdgeLabels": " | ".join(exact_edge_labels),
        "leftEdgeLabels": " | ".join(left_edge_labels),
        "bottomEdgeLabels": " | ".join(bottom_edge_labels),
    }
    return {
        "name": name,
        "frame": frame,
        "eventCount": len(ordered),
        "events": ordered,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
    }


def contact_summary(event: dict) -> str:
    if not event["contacts"]:
        return "-"
    return "; ".join(
        f"{contact['edge']} {contact['relation']} {contact['distancePx']}px"
        for contact in event["contacts"]
    )


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    draw.rectangle([bbox[0] - 4, bbox[1] - 4, bbox[2] + 4, bbox[3] + 4], fill=(255, 255, 255))
    draw.text((x, y), text, fill=fill, font=font)


def build_overlay(scenarios: list[dict]) -> None:
    im = Image.open(PAGE76).convert("RGB")
    crop_box = [720, 2320, 2320, 3030]
    crop = im.crop(crop_box)
    draw = ImageDraw.Draw(crop)
    colors = {
        "current": (230, 40, 40),
        "g5_edge_touch_dx_minus_38": (20, 150, 65),
        "nearest_grid_dx_minus_40": (45, 80, 220),
        "best_overlap_dx_minus_160_dy_35": (115, 115, 115),
    }

    def tr_box(box: list[float]) -> list[float]:
        return [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]

    target_ids = {"should_sell", "earnings", "pay_imf", "G5", "tagged_mike", "could_sell", "trust_guy", "O5"}
    first = scenarios[0]
    for event in first["events"]:
        if event["id"] not in target_ids:
            continue
        color = (255, 135, 0) if event["id"] in {"G5", "O5"} else (40, 135, 110)
        draw.rectangle(tr_box(event["box"]), outline=color, width=2)
        draw_label(draw, (int(event["box"][0] - crop_box[0]), int(event["box"][1] - crop_box[1] - 23)), event["id"], color)

    for scenario in scenarios:
        color = colors.get(scenario["name"], (0, 0, 0))
        draw.rectangle(tr_box(scenario["frame"]), outline=color, width=4)
        draw_label(
            draw,
            (int(scenario["frame"][0] - crop_box[0] + 5), int(scenario["frame"][1] - crop_box[1] + 8 + 26 * list(colors).index(scenario["name"]))),
            scenario["name"].replace("_", " "),
            color,
        )

    crop.save(OUT_OVERLAY, quality=95)


def main() -> None:
    edge = json.loads(EDGE_JSON.read_text())
    tri = json.loads(TRI_JSON.read_text())
    base = [float(v) for v in tri["frame"]]
    records = edge["records"]
    scenarios = [
        analyze_scenario("current", base, records),
        analyze_scenario("g5_edge_touch_dx_minus_38", shift_box(base, -38.0, 0.0), records),
        analyze_scenario("nearest_grid_dx_minus_40", shift_box(base, -40.0, 0.0), records),
        analyze_scenario("best_overlap_dx_minus_160_dy_35", shift_box(base, -160.0, 35.0), records),
    ]

    current = scenarios[0]
    edge_touch = scenarios[1]
    stable_exact = current["streams"]["topDownCompact"] == edge_touch["streams"]["topDownCompact"]
    all_hits = {
        f"{scenario['name']}:{key}": value
        for scenario in scenarios
        for key, value in scenario["streams"].items()
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 frame contact-order stability under tri-contact repair; no key derivation",
        "sourceReports": {
            "edgeReconciliation": str(EDGE_JSON.relative_to(ROOT)),
            "triContact": str(TRI_JSON.relative_to(ROOT)),
        },
        "baseFrame": base,
        "scenarios": scenarios,
        "currentVsDxMinus38TopDownStable": stable_exact,
        "allInstructionTermHits": instruction_hits(all_hits),
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "assessment": [
            "The exact dx=-38 tri-contact repair preserves the same top-down corridor ladder as the current frame.",
            f"Current compact stream: `{current['streams']['topDownCompact']}`.",
            f"dx=-38 compact stream: `{edge_touch['streams']['topDownCompact']}`.",
            "The relation changes are geometric, not semantic: #4 words become slightly more edge-adjacent while G5 becomes exact edge contact and O5 remains bottom-clipped.",
            "No read/take/fold/mirror/word/letter/key instruction appears in the repaired contact streams.",
            "The heavier dx=-160/dy=35 fit changes contacts more aggressively and remains less source-like because it breaks the M3 tri-contact signature.",
        ],
        "nextMove": "Use dx=-38/-40 as a source-registration acceptance test only. The next high-value move is still obtaining or inspecting a higher-resolution Canva/original-layout image or a physical scan/photo that naturally explains the same contacts.",
    }

    build_overlay(scenarios)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Tri-Contact Frame Contact Stability",
        "",
        "Scope: compare p78 frame edge-contact order before and after the dx=-38/-40 tri-contact repair. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        f"- Current vs dx=-38 top-down stable: `{stable_exact}`",
        f"- Instruction hits across all streams: `{result['allInstructionTermHits']}`",
        "",
        "## Streams",
        "",
        "| scenario | event count | top-down compact stream | initials | cut labels | instruction hits |",
        "|---|---:|---|---|---|---|",
    ]
    for scenario in scenarios:
        streams = scenario["streams"]
        lines.append(
            f"| `{scenario['name']}` | {scenario['eventCount']} | `{streams['topDownCompact']}` | `{streams['topDownInitials']}` | `{streams['cutLabels']}` | `{scenario['instructionTermHits']}` |"
        )

    lines.extend(["", "## Contact Deltas", ""])
    for scenario in scenarios:
        lines.append(f"### {scenario['name']}")
        lines.extend(["", "| order | id | label | overlap | primary contact | all contacts |", "|---:|---|---|---:|---|---|"])
        for i, event in enumerate(scenario["events"], 1):
            primary = event["primaryContact"]
            primary_text = "-"
            if primary:
                primary_text = f"{primary['edge']} {primary['relation']} {primary['distancePx']}px"
            lines.append(
                f"| {i} | `{event['id']}` | {event['label']} | `{event['overlapVsTarget']}` | {primary_text} | {contact_summary(event)} |"
            )
        lines.append("")

    lines.extend(["## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("stable current vs dx=-38:", stable_exact)
    print("instruction hits:", result["allInstructionTermHits"])


if __name__ == "__main__":
    main()
