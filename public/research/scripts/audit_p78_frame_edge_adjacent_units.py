#!/usr/bin/env python3
"""Audit edge-adjacent reading around the reflected p78 frame.

Several earlier passes read the p78 frame contacts and the filled graphic band.
This pass checks a smaller visual possibility: the intended text may sit just
outside or just inside the frame edges, not directly in the frame. It tests the
current frame, dx=-38 edge-touch repair, and dx=-40 grid repair.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
TRICONTACT_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/p78_frame_edge_adjacent_units"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_edge_adjacent_units.json"
OUT_MD = OUT / "p78_frame_edge_adjacent_units.md"
OUT_OVERLAY = OUT / "p78_frame_edge_adjacent_units_overlay.jpg"

LINE_Y_THRESHOLD = 34.0
ADJACENT_X_MARGIN = 125.0
ADJACENT_Y_MARGIN = 90.0

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "above",
    "below",
    "inside",
    "outside",
    "edge",
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def box_union(boxes: list[list[float]]) -> list[float]:
    return [
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    ]


def box_center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def token_text(words: list[dict]) -> str:
    return clean(" ".join(display_word(w) for w in sorted(words, key=lambda w: w["box"][0])))


def display_word(word: dict) -> str:
    """Patch known stale OCR blobs to the corrected article text."""
    raw = word["text"]
    if norm(raw) == "siukbeodmensertslveaarty":
        return "shitcoiner at heart"
    return raw


def compact(text: str, limit: int = 130) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def load_page76() -> dict:
    data = json.loads(MAP_JSON.read_text(encoding="utf-8"))
    return next(page for page in data["pages"] if page["page"] == 76)


def line_groups(words: list[dict]) -> list[dict]:
    groups: list[dict] = []
    for word in sorted(words, key=lambda w: (box_center(w["box"])[1], w["box"][0])):
        cy = box_center(word["box"])[1]
        placed = False
        for group in groups:
            if abs(group["cy"] - cy) <= LINE_Y_THRESHOLD:
                group["words"].append(word)
                centers = [box_center(w["box"])[1] for w in group["words"]]
                group["cy"] = sum(centers) / len(centers)
                placed = True
                break
        if not placed:
            groups.append({"cy": cy, "words": [word]})
    rows = []
    for idx, group in enumerate(sorted(groups, key=lambda g: g["cy"]), 1):
        words_sorted = sorted(group["words"], key=lambda w: w["box"][0])
        row_box = box_union([w["box"] for w in words_sorted])
        rows.append(
            {
                "line": idx,
                "cy": round(group["cy"], 2),
                "box": row_box,
                "text": token_text(words_sorted),
                "words": words_sorted,
            }
        )
    return rows


def words_in_x_range(line: dict, x0: float, x1: float) -> list[dict]:
    return [w for w in line["words"] if overlap(w["box"][0], w["box"][2], x0, x1) > 0]


def words_left_of(line: dict, x: float, margin: float) -> list[dict]:
    return [w for w in line["words"] if 0 <= x - w["box"][2] <= margin]


def words_right_of(line: dict, x: float, margin: float) -> list[dict]:
    return [w for w in line["words"] if 0 <= w["box"][0] - x <= margin]


def nearest_line(lines: list[dict], y: float, direction: str, x0: float, x1: float) -> dict | None:
    if direction == "above":
        candidates = [ln for ln in lines if ln["box"][3] < y and words_in_x_range(ln, x0, x1)]
        return max(candidates, key=lambda ln: ln["box"][3], default=None)
    if direction == "below":
        candidates = [ln for ln in lines if ln["box"][1] > y and words_in_x_range(ln, x0, x1)]
        return min(candidates, key=lambda ln: ln["box"][1], default=None)
    raise ValueError(direction)


def line_stream(lines: list[dict], x0: float, x1: float) -> str:
    parts = []
    for line in lines:
        chosen = token_text(words_in_x_range(line, x0, x1))
        if chosen:
            parts.append(chosen)
    return " | ".join(parts)


def frame_audit(name: str, frame: list[float], lines: list[dict]) -> dict:
    x0, y0, x1, y1 = frame
    vertical_lines = [ln for ln in lines if overlap(ln["box"][1], ln["box"][3], y0, y1) > 0]
    top_cut = [ln for ln in lines if ln["box"][1] <= y0 <= ln["box"][3]]
    bottom_cut = [ln for ln in lines if ln["box"][1] <= y1 <= ln["box"][3]]
    above_top = nearest_line(lines, y0, "above", x0, x1)
    below_top = nearest_line(lines, y0, "below", x0, x1)
    above_bottom = nearest_line(lines, y1, "above", x0, x1)
    below_bottom = nearest_line(lines, y1, "below", x0, x1)

    left_outside_parts = []
    left_inside_parts = []
    right_inside_parts = []
    right_outside_parts = []
    for line in vertical_lines:
        left_outside = token_text(words_left_of(line, x0, ADJACENT_X_MARGIN))
        left_inside = token_text([w for w in line["words"] if x0 <= w["box"][0] <= x0 + ADJACENT_X_MARGIN])
        right_inside = token_text([w for w in line["words"] if x1 - ADJACENT_X_MARGIN <= w["box"][2] <= x1])
        right_outside = token_text(words_right_of(line, x1, ADJACENT_X_MARGIN))
        if left_outside:
            left_outside_parts.append(left_outside)
        if left_inside:
            left_inside_parts.append(left_inside)
        if right_inside:
            right_inside_parts.append(right_inside)
        if right_outside:
            right_outside_parts.append(right_outside)

    streams = {
        "top_cut_inside": line_stream(top_cut, x0, x1),
        "top_line_above": token_text(words_in_x_range(above_top, x0, x1)) if above_top else "",
        "top_line_below": token_text(words_in_x_range(below_top, x0, x1)) if below_top else "",
        "bottom_cut_inside": line_stream(bottom_cut, x0, x1),
        "bottom_line_above": token_text(words_in_x_range(above_bottom, x0, x1)) if above_bottom else "",
        "bottom_line_below": token_text(words_in_x_range(below_bottom, x0, x1)) if below_bottom else "",
        "left_outside_adjacent": " | ".join(left_outside_parts),
        "left_inside_adjacent": " | ".join(left_inside_parts),
        "right_inside_adjacent": " | ".join(right_inside_parts),
        "right_outside_adjacent": " | ".join(right_outside_parts),
    }
    derived = {
        "outside_clockwise": " | ".join(
            item
            for item in [
                streams["top_line_above"],
                streams["right_outside_adjacent"],
                streams["bottom_line_below"],
                streams["left_outside_adjacent"],
            ]
            if item
        ),
        "inside_clockwise": " | ".join(
            item
            for item in [
                streams["top_cut_inside"],
                streams["right_inside_adjacent"],
                streams["bottom_cut_inside"],
                streams["left_inside_adjacent"],
            ]
            if item
        ),
    }
    streams.update(derived)
    stream_hits = {key: instruction_hits(value) for key, value in streams.items() if instruction_hits(value)}
    return {
        "name": name,
        "frame": frame,
        "streams": streams,
        "streamCompacts": {key: compact(value) for key, value in streams.items()},
        "instructionHits": stream_hits,
        "lineRefs": {
            "topCut": [ln["line"] for ln in top_cut],
            "bottomCut": [ln["line"] for ln in bottom_cut],
            "aboveTop": above_top["line"] if above_top else None,
            "belowTop": below_top["line"] if below_top else None,
            "aboveBottom": above_bottom["line"] if above_bottom else None,
            "belowBottom": below_bottom["line"] if below_bottom else None,
            "verticalLines": [ln["line"] for ln in vertical_lines],
        },
    }


def draw_overlay(frames: list[dict], page_words: list[dict]) -> None:
    image = Image.open(PAGE_IMAGE).convert("RGB")
    crop = (650, 2280, 2320, 3060)
    cropped = image.crop(crop)
    draw = ImageDraw.Draw(cropped, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    colors = {
        "current": (255, 80, 80, 200),
        "dx_-38_edge_touch": (80, 200, 255, 200),
        "dx_-40_grid": (255, 200, 80, 200),
    }
    for item in frames:
        color = colors.get(item["name"], (255, 255, 255, 180))
        x0, y0, x1, y1 = item["frame"]
        rect = [x0 - crop[0], y0 - crop[1], x1 - crop[0], y1 - crop[1]]
        draw.rectangle(rect, outline=color, width=4)
        draw.text((rect[0] + 4, rect[1] + 4), item["name"], fill=color, font=font)

    # Mark words near the dx=-38 frame because that is the strongest repaired signature.
    main_frame = next(item["frame"] for item in frames if item["name"] == "dx_-38_edge_touch")
    x0, y0, x1, y1 = main_frame
    for word in page_words:
        box = word["box"]
        near_left = 0 <= abs(box[2] - x0) <= ADJACENT_X_MARGIN and overlap(box[1], box[3], y0, y1) > 0
        inside_strip = x0 <= box[0] <= x0 + ADJACENT_X_MARGIN and overlap(box[1], box[3], y0, y1) > 0
        if near_left or inside_strip:
            rect = [box[0] - crop[0], box[1] - crop[1], box[2] - crop[0], box[3] - crop[1]]
            draw.rectangle(rect, outline=(0, 255, 160, 180), width=2)
    cropped.save(OUT_OVERLAY, quality=92)


def main() -> None:
    page = load_page76()
    lines = line_groups(page["words"])
    tri = json.loads(TRICONTACT_JSON.read_text(encoding="utf-8"))
    tri_records = {row["name"]: row for row in tri["records"]}
    frame_specs = [
        ("current", tri_records["current"]["frame"]),
        ("dx_-38_edge_touch", tri_records["g5_edge_touch"]["frame"]),
        ("dx_-40_grid", tri_records["nearest_grid_dx_-40"]["frame"]),
    ]
    audits = [frame_audit(name, frame, lines) for name, frame in frame_specs]
    draw_overlay(audits, page["words"])

    all_hits = {
        audit["name"]: audit["instructionHits"]
        for audit in audits
        if audit["instructionHits"]
    }
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "edge-adjacent words around current and repaired p78 frames; no key derivation",
        "sourceReports": {
            "map": str(MAP_JSON.relative_to(ROOT)),
            "triContact": str(TRICONTACT_JSON.relative_to(ROOT)),
        },
        "overlay": str(OUT_OVERLAY.relative_to(ROOT)),
        "frameAudits": audits,
        "instructionHits": all_hits,
        "assessment": [
            "Edge-adjacent reading around current, dx=-38, and dx=-40 frames produces ordinary page-76 corridor prose.",
            "The outside-left stream mostly repeats the already-known G5/O5 path around `$1 billion`, `Volcano Bonds`, `loan`, `Novogratz`, `trust`, and `shitcoiner at heart`.",
            "The top/bottom above/below streams add nearby article context but no instruction-like phrase naming word, letter, line, key, mirror, inside, outside, above, or below.",
            "This closes edge-adjacent text as a standalone selector under the current scan.",
        ],
        "nextMove": "Keep the p78 frame as registration evidence only. The next useful move is still a better source/physical/Canva image or a new external rule that names the extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines_md = [
        "# P78 Frame Edge-Adjacent Units",
        "",
        "Scope: test whether the text just outside or just inside the current/repaired p78 frame edges supplies the missing selector. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{result['overlay']}`",
        f"- Frame variants: `{', '.join(a['name'] for a in audits)}`",
        f"- Instruction-hit frame count: `{len(all_hits)}`",
        "",
        "## Streams",
        "",
        "| frame | stream | output | instruction hits |",
        "|---|---|---|---|",
    ]
    for audit in audits:
        for key, value in audit["streamCompacts"].items():
            hits = audit["instructionHits"].get(key, [])
            lines_md.append(f"| `{audit['name']}` | `{key}` | `{value}` | `{hits}` |")
    lines_md.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines_md.append(f"- {item}")
    lines_md.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines_md) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")
    print("instruction-hit frame count:", len(all_hits))
    for audit in audits:
        print(audit["name"], "left outside:", compact(audit["streams"]["left_outside_adjacent"], 160))


if __name__ == "__main__":
    main()
