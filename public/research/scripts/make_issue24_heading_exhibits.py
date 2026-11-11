#!/usr/bin/env python3
"""Show the faint page-74 heading and page-75 print at matching nominal coordinates."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image


def create(packet, output):
    manifest = json.loads((packet / "PACKET_MANIFEST.json").read_bytes())
    if manifest["testId"] != "issue24-full-page-glyph-review":
        raise ValueError("Use the registered full-page tile packet")
    hashes = {item["path"]: item["sha256"] for item in manifest["assets"]}

    def tile(name):
        raw = (packet / name).read_bytes()
        if sha256(raw).hexdigest() != hashes[name]:
            raise ValueError("Source tile differs from the packet")
        return Image.open(BytesIO(raw)).convert("RGB")

    source = tile("u-p74-NE.png").crop((0, 300, 1180, 1100))
    reflected = source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    reference = tile("u-p75-NW.png").crop((140, 300, 1320, 1100))
    output.mkdir()
    reflected.save(output / "p74-faint-heading-reflected.png", format="PNG")
    reference.save(output / "p75-heading-upright.png", format="PNG")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create(args.packet, args.out)


if __name__ == "__main__":
    main()
