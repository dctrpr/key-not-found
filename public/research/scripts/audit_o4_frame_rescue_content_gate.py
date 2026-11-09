#!/usr/bin/env python3
"""Check whether the 3-up/1-down O4 frame-rescue envelope isolates content.

The previous pass found that the dual p78 frame envelope needs a 3-up/1-down
line-pitch expansion to fully cover O4/B4/G5/O5. This bounded pass asks whether
that rectangle is narrow enough to be a selector, or whether it captures a broad
run of ordinary corridor text.

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
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
OFFSET_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_offset_control/o4_frame_rescue_offset_control.json"
CORRIDOR_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
ARTICLE_MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
ACTIVE_RECON_JSON = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_content_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "o4_frame_rescue_content_gate.json"
OUT_MD = OUT / "o4_frame_rescue_content_gate.md"
SHEET = OUT / "o4_frame_rescue_content_gate_sheet.jpg"


HARD_INSTRUCTION_TERMS = [
    "address",
    "above",
    "below",
    "edge",
    "extract",
    "font",
    "fold",
    "frame",
    "key",
    "left",
    "letter",
    "line",
    "mirror",
    "private",
    "read",
    "right",
    "seed",
    "select",
    "take",
    "word",
]

CONTEXT_TERMS = ["bitcoin", "bonds", "dip", "heart", "imf", "mike", "sell", "shitcoiner", "volcano"]


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


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$']+", text)


def term_hits(text: str, terms: list[str]) -> list[str]:
    normalized = " ".join(words(text)).lower()
    hits = []
    for term in terms:
        if re.search(rf"\b{re.escape(term.lower())}\b", normalized):
            hits.append(term)
    return hits


def robust_char_groups() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP_JSON)
    page = next(page for page in data["pages"] if page.get("page") == 76)
    valid_chars = []
    for char in page["chars"]:
        box = list(map(float, char["box"]))
        w = box[2] - box[0]
        h = box[3] - box[1]
        if w <= 0 or h <= 0 or w > 180 or h > 120:
            continue
        valid_chars.append({**char, "box": box, "yc": (box[1] + box[3]) / 2})

    groups: list[dict[str, Any]] = []
    for char in sorted(valid_chars, key=lambda item: (item["yc"], item["box"][0])):
        if not groups or abs(groups[-1]["medianY"] - char["yc"]) > 28:
            groups.append({"chars": [char], "medianY": char["yc"]})
        else:
            groups[-1]["chars"].append(char)
            ys = sorted(item["yc"] for item in groups[-1]["chars"])
            groups[-1]["medianY"] = ys[len(ys) // 2]

    line_groups = []
    for group in groups:
        chars = sorted(group["chars"], key=lambda item: item["box"][0])
        box = [
            min(item["box"][0] for item in chars),
            min(item["box"][1] for item in chars),
            max(item["box"][2] for item in chars),
            max(item["box"][3] for item in chars),
        ]
        line_groups.append(
            {
                "medianY": round(group["medianY"], 2),
                "box": [round(v, 2) for v in box],
                "ocrText": "".join(item["c"] for item in chars).strip(),
            }
        )
    return line_groups


def line_boxes_for_corridor(records: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    groups = robust_char_groups()
    lower_groups = [group for group in groups if 2050 <= group["medianY"] <= 3060]
    # The 3D layer reliably preserves line positions here. The OCR text is not
    # authority, so the exact wording below comes from the corridor transcript.
    first_line_index = 21
    by_line: dict[int, dict[str, Any]] = {}
    for offset, group in enumerate(lower_groups):
        by_line[first_line_index + offset] = group

    result: dict[int, dict[str, Any]] = {}
    for record in records:
        group = by_line.get(int(record["lineIndex"]))
        if group:
            result[int(record["lineIndex"])] = group
    return result


def classify_lines(frame: list[float], records: list[dict[str, Any]], active_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    line_boxes = line_boxes_for_corridor(records)
    active_phrases = {target["phrase"].lower(): target["id"] for target in active_targets}
    rows = []
    for record in records:
        line_index = int(record["lineIndex"])
        group = line_boxes.get(line_index)
        if not group:
            continue
        frac = overlap_fraction(frame, group["box"])
        if frac <= 0:
            continue

        text = record["text"]
        active_on_line = [
            {"id": target_id, "phrase": phrase}
            for phrase, target_id in active_phrases.items()
            if phrase in text.lower()
        ]
        highlight_entries = record.get("highlights", [])
        non_active_highlights = [
            entry
            for entry in highlight_entries
            if not any(active["phrase"] in entry.lower() for active in active_on_line)
        ]
        all_words = words(text)
        word_count = int(record.get("wordCount") or len(all_words))
        active_word_count = sum(len(words(active["phrase"])) for active in active_on_line)
        rows.append(
            {
                "lineIndex": line_index,
                "corridorIndex": record["corridorIndex"],
                "text": text,
                "lineBox": group["box"],
                "ocrWitness": group["ocrText"],
                "overlapVsLine": round(frac, 6),
                "wordCount": word_count,
                "activeTargets": active_on_line,
                "activeTargetWordCount": active_word_count,
                "boldLetters": record.get("boldLetters", ""),
                "partialBoldLetters": record.get("partialBoldLetters", ""),
                "highlights": highlight_entries,
                "nonActiveHighlights": non_active_highlights,
                "hardInstructionHits": term_hits(text, HARD_INSTRUCTION_TERMS),
                "contextTermHits": term_hits(text, CONTEXT_TERMS),
            }
        )
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [180, 2070, 2315, 3065]
    scale = 0.48
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 28
    header_h = 138
    footer_h = 360
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 22), "O4 Frame Rescue Content Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 60),
        "Checks whether the 3-up/1-down full-coverage frame isolates the active quartet.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 88),
        "Pink = 3-up/1-down. Grey = original dual frame. Orange/grey boxes = active targets. Blue bands = included lines.",
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

    for row in result["includedLines"]:
        box = row["lineBox"]
        draw.rectangle([sx(result["fullCoverageFrame"][0]), sy(box[1]), sx(result["fullCoverageFrame"][2]), sy(box[3])], fill=(30, 74, 125), outline=None)
    # Paste the panel again with transparency not available above; redraw bands as outlines instead.
    sheet.paste(panel, (margin, header_h))
    for row in result["includedLines"]:
        box = row["lineBox"]
        draw.rectangle([sx(result["fullCoverageFrame"][0]), sy(box[1]), sx(result["fullCoverageFrame"][2]), sy(box[3])], outline="#2f8cff", width=1)
        draw.text((sx(result["fullCoverageFrame"][2]) - 60, sy(box[1]) - 2), f"L{row['lineIndex']}", fill="#9ec7ff", font=small)

    draw_box(result["dualEnvelope"], "#91a2b8", 3)
    draw_box(result["topOnlyThreeFrame"], "#ffe45c", 2)
    draw_box(result["fullCoverageFrame"], "#ff73c8", 4)

    colors = {"Y": "#ff9b2e", "K": "#9aa4b2"}
    for target in result["targets"]:
        draw_box(target["box"], colors.get(target["visualState"], "#ffffff"), 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 16), target["id"], fill="#ffffff", font=small)

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Containment Summary", fill=(238, 243, 248), font=normal)
    y += 30
    notes = [
        f"Included lines: {result['summary']['includedLineRange']} ({result['summary']['includedLineCount']} lines).",
        f"Included words: {result['summary']['includedWordCount']}; active-target words: {result['summary']['activeTargetWordCount']}.",
        f"Non-target words in frame: {result['summary']['nonTargetWordCount']}; active-word density: {result['summary']['activeTargetWordDensity']}.",
        f"Non-active highlights: {result['summary']['nonActiveHighlightEntryCount']}; bold-context lines: {result['summary']['nonActiveBoldContextLineCount']}.",
        f"Hard instruction hits inside included exact text: {result['summary']['hardInstructionHitCount']}.",
        "Result: useful source-validation benchmark, not extraction permission.",
    ]
    for note in notes:
        draw.text((margin, y), note, fill=(255, 219, 137), font=normal)
        y += 25

    y += 12
    draw.text((margin, y), "Line Stream", fill=(238, 243, 248), font=normal)
    y += 28
    for row in result["includedLines"][:11]:
        active_ids = ",".join(active["id"] for active in row["activeTargets"]) or "-"
        snippet = row["text"][:82]
        draw.text((margin, y), f"L{row['lineIndex']} C{row['corridorIndex']} {active_ids}: {snippet}", fill=(202, 211, 221), font=mono)
        y += 21

    sheet.save(SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    offset = load_json(OFFSET_JSON)
    corridor = load_json(CORRIDOR_JSON)
    active_recon = load_json(ACTIVE_RECON_JSON)
    targets = active["targets"]
    records = corridor["records"]

    line_pitch = float(offset["linePitchPx"])
    dual = list(map(float, offset["dualEnvelope"]))
    full = list(map(float, offset["minimumFullCoverageFrame"]))
    top_three = [dual[0], dual[1] - 3 * line_pitch, dual[2], dual[3]]
    included = classify_lines(full, records, targets)

    included_words = sum(row["wordCount"] for row in included)
    active_words = sum(row["activeTargetWordCount"] for row in included)
    hard_hits = sorted({hit for row in included for hit in row["hardInstructionHits"]})
    context_hits = sorted({hit for row in included for hit in row["contextTermHits"]})
    non_active_highlights = [
        {"lineIndex": row["lineIndex"], "entry": entry}
        for row in included
        for entry in row["nonActiveHighlights"]
    ]
    non_active_bold_lines = [
        {
            "lineIndex": row["lineIndex"],
            "corridorIndex": row["corridorIndex"],
            "boldLetters": row["boldLetters"],
            "partialBoldLetters": row["partialBoldLetters"],
            "activeTargets": [item["id"] for item in row["activeTargets"]],
        }
        for row in included
        if (row["boldLetters"] or row["partialBoldLetters"])
        and not (
            len(row["activeTargets"]) == 1
            and row["boldLetters"].lower().replace(" ", "")
            in row["activeTargets"][0]["phrase"].lower().replace(" ", "")
        )
    ]

    line_indexes = [row["lineIndex"] for row in included]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3-up/1-down O4 frame-rescue content containment gate; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "offsetControl": rel(OFFSET_JSON),
            "corridorTranscript": rel(CORRIDOR_JSON),
            "article3dMap": rel(ARTICLE_MAP_JSON),
            "activeLineUnitReconciliation": rel(ACTIVE_RECON_JSON),
        },
        "linePitchPx": round(line_pitch, 2),
        "dualEnvelope": [round(v, 2) for v in dual],
        "topOnlyThreeFrame": [round(v, 2) for v in top_three],
        "fullCoverageFrame": [round(v, 2) for v in full],
        "targets": [
            {
                "id": row["id"],
                "phrase": row["phrase"],
                "box": [round(v, 2) for v in row["box"]],
                "visualState": row["visualState"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
            }
            for row in targets
        ],
        "activeLineRecords": active_recon.get("records", []),
        "includedLines": included,
        "nonActiveHighlightEntries": non_active_highlights,
        "nonActiveBoldContextLines": non_active_bold_lines,
        "summary": {
            "includedLineCount": len(included),
            "includedLineRange": f"{min(line_indexes)}-{max(line_indexes)}" if line_indexes else "-",
            "includedCorridorRange": f"{min(row['corridorIndex'] for row in included)}-{max(row['corridorIndex'] for row in included)}"
            if included
            else "-",
            "includedWordCount": included_words,
            "activeTargetWordCount": active_words,
            "nonTargetWordCount": included_words - active_words,
            "activeTargetWordDensity": round(active_words / included_words, 4) if included_words else 0,
            "activeTargetsFullyCovered": [row["id"] for row in targets],
            "nonActiveHighlightEntryCount": len(non_active_highlights),
            "nonActiveBoldContextLineCount": len(non_active_bold_lines),
            "hardInstructionHits": hard_hits,
            "hardInstructionHitCount": len(hard_hits),
            "contextTermHits": context_hits,
            "selectorUnlocked": False,
        },
        "decision": {
            "o4FrameRescueContentGate": "fails_isolation_selector",
            "selectorUnlocked": False,
            "reason": "The compact full-coverage frame captures lines 22-32 and 92 non-target words, plus non-active highlight/bold context, with zero hard instruction hits.",
            "nextMove": "Keep 3-up/1-down as a future source-comparison benchmark only; do not use it to extract under the current scan unless new source wording names a content unit/order.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# O4 Frame Rescue Content Gate",
        "",
        "Scope: check whether the `3-up / 1-down` O4 frame-rescue envelope isolates the active quartet. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Full-coverage frame: `{result['fullCoverageFrame']}`",
        f"- Included line range: `{result['summary']['includedLineRange']}`",
        f"- Included corridor range: `{result['summary']['includedCorridorRange']}`",
        f"- Included words: `{included_words}`",
        f"- Active-target words: `{active_words}`",
        f"- Non-target words: `{included_words - active_words}`",
        f"- Active-target word density: `{result['summary']['activeTargetWordDensity']}`",
        f"- Non-active highlight entries: `{len(non_active_highlights)}`",
        f"- Non-active bold-context lines: `{len(non_active_bold_lines)}`",
        f"- Hard instruction hits: `{hard_hits}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Included Lines",
        "",
        "| line | corridor | words | active targets | hard hits | context hits | text |",
        "|---:|---:|---:|---|---|---|---|",
    ]
    for row in included:
        active_ids = ", ".join(item["id"] for item in row["activeTargets"]) or "-"
        lines.append(
            f"| `{row['lineIndex']}` | `{row['corridorIndex']}` | `{row['wordCount']}` | `{active_ids}` | `{', '.join(row['hardInstructionHits']) or '-'}` | `{', '.join(row['contextTermHits']) or '-'}` | {row['text']} |"
        )

    lines.extend(
        [
            "",
            "## Non-Active Highlight/Bold Content",
            "",
        ]
    )
    for item in non_active_highlights:
        lines.append(f"- L{item['lineIndex']}: `{item['entry']}`")
    for item in non_active_bold_lines:
        active_display = ", ".join(item["activeTargets"]) if item["activeTargets"] else "-"
        lines.append(
            f"- L{item['lineIndex']} C{item['corridorIndex']}: bold `{item['boldLetters']}` partial `{item['partialBoldLetters']}` active `{active_display}`"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The `3-up / 1-down` frame fully covers the active quartet, but it captures a full L22-L32 corridor band rather than isolating only the target phrases.",
            f"- It contains `{included_words - active_words}` non-target words and `{len(non_active_highlights)}` non-active highlight entries.",
            "- It has zero hard instruction hits in the exact corridor text.",
            "- Treat this as a future source/original-layout validation benchmark only, not extraction permission under the current scan.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("includedLineRange:", result["summary"]["includedLineRange"])
    print("includedWordCount:", included_words)
    print("nonTargetWordCount:", included_words - active_words)
    print("hardInstructionHitCount:", len(hard_hits))
    print("selectorUnlocked:", False)


if __name__ == "__main__":
    main()
