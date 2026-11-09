#!/usr/bin/env python3
"""Check whether the dx=-38/-40 repair is supported by the p78 source graphic.

The repaired frame is useful after reflection onto page 76 because it touches
G5 while preserving M3/O5 contacts. This pass asks a narrower source-side
question: does the same repaired frame fit the actual p78 brush/pull-quote
graphic better than the current detected p78 graphic frame?

No OCR extraction, key derivation, hashing, seed checks, WIF checks, or address
checks are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from audit_p78_graphic_pullquote_reflection import detect_graphic_mask
from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge.json"
OUT = ROOT / "analysis_outputs/source_audit/p78_frame_source_side_fit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_source_side_fit.json"
OUT_MD = OUT / "p78_frame_source_side_fit.md"
SHEET = OUT / "p78_frame_source_side_fit_sheet.jpg"


def font(size: int = 18) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def area(box: list[int] | tuple[int, int, int, int]) -> int:
    return max(0, int(box[2]) - int(box[0])) * max(0, int(box[3]) - int(box[1]))


def intersection(a: list[int], b: list[int]) -> list[int] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def mask_pixels(mask: np.ndarray, box: list[int]) -> int:
    x0, y0, x1, y1 = box
    x0 = max(0, min(mask.shape[1], x0))
    x1 = max(0, min(mask.shape[1], x1))
    y0 = max(0, min(mask.shape[0], y0))
    y1 = max(0, min(mask.shape[0], y1))
    if x1 <= x0 or y1 <= y0:
        return 0
    return int(mask[y0:y1, x0:x1].sum())


def summarize_frame(row: dict, graphic_box: list[int], mask: np.ndarray, total_pixels: int) -> dict:
    frame = [int(v) for v in row["p78UprightBox"]]
    inter = intersection(frame, graphic_box)
    frame_pixels = mask_pixels(mask, frame)
    outside_pixels = total_pixels - frame_pixels
    frame_area = area(frame)
    return {
        "name": row["name"],
        "p78UprightBox": frame,
        "p76ReflectedUprightBox": row["p76ReflectedUprightBox"],
        "dx": row["dx"],
        "dy": row["dy"],
        "color": row["color"],
        "intersectionWithDetectedGraphicBox": inter,
        "bboxOverlapVsGraphicBox": round(area(inter) / max(1, area(graphic_box)), 6) if inter else 0.0,
        "graphicMaskPixelsInsideFrame": frame_pixels,
        "graphicMaskPixelsOutsideFrame": outside_pixels,
        "graphicMaskCapture": round(frame_pixels / max(1, total_pixels), 6),
        "frameMaskDensity": round(frame_pixels / max(1, frame_area), 6),
        "sourceFrameOffsetFromDetectedGraphicBox": {
            "left": frame[0] - graphic_box[0],
            "top": frame[1] - graphic_box[1],
            "right": frame[2] - graphic_box[2],
            "bottom": frame[3] - graphic_box[3],
        },
    }


def draw_sheet(img: Image.Image, graphic_box: list[int], rows: list[dict], mask: np.ndarray) -> None:
    crop = [210, 2325, 1415, 3045]
    panel = img.copy().convert("RGBA")
    arr = np.zeros((panel.height, panel.width, 4), dtype=np.uint8)
    arr[mask] = [0, 120, 255, 95]
    panel = Image.alpha_composite(panel, Image.fromarray(arr, "RGBA")).convert("RGB")
    draw = ImageDraw.Draw(panel)
    fnt = font(21)
    title = font(30)
    draw.rectangle(graphic_box, outline="#00d6ff", width=6)
    draw.text((graphic_box[0], max(0, graphic_box[1] - 30)), "detected p78 graphic box", fill="#00d6ff", font=fnt)
    for row in rows:
        draw.rectangle(row["p78UprightBox"], outline=row["color"], width=5)
        draw.text((row["p78UprightBox"][0], max(0, row["p78UprightBox"][1] - 25)), row["name"], fill=row["color"], font=fnt)

    detail_w = 780
    crop_img = panel.crop(tuple(crop))
    sheet = Image.new("RGB", (crop_img.width + detail_w + 60, crop_img.height + 60), (16, 18, 22))
    sheet.paste(crop_img, (24, 42))
    text_draw = ImageDraw.Draw(sheet)
    text_draw.text((24, 10), "p78 source-side frame fit", fill=(238, 242, 247), font=title)
    x = crop_img.width + 44
    y = 44
    for row in rows:
        text_draw.text((x, y), row["name"], fill=row["color"], font=fnt)
        y += 28
        text_draw.text((x, y), f"capture={row['graphicMaskCapture']} density={row['frameMaskDensity']}", fill=(238, 242, 247), font=fnt)
        y += 28
        offsets = row["sourceFrameOffsetFromDetectedGraphicBox"]
        text_draw.text((x, y), f"offset L/T/R/B={offsets['left']}/{offsets['top']}/{offsets['right']}/{offsets['bottom']}", fill=(190, 202, 214), font=fnt)
        y += 42
    sheet.save(SHEET, quality=94)


def main() -> None:
    bridge = json.loads(BRIDGE_JSON.read_text(encoding="utf-8"))
    p78 = upright_image(78).convert("RGB")
    mask, graphic_box_tuple, _ = detect_graphic_mask(p78)
    graphic_box = [int(v) for v in graphic_box_tuple]
    total_pixels = int(mask.sum())
    rows = [summarize_frame(row, graphic_box, mask, total_pixels) for row in bridge["rows"]]
    draw_sheet(p78, graphic_box, rows, mask)

    current = next(row for row in rows if row["name"] == "current")
    repaired = [row for row in rows if row["name"] != "current"]
    source_favors_current = all(current["graphicMaskCapture"] >= row["graphicMaskCapture"] for row in repaired)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 source-side fit of current and dx=-38/-40 repaired frames; no OCR extraction or key derivation",
        "sourceReports": {"bridge": str(BRIDGE_JSON.relative_to(ROOT))},
        "detectedP78GraphicBox": graphic_box,
        "graphicMaskPixels": total_pixels,
        "rows": rows,
        "sheet": str(SHEET.relative_to(ROOT)),
        "summary": {
            "sourceSideFitFavorsCurrentDetectedBox": source_favors_current,
            "currentCapture": current["graphicMaskCapture"],
            "repairedCaptures": {row["name"]: row["graphicMaskCapture"] for row in repaired},
        },
        "assessment": [
            "The current p78 source frame is the detected graphic bounding box and captures the full detected dark graphic mask.",
            "The dx=-38/-40 repaired frames shift the p78 source box right by 38-40 px, losing a small amount of left-side source graphic while adding right-side whitespace.",
            "Therefore dx=-38/-40 is better described as a target-side/source-registration repair that improves the p76 G5/M3/O5 tri-contact, not as a better p78 source-object bounding box.",
            "This does not weaken the repaired frame as a validation signature; it narrows what the repair means.",
        ],
        "nextMove": "Keep current p78 box for source-object detection and dx=-38/-40 for p76 registration validation; do not treat the repair itself as an extraction instruction.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P78 Frame Source-Side Fit Audit",
        "",
        "Scope: compare whether current or dx=-38/-40 repaired p78 frames better fit the actual p78 brush/pull-quote graphic. No OCR extraction, key derivation, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Detected p78 graphic box: `{graphic_box}`",
        f"- Graphic mask pixels: `{total_pixels}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Source-side fit favors current detected box: `{source_favors_current}`",
        "",
        "## Frame Fit",
        "",
        "| frame | p78 upright box | mask capture | mask outside | density | offset from detected L/T/R/B |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        offsets = row["sourceFrameOffsetFromDetectedGraphicBox"]
        lines.append(
            f"| `{row['name']}` | `{row['p78UprightBox']}` | `{row['graphicMaskCapture']}` | `{row['graphicMaskPixelsOutsideFrame']}` | `{row['frameMaskDensity']}` | `{offsets['left']}/{offsets['top']}/{offsets['right']}/{offsets['bottom']}` |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("sourceSideFitFavorsCurrentDetectedBox:", source_favors_current)


if __name__ == "__main__":
    main()
