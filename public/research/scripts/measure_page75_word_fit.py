#!/usr/bin/env python3
"""Measure one proposed line wrap against visible print in two Issue 24 scans."""
import argparse
import json
from math import hypot
from pathlib import Path

import numpy as np

from measure_page78_right_anchor import ROOT, digest, load_pages, pinned, slope

PROTOCOL = ROOT / "analysis_outputs/continuation_20261111/page75_word_fit/PROTOCOL.json"


def view(image, window, baseline, strip, projection_slope):
    x0, x1, y0, y1 = window
    y, x = np.mgrid[y0:y1, x0:x1]
    shade = image[y0:y1, x0:x1].max(axis=2)
    if baseline is not None:
        xref, yref = baseline[0]
        offset = y - (yref + (x - xref) * slope(baseline))
        shade = np.where((offset >= -strip[0]) & (offset <= strip[1]), shade, 255)
    return x, (x + projection_slope * y) / hypot(1, projection_slope), shade


def ink_edges(pixels, horizontal, threshold, settings, minimum):
    x, along, shade = pixels
    x0, x1 = horizontal
    mask = (shade <= threshold) & (x >= x0) & (x < x1)
    count = int(mask.sum())
    if count < minimum:
        return {"pixels": count, "invalid": "insufficient-ink"}
    q = settings["quantile"]
    left, right = np.quantile(along[mask], [q, 1 - q]).tolist()
    native_left, native_right = np.quantile(x[mask], [q, 1 - q]).tolist()
    result = {"pixels": count, "left": left, "right": right}
    if min(native_left - x0, x1 - 1 - native_right) < settings["locatorClearancePx"]:
        result["invalid"] = "ink-near-window-edge"
    return result


def sample_rows(images, rows, baseline_by_row, settings):
    output = {}
    opener_slopes = [slope(baseline_by_row[row]) for row in ("p75r01", "p75r02")] if baseline_by_row else []
    for row_id, spec in rows.items():
        baseline = baseline_by_row.get(row_id)
        projection = (sum(opener_slopes) / 2 if row_id in ("p75r01", "p75r02")
                      else slope(baseline)) if baseline is not None else 0
        window = spec["window"]
        pixels = view(images[int(row_id[1:3])], window, baseline, settings["baselineStrip"], projection)
        for label, interval in spec["segments"].items():
            minimum = settings["minPeriodPixels"] if label == "period" else settings["minInkPixels"]
            output[label] = {str(threshold): ink_edges(pixels, interval, threshold, settings, minimum)
                             for threshold in settings["shadeThresholds"]}
    return output


def compare(edges):
    if any("invalid" in edge for edge in edges.values()):
        return {"invalidSegments": [name for name, edge in edges.items() if "invalid" in edge]}
    r1, r2, prefix, to = (edges[name] for name in ("row1", "row2", "row2BeforePeriod", "openerTo"))
    to_width = to["right"] - to["left"] + 1
    gaps = {}
    for name in ("started", "hard", "listen"):
        prev, ref_to = edges[name], edges[f"{name}To"]
        width = ref_to["right"] - ref_to["left"] + 1
        raw = ref_to["left"] - prev["right"] - 1
        gaps[name] = {"raw": raw, "scaled": raw * to_width / width, "toWidthRatio": width / to_width}
    return {"leftStartSeparationPx": abs(r1["left"] - r2["left"]), "openerToInkWidthPx": to_width,
            "visibleFullWidthRightPx": r2["right"], "visiblePrePeriodRightPx": prefix["right"],
            "row1RightPx": r1["right"], "zeroGapDemandPx": r1["right"] + to_width,
            "gaps": gaps}


def assess(samples, settings):
    if any("invalidSegments" in sample for sample in samples):
        return {"outcome": "inconclusive-locator-support"}
    guard = settings["guardPx"]
    demand_low = min(sample["zeroGapDemandPx"] + max(
        0, min(gap["scaled"] for gap in sample["gaps"].values()) - guard
    ) for sample in samples) - guard
    demand_high = max(sample["zeroGapDemandPx"] + max(
        gap["scaled"] for gap in sample["gaps"].values()
    ) for sample in samples) + 2 * guard
    preperiod_lower = min(sample["visiblePrePeriodRightPx"] for sample in samples) - guard
    full_ink_upper = max(sample["visibleFullWidthRightPx"] for sample in samples) + guard
    left_check = all(sample["leftStartSeparationPx"] <= settings["maxStartSeparationPx"] for sample in samples)
    scale_check = all(
        all(gap["raw"] > 0 and 1 / settings["maxToWidthRatio"] <= gap["toWidthRatio"] <= settings["maxToWidthRatio"]
            for gap in sample["gaps"].values())
        for sample in samples
    )
    margin = preperiod_lower - demand_high
    excess = demand_low - full_ink_upper
    if left_check and scale_check and margin > 0:
        outcome = "conditional-fit-within-observed-width"
    elif left_check and scale_check and excess > 0:
        outcome = "empirical-demand-exceeds-observed-width"
    else:
        outcome = "inconclusive-observed-width"
    return {"outcome": outcome, "openerStartCheckPassed": left_check, "spacingScaleCheckPassed": scale_check,
            "appendedEndpointLowPx": demand_low, "appendedEndpointHighPx": demand_high,
            "prePeriodInkLowerPx": preperiod_lower, "fullInkUpperPx": full_ink_upper,
            "conservativeFitMarginPx": margin, "empiricalExcessOverFullInkPx": excess}


def analyze(protocol):
    settings = protocol["settings"]
    source_receipts = {
        name: {row["id"]: row["baseline"] for row in json.loads(pinned(spec))["rows"]}
        for name, spec in protocol["readerReceipts"].items()
    }
    result = {}
    for source in protocol["sources"]:
        name = source["id"]
        images, hashes = load_pages(source, (75, 78))
        rows = protocol["windows"][name]
        variant_receipts = source_receipts if name == "low" else {"upright": {}}
        variants = {}
        for variant, reader in variant_receipts.items():
            baselines = {row: reader[row.replace("r", "-l", 1)] for row in rows} if reader else {}
            edges = sample_rows(images, rows, baselines, settings)
            conditions = [{
                "shadeThreshold": threshold,
                **compare({label: values[str(threshold)] for label, values in edges.items()}),
            } for threshold in settings["shadeThresholds"]]
            variants[variant] = {"edges": edges, "conditions": conditions}
        samples = [case for variant in variants.values() for case in variant["conditions"]]
        result[name] = {"embeddedJpegSha256": hashes, "variants": variants, "summary": assess(samples, settings)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = PROTOCOL.read_bytes()
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              "scans": analyze(json.loads(raw))}
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
