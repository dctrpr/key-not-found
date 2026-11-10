#!/usr/bin/env python3
"""Produce exact upright/reflected crop pairs for the frozen G07 observations."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
import json
from math import ceil, floor
from pathlib import Path
import re
import subprocess

BASE = "analysis_outputs/continuation_20261110"
REVIEW = f"{BASE}/g07_glyph_review"
PROTOCOL = f"{REVIEW}/PROTOCOL.json"
INVENTORY = f"{REVIEW}/BASELINE_BOXES.json"
EARLIER = f"{BASE}/batch20/G07/RESULT.json"
SCRIPT = "scripts/prepare_g07_glyph_review.py"
TEST_ID = "g07-mirror-glyph-orientation"
WIDTH, HEIGHT = 2544, 3264
PADDING = 8
SHEET_ROWS = 4
PANE_WIDTH = 760
PANE_HEIGHT = 290
COUNTS = dict(zip(range(73, 81), (10, 7, 20, 22, 17, 10, 13, 15)))
CONTROL_EXPECTATIONS = {"c01": "symmetric-only", "c02": "reversed", "c03": "ordinary"}
GLYPHS = {
    "F": ("11111","10000","10000","11110","10000","10000","10000"),
    "R": ("11110","10001","10001","11110","10100","10010","10001"),
    "O": ("01110","10001","10001","10001","10001","10001","01110"),
    "G": ("01110","10001","10000","10111","10001","10001","01110"),
    "H": ("10001","10001","10001","11111","10001","10001","10001"),
    "I": ("11111","00100","00100","00100","00100","00100","11111"),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def digest(raw):
    return sha256(raw).hexdigest()


def registered_inputs(research, protocol, receipt_path, commit):
    require(re.fullmatch(r"[a-f0-9]{40}", commit), "Supply the full registration commit")
    require(protocol == research / PROTOCOL, "Unexpected protocol path")
    raw = protocol.read_bytes()
    spec = json.loads(raw)
    receipt = json.loads(receipt_path.read_bytes())
    require(spec["testId"] == TEST_ID and spec["paddingPx"] == PADDING and spec["sheetRows"] == SHEET_ROWS
            and spec["controlExpectations"] == CONTROL_EXPECTATIONS, "Protocol scope differs")
    require(receipt["registrationCommit"] == commit and receipt["protocolSha256"] == digest(raw)
            and receipt["remoteHeadMatched"] is True and receipt["targetPixelsOpenedAtVerification"] is False,
            "Missing pre-pixel registration")
    pins = {**spec["sourceHashes"], **spec["scriptHashes"], PROTOCOL: digest(raw)}
    require(len(pins) == receipt["pinnedBlobsVerified"], "Registration pin count differs")
    require(Path(__file__).resolve() == research / SCRIPT and SCRIPT in spec["scriptHashes"],
            "Use the registered preparation script")
    buffers = {}
    for name, wanted in pins.items():
        path = (research / name).resolve()
        require(path.is_relative_to(research) and path.relative_to(research).as_posix() == name,
                "Invalid pin path")
        current = path.read_bytes()
        previous = subprocess.check_output(
            ["git", "-C", str(research.parent.parent), "show", f"{commit}:public/research/{name}"])
        require(current == previous and digest(current) == wanted, f"Registered file differs: {name}")
        buffers[name] = current
    return spec, digest(raw), buffers


def enclose(box):
    left, low, right, high = box
    return [floor(WIDTH * left), floor(HEIGHT * (1-high)),
            ceil(WIDTH * right), ceil(HEIGHT * (1-low))]


def target_inventory(raw):
    inventory = json.loads(raw)
    require(inventory["counts"] == {"normal": 207, "horizontalMirror": 114, "total": 321}
            and len(inventory["records"]) == 321, "Wrong box inventory")
    groups = {page: [] for page in COUNTS}
    all_streams = set()
    for record in inventory["records"]:
        page = record["printedPage"]
        orientation = record["orientation"]
        require(page in groups and orientation in ("normal", "horizontal-mirror")
                and record["imageDimensionsPx"] == [WIDTH, HEIGHT], "Unknown source view")
        stream_id = record["publicStreamId"]
        require(stream_id not in all_streams, "Duplicate stream ID")
        all_streams.add(stream_id)
        require(record["jobId"] == f"p{page}-baseline-m{int(orientation == 'horizontal-mirror')}"
                and re.fullmatch(rf"G07:{record['jobId']}:observation[0-9]+", stream_id),
                "Source view and stream ID differ")
        a,b,c,d = map(Fraction, record["normalizedBoxDecimal"])
        require(0 <= a < c <= 1 and 0 <= b < d <= 1, "Out-of-range normalized rectangle")
        require(record["viewPixelEnclosure"] == enclose((a,b,c,d)), "Detector box enclosure differs")
        upright = enclose((1-c,b,1-a,d)) if orientation == "horizontal-mirror" else enclose((a,b,c,d))
        require(record["uprightPixelEnclosure"] == upright, "Upright box mapping differs")
        if orientation == "horizontal-mirror":
            l,t,r,bottom = upright
            ident = f"p{page}-{len(groups[page])+1:02d}"
            groups[page].append({
                "id": ident, "printedPage": page, "publicStreamId": stream_id,
                "pixelBounds": [max(0,l-PADDING), max(0,t-PADDING),
                                min(WIDTH,r+PADDING), min(HEIGHT,bottom+PADDING)],
                "uprightPath": f"u-{ident}.png", "reflectedPath": f"r-{ident}.png",
            })
    require({p:len(rows) for p,rows in groups.items()} == COUNTS, "Wrong mirrored observation population")
    return groups


def sheet(rows, Image, ImageDraw):
    """Show source and reflection at the same display scale for each target."""
    gutter, top, row_pad = 18, 34, 42
    renders = []
    for target_id, upright, reflected in rows:
        factor = min(1, PANE_WIDTH / upright.width, PANE_HEIGHT / upright.height)
        size = (max(1, int(upright.width * factor)), max(1, int(upright.height * factor)))
        pair = tuple(pic if pic.size == size else pic.resize(size, Image.Resampling.NEAREST)
                     for pic in (upright, reflected))
        renders.append((target_id, *pair))
    width = 2 * PANE_WIDTH + 3 * gutter
    height = top + sum(u.height + row_pad for _,u,_ in renders)
    canvas = Image.new("RGB", (width, height), "#181817")
    draw = ImageDraw.Draw(canvas)
    draw.text((gutter, 10), "UPRIGHT SOURCE", fill="#f1f0e6")
    draw.text((2*gutter+PANE_WIDTH, 10), "HORIZONTAL REFLECTION", fill="#f1f0e6")
    y = top
    for ident, upright, reflected in renders:
        draw.text((gutter, y), ident, fill="#d6ff3c")
        draw.line((gutter, y+16, width-gutter, y+16), fill="#50504c")
        canvas.paste(upright, (gutter, y+21))
        canvas.paste(reflected, (2*gutter+PANE_WIDTH, y+21))
        y += upright.height + row_pad
    return canvas


def synthetic_word(word, Image, ImageDraw):
    cell = 9
    source = Image.new("RGB", ((len(word)*6+1)*cell, 11*cell), "#fafafa")
    draw = ImageDraw.Draw(source)
    for index, letter in enumerate(word):
        for y, line in enumerate(GLYPHS[letter], 2):
            for x, bit in enumerate(line, 1 + index * 6):
                if bit == "1":
                    draw.rectangle((x*cell,y*cell,(x+1)*cell-1,(y+1)*cell-1),fill="#222222")
    return source


def control_pairs(Image, ImageDraw):
    normal = synthetic_word("FROG", Image, ImageDraw)
    reflected = normal.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    symmetric = synthetic_word("HIOIH", Image, ImageDraw)
    return [
        ("c01", symmetric, symmetric.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),
        ("c02", reflected, normal),
        ("c03", normal, reflected),
    ]


def save_image(output, name, image):
    dest = output / name
    image.save(dest, format="PNG")
    dest.chmod(0o600)
    return {"path": name, "sha256": digest(dest.read_bytes())}


def run(args):
    research = args.research.resolve()
    spec, protocol_hash, buffers = registered_inputs(research, args.protocol.resolve(),
                                                      args.registration_receipt, args.registration_commit)
    groups = target_inventory(buffers[INVENTORY])
    result = json.loads(buffers[EARLIER])
    pins = {item["page"]:item for item in result["sourceImageInventory"]}
    require(set(pins) == set(COUNTS), "Earlier source image inventory changed")
    output = args.out.resolve()
    require(args.out.is_absolute() and not output.is_relative_to(research.parent.parent)
            and "public" not in {part.lower() for part in output.parts}, "Use a fresh private output")
    output.mkdir(mode=0o700)
    import fitz
    import PIL
    from PIL import Image, ImageDraw

    require(spec["runtimeVersions"] == {"pymupdf": fitz.__version__, "pillow": PIL.__version__},
            "Image library version differs")
    assets, targets, sheets, controls = [], [], [], []
    with fitz.open(stream=buffers["magazine.pdf"], filetype="pdf") as pdf:
        for page, rows in groups.items():
            physical = pdf[page-73]
            entries = physical.get_images(full=True)
            require(len(entries) == 1, "Unexpected embedded image count")
            source = pdf.extract_image(entries[0][0])["image"]
            upright = Image.open(BytesIO(source)).convert("RGB").transpose(Image.Transpose.ROTATE_180)
            require(digest(source) == pins[page]["embeddedImageSha256"]
                    and upright.size == (WIDTH, HEIGHT)
                    and digest(upright.tobytes()) == pins[page]["uprightRGBSha256"],
                    "Source image differs from the original baseline")
            reflected = upright.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            for start in range(0, len(rows), SHEET_ROWS):
                pair_rows = []
                sheet_name = f"sheet-p{page}-{start//SHEET_ROWS+1:02d}.png"
                for row in rows[start:start+SHEET_ROWS]:
                    l,t,r,b = row["pixelBounds"]
                    a = upright.crop((l,t,r,b))
                    bpic = reflected.crop((WIDTH-r,t,WIDTH-l,b))
                    require(a.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes() == bpic.tobytes(),
                            "Crop does not map to the same ink")
                    assets.append(save_image(output, row["uprightPath"], a))
                    assets.append(save_image(output, row["reflectedPath"], bpic))
                    pair_rows.append((row["id"],a,bpic))
                    targets.append({**row, "sheet": sheet_name})
                sheets.append({"path":sheet_name,"targetIds":[row[0] for row in pair_rows]})
                assets.append(save_image(output, sheet_name, sheet(pair_rows, Image, ImageDraw)))
    for ident,u,r in control_pairs(Image,ImageDraw):
        asset = save_image(output, f"control-{ident}.png", sheet([(ident,u,r)],Image,ImageDraw))
        controls.append({"id":ident,**asset})
        assets.append(asset)
    require(len(targets) == 114 and len(sheets) == 32 and len(assets) == 263, "Packet size differs")
    manifest = {"version":1,"testId":TEST_ID,"registrationCommit":args.registration_commit,
                "protocolSha256":protocol_hash,"preparedAtUTC":utc(),
                "targets":targets,"controls":controls,"sheets":sheets,"assets":assets}
    file = output/"PACKET_MANIFEST.json"
    file.write_text(json.dumps(manifest,indent=2)+"\n")
    file.chmod(0o600)
    print(json.dumps({"targets":len(targets),"assets":len(assets),
                      "packetManifestSha256":digest(file.read_bytes())}))


def self_test():
    from PIL import Image, ImageDraw
    checks = control_pairs(Image,ImageDraw)
    require(checks[0][1].tobytes() == checks[0][2].tobytes(), "Symmetric control differs")
    require(checks[1][1].tobytes() == checks[2][2].tobytes() and
            checks[1][2].tobytes() == checks[2][1].tobytes() and
            checks[2][1].tobytes() != checks[2][2].tobytes(), "Asymmetric controls differ")
    for ident,a,b in checks:
        require(sheet([(ident,a,b)], Image,ImageDraw).width == 1574, "Sheet width differs")
    require(enclose((Fraction(0),Fraction(0),Fraction(1),Fraction(1))) == [0,0,WIDTH,HEIGHT],
            "Normalized box enclosure differs")
    print(json.dumps({"syntheticControlsPassed":True,"glyphControls":len(checks),"targetPixelsOpened":False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--research", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--registration-receipt", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    require(all((args.research,args.protocol,args.registration_commit,args.registration_receipt,args.out)),
            "Supply registered preparation arguments")
    run(args)


if __name__ == "__main__":
    main()
