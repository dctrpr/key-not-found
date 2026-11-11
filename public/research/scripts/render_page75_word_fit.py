#!/usr/bin/env python3
"""Render the saved page 75 word-fit measurement as a native-pixel comparison."""

import argparse
import json
from math import isfinite
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BACKGROUND = "#10110f"
PANEL = "#191b17"
GRID = "#34372f"
PAPER = "#f3f1e7"
MUTED = "#b6b9ad"
LIME = "#d6ff3c"
BLUE = "#9ad9e8"
AXIS_MIN = -30
AXIS_MAX = 30


def positions(scan):
    summary = scan["summary"]
    origin = summary["fullInkUpperPx"]
    row_end = max(edge["right"] for variant in scan["variants"].values()
                  for edge in variant["edges"]["row2"].values())
    values = (summary["appendedEndpointLowPx"] - origin,
              summary["appendedEndpointHighPx"] - origin,
              row_end - origin,
              summary["prePeriodInkLowerPx"] - origin)
    left, right, visible, pre_period = values
    if not (all(isfinite(value) and AXIS_MIN <= value <= AXIS_MAX for value in values)
            and left < right and pre_period < visible < 0):
        raise ValueError("The saved measurement cannot be represented on the fixed plot axis")
    return values


def draw_scan(draw, fonts, y, title, scan):
    left, right, visible, pre_period = positions(scan)
    plot_left, plot_right = 404, 1189
    plot_top, plot_bottom = y + 60, y + 251

    def x(value):
        return round(plot_left + (value - AXIS_MIN) * (plot_right - plot_left) / (AXIS_MAX - AXIS_MIN))

    draw.rounded_rectangle((44, y, 1236, y + 294), radius=12, fill=PANEL, outline=GRID, width=2)
    draw.text((65, y + 16), title, font=fonts[37], fill=PAPER, anchor="lt")
    for tick in range(AXIS_MIN, AXIS_MAX + 1, 10):
        xx = x(tick)
        if tick == 0:
            for yy in range(plot_top, plot_bottom, 14):
                draw.line((xx, yy, xx, min(yy + 8, plot_bottom)), fill=MUTED, width=3)
        else:
            draw.line((xx, plot_top, xx, plot_bottom), fill=GRID, width=2)
        tick_label = f"{tick:+d}" if tick else "0"
        draw.text((xx, plot_bottom + 12), tick_label, font=fonts[25],
                  fill=PAPER if not tick else MUTED, anchor="mt")

    lanes = (
        (y + 88, 'Proposed “to” endpoint', f"{left:+.1f} to {right:+.1f} px", LIME),
        (y + 151, "Row 2 end and guard", f"{visible:+.1f} px to bound", PAPER),
        (y + 214, "Pre-period lower bound", f"{pre_period:+.1f} px", BLUE),
    )
    for yy, label, value, color in lanes:
        draw.text((65, yy - 22), label, font=fonts[29], fill=PAPER, anchor="lt")
        draw.text((65, yy + 12), value, font=fonts[25], fill=color, anchor="lt")

    yy = lanes[0][0]
    draw.line((x(left), yy, x(right), yy), fill=LIME, width=10)
    for endpoint in (left, right):
        draw.line((x(endpoint), yy - 12, x(endpoint), yy + 12), fill=LIME, width=4)

    yy = lanes[1][0]
    draw.rounded_rectangle((x(visible), yy - 7, x(0), yy + 7), radius=3, outline=PAPER, width=3)
    draw.ellipse((x(visible) - 7, yy - 7, x(visible) + 7, yy + 7), fill=PAPER)

    yy = lanes[2][0]
    xx = x(pre_period)
    draw.polygon(((xx - 10, yy), (xx, yy - 10), (xx + 10, yy), (xx, yy + 10)), fill=BLUE)


def render(measurements):
    image = Image.new("RGB", (1280, 1000), BACKGROUND)
    draw = ImageDraw.Draw(image)
    fonts = {size: ImageFont.load_default(size=size) for size in (25, 27, 29, 31, 37, 53)}
    draw.text((44, 33), "KEY NOT FOUND   /   PAGE 75", font=fonts[25], fill=LIME, anchor="lt")
    draw.text((44, 77), 'Where would “to” end?', font=fonts[53], fill=PAPER, anchor="lt")
    draw.text((44, 146), "Estimated endpoint if the next word were placed on row 1.",
              font=fonts[31], fill=MUTED, anchor="lt")
    draw.text((44, 195), "The dashed line marks the full visible-ink upper bound.",
              font=fonts[27], fill=MUTED, anchor="lt")

    draw_scan(draw, fonts, 242, "Sharper scan", measurements["scans"]["high"])
    draw_scan(draw, fonts, 554, "Second scan", measurements["scans"]["low"])

    draw.line((44, 878, 1236, 878), fill=GRID, width=2)
    draw.text((44, 899), "Native pixels relative to the full visible-ink upper bound (0).",
              font=fonts[27], fill=PAPER, anchor="lt")
    draw.text((44, 946), "The text-frame edge remains unknown. The cause of the break is unresolved.",
              font=fonts[27], fill=MUTED, anchor="lt")
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
