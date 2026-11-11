#!/usr/bin/env python3
"""Build the registered page-77 comparison from exact high-scan crops."""
import argparse
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from measure_p77_initial_transfer import PROTOCOL, ROOT, checked_crop, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(PROTOCOL.read_bytes())
    result = json.loads(PROTOCOL.with_name("DIRECT_MEASUREMENTS.json").read_bytes())
    high_result = result["scans"]["high"]
    if not high_result["targetScored"]:
        raise ValueError("No high-scan target measurement")
    high_spec = spec["sources"][0]
    raw = (ROOT / high_spec["path"]).read_bytes()
    if digest(raw) != high_spec["sha256"]:
        raise ValueError("Source crop hash differs")
    source = Image.open(BytesIO(raw)).convert("RGB")
    cards = [
        ("Known uppercase B", spec["caseControls"]["B"]["high"], high_result["controlRanges"]["B"]),
        ("Disputed initial", result["targetBoxes"]["high"], high_result["targetRange"]),
        ("Known lowercase b", spec["caseControls"]["b"]["high"], high_result["controlRanges"]["b"]),
    ]
    canvas = Image.new("RGB", (1056, 460), "#121211")
    draw = ImageDraw.Draw(canvas)
    fonts = {size: ImageFont.load_default(size=size) for size in (19, 22, 38)}
    draw.text((36, 27), "One initial, three native crops", font=fonts[38], fill="#f4f1e8")
    draw.text((36, 76), "Issue 24 · page 77 · sharper scan · pixels enlarged 5x", font=fonts[19], fill="#b1aea4")
    for index, (label, box, limits) in enumerate(cards):
        x = 36 + 334 * index
        color = "#d6ff3c" if index == 1 else "#f4f1e8"
        draw.rectangle((x, 122, x + 315, 402), outline=color if index == 1 else "#54534c", width=2)
        draw.text((x + 15, 134), label, font=fonts[22], fill=color)
        tile = checked_crop(source, box)
        tile = tile.resize((tile.width * 5, tile.height * 5), Image.Resampling.NEAREST)
        canvas.paste(tile, (x + (315 - tile.width) // 2, 173 + (205 - tile.height) // 2))
        draw.text((x + 15, 371), f"{limits[0]:.2f} to {limits[1]:.2f}", font=fonts[22], fill=color)
    draw.text((36, 421), "Upper-right to lower-right ink ratio across the declared box and background variations.",
              font=fonts[19], fill="#b1aea4")
    with args.out.open("xb") as stream:
        canvas.save(stream, format="PNG", compress_level=9)


if __name__ == "__main__":
    main()
