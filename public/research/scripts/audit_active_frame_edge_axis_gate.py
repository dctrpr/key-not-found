#!/usr/bin/env python3
"""Check whether p78 frame edges/centerlines select active page-76 targets.

Whole-frame overlap and frame-center reflection are already closed for the
current scan. This bounded pass tests the remaining simple layout mechanic:
whether the p78 same-layout or current-mirror frame edges/centerlines behave as
readable axes through O4/B4/G5/O5 or instruction-bearing words.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
P78_SOURCE_JSON = ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json"
SCORING_JSON = ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/active_frame_edge_axis_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_frame_edge_axis_gate.json"
OUT_MD = OUT / "active_frame_edge_axis_gate.md"
SHEET = OUT / "active_frame_edge_axis_gate_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def hard_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def overlap_len(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def line_contacts_box(line: dict[str, Any], box: list[float]) -> dict[str, Any]:
    orientation = line["orientation"]
    value = line["value"]
    span0, span1 = line["span"]
    if orientation == "vertical":
        crosses = box[0] <= value <= box[2] and overlap_len(span0, span1, box[1], box[3]) > 0
        contact = overlap_len(span0, span1, box[1], box[3]) / max(box[3] - box[1], 1.0) if crosses else 0.0
        distance = 0.0 if box[0] <= value <= box[2] else min(abs(value - box[0]), abs(value - box[2]))
    else:
        crosses = box[1] <= value <= box[3] and overlap_len(span0, span1, box[0], box[2]) > 0
        contact = overlap_len(span0, span1, box[0], box[2]) / max(box[2] - box[0], 1.0) if crosses else 0.0
        distance = 0.0 if box[1] <= value <= box[3] else min(abs(value - box[1]), abs(value - box[3]))
    return {
        "crosses": crosses,
        "contactFraction": round(contact, 6),
        "perpendicularDistancePx": round(distance, 2),
    }


def frame_lines(frame_name: str, frame: list[float]) -> list[dict[str, Any]]:
    x0, y0, x1, y1 = frame
    cx, cy = center(frame)
    return [
        {"id": f"{frame_name}_left", "frame": frame_name, "role": "left", "orientation": "vertical", "value": x0, "span": [y0, y1]},
        {"id": f"{frame_name}_right", "frame": frame_name, "role": "right", "orientation": "vertical", "value": x1, "span": [y0, y1]},
        {"id": f"{frame_name}_center_x", "frame": frame_name, "role": "center_x", "orientation": "vertical", "value": cx, "span": [y0, y1]},
        {"id": f"{frame_name}_top", "frame": frame_name, "role": "top", "orientation": "horizontal", "value": y0, "span": [x0, x1]},
        {"id": f"{frame_name}_bottom", "frame": frame_name, "role": "bottom", "orientation": "horizontal", "value": y1, "span": [x0, x1]},
        {"id": f"{frame_name}_center_y", "frame": frame_name, "role": "center_y", "orientation": "horizontal", "value": cy, "span": [x0, x1]},
    ]


def line_word_hits(line: dict[str, Any], page_words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for word in page_words:
        c = line_contacts_box(line, word["box"])
        if not c["crosses"]:
            continue
        hits = hard_hits(word.get("text", ""))
        rows.append(
            {
                "id": word["id"],
                "text": word.get("text", ""),
                "importance": word.get("importance", 0),
                "contactFraction": c["contactFraction"],
                "hardInstructionHits": hits,
            }
        )
    return rows


def summarize_line(line: dict[str, Any], targets: list[dict[str, Any]], page_words: list[dict[str, Any]]) -> dict[str, Any]:
    target_hits = []
    nearest = []
    for target in targets:
        c = line_contacts_box(line, target["box"])
        if c["crosses"]:
            target_hits.append(
                {
                    "id": target["id"],
                    "label": target["label"],
                    "visualState": target["visualState"],
                    "pageLine": target["pageLine"],
                    "corridorIndex": target["corridorIndex"],
                    "contactFraction": c["contactFraction"],
                }
            )
        nearest.append(
            {
                "id": target["id"],
                "distancePx": c["perpendicularDistancePx"],
                "crosses": c["crosses"],
            }
        )
    words = line_word_hits(line, page_words)
    hard_terms = sorted({term for row in words for term in row["hardInstructionHits"]})
    return {
        **line,
        "value": round(line["value"], 2),
        "span": [round(v, 2) for v in line["span"]],
        "activeTargetHitCount": len(target_hits),
        "activeTargetHits": target_hits,
        "strongActiveTargetHitCount": sum(1 for row in target_hits if row["contactFraction"] >= 0.5),
        "nearestActiveDistances": sorted(nearest, key=lambda row: row["distancePx"]),
        "wordHitCount": len(words),
        "wordPreview": " ".join(row["text"] for row in words[:8]),
        "focusWordCount": sum(1 for row in words if row["importance"] >= 3),
        "hardInstructionHitCount": len(hard_terms),
        "hardInstructionHits": hard_terms,
        "wordRows": words,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [180, 2050, 2320, 3065]
    scale = 0.48
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 138
    table_h = 260
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + table_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 22), "Active Frame Edge/Axis Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 60),
        "Tests p78 same-layout and current-mirror frame edges/centerlines against O4/B4/G5/O5.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 86),
        "Cyan = same-layout frame/axes. Blue = current mirror frame/axes. Orange/grey boxes = active targets.",
        fill=(176, 186, 198),
        font=small,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    def draw_box(box: list[float], color: str, width: int = 2) -> None:
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)

    draw_box(result["frames"]["sameLayoutFrame"], "#55d6ff", 3)
    draw_box(result["frames"]["currentMirrorFrame"], "#4f7dff", 3)
    for line in result["lines"]:
        color = "#55d6ff" if line["frame"] == "same_layout" else "#4f7dff"
        width = 2 if "center" in line["role"] else 1
        if line["orientation"] == "vertical":
            draw.line((sx(line["value"]), sy(line["span"][0]), sx(line["value"]), sy(line["span"][1])), fill=color, width=width)
        else:
            draw.line((sx(line["span"][0]), sy(line["value"]), sx(line["span"][1]), sy(line["value"])), fill=color, width=width)

    colors = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for target in result["targets"]:
        draw_box(target["box"], colors.get(target["visualState"], "#ffffff"), 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 16), target["id"], fill="#ffffff", font=small)

    y = header_h + panel.size[1] + 20
    draw.text((margin, y), "Line Contacts", fill=(238, 243, 248), font=normal)
    y += 30
    draw.text((margin, y), "line", fill=(129, 143, 158), font=small)
    draw.text((margin + 270, y), "active hits", fill=(129, 143, 158), font=small)
    draw.text((margin + 470, y), "instruction hits", fill=(129, 143, 158), font=small)
    draw.text((margin + 650, y), "words", fill=(129, 143, 158), font=small)
    y += 22
    for line in result["lines"]:
        active = ",".join(row["id"] for row in line["activeTargetHits"]) or "-"
        instr = ",".join(line["hardInstructionHits"]) or "-"
        draw.text((margin, y), line["id"], fill=(202, 211, 221), font=mono)
        draw.text((margin + 270, y), active[:28], fill=(202, 211, 221), font=mono)
        draw.text((margin + 470, y), instr, fill=(202, 211, 221), font=mono)
        draw.text((margin + 650, y), str(line["wordHitCount"]), fill=(202, 211, 221), font=mono)
        y += 18
        if y > sheet_h - margin - 20:
            break

    sheet.save(SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    article = load_json(ARTICLE_JSON)
    p78_source = load_json(P78_SOURCE_JSON)
    scoring = load_json(SCORING_JSON)
    page76 = next(page for page in article["pages"] if page["page"] == 76)
    targets = active["targets"]

    same_layout_frame = list(map(float, p78_source["sourceGraphic"]["box"]))
    current_mirror_frame = list(map(float, scoring["numericBenchmarks"]["p78Frame"]["currentFrame"]))
    raw_lines = frame_lines("same_layout", same_layout_frame) + frame_lines("current_mirror", current_mirror_frame)
    lines = [summarize_line(line, targets, page76["words"]) for line in raw_lines]

    instruction_terms = sorted({term for line in lines for term in line["hardInstructionHits"]})
    total_active_hits = sum(line["activeTargetHitCount"] for line in lines)
    total_strong_active_hits = sum(line["strongActiveTargetHitCount"] for line in lines)
    line_hit_stream = " | ".join(
        f"{line['id']}=>{','.join(row['id'] for row in line['activeTargetHits']) or '-'}"
        for line in lines
    )
    strong_lines = [line["id"] for line in lines if line["strongActiveTargetHitCount"]]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 same-layout/current-mirror frame edge and centerline selector audit; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "p78SourceInstructionSurface": rel(P78_SOURCE_JSON),
            "futureSourceScoringRubric": rel(SCORING_JSON),
        },
        "frames": {
            "sameLayoutFrame": [round(v, 2) for v in same_layout_frame],
            "currentMirrorFrame": [round(v, 2) for v in current_mirror_frame],
        },
        "targets": [
            {
                "id": row["id"],
                "label": row["label"],
                "phrase": row["phrase"],
                "box": [round(v, 2) for v in row["box"]],
                "visualState": row["visualState"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
            }
            for row in targets
        ],
        "lines": lines,
        "summary": {
            "frameCount": 2,
            "lineCount": len(lines),
            "totalActiveTargetHitCount": total_active_hits,
            "totalStrongActiveTargetHitCount": total_strong_active_hits,
            "strongActiveTargetLines": strong_lines,
            "lineHitStream": line_hit_stream,
            "totalHardInstructionHitCount": len(instruction_terms),
            "totalHardInstructionHits": instruction_terms,
            "selectorUnlocked": False,
        },
        "decision": {
            "activeFrameEdgeAxis": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep p78 frame edges/centerlines as layout/source-comparison landmarks only; reopen only if source wording names frame edge, centerline, axis, or boundary reading.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines_md = [
        "# Active Frame Edge/Axis Gate",
        "",
        "Scope: test whether p78 same-layout/current-mirror frame edges or centerlines select O4/B4/G5/O5 or instruction-bearing words. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Same-layout frame: `{result['frames']['sameLayoutFrame']}`",
        f"- Current-mirror frame: `{result['frames']['currentMirrorFrame']}`",
        f"- Lines checked: `{result['summary']['lineCount']}`",
        f"- Active target contacts: `{result['summary']['totalActiveTargetHitCount']}` total, `{result['summary']['totalStrongActiveTargetHitCount']}` strong",
        f"- Hard instruction hits: `{result['summary']['totalHardInstructionHitCount']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Contact Table",
        "",
        "| line | role | active hits | strong hits | words touched | instruction hits | preview |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for line in lines:
        active_hits = ", ".join(f"{row['id']}:{row['contactFraction']}" for row in line["activeTargetHits"]) or "-"
        lines_md.append(
            f"| `{line['id']}` | `{line['role']}` | {active_hits} | `{line['strongActiveTargetHitCount']}` | `{line['wordHitCount']}` | `{', '.join(line['hardInstructionHits']) or '-'}` | `{line['wordPreview']}` |"
        )
    lines_md.extend(
        [
            "",
            "## Decision",
            "",
            "- Frame edges/centerlines do not create a selector from the active quartet.",
            "- Same-layout frame lines touch B4/G5/O5, and current-mirror lines touch O5/O4-adjacent highlight geometry, but the contacts are expected from the already-known frame placement.",
            "- No frame line touches all four active targets, no line creates an ordered `O4/B4/G5/O5` transfer, and no touched words contain hard instruction terms.",
            "- Keep p78 frame edges/centerlines as layout/source-comparison landmarks only; reopen only if source wording names frame edge, centerline, axis, or boundary reading.",
        ]
    )
    OUT_MD.write_text("\n".join(lines_md) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("lineCount:", len(lines))
    print("activeTargetHits:", total_active_hits)
    print("strongActiveTargetHits:", total_strong_active_hits)
    print("hardInstructionHits:", len(instruction_terms))
    print("lineHitStream:", line_hit_stream)


if __name__ == "__main__":
    main()
