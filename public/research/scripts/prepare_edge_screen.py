#!/usr/bin/env python3
"""Prepare fixed, native-pixel paper-perimeter review packets from a pinned PDF."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess

TEST_ID = "g02-perimeter-visibility"
PROTOCOL = "analysis_outputs/continuation_20261110/g02_edge_screen/PROTOCOL.json"
SCRIPT = "scripts/prepare_edge_screen.py"
SOURCE = "keyser bitcoin .pdf"
PAGES = (76, 77, 78, 79)
SIZE = (2040, 2805)
X = (0, 306, 1734, 2040)
Y = (0, 421, 2384, 2805)
ORDER = ("NW", "N", "NE", "E", "SE", "S", "SW", "W")
POSITIONS = ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1))
TRANSECTS = {"top": (510, 1020, 1530), "right": (701, 1402, 2103),
             "bottom": (510, 1020, 1530), "left": (701, 1402, 2103)}
HALF_STRIP = 24


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def digest(data):
    return sha256(data).hexdigest()


def boxes():
    return {name: (X[col], Y[row], X[col+1], Y[row+1])
            for name, (col, row) in zip(ORDER, POSITIONS)}


def guide_box(side, at):
    if side == "top":
        return at-HALF_STRIP, Y[0], at+HALF_STRIP+1, Y[1]
    if side == "bottom":
        return at-HALF_STRIP, Y[2], at+HALF_STRIP+1, Y[3]
    if side == "left":
        return X[0], at-HALF_STRIP, X[1], at+HALF_STRIP+1
    require(side == "right", "Unknown edge")
    return X[2], at-HALF_STRIP, X[3], at+HALF_STRIP+1


def guide(image, page, side, Image, ImageDraw):
    """Add native-pixel rulers outside unchanged transect pixel strips."""
    panels = []
    vertical = side in ("top", "bottom")
    for at in TRANSECTS[side]:
        x0, y0, x1, y1 = guide_box(side, at)
        crop = image.crop((x0, y0, x1, y1))
        left, top = (42, 32) if vertical else (12, 32)
        panel = Image.new("RGB", (left+crop.width+14, top+crop.height+32), "#eeeeeb")
        panel.paste(crop, (left, top))
        draw = ImageDraw.Draw(panel)
        if vertical:
            draw.text((5, 5), f"p{page} {side}", fill="#111111")
            draw.text((5, 17), f"x={at}", fill="#111111")
            draw.line((left+HALF_STRIP, top-5, left+HALF_STRIP, top-1), fill="#963018")
            ticks = sorted({y0, y1-1, *(v for v in range(y0, y1) if v % 50 == 0)})
            for number in ticks:
                y = top+number-y0
                draw.line((left-6, y, left-1, y), fill="#111111")
                if number in (y0, y1-1) or min(number-y0, y1-1-number) >= 13:
                    draw.text((3, max(top, min(y-5, top+crop.height-11))), str(number), fill="#111111")
        else:
            draw.text((4, 5), f"p{page} {side}  y={at}", fill="#111111")
            draw.line((left-6, top+HALF_STRIP, left-1, top+HALF_STRIP), fill="#963018")
            ticks = sorted({x0, x1-1, *(v for v in range(x0, x1) if v % 50 == 0)})
            for number in ticks:
                x = left+number-x0
                y = top+crop.height
                draw.line((x, y+1, x, y+6), fill="#111111")
                if number in (x0, x1-1) or min(number-x0, x1-1-number) >= 26:
                    label_x = max(1, min(x-9, panel.width-27))
                    draw.text((label_x, y+8), str(number), fill="#111111")
        require(panel.crop((left, top, left+crop.width, top+crop.height)).tobytes() == crop.tobytes(),
                "A guide changed source pixels")
        panels.append(panel)
    gap = 12
    sheet = Image.new("RGB", (sum(p.width for p in panels)+gap*(len(panels)-1),
                               max(p.height for p in panels)), "#464641")
    x = 0
    for panel in panels:
        sheet.paste(panel, (x, 0))
        x += panel.width+gap
    return sheet


def write_png(root, name, image):
    file = root / name
    image.save(file, format="PNG")
    file.chmod(0o600)
    return {"path": name, "sha256": digest(file.read_bytes())}


def packet_for_page(page, image, directory, Image, ImageDraw):
    require(image.size == SIZE and image.mode == "RGB", "Unexpected source raster")
    windows = []
    for label, box in boxes().items():
        name = f"p{page}-{label}"
        asset = write_png(directory, f"window-{name}.png", image.crop(box))
        windows.append({"id": name, "page": page, "box": list(box), **asset})
    sheets = []
    for side in TRANSECTS:
        name = f"p{page}-{side}"
        asset = write_png(directory, f"guide-{name}.png", guide(image, page, side, Image, ImageDraw))
        sheets.append({"id": name, "page": page, "side": side, **asset})
    overview = Image.new("RGB", SIZE, "#deddd7")
    for box in boxes().values():
        overview.paste(image.crop(box), box[:2])
    asset = write_png(directory, f"overview-p{page}.png", overview)
    return windows, sheets, {"id": f"p{page}", "page": page, **asset}


def registered(research, protocol, registration, commit):
    require(re.fullmatch(r"[a-f0-9]{40}", commit), "Supply a full registration commit")
    require(protocol == research / PROTOCOL, "Unexpected protocol path")
    protocol_raw = protocol.read_bytes()
    data = json.loads(protocol_raw)
    receipt = json.loads(registration.read_bytes())
    require(data["testId"] == TEST_ID and data["pages"] == list(PAGES)
            and data["imageSize"] == list(SIZE) and data["xCuts"] == list(X) and data["yCuts"] == list(Y)
            and data["windowOrder"] == list(ORDER) and data["guideHalfStripPx"] == HALF_STRIP
            and data["transects"] == {side: list(at) for side, at in TRANSECTS.items()},
            "Protocol differs from the frozen source scope")
    require(receipt["registrationCommit"] == commit and receipt["protocolSha256"] == digest(protocol_raw)
            and receipt["remoteHeadMatched"] is True and receipt["targetPixelsOpenedAtVerification"] is False,
            "Registration receipt differs")
    require(SOURCE in data["sourceHashes"] and SCRIPT in data["scriptHashes"], "Missing source or runner pin")
    require(Path(__file__).resolve() == research / SCRIPT, "Use the registered runner path")
    checkout = research.parent.parent
    pins = {**data["sourceHashes"], **data["scriptHashes"], PROTOCOL: digest(protocol_raw)}
    require(len(pins) == receipt["pinnedBlobsVerified"], "Registration pin count differs")
    for name, wanted in pins.items():
        file = (research / name).resolve()
        require(file.is_relative_to(research) and Path(name).as_posix() == name, "Invalid pin path")
        raw = file.read_bytes()
        actual = subprocess.check_output(["git", "-C", str(checkout), "show", f"{commit}:public/research/{name}"])
        require(raw == actual and digest(raw) == wanted, f"Current or registered pin changed: {name}")
    return data, digest(protocol_raw)


def run(args):
    research = args.research.resolve()
    spec, protocol_sha = registered(research, args.protocol.resolve(), args.registration_receipt,
                                    args.registration_commit)
    output = args.out.resolve()
    require(args.out.is_absolute() and not output.is_relative_to(research.parent.parent)
            and "public" not in {part.lower() for part in output.parts}, "Use a fresh private output")
    output.mkdir(mode=0o700)
    import fitz
    import PIL
    from PIL import Image, ImageDraw
    require(fitz.__version__ == spec["runtimeVersions"]["pymupdf"]
            and PIL.__version__ == spec["runtimeVersions"]["pillow"], "Image library version differs")
    windows, guides, overview, pages = [], [], [], []
    pdf_bytes = (research / SOURCE).read_bytes()
    require(digest(pdf_bytes) == spec["sourceHashes"][SOURCE], "Source changed after registration check")
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page_number in PAGES:
            page = document[page_number-73]
            entries = page.get_images(full=True)
            require(len(entries) == 1 and page.rotation == 0, "Unexpected PDF image count or orientation")
            raw = document.extract_image(entries[0][0])["image"]
            image_sha = digest(raw)
            require(image_sha == spec["embeddedImageSha256"][str(page_number)], "Embedded image changed")
            image = Image.open(BytesIO(raw)).convert("RGB")
            crops, strips, entire = packet_for_page(page_number, image, output, Image, ImageDraw)
            windows.extend(crops)
            guides.extend(strips)
            overview.append(entire)
            pages.append({"printedPage": page_number, "embeddedSha256": image_sha, "size": list(image.size)})
    require((len(windows), len(guides), len(overview)) == (32, 16, 4), "Packet population differs")
    manifest = {
        "version": 1, "testId": TEST_ID, "registrationCommit": args.registration_commit,
        "protocolSha256": protocol_sha, "sourcePdfSha256": digest(pdf_bytes), "preparedAtUTC": utc(),
        "runtimeVersions": spec["runtimeVersions"], "pages": pages,
        "windows": windows, "guides": guides, "overview": overview,
    }
    manifest_path = output / "PACKET_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    manifest_path.chmod(0o600)
    print(json.dumps({"windows": len(windows), "guides": len(guides), "overview": len(overview),
                      "packetManifestSha256": digest(manifest_path.read_bytes())}))


def self_test():
    from PIL import Image, ImageDraw
    require(len(boxes()) == 8 and set(boxes()) == set(ORDER), "Window population differs")
    area = sum((x1-x0)*(y1-y0) for x0,y0,x1,y1 in boxes().values())
    require(area + (X[2]-X[1])*(Y[2]-Y[1]) == SIZE[0]*SIZE[1], "Window coverage differs")
    dummy = Image.new("RGB", SIZE, (11, 132, 67))
    for side, coordinates in TRANSECTS.items():
        for at in coordinates:
            x0,y0,x1,y1 = guide_box(side, at)
            require(0 <= x0 < x1 <= SIZE[0] and 0 <= y0 < y1 <= SIZE[1], "Guide exceeds image")
        guide(dummy, 76, side, Image, ImageDraw)
    print(json.dumps({"syntheticControlsPassed": True, "targetPixelsOpened": False, "guideSheets": 4}))


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
    require(all((args.research, args.protocol, args.registration_commit, args.registration_receipt, args.out)),
            "Supply registration and private output arguments")
    run(args)


if __name__ == "__main__":
    main()
