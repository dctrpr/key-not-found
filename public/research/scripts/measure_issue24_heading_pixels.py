#!/usr/bin/env python3
"""Test local opposite-face print correspondence on pinned Issue 24 JPEGs."""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "analysis_outputs/continuation_20261111/heading_pixel_match/PROTOCOL.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_pages(source, numbers):
    raw = (ROOT / source["path"]).read_bytes()
    if digest(raw) != source["sha256"]:
        raise ValueError("PDF hash differs from protocol")
    pages, hashes = {}, {}
    with fitz.open(stream=raw, filetype="pdf") as pdf:
        for number in numbers:
            page = pdf[number - 73]
            images = page.get_images(full=True)
            if page.rotation != source["rotation"] or len(images) != 1 or images[0][1] != 0:
                raise ValueError(f"Unexpected image placement on printed page {number}")
            raw_image = pdf.extract_image(images[0][0])["image"]
            hashes[number] = digest(raw_image)
            with Image.open(BytesIO(raw_image)) as image:
                if image.format != "JPEG" or list(image.size) != source["dimensions"]:
                    raise ValueError(f"Unexpected embedded image on printed page {number}")
                upright = image.convert("L")
                if source["rotation"] == 180:
                    upright = upright.transpose(Image.Transpose.ROTATE_180)
                pages[number] = np.asarray(upright, dtype=np.float64)
    return pages, hashes


def box_blur(image, radius):
    width = 2 * radius + 1
    for axis in (0, 1):
        view = np.swapaxes(image, 0, axis)
        prefix = np.pad(view, ((radius, radius), (0, 0)), mode="edge").cumsum(axis=0)
        prefix = np.pad(prefix, ((1, 0), (0, 0)))
        image = np.swapaxes((prefix[width:] - prefix[:-width]) / width, 0, axis)
    return image


def sums(image, height, width):
    integral = np.pad(image.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    return (integral[height:, width:] - integral[:-height, width:]
            - integral[height:, :-width] + integral[:-height, :-width])


def score_map(receiver, template):
    template = template - template.mean()
    height, width = template.shape
    shape = tuple(1 << (a + b - 2).bit_length() for a, b in zip(receiver.shape, template.shape))
    convolution = np.fft.irfft2(
        np.fft.rfft2(receiver, s=shape, axes=(0, 1))
        * np.fft.rfft2(template[::-1, ::-1], s=shape, axes=(0, 1)), s=shape, axes=(0, 1),
    )[height - 1:receiver.shape[0], width - 1:receiver.shape[1]]
    energy = sums(receiver ** 2, height, width) - sums(receiver, height, width) ** 2 / template.size
    denominator = np.sqrt(np.maximum(energy, 0) * np.sum(template ** 2))
    return np.divide(convolution, denominator, out=np.zeros_like(convolution), where=denominator > 1e-8)


def window(image, box, center, search):
    x0, y0, x1, y1 = box
    dx, dy = center
    sx, sy = search
    bounds = (x0 + dx - sx, y0 + dy - sy, x1 + dx + sx, y1 + dy + sy)
    left, top, right, bottom = bounds
    if not (0 <= left < right <= image.shape[1] and 0 <= top < bottom <= image.shape[0]):
        raise ValueError(f"Search outside raster: {bounds}")
    return image[top:bottom, left:right]


def maximum(values, center, search, guard):
    y, x = np.unravel_index(values.argmax(), values.shape)
    yy, xx = np.indices(values.shape)
    outside = (abs(xx - x) > guard) | (abs(yy - y) > guard)
    return {"offset": [int(x) + center[0] - search[0], int(y) + center[1] - search[1]],
            "score": float(values[y, x]), "runnerUp": float(values[outside].max()),
            "edge": bool(x in (0, values.shape[1] - 1) or y in (0, values.shape[0] - 1))}


def measure_feature(feature, reference, receivers, settings):
    box = feature["box"]
    x0, y0, x1, y1 = box
    template = reference[y0:y1, x0:x1]
    search = settings["searchXY"]
    guard = settings["runnerGuard"]
    center = [0, 0]
    receiver = receivers[74]

    def compare(image, pattern, offset):
        values = score_map(window(image, box, offset, search), pattern)
        return maximum(values, offset, search, guard), values

    correct, values = compare(receiver, template, center)
    controls = {"wrong-handed-template": compare(receiver, template[:, ::-1], center)[0]}
    for number in settings["wrongFaces"]:
        controls[f"wrong-receiver-p{number}"] = compare(receivers[number], template, center)[0]
    for offset in settings["displacedControls"]:
        controls[f"same-receiver-at-{offset[0]}-{offset[1]}"] = compare(receiver, template, offset)[0]

    # Inject a fixed weak copy into a wrong-face window to check the score/search plumbing.
    # A recovery here says nothing about the amplitude or visibility of actual ghost ink.
    known = settings["syntheticOffsetXY"]
    sx, sy = search
    yy, xx = sy + known[1], sx + known[0]
    wrong = receivers[settings["wrongFaces"][0]]
    synthetic = window(wrong, box, center, search).copy()
    region = synthetic[yy:yy + template.shape[0], xx:xx + template.shape[1]]
    region += settings["syntheticScale"] * (template - template.mean())
    injected = maximum(score_map(synthetic, template), center, search, guard)
    injected["recovered"] = distance(known, injected["offset"]) <= 2

    control_maximum = max(control["score"] for control in controls.values())
    gate = settings["gate"]
    passes = (not correct["edge"] and correct["score"] >= gate["minimumScore"]
              and correct["score"] - correct["runnerUp"] >= gate["minimumRunnerGap"]
              and correct["score"] - control_maximum >= gate["minimumControlGap"]
              and injected["recovered"])
    return {**feature, "match": correct, "controls": controls, "maxControl": control_maximum,
            "synthetic": injected, "localPass": passes}, values


def distance(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def analyze(source, settings):
    images, hashes = load_pages(source, [74, 75, *settings["wrongFaces"]])
    reference_image = images.pop(75)
    reference = box_blur(reference_image, 1) - box_blur(reference_image, 12)
    clip = settings["clip"]
    receivers = {}
    for number in tuple(images):
        image = images.pop(number)
        filtered = box_blur(image, 1) - box_blur(image, 12)
        receivers[number] = np.clip(filtered[:, ::-1], -clip, clip)
    measurements = [measure_feature(feature, reference, receivers, settings) for feature in source["features"]]
    calibration = [row for row, _ in measurements if row["role"] == "calibration"]
    holdouts = [row for row, _ in measurements if row["role"] == "holdout"]
    first, second = (row["match"]["offset"] for row in calibration)
    shift = None
    if all(row["localPass"] for row in calibration) and distance(first, second) <= settings["calibrationTolerance"]:
        shift = [round((a + b) / 2) for a, b in zip(first, second)]
    supported = []
    for row, values in measurements:
        if row["role"] == "holdout":
            residual = distance(shift, row["match"]["offset"]) if shift is not None else None
            sx, sy = settings["searchXY"]
            row["frozenShiftScore"] = float(values[sy + shift[1], sx + shift[0]]) if shift is not None else None
            row["offsetResidual"] = residual
            row["holdoutPass"] = bool(row["localPass"] and residual is not None
                                      and residual <= settings["holdoutTolerance"]
                                      and row["frozenShiftScore"] - row["maxControl"] >= settings["gate"]["minimumControlGap"])
            if row["holdoutPass"]:
                supported.append(row)
    spanning = any(abs(a["box"][1] - b["box"][1]) >= settings["holdoutVerticalSeparation"]
                   for a in supported for b in supported)
    status = ("local-translation-supported" if spanning else
              "heading-only" if shift is not None else
              "isolated-local-match" if any(row["localPass"] for row in calibration) else "no-heading-lock")
    return {"name": source["name"], "embeddedJpegSha256": hashes, "features": calibration + holdouts,
            "calibrationSpread": distance(first, second), "headingShiftXY": shift, "status": status}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New path for the JSON result")
    args = parser.parse_args()
    raw = PROTOCOL.read_bytes()
    protocol = json.loads(raw)
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              "runs": [analyze(source, protocol["settings"]) for source in protocol["sources"]]}
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
