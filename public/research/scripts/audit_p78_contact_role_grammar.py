#!/usr/bin/env python3
"""Audit whether the p78 frame contacts form a small human-readable grammar."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "p78_contact_role_grammar"

TRICONTACT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_edge_adjacent_units/p78_frame_edge_adjacent_units.json"
G5_O5_JSON = ROOT / "analysis_outputs/source_audit/g5_o5_local_unit_rules/g5_o5_local_unit_rules.json"
M3_M4_JSON = ROOT / "analysis_outputs/source_audit/m3_m4_obbo_order/m3_m4_obbo_order.json"
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

INSTRUCTION_TERMS = {
    "read",
    "take",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "top",
    "bottom",
    "inside",
    "outside",
    "word",
    "letter",
    "line",
    "key",
    "private",
    "seed",
    "wif",
    "address",
    "index",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def center(box: list[float]) -> tuple[float, float]:
    x0, y0, x1, y1 = box
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def initials(text: str) -> str:
    return "".join(word[0] for word in re.findall(r"[A-Za-z0-9]+", text))


def edge_letters(items: list[dict[str, str]]) -> str:
    return "".join(item["edge"] for item in items)


def phrase_stream(items: list[dict[str, str]]) -> str:
    return " | ".join(item["label"] for item in items)


def instruction_hits(text: str) -> list[str]:
    words = set(re.findall(r"[a-z]+", text.lower()))
    return sorted(words & INSTRUCTION_TERMS)


def find_frame_audit(edge_data: dict[str, Any], name: str) -> dict[str, Any]:
    for audit in edge_data["frameAudits"]:
        if audit["name"] == name:
            return audit
    raise KeyError(name)


def draw_overlay(page_path: Path, frame: list[float], contacts: list[dict[str, Any]]) -> str:
    image = Image.open(page_path).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 28)
        small = ImageFont.truetype("Arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    fx0, fy0, fx1, fy1 = frame
    draw.rectangle(frame, outline=(255, 40, 40, 255), width=8)
    draw.text((fx0 + 12, fy0 + 12), "p78 frame dx=-38", fill=(255, 40, 40, 255), font=font)

    colors = {
        "black_text": (20, 20, 20, 190),
        "orange_text": (255, 128, 0, 190),
        "visual_mark": (120, 70, 255, 190),
        "text": (70, 180, 255, 160),
    }
    outlines = {
        "black_text": (20, 20, 20, 255),
        "orange_text": (255, 128, 0, 255),
        "visual_mark": (120, 70, 255, 255),
        "text": (70, 180, 255, 255),
    }
    for contact in contacts:
        box = contact.get("box")
        if not box:
            continue
        kind = contact["kind"]
        fill = colors.get(kind, (255, 255, 0, 140))
        outline = outlines.get(kind, (255, 255, 0, 255))
        draw.rectangle(box, fill=fill, outline=outline, width=5)
        x, y = center(box)
        label = f"{contact['edge']}: {contact['id']} {contact['label']}"
        draw.text((x + 8, y - 16), label, fill=outline, font=small)

    overlay_path = OUT_DIR / "p78_contact_role_grammar_overlay.jpg"
    image.save(overlay_path, quality=92)
    return str(overlay_path.relative_to(ROOT))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tri = load_json(TRICONTACT_JSON)
    edge = load_json(EDGE_JSON)
    g5o5 = load_json(G5_O5_JSON)
    m3m4 = load_json(M3_M4_JSON)

    tri_record = next(r for r in tri["records"] if r["name"] == "g5_edge_touch")
    edge_audit = find_frame_audit(edge, "dx_-38_edge_touch")
    streams = edge_audit["streams"]

    contacts = [
        {
            "edge": "T",
            "id": "T-cut",
            "label": streams["top_cut_inside"],
            "kind": "text",
            "role": "top edge text cut",
            "box": [tri_record["frame"][0], tri_record["frame"][1], tri_record["frame"][0] + 220, tri_record["frame"][1] + 55],
            "evidence": "edge-adjacent audit top_cut_inside",
        },
        {
            "edge": "L",
            "id": tri["targets"]["G5"]["id"],
            "label": tri["targets"]["G5"]["label"],
            "kind": "black_text",
            "role": "left edge touches G5 after dx=-38 repair",
            "box": tri["targets"]["G5"]["box"],
            "evidence": f"left edge gap {tri_record['leftEdgeToG5RightPx']} px, vertical overlap {tri_record['leftEdgeG5VerticalOverlapPx']} px",
        },
        {
            "edge": "R",
            "id": "M3",
            "label": "standalone mark",
            "kind": "visual_mark",
            "role": "right edge cuts M3 and M3 axis remains in the mark",
            "box": tri["m3"]["box"],
            "evidence": f"right-edge M3 overlap {tri_record['rightEdgeM3VerticalOverlapPx']} px, axis in mark {tri_record['m3AxisRightInsideM3']}",
        },
        {
            "edge": "B",
            "id": tri["targets"]["O5"]["id"],
            "label": tri["targets"]["O5"]["label"],
            "kind": "orange_text",
            "role": "bottom edge clips O5",
            "box": tri["targets"]["O5"]["box"],
            "evidence": f"bottom O5 width {tri_record['bottomEdgeO5HorizontalOverlapPx']} px, O5 overlap {tri_record['o5OverlapVsTarget']}",
        },
    ]

    by_edge = {c["edge"]: c for c in contacts}
    orderings = {
        "clockwise_top_start": [by_edge[e] for e in "TRBL"],
        "counterclockwise_top_start": [by_edge[e] for e in "TLBR"],
        "tri_contact_edges_left_right_bottom": [by_edge[e] for e in "LRB"],
        "tri_contact_clockwise_left_start": [by_edge[e] for e in "LRB"],
        "tri_contact_counterclockwise_left_start": [by_edge[e] for e in "LBR"],
        "text_contacts_only": [by_edge[e] for e in "LB"],
        "color_or_medium_black_mark_orange": [by_edge[e] for e in "LRB"],
        "top_then_text_contacts": [by_edge[e] for e in "TLB"],
        "bottom_then_left_then_right": [by_edge[e] for e in "BLR"],
    }

    stream_records = []
    for name, items in orderings.items():
        labels = phrase_stream(items)
        ids = " | ".join(item["id"] for item in items)
        rec = {
            "name": name,
            "edgeCode": edge_letters(items),
            "ids": ids,
            "labels": labels,
            "initials": " ".join(initials(item["label"]) for item in items),
            "instructionHits": instruction_hits(labels),
        }
        stream_records.append(rec)

    structural = {
        "chosenFrame": tri_record["name"],
        "chosenFrameBox": tri_record["frame"],
        "triContactPass": tri_record["triContactPass"],
        "g5O5LineGap": g5o5["structural"]["lineGapO5MinusG5"],
        "g5LinePlus5MatchesO5": g5o5["structural"]["g5LinePlus5MatchesO5Line"],
        "m3M4WedgeSelectedAnchors": [
            r["label"] for r in m3m4["anchorRecords"] if r.get("insideM3M4Wedge")
        ],
    }

    overlay = draw_overlay(PAGE76_IMAGE, tri_record["frame"], contacts)

    assessment = [
        "The dx=-38 p78 frame has a stable three-object contact grammar: left touches G5, right cuts M3, and bottom clips O5.",
        "Adding the top edge gives ordinary nearby article text ('should sell'), not an instruction.",
        "Clockwise, counterclockwise, edge-role, medium/color, and text-only readings produce labels/initials only; no instruction-like terms appear in the content streams.",
        "The grammar reconfirms registration and the G5/O5 five-line structure, but it still does not name a word, letter, line, direction, or key unit.",
        "This closes p78 contact-role ordering as a standalone selector under the current scan.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bounded p78 frame contact-role grammar audit; no key derivation",
        "sources": {
            "triContact": str(TRICONTACT_JSON.relative_to(ROOT)),
            "edgeAdjacent": str(EDGE_JSON.relative_to(ROOT)),
            "g5O5": str(G5_O5_JSON.relative_to(ROOT)),
            "m3M4": str(M3_M4_JSON.relative_to(ROOT)),
        },
        "overlay": overlay,
        "contacts": contacts,
        "structural": structural,
        "streams": stream_records,
        "instructionHits": {r["name"]: r["instructionHits"] for r in stream_records if r["instructionHits"]},
        "assessment": assessment,
        "decision": "Do not promote p78 contact-role grammar to extraction evidence; use it only as source-registration validation.",
        "nextMove": "Use the Typeka/font layer and comparison articles to ask whether the three fonts regular/mix/bold provide the missing extraction unit around the page-76 G5/O5 corridor.",
    }

    (OUT_DIR / "p78_contact_role_grammar.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# P78 Contact-Role Grammar",
        "",
        "Scope: test whether the repaired p78 frame contacts form a small human-readable extraction grammar. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{overlay}`",
        f"- Chosen frame: `{structural['chosenFrame']}` `{structural['chosenFrameBox']}`",
        f"- Tri-contact pass: `{structural['triContactPass']}`",
        f"- G5/O5 line gap: `{structural['g5O5LineGap']}`; G5 line + 5 equals O5 line: `{structural['g5LinePlus5MatchesO5']}`",
        f"- M3/M4 wedge selected anchors from prior audit: `{', '.join(structural['m3M4WedgeSelectedAnchors'])}`",
        "",
        "## Contacts",
        "",
        "| edge | id | label | kind | role | evidence |",
        "|---|---|---|---|---|---|",
    ]
    for c in contacts:
        lines.append(
            f"| `{c['edge']}` | `{c['id']}` | `{c['label']}` | `{c['kind']}` | {c['role']} | {c['evidence']} |"
        )

    lines.extend(
        [
            "",
            "## Read Orders",
            "",
            "| order | edges | ids | labels | initials | instruction hits |",
            "|---|---|---|---|---|---|",
        ]
    )
    for r in stream_records:
        lines.append(
            f"| `{r['name']}` | `{r['edgeCode']}` | `{r['ids']}` | `{r['labels']}` | `{r['initials']}` | `{', '.join(r['instructionHits'])}` |"
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
    (OUT_DIR / "p78_contact_role_grammar.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
