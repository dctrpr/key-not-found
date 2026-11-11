#!/usr/bin/env python3
"""Prepare the registered lower-resolution heading views in two stages."""
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


TEST_ID = "issue24-second-scan-heading-review"
PROTOCOL = "analysis_outputs/continuation_20261111/second_scan_heading_review/PROTOCOL.json"
SCRIPT = "scripts/prepare_issue24_second_scan_heading.py"
SOURCE = {
    "path": "keyser bitcoin .pdf",
    "sha256": "dcd13efd0e46c49927dc8ec2e38a96fffc20d92fde7434151250fd6b9c62e6f4",
    "pdfPages": {"74": 1, "75": 2},
    "nativeDimensions": [2040, 2805],
    "rotation": 0,
}
CROP = (0, 0, 2040, 1683)
STAGES = (("stage1", 74), ("stage2", 75))
MAX_JSON = 1_000_000
MAX_FILE = 32_000_000


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
            and spec["cropXYXY"] == list(CROP) and all(type(edge) is int for edge in spec["cropXYXY"]),
            "Registered source or crop differs")
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


def crop_pair(Image, upright, box, stage):
    crop = upright.crop(box)
    variants = (("u.png", "upright", crop),
                ("r.png", "horizontal-mirror", crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)))
    assets, buffers = [], {}
    for name, orientation, image in variants:
        pixels = image.tobytes()
        # Build a fresh RGB image to exclude JPEG profile and comment metadata.
        clean = Image.frombytes("RGB", image.size, pixels)
        stream = BytesIO()
        clean.save(stream, format="PNG", compress_level=9)
        png = stream.getvalue()
        path = f"{stage}/{name}"
        assets.append({"path": path, "orientation": orientation, "width": image.width,
                       "height": image.height, "rgbSha256": digest(pixels), "sha256": digest(png)})
        buffers[path] = png
    return assets, buffers


def read_stage(pdf, Image, stage, printed_page):
    index = SOURCE["pdfPages"][str(printed_page)]
    page = pdf[index]
    images = page.get_images(full=True)
    require(page.rotation == SOURCE["rotation"] and len(images) == 1, "Page rotation or image count differs")
    image_info = images[0]
    require(image_info[0] > 0 and image_info[1] == 0
            and list(image_info[2:4]) == SOURCE["nativeDimensions"], "Embedded image geometry differs")
    extracted = pdf.extract_image(image_info[0])
    require(extracted["ext"] == "jpeg", "Expected the sole embedded JPEG")
    jpeg = extracted["image"]
    with Image.open(BytesIO(jpeg)) as image:
        require(image.format == "JPEG" and list(image.size) == SOURCE["nativeDimensions"], "JPEG dimensions differ")
        upright = image.convert("RGB")
    assets, buffers = crop_pair(Image, upright, CROP, stage)
    metadata = {"printedPage": printed_page, "pdfPageIndex": index,
                "embeddedJpegSha256": digest(jpeg), "uprightRGBSha256": digest(upright.tobytes()),
                "assets": assets}
    return metadata, buffers


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

    stages, pngs = {}, {}
    with fitz.open(stream=source, filetype="pdf") as pdf:
        require(not pdf.needs_pass and len(pdf) == 8, "Source document geometry differs")
        for stage, page in STAGES:
            metadata, buffers = read_stage(pdf, Image, stage, page)
            stages[stage] = metadata
            pngs.update(buffers)
    manifest = {"version": 1, "testId": TEST_ID, "registrationCommit": args.registration_commit,
                "protocolSha256": protocol_sha, "registrationReceiptSha256": receipt_sha,
                "preparedAtUTC": utc(), "source": SOURCE, "cropXYXY": list(CROP),
                "runtimeVersions": {"pymupdf": fitz.VersionBind, "pillow": PIL.__version__,
                                    "zlib": zlib.ZLIB_RUNTIME_VERSION},
                "stages": stages}
    raw = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.mkdir(mode=0o700)
    for stage, _ in STAGES:
        (out / stage).mkdir(mode=0o700)
    for path, png in pngs.items():
        write_private(out / path, png)
    write_private(out / "MANIFEST.json", raw)
    print(json.dumps({"testId": TEST_ID, "stages": len(stages), "pngAssets": len(pngs),
                      "manifestSha256": digest(raw)}))


def self_test():
    from PIL import Image

    upright = Image.frombytes("RGB", (7, 5), bytes(range(105)))
    box = (1, 1, 6, 4)
    assets, pngs = crop_pair(Image, upright, box, "stage1")
    require((assets, pngs) == crop_pair(Image, upright, box, "stage1"), "Synthetic replay differs")
    for asset in assets:
        png = pngs[asset["path"]]
        with Image.open(BytesIO(png)) as decoded:
            expected = upright.crop(box)
            if asset["orientation"] == "horizontal-mirror":
                expected = expected.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            require(decoded.size == (5, 3) and decoded.mode == "RGB" and decoded.tobytes() == expected.tobytes()
                    and not decoded.info and asset["sha256"] == digest(png)
                    and asset["rgbSha256"] == digest(decoded.tobytes()), "Synthetic crop pixels differ")
    print(json.dumps({"passed": True, "syntheticPngs": len(pngs), "targetReads": 0}))


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
        print("Heading packet preparation did not complete", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
