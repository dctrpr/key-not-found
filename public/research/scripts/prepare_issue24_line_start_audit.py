#!/usr/bin/env python3
"""Prepare registered native page crops for the Issue 24 line-start audit."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zlib


TEST_ID = "issue24-line-start-audit"
PROTOCOL = "analysis_outputs/continuation_20261111/line_start_audit/PROTOCOL.json"
SCRIPT = "scripts/prepare_issue24_line_start_audit.py"
SOURCE = {
    "path": "keyser bitcoin .pdf",
    "sha256": "dcd13efd0e46c49927dc8ec2e38a96fffc20d92fde7434151250fd6b9c62e6f4",
    "pdfPages": {"75": 2, "76": 3, "77": 4, "78": 5, "79": 6},
    "nativeDimensions": [2040, 2805],
    "rotation": 0,
}
CROPS = (("top", (0, 0, 2040, 1483)), ("bottom", (0, 1322, 2040, 2805)))
MAX_JSON = 1_000_000
MAX_FILE = 32_000_000

# Page 75 comes from the second-scan packet. Pages 76–79 come from RASTER_VERIFICATION.json.
JPEG_PINS = {'75': '14b61ce3980ee0af4f23df87f19b4d0ffcce2ece2f25fa6bc2b02bf6d7336b72',
 '76': '26d6e8002fe1d86b5ba42656d34589b738659d01660e99a6f6c62f30dd7543fd',
 '77': 'eeaf8a1d9ba8f13873725a0c00d224a8c90bfd2c2610cd2766bf29a922d44c8f',
 '78': '356a99c43703ffa467e34e2aaf7fc91f2a23dbe5170f89c60dd0282b78bd1830',
 '79': '961a53e248be9a672ed4a90f63b40f0c9066bbf1e47ad9903123043c2cbde247'}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def read_bounded(path, limit):
    require(path.is_file() and path.stat().st_size <= limit, "Input missing or oversized")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "Input grew beyond its size limit")
    return raw


def parse_json(raw):
    def unique_fields(pairs):
        fields = dict(pairs)
        require(len(fields) == len(pairs), "Repeated JSON field")
        return fields

    def invalid_number(_):
        raise ValidationError("Nonfinite JSON number")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_fields, parse_constant=invalid_number)


def checked_path(root, relative):
    require(isinstance(relative, str) and bool(relative), "Missing registered path")
    name = Path(relative)
    require(not name.is_absolute() and ".." not in name.parts and name.as_posix() == relative,
            "Expected a canonical relative path")
    path = (root / name).resolve(strict=True)
    require(path.is_relative_to(root) and path.relative_to(root).as_posix() == relative,
            "Registered path alias or escape")
    return path


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def validate_receipt(receipt, commit, protocol_sha, pins):
    require(isinstance(receipt, dict) and set(receipt) == {
        "registrationCommit", "protocolSha256", "verifiedAtUTC", "checkedPins",
        "remoteHeadMatched", "targetPixelsOpenedAtVerification",
    }, "Unexpected registration receipt fields")
    require(receipt["registrationCommit"] == commit and receipt["protocolSha256"] == protocol_sha
            and receipt["checkedPins"] == pins and receipt["remoteHeadMatched"] is True
            and receipt["targetPixelsOpenedAtVerification"] is False, "Pre-pixel receipt differs")
    recorded = receipt["verifiedAtUTC"]
    require(isinstance(recorded, str)
            and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", recorded),
            "Expected a UTC registration time")
    verified = datetime.fromisoformat(recorded[:-1] + "+00:00")
    require(verified < datetime.now(timezone.utc), "Registration must precede preparation")


def verify_registration(research, protocol, receipt_path, commit):
    require(re.fullmatch(r"[a-f0-9]{40}", commit), "Supply the complete Git commit")
    require(research.name == "research" and research.parent.name == "public", "Unexpected research root")
    checkout = research.parent.parent
    require(protocol == checked_path(research, PROTOCOL), "Unexpected protocol path")
    protocol_bytes = read_bounded(protocol, MAX_JSON)
    spec = parse_json(protocol_bytes)
    require(spec["testId"] == TEST_ID and spec["source"] == SOURCE
            and type(spec["source"]["rotation"]) is int
            and all(type(index) is int for index in spec["source"]["pdfPages"].values())
            and spec["cropXYXY"] == [list(box) for _, box in CROPS]
            and all(type(edge) is int for box in spec["cropXYXY"] for edge in box)
            and spec["embeddedJpegSha256ByPage"] == JPEG_PINS,
            "Registered source, JPEG pins or crop differs")
    pins = spec["registrationPins"]
    require(isinstance(pins, list) and bool(pins), "Missing registration pins")
    registered = {}
    for pin in pins:
        require(isinstance(pin, dict) and set(pin) == {"path", "sha256"}
                and isinstance(pin["path"], str) and pin["path"] not in registered
                and isinstance(pin["sha256"], str) and re.fullmatch(r"[a-f0-9]{64}", pin["sha256"]),
                "Malformed or repeated registration pin")
        registered[pin["path"]] = pin["sha256"]
    source_name = f"public/research/{SOURCE['path']}"
    script_name = f"public/research/{SCRIPT}"
    require(registered.get(source_name) == SOURCE["sha256"]
            and registered.get(script_name) == digest(read_bounded(Path(__file__), MAX_JSON)),
            "Source or executing code pin differs")
    receipt_bytes = read_bounded(receipt_path, MAX_JSON)
    protocol_sha = digest(protocol_bytes)
    validate_receipt(parse_json(receipt_bytes), commit, protocol_sha, pins)

    git_executable = shutil.which("git") if (checkout / ".git").exists() else None

    def git(*args):
        return subprocess.run([git_executable, "-C", str(checkout), *args], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=30, check=True).stdout

    def check_blob(name, current):
        if git_executable is not None:
            blob = f"{commit}:{name}"
            require(int(git("cat-file", "-s", blob)) == len(current)
                    and git("cat-file", "blob", blob) == current, "Registered Git blob differs")

    if git_executable is not None:
        root = Path(os.fsdecode(git("rev-parse", "--show-toplevel")).strip()).resolve()
        require(root == checkout and git("cat-file", "-t", commit) == b"commit\n", "Invalid registered Git object")
        check_blob(f"public/research/{PROTOCOL}", protocol_bytes)

    source_bytes = None
    for name, expected in registered.items():
        current = read_bounded(checked_path(checkout, name), MAX_FILE)
        require(digest(current) == expected, "Current file differs from its registration pin")
        check_blob(name, current)
        if name == source_name:
            source_bytes = current
    return source_bytes, protocol_sha, digest(receipt_bytes)


def fresh_private_output(out, checkout):
    entered = out if out.is_absolute() else Path.cwd() / out
    resolved = entered.resolve()
    require(resolved.parent.is_dir() and not entered.is_symlink() and not resolved.exists(),
            "Use a fresh output directory with an existing parent")
    for path in (entered, Path(os.path.abspath(entered)), resolved,
                 *(ancestor.resolve() for ancestor in entered.parents)):
        require(not path.is_relative_to(checkout) and "public" not in {part.lower() for part in path.parts},
                "Output must be outside the public checkout")
    return resolved


def encode_crop(Image, upright, box, path, page):
    crop = upright.crop(box)
    pixels = crop.tobytes()
    # A fresh RGB image excludes embedded profiles and comments from the PNG.
    clean = Image.frombytes("RGB", crop.size, pixels)
    stream = BytesIO()
    clean.save(stream, format="PNG", compress_level=9)
    png = stream.getvalue()
    return {"path": path, "page": page, "cropXYXY": list(box), "width": crop.width,
            "height": crop.height, "rgbSha256": digest(pixels), "sha256": digest(png)}, png


def read_page(pdf, Image, printed_page):
    index = SOURCE["pdfPages"][printed_page]
    page = pdf[index]
    images = page.get_images(full=True)
    require(page.rotation == SOURCE["rotation"] and len(images) == 1, "Page rotation or image count differs")
    image_info = images[0]
    require(image_info[0] > 0 and image_info[1] == 0
            and list(image_info[2:4]) == SOURCE["nativeDimensions"], "Embedded image geometry differs")
    extracted = pdf.extract_image(image_info[0])
    require(extracted["ext"] == "jpeg", "Expected the sole embedded JPEG")
    jpeg = extracted["image"]
    jpeg_sha = digest(jpeg)
    require(jpeg_sha == JPEG_PINS[printed_page], "Embedded JPEG differs from its pin")
    with Image.open(BytesIO(jpeg)) as image:
        require(image.format == "JPEG" and list(image.size) == SOURCE["nativeDimensions"], "JPEG dimensions differ")
        upright = image.convert("RGB")
    assets, buffers = [], {}
    for name, box in CROPS:
        path = f"assets/p{printed_page}-{name}.png"
        asset, png = encode_crop(Image, upright, box, path, int(printed_page))
        assets.append(asset)
        buffers[path] = png
    metadata = {"embeddedJpegSha256": jpeg_sha, "uprightRGBSha256": digest(upright.tobytes())}
    return metadata, assets, buffers


def write_private(path, raw):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
        stream.write(raw)


def prepare(args):
    research = args.research.resolve(strict=True)
    out = fresh_private_output(args.out, research.parent.parent)
    source, protocol_sha, receipt_sha = verify_registration(
        research, args.protocol.resolve(strict=True), args.registration_receipt, args.registration_commit)

    import fitz
    import PIL
    from PIL import Image

    pages, assets, pngs = {}, [], {}
    with fitz.open(stream=source, filetype="pdf") as pdf:
        require(not pdf.needs_pass and len(pdf) == 8, "Source document geometry differs")
        for page in SOURCE["pdfPages"]:
            metadata, page_assets, buffers = read_page(pdf, Image, page)
            pages[page] = metadata
            assets.extend(page_assets)
            pngs.update(buffers)
    require(len(pages) == 5 and len(assets) == len(pngs) == 10, "Packet population differs")
    manifest = {"version": 1, "testId": TEST_ID, "registrationCommit": args.registration_commit,
                "protocolSha256": protocol_sha, "registrationReceiptSha256": receipt_sha,
                "preparedAtUTC": utc(), "source": SOURCE, "cropXYXY": [list(box) for _, box in CROPS],
                "runtimeVersions": {"pymupdf": fitz.VersionBind, "pillow": PIL.__version__,
                                    "zlib": zlib.ZLIB_RUNTIME_VERSION},
                "pages": pages, "assets": assets}
    raw = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.mkdir(mode=0o700)
    (out / "assets").mkdir(mode=0o700)
    for path, png in pngs.items():
        write_private(out / path, png)
    write_private(out / "MANIFEST.json", raw)
    print(json.dumps({"testId": TEST_ID, "pages": len(pages), "pngAssets": len(pngs),
                      "manifestSha256": digest(raw)}))


def self_test():
    from PIL import Image

    upright = Image.frombytes("RGB", (8, 7), bytes(range(168)))
    rows = []
    for name, box in (("top", (0, 0, 8, 4)), ("bottom", (0, 3, 8, 7))):
        path = f"assets/p75-{name}.png"
        asset, png = encode_crop(Image, upright, box, path, 75)
        require((asset, png) == encode_crop(Image, upright, box, path, 75), "Synthetic replay differs")
        with Image.open(BytesIO(png)) as decoded:
            pixels = decoded.tobytes()
            require(decoded.size == (8, 4) and decoded.mode == "RGB" and not decoded.info
                    and pixels == upright.crop(box).tobytes() and asset["sha256"] == digest(png)
                    and asset["rgbSha256"] == digest(pixels), "Synthetic crop pixels differ")
            rows.append(pixels)
    require(rows[0][-24:] == rows[1][:24], "Synthetic overlap differs")
    print(json.dumps({"passed": True, "syntheticPngs": len(rows), "exactOverlap": True, "targetReads": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    for option in ("research", "protocol", "registration-receipt", "out"):
        parser.add_argument(f"--{option}", type=Path)
    parser.add_argument("--registration-commit")
    args = parser.parse_args()
    values = (args.research, args.protocol, args.registration_receipt, args.out, args.registration_commit)
    try:
        if args.self_test:
            require(not any(values), "Synthetic test accepts no registered paths")
            self_test()
        else:
            require(all(values), "Supply all five preparation arguments")
            prepare(args)
        return 0
    except ValidationError as error:
        print(str(error), file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError, subprocess.SubprocessError):
        print("Line-start packet preparation did not complete", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
