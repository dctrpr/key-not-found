#!/usr/bin/env python3
"""Prepare exact overlapping Issue 24 tiles and optional lossless glyph views."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True

import prepare_g07_glyph_review as glyphs

FOLDER = "analysis_outputs/continuation_20261111/full_page_glyph_review"
PROTOCOL = f"{FOLDER}/PROTOCOL.json"
EARLIER = "analysis_outputs/continuation_20261110/batch20/G07/RESULT.json"
SCRIPT = "scripts/prepare_full_page_glyph_review.py"
CONTROL_SCRIPT = "scripts/prepare_g07_glyph_review.py"
TEST_ID = "issue24-full-page-glyph-review"
SIZE = (2544, 3264)
PAGES = tuple(range(73, 81))
TILES = {
    "NW": (0, 0, 1320, 1680),
    "NE": (1224, 0, 2544, 1680),
    "SW": (0, 1584, 1320, 3264),
    "SE": (1224, 1584, 2544, 3264),
}
CONTROLS = {"c01": "ordinary", "c02": "reversed", "c03": "symmetric-only", "c04": "rotated-ordinary"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def verify_pins(research, protocol, receipt_path, commit):
    require(re.fullmatch(r"[a-f0-9]{40}", commit), "Supply the complete Git commit")
    require(protocol == research / PROTOCOL, "Unexpected protocol path")
    raw = protocol.read_bytes()
    spec = json.loads(raw)
    receipt = json.loads(receipt_path.read_bytes())
    require(spec["testId"] == TEST_ID and spec["imageSize"] == list(SIZE)
            and spec["pages"] == list(PAGES) and spec["tiles"] == {k: list(v) for k,v in TILES.items()}
            and spec["controlExpectations"] == CONTROLS, "Registered parameters differ")
    require(receipt["registrationCommit"] == commit and receipt["protocolSha256"] == digest(raw)
            and receipt["remoteHeadMatched"] is True and receipt["targetPixelsOpenedAtVerification"] is False,
            "Pre-pixel registration receipt is missing or changed")
    pins = {**spec["sourceHashes"], **spec["scriptHashes"], PROTOCOL: digest(raw)}
    require(len(pins) == receipt["pinnedBlobsVerified"], "Registration pin count differs")
    for name, file in ((SCRIPT, __file__), (CONTROL_SCRIPT, glyphs.__file__)):
        require(Path(file).resolve() == research / name and name in spec["scriptHashes"],
                "Use the registered code")
    buffers = {}
    for name, expected in pins.items():
        path = (research / name).resolve()
        require(path.is_relative_to(research) and path.relative_to(research).as_posix() == name,
                "Invalid registered path")
        current = path.read_bytes()
        previous = subprocess.check_output(
            ["git", "-C", str(research.parent.parent), "show", f"{commit}:public/research/{name}"])
        require(current == previous and digest(current) == expected, f"Registered blob differs: {name}")
        buffers[name] = current
    return spec, digest(raw), buffers


def controls(Image, ImageDraw):
    old = {name: (left, right) for name, left, right in glyphs.control_pairs(Image, ImageDraw)}
    turn = old["c03"][0].transpose(Image.Transpose.ROTATE_180)
    return (("c01", *old["c03"]), ("c02", *old["c02"]), ("c03", *old["c01"]),
            ("c04", turn, turn.transpose(Image.Transpose.FLIP_LEFT_RIGHT)))


def prepare(args):
    import fitz
    import PIL
    from PIL import Image, ImageDraw

    research = args.research.resolve()
    spec, protocol_sha, pinned = verify_pins(research, args.protocol.resolve(),
                                           args.registration_receipt, args.registration_commit)
    require(spec["runtimeVersions"] == {"pymupdf":fitz.__version__,"pillow":PIL.__version__},
            "Image library version differs")
    out = args.out.resolve()
    require(args.out.is_absolute() and not out.is_relative_to(research.parent.parent)
            and "public" not in {part.lower() for part in out.parts}, "Use a fresh private output")
    out.mkdir(mode=0o700)
    prior = json.loads(pinned[EARLIER])
    expected = {row["page"]:row for row in prior["sourceImageInventory"]}
    require(set(expected) == set(PAGES), "Previous source raster population differs")
    manifest = {"version":1,"testId":TEST_ID,"registrationCommit":args.registration_commit,
                "protocolSha256":protocol_sha,"tiles":[],"controls":[],"assets":[]}
    with fitz.open(stream=pinned["magazine.pdf"], filetype="pdf") as pdf:
        for page in PAGES:
            source = pdf[page-73]
            images = source.get_images(full=True)
            require(len(images) == 1, "Expected one page JPEG")
            raw = pdf.extract_image(images[0][0])["image"]
            upright = Image.open(BytesIO(raw)).convert("RGB").transpose(Image.Transpose.ROTATE_180)
            require(digest(raw) == expected[page]["embeddedImageSha256"] and upright.size == SIZE
                    and digest(upright.tobytes()) == expected[page]["uprightRGBSha256"],
                    "Baseline raster hash or dimensions changed")
            for suffix, box in TILES.items():
                ident = f"p{page}-{suffix}"
                photo = upright.crop(box)
                mirror = photo.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                u_name, r_name = f"u-{ident}.png", f"r-{ident}.png"
                manifest["tiles"].append({"id":ident,"page":page,"box":list(box),
                                          "uprightPath":u_name,"reflectedPath":r_name})
                manifest["assets"].extend((glyphs.save_image(out,u_name,photo),
                                            glyphs.save_image(out,r_name,mirror)))
    for ident,left,right in controls(Image,ImageDraw):
        asset = glyphs.save_image(out,f"control-{ident}.png",glyphs.sheet([(ident,left,right)],Image,ImageDraw))
        manifest["controls"].append({"id":ident,**asset})
        manifest["assets"].append(asset)
    require(len(manifest["tiles"]) == 32 and len(manifest["assets"]) == 68, "Packet population differs")
    manifest["preparedAtUTC"] = utc()
    path = out/"PACKET_MANIFEST.json"
    path.write_text(json.dumps(manifest,indent=2)+"\n")
    path.chmod(0o600)
    print(json.dumps({"tiles":32,"assets":68,"packetManifestSha256":digest(path.read_bytes())}))


def diagnostic(args):
    from PIL import Image, ImageDraw

    packet = args.packet.resolve()
    raw_manifest = json.loads((packet/"PACKET_MANIFEST.json").read_bytes())
    require(raw_manifest["testId"] == TEST_ID, "Unexpected packet")
    require(bool(args.tile) != bool(args.page), "Choose a tile or a full page")
    hashes = {row["path"]: row["sha256"] for row in raw_manifest["assets"]}

    def native_tile(ident):
        require(re.fullmatch(r"p(?:7[3-9]|80)-(?:NW|NE|SW|SE)",ident), "Unknown tile ID")
        tile = next(row for row in raw_manifest["tiles"] if row["id"] == ident)
        name = f"u-{ident}.png"
        require(tile["uprightPath"] == name, "Tile path differs")
        raw = (packet/name).read_bytes()
        require(digest(raw) == hashes[name], "Tile hash differs")
        return Image.open(BytesIO(raw)).convert("RGB")

    if args.page:
        photo = Image.new("RGB",SIZE)
        for suffix, box in TILES.items():
            photo.paste(native_tile(f"p{args.page}-{suffix}"),box[:2])
    else:
        photo = native_tile(args.tile)
    left, top, right, bottom = args.box
    require(0 <= left < right <= photo.width and 0 <= top < bottom <= photo.height, "Invalid local crop")
    crop = photo.crop(args.box)
    turn = {90:Image.Transpose.ROTATE_90,180:Image.Transpose.ROTATE_180,270:Image.Transpose.ROTATE_270}
    turned = crop if args.turn == 0 else crop.transpose(turn[args.turn])
    reflected = turned.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    gap, header = 12, 26
    width, height = turned.size
    canvas = Image.new("RGB",(2*width+3*gap,height+header+gap),"#242422")
    draw = ImageDraw.Draw(canvas)
    draw.text((gap,6),f"Source turned {args.turn}° CCW",fill="white")
    draw.text((2*gap+width,6),"Reflection of turned source",fill="white")
    canvas.paste(turned,(gap,header))
    canvas.paste(reflected,(2*gap+width,header))
    with args.out.open("xb") as file:
        canvas.save(file,format="PNG")


def self_test():
    from PIL import Image, ImageDraw
    require(set(TILES) == {"NW","NE","SW","SE"} and TILES["NW"][2]-TILES["NE"][0] == 96
            and TILES["NW"][3]-TILES["SW"][1] == 96, "Tile partition differs")
    data = controls(Image,ImageDraw)
    require([row[0] for row in data] == list(CONTROLS), "Control IDs differ")
    require(all(left.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes() == right.tobytes()
                for _,left,right in data), "Control pairs differ")
    require(data[2][1].tobytes() == data[2][2].tobytes()
            and data[3][1].tobytes() == data[0][1].transpose(Image.Transpose.ROTATE_180).tobytes(),
            "Symmetric and rotation controls differ")
    print(json.dumps({"syntheticControlsPassed":True,"controls":len(data),"targetPixelsOpened":False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--diagnostic", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    for name in ("research","protocol","registration-receipt","out","packet"):
        parser.add_argument(f"--{name}",type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--tile")
    parser.add_argument("--page",type=int,choices=PAGES)
    parser.add_argument("--box",type=int,nargs=4)
    parser.add_argument("--turn",type=int,choices=(0,90,180,270))
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.diagnostic:
        require(all((args.packet,args.box,args.out)) and args.turn is not None,
                "Supply packet, crop box, turn and output")
        diagnostic(args)
    else:
        require(all((args.research,args.protocol,args.registration_receipt,args.registration_commit,args.out)),
                "Supply registered preparation arguments")
        prepare(args)


if __name__ == "__main__":
    main()
