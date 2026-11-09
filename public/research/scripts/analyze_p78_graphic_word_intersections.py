#!/usr/bin/env python3
"""Check whether the mirrored p78 graphic selects specific p76 words.

This follows the p78 graphic pull-quote audit. It intersects the mirrored dark
brush/stroke mask and an approximate "negative text hole" mask with page-76 OCR
word boxes. OCR boxes are labels only; exact wording still comes from the
corrected text witness.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from audit_p78_graphic_pullquote_reflection import detect_graphic_mask, hflip_box
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/p78_graphic_word_intersections"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "p78_graphic_word_intersections.json"
OUT_MD = OUT_DIR / "p78_graphic_word_intersections.md"
OVERLAY = OUT_DIR / "p78_graphic_word_intersections_overlay.jpg"


def font(size: int):
    for name in ("Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def mask_close(mask: np.ndarray, size: int = 23) -> np.ndarray:
    img = Image.fromarray((mask * 255).astype(np.uint8))
    closed = img.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.MinFilter(size))
    return np.asarray(closed) > 0


def mask_stats(mask: np.ndarray, box: list[float]) -> tuple[int, float, bool]:
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    h, w = mask.shape
    x1 = max(0, min(w, x1))
    x2 = max(0, min(w, x2))
    y1 = max(0, min(h, y1))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return 0, 0.0, False
    crop = mask[y1:y2, x1:x2]
    pixels = int(crop.sum())
    density = pixels / ((x2 - x1) * (y2 - y1))
    cx = max(0, min(w - 1, int(round((x1 + x2) / 2))))
    cy = max(0, min(h - 1, int(round((y1 + y2) / 2))))
    return pixels, round(density, 6), bool(mask[cy, cx])


def words_on_p76() -> list[dict]:
    data = json.loads(DATA.read_text())
    page = next(page for page in data["pages"] if page["page"] == 76)
    words = []
    for word in page["words"]:
        token = word.get("token") or ""
        if not token:
            continue
        box = word["box"]
        cx, cy = word["center"]
        if 1100 <= cx <= 2300 and 2300 <= cy <= 3050:
            words.append(word)
    return sorted(words, key=lambda item: (item["center"][1], item["center"][0]))


def text_stream(rows: list[dict], limit: int = 40) -> str:
    words = [row["text"] for row in sorted(rows, key=lambda item: (item["center"][1], item["center"][0]))]
    return " ".join(words[:limit])


def draw_overlay(p76: Image.Image, reflected_dark: np.ndarray, hole_mask: np.ndarray, rows: list[dict], reflected_box) -> None:
    out = p76.convert("RGBA")
    arr = np.zeros((out.height, out.width, 4), dtype=np.uint8)
    arr[reflected_dark] = [0, 120, 255, 95]
    arr[hole_mask] = [255, 0, 180, 115]
    out = Image.alpha_composite(out, Image.fromarray(arr, "RGBA"))
    draw = ImageDraw.Draw(out)
    fnt = font(26)
    draw.rectangle(reflected_box, outline=(0, 90, 255, 255), width=5)
    draw.text((reflected_box[0], max(0, reflected_box[1] - 34)), "blue=dark brush, magenta=negative holes", fill=(0, 90, 255, 255), font=fnt)
    for row in rows:
        if row["darkPixels"] <= 0 and row["holePixels"] <= 0:
            continue
        color = (255, 0, 180, 255) if row["holePixels"] >= row["darkPixels"] else (0, 90, 255, 255)
        draw.rectangle(row["box"], outline=color, width=3)
        draw.text((row["box"][0], max(0, row["box"][1] - 26)), row["text"], fill=color, font=fnt)
    out.convert("RGB").save(OVERLAY, quality=94)


def main() -> None:
    p78 = upright_image(78).convert("RGB")
    p76 = upright_image(76).convert("RGB")
    dark_mask, graphic_box, _ = detect_graphic_mask(p78)
    reflected_dark = np.fliplr(dark_mask)
    reflected_box = hflip_box(graphic_box, p78.width)

    closed = mask_close(dark_mask, 23)
    hole_mask = np.fliplr(closed & ~dark_mask)

    rows = []
    for word in words_on_p76():
        dark_pixels, dark_density, dark_center = mask_stats(reflected_dark, word["box"])
        hole_pixels, hole_density, hole_center = mask_stats(hole_mask, word["box"])
        rows.append(
            {
                "index": word["index"],
                "text": word["text"],
                "token": word.get("token", ""),
                "box": [round(v, 2) for v in word["box"]],
                "center": [round(v, 2) for v in word["center"]],
                "darkPixels": dark_pixels,
                "darkDensity": dark_density,
                "darkCenter": dark_center,
                "holePixels": hole_pixels,
                "holeDensity": hole_density,
                "holeCenter": hole_center,
            }
        )

    dark_hits = [row for row in rows if row["darkPixels"] >= 40 or row["darkCenter"]]
    hole_hits = [row for row in rows if row["holePixels"] >= 25 or row["holeCenter"]]
    bbox_words = [
        row
        for row in rows
        if reflected_box[0] <= row["center"][0] <= reflected_box[2]
        and reflected_box[1] <= row["center"][1] <= reflected_box[3]
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Intersect mirrored p78 graphic dark/negative masks with p76 OCR word labels; no key derivation.",
        "sources": {"data": str(DATA)},
        "reflectedBoxOnP76": list(map(int, reflected_box)),
        "overlay": str(OVERLAY),
        "wordRowsConsidered": len(rows),
        "bboxWordCount": len(bbox_words),
        "darkHitCount": len(dark_hits),
        "holeHitCount": len(hole_hits),
        "bboxStream": text_stream(bbox_words),
        "darkHitStream": text_stream(dark_hits),
        "holeHitStream": text_stream(hole_hits),
        "darkHits": dark_hits,
        "holeHits": hole_hits,
        "bboxWords": bbox_words,
        "assessment": [
            "The mirrored graphic does intersect concrete p76 word labels, mostly around the broad sell/earnings/IMF/Mike/Novogratz/distrust corridor.",
            "The dark-mask and negative-hole streams do not produce an instruction; they are broad collision artifacts from the brush graphic.",
            "This strengthens the p76 lower corridor but does not define a precise extraction unit.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    draw_overlay(p76, reflected_dark, hole_mask, rows, reflected_box)

    lines = [
        "# P78 Graphic Word-Intersection Audit",
        "",
        "Scope: intersect the mirrored p78 lower graphic with p76 word labels, using dark brush pixels and approximate negative text holes. OCR boxes are labels only. No key derivation was run.",
        "",
        f"- Reflected p76 box: `{result['reflectedBoxOnP76']}`",
        f"- Overlay: `{OVERLAY}`",
        f"- Words considered: `{len(rows)}`",
        f"- Words inside reflected box: `{len(bbox_words)}`",
        f"- Dark-mask hits: `{len(dark_hits)}`",
        f"- Negative-hole hits: `{len(hole_hits)}`",
        "",
        "## Streams",
        "",
        f"- `bboxStream`: `{result['bboxStream']}`",
        f"- `darkHitStream`: `{result['darkHitStream']}`",
        f"- `holeHitStream`: `{result['holeHitStream']}`",
        "",
        "## Top Dark Hits",
        "",
    ]
    for row in sorted(dark_hits, key=lambda item: (-item["darkPixels"], item["index"]))[:18]:
        lines.append(f"- `{row['text']}` idx `{row['index']}` darkPixels=`{row['darkPixels']}` density=`{row['darkDensity']}` center=`{row['darkCenter']}`")

    lines.extend(["", "## Top Negative-Hole Hits", ""])
    for row in sorted(hole_hits, key=lambda item: (-item["holePixels"], item["index"]))[:18]:
        lines.append(f"- `{row['text']}` idx `{row['index']}` holePixels=`{row['holePixels']}` density=`{row['holeDensity']}` center=`{row['holeCenter']}`")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The mirrored p78 graphic lands on a coherent p76 phrase band: `should sell`, `earnings`, `to pay off the IMF`, `I tagged Mike`, `he could sell`, `but so far he`, `trust that guy`, plus the lower `shitcoiner at heart` OCR blob.",
            "- The dark and hole masks do not select a clean word order or instruction. They are too broad and include visual-art collision.",
            "- Keep this as corroborating evidence for the lower p76 corridor, not as a standalone selector. A future rule would still need to specify whether to read through dark brush, white holes, bounding box, or adjacent words.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(OUT_MD)
    print(OUT_JSON)
    print(OVERLAY)


if __name__ == "__main__":
    main()
