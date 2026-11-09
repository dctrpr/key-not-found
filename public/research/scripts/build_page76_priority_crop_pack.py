#!/usr/bin/env python3
"""Build a high-res crop pack for the current page-76 target priorities.

This prepares visual baselines for future source/physical/Canva comparison.
It does not generate secrets, hashes, or wallet candidates.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
CHOOSER_PATH = ROOT / "analysis_outputs/source_audit/page76_next_target_chooser/page76_next_target_chooser.json"
FRAME_PATH = ROOT / "analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack"
OUT_JSON = OUT_DIR / "page76_priority_crop_pack.json"
OUT_MD = OUT_DIR / "page76_priority_crop_pack.md"
SHEET_PATH = OUT_DIR / "page76_priority_crop_sheet.jpg"


TARGETS = [
    {
        "id": "L32_O5_primary",
        "title": "Primary O5 / L32",
        "lineIndex": 32,
        "text": "Maybe because he's a shitcoiner at heart.",
        "crop": [850, 2860, 1770, 3038],
        "boxes": [
            {"label": "O5 shitcoiner at heart", "box": [1040, 2932, 1661, 2982], "color": "#ff9b2e"},
        ],
    },
    {
        "id": "L27_G5_pair",
        "title": "Paired G5 / L27",
        "lineIndex": 27,
        "text": "collateralized Volcano Bonds to pay off the IMF",
        "crop": [720, 2505, 1650, 2625],
        "boxes": [
            {"label": "G5 Volcano Bonds", "box": [795, 2544, 1196, 2592], "color": "#8f98a5"},
            {"label": "pay off the IMF", "box": [1278.51, 2535.36, 1607.19, 2579.93], "color": "#55d6ff"},
        ],
    },
    {
        "id": "L25_should_sell",
        "title": "Frame Top / L25",
        "lineIndex": 25,
        "text": "$1 billion in bitcoin - that he should sell",
        "crop": [720, 2355, 1515, 2455],
        "boxes": [
            {"label": "should sell", "box": [1201.11, 2393.42, 1439.33, 2433.53], "color": "#ff5ebc"},
        ],
    },
    {
        "id": "L26_L29_source_band",
        "title": "Broad p78 Source Band / L26-L29",
        "lineIndex": "26-29",
        "text": "earnings / Volcano Bonds / Mike / could sell band",
        "crop": [720, 2440, 1685, 2745],
        "boxes": [
            {"label": "earnings", "box": [1222.22, 2467.15, 1398.23, 2507.26], "color": "#ff5ebc"},
            {"label": "G5 Volcano Bonds", "box": [795, 2544, 1196, 2592], "color": "#8f98a5"},
            {"label": "I tagged Mike", "box": [1258.41, 2609.09, 1542.06, 2653.65], "color": "#55d6ff"},
            {"label": "could sell", "box": [1285.54, 2686.2, 1531.3, 2726.31], "color": "#55d6ff"},
        ],
    },
    {
        "id": "L25_L32_frame_context",
        "title": "Full Frame Context / L25-L32",
        "lineIndex": "25-32",
        "text": "should sell -> Volcano Bonds -> shitcoiner at heart",
        "crop": [720, 2350, 1750, 3045],
        "boxes": [
            {"label": "should sell", "box": [1201.11, 2393.42, 1439.33, 2433.53], "color": "#ff5ebc"},
            {"label": "G5 Volcano Bonds", "box": [795, 2544, 1196, 2592], "color": "#8f98a5"},
            {"label": "O5 shitcoiner at heart", "box": [1040, 2932, 1661, 2982], "color": "#ff9b2e"},
        ],
    },
]


def font(size: int = 24) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def clamp_crop(crop: list[int], width: int, height: int) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = [int(round(v)) for v in crop]
    return max(0, x1), max(0, y1), min(width, x2), min(height, y2)


def draw_box(draw: ImageDraw.ImageDraw, crop: tuple[int, int, int, int], box: list[float], color: str, label: str, fnt: ImageFont.ImageFont) -> None:
    x1, y1, _, _ = crop
    bx1, by1, bx2, by2 = [int(round(v)) for v in box]
    local = [bx1 - x1, by1 - y1, bx2 - x1, by2 - y1]
    draw.rectangle(local, outline=color, width=4)
    tx, ty = local[0], max(0, local[1] - 24)
    bbox = draw.textbbox((tx, ty), label, font=fnt)
    draw.rectangle([bbox[0] - 3, bbox[1] - 2, bbox[2] + 3, bbox[3] + 2], fill=(12, 15, 20))
    draw.text((tx, ty), label, fill=color, font=fnt)


def draw_frame_lines(draw: ImageDraw.ImageDraw, crop: tuple[int, int, int, int], frame: list[float]) -> None:
    x1, y1, x2, y2 = crop
    fx1, fy1, fx2, fy2 = frame
    # Draw only frame edges that intersect this crop.
    color = "#55d6ff"
    if x1 <= fx1 <= x2:
      draw.line([(fx1 - x1, max(0, fy1 - y1)), (fx1 - x1, min(y2 - y1, fy2 - y1))], fill=color, width=3)
    if y1 <= fy1 <= y2:
      draw.line([(max(0, fx1 - x1), fy1 - y1), (min(x2 - x1, fx2 - x1), fy1 - y1)], fill=color, width=3)
    if y1 <= fy2 <= y2:
      draw.line([(max(0, fx1 - x1), fy2 - y1), (min(x2 - x1, fx2 - x1), fy2 - y1)], fill=color, width=3)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(PAGE_PATH).convert("RGB")
    chooser = json.loads(CHOOSER_PATH.read_text())
    frame = json.loads(FRAME_PATH.read_text())["reflectedP78BoxOnP76"]
    fnt = font(18)
    title_font = font(28)
    small_font = font(16)

    crop_entries = []
    rendered = []
    for target in TARGETS:
        crop = clamp_crop(target["crop"], source.width, source.height)
        img = source.crop(crop).convert("RGB")
        overlay = ImageDraw.Draw(img)
        draw_frame_lines(overlay, crop, frame)
        for item in target["boxes"]:
            draw_box(overlay, crop, item["box"], item["color"], item["label"], fnt)
        out_path = OUT_DIR / f"{target['id']}.jpg"
        img.save(out_path, quality=94)
        crop_entries.append(
            {
                "id": target["id"],
                "title": target["title"],
                "lineIndex": target["lineIndex"],
                "text": target["text"],
                "crop": list(crop),
                "output": str(out_path.relative_to(ROOT)),
                "boxes": target["boxes"],
            }
        )
        rendered.append((target, img))

    sheet_width = 1500
    margin = 24
    panel_gap = 24
    scaled_panels = []
    for target, img in rendered:
        max_w = sheet_width - margin * 2
        scale = min(1.0, max_w / img.width)
        scaled = img.resize((int(img.width * scale), int(img.height * scale)))
        scaled_panels.append((target, scaled))

    sheet_height = margin
    for _, img in scaled_panels:
        sheet_height += 70 + img.height + panel_gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), (16, 18, 22))
    draw = ImageDraw.Draw(sheet)
    y = margin
    for target, img in scaled_panels:
        draw.text((margin, y), f"{target['title']} - {target['text']}", fill=(237, 241, 245), font=title_font)
        draw.text((margin, y + 36), f"crop {target['crop']}", fill=(154, 168, 183), font=small_font)
        y += 70
        sheet.paste(img, (margin, y))
        y += img.height + panel_gap
    sheet.save(SHEET_PATH, quality=94)

    report = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "High-res crop pack for current page-76 priority targets; no key derivation.",
        "sourceImage": str(PAGE_PATH.relative_to(ROOT)),
        "decisionSource": str(CHOOSER_PATH.relative_to(ROOT)),
        "frameSource": str(FRAME_PATH.relative_to(ROOT)),
        "targetPriority": chooser["decision"],
        "reflectedP78FrameOnP76": frame,
        "sheet": str(SHEET_PATH.relative_to(ROOT)),
        "crops": crop_entries,
        "assessment": [
            "This crop pack is a visual baseline for future source/physical/Canva comparisons.",
            "O5/L32 remains the primary visual target, G5/L27 is the paired target, and L26-L29 is the broad p78 source band.",
            "The crop pack does not define an extraction unit and should not trigger key derivation by itself.",
        ],
        "nextMove": "If a new source image appears, compare these exact crops first and require a named extraction unit before trying keys.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        "# Page 76 Priority Crop Pack",
        "",
        "Scope: create high-res visual baselines for the current page-76 priority targets. No key derivation, hashing, seed phrases, WIF checks, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{report['createdAt']}`",
        f"- Source image: `{report['sourceImage']}`",
        f"- Contact sheet: `{report['sheet']}`",
        "",
        "## Target Priority",
        "",
        f"- Primary: L32/O5 `{chooser['decision']['primaryManualTarget']['text']}`.",
        f"- Pair: L27/G5 `{chooser['decision']['pairedTarget']['text']}`.",
        f"- Broad source band: L26-L29 around `{chooser['decision']['sourceBandTarget']['text']}`.",
        "",
        "## Crops",
        "",
    ]
    for entry in crop_entries:
        md.extend(
            [
                f"### {entry['title']}",
                f"- id: `{entry['id']}`",
                f"- line: `{entry['lineIndex']}`",
                f"- text: `{entry['text']}`",
                f"- crop: `{entry['crop']}`",
                f"- output: `{entry['output']}`",
                "",
            ]
        )
    md.extend(
        [
            "## Assessment",
            "",
            "- The crop pack turns the current line priority into a repeatable visual baseline.",
            "- It does not solve the selector gap. Use it only to compare future source/original-layout/physical imagery.",
            "- The p78 reflected frame edges are drawn in cyan where they intersect each crop, so a new source can be tested against the same O5/G5/frame signature.",
            "",
            "## Next Move",
            "",
            "- If a new source appears, compare O5/L32 first, G5/L27 second, and then the L26-L29 band. Require a named extraction unit before key checks resume.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET_PATH}")


if __name__ == "__main__":
    main()
