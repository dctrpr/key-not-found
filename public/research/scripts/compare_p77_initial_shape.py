#!/usr/bin/env python3
"""Compare one printed initial against same-row case controls in each scan."""
import argparse
from itertools import product
import json
from pathlib import Path

import numpy as np

from measure_p77_initial_transfer import PROTOCOL, case_class, checked_crop, digest, ink_ratio, load, low_target_box


def measures(image, box, backgrounds, settings, shifts):
    rows = []
    for dx, dy, (percentile, background) in product(shifts, shifts, backgrounds.items()):
        x0, y0, x1, y1 = box
        shifted = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
        pixels = np.asarray(checked_crop(image, shifted), dtype=float)
        rows.append({"offsetXY": [dx, dy], "backgroundPercentile": percentile,
                     **ink_ratio(pixels, background, settings)})
    return rows


def envelope(rows):
    values = [row["upperToLowerRatio"] for row in rows]
    return [min(values), max(values)] if all(value is not None for value in values) else None


def analyze(optical, design):
    settings = optical["settings"]
    train = [pair for pair in optical["ordinaryPairs"] if pair["role"] == "fit"]
    neighbor = next(pair for pair in optical["ordinaryPairs"] if pair["id"] == optical["requiredNearTargetHoldout"])
    high = optical["targetHighBox"]
    target_boxes = {"high": high, "low": low_target_box(high, neighbor)}
    results = {}
    for source in optical["sources"]:
        name = source["id"]
        image = load(source)
        backgrounds = {percentile: float(np.median([np.percentile(np.asarray(checked_crop(image, pair[name])), percentile)
                                                      for pair in train]))
                       for percentile in design["backgroundPercentiles"]}
        controls = {case: measures(image, boxes[name], backgrounds, settings, design["translations"])
                    for case, boxes in optical["caseControls"].items()}
        ranges = {case: envelope(rows) for case, rows in controls.items()}
        separation = ranges["B"][0] - ranges["b"][1] if all(ranges.values()) else None
        passed = separation is not None and separation >= design["minimumEnvelopeGap"]
        record = {"backgroundGrayLevels": backgrounds, "controls": controls, "controlRanges": ranges,
                  "controlSeparation": separation, "controlGatePass": passed, "targetScored": False}
        if passed:
            target = measures(image, target_boxes[name], backgrounds, settings, design["translations"])
            limits = envelope(target)
            threshold = (ranges["B"][0] + ranges["b"][1]) / 2
            ends = {case_class(value, threshold, design["ambiguityMargin"]) for value in (limits or [None])}
            nominal = next(row for row in target if row["offsetXY"] == [0, 0] and row["backgroundPercentile"] == 15)
            record.update({"targetScored": True, "target": target, "targetRange": limits, "threshold": threshold,
                           "nominalTargetRatio": nominal["upperToLowerRatio"],
                           "class": ends.pop() if len(ends) == 1 else "ambiguous"})
        results[name] = record
    return {"targetBoxes": target_boxes, "scans": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    raw = PROTOCOL.with_name("DIRECT_PROTOCOL.json").read_bytes()
    design = json.loads(raw)
    optical = PROTOCOL.read_bytes()
    if digest(optical) != design["opticalProtocolSha256"]:
        raise ValueError("Original geometry or case metrics differ")
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              **analyze(json.loads(optical), design)}
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, allow_nan=False)
        output.write("\n")


if __name__ == "__main__":
    main()
