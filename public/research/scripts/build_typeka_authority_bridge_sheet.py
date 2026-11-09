#!/usr/bin/env python3
"""Build a visual Typeka/font authority bridge for the page-76 corridor."""

from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DISAMBIG = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json"
CROP_DIR = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack"
OUT_DIR = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation"
OUT_JSON = OUT_DIR / "typeka_authority_bridge_sheet.json"
OUT_MD = OUT_DIR / "typeka_authority_bridge_sheet.md"
OUT_IMG = OUT_DIR / "typeka_authority_bridge_sheet.jpg"


PANELS = [
    {
        "id": "L25_should_sell",
        "crop": CROP_DIR / "L25_should_sell.jpg",
        "title": "L25: $1 billion / should sell",
        "targetIds": ["one_billion", "should_sell"],
        "summary": "$1 billion is DOCM-bold + black-highlighted; Markdown missed it. should sell is regular.",
    },
    {
        "id": "L27_G5_pair",
        "crop": CROP_DIR / "L27_G5_pair.jpg",
        "title": "L27/G5: Volcano Bonds / IMF loan",
        "targetIds": ["volcano_bonds", "imf_loan"],
        "summary": "Volcano Bonds is DOCM-bold + black-highlighted; Markdown missed it.",
    },
    {
        "id": "L26_L29_source_band",
        "crop": CROP_DIR / "L26_L29_source_band.jpg",
        "title": "L26-L29: source band",
        "targetIds": ["future_bitcoin_earnings", "tagged_mike", "novogratz"],
        "summary": "Future earnings is regular; Mike/Novogratz contains Typeka Mix nearby context.",
    },
    {
        "id": "L32_O5_primary",
        "crop": CROP_DIR / "L32_O5_primary.jpg",
        "title": "L32/O5: shitcoiner at heart",
        "targetIds": ["shitcoiner_heart"],
        "summary": "O5 is DOCM-bold + yellow-highlighted and also Markdown-bold.",
    },
    {
        "id": "L25_L32_frame_context",
        "crop": CROP_DIR / "L25_L32_frame_context.jpg",
        "title": "Frame context: should sell -> Volcano Bonds -> O5",
        "targetIds": ["should_sell", "volcano_bonds", "shitcoiner_heart", "trust_that_guy"],
        "summary": "The compact p78-frame benchmark is R-K-Y; Typeka Mix lands nearby, not on the G5/O5 pair.",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def row_lookup(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in data["rows"]}


def state_line(row: dict[str, Any]) -> str:
    docm = row["docm"]
    md = row["markdown"]
    highlights = docm.get("highlights", {})
    hl = ", ".join(f"{key}:{value}" for key, value in highlights.items()) or "none"
    return (
        f"{row['phrase']}: font={docm.get('dominantFont')}; "
        f"bold={docm.get('boldFraction')}; mix={docm.get('mixFraction')}; "
        f"highlight={hl}; mdBold={md.get('boldFraction')}"
    )


def fit_crop(path: Path, width: int, height: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), "white")
    x = (width - img.width) // 2
    y = (height - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], fnt: ImageFont.ImageFont, fill: str, max_chars: int, line_h: int) -> int:
    x, y = xy
    for line in textwrap.wrap(text, width=max_chars, break_long_words=False):
        draw.text((x, y), line, fill=fill, font=fnt)
        y += line_h
    return y


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(DISAMBIG.read_text())
    rows = row_lookup(data)

    sheet_w = 1900
    crop_w = 860
    crop_h = 260
    row_h = 330
    margin = 36
    header_h = 124
    sheet_h = header_h + row_h * len(PANELS) + margin
    img = Image.new("RGB", (sheet_w, sheet_h), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    title_font = font(38, bold=True)
    label_font = font(25, bold=True)
    body_font = font(22)
    small_font = font(18)

    draw.text((margin, 28), "Typeka / Bold Authority Bridge", fill=(20, 28, 38), font=title_font)
    draw.text(
        (margin, 78),
        "Use DOCM font/highlight states for typography. Markdown bold is annotation-only. No key extraction here.",
        fill=(76, 88, 103),
        font=body_font,
    )

    panel_records = []
    for idx, panel in enumerate(PANELS):
        y = header_h + idx * row_h
        draw.rounded_rectangle((margin, y + 12, sheet_w - margin, y + row_h - 14), radius=8, fill="white", outline=(220, 226, 235))
        crop = fit_crop(panel["crop"], crop_w, crop_h)
        img.paste(crop, (margin + 18, y + 36))
        x_text = margin + 18 + crop_w + 30
        y_text = y + 34
        draw.text((x_text, y_text), panel["title"], fill=(18, 24, 32), font=label_font)
        y_text += 38
        y_text = draw_wrapped(draw, panel["summary"], (x_text, y_text), body_font, (45, 55, 72), 72, 28)
        y_text += 6

        target_records = []
        for target_id in panel["targetIds"]:
            row = rows[target_id]
            line = state_line(row)
            y_text = draw_wrapped(draw, "- " + line, (x_text, y_text), small_font, (70, 82, 98), 96, 23)
            target_records.append(
                {
                    "id": target_id,
                    "phrase": row["phrase"],
                    "docmDominantFont": row["docm"].get("dominantFont"),
                    "docmBoldFraction": row["docm"].get("boldFraction"),
                    "docmMixFraction": row["docm"].get("mixFraction"),
                    "docmHighlights": row["docm"].get("highlights"),
                    "markdownBoldFraction": row["markdown"].get("boldFraction"),
                }
            )
        panel_records.append({**panel, "crop": str(panel["crop"].relative_to(ROOT)), "targets": target_records})

    img.save(OUT_IMG, quality=92)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "visual bridge from page-76 priority crops to DOCM Typeka/bold/highlight authority; no key derivation",
        "sheet": str(OUT_IMG.relative_to(ROOT)),
        "sourceAudit": str(DISAMBIG.relative_to(ROOT)),
        "panels": panel_records,
        "assessment": [
            "The active visual targets should be inspected with DOCM font/highlight states, not the old Markdown-bold layer.",
            "$1 billion and Volcano Bonds are bold/black in DOCM even though Markdown did not mark them bold.",
            "Typeka Mix is real but appears as nearby contextual styling, not as the G5/O5 target style.",
        ],
        "decision": "Use this sheet next to the 3D viewer and page-76 crop pack when checking typography around the lower corridor.",
        "nextMove": "Continue source-gated geometry validation; do not reopen font extraction without a clue naming font or selected units.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Typeka Authority Bridge Sheet",
        "",
        "Scope: visual bridge from page-76 priority crops to DOCM Typeka/bold/highlight states. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Sheet: `{OUT_IMG.relative_to(ROOT)}`",
        f"- Source audit: `{DISAMBIG.relative_to(ROOT)}`",
        "",
        "## Panels",
        "",
    ]
    for panel in panel_records:
        lines.append(f"### {panel['id']}")
        lines.append(f"- Crop: `{panel['crop']}`")
        lines.append(f"- Summary: {panel['summary']}")
        for target in panel["targets"]:
            lines.append(
                f"- `{target['phrase']}`: font `{target['docmDominantFont']}`, "
                f"bold `{target['docmBoldFraction']}`, mix `{target['docmMixFraction']}`, "
                f"highlight `{target['docmHighlights']}`, markdown bold `{target['markdownBoldFraction']}`."
            )
        lines.append("")
    lines.extend(
        [
            "## Decision",
            "",
            "- Use this sheet next to the 3D viewer and page-76 crop pack when checking the lower corridor.",
            "- Markdown bold remains annotation-only; DOCM states are the formatting witness.",
            "- This is a guardrail artifact, not extraction evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_IMG}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
