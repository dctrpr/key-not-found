#!/usr/bin/env python3
"""
Audit whether active page-76 highlight edges select adjacent text.

This is a bounded visual/geometry pass over the locked O4/B4/G5/O5 target
boxes. It does not derive private keys, hash text, generate seed phrases,
check WIF strings, or query addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "page76_highlight_edge_selector"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAP_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
OBBO_JSON = ROOT / "analysis_outputs" / "source_audit" / "obbo_highres_boundary_coincidences" / "obbo_highres_boundary_coincidences.json"
AUTHORITY_JSON = ROOT / "analysis_outputs" / "source_audit" / "active_text_authority_drift" / "active_text_authority_drift.json"
PAGE_IMG = ROOT / "analysis_outputs" / "3d_article_map" / "page_76_upright.jpg"

OUT_JSON = OUT_DIR / "page76_highlight_edge_selector.json"
OUT_MD = OUT_DIR / "page76_highlight_edge_selector.md"
OUT_OVERLAY = OUT_DIR / "page76_highlight_edge_selector_overlay.jpg"


INSTRUCTION_TERMS = [
    "read",
    "take",
    "fold",
    "mirror",
    "word",
    "letter",
    "line",
    "key",
    "left",
    "right",
    "first",
    "last",
    "above",
    "below",
    "edge",
]

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_ANCHORS = {
    "O4": "buying_dip",
    "B4": "one_billion",
    "G5": "volcano_bonds",
    "O5": "shitcoiner_heart",
}


def overlap_len(a1: float, a2: float, b1: float, b2: float) -> float:
    return max(0.0, min(a2, b2) - max(a1, b1))


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def clean_word(text: str | None) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def first_alpha(text: str) -> str:
    m = re.search(r"[A-Za-z0-9$]", text)
    return m.group(0) if m else ""


def last_alpha(text: str) -> str:
    m = re.findall(r"[A-Za-z0-9$]", text)
    return m[-1] if m else ""


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if term in low]


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def active_authority() -> dict[str, dict]:
    data = json.loads(AUTHORITY_JSON.read_text())
    return {item["label"]: item for item in data["targets"] if item.get("label") in set(TARGET_ORDER)}


def target_records() -> list[dict]:
    anchors = {item["id"]: item for item in json.loads(OBBO_JSON.read_text())["anchors"]}
    authority = active_authority()
    records = []
    for label in TARGET_ORDER:
        anchor = anchors[TARGET_ANCHORS[label]]
        phrase = authority[label]["phrase"]
        docm_state = authority[label].get("docmState", {})
        records.append(
            {
                "label": label,
                "anchorId": anchor["id"],
                "phrase": phrase,
                "visualLabel": anchor["label"],
                "color": "orange" if anchor["color"] == "orange" else "black",
                "box": [float(v) for v in anchor["box"]],
                "docmState": docm_state,
            }
        )
    return records


def word_candidates(page: dict) -> list[dict]:
    out = []
    for word in page["words"]:
        text = clean_word(word.get("text") or word.get("token"))
        token = clean_word(word.get("token") or text)
        if not text and not token:
            continue
        box = [float(v) for v in word["box"]]
        out.append(
            {
                "id": word.get("id"),
                "index": word.get("index"),
                "text": text,
                "token": token,
                "box": box,
                "center": center(box),
            }
        )
    return out


def nearest_side_word(words: list[dict], box: list[float], side: str) -> dict | None:
    bx1, by1, bx2, by2 = box
    bcx, bcy = center(box)
    scored = []
    for word in words:
        wx1, wy1, wx2, wy2 = word["box"]
        wcx, wcy = word["center"]
        v_overlap = overlap_len(by1, by2, wy1, wy2)
        h_overlap = overlap_len(bx1, bx2, wx1, wx2)
        if side == "left":
            if wx2 > bx1 or v_overlap <= 0:
                continue
            dist = bx1 - wx2
            score = (dist, abs(wcy - bcy), abs(wcx - bcx))
            relation = "same-row-left"
        elif side == "right":
            if wx1 < bx2 or v_overlap <= 0:
                continue
            dist = wx1 - bx2
            score = (dist, abs(wcy - bcy), abs(wcx - bcx))
            relation = "same-row-right"
        elif side == "above":
            if wy2 > by1:
                continue
            dist = by1 - wy2
            # Prefer true horizontal overlap, but allow a nearest-word fallback
            # so blank edge results are explicit instead of silent.
            overlap_penalty = 0 if h_overlap > 0 else abs(wcx - bcx)
            score = (dist, overlap_penalty, abs(wcx - bcx))
            relation = "vertical-overlap-above" if h_overlap > 0 else "nearest-above"
        else:
            if wy1 < by2:
                continue
            dist = wy1 - by2
            overlap_penalty = 0 if h_overlap > 0 else abs(wcx - bcx)
            score = (dist, overlap_penalty, abs(wcx - bcx))
            relation = "vertical-overlap-below" if h_overlap > 0 else "nearest-below"
        scored.append((score, {**word, "distancePx": round(score[0], 2), "relation": relation}))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0])
    return scored[0][1]


def crossing_chars(page: dict, box: list[float], side: str) -> dict[str, object]:
    bx1, by1, bx2, by2 = box
    hits = []
    for char in page["chars"]:
        c = char.get("c", "")
        if not c or not str(c).strip():
            continue
        cx1, cy1, cx2, cy2 = [float(v) for v in char["box"]]
        ccx, ccy = center([cx1, cy1, cx2, cy2])
        if side == "left":
            ok = cx1 <= bx1 <= cx2 and overlap_len(by1, by2, cy1, cy2) > 1
            order = (ccy, ccx)
        elif side == "right":
            ok = cx1 <= bx2 <= cx2 and overlap_len(by1, by2, cy1, cy2) > 1
            order = (ccy, ccx)
        elif side == "top":
            ok = cy1 <= by1 <= cy2 and overlap_len(bx1, bx2, cx1, cx2) > 1
            order = (ccx, ccy)
        else:
            ok = cy1 <= by2 <= cy2 and overlap_len(bx1, bx2, cx1, cx2) > 1
            order = (ccx, ccy)
        if ok:
            hits.append((order, {"c": c, "i": char.get("i"), "box": [round(cx1, 2), round(cy1, 2), round(cx2, 2), round(cy2, 2)]}))
    hits.sort(key=lambda item: item[0])
    chars = "".join(item[1]["c"] for item in hits)
    return {
        "count": len(hits),
        "chars": chars[:120],
        "truncated": len(chars) > 120,
        "items": [item[1] for item in hits[:40]],
    }


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], fill: tuple[int, int, int, int]) -> None:
    draw.line([start, end], fill=fill, width=3)
    ex, ey = end
    sx, sy = start
    dx = ex - sx
    dy = ey - sy
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    p1 = (ex - ux * 12 + px * 6, ey - uy * 12 + py * 6)
    p2 = (ex - ux * 12 - px * 6, ey - uy * 12 - py * 6)
    draw.polygon([end, p1, p2], fill=fill)


def main() -> None:
    page = load_page76()
    words = word_candidates(page)
    records = target_records()

    for record in records:
        box = record["box"]
        phrase = record["phrase"]
        literal = phrase.strip()
        record["literalEdgeChars"] = {
            "first": literal[0] if literal else "",
            "last": literal[-1] if literal else "",
            "firstAlpha": first_alpha(literal),
            "lastAlpha": last_alpha(literal),
        }
        record["nearestWords"] = {
            side: nearest_side_word(words, box, side)
            for side in ["left", "right", "above", "below"]
        }
        record["edgeCrossingChars"] = {
            side: crossing_chars(page, box, side)
            for side in ["left", "right", "top", "bottom"]
        }

    streams = {
        "targetFirstLiteral": "".join(row["literalEdgeChars"]["first"] for row in records),
        "targetLastLiteral": "".join(row["literalEdgeChars"]["last"] for row in records),
        "targetFirstAlpha": "".join(row["literalEdgeChars"]["firstAlpha"] for row in records),
        "targetLastAlpha": "".join(row["literalEdgeChars"]["lastAlpha"] for row in records),
    }
    for side in ["left", "right", "above", "below"]:
        side_words = [row["nearestWords"][side]["text"] if row["nearestWords"][side] else "" for row in records]
        streams[f"{side}Words"] = " | ".join(word or "-" for word in side_words)
        streams[f"{side}Initials"] = "".join(first_alpha(word) or "-" for word in side_words)
        streams[f"{side}Lasts"] = "".join(last_alpha(word) or "-" for word in side_words)

    stream_hits = {name: instruction_hits(value) for name, value in streams.items()}

    assessment = [
        "The four active target boxes do not expose a consistent adjacent-edge selector: left/right sides are absent for some targets, and above/below words are ordinary neighboring prose.",
        "Literal target edges produce only the known phrase-edge streams, not instructions: first/significant `b$Vs`, last/significant `pnst`.",
        "Adjacent side streams also fail as instructions; they mostly restate local prose around El Salvador/Bukele/Volcano Bonds/O5.",
        "Edge-crossing characters are not one-letter selectors. Top/bottom crossings generally traverse whole highlighted text rows, while left/right often hit zero or arbitrary OCR character edges.",
        "This keeps the active highlights as target locators and source-comparison evidence, not a complete word/letter edge rule.",
    ]
    decision = (
        "Do not use active highlight boundaries alone as selectors. Reopen this only if a new clue specifies a side such as left/right/top/bottom, or a physical/original-layout source changes the edge contacts."
    )
    next_move = (
        "Shift back to external/source instructions: find a rule naming the unit/order, or compare a new physical/original-layout scan against these locked edge-adjacency baselines."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 active highlight edge selector audit; no key derivation.",
        "sources": {
            "pageMap": str(MAP_JSON.relative_to(ROOT)),
            "activeAnchors": str(OBBO_JSON.relative_to(ROOT)),
            "textAuthority": str(AUTHORITY_JSON.relative_to(ROOT)),
        },
        "records": records,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    img = Image.open(PAGE_IMG).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    font = ImageFont.load_default()
    target_colors = {
        "orange": (255, 145, 35, 105),
        "black": (20, 24, 32, 190),
    }
    outline_colors = {
        "orange": (255, 200, 85, 255),
        "black": (125, 220, 255, 255),
    }
    side_colors = {
        "left": (255, 255, 255, 230),
        "right": (255, 255, 255, 230),
        "above": (85, 210, 255, 230),
        "below": (255, 100, 190, 230),
    }
    for record in records:
        box = record["box"]
        color = target_colors[record["color"]]
        outline = outline_colors[record["color"]]
        draw.rectangle(box, fill=color, outline=outline, width=5)
        draw.text((box[0], max(0, box[1] - 18)), f"{record['label']} {record['phrase']}", fill=(255, 255, 255, 255), font=font)
        bcx, bcy = center(box)
        for side, word in record["nearestWords"].items():
            if not word:
                continue
            wx1, wy1, wx2, wy2 = word["box"]
            wcx, wcy = word["center"]
            draw.rectangle(word["box"], outline=side_colors[side], width=3)
            label = f"{side}: {word['text']}"
            tx = min(max(wx1, 0), img.width - 140)
            ty = max(0, wy1 - 14)
            draw.text((tx, ty), label, fill=side_colors[side], font=font)
            draw_arrow(draw, (bcx, bcy), (wcx, wcy), side_colors[side])

    min_x = max(0, int(min(row["box"][0] for row in records) - 260))
    min_y = max(0, int(min(row["box"][1] for row in records) - 260))
    max_x = min(img.width, int(max(row["box"][2] for row in records) + 300))
    max_y = min(img.height, int(max(row["box"][3] for row in records) + 300))
    img.crop((min_x, min_y, max_x, max_y)).save(OUT_OVERLAY, quality=92)

    md = [
        "# Page 76 Highlight Edge Selector Audit",
        "",
        "Scope: test whether the active O4/B4/G5/O5 highlight boxes select adjacent text at their left/right/top/bottom edges. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY.relative_to(ROOT)}`",
        "",
        "## Edge Neighbors",
        "",
        "| target | phrase | left | right | above | below | first/last significant |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in records:
        nw = record["nearestWords"]
        def show(side: str) -> str:
            item = nw[side]
            return "-" if not item else f"{item['text']} ({item['relation']}, {item['distancePx']} px)"
        phrase = record["phrase"].replace("|", "\\|")
        edge = record["literalEdgeChars"]
        md.append(
            f"| `{record['label']}` | {phrase} | {show('left')} | {show('right')} | {show('above')} | {show('below')} | "
            f"`{edge['firstAlpha']}/{edge['lastAlpha']}` |"
        )

    md.extend(["", "## Streams Checked", "", "| stream | value | instruction hits |", "|---|---|---|"])
    for name, value in streams.items():
        hits = ", ".join(stream_hits[name]) or "-"
        safe_value = value.replace("|", "\\|")
        md.append(f"| `{name}` | `{safe_value}` | {hits} |")

    md.extend(["", "## Edge Crossing Character Counts", "", "| target | left | right | top | bottom |", "|---|---:|---:|---:|---:|"])
    for record in records:
        counts = {side: record["edgeCrossingChars"][side]["count"] for side in ["left", "right", "top", "bottom"]}
        md.append(f"| `{record['label']}` | {counts['left']} | {counts['right']} | {counts['top']} | {counts['bottom']} |")

    md.extend(["", "## Findings", ""])
    for item in assessment:
        md.append(f"- {item}")
    md.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}"])
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)
    print(OUT_OVERLAY)


if __name__ == "__main__":
    main()
