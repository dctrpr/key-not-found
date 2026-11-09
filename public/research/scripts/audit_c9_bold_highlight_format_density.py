#!/usr/bin/env python3
"""Check C9 slot bold/highlight format density on page 76.

The C9/YK frame isolates O4/B4/G5/O5 only after combining color/style with the
frame. This bounded pass checks the line-level bold/highlight evidence inside
the same C9 corridor band, especially whether bold letters themselves isolate
the active quartet or provide a source-backed unit/order rule.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LINE_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
C9_JSON = ROOT / "analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json"
YK_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/c9_bold_highlight_format_density"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_bold_highlight_format_density.json"
OUT_MD = OUT / "c9_bold_highlight_format_density.md"
SHEET = OUT / "c9_bold_highlight_format_density_sheet.jpg"


HARD_INSTRUCTION_TERMS = [
    "address",
    "edge",
    "extract",
    "font",
    "fold",
    "key",
    "letter",
    "line",
    "mirror",
    "private",
    "read",
    "reverse",
    "seed",
    "select",
    "take",
    "word",
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


def token_hits(text: str) -> list[str]:
    normalized = " ".join(re.findall(r"[A-Za-z0-9$]+", text)).lower()
    return [term for term in HARD_INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", normalized)]


def clean_letters(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9$]", "", text)


def classify_highlights(tags: list[str]) -> dict[str, int]:
    return {
        "orange": sum(1 for tag in tags if tag.startswith("orange:")),
        "grey": sum(1 for tag in tags if tag.startswith("grey:")),
        "bold": sum(1 for tag in tags if tag.startswith("bold")),
    }


def target_line_map(c9: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    by_line: dict[int, list[dict[str, Any]]] = {}
    for target in c9["activeTargets"]:
        by_line.setdefault(int(target["pageLine"]), []).append(target)
    return by_line


def make_rows(line_data: dict[str, Any], c9: dict[str, Any]) -> list[dict[str, Any]]:
    by_line = target_line_map(c9)
    rows = []
    for record in line_data["records"]:
        corridor = int(record["corridorIndex"])
        if corridor < 4 or corridor > 14:
            continue
        tags = list(record.get("highlights", []))
        bold_letters = record.get("boldLetters", "")
        partial_bold = record.get("partialBoldLetters", "")
        targets = by_line.get(int(record["lineIndex"]), [])
        active_ids = [target["id"] for target in targets]
        active_short = [target["shortId"] for target in targets]
        tag_counts = classify_highlights(tags)
        format_signal = bool(tags or bold_letters or partial_bold)
        rows.append(
            {
                "lineIndex": int(record["lineIndex"]),
                "corridorIndex": corridor,
                "text": record["text"],
                "wordCount": int(record["wordCount"]),
                "activeTargetIds": active_ids,
                "activeTargetShortIds": active_short,
                "isActiveTargetLine": bool(active_ids),
                "boldLetters": bold_letters,
                "boldLetterCount": len(clean_letters(bold_letters)),
                "partialBoldLetters": partial_bold,
                "partialBoldLetterCount": len(clean_letters(partial_bold)),
                "highlightTags": tags,
                "highlightTagCount": len(tags),
                "highlightTagCounts": tag_counts,
                "formatSignal": format_signal,
                "hardInstructionHits": sorted(set(token_hits(" ".join([bold_letters, partial_bold, " ".join(tags)])))),
            }
        )
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    crop = [180, 2070, 2315, 3065]
    scale = 0.43
    panel = Image.open(PAGE_IMAGE).convert("RGB").crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 28
    header_h = 132
    footer_h = 440
    sheet = Image.new("RGB", (margin * 2 + panel.size[0], header_h + panel.size[1] + footer_h + margin), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(15)
    small = font(12)
    mono = font(12)

    draw.text((margin, 20), "C9 Bold/Highlight Format Density", fill=(240, 244, 248), font=title)
    draw.text((margin, 58), "Tests whether bold letters or highlight tags inside C9 isolate O4/B4/G5/O5.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 84), "Blue = C9 frame. Orange/grey boxes = active targets. Right table summarizes C9 corridor lines.", fill=(178, 188, 199), font=small)
    sheet.paste(panel, (margin, header_h))

    frame = result["c9Frame"]
    targets = result["activeTargets"]

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline="#55d6ff", width=3)
    for target in targets:
        color = "#ff9b2e" if target["visualState"] == "Y" else "#aab4c2"
        box = target["box"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
        draw.text((sx(box[0]), max(header_h, sy(box[1]) - 16)), target["shortId"], fill=color, font=small)

    y = header_h + panel.size[1] + 22
    draw.text((margin, y), "Summary", fill=(238, 243, 248), font=normal)
    y += 28
    notes = [
        f"C9 corridor lines: {result['summary']['lineCount']}; active target lines: {result['summary']['activeLineCount']}; non-active format lines: {result['summary']['nonActiveFormatLineCount']}.",
        f"Bold-letter active exact target matches: {result['summary']['activeExactBoldTargetMatchCount']}/4.",
        f"Active bold stream: {result['summary']['activeBoldLetterStream'] or '-'}",
        f"Non-active bold stream: {result['summary']['nonActiveBoldLetterStream'] or '-'}",
        f"Hard instruction hits in bounded format streams: {result['summary']['hardInstructionHitCount']}.",
        "Result: bold/highlight density is format context only; Y/K+frame remains source-validation, not extraction.",
    ]
    for note in notes:
        draw.text((margin, y), note[:132], fill=(255, 219, 137), font=normal)
        y += 24

    y += 8
    draw.text((margin, y), "C9 Line Format Rows", fill=(238, 243, 248), font=normal)
    y += 24
    for row in result["lineRows"]:
        tag = ",".join(row["activeTargetShortIds"]) or "-"
        bold = row["boldLetters"] or "-"
        highlights = "; ".join(row["highlightTags"]) or "-"
        draw.text(
            (margin, y),
            f"L{row['lineIndex']}/C{row['corridorIndex']} {tag} bold={bold[:34]} tags={highlights[:56]}",
            fill="#c6d1df",
            font=mono,
        )
        y += 18

    sheet.save(SHEET, quality=94)


def main() -> None:
    line_data = load_json(LINE_JSON)
    c9 = load_json(C9_JSON)
    yk = load_json(YK_JSON)
    rows = make_rows(line_data, c9)
    active_rows = [row for row in rows if row["isActiveTargetLine"]]
    non_active_rows = [row for row in rows if not row["isActiveTargetLine"]]
    format_rows = [row for row in rows if row["formatSignal"]]
    non_active_format_rows = [row for row in non_active_rows if row["formatSignal"]]

    active_bold_stream = "".join(row["boldLetters"] for row in active_rows)
    non_active_bold_stream = "".join(row["boldLetters"] for row in non_active_rows)
    format_tag_stream = " | ".join(tag for row in rows for tag in row["highlightTags"])
    hard_hits = sorted(set(token_hits(active_bold_stream + " " + non_active_bold_stream + " " + format_tag_stream)))

    exact_bold_matches = []
    mismatches = []
    expected_by_id = {
        "buying_dip": "buyingthedip",
        "one_billion": "$1billion",
        "volcano_bonds": "VolcanoBonds",
        "shitcoiner_heart": "shitcoineratheart",
    }
    for row in active_rows:
        for target_id in row["activeTargetIds"]:
            expected = expected_by_id[target_id]
            actual = clean_letters(row["boldLetters"])
            if expected.lower() in actual.lower():
                exact_bold_matches.append({"targetId": target_id, "lineIndex": row["lineIndex"], "actualBoldLetters": row["boldLetters"]})
            else:
                mismatches.append({"targetId": target_id, "lineIndex": row["lineIndex"], "expectedBoldLetters": expected, "actualBoldLetters": row["boldLetters"]})

    result: dict[str, Any] = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 page-76 bold/highlight format density control; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "page76LineLevelCorridor": rel(LINE_JSON),
            "c9FramePageControl": rel(C9_JSON),
            "ykFrameControl": rel(YK_JSON),
        },
        "c9Frame": c9["c9Frame"],
        "activeTargets": c9["activeTargets"],
        "lineRows": rows,
        "summary": {
            "lineCount": len(rows),
            "activeLineCount": len(active_rows),
            "formatSignalLineCount": len(format_rows),
            "nonActiveFormatLineCount": len(non_active_format_rows),
            "activeBoldLetterStream": active_bold_stream,
            "nonActiveBoldLetterStream": non_active_bold_stream,
            "activeBoldLetterCount": len(clean_letters(active_bold_stream)),
            "nonActiveBoldLetterCount": len(clean_letters(non_active_bold_stream)),
            "activeExactBoldTargetMatchCount": len(exact_bold_matches),
            "activeExactBoldTargetMatches": exact_bold_matches,
            "activeBoldTargetMismatches": mismatches,
            "formatTagStream": format_tag_stream,
            "hardInstructionHits": hard_hits,
            "hardInstructionHitCount": len(hard_hits),
            "frameYkActiveTargetCoverage": yk.get("summary", {}).get("frameYkActiveTargetCoverage"),
            "frameYkNonActiveGroupCount": yk.get("summary", {}).get("frameYkNonActiveGroupCount"),
            "selectorUnlocked": False,
        },
        "assessment": [
            "C9 corridor format is dense: active target lines and non-active lines both contain bold/highlight signals.",
            "Only O4 and O5 have exact active phrase matches in the line-level bold-letter stream; B4 has no bold letters and G5's line-level bold letters are IMF, not Volcano Bonds.",
            "Non-active C9 lines add substantial bold-letter material: President Nayib Bukele, loanie, Nvz, and Idelluhu.",
            "Therefore bold letters inside C9 cannot replace the Y/K+frame isolation rule and do not supply unit/order permission.",
        ],
        "decision": {
            "c9BoldHighlightFormatDensity": "closed_for_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep C9/YK as source-validation only. Reopen extraction only if a new source/clue explicitly names bold letters, highlight colors, or a format-unit order.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Bold/Highlight Format Density",
        "",
        "Scope: check page-76 line-level bold/highlight evidence inside the C9 frame band. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- C9 frame: `{result['c9Frame']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- C9 corridor line count: `{result['summary']['lineCount']}`.",
        f"- Active target lines: `{result['summary']['activeLineCount']}`.",
        f"- Format-signal lines: `{result['summary']['formatSignalLineCount']}`; non-active format-signal lines: `{result['summary']['nonActiveFormatLineCount']}`.",
        f"- Active bold-letter stream: `{active_bold_stream}`.",
        f"- Non-active bold-letter stream: `{non_active_bold_stream}`.",
        f"- Exact active phrase matches in bold letters: `{len(exact_bold_matches)}/4`.",
        f"- Hard instruction hits in bounded format streams: `{len(hard_hits)}` (`{hard_hits}`).",
        "",
        "## C9 Line Format Rows",
        "",
        "| line/corridor | active target | bold letters | partial bold | highlight tags |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `L{row['lineIndex']}/C{row['corridorIndex']}` | `{','.join(row['activeTargetShortIds']) or '-'}` | `{row['boldLetters'] or '-'}` | `{row['partialBoldLetters'] or '-'}` | `{'; '.join(row['highlightTags']) or '-'}` |"
        )

    lines.extend(
        [
            "",
            "## Active Bold Match Check",
            "",
        ]
    )
    for item in exact_bold_matches:
        lines.append(f"- Match: `{item['targetId']}` on line `{item['lineIndex']}` has bold letters `{item['actualBoldLetters']}`.")
    for item in mismatches:
        lines.append(
            f"- Mismatch: `{item['targetId']}` on line `{item['lineIndex']}` expected `{item['expectedBoldLetters']}` but line-level bold letters are `{item['actualBoldLetters'] or '-'}`."
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote C9 bold-letter or general highlight density as a selector.",
            "- The line-level bold stream does not match all four active targets and includes non-active controls.",
            "- Keep C9/YK as source-validation only. Reopen extraction only if a new source/clue explicitly names bold letters, highlight colors, or a format-unit order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
