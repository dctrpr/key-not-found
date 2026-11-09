#!/usr/bin/env python3
"""Build a coordinate bridge between readable/upright and native PDF source images.

The current source images are native PDF orientation; the 3D viewer and most
page-76 geometry records use readable/upright orientation. This pass converts
the active page-76 O5/G5/frame benchmark boxes into native coordinates and
renders side-by-side overlays.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, or address
checks are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PRIORITY_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"
OUT = ROOT / "analysis_outputs/source_audit/upright_native_coordinate_bridge"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "upright_native_coordinate_bridge.json"
OUT_MD = OUT / "upright_native_coordinate_bridge.md"
SHEET = OUT / "upright_native_coordinate_bridge_sheet.jpg"


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


def rot180_box(box: list[float], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    return [width - x1, height - y1, width - x0, height - y0]


def box_size(box: list[int]) -> str:
    return f"{box[2] - box[0]}x{box[3] - box[1]}"


def draw_labeled_boxes(image: Image.Image, rows: list[dict], coord_key: str, title: str) -> Image.Image:
    img = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    fnt = font(28)
    small = font(19)
    palette = {
        "O5": "#ff8a00",
        "G5": "#00d6ff",
        "should_sell": "#ff5ebc",
        "frame": "#55d6ff",
    }
    draw.rectangle([20, 20, 760, 68], fill=(12, 15, 20))
    draw.text((34, 30), title, fill=(238, 242, 247), font=fnt)
    for row in rows:
        box = row[coord_key]
        color = palette.get(row["id"], "#55d6ff")
        if row["id"] == "frame":
            draw.rectangle(box, outline=color, width=6)
        else:
            draw.rectangle(box, outline=color, width=5)
            draw.text((box[0], max(0, box[1] - 25)), row["label"], fill=color, font=small)
    return img


def build_sheet(upright: Image.Image, native: Image.Image, rows: list[dict]) -> None:
    crop_upright = [700, 2325, 1775, 3060]
    # Convert the upright context crop to native coordinates.
    crop_native = rot180_box(crop_upright, upright.width, upright.height)
    upright_overlay = draw_labeled_boxes(upright, rows, "uprightBox", "readable/upright coordinates")
    native_overlay = draw_labeled_boxes(native, rows, "nativeBox", "native source/PDF coordinates")
    panels = [
        ("upright page crop", upright_overlay.crop(crop_upright)),
        ("native page crop", native_overlay.crop(crop_native)),
        ("native crop rotated back", native_overlay.crop(crop_native).rotate(180)),
    ]
    margin = 24
    gap = 22
    panel_w = 560
    label_h = 34
    rendered = []
    for label, img in panels:
        scale = min(panel_w / img.width, 1.0)
        rendered.append((label, img.resize((int(img.width * scale), int(img.height * scale)))))
    width = margin * 2 + panel_w * len(rendered) + gap * (len(rendered) - 1)
    height = margin * 2 + label_h + max(img.height for _, img in rendered)
    sheet = Image.new("RGB", (width, height), (16, 18, 22))
    draw = ImageDraw.Draw(sheet)
    fnt = font(20)
    x = margin
    for label, img in rendered:
        draw.text((x, margin), label, fill=(238, 242, 247), font=fnt)
        sheet.paste(img, (x, margin + label_h))
        x += panel_w + gap
    sheet.save(SHEET, quality=94)


def main() -> None:
    priority = json.loads(PRIORITY_JSON.read_text(encoding="utf-8"))
    upright = Image.open(UPRIGHT_IMAGE).convert("RGB")
    native = Image.open(NATIVE_IMAGE).convert("RGB")
    if upright.size != native.size:
        raise RuntimeError(f"size mismatch: upright={upright.size} native={native.size}")
    width, height = upright.size

    rows = [
        {
            "id": "frame",
            "label": "reflected p78 frame",
            "uprightBox": [int(v) for v in priority["reflectedP78FrameOnP76"]],
        }
    ]
    for crop in priority["crops"]:
        for item in crop.get("boxes", []):
            if "O5" in item["label"] or "G5" in item["label"] or "should sell" in item["label"]:
                label_id = "O5" if "O5" in item["label"] else "G5" if "G5" in item["label"] else "should_sell"
                if any(row["id"] == label_id for row in rows):
                    continue
                rows.append(
                    {
                        "id": label_id,
                        "label": item["label"],
                        "uprightBox": [int(round(v)) for v in item["box"]],
                    }
                )
    rows.sort(key=lambda row: ["frame", "should_sell", "G5", "O5"].index(row["id"]))
    for row in rows:
        row["nativeBox"] = rot180_box(row["uprightBox"], width, height)
        row["size"] = box_size(row["uprightBox"])

    build_sheet(upright, native, rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "readable/upright to native source coordinate bridge for active page-76 benchmark boxes; no OCR or key derivation",
        "uprightImage": str(UPRIGHT_IMAGE.relative_to(ROOT)),
        "nativeImage": str(NATIVE_IMAGE.relative_to(ROOT)),
        "transform": "rotate180",
        "imageSize": [width, height],
        "rows": rows,
        "sheet": str(SHEET.relative_to(ROOT)),
        "assessment": [
            "The active page-76 benchmark can be represented in both readable/upright coordinates and native PDF/source coordinates with a simple 180-degree rotation.",
            "Future source/PDF extraction checks should convert coordinates instead of visually comparing unlike orientations.",
            "This is a geometry bridge only; it does not add an extraction unit or key material.",
        ],
        "nextMove": "Use this bridge when comparing physical/source images or when rebuilding p78/frame contacts from native PDF extraction.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Upright / Native Coordinate Bridge",
        "",
        "Scope: map the active page-76 O5/G5/frame benchmark between readable/upright coordinates and native PDF/source coordinates. No OCR extraction, key derivation, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Transform: `{result['transform']}`",
        f"- Image size: `{width}x{height}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Coordinate Bridge",
        "",
        "| id | label | upright box | native source box | size |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['id']}` | {row['label']} | `{row['uprightBox']}` | `{row['nativeBox']}` | `{row['size']}` |")
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    for row in rows:
        print(row["id"], row["uprightBox"], "->", row["nativeBox"])


if __name__ == "__main__":
    main()
