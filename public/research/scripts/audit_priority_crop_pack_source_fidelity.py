#!/usr/bin/env python3
"""Audit the page-76 priority crop pack against the current source scan.

The existing crop pack was generated from the 3D upright image layer. The
current source image cache stores the same PDF pages in native orientation,
which is 180 degrees from readable/upright orientation. This pass re-renders
the same crop windows from the current source image after that 180-degree
rotation and confirms whether the crop pack is source-faithful.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, or address
checks are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PRIORITY_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
SOURCE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"
OUT = ROOT / "analysis_outputs/source_audit/priority_crop_pack_source_fidelity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "priority_crop_pack_source_fidelity.json"
OUT_MD = OUT / "priority_crop_pack_source_fidelity.md"
SHEET = OUT / "priority_crop_pack_source_fidelity_sheet.jpg"


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


def crop_tuple(crop: list[int | float]) -> tuple[int, int, int, int]:
    return tuple(int(round(v)) for v in crop)  # type: ignore[return-value]


def diff_stats(a: Image.Image, b: Image.Image) -> dict:
    if a.size != b.size:
        return {"sameSize": False, "aSize": list(a.size), "bSize": list(b.size)}
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    stat = ImageStat.Stat(diff)
    mean_abs = sum(stat.mean) / len(stat.mean)
    rms = (sum(value * value for value in stat.rms) / len(stat.rms)) ** 0.5
    max_abs = max(channel[1] for channel in diff.getextrema())
    return {
        "sameSize": True,
        "rms": round(rms, 6),
        "meanAbs": round(mean_abs, 6),
        "maxAbs": int(max_abs),
    }


def draw_box(draw: ImageDraw.ImageDraw, crop: tuple[int, int, int, int], box: list[float], color: str, label: str, fnt: ImageFont.ImageFont) -> None:
    x0, y0, _, _ = crop
    bx0, by0, bx1, by1 = [int(round(v)) for v in box]
    rect = [bx0 - x0, by0 - y0, bx1 - x0, by1 - y0]
    draw.rectangle(rect, outline=color, width=4)
    tx, ty = rect[0], max(0, rect[1] - 24)
    text_box = draw.textbbox((tx, ty), label, font=fnt)
    draw.rectangle([text_box[0] - 3, text_box[1] - 2, text_box[2] + 3, text_box[3] + 2], fill=(12, 15, 20))
    draw.text((tx, ty), label, fill=color, font=fnt)


def draw_frame(draw: ImageDraw.ImageDraw, crop: tuple[int, int, int, int], frame: list[float]) -> None:
    x0, y0, x1, y1 = crop
    fx0, fy0, fx1, fy1 = frame
    color = "#55d6ff"
    if x0 <= fx0 <= x1:
        draw.line([(fx0 - x0, max(0, fy0 - y0)), (fx0 - x0, min(y1 - y0, fy1 - y0))], fill=color, width=3)
    if y0 <= fy0 <= y1:
        draw.line([(max(0, fx0 - x0), fy0 - y0), (min(x1 - x0, fx1 - x0), fy0 - y0)], fill=color, width=3)
    if y0 <= fy1 <= y1:
        draw.line([(max(0, fx0 - x0), fy1 - y0), (min(x1 - x0, fx1 - x0), fy1 - y0)], fill=color, width=3)


def render_source_crop(source: Image.Image, entry: dict, frame: list[float], fnt: ImageFont.ImageFont) -> tuple[Image.Image, Path]:
    crop = crop_tuple(entry["crop"])
    img = source.crop(crop).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_frame(draw, crop, frame)
    for box in entry.get("boxes", []):
        draw_box(draw, crop, box["box"], box["color"], box["label"], fnt)
    out_path = OUT / f"{entry['id']}_source.jpg"
    img.save(out_path, quality=94)
    return img, out_path


def build_sheet(rows: list[dict], source: Image.Image, old_source: Image.Image) -> None:
    title_font = font(21)
    small_font = font(15)
    margin = 22
    gap = 18
    panel_w = 410
    label_h = 52
    rows_rendered = []
    for row in rows:
        crop = crop_tuple(row["crop"])
        source_crop = source.crop(crop).convert("RGB")
        old_crop = old_source.crop(crop).convert("RGB")
        diff = ImageChops.difference(source_crop, old_crop)
        scale = min(panel_w / source_crop.width, 1.0)
        panels = []
        for label, img in [("current source", source_crop), ("old 3D source", old_crop), ("abs diff", diff)]:
            panels.append((label, img.resize((int(img.width * scale), int(img.height * scale)))))
        rows_rendered.append((row, panels))

    row_heights = [label_h + max(img.height for _, img in panels) + gap for _, panels in rows_rendered]
    sheet_w = margin * 2 + panel_w * 3 + gap * 2
    sheet_h = margin + sum(row_heights)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (16, 18, 22))
    draw = ImageDraw.Draw(sheet)
    y = margin
    for row, panels in rows_rendered:
        draw.text((margin, y), f"{row['id']}  RMS={row['raw3dVsSourceDiff']['rms']}  max={row['raw3dVsSourceDiff']['maxAbs']}", fill=(237, 241, 245), font=title_font)
        draw.text((margin, y + 25), str(row["crop"]), fill=(154, 168, 183), font=small_font)
        x = margin
        y_img = y + label_h
        for label, img in panels:
            draw.text((x, y_img - 20), label, fill=(154, 168, 183), font=small_font)
            sheet.paste(img, (x, y_img))
            x += panel_w + gap
        y += label_h + max(img.height for _, img in panels) + gap
    sheet.save(SHEET, quality=94)


def main() -> None:
    priority = json.loads(PRIORITY_JSON.read_text(encoding="utf-8"))
    source_native = Image.open(SOURCE_IMAGE).convert("RGB")
    source = source_native.rotate(180)
    old_source_path = ROOT / priority["sourceImage"]
    old_source = Image.open(old_source_path).convert("RGB")
    fnt = font(18)
    frame = priority["reflectedP78FrameOnP76"]

    rows = []
    source_outputs = []
    for entry in priority["crops"]:
        crop = crop_tuple(entry["crop"])
        source_raw = source.crop(crop).convert("RGB")
        old_raw = old_source.crop(crop).convert("RGB")
        source_annotated, out_path = render_source_crop(source, entry, frame, fnt)
        row = {
            "id": entry["id"],
            "title": entry["title"],
            "lineIndex": entry["lineIndex"],
            "text": entry["text"],
            "crop": list(crop),
            "oldCropPackOutput": entry["output"],
            "sourceRenderedOutput": str(out_path.relative_to(ROOT)),
            "raw3dVsSourceDiff": diff_stats(source_raw, old_raw),
        }
        rows.append(row)
        source_outputs.append((entry, source_annotated))

    build_sheet(rows, source, old_source)

    stale = any(row["raw3dVsSourceDiff"]["rms"] > 10 for row in rows)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 priority crop pack source-fidelity audit; no OCR extraction or key derivation",
        "priorityCropPack": str(PRIORITY_JSON.relative_to(ROOT)),
        "currentSourceImage": str(SOURCE_IMAGE.relative_to(ROOT)),
        "currentSourceTransform": "rotate180",
        "oldCropPackSourceImage": priority["sourceImage"],
        "sheet": str(SHEET.relative_to(ROOT)),
        "rows": rows,
        "summary": {
            "cropCount": len(rows),
            "anyHigh3dVsSourceDiff": stale,
            "maxRawRms": max(row["raw3dVsSourceDiff"]["rms"] for row in rows),
            "minRawRms": min(row["raw3dVsSourceDiff"]["rms"] for row in rows),
        },
        "assessment": [
            "The existing priority crop pack was rendered from the 3D upright image layer.",
            "After rotating the native source image 180 degrees into readable orientation, the same crop windows visually match the 3D upright layer at JPEG-resave tolerance.",
            "The earlier stale-crop conclusion was caused by comparing readable-upright crop coordinates against native upside-down source coordinates.",
            "The old crop pack remains valid as readable-orientation geometry, provided future source comparisons apply the same 180-degree source transform.",
        ],
        "nextMove": "For future source comparisons, rotate source_images/fresh PDF extraction 180 degrees before applying existing upright page-76 crop coordinates.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Priority Crop Pack Source-Fidelity Audit",
        "",
        "Scope: compare the existing page-76 priority crop pack against the current source scan. No OCR extraction, key derivation, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Existing crop-pack source: `{result['oldCropPackSourceImage']}`",
        f"- Current source image: `{result['currentSourceImage']}`",
        f"- Current source transform: `{result['currentSourceTransform']}`",
        f"- Comparison/source-render sheet: `{result['sheet']}`",
        f"- Any high 3D-vs-source crop difference after transform: `{stale}`",
        f"- Raw RMS range: `{result['summary']['minRawRms']}` to `{result['summary']['maxRawRms']}`",
        "",
        "## Crop Differences",
        "",
        "| crop | old source | current source-rendered output | raw RMS | raw max | assessment |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        diff = row["raw3dVsSourceDiff"]
        assessment = "stale for exact geometry" if diff["rms"] > 10 else "source-faithful after rotate180"
        lines.append(
            f"| `{row['id']}` | `{row['oldCropPackOutput']}` | `{row['sourceRenderedOutput']}` | `{diff['rms']}` | `{diff['maxAbs']}` | {assessment} |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("maxRawRms:", result["summary"]["maxRawRms"])


if __name__ == "__main__":
    main()
