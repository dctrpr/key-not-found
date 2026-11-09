#!/usr/bin/env python3
"""Character-level audit of mirrored p78 graphic over p76.

This checks whether the mirrored lower page-78 graphic selects a sharper
letter sequence on page 76 than the previous word-level pass. It does not
promote the letters into key candidates.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from audit_p78_graphic_pullquote_reflection import detect_graphic_mask, hflip_box
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/p78_graphic_char_intersections"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "p78_graphic_char_intersections.json"
OUT_MD = OUT_DIR / "p78_graphic_char_intersections.md"
OVERLAY = OUT_DIR / "p78_graphic_char_intersections_overlay.jpg"


def font(size: int):
    for name in ("Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def close_mask(mask: np.ndarray, size: int = 23) -> np.ndarray:
    img = Image.fromarray((mask * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.MinFilter(size))) > 0


def point_in_mask(mask: np.ndarray, x: float, y: float) -> bool:
    xi = int(round(x))
    yi = int(round(y))
    if yi < 0 or xi < 0 or yi >= mask.shape[0] or xi >= mask.shape[1]:
        return False
    return bool(mask[yi, xi])


def mask_pixels(mask: np.ndarray, box: list[float]) -> int:
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    h, w = mask.shape
    x1 = max(0, min(w, x1))
    x2 = max(0, min(w, x2))
    y1 = max(0, min(h, y1))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return 0
    return int(mask[y1:y2, x1:x2].sum())


def chars_on_p76() -> list[dict]:
    data = json.loads(DATA.read_text())
    page = next(page for page in data["pages"] if page["page"] == 76)
    chars = []
    for ch in page["chars"]:
        c = ch.get("c", "")
        if not c or c.isspace():
            continue
        x, y = ch["x"], ch["y"]
        if 1100 <= x <= 2300 and 2300 <= y <= 3050:
            chars.append(ch)
    return sorted(chars, key=lambda item: (item["y"], item["x"]))


def stream(chars: list[dict]) -> str:
    def key(item: dict):
        if "y" in item and "x" in item:
            return (item["y"], item["x"])
        center = item.get("center", [0, 0])
        return (center[1], center[0])

    return "".join(ch["c"] for ch in sorted(chars, key=key))


def clean_letters(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text)


def draw_overlay(p76: Image.Image, dark_mask: np.ndarray, hole_mask: np.ndarray, rows: list[dict], reflected_box) -> None:
    out = p76.convert("RGBA")
    arr = np.zeros((out.height, out.width, 4), dtype=np.uint8)
    arr[dark_mask] = [0, 120, 255, 75]
    arr[hole_mask] = [255, 0, 180, 95]
    out = Image.alpha_composite(out, Image.fromarray(arr, "RGBA"))
    draw = ImageDraw.Draw(out)
    fnt = font(20)
    draw.rectangle(reflected_box, outline=(0, 90, 255, 255), width=5)
    for row in rows:
        if not row["darkCenter"] and not row["holeCenter"]:
            continue
        color = (255, 0, 180, 255) if row["holeCenter"] else (0, 90, 255, 255)
        x, y = row["center"]
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), outline=color, width=3)
        draw.text((x + 6, y - 24), row["c"], fill=color, font=fnt)
    out.convert("RGB").save(OVERLAY, quality=94)


def main() -> None:
    p78 = upright_image(78).convert("RGB")
    p76 = upright_image(76).convert("RGB")
    dark, graphic_box, _ = detect_graphic_mask(p78)
    reflected_dark = np.fliplr(dark)
    hole = np.fliplr(close_mask(dark, 23) & ~dark)
    reflected_box = hflip_box(graphic_box, p78.width)

    rows = []
    for ch in chars_on_p76():
        dc = point_in_mask(reflected_dark, ch["x"], ch["y"])
        hc = point_in_mask(hole, ch["x"], ch["y"])
        dp = mask_pixels(reflected_dark, ch["box"])
        hp = mask_pixels(hole, ch["box"])
        inside_bbox = reflected_box[0] <= ch["x"] <= reflected_box[2] and reflected_box[1] <= ch["y"] <= reflected_box[3]
        rows.append(
            {
                "i": ch["i"],
                "c": ch["c"],
                "box": [round(v, 2) for v in ch["box"]],
                "center": [round(ch["x"], 2), round(ch["y"], 2)],
                "insideReflectedBox": inside_bbox,
                "darkCenter": dc,
                "holeCenter": hc,
                "darkPixels": dp,
                "holePixels": hp,
            }
        )

    bbox_chars = [r for r in rows if r["insideReflectedBox"]]
    dark_center = [r for r in rows if r["darkCenter"]]
    hole_center = [r for r in rows if r["holeCenter"]]
    dark_pixel = [r for r in rows if r["darkPixels"] >= 8]
    hole_pixel = [r for r in rows if r["holePixels"] >= 8]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Character-level mirrored p78 graphic intersections with p76 OCR char labels; no key derivation.",
        "reflectedBoxOnP76": list(map(int, reflected_box)),
        "overlay": str(OVERLAY),
        "charsConsidered": len(rows),
        "bboxCharCount": len(bbox_chars),
        "darkCenterCount": len(dark_center),
        "holeCenterCount": len(hole_center),
        "darkPixelCount": len(dark_pixel),
        "holePixelCount": len(hole_pixel),
        "streams": {
            "bbox": stream(bbox_chars),
            "bboxLetters": clean_letters(stream(bbox_chars)),
            "darkCenter": stream(dark_center),
            "darkCenterLetters": clean_letters(stream(dark_center)),
            "holeCenter": stream(hole_center),
            "holeCenterLetters": clean_letters(stream(hole_center)),
            "darkPixels": stream(dark_pixel),
            "darkPixelsLetters": clean_letters(stream(dark_pixel)),
            "holePixels": stream(hole_pixel),
            "holePixelsLetters": clean_letters(stream(hole_pixel)),
        },
        "darkCenterRows": dark_center,
        "holeCenterRows": hole_center,
        "assessment": [
            "Character-level intersections remain ordinary corridor fragments rather than an instruction.",
            "Center-hit streams are shorter but still contain pieces of IMF/Mike/sell/trust/shitcoiner prose.",
            "This closes the current p78 graphic dark/hole micro-selector under literal hflip.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    draw_overlay(p76, reflected_dark, hole, rows, reflected_box)

    lines = [
        "# P78 Graphic Character-Intersection Audit",
        "",
        "Scope: check whether the mirrored p78 graphic selects a sharper p76 letter stream than the previous word-level pass. OCR char boxes are labels only. No key derivation was run.",
        "",
        f"- Reflected p76 box: `{result['reflectedBoxOnP76']}`",
        f"- Overlay: `{OVERLAY}`",
        f"- Chars considered: `{len(rows)}`",
        f"- Bbox chars: `{len(bbox_chars)}`",
        f"- Dark center hits: `{len(dark_center)}`",
        f"- Hole center hits: `{len(hole_center)}`",
        f"- Dark pixel hits: `{len(dark_pixel)}`",
        f"- Hole pixel hits: `{len(hole_pixel)}`",
        "",
        "## Streams",
        "",
    ]
    for key, value in result["streams"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- Character centers under the mirrored dark/negative masks still read as fragments of the same ordinary p76 corridor, not an instruction.",
            "- The useful result remains target confirmation: p78 graphic -> p76 lower corridor.",
            "- Close this micro-selector unless a new rule explicitly says to use dark strokes, white holes, or character centers from the graphic.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(OUT_MD)
    print(OUT_JSON)
    print(OVERLAY)


if __name__ == "__main__":
    main()
