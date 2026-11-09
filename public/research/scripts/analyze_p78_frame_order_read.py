#!/usr/bin/env python3
"""Read the reflected p78 graphic frame in simple edge/corner orders.

This follows the edge reconciliation audit. It does not use the filled p78
mask. It reads only frame contacts: top edge, left edge, bottom edge, and
nearest corners. No key candidates, hashes, seeds, or address checks are made.
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
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/p78_frame_order_read"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_order_read.json"
OUT_MD = OUT / "p78_frame_order_read.md"
OUT_OVERLAY = OUT / "p78_frame_order_read_overlay.jpg"


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
    return re.sub(r"[^a-z0-9]", "", text.lower())


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def overlap_len(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


def point_box_distance(point: tuple[float, float], box: list[float]) -> float:
    x, y = point
    dx = max(box[0] - x, 0, x - box[2])
    dy = max(box[1] - y, 0, y - box[3])
    return math.hypot(dx, dy)


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


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


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


def build_candidates(page: dict) -> list[dict]:
    trusted = lower_trusted_boxes()
    orange = {h["id"]: h["box"] for h in page["highlights"]}
    specs = [
        ("should_sell", "should sell", "top-edge article phrase", union_box(find_word_sequence(page, ["should", "sell"]))),
        ("earnings", "earnings", "left-edge word", union_box(find_word_sequence(page, ["earnings"]))),
        ("G5", "Volcano Bonds", "trusted #5 grey pair", trusted.get("Volcano Bonds")),
        ("pay_imf", "pay off the IMF", "left-edge phrase", union_box(find_word_sequence(page, ["pay", "off", "the", "imf"]))),
        ("tagged_mike", "I tagged Mike", "left-edge phrase", union_box(find_word_sequence(page, ["i", "tagged", "mike"]))),
        ("could_sell", "could sell", "left-edge phrase", union_box(find_word_sequence(page, ["could", "sella"]))),
        ("trust_guy", "trust that guy", "left-edge phrase", union_box(find_word_sequence(page, ["trust", "that", "guy"]))),
        ("O5", "shitcoiner at heart", "bottom-edge #5 orange pair", orange.get("p76_orange_5")),
    ]
    return [{"id": sid, "label": label, "role": role, "box": box} for sid, label, role, box in specs if box]


def edge_events(pbox: list[float], candidates: list[dict]) -> dict[str, list[dict]]:
    left_x, top_y, right_x, bottom_y = pbox
    out = {"top": [], "left": [], "bottom": [], "right": []}
    for cand in candidates:
        box = cand["box"]
        cx, cy = center(box)
        top_overlap = overlap_len(left_x, right_x, box[0], box[2])
        left_overlap = overlap_len(top_y, bottom_y, box[1], box[3])
        bottom_overlap = top_overlap
        right_overlap = left_overlap

        if box[1] <= top_y <= box[3] and top_overlap > 0:
            out["top"].append({**cand, "axisPosition": cx, "distancePx": 0.0, "overlapPx": round(top_overlap, 2), "relation": "cuts"})
        if box[0] <= left_x <= box[2] and left_overlap > 0:
            out["left"].append({**cand, "axisPosition": cy, "distancePx": 0.0, "overlapPx": round(left_overlap, 2), "relation": "cuts"})
        elif left_overlap > 0 and abs(box[0] - left_x) <= 55:
            out["left"].append({**cand, "axisPosition": cy, "distancePx": round(abs(box[0] - left_x), 2), "overlapPx": round(left_overlap, 2), "relation": "left-adjacent"})
        elif left_overlap > 0 and abs(box[2] - left_x) <= 55:
            out["left"].append({**cand, "axisPosition": cy, "distancePx": round(abs(box[2] - left_x), 2), "overlapPx": round(left_overlap, 2), "relation": "right-adjacent"})
        if box[1] <= bottom_y <= box[3] and bottom_overlap > 0:
            out["bottom"].append({**cand, "axisPosition": cx, "distancePx": 0.0, "overlapPx": round(bottom_overlap, 2), "relation": "cuts"})
        if box[0] <= right_x <= box[2] and right_overlap > 0:
            out["right"].append({**cand, "axisPosition": cy, "distancePx": 0.0, "overlapPx": round(right_overlap, 2), "relation": "cuts"})
    out["top"].sort(key=lambda e: e["axisPosition"])
    out["left"].sort(key=lambda e: e["axisPosition"])
    out["bottom"].sort(key=lambda e: e["axisPosition"])
    out["right"].sort(key=lambda e: e["axisPosition"])
    return out


def dedupe_labels(labels: list[str]) -> list[str]:
    out = []
    for label in labels:
        if not out or out[-1] != label:
            out.append(label)
    return out


def stream_from(events: list[dict]) -> str:
    return " | ".join(dedupe_labels([event["label"] for event in events]))


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits = {}
    for name, value in streams.items():
        value_norm = value.lower()
        found = [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", value_norm)]
        if found:
            hits[name] = found
    return hits


def main() -> None:
    edge = json.loads(EDGE_JSON.read_text())
    pbox = edge["reflectedP78BoxOnP76"]
    page = load_page76()
    candidates = build_candidates(page)
    events = edge_events(pbox, candidates)

    top_lr = events["top"]
    left_tb = events["left"]
    left_bt = list(reversed(left_tb))
    bottom_lr = events["bottom"]
    bottom_rl = list(reversed(bottom_lr))

    corners = {
        "topLeft": (pbox[0], pbox[1]),
        "topRight": (pbox[2], pbox[1]),
        "bottomRight": (pbox[2], pbox[3]),
        "bottomLeft": (pbox[0], pbox[3]),
    }
    corner_events = {}
    for name, point in corners.items():
        nearest = sorted(
            candidates,
            key=lambda c: point_box_distance(point, c["box"]),
        )[:4]
        corner_events[name] = [
            {**cand, "distancePx": round(point_box_distance(point, cand["box"]), 2)}
            for cand in nearest
        ]

    l_shape = dedupe_labels([e["label"] for e in top_lr + left_tb + bottom_lr])
    l_shape_reverse = list(reversed(l_shape))
    minimal = [
        corner_events["topLeft"][0]["label"],
        "Volcano Bonds",
        corner_events["bottomLeft"][0]["label"],
    ]
    streams = {
        "topEdgeLeftToRight": stream_from(top_lr),
        "leftEdgeTopToBottom": stream_from(left_tb),
        "leftEdgeBottomToTop": stream_from(left_bt),
        "bottomEdgeLeftToRight": stream_from(bottom_lr),
        "bottomEdgeRightToLeft": stream_from(bottom_rl),
        "lShapeTopLeftDown": " | ".join(l_shape),
        "lShapeReverse": " | ".join(l_shape_reverse),
        "minimalCornerFrame": " | ".join(minimal),
        "minimalCornerFrameInitials": "".join(norm(label)[:1] for label in minimal if norm(label)),
        "leftEdgeInitialsTopDown": "".join(norm(e["label"])[:1] for e in left_tb if norm(e["label"])),
        "leftEdgeInitialsBottomUp": "".join(norm(e["label"])[:1] for e in left_bt if norm(e["label"])),
    }
    action_phrase = "should sell Volcano Bonds"
    minimal_action = (
        len(minimal) >= 2
        and minimal[0] == "should sell"
        and minimal[1] == "Volcano Bonds"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Read reflected p78 graphic frame edges/corners only; no filled-mask extraction and no key derivation.",
        "reflectedP78BoxOnP76": pbox,
        "edgeEvents": events,
        "cornerEvents": corner_events,
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
        "actionPhraseObservation": action_phrase if minimal_action else "",
        "assessment": [
            "Frame reading produces a coherent article phrase path, not a puzzle extraction instruction.",
            "The strongest minimal frame phrase is `should sell | Volcano Bonds | shitcoiner at heart`.",
            "`should sell Volcano Bonds` is semantically coherent in the article context, but it does not name an extraction unit such as word, letter, line, key, or mirror.",
            "The left-edge stream is `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`, again ordinary corridor prose.",
            "Close p78 frame-order streams as standalone selectors; keep p78 as a frame/registration clue for the G5/O5 target pair.",
        ],
        "nextMove": "Inspect whether the G5/O5 pair plus the phrase `should sell Volcano Bonds` points to a public/source instruction outside page 76, such as the original tweet/Canva clue or physical p78 graphic labels.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    image = Image.open(PAGE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
        small = ImageFont.truetype("Arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = font

    draw.rectangle(pbox, outline=(35, 90, 230, 240), width=7, fill=(35, 90, 230, 18))
    for edge_name, evs in events.items():
        for i, event in enumerate(evs, 1):
            box = event["box"]
            color = (255, 128, 0, 230) if event["id"] in {"O5", "G5"} else (40, 150, 80, 230)
            draw.rectangle(box, outline=color, width=4, fill=(color[0], color[1], color[2], 25))
            draw.text((box[0], max(0, box[1] - 22)), f"{edge_name}:{i} {event['label']}", fill=color, font=small)

    for name, point in corners.items():
        x, y = point
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(35, 90, 230, 240))
        nearest = corner_events[name][0]
        draw.text((x + 14, y - 10), f"{name}->{nearest['label']}", fill=(35, 90, 230, 240), font=small)

    crop = image.crop((300, 2300, 2300, 3065))
    crop.save(OUT_OVERLAY, quality=92)

    md = [
        "# P78 Frame Order Read",
        "",
        "Scope: read only the reflected p78 frame edges/corners. The filled mask is ignored. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Reflected p78 box on p76: `{pbox}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        "",
        "## Edge Streams",
        "",
    ]
    for key, value in streams.items():
        md.append(f"- `{key}`: `{value or '-'}`")
    md.append(f"- Instruction-term hits: `{result['instructionTermHits'] or {}}`")
    if result["actionPhraseObservation"]:
        md.append(f"- Action-phrase observation: `{result['actionPhraseObservation']}`")

    md.extend(["", "## Edge Events", "", "| edge | order | label | relation | distance | overlap |", "|---|---:|---|---|---:|---:|"])
    for edge_name in ("top", "left", "bottom", "right"):
        for i, event in enumerate(events[edge_name], 1):
            md.append(
                f"| `{edge_name}` | {i} | `{event['label']}` | `{event['relation']}` | {event['distancePx']} | {event['overlapPx']} |"
            )
    md.extend(["", "## Corners", "", "| corner | nearest labels |", "|---|---|"])
    for name, nearest in corner_events.items():
        labels = ", ".join(f"`{item['label']}` ({item['distancePx']}px)" for item in nearest)
        md.append(f"| `{name}` | {labels} |")

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
