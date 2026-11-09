#!/usr/bin/env python3
"""Test whether p78 graphic edges reconcile the #4 band with the #5 pair.

Previous p78 graphic tests used the filled reflected graphic/mask and found a
broad lower-corridor band. This pass asks a different, narrower question:
do the *edges* of the reflected p78 graphic box point at the trusted G5/O5
pair (`Volcano Bonds` / `shitcoiner at heart`)?

No key candidates, hashes, seeds, or address checks are generated.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
P78_WORDS_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_graphic_edge_reconciliation.json"
OUT_MD = OUT / "p78_graphic_edge_reconciliation.md"
OUT_OVERLAY = OUT / "p78_graphic_edge_reconciliation_overlay.jpg"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersect(a: list[float], b: list[float]) -> list[float] | None:
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    if box[2] <= box[0] or box[3] <= box[1]:
        return None
    return box


def overlap_len(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


def point_box_distance(point: tuple[float, float], box: list[float]) -> float:
    x, y = point
    dx = max(box[0] - x, 0, x - box[2])
    dy = max(box[1] - y, 0, y - box[3])
    return math.hypot(dx, dy)


def edge_relation(edge: str, pbox: list[float], cbox: list[float]) -> dict:
    if edge == "left":
        x = pbox[0]
        along = overlap_len(pbox[1], pbox[3], cbox[1], cbox[3])
        if cbox[0] <= x <= cbox[2]:
            perp = 0.0
            relation = "cuts"
        elif cbox[2] < x:
            perp = x - cbox[2]
            relation = "right-adjacent"
        else:
            perp = cbox[0] - x
            relation = "left-adjacent"
    elif edge == "right":
        x = pbox[2]
        along = overlap_len(pbox[1], pbox[3], cbox[1], cbox[3])
        if cbox[0] <= x <= cbox[2]:
            perp = 0.0
            relation = "cuts"
        elif cbox[2] < x:
            perp = x - cbox[2]
            relation = "right-adjacent"
        else:
            perp = cbox[0] - x
            relation = "left-adjacent"
    elif edge == "top":
        y = pbox[1]
        along = overlap_len(pbox[0], pbox[2], cbox[0], cbox[2])
        if cbox[1] <= y <= cbox[3]:
            perp = 0.0
            relation = "cuts"
        elif cbox[3] < y:
            perp = y - cbox[3]
            relation = "below-adjacent"
        else:
            perp = cbox[1] - y
            relation = "above-adjacent"
    else:
        y = pbox[3]
        along = overlap_len(pbox[0], pbox[2], cbox[0], cbox[2])
        if cbox[1] <= y <= cbox[3]:
            perp = 0.0
            relation = "cuts"
        elif cbox[3] < y:
            perp = y - cbox[3]
            relation = "below-adjacent"
        else:
            perp = cbox[1] - y
            relation = "above-adjacent"
    return {
        "edge": edge,
        "relation": relation,
        "perpendicularDistancePx": round(perp, 2),
        "alongOverlapPx": round(along, 2),
        "isEdgeContact": along > 0 and perp <= 50,
    }


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def find_word_sequence(page: dict, tokens: list[str]) -> list[dict]:
    words = page["words"]
    toks = [norm(w.get("token") or w.get("text") or "") for w in words]
    for i in range(0, len(toks) - len(tokens) + 1):
        if toks[i : i + len(tokens)] == tokens:
            return words[i : i + len(tokens)]
    return []


def union_box(words: list[dict]) -> list[float] | None:
    if not words:
        return None
    return [
        min(w["box"][0] for w in words),
        min(w["box"][1] for w in words),
        max(w["box"][2] for w in words),
        max(w["box"][3] for w in words),
    ]


def lower_trusted_boxes() -> dict[str, list[float]]:
    data = json.loads(LOWER_MARKS_JSON.read_text())
    out = {}
    for item in data["analyses"]:
        note = item.get("note", "")
        if "$1 billion" in note:
            out["$1 billion"] = item["box"]
        elif "Volcano Bonds" in note:
            out["Volcano Bonds"] = item["box"]
    return out


def main() -> None:
    p78 = json.loads(P78_WORDS_JSON.read_text())
    pbox = p78["reflectedBoxOnP76"]
    page = load_page76()
    trusted = lower_trusted_boxes()

    orange = {h["id"]: h["box"] for h in page["highlights"]}
    candidates = [
        {"id": "O4", "label": "buying the dip", "kind": "orange", "box": orange["p76_orange_4"]},
        {"id": "B4_text", "label": "$1 billion", "kind": "trusted-grey", "box": trusted["$1 billion"]},
        {"id": "should_sell", "label": "should sell", "kind": "word-sequence", "box": union_box(find_word_sequence(page, ["should", "sell"]))},
        {"id": "earnings", "label": "earnings", "kind": "word", "box": union_box(find_word_sequence(page, ["earnings"]))},
        {"id": "G5", "label": "Volcano Bonds", "kind": "trusted-grey", "box": trusted["Volcano Bonds"]},
        {"id": "pay_imf", "label": "pay off the IMF", "kind": "word-sequence", "box": union_box(find_word_sequence(page, ["pay", "off", "the", "imf"]))},
        {"id": "tagged_mike", "label": "I tagged Mike", "kind": "word-sequence", "box": union_box(find_word_sequence(page, ["i", "tagged", "mike"]))},
        {"id": "could_sell", "label": "could sell", "kind": "word-sequence", "box": union_box(find_word_sequence(page, ["could", "sella"]))},
        {"id": "trust_guy", "label": "trust that guy", "kind": "word-sequence", "box": union_box(find_word_sequence(page, ["trust", "that", "guy"]))},
        {"id": "O5", "label": "shitcoiner at heart", "kind": "orange", "box": orange["p76_orange_5"]},
    ]
    candidates = [c for c in candidates if c["box"]]

    corners = {
        "topLeft": (pbox[0], pbox[1]),
        "topRight": (pbox[2], pbox[1]),
        "bottomLeft": (pbox[0], pbox[3]),
        "bottomRight": (pbox[2], pbox[3]),
    }

    records = []
    for candidate in candidates:
        cbox = candidate["box"]
        inter = intersect(pbox, cbox)
        edge_contacts = [edge_relation(edge, pbox, cbox) for edge in ("left", "right", "top", "bottom")]
        edge_contacts = [r for r in edge_contacts if r["isEdgeContact"]]
        corner_distances = {
            name: round(point_box_distance(point, cbox), 2)
            for name, point in corners.items()
        }
        records.append(
            {
                **candidate,
                "box": [round(v, 2) for v in cbox],
                "intersection": [round(v, 2) for v in inter] if inter else None,
                "overlapFracOfCandidate": round(area(inter) / area(cbox), 4) if inter else 0.0,
                "overlapFracOfP78Box": round(area(inter) / area(pbox), 4) if inter else 0.0,
                "edgeContacts": edge_contacts,
                "cornerDistancesPx": corner_distances,
                "nearestCorner": min(corner_distances.items(), key=lambda kv: kv[1]),
            }
        )

    edge_contact_records = [r for r in records if r["edgeContacts"]]
    edge_contact_records.sort(key=lambda r: (min(c["perpendicularDistancePx"] for c in r["edgeContacts"]), -max(c["alongOverlapPx"] for c in r["edgeContacts"]), r["id"]))

    # Nearest words to the four p78 box corners are useful for human inspection.
    corner_words = {}
    for name, point in corners.items():
        nearest = sorted(
            page["words"],
            key=lambda w: point_box_distance(point, w["box"]),
        )[:8]
        corner_words[name] = [
            {
                "text": w["text"],
                "token": norm(w.get("token") or w.get("text") or ""),
                "distancePx": round(point_box_distance(point, w["box"]), 2),
                "box": [round(v, 2) for v in w["box"]],
            }
            for w in nearest
        ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "P78 reflected graphic edge/corner test against trusted lower-corridor boxes; no key derivation.",
        "reflectedP78BoxOnP76": pbox,
        "records": records,
        "edgeContactRecords": edge_contact_records,
        "cornerNearestWords": corner_words,
        "keyFindings": {
            "leftEdgeToVolcanoBondsGapPx": next(
                c["perpendicularDistancePx"]
                for r in records
                if r["id"] == "G5"
                for c in r["edgeContacts"]
                if c["edge"] == "left"
            ),
            "bottomEdgeCutsO5": any(c["edge"] == "bottom" and c["relation"] == "cuts" for r in records if r["id"] == "O5" for c in r["edgeContacts"]),
            "bottomLeftCornerDistanceToO5Px": next(r["cornerDistancesPx"]["bottomLeft"] for r in records if r["id"] == "O5"),
        },
        "assessment": [
            "The filled p78 graphic remains broad, but the reflected p78 box edges do reconcile it with the #5 pair.",
            "The left edge runs immediately to the right of trusted G5 `Volcano Bonds` with a 38px gap and vertical overlap.",
            "The bottom edge cuts O5 `shitcoiner at heart`; the bottom-left corner lies inside O5.",
            "The top edge also cuts the #4 source row around `should sell`, explaining why the filled graphic selected #4 band words.",
            "This upgrades p78 graphic support for G5/O5 from broad corridor evidence to edge/framing evidence, but it still does not specify a final extraction unit.",
        ],
        "nextMove": "Treat the p78 graphic as a frame: top edge starts in the #4 source band, left/bottom edges frame G5/O5. Next test should inspect edge order/corners only, not the filled mask.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    image = Image.open(PAGE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
        small = ImageFont.truetype("Arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    draw.rectangle(pbox, outline=(30, 110, 240, 240), width=7, fill=(30, 110, 240, 20))
    draw.text((pbox[0], pbox[1] - 30), "reflected p78 graphic box", fill=(30, 110, 240, 240), font=font)
    for name, point in corners.items():
        x, y = point
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(30, 110, 240, 240))
        draw.text((x + 12, y - 8), name, fill=(30, 110, 240, 240), font=small)

    palette = {
        "O4": (255, 128, 0, 230),
        "B4_text": (80, 80, 80, 230),
        "should_sell": (180, 100, 30, 230),
        "earnings": (40, 150, 80, 230),
        "G5": (0, 0, 0, 230),
        "pay_imf": (230, 120, 0, 230),
        "tagged_mike": (160, 60, 180, 230),
        "could_sell": (40, 150, 80, 230),
        "trust_guy": (0, 0, 0, 230),
        "O5": (255, 128, 0, 240),
    }
    for rec in records:
        color = palette.get(rec["id"], (100, 100, 100, 220))
        box = rec["box"]
        draw.rectangle(box, outline=color, width=4, fill=(color[0], color[1], color[2], 24))
        draw.text((box[0], max(0, box[1] - 22)), rec["label"], fill=color, font=small)

    crop = image.crop((300, 2300, 2300, 3065))
    crop.save(OUT_OVERLAY, quality=92)

    md = [
        "# P78 Graphic Edge Reconciliation",
        "",
        "Scope: test whether the reflected p78 graphic edges/corners reconcile the broad #4 band with the #5 G5/O5 pair. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Reflected p78 box on p76: `{pbox}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        "",
        "## Edge Contacts",
        "",
        "| candidate | overlap | edge contacts | nearest corner |",
        "|---|---:|---|---|",
    ]
    for rec in edge_contact_records:
        contacts = "; ".join(
            f"{c['edge']} {c['relation']} dist={c['perpendicularDistancePx']}px overlap={c['alongOverlapPx']}px"
            for c in rec["edgeContacts"]
        )
        corner = rec["nearestCorner"]
        md.append(
            f"| `{rec['label']}` | {rec['overlapFracOfCandidate']} | {contacts} | `{corner[0]}` {corner[1]}px |"
        )

    md.extend(["", "## Corner Nearest Words", ""])
    for name, words in corner_words.items():
        md.append(f"- `{name}`: " + ", ".join(f"`{w['text']}`({w['distancePx']}px)" for w in words[:5]))

    md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        md.append(f"- {item}")
    md.extend(["", f"Next move: {result['nextMove']}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)
    print(OUT_OVERLAY)


if __name__ == "__main__":
    main()
