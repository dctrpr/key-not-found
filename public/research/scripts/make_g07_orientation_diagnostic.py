#!/usr/bin/env python3
"""Show the disputed G07 crop before and after an exact 180-degree turn."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from PIL import Image, ImageDraw


def make_diagnostic(packet):
    manifest = json.loads((packet / "PACKET_MANIFEST.json").read_bytes())
    hashes = {record["path"]: record["sha256"] for record in manifest["assets"]}
    pair = []
    for name in ("u-p73-04.png", "r-p73-04.png"):
        raw = (packet / name).read_bytes()
        if sha256(raw).hexdigest() != hashes[name]:
            raise ValueError("Crop differs from the registered packet")
        pair.append(Image.open(BytesIO(raw)).convert("RGB"))
    upright, reflected = pair
    if reflected.tobytes() != upright.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes():
        raise ValueError("Crops must show the same ink")
    turn = Image.Transpose.ROTATE_180
    panels = [
        ("Upright crop", upright),
        ("Horizontal reflection", reflected),
        ("Upright crop turned 180 degrees", upright.transpose(turn)),
        ("Reflection turned 180 degrees", reflected.transpose(turn)),
    ]
    gap, header = 12, 24
    width, height = upright.size
    canvas = Image.new("RGB", (width * 2 + gap * 3, (height + header) * 2 + gap * 3), "#1d1d1c")
    draw = ImageDraw.Draw(canvas)
    for index, (label, picture) in enumerate(panels):
        x = gap + (index % 2) * (width + gap)
        y = gap + (index // 2) * (height + header + gap)
        draw.text((x, y), label, fill="#f2f1e8")
        canvas.paste(picture, (x, y + header))
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    with args.out.open("xb") as out:
        make_diagnostic(args.packet).save(out, format="PNG")


if __name__ == "__main__":
    main()
