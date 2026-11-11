#!/usr/bin/env python3
"""Measure exact pixel coverage of the frozen G07 normal-view box controls."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

EXPECTED_BOXES = "2d7a6b97564ec8e85c3ac086a4dba87e9631666d3329d0a709c514d88b627fa0"
EXPECTED_SIZE = [2544, 3264]
PADDING = 8


def area(rectangle):
    left, top, right, bottom = rectangle
    return (right - left) * (bottom - top)


def intersect(first, second):
    left, top = (max(first[i], second[i]) for i in (0, 1))
    right, bottom = (min(first[i], second[i]) for i in (2, 3))
    return (left, top, right, bottom) if left < right and top < bottom else None


def covered_area(rectangles):
    """Sum disjoint x strips, using the union of y intervals in each."""
    cuts = sorted({value for rect in rectangles for value in (rect[0], rect[2])})
    result = 0
    for left, right in zip(cuts, cuts[1:]):
        intervals = sorted((top, bottom) for a, top, b, bottom in rectangles if a <= left < b)
        last = 0
        height = 0
        for top, bottom in intervals:
            height += max(0, bottom - max(last, top))
            last = max(last, bottom)
        result += (right-left)*height
    return result


def pad(rectangle):
    left, top, right, bottom = rectangle
    width, height = EXPECTED_SIZE
    return max(0, left-PADDING), max(0, top-PADDING), min(width, right+PADDING), min(height, bottom+PADDING)


def audit(raw, packet_raw):
    digest = sha256(raw).hexdigest()
    if digest != EXPECTED_BOXES:
        raise ValueError("Unexpected baseline coordinates")
    data = json.loads(raw)
    packet = json.loads(packet_raw)
    rows = data["records"]
    pages = {page:[] for page in range(73,81)}
    mirror = [row for row in rows if row["orientation"] == "horizontal-mirror"]
    targets = packet["targets"]
    if len(mirror) != len(targets) or len(targets) != 114:
        raise ValueError("Wrong target population")
    for record, target in zip(mirror, targets):
        region = pad(record["uprightPixelEnclosure"])
        page = record["printedPage"]
        if (record["imageDimensionsPx"] != EXPECTED_SIZE or page != target["printedPage"]
                or record["publicStreamId"] != target["publicStreamId"]
                or list(region) != target["pixelBounds"]):
            raise ValueError("Packet crop differs from the frozen target")
        pages[page].append(region)
    per_page = {str(page):Counter() for page in pages}
    metrics = []
    for row in rows:
        if row["orientation"] != "normal":
            continue
        rect = row["uprightPixelEnclosure"]
        page = row["printedPage"]
        clips = [part for region in pages[page] if (part := intersect(rect, region)) is not None]
        hit = covered_area(clips)
        total = area(rect)
        if not 0 <= hit <= total or not total:
            raise ValueError("Invalid pixel coverage")
        state = "disjoint" if hit == 0 else "full" if hit == total else "partial"
        metrics.append({"printedPage":page,"publicStreamId":row["publicStreamId"],
                        "pixels":total,"coveredPixels":hit,"status":state})
        per_page[str(page)][state] += 1
    if len(metrics) != 207:
        raise ValueError("Wrong comparison population")
    return {
        "version":1,"testId":"g07-mirror-glyph-orientation",
        "baselineBoxesSha256":digest,"packetManifestSha256":sha256(packet_raw).hexdigest(),
        "counts":dict(Counter(row["status"] for row in metrics)),"normalBoxCount":len(metrics),
        "targetBoxCount":len(targets),
        "perPage":{page:dict(counts) for page,counts in per_page.items()},
        "normalBoxCoverage":metrics,
        "scope":"Half-open integer pixel union of padded mirror-review windows over archived normal-view detector rectangles. Geometry only.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline",required=True,type=Path)
    parser.add_argument("--packet-manifest",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    output=audit(args.baseline.read_bytes(),args.packet_manifest.read_bytes())
    with args.out.open("x",encoding="utf-8") as handle:
        json.dump(output,handle,indent=2)
        handle.write("\n")
    print(json.dumps(output["counts"]))


if __name__ == "__main__":
    main()
