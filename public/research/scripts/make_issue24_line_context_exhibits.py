#!/usr/bin/env python3
"""Recreate exact high/low source crops for the line-boundary adjudication."""
import argparse
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import fitz
from PIL import Image

HIGH_PIN = "a30c61f8c49674afb7bccc6680d6477f6e919175386a2422de0a944db4e76c13"
CANONICAL_PIN = "c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe"
READER_PIN = "6c5a6e1521a865aa5a57a7f6486e80a93bfde418f7fbab0073f88a2d1473f760"
PACKET_PIN = "68c16722d2a3c80362ce67e164e98683f75be726993179fa087d9f1fe6ea20cc"
ROWS = ("p75r03", "p75r25", "p76r18", "p77r09", "p77r24")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, expected):
    data = path.read_bytes()
    if digest(data) != expected:
        raise ValueError("Source pin differs")
    return data


def high_box(locator):
    x0, y0, x1, y1 = locator["box"]
    cx, cy = 1272, 1632
    angle = math.radians(locator["rotate_ccw_degrees"])
    sine, cosine = math.sin(angle), math.cos(angle)
    points = [(cx + cosine*(x-cx) - sine*(y-cy), cy + sine*(x-cx) + cosine*(y-cy))
              for x in (x0, x1) for y in (y0, y1)]
    xx, yy = zip(*points)
    return (max(0, math.floor(min(xx))-48), max(0, math.floor(min(yy))-48),
            min(2544, math.ceil(max(xx))+48), min(3264, math.ceil(max(yy))+48))


def save_crop(image, box, path):
    crop = image.crop(box)
    clean = Image.frombytes("RGB", crop.size, crop.tobytes())
    clean.save(path, compress_level=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--reader", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Use a fresh output directory")
    high_bytes = pinned(args.research/"magazine.pdf", HIGH_PIN)
    canonical = json.loads(pinned(args.research/"sources/printed-lines.json", CANONICAL_PIN))
    reader = json.loads(pinned(args.reader, READER_PIN))
    packet = json.loads(pinned(args.packet/"MANIFEST.json", PACKET_PIN))
    high_rows = {row["id"]: row for row in canonical["rows"]}
    low_rows = {row["id"]: row for row in reader["rows"]}
    assets = {asset["path"]: asset for asset in packet["assets"]}
    args.out.mkdir(mode=0o700)
    with fitz.open(stream=high_bytes, filetype="pdf") as pdf:
        for identifier in ROWS:
            row = high_rows[identifier]
            page = pdf[row["page"]-73]
            images = page.get_images(full=True)
            if len(images) != 1 or page.rotation != 180:
                raise ValueError("High source geometry differs")
            source = pdf.extract_image(images[0][0])
            with Image.open(BytesIO(source["image"])) as raw:
                if raw.size != (2544, 3264):
                    raise ValueError("High source dimensions differ")
                high = raw.convert("RGB").transpose(Image.Transpose.ROTATE_180)
            save_crop(high, high_box(row["locator"]), args.out/f"high-{identifier}.png")

            low = Image.new("RGB", (2040, 2805))
            for side in ("top", "bottom"):
                relative = f"assets/p{row['page']}-{side}.png"
                asset = assets[relative]
                data = pinned(args.packet/relative, asset["sha256"])
                with Image.open(BytesIO(data)) as image:
                    low.paste(image, (0, asset["cropXYXY"][1]))
            if digest(low.tobytes()) != packet["pages"][str(row["page"])]["uprightRGBSha256"]:
                raise ValueError("Low source raster differs")
            lower = low_rows[identifier.replace("r", "-l")]
            x0, y0, x1, y1 = lower["boxXYXY"]
            box = [max(0, x0-24), max(0, y0-40), min(2040, x1+24), min(2805, y1+40)]
            save_crop(low, box, args.out/f"low-{identifier}.png")
    print(json.dumps({"sourceExhibits": len(ROWS)*2, "fittedTransforms": 0}))


if __name__ == "__main__":
    main()
