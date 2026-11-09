#!/usr/bin/env python3
"""Build a page-76 lower-corridor overlay with typography authority.

This is a visual inspection artifact. It puts DOCM font/highlight states,
trusted phrase boxes, row guides, and the lower standalone marks on the same
page-76 source crop. It does not derive or check keys.
"""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PAGE_IMG = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
TYPEKA = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json"
MARKS = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_typography_overlay"
OUT_IMG = OUT_DIR / "page76_typography_overlay.jpg"
OUT_JSON = OUT_DIR / "page76_typography_overlay.json"
OUT_MD = OUT_DIR / "page76_typography_overlay.md"

CROP = (360, 2108, 2544, 3218)
MARGIN = 38
HEADER_H = 112
LEGEND_W = 760


TARGETS = [
    {
        "id": "buying_dip",
        "label": '"buying the dip"',
        "boxes": [[1328, 2160, 1760, 2226]],
        "note": "orange/DOCM-bold phrase; OCR word is corrupted in 3D map",
    },
    {
        "id": "one_billion",
        "label": "$1 billion",
        "boxes": [[430, 2400, 690, 2447]],
        "note": "DOCM-bold + black highlight; Markdown missed bold",
    },
    {
        "id": "should_sell",
        "label": "should sell",
        "wordTokens": ["should", "sell"],
        "note": "regular phrase immediately after the $1 billion anchor",
    },
    {
        "id": "future_bitcoin_earnings",
        "label": "future bitcoin earnings",
        "wordTokens": ["future", "bitcoin", "earnings"],
        "note": "regular bridge between amount and G5",
    },
    {
        "id": "volcano_bonds",
        "label": "Volcano Bonds",
        "boxes": [[795, 2544, 1196, 2592]],
        "note": "DOCM-bold + black highlight; Markdown missed bold",
    },
    {
        "id": "imf_loan",
        "label": "IMF loan",
        "boxes": [[1540, 2535, 1608, 2580], [485, 2609, 570, 2654]],
        "note": "wraps across the next line; mostly DOCM-bold",
    },
    {
        "id": "tagged_mike",
        "label": "I tagged Mike",
        "wordTokens": ["i", "tagged", "mike"],
        "note": "contains some Typeka Mix but is not highlighted",
    },
    {
        "id": "novogratz",
        "label": "Novogratz",
        "wordTokens": ["novogratz"],
        "note": "Typeka Mix nearby context, not a highlight target",
    },
    {
        "id": "trust_that_guy",
        "label": "I don't really trust that guy",
        "wordTokens": ["i", "dont", "really", "trust", "that", "guy"],
        "note": "Typeka Mix nearby context, not DOCM-bold",
    },
    {
        "id": "shitcoiner_heart",
        "label": "shitcoiner at heart",
        "boxes": [[1040, 2932, 1661, 2982]],
        "note": "O5 primary target; DOCM-bold + orange/yellow highlight",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_page_words() -> list[dict[str, Any]]:
    data = json.loads(ARTICLE_MAP.read_text(encoding="utf-8"))
    page = next(item for item in data["pages"] if item["page"] == 76)
    return page["words"]


def target_box_from_words(words: list[dict[str, Any]], tokens: list[str], y_min: float = CROP[1], y_max: float = CROP[3]) -> list[float] | None:
    candidates = [word for word in words if y_min <= word["center"][1] <= y_max]
    for idx in range(len(candidates) - len(tokens) + 1):
        window = candidates[idx : idx + len(tokens)]
        if [word["token"] for word in window] == tokens:
            return [
                min(word["box"][0] for word in window),
                min(word["box"][1] for word in window),
                max(word["box"][2] for word in window),
                max(word["box"][3] for word in window),
            ]
    return None


def adjusted(box: list[float]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (
        int(round(MARGIN + x1 - CROP[0])),
        int(round(HEADER_H + MARGIN + y1 - CROP[1])),
        int(round(MARGIN + x2 - CROP[0])),
        int(round(HEADER_H + MARGIN + y2 - CROP[1])),
    )


def style_for(row: dict[str, Any]) -> dict[str, Any]:
    docm = row["docm"]
    highlights = docm.get("highlights", {})
    if "black" in highlights:
        fill = (35, 42, 52, 92)
        outline = (20, 25, 31)
        tag = "black highlight"
    elif "yellow" in highlights:
        fill = (255, 147, 38, 105)
        outline = (225, 91, 0)
        tag = "orange/yellow highlight"
    elif docm.get("mixFraction", 0) >= 0.5:
        fill = (36, 117, 206, 82)
        outline = (18, 83, 165)
        tag = "Typeka Mix"
    else:
        fill = (123, 132, 148, 62)
        outline = (87, 96, 112)
        tag = "regular Typeka"
    return {"fill": fill, "outline": outline, "tag": tag, "bold": docm.get("boldFraction", 0) > 0.5}


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width_chars: int, fnt: ImageFont.ImageFont, fill: tuple[int, int, int]) -> int:
    x, y = xy
    for line in textwrap.wrap(text, width=width_chars, break_long_words=False):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += 24
    return y


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = Image.open(PAGE_IMG).convert("RGB")
    crop = base.crop(CROP)
    crop_w, crop_h = crop.size
    sheet_w = crop_w + LEGEND_W + MARGIN * 3
    sheet_h = crop_h + HEADER_H + MARGIN * 2
    sheet = Image.new("RGB", (sheet_w, sheet_h), (247, 249, 252))
    sheet.paste(crop, (MARGIN, HEADER_H + MARGIN))

    overlay = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text_draw = ImageDraw.Draw(sheet)
    title_font = font(34, True)
    label_font = font(18, True)
    small_font = font(17)
    tiny_font = font(14)

    text_draw.text((MARGIN, 30), "Page 76 Lower Corridor: Typography + Visual Marks", font=title_font, fill=(20, 26, 34))
    text_draw.text(
        (MARGIN, 74),
        "DOCM font/highlight authority overlaid on the source-faithful page crop. This is inspection evidence only.",
        font=small_font,
        fill=(83, 93, 108),
    )

    typeka_data = json.loads(TYPEKA.read_text(encoding="utf-8"))
    typeka_by_id = {row["id"]: row for row in typeka_data["rows"]}
    words = load_page_words()
    marks = json.loads(MARKS.read_text(encoding="utf-8"))

    target_records = []
    for row in marks["rowsUsed"]:
        y = row["y"]
        if CROP[1] <= y <= CROP[3]:
            y_adj = HEADER_H + MARGIN + y - CROP[1]
            color = (225, 127, 36, 170) if row["highlight"] else (134, 145, 160, 95)
            draw.line([(MARGIN, y_adj), (MARGIN + crop_w, y_adj)], fill=color, width=1)
            text_draw.text((MARGIN + 8, int(y_adj - 18)), f"L{row['canonicalLineIndex']}", font=tiny_font, fill=(78, 88, 102))

    for target in TARGETS:
        boxes = target.get("boxes")
        if boxes is None:
            box = target_box_from_words(words, target["wordTokens"])
            boxes = [box] if box else []
        row = typeka_by_id[target["id"]]
        style = style_for(row)
        for box in boxes:
            if not box:
                continue
            x1, y1, x2, y2 = adjusted(box)
            draw.rounded_rectangle((x1, y1, x2, y2), radius=5, fill=style["fill"], outline=style["outline"], width=4 if style["bold"] else 2)
            text_draw.text((x1, max(HEADER_H + MARGIN, y1 - 20)), target["label"], font=tiny_font, fill=style["outline"])
        target_records.append(
            {
                "id": target["id"],
                "label": target["label"],
                "boxes": boxes,
                "styleTag": style["tag"],
                "docmDominantFont": row["docm"].get("dominantFont"),
                "docmBoldFraction": row["docm"].get("boldFraction"),
                "docmMixFraction": row["docm"].get("mixFraction"),
                "docmHighlights": row["docm"].get("highlights"),
                "note": target["note"],
            }
        )

    mark_records = []
    for analysis in marks["analyses"]:
        if analysis.get("classification") != "standalone-mark":
            continue
        box = analysis["box"]
        x1, y1, x2, y2 = adjusted(box)
        draw.rectangle((x1, y1, x2, y2), outline=(122, 65, 176, 230), width=5)
        text_draw.text((x1, max(HEADER_H + MARGIN, y1 - 24)), f"M{analysis['index']} standalone", font=label_font, fill=(94, 44, 145))
        mark_records.append(
            {
                "index": analysis["index"],
                "box": box,
                "axis": analysis.get("axis"),
                "closestRows": [row["canonicalLineIndex"] for row in analysis.get("rowHits", {}).get("closestRows", [])],
            }
        )

    sheet = Image.alpha_composite(sheet.convert("RGBA"), overlay).convert("RGB")
    text_draw = ImageDraw.Draw(sheet)
    legend_x = MARGIN * 2 + crop_w
    text_draw.rounded_rectangle((legend_x, HEADER_H + MARGIN, sheet_w - MARGIN, sheet_h - MARGIN), radius=8, fill=(255, 255, 255), outline=(220, 226, 234))
    yy = HEADER_H + MARGIN + 24
    text_draw.text((legend_x + 24, yy), "Inspection Reading", font=font(25, True), fill=(23, 31, 42))
    yy += 42
    points = [
        "The black/DOCM-bold anchors are $1 billion and Volcano Bonds.",
        "The orange/DOCM-bold anchors are buying the dip and shitcoiner at heart.",
        "Typeka Mix is visible in Novogratz / trust-that-guy context, not on the G5/O5 target pair.",
        "M3 brackets the Novogratz/trust rows from the right; M4 sits below, nearest O5.",
        "No clean next unit/order appears from typography alone.",
    ]
    for point in points:
        yy = draw_wrapped(text_draw, "- " + point, (legend_x + 24, yy), 54, small_font, (54, 64, 78))
        yy += 8
    yy += 12
    text_draw.text((legend_x + 24, yy), "Color key", font=font(21, True), fill=(23, 31, 42))
    yy += 34
    swatches = [
        ((35, 42, 52), "black highlight + DOCM-bold"),
        ((225, 91, 0), "orange/yellow highlight + DOCM-bold"),
        ((18, 83, 165), "Typeka Mix nearby context"),
        ((87, 96, 112), "regular Typeka context"),
        ((122, 65, 176), "standalone visual mark"),
    ]
    for color, label in swatches:
        text_draw.rectangle((legend_x + 26, yy + 3, legend_x + 52, yy + 24), fill=color)
        text_draw.text((legend_x + 64, yy), label, font=small_font, fill=(62, 72, 84))
        yy += 32

    sheet.save(OUT_IMG, quality=94)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 lower-corridor visual overlay of trusted phrase boxes, DOCM typography states, row guides, and standalone marks; no key derivation",
        "sourceImage": str(PAGE_IMG.relative_to(ROOT)),
        "crop": CROP,
        "sheet": str(OUT_IMG.relative_to(ROOT)),
        "typekaSource": str(TYPEKA.relative_to(ROOT)),
        "markSource": str(MARKS.relative_to(ROOT)),
        "targets": target_records,
        "standaloneMarks": mark_records,
        "findings": [
            "$1 billion and Volcano Bonds remain the black-highlighted DOCM-bold anchors in this corridor.",
            "buying the dip and shitcoiner at heart remain the orange/yellow DOCM-bold anchors.",
            "Typeka Mix sits on nearby context, especially Novogratz and I don't really trust that guy; it does not align as a clean G5/O5 selector.",
            "M3 and M4 support the lower-corridor bracket visually, but this overlay still does not expose a human-readable unit/order rule.",
        ],
        "decision": "Keep this overlay as the active visual inspection map for page 76, but do not promote typography alone to extraction evidence.",
        "nextMove": "Use the overlay to compare future physical/source imagery; otherwise move to a small source-gated adjacency test around the four anchored phrases.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page 76 Typography Overlay",
        "",
        "Scope: page-76 lower-corridor visual overlay of trusted phrase boxes, DOCM typography states, row guides, and standalone marks. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Source image: `{result['sourceImage']}`",
        f"- Typeka source: `{result['typekaSource']}`",
        f"- Mark source: `{result['markSource']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in result["findings"]:
        lines.append(f"- {finding}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Typography is now visible directly on the page-76 corridor, so future visual inspection does not have to mentally combine separate crop sheets.",
            "- The overlay strengthens the source/fidelity guardrail but does not provide the missing selector.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_IMG}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
