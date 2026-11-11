#!/usr/bin/env python3
"""Measure shared print edges without reading or classifying glyphs."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from math import hypot
from pathlib import Path
from statistics import median

import fitz
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "analysis_outputs/continuation_20261111/page78_right_anchor"


def digest(data):
    return sha256(data).hexdigest()


def pinned(spec):
    data = (ROOT / spec["path"]).read_bytes()
    if digest(data) != spec["sha256"]:
        raise ValueError(f"Pinned input differs: {spec['path']}")
    return data


def load_pages(spec, pages):
    images, hashes = {}, {}
    with fitz.open(stream=pinned(spec), filetype="pdf") as document:
        for number in pages:
            page = document[spec["pdfIndexes"][str(number)]]
            images_info = page.get_images(full=True)
            if page.rotation != spec["rotation"] or len(images_info) != 1 or images_info[0][1]:
                raise ValueError("Page image count, mask or orientation differs")
            raw = document.extract_image(images_info[0][0])["image"]
            hashes[number] = digest(raw)
            if hashes[number] != spec["embeddedJpegSha256"][str(number)]:
                raise ValueError(f"Embedded image differs on printed page {number}")
            with Image.open(BytesIO(raw)) as image:
                if image.format != "JPEG" or list(image.size) != spec["size"]:
                    raise ValueError("Embedded raster geometry differs")
                upright = image.convert("RGB")
                if spec["rotation"] == 180:
                    upright = upright.transpose(Image.Transpose.ROTATE_180)
                images[number] = np.asarray(upright)
    return images, hashes


def average_baseline(reader_a, reader_b):
    return [[(x + y) / 2 for x, y in zip(a, b)] for a, b in zip(reader_a["baseline"], reader_b["baseline"])]


def slope(line):
    (x0, y0), (x1, y1) = line
    return (y1 - y0) / (x1 - x0)


def row_window(name, row_id, canonical, readers, settings):
    if name == "high":
        _, y0, _, y1 = canonical[row_id]["locator"]["box"]
        if canonical[row_id]["locator"]["rotate_ccw_degrees"] != 0:
            raise ValueError("High line locator is not upright")
        return (y0 - settings["highVerticalPadding"], y1 + settings["highVerticalPadding"]), None
    low_id = row_id.replace("r", "-l", 1)
    a, b = [reader[low_id] for reader in readers]
    return None, average_baseline(a, b)


def strip_pixels(image, block, y_band, baseline, settings):
    height, width = image.shape[:2]
    x0, x1 = [round(width * factor) for factor in block["laneXFraction"]]
    if baseline is not None:
        xref, yref = baseline[0]
        m = slope(baseline)
        above, below = settings["lowBaselineStrip"]
        y_ends = [yref + m * (x - xref) for x in (x0, x1 - 1)]
        y0, y1 = int(min(y_ends)) - above - 1, int(max(y_ends)) + below + 2
    else:
        y0, y1 = y_band
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError("Row window falls outside the raster")
    patch = image[y0:y1, x0:x1]
    ink = patch.max(axis=2) if block["polarity"] == "dark-on-light" else 255 - patch.min(axis=2)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    allowed = np.ones(ink.shape, dtype=bool)
    if baseline is not None:
        offset = yy - (yref + m * (xx - xref))
        allowed = (offset >= -above) & (offset <= below)
    return ink, allowed, xx, yy, [x0, y0, x1, y1]


def span(values):
    return max(values) - min(values)


def classify(left, right, centers, width, settings):
    l, r, c = (span(values) / width for values in (left, right, centers))
    tight, variation = settings["tightEdgeFraction"], settings["raggedEdgeFraction"]
    ratio = settings["minimumRaggedToTightRatio"]
    if r <= tight and l >= variation and l >= ratio * r:
        label = "right"
    elif l <= tight and r >= variation and r >= ratio * l:
        label = "left"
    elif c <= tight and min(l, r) >= variation and min(l, r) >= ratio * c:
        label = "center"
    else:
        label = "mixed-or-unresolved"
    return {"classification": label, "leftSpanPx": span(left), "rightSpanPx": span(right),
            "centerSpanPx": span(centers), "leftSpanFraction": l, "rightSpanFraction": r, "centerSpanFraction": c}


def measure_block(image, block, name, canonical, readers, settings):
    width = image.shape[1]
    windows = [row_window(name, row_id, canonical, readers, settings) for row_id in block["rowIds"]]
    deskew = median([slope(line) for _, line in windows]) if name == "low" else 0.0
    rows = []
    for row_id, (band, line) in zip(block["rowIds"], windows):
        ink, allowed, xx, yy, box = strip_pixels(image, block, band, line, settings)
        projections = (xx + deskew * yy) / hypot(1, deskew)
        edges = []
        for threshold in settings["shadeThresholds"]:
            mask = (ink <= threshold) & allowed
            pixel_count = int(mask.sum())
            if pixel_count < settings["minimumInkPixels"]:
                edges.append({"threshold": threshold, "inkPixels": pixel_count, "invalid": "insufficient-contrast"})
                continue
            q = settings["edgeQuantile"]
            left, right = np.quantile(projections[mask], [q, 1 - q]).tolist()
            native_left, native_right = np.quantile(xx[mask], [q, 1 - q]).tolist()
            edge = {"threshold": threshold, "inkPixels": pixel_count, "left": left, "right": right,
                    "center": (left + right) / 2, "nativeLeft": native_left, "nativeRight": native_right}
            if native_left - box[0] < 3 or box[2] - 1 - native_right < 3:
                edge["invalid"] = "near-lane-boundary"
            edges.append(edge)
        rows.append({"id": row_id, "windowXYXY": box, "rowBaseline": line, "edges": edges})

    scores = []
    for index, threshold in enumerate(settings["shadeThresholds"]):
        selected = [row["edges"][index] for row in rows]
        invalid_rows = [row["id"] for row, edge in zip(rows, selected) if "invalid" in edge]
        if invalid_rows:
            scores.append({"threshold": threshold, "classification": "invalid", "invalidRows": invalid_rows})
            continue
        endpoints = [[edge[label] for edge in selected] for label in ("left", "right", "center")]
        scores.append({"threshold": threshold, **classify(*endpoints, width, settings)})
    labels = {row["classification"] for row in scores}
    classification = "invalid" if "invalid" in labels else (
        labels.pop() if len(labels) == 1 else "threshold-sensitive"
    )
    return {"id": block["id"], "printedPage": block["page"], "blockSlope": deskew,
            "classification": classification,
            "thresholdResults": scores, "rows": rows}


def analyze(spec):
    canonical = {row["id"]: row for row in json.loads(pinned(spec["canonicalRows"]))["rows"]}
    readers = [{row["id"]: row for row in json.loads(pinned(reader))["rows"]} for reader in spec["lowReaderReceipts"]]
    for block in spec["blocks"]:
        for row_id in block["rowIds"]:
            if canonical[row_id]["page"] != block["page"]:
                raise ValueError("Declared row is on another page")
    numbers = sorted({block["page"] for block in spec["blocks"]})
    observations = {}
    for source in spec["sources"]:
        name = source["id"]
        images, hashes = load_pages(source, numbers)
        observations[name] = {"embeddedJpegSha256": hashes, "size": source["size"],
                              "blocks": [measure_block(images[block["page"]], block, name, canonical, readers, spec["settings"])
                                         for block in spec["blocks"]]}
    both_right = [block["id"] for block in spec["blocks"] if all(
        next(row for row in source["blocks"] if row["id"] == block["id"])["classification"] == "right"
        for source in observations.values())]
    return {"scans": observations, "rightAlignedInBoth": both_right,
            "targetRightAlignedInBoth": spec["targetBlock"] in both_right,
            "otherRightAlignedInBoth": [name for name in both_right if name != spec["targetBlock"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    raw = (DIRECTORY / "PROTOCOL.json").read_bytes()
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              **analyze(json.loads(raw))}
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
