#!/usr/bin/env python3
"""Control-test the p78 OVERDOSE graphic same-layout slot across article pages.

The previous header-registration pass showed that placing the p78 pull-quote
frame at the same page coordinates on page 76 covers B4/G5 and clips O5. This
bounded pass checks whether that same-layout slot is a distinctive page-76
selector or just a recurring lower-page layout zone.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_TARGETS_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
P78_SOURCE_JSON = ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json"
OUT = ROOT / "analysis_outputs/source_audit/overdose_same_slot_control_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "overdose_same_slot_control_gate.json"
OUT_MD = OUT / "overdose_same_slot_control_gate.md"
SHEET = OUT / "overdose_same_slot_control_gate_sheet.jpg"

HARD_INSTRUCTION_TERMS = [
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


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def overlap_fraction(frame: list[float], box: list[float]) -> float:
    inter = intersection(frame, box)
    return 0.0 if not inter else area(inter) / max(area(box), 1.0)


def mirror_box_x(box: list[float], width: float) -> list[float]:
    return [width - box[2], box[1], width - box[0], box[3]]


def hard_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in HARD_INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def page_image_path(page_no: int) -> Path:
    return ROOT / f"analysis_outputs/3d_article_map/page_{page_no}_upright.jpg"


def summarize_page_slot(page: dict[str, Any], frame: list[float], active_targets: list[dict[str, Any]]) -> dict[str, Any]:
    word_rows = []
    hard_terms: set[str] = set()
    for word in page.get("words", []):
        frac = overlap_fraction(frame, word["box"])
        if frac <= 0.15:
            continue
        hits = hard_hits(word.get("text", ""))
        hard_terms.update(hits)
        word_rows.append(
            {
                "id": word["id"],
                "text": word.get("text", ""),
                "token": word.get("token", ""),
                "overlapVsWord": round(frac, 6),
                "importance": word.get("importance", 0),
                "hardInstructionHits": hits,
            }
        )

    highlight_rows = []
    for h in page.get("highlights", []):
        frac = overlap_fraction(frame, h["box"])
        if frac <= 0:
            continue
        highlight_rows.append(
            {
                "id": h["id"],
                "kind": h["kind"],
                "overlapVsHighlight": round(frac, 6),
            }
        )

    active_rows = []
    if page["page"] == 76:
        for target in active_targets:
            frac = overlap_fraction(frame, target["box"])
            if frac <= 0:
                continue
            active_rows.append(
                {
                    "id": target["id"],
                    "label": target["label"],
                    "overlapVsTarget": round(frac, 6),
                    "pageLine": target["pageLine"],
                    "corridorIndex": target["corridorIndex"],
                }
            )

    text_stream = " ".join(row["text"] for row in word_rows)
    return {
        "page": page["page"],
        "frame": [round(v, 2) for v in frame],
        "wordCount": len(word_rows),
        "focusWordCount": sum(1 for row in word_rows if row["importance"] >= 3),
        "hardInstructionHitCount": len(hard_terms),
        "hardInstructionHits": sorted(hard_terms),
        "highlightOverlapCount": len(highlight_rows),
        "activeTargetHitCount": len(active_rows),
        "activeTargets": active_rows,
        "wordStreamPreview": text_stream[:220],
        "wordRows": word_rows,
        "highlightRows": highlight_rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    pages = [75, 76, 77, 78, 79]
    crop = [220, 2300, 1800, 3060]
    scale = 0.28
    panel_w = int((crop[2] - crop[0]) * scale)
    panel_h = int((crop[3] - crop[1]) * scale)
    margin = 24
    gap = 18
    header_h = 130
    table_h = 290
    sheet_w = margin * 2 + len(pages) * panel_w + (len(pages) - 1) * gap
    sheet_h = header_h + panel_h + table_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(16)
    small = font(12)

    draw.text((margin, 20), "OVERDOSE Same-Slot Control Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 58),
        "The p78 pull-quote frame is placed at the same page coordinates across article pages.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 84),
        "Blue box = same-layout p78 source slot. Orange/grey outlines = active p76 targets.",
        fill=(176, 186, 198),
        font=small,
    )

    active_targets = result["activeTargets"]
    x = margin
    for page_no in pages:
        img = Image.open(page_image_path(page_no)).convert("RGB")
        panel = img.crop(crop).resize((panel_w, panel_h))
        sheet.paste(panel, (x, header_h))
        draw.text((x, header_h - 22), f"p{page_no}", fill=(238, 242, 247), font=normal)

        def sx(v: float) -> float:
            return x + (v - crop[0]) * scale

        def sy(v: float) -> float:
            return header_h + (v - crop[1]) * scale

        frame = result["sameSlotFrame"]
        draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline="#55d6ff", width=3)
        if page_no == 76:
            for target in active_targets:
                color = "#ff9b2e" if target["visualState"] == "Y" else "#aeb7c2"
                box = target["box"]
                draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=2)
                draw.text((sx(box[0]), max(header_h, sy(box[1]) - 13)), target["shortId"], fill=color, font=small)
        x += panel_w + gap

    y = header_h + panel_h + 26
    draw.text((margin, y), "Control Summary", fill=(238, 242, 247), font=normal)
    y += 28
    col_x = [margin, margin + 70, margin + 165, margin + 270, margin + 380, margin + 510]
    headers = ["page", "words", "focus", "orange", "active hits", "hard instruction terms"]
    for label, cx in zip(headers, col_x):
        draw.text((cx, y), label, fill=(176, 186, 198), font=small)
    y += 22
    for row in result["sameSlotPageRows"]:
        values = [
            f"p{row['page']}",
            str(row["wordCount"]),
            str(row["focusWordCount"]),
            str(row["highlightOverlapCount"]),
            str(row["activeTargetHitCount"]),
            ", ".join(row["hardInstructionHits"]) or "-",
        ]
        for value, cx in zip(values, col_x):
            draw.text((cx, y), value[:52], fill=(232, 238, 244), font=small)
        y += 22

    y += 12
    draw.rectangle([margin, y, sheet_w - margin, y + 82], fill=(40, 28, 18), outline=(111, 74, 30), width=2)
    draw.text((margin + 12, y + 12), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 12, y + 40),
        "Same-slot geometry is a source-comparison benchmark only: p76 is interesting, but the slot has no hard instruction term.",
        fill=(255, 219, 137),
        font=small,
    )
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(SHEET, quality=94)


def main() -> None:
    article = load_json(ARTICLE_JSON)
    active = load_json(ACTIVE_TARGETS_JSON)
    p78_source = load_json(P78_SOURCE_JSON)
    p78_box = [float(v) for v in p78_source["sourceGraphic"]["box"]]
    width = article["pages"][0]["width"]
    mirror_frame = mirror_box_x(p78_box, width)

    id_map = {
        "buying_dip": "O4",
        "one_billion": "B4",
        "volcano_bonds": "G5",
        "shitcoiner_heart": "O5",
    }
    active_targets = [
        {
            "id": row["id"],
            "shortId": id_map[row["id"]],
            "label": row["label"],
            "box": [float(v) for v in row["box"]],
            "visualState": row["visualState"],
            "pageLine": row["pageLine"],
            "corridorIndex": row["corridorIndex"],
        }
        for row in active["targets"]
    ]

    pages = [page for page in article["pages"] if page["page"] in {75, 76, 77, 78, 79}]
    same_rows = [summarize_page_slot(page, p78_box, active_targets) for page in pages]
    p76_page = next(page for page in pages if page["page"] == 76)
    mirror_row = summarize_page_slot(p76_page, mirror_frame, active_targets)

    p76_same = next(row for row in same_rows if row["page"] == 76)
    max_control_active_hits = max(row["activeTargetHitCount"] for row in same_rows if row["page"] != 76)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "same-layout p78 OVERDOSE graphic slot control across article pages; no OCR or key derivation",
        "inputs": {
            "article3dMap": rel(ARTICLE_JSON),
            "activeTargets": rel(ACTIVE_TARGETS_JSON),
            "p78SourceGraphic": rel(P78_SOURCE_JSON),
        },
        "sameSlotFrame": [round(v, 2) for v in p78_box],
        "p76HorizontalMirrorFrame": [round(v, 2) for v in mirror_frame],
        "activeTargets": active_targets,
        "sameSlotPageRows": same_rows,
        "p76MirrorRow": mirror_row,
        "summary": {
            "p76SameSlotActiveTargetHitCount": p76_same["activeTargetHitCount"],
            "p76SameSlotActiveTargets": [row["id"] for row in p76_same["activeTargets"]],
            "p76SameSlotHardInstructionHitCount": p76_same["hardInstructionHitCount"],
            "p76MirrorActiveTargetHitCount": mirror_row["activeTargetHitCount"],
            "p76MirrorActiveTargets": [row["id"] for row in mirror_row["activeTargets"]],
            "p76MirrorHardInstructionHitCount": mirror_row["hardInstructionHitCount"],
            "controlPageCount": len(same_rows) - 1,
            "maxControlActiveHitCount": max_control_active_hits,
        },
        "assessment": [
            "The p78 same-layout slot is distinctive for page 76 only because the active target boxes are defined on page 76; it fully covers B4/G5 and clips O5, but it still misses O4.",
            "Across the comparable same-layout page slots, the covered text is ordinary article prose and no slot contains a hard extraction term such as read/take/word/letter/mirror/key/private/encoded.",
            "The current p76 horizontal mirror remains the known p78 frame benchmark but touches only O5 among active targets.",
            "Therefore the same-layout p78 OVERDOSE slot is useful as a future source-comparison control, not as a current-scan selector.",
        ],
        "decision": {
            "sameSlotAsSelector": "closed_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Reopen same-slot OVERDOSE layout only if a future original-layout/source item explicitly names repeated layout, same position, or page-slot transfer as the unit/order rule.",
        },
        "sheet": rel(SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# OVERDOSE Same-Slot Control Gate",
        "",
        "Scope: place the p78 source graphic frame at the same page coordinates across article pages and compare it to the page-76 active targets. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Same-layout frame: `{result['sameSlotFrame']}`",
        f"- p76 horizontal mirror frame: `{result['p76HorizontalMirrorFrame']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Same-Slot Page Controls",
        "",
        "| page | words in slot | focus words | highlight overlaps | active target hits | hard instruction hits | preview |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in same_rows:
        lines.append(
            f"| p{row['page']} | `{row['wordCount']}` | `{row['focusWordCount']}` | `{row['highlightOverlapCount']}` | "
            f"`{row['activeTargetHitCount']}` | `{row['hardInstructionHitCount']}` | {row['wordStreamPreview']} |"
        )
    lines.extend(
        [
            "",
            "## P76 Mirror Comparison",
            "",
            f"- Current horizontal mirror active hits: `{mirror_row['activeTargetHitCount']}` ({', '.join(row['id'] for row in mirror_row['activeTargets']) or '-'})",
            f"- Current horizontal mirror hard instruction hits: `{mirror_row['hardInstructionHitCount']}`",
            "",
            "## Assessment",
            "",
        ]
    )
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", ""])
    lines.append("- Same-slot OVERDOSE layout is closed as a current-scan selector.")
    lines.append("- Keep it as a future source-comparison control only; no selector was unlocked.")
    lines.append(f"- Next move: {result['decision']['nextMove']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("p76SameSlotActiveTargets:", ",".join(result["summary"]["p76SameSlotActiveTargets"]) or "-")
    print("p76SameSlotHardInstructionHitCount:", result["summary"]["p76SameSlotHardInstructionHitCount"])
    print("p76MirrorActiveTargets:", ",".join(result["summary"]["p76MirrorActiveTargets"]) or "-")
    print("p76MirrorHardInstructionHitCount:", result["summary"]["p76MirrorHardInstructionHitCount"])


if __name__ == "__main__":
    main()
