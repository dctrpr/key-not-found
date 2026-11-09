#!/usr/bin/env python3
"""Bridge the active p78 frame through mirror and native/upright coordinates.

The active p78 graphic frame is normally discussed after it is horizontally
reflected onto page 76. This pass reconstructs the corresponding source box on
page 78, then records current and repaired-frame coordinates in:

- p78 readable/upright coordinates
- p76 readable/upright reflected coordinates
- p78 native PDF/source coordinates
- p76 native PDF/source coordinates

No OCR extraction, key derivation, hashing, seed checks, WIF checks, or address
checks are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TRI_JSON = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
P78_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_78_upright.jpg"
P76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
P78_NATIVE = ROOT / "analysis_outputs/source_images/magazine_page_78.jpg"
P76_NATIVE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"
OUT = ROOT / "analysis_outputs/source_audit/p78_frame_source_native_bridge"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p78_frame_source_native_bridge.json"
OUT_MD = OUT / "p78_frame_source_native_bridge.md"
SHEET = OUT / "p78_frame_source_native_bridge_sheet.jpg"


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


def hflip_box(box: list[float], width: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [width - x1, y0, width - x0, y1]


def rot180_box(box: list[float], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    return [width - x1, height - y1, width - x0, height - y0]


def shift_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def rect_label(draw: ImageDraw.ImageDraw, box: list[float], color: str, label: str, fnt: ImageFont.ImageFont) -> None:
    b = [int(round(v)) for v in box]
    draw.rectangle(b, outline=color, width=5)
    x, y = b[0], max(0, b[1] - 25)
    text_box = draw.textbbox((x, y), label, font=fnt)
    draw.rectangle([text_box[0] - 3, text_box[1] - 2, text_box[2] + 3, text_box[3] + 2], fill=(12, 15, 20))
    draw.text((x, y), label, fill=color, font=fnt)


def make_panel(image: Image.Image, boxes: list[dict], coord_key: str, crop: list[int], title: str) -> Image.Image:
    panel = image.copy().convert("RGB")
    draw = ImageDraw.Draw(panel)
    fnt = font(21)
    title_font = font(30)
    draw.rectangle([20, 20, 850, 70], fill=(12, 15, 20))
    draw.text((34, 30), title, fill=(238, 242, 247), font=title_font)
    for box in boxes:
        rect_label(draw, box[coord_key], box["color"], box["label"], fnt)
    return panel.crop(tuple(crop))


def build_sheet(rows: list[dict]) -> None:
    p78u = Image.open(P78_UPRIGHT).convert("RGB")
    p76u = Image.open(P76_UPRIGHT).convert("RGB")
    p78n = Image.open(P78_NATIVE).convert("RGB")
    p76n = Image.open(P76_NATIVE).convert("RGB")

    crops = {
        "p78UprightBox": [250, 2320, 1385, 3040],
        "p76ReflectedUprightBox": [1120, 2320, 2325, 3040],
        "p78NativeBox": [1120, 250, 2325, 930],
        "p76NativeBox": [220, 250, 1385, 930],
    }
    panels = [
        ("p78 upright source", make_panel(p78u, rows, "p78UprightBox", crops["p78UprightBox"], "p78 upright source frame")),
        ("p76 upright reflected", make_panel(p76u, rows, "p76ReflectedUprightBox", crops["p76ReflectedUprightBox"], "p76 upright reflected frame")),
        ("p78 native source", make_panel(p78n, rows, "p78NativeBox", crops["p78NativeBox"], "p78 native source frame")),
        ("p76 native reflected", make_panel(p76n, rows, "p76NativeBox", crops["p76NativeBox"], "p76 native reflected frame")),
    ]
    margin = 24
    gap = 20
    label_h = 34
    panel_w = 530
    rendered = []
    for label, img in panels:
        scale = min(panel_w / img.width, 1.0)
        rendered.append((label, img.resize((int(img.width * scale), int(img.height * scale)))))
    width = margin * 2 + panel_w * 2 + gap
    row_h = label_h + max(img.height for _, img in rendered[:2]) + gap
    height = margin * 2 + row_h * 2
    sheet = Image.new("RGB", (width, height), (16, 18, 22))
    draw = ImageDraw.Draw(sheet)
    fnt = font(20)
    positions = [
        (margin, margin),
        (margin + panel_w + gap, margin),
        (margin, margin + row_h),
        (margin + panel_w + gap, margin + row_h),
    ]
    for (label, img), (x, y) in zip(rendered, positions):
        draw.text((x, y), label, fill=(238, 242, 247), font=fnt)
        sheet.paste(img, (x, y + label_h))
    sheet.save(SHEET, quality=94)


def main() -> None:
    tri = json.loads(TRI_JSON.read_text(encoding="utf-8"))
    p76u = Image.open(P76_UPRIGHT)
    width, height = p76u.size
    base_reflected = [float(v) for v in tri["frame"]]
    records = [
        ("current", 0.0, 0.0, "#55d6ff"),
        ("g5_edge_touch_dx_-38", -38.0, 0.0, "#ff5ebc"),
        ("nearest_grid_dx_-40", -40.0, 0.0, "#ff9b2e"),
    ]
    rows = []
    for name, dx, dy, color in records:
        p76_reflected = shift_box(base_reflected, dx, dy)
        p78_source = hflip_box(p76_reflected, width)
        rows.append(
            {
                "name": name,
                "label": name,
                "dx": dx,
                "dy": dy,
                "color": color,
                "p78UprightBox": [int(round(v)) for v in p78_source],
                "p76ReflectedUprightBox": [int(round(v)) for v in p76_reflected],
                "p78NativeBox": rot180_box(p78_source, width, height),
                "p76NativeBox": rot180_box(p76_reflected, width, height),
            }
        )

    build_sheet(rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78 frame source/native coordinate bridge; no OCR extraction or key derivation",
        "sourceReports": {"triContact": str(TRI_JSON.relative_to(ROOT))},
        "transformChain": [
            "p78 upright source box --horizontal flip--> p76 upright reflected box",
            "upright box --rotate180--> native PDF/source box",
        ],
        "imageSize": [width, height],
        "rows": rows,
        "sheet": str(SHEET.relative_to(ROOT)),
        "assessment": [
            "The active p78 frame benchmark can now be compared in both the source page and target page coordinate systems.",
            "The current and dx=-38/-40 repaired frames keep the same simple transform chain: horizontal mirror between p78 and p76, then rotate180 for native source images.",
            "This preserves the repaired frame as a source-registration benchmark but does not provide a word/letter/line extraction unit.",
        ],
        "nextMove": "Use these coordinates when comparing any future physical/original-layout source against the p78-frame-to-p76 lower-corridor benchmark.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P78 Frame Source / Native Bridge",
        "",
        "Scope: reconstruct the p78 source frame and bridge current/repaired frame boxes across p78/p76 and upright/native coordinate systems. No OCR extraction, key derivation, seed, WIF, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Image size: `{width}x{height}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Coordinate Chain",
        "",
        "- p78 upright source box --horizontal flip--> p76 upright reflected box",
        "- upright box --rotate180--> native PDF/source box",
        "",
        "## Frame Coordinates",
        "",
        "| frame | dx/dy | p78 upright source | p76 upright reflected | p78 native source | p76 native reflected |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['name']}` | `{row['dx']}/{row['dy']}` | `{row['p78UprightBox']}` | `{row['p76ReflectedUprightBox']}` | `{row['p78NativeBox']}` | `{row['p76NativeBox']}` |"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    for row in rows:
        print(row["name"], row["p78UprightBox"], "->", row["p76ReflectedUprightBox"])


if __name__ == "__main__":
    main()
