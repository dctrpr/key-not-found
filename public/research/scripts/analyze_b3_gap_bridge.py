#!/usr/bin/env python3
"""Audit the B3+3 `Don't believe me?` gap as a possible bridge line.

This pass does not generate key candidates. It checks whether the previously
unsupported B3+3 landing is a true dead miss, or whether the line behaves as a
short prompt that points into the following El Salvador / buying-the-dip block.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LINE_OFFSET_JSON = ROOT / "analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json"
CANONICAL_JSON = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/b3_gap_bridge"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "b3_gap_bridge.json"
OUT_MD = OUT / "b3_gap_bridge.md"
OUT_OVERLAY = OUT / "b3_gap_bridge_overlay.jpg"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_page76() -> dict:
    data = json.loads(CANONICAL_JSON.read_text())
    return next(page for page in data["pages"].values() if page["articlePage"] == 76)


def load_highres_page76() -> dict:
    data = json.loads(MAP_JSON.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def highres_rows(page: dict) -> list[dict]:
    rows: list[list[dict]] = []
    for word in sorted(page["words"], key=lambda w: (w["center"][1], w["center"][0])):
        if word.get("token") == "overdose":
            continue
        placed = False
        for row in rows:
            if abs(row[0]["center"][1] - word["center"][1]) < 16:
                row.append(word)
                placed = True
                break
        if not placed:
            rows.append([word])

    out = []
    for row in rows:
        row.sort(key=lambda w: w["center"][0])
        out.append(
            {
                "y": sum(w["center"][1] for w in row) / len(row),
                "tokens": [norm(w.get("token") or w.get("text") or "") for w in row if norm(w.get("token") or w.get("text") or "")],
                "words": row,
                "box": [
                    min(w["box"][0] for w in row),
                    min(w["box"][1] for w in row),
                    max(w["box"][2] for w in row),
                    max(w["box"][3] for w in row),
                ],
                "text": " ".join(w["text"] for w in row),
            }
        )
    return out


def line_tokens(page: dict, line_index: int) -> list[str]:
    return [norm(w["letters"] or w["text"]) for w in page["words"] if w["lineIndex"] == line_index and norm(w["letters"] or w["text"])]


def best_row_for_line(tokens: list[str], rows: list[dict]) -> dict | None:
    if not tokens:
        return None
    best = None
    best_score = -1
    for row in rows:
        score = 0
        row_tokens = row["tokens"]
        for token in set(tokens):
            score += min(tokens.count(token), row_tokens.count(token))
        if score > best_score:
            best = row
            best_score = score
    return best if best_score > 0 else None


def units_by_line(units: list[dict]) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = defaultdict(list)
    for unit in units:
        out[unit["line"]].append(unit)
    return out


def text_for_line(lines: list[dict], line: int) -> str:
    if 0 <= line < len(lines):
        return clean(lines[line]["text"])
    return ""


def line_info(page: dict, rows: list[dict], units_map: dict[int, list[dict]], line: int) -> dict:
    tokens = line_tokens(page, line)
    row = best_row_for_line(tokens, rows)
    units = units_map.get(line, [])
    return {
        "line": line,
        "text": text_for_line(page["lines"], line),
        "tokens": tokens,
        "rowY": round(row["y"], 2) if row else None,
        "rowBox": [round(v, 2) for v in row["box"]] if row else None,
        "rowText": row["text"] if row else "",
        "units": [u["id"] for u in units],
        "unitLabels": [u["label"] for u in units],
        "isQuestion": "?" in text_for_line(page["lines"], line),
        "isBlank": not text_for_line(page["lines"], line),
    }


def main() -> None:
    offset = json.loads(LINE_OFFSET_JSON.read_text())
    page = load_page76()
    highres = load_highres_page76()
    rows = highres_rows(highres)
    units_map = units_by_line(offset["units"])

    down_rows = [row for row in offset["landingRows"] if row.get("direction") == "down"]
    bridge_checks = []
    for row in down_rows:
        source_index = row["sourceIndex"]
        first_line = row["targetLine"]
        second_line = first_line + source_index
        second_units = units_map.get(second_line, [])
        bridge_checks.append(
            {
                "sourceId": row["sourceId"],
                "sourceIndex": source_index,
                "sourceLine": row["sourceLine"],
                "sourceLabel": row["sourceLabel"],
                "firstLine": first_line,
                "firstText": row["targetText"],
                "firstUnits": row["targetUnits"],
                "firstIsQuestion": "?" in row["targetText"],
                "secondLine": second_line,
                "secondText": text_for_line(page["lines"], second_line),
                "secondUnits": [u["id"] for u in second_units],
                "secondUnitLabels": [u["label"] for u in second_units],
                "secondIsHighlightHit": bool(second_units),
            }
        )

    b3 = next(row for row in bridge_checks if row["sourceId"] == "B3")
    context_lines = [line_info(page, rows, units_map, line) for line in range(15, 24)]
    lower_rows = json.loads(LOWER_MARKS_JSON.read_text()).get("rowsUsed", [])
    lower_context = [row for row in lower_rows if 19 <= row["canonicalLineIndex"] <= 23]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Test B3+3 as a bridge/prompt line, not key material.",
        "b3Bridge": b3,
        "allDownSecondStepChecks": bridge_checks,
        "uniqueSecondStepHits": [
            row for row in bridge_checks if (not row["firstUnits"] and row["secondIsHighlightHit"])
        ],
        "contextLines15To23": context_lines,
        "lowerMarkRows19To23": lower_context,
        "assessment": [
            "B3+3 is not a normal highlighted target, but it is not empty noise: it lands on the isolated question `Don't believe me?`.",
            "Repeating B3's own offset once more (`line 19 + 3`) lands on line 22, the orange O4 `buying the dip` highlight.",
            "Among unsupported down-offset landings, this is the only clean second-step highlight bridge.",
            "The line acts more like a prompt/gateway into the El Salvador proof block than a word/letter extraction unit.",
            "Promote B3+3 from unsupported miss to bridge evidence; do not derive keys from the phrase itself.",
        ],
        "nextMove": "Retest the page-76 locator chain with B3+3 treated as a bridge into O4, then see whether the resulting ordered block names a simple extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    image = Image.open(PAGE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 26)
        small = ImageFont.truetype("Arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    colors = {
        "B3": (0, 0, 0, 230),
        "prompt": (35, 95, 240, 230),
        "O4": (255, 128, 0, 230),
    }
    draw_items = [
        ("B3 source", line_info(page, rows, units_map, 16), colors["B3"]),
        ("B3+3 prompt", line_info(page, rows, units_map, 19), colors["prompt"]),
        ("prompt+3 / O4", line_info(page, rows, units_map, 22), colors["O4"]),
    ]
    for label, info, color in draw_items:
        box = info["rowBox"]
        if not box:
            continue
        pad = 10
        rect = [box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad]
        draw.rectangle(rect, outline=color, width=5, fill=(color[0], color[1], color[2], 35))
        draw.text((rect[0], max(0, rect[1] - 28)), label, fill=color, font=small)

    def center(info: dict) -> tuple[float, float] | None:
        box = info["rowBox"]
        if not box:
            return None
        return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

    c1 = center(draw_items[0][1])
    c2 = center(draw_items[1][1])
    c3 = center(draw_items[2][1])
    for a, b, label in ((c1, c2, "+3"), (c2, c3, "+3")):
        if a and b:
            x = min(a[0], b[0]) - 110
            draw.line((x, a[1], x, b[1]), fill=(35, 95, 240, 220), width=6)
            draw.polygon([(x, b[1]), (x - 12, b[1] - 18), (x + 12, b[1] - 18)], fill=(35, 95, 240, 220))
            draw.text((x - 42, (a[1] + b[1]) / 2 - 12), label, fill=(35, 95, 240, 230), font=font)

    crop = image.crop((350, 1400, 2240, 2290))
    crop.save(OUT_OVERLAY, quality=92)

    md = [
        "# B3 Gap Bridge Audit",
        "",
        "Scope: test whether the previously unsupported `B3+3` landing is a true dead miss or a bridge/prompt line. No key candidates, hashes, seed phrases, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        "",
        "## B3 Result",
        "",
        f"- B3 source line `{b3['sourceLine']}`: `{b3['sourceLabel']}`",
        f"- First step, `+{b3['sourceIndex']}` -> line `{b3['firstLine']}`: `{b3['firstText']}`",
        f"- Second step, `+{b3['sourceIndex']}` again -> line `{b3['secondLine']}`: `{b3['secondText']}`",
        f"- Second-step highlighted unit(s): `{', '.join(b3['secondUnits']) or '-'}` / `{', '.join(b3['secondUnitLabels']) or '-'}`",
        "",
        "## Unsupported Down-Offset Second-Step Check",
        "",
        "| source | first landing | first units | second landing | second units |",
        "|---|---|---|---|---|",
    ]
    for row in bridge_checks:
        if row["firstUnits"]:
            continue
        md.append(
            f"| `{row['sourceId']}+{row['sourceIndex']}` | L{row['firstLine']} `{row['firstText'] or '-'}` | "
            f"`{', '.join(row['firstUnits']) or '-'}` | L{row['secondLine']} `{row['secondText'] or '-'}` | "
            f"`{', '.join(row['secondUnits']) or '-'}` |"
        )

    md.extend(["", "## Local Context", "", "| line | units | text |", "|---:|---|---|"])
    for info in context_lines:
        md.append(f"| {info['line']} | `{', '.join(info['units']) or '-'}` | {info['text'] or '(blank)'} |")

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
