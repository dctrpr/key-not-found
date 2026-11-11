#!/usr/bin/env python3
"""Render the six registered right-alignment comparisons from saved measurements."""

import argparse
import json
from math import isfinite
from pathlib import Path
from statistics import median

from PIL import Image, ImageDraw, ImageFont


THRESHOLD = 120
SCANS = (("high", "Sharper scan"), ("low", "Second scan"))
BLOCKS = (
    ("p77-right-control", 77, 8, 16, "Comparison"),
    ("p78-final", 78, 19, 22, "Final four lines"),
    ("p79-right-control", 79, 22, 25, "Comparison"),
)
BACKGROUND = "#10110f"
PANEL = "#191b17"
LINE = "#34372f"
PAPER = "#f3f1e7"
MUTED = "#b6b9ad"
CONTROL = "#b8c0ac"
ACCENT = "#d6ff3c"


def single_at_threshold(records):
    selected = [record for record in records if record["threshold"] == THRESHOLD]
    if len(selected) != 1:
        raise ValueError(f"Expected one result at threshold {THRESHOLD}")
    return selected[0]


def load_cells(measurements):
    cells = {}
    for scan_id, _ in SCANS:
        scan = measurements["scans"][scan_id]
        width = scan["size"][0]
        if not isinstance(width, int) or width <= 0:
            raise ValueError("Invalid scan width")
        blocks = {block["id"]: block for block in scan["blocks"]}
        if len(blocks) != len(scan["blocks"]):
            raise ValueError("Duplicate block identifier")
        for block_id, page, first, last, _ in BLOCKS:
            block = blocks[block_id]
            ids = [f"p{page}r{row:02d}" for row in range(first, last + 1)]
            if [row["id"] for row in block["rows"]] != ids:
                raise ValueError(f"Unexpected row order for {scan_id}/{block_id}")
            summary = single_at_threshold(block["thresholdResults"])
            segments = []
            for row in block["rows"]:
                edge = single_at_threshold(row["edges"])
                left, right = edge["left"] / width, edge["right"] / width
                if not (isfinite(left) and isfinite(right) and 0 <= left < right <= 1):
                    raise ValueError(f"Invalid measured edges for {scan_id}/{row['id']}")
                segments.append((row["id"][-3:], left, right))
            spread = max(right for _, _, right in segments) - min(right for _, _, right in segments)
            if abs(spread - summary["rightSpanFraction"]) > 1e-9:
                raise ValueError(f"Right-edge spread differs from the saved result for {scan_id}/{block_id}")
            cells[(scan_id, block_id)] = (width, segments, spread)
    return cells


def draw_cell(draw, fonts, x, y, width, segments, spread, target):
    pitch = 33
    height = len(segments) * pitch + 83
    edge_color = ACCENT if target else CONTROL
    draw.rounded_rectangle((x, y, x + width, y + height), radius=12, fill=PANEL, outline=LINE, width=2)
    plot_left, plot_right = x + 80, x + width - 28
    plot_top, plot_bottom = y + 13, y + len(segments) * pitch + 13

    def position(fraction):
        return round(plot_left + fraction * (plot_right - plot_left))

    for tick in (0, 0.25, 0.5, 0.75, 1):
        xx = position(tick)
        draw.line((xx, plot_top, xx, plot_bottom), fill=LINE, width=2)
    anchor = position(median(right for _, _, right in segments))
    for yy in range(plot_top, plot_bottom, 14):
        draw.line((anchor, yy, anchor, min(yy + 8, plot_bottom)), fill=edge_color, width=3)

    for index, (row_id, left, right) in enumerate(segments):
        yy = y + 28 + index * pitch
        draw.text((x + 15, yy), row_id, font=fonts[25], fill=MUTED, anchor="lm")
        x0, x1 = position(left), position(right)
        draw.rounded_rectangle((x0, yy - 4, x1, yy + 4), radius=4, fill=edge_color)
        draw.ellipse((x1 - 5, yy - 5, x1 + 5, yy + 5), fill=edge_color)

    for tick, label in ((0, "0%"), (0.5, "50%"), (1, "100%")):
        draw.text((position(tick), plot_bottom + 4), label, font=fonts[23], fill=MUTED, anchor="mt")
    draw.text((x + 16, y + height - 30), f"Right-edge spread  {spread * 100:.2f}%", font=fonts[26],
              fill=edge_color, anchor="lt")
    return height


def render(measurements):
    cells = load_cells(measurements)
    width, height = 1280, 1370
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    fonts = {size: ImageFont.load_default(size=size) for size in (23, 25, 26, 28, 30, 33, 36, 52)}

    draw.text((44, 36), "KEY NOT FOUND   /   ISSUE 24", font=fonts[25], fill=ACCENT, anchor="lt")
    draw.text((44, 77), "Three blocks share the pattern", font=fonts[52], fill=PAPER, anchor="lt")
    draw.text((45, 143), "Page 78 has a tight right edge. Pages 77 and 79 do too.",
              font=fonts[33], fill=MUTED, anchor="lt")

    draw.line((48, 211, 94, 211), fill=CONTROL, width=8)
    draw.text((108, 211), "Measured row span", font=fonts[28], fill=PAPER, anchor="lm")
    for xx in (467, 484, 501):
        draw.line((xx, 211, xx + 10, 211), fill=CONTROL, width=3)
    draw.text((526, 211), "Median right edge", font=fonts[28], fill=PAPER, anchor="lm")
    draw.text((1236, 211), "Threshold 120", font=fonts[28], fill=MUTED, anchor="rm")

    cell_width, columns = 584, (44, 652)
    for x, (scan_id, scan_title) in zip(columns, SCANS):
        pixels, _, _ = cells[(scan_id, BLOCKS[0][0])]
        draw.text((x, 259), scan_title, font=fonts[36], fill=PAPER, anchor="lt")
        draw.text((x + cell_width, 263), f"{pixels:,} px wide", font=fonts[26], fill=MUTED, anchor="rt")

    y = 317
    for block_id, page, _, _, role in BLOCKS:
        target = page == 78
        draw.text((44, y), f"Page {page}  /  {role}", font=fonts[30], fill=ACCENT if target else PAPER, anchor="lt")
        for x, (scan_id, _) in zip(columns, SCANS):
            _, segments, spread = cells[(scan_id, block_id)]
            cell_height = draw_cell(draw, fonts, x, y + 42, cell_width, segments, spread, target)
        y += 42 + cell_height + 17

    draw.line((44, y + 1, 1236, y + 1), fill=LINE, width=2)
    draw.text((44, y + 19), "Horizontal scale is the percentage of each scan’s width after tilt correction.",
              font=fonts[26], fill=MUTED, anchor="lt")
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Saved MEASUREMENTS.json")
    parser.add_argument("--out", type=Path, required=True, help="New PNG output")
    args = parser.parse_args()
    image = render(json.loads(args.input.read_text(encoding="utf-8")))
    with args.out.open("xb") as handle:
        image.save(handle, format="PNG", compress_level=9)


if __name__ == "__main__":
    main()
