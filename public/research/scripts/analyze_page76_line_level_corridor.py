#!/usr/bin/env python3
"""Manual line-level audit of the page-76 El Salvador corridor.

This avoids letter-level geometry and broad key transforms. It asks whether the
visible line order, bold fragments, and highlighted line positions in the
strongest page-76 corridor provide a simple selector.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT_MD = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.md"
OUT_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
OUT_IMG = ROOT / "analysis_outputs/source_audit/page76_line_level_corridor.jpg"


CORRIDOR_LINE_RANGE = range(19, 33)
MANUAL_HIGHLIGHTS = {
    22: ["orange: buying the dip"],
    25: ["grey: $1 billion"],
    27: ["grey: Volcano Bonds", "bold: IMF"],
    28: ["bold-partial/full: Mike"],
    29: ["bold-partial: Novogratz"],
    31: ["bold partial: I don't really trust that guy"],
    32: ["orange: shitcoiner at heart"],
}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text)


def clean_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def line_words(page: dict, line_index: int) -> list[dict]:
    return [w for w in page["words"] if w["lineIndex"] == line_index]


def line_record(page: dict, line: dict) -> dict:
    idx = line["lineIndex"]
    text = clean_line(line["text"])
    ws = line_words(page, idx)
    plain_words = words(text)
    bold_letters = "".join(w.get("boldLetters", "") for w in ws)
    partial_bold = "".join(w.get("boldLetters", "") for w in ws if w.get("partialBold"))
    return {
        "lineIndex": idx,
        "corridorIndex": idx - min(CORRIDOR_LINE_RANGE) + 1,
        "text": text,
        "initial": plain_words[0][0] if plain_words else "",
        "lastWord": plain_words[-1] if plain_words else "",
        "lastInitial": plain_words[-1][0] if plain_words else "",
        "wordCount": len(plain_words),
        "boldLetters": bold_letters,
        "partialBoldLetters": partial_bold,
        "highlights": MANUAL_HIGHLIGHTS.get(idx, []),
    }


def draw_corridor_image(records: list[dict]) -> None:
    img = upright_image(76).convert("RGB")
    # Crop the lower corridor where the relevant lines live.
    crop = img.crop((250, 1875, 2220, 3264))
    draw = ImageDraw.Draw(crop)
    try:
        font = ImageFont.truetype("Arial.ttf", 28)
    except Exception:
        font = ImageFont.load_default()

    # Approximate y positions from the high-res scan; this is for visual review,
    # not measurement.
    y_positions = {
        19: 45,
        20: 135,
        21: 220,
        22: 310,
        23: 395,
        24: 485,
        25: 575,
        26: 665,
        27: 750,
        28: 840,
        29: 930,
        30: 1020,
        31: 1110,
        32: 1200,
    }
    for rec in records:
        y = y_positions.get(rec["lineIndex"])
        if y is None:
            continue
        label = f"L{rec['corridorIndex']:02d}/p76:{rec['lineIndex']}"
        color = (255, 80, 0) if rec["highlights"] else (0, 120, 255)
        draw.text((10, y), label, fill=color, font=font)
        draw.line((0, y + 32, crop.width, y + 32), fill=color, width=2)
    crop.save(OUT_IMG, quality=94)


def main() -> None:
    with CANONICAL.open() as f:
        data = json.load(f)
    page = next(p for p in data["pages"].values() if p["articlePage"] == 76)
    records = [line_record(page, page["lines"][idx]) for idx in CORRIDOR_LINE_RANGE]

    streams = {
        "line_initials": "".join(r["initial"] for r in records),
        "line_last_initials": "".join(r["lastInitial"] for r in records),
        "highlighted_corridor_positions": ",".join(str(r["corridorIndex"]) for r in records if r["highlights"]),
        "highlighted_page_line_indexes": ",".join(str(r["lineIndex"]) for r in records if r["highlights"]),
        "highlighted_line_initials": "".join(r["initial"] for r in records if r["highlights"]),
        "highlighted_line_last_initials": "".join(r["lastInitial"] for r in records if r["highlights"]),
        "all_bold_letters": "".join(r["boldLetters"] for r in records),
        "partial_bold_letters": "".join(r["partialBoldLetters"] for r in records),
    }

    result = {
        "source": str(CANONICAL),
        "visual": str(OUT_IMG),
        "lineRange": [min(CORRIDOR_LINE_RANGE), max(CORRIDOR_LINE_RANGE)],
        "streams": streams,
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    draw_corridor_image(records)

    lines = [
        "# Page 76 Line-Level Corridor",
        "",
        "Scope: line-level inspection of the high-signal El Salvador / IMF / buying-the-dip / $1 billion / Volcano Bonds corridor. This checks visible reading order and line units, not private-key formats.",
        "",
        f"- Visual line sheet: `{OUT_IMG}`",
        "",
        "## Streams",
        "",
    ]
    for key, value in streams.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Lines", ""])
    for r in records:
        flags = "; ".join(r["highlights"]) if r["highlights"] else "-"
        lines.append(
            f"- L{r['corridorIndex']:02d} p76:{r['lineIndex']} `{r['text']}` "
            f"initial={r['initial']} last={r['lastWord']} bold=`{r['boldLetters']}` partial=`{r['partialBoldLetters']}` flags={flags}"
        )

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The corridor reads as a coherent narrative chain, not as an instruction: El Salvador -> IMF/Twitter -> buying the dip -> Bukele -> volcanoes -> $1 billion -> Volcano Bonds -> IMF loan -> Mike Novogratz -> distrust -> shitcoiner at heart.",
            "- Line initials, last initials, highlighted-line positions, and bold/partial-bold streams do not form a readable selector.",
            "- The highlighted positions are sparse (`4,7,9,10,11,13,14` in corridor numbering) and do not map cleanly to words or a checksum-like structure.",
            "- This strengthens the conclusion that local digital evidence has reached a selector gap. The next meaningful improvement is external/visual: a physical magazine scan/photo or manual inspection of the original Canva/source clue for an instruction we have not encoded.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()
