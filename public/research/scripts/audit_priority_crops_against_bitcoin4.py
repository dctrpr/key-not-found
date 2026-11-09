#!/usr/bin/env python3
"""Compare the page-76 priority crop pack against bitcoin4.pdf.

This is a source-fidelity audit only. It maps the current high-res priority
crops into the lower-quality bitcoin4 Issue 24 witness and checks whether those
regions remain visually recognizable. It does not extract text or derive keys.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CROP_PACK_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
HIGH_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
BITCOIN4_PDF = Path("private_inputs/Desktop/bitcoin4.pdf")
WITNESS_JSON = ROOT / "analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.json"

OUT = ROOT / "analysis_outputs/source_audit/priority_crops_bitcoin4_comparison"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "priority_crops_bitcoin4_comparison.json"
OUT_MD = OUT / "priority_crops_bitcoin4_comparison.md"
OUT_SHEET = OUT / "priority_crops_bitcoin4_comparison_sheet.jpg"


def extract_page_image(path: Path, page_index: int) -> Image.Image:
    doc = fitz.open(path)
    page = doc[page_index]
    images = page.get_images(full=True)
    if images:
        raw = doc.extract_image(images[0][0])["image"]
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if page.rotation:
            img = img.rotate(-page.rotation, expand=True)
        return img
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def transform_box(box: list[float], t: dict[str, float]) -> list[float]:
    return [
        t["ax"] * box[0] + t["bx"],
        t["ay"] * box[1] + t["by"],
        t["ax"] * box[2] + t["bx"],
        t["ay"] * box[3] + t["by"],
    ]


def clamp_box(box: list[float], width: int, height: int) -> list[int]:
    x0 = max(0, min(width - 1, int(round(box[0]))))
    y0 = max(0, min(height - 1, int(round(box[1]))))
    x1 = max(x0 + 1, min(width, int(round(box[2]))))
    y1 = max(y0 + 1, min(height, int(round(box[3]))))
    return [x0, y0, x1, y1]


def crop(img: Image.Image, box: list[int]) -> Image.Image:
    return img.crop(tuple(box))


def orange_ratio(img: Image.Image) -> float:
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    mask = (r > 150) & (g > 65) & (g < 230) & (b < 180) & ((r - b) > 45) & ((r - g) > -45)
    return float(mask.mean())


def dark_ratio(img: Image.Image) -> float:
    arr = np.asarray(img.convert("L"))
    return float((arr < 105).mean())


def edge_density(img: Image.Image) -> float:
    arr = np.asarray(img.convert("L")).astype(np.int16)
    if arr.shape[0] < 2 or arr.shape[1] < 2:
        return 0.0
    gx = np.abs(np.diff(arr, axis=1))
    gy = np.abs(np.diff(arr, axis=0))
    return float(((gx > 28).mean() + (gy > 28).mean()) / 2.0)


def average_hash(img: Image.Image, size: int = 16) -> str:
    small = img.convert("L").resize((size, size), Image.Resampling.LANCZOS)
    arr = np.asarray(small, dtype=np.float32)
    bits = arr > arr.mean()
    return "".join("1" if bit else "0" for bit in bits.flatten())


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b))


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    if a.size != b.size:
        a = a.resize(b.size, Image.Resampling.LANCZOS)
    aa = np.asarray(a.convert("L")).astype(np.float32)
    bb = np.asarray(b.convert("L")).astype(np.float32)
    return float(np.abs(aa - bb).mean())


def quick_font() -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(name, 22)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_annotations(
    img: Image.Image,
    crop_origin: list[int],
    boxes: list[dict[str, Any]],
    transform: dict[str, float] | None = None,
) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    font = quick_font()
    for item in boxes:
        box = [float(v) for v in item["box"]]
        if transform:
            box = transform_box(box, transform)
        rel = [
            int(round(box[0] - crop_origin[0])),
            int(round(box[1] - crop_origin[1])),
            int(round(box[2] - crop_origin[0])),
            int(round(box[3] - crop_origin[1])),
        ]
        color = item.get("color", "#00aaff")
        draw.rectangle(rel, outline=color, width=3)
        label = item.get("label", "")
        if label:
            x = max(0, rel[0])
            y = max(0, rel[1] - 22)
            draw.text((x, y), label, fill=color, font=font)
    return out


def fit_for_sheet(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / img.width, max_h / img.height)
    size = (max(1, int(round(img.width * scale))), max(1, int(round(img.height * scale))))
    return img.resize(size, Image.Resampling.LANCZOS)


def make_sheet(rows: list[dict[str, Any]]) -> None:
    font = quick_font()
    max_w = 680
    max_h = 310
    row_h = 410
    gutter = 28
    width = max_w * 2 + gutter * 3
    height = row_h * len(rows) + 40
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    y = 20
    for row in rows:
        title = f"{row['id']} | mapped bitcoin4 crop {row['bitcoin4CropBox']}"
        draw.text((gutter, y), title, fill=(20, 20, 20), font=font)
        y_img = y + 34
        hi = fit_for_sheet(row["highImage"], max_w, max_h)
        lo = fit_for_sheet(row["lowImage"], max_w, max_h)
        sheet.paste(hi, (gutter, y_img))
        sheet.paste(lo, (gutter * 2 + max_w, y_img))
        draw.text((gutter, y_img + hi.height + 8), "magazine.pdf baseline", fill=(60, 60, 60), font=font)
        draw.text((gutter * 2 + max_w, y_img + lo.height + 8), "bitcoin4.pdf mapped witness", fill=(60, 60, 60), font=font)
        y += row_h
    sheet.save(OUT_SHEET, quality=95)


def main() -> None:
    if not BITCOIN4_PDF.exists():
        raise FileNotFoundError(BITCOIN4_PDF)

    crop_pack = json.loads(CROP_PACK_JSON.read_text())
    witness = json.loads(WITNESS_JSON.read_text())
    transform = witness["transforms"]["p76"]

    high_page = Image.open(HIGH_PAGE).convert("RGB")
    low_page = extract_page_image(BITCOIN4_PDF, 3)

    crop_records: list[dict[str, Any]] = []
    sheet_rows: list[dict[str, Any]] = []
    for item in crop_pack["crops"]:
        high_box = [float(v) for v in item["crop"]]
        high_crop_box = clamp_box(high_box, high_page.width, high_page.height)
        low_crop_box = clamp_box(transform_box(high_box, transform), low_page.width, low_page.height)
        high_img = crop(high_page, high_crop_box)
        low_img = crop(low_page, low_crop_box)

        high_annotated = draw_annotations(high_img, high_crop_box, item.get("boxes", []))
        low_annotated = draw_annotations(low_img, low_crop_box, item.get("boxes", []), transform)

        ah_high = average_hash(high_img)
        ah_low = average_hash(low_img)
        record = {
            "id": item["id"],
            "lineIndex": item["lineIndex"],
            "text": item["text"],
            "highCropBox": high_crop_box,
            "bitcoin4CropBox": low_crop_box,
            "scaleApprox": {
                "x": round((low_crop_box[2] - low_crop_box[0]) / max(1, high_crop_box[2] - high_crop_box[0]), 6),
                "y": round((low_crop_box[3] - low_crop_box[1]) / max(1, high_crop_box[3] - high_crop_box[1]), 6),
            },
            "visualMetrics": {
                "orangeRatioHigh": round(orange_ratio(high_img), 6),
                "orangeRatioBitcoin4": round(orange_ratio(low_img), 6),
                "darkRatioHigh": round(dark_ratio(high_img), 6),
                "darkRatioBitcoin4": round(dark_ratio(low_img), 6),
                "edgeDensityHigh": round(edge_density(high_img), 6),
                "edgeDensityBitcoin4": round(edge_density(low_img), 6),
                "avgHashHamming16": hamming(ah_high, ah_low),
                "meanAbsDiffAfterResize": round(mean_abs_diff(high_img, low_img), 3),
            },
            "mappedAnnotations": [
                {
                    "label": box["label"],
                    "highBox": [round(float(v), 3) for v in box["box"]],
                    "bitcoin4Box": [round(v, 3) for v in transform_box([float(x) for x in box["box"]], transform)],
                }
                for box in item.get("boxes", [])
            ],
        }
        crop_records.append(record)
        sheet_rows.append(
            {
                "id": item["id"],
                "bitcoin4CropBox": low_crop_box,
                "highImage": high_annotated,
                "lowImage": low_annotated,
            }
        )

    make_sheet(sheet_rows)

    conclusion = (
        "bitcoin4 preserves the same priority regions well enough for rough visual source-fidelity checks, "
        "but its lower resolution and page-specific distortion keep it unsuitable as geometry truth or extraction material."
    )
    next_move = (
        "Use the crop pack as the future-source baseline, and only revisit bitcoin4 if a new external clue names "
        "the lower-quality scan or says to compare source differences directly."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Map page-76 priority crop pack into bitcoin4.pdf; source-fidelity audit only; no key derivation.",
        "sources": {
            "cropPack": str(CROP_PACK_JSON),
            "highPage": str(HIGH_PAGE),
            "bitcoin4": str(BITCOIN4_PDF),
            "highPageSize": [high_page.width, high_page.height],
            "bitcoin4PageSize": [low_page.width, low_page.height],
            "p76TransformFromWitnessAudit": transform,
        },
        "crops": crop_records,
        "sheet": str(OUT_SHEET),
        "conclusion": conclusion,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Priority Crops vs bitcoin4",
        "",
        "Scope: map the current page-76 priority crop pack into the lower-quality `bitcoin4.pdf` Issue 24 witness. No text extraction, hashing, seed checking, or address checking was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{OUT_SHEET}`",
        f"- High-res page size: `{result['sources']['highPageSize']}`",
        f"- bitcoin4 page size: `{result['sources']['bitcoin4PageSize']}`",
        f"- p76 transform residual source: `{WITNESS_JSON}`",
        "",
        "## Crop Results",
        "",
        "| Crop | bitcoin4 mapped crop | Orange high/bitcoin4 | Dark high/bitcoin4 | Edge high/bitcoin4 | Hash diff | Resize MAD |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rec in crop_records:
        m = rec["visualMetrics"]
        lines.append(
            f"| `{rec['id']}` | `{rec['bitcoin4CropBox']}` | "
            f"`{m['orangeRatioHigh']}` / `{m['orangeRatioBitcoin4']}` | "
            f"`{m['darkRatioHigh']}` / `{m['darkRatioBitcoin4']}` | "
            f"`{m['edgeDensityHigh']}` / `{m['edgeDensityBitcoin4']}` | "
            f"`{m['avgHashHamming16']}` | `{m['meanAbsDiffAfterResize']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {conclusion}",
            "- The mapped crops still show the same visual regions, so bitcoin4 can help catch gross source mismatches.",
            "- The metrics and prior p78 frame test still make bitcoin4 a weak witness for exact geometry.",
            "",
            "## Next Move",
            "",
            f"- {next_move}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")


if __name__ == "__main__":
    main()
