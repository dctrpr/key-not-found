#!/usr/bin/env python3
"""Check two suspected image reuses with frozen crop/scale registration."""
import argparse
from hashlib import sha256
from itertools import product
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image


PROTOCOL = Path(__file__).resolve().parents[1] / "analysis_outputs/continuation_20261111/announcement_photo_lineage/PROTOCOL.json"


def digest(raw):
    return sha256(raw).hexdigest()


def read_image(assets, spec):
    raw = (assets / spec["file"]).read_bytes()
    if digest(raw) != spec["sha256"]:
        raise ValueError(f"Unexpected bytes for {spec['file']}")
    with Image.open(BytesIO(raw)) as image:
        if list(image.size) != spec["size"]:
            raise ValueError(f"Unexpected size for {spec['file']}")
        return np.asarray(image.convert("L"), dtype=np.float64)


def make_patches(target, boxes):
    patches = []
    for label, (x0, y0, x1, y1) in boxes.items():
        yy, xx = np.mgrid[y0:y1, x0:x1]
        values = target[y0:y1, x0:x1]
        centered = values - values.mean()
        magnitude = np.sqrt(np.sum(centered ** 2))
        if magnitude < 1:
            raise ValueError(f"Template has no contrast: {label}")
        patches.append((label, xx + .5, yy + .5, centered / magnitude))
    return patches


def score(reference, patch, mapping):
    _, xx, yy, target = patch
    scale, dx, dy = mapping
    x = xx * scale + dx - .5
    y = yy * scale + dy - .5
    x0, y0 = x.astype(int), y.astype(int)
    if x.min() < 0 or y.min() < 0 or x.max() >= reference.shape[1] - 1 or y.max() >= reference.shape[0] - 1:
        return -2.0
    fx, fy = x - x0, y - y0
    upper = reference[y0, x0] * (1 - fx) + reference[y0, x0 + 1] * fx
    lower = reference[y0 + 1, x0] * (1 - fx) + reference[y0 + 1, x0 + 1] * fx
    sampled = upper * (1 - fy) + lower * fy
    sampled -= sampled.mean()
    norm = np.sqrt(np.sum(sampled ** 2))
    return float(np.sum(sampled * target) / norm) if norm else -2.0


def compare(spec, images, gates):
    target, reference = [images[spec[key]] for key in ("target", "reference")]
    calibration = make_patches(target, spec["calibration"])
    holdouts = make_patches(target, spec["holdouts"])
    best = None
    for mapping in product(spec["scales"], spec["xOffsets"], spec["yOffsets"]):
        scores = [score(reference, patch, mapping) for patch in calibration]
        if min(scores) < -1:
            continue
        mean = sum(scores) / len(scores)
        if best is None or mean > best[0]:
            best = (mean, mapping, scores)
    if best is None:
        raise ValueError("No eligible mappings")
    mean, mapping, scores = best
    scale, dx, dy = mapping
    shift = spec["controlShiftTargetPx"] * scale
    controls = [(scale, dx + a * shift, dy + b * shift) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))]
    holdout_results = {}
    for patch in holdouts:
        observed = score(reference, patch, mapping)
        control_scores = [score(reference, patch, control) for control in controls]
        strongest = max(control_scores)
        passed = (min(control_scores) >= -1 and observed >= gates["minimumHoldoutScore"]
                  and observed - strongest >= gates["minimumDisplacedGap"])
        holdout_results[patch[0]] = {"score": observed, "displacedScores": control_scores,
                                     "displacedGap": observed - strongest, "passed": passed}
    total = sum(item["passed"] for item in holdout_results.values())
    inside_grid = all(value not in (grid[0], grid[-1])
                      for value, grid in zip(mapping, (spec["scales"], spec["xOffsets"], spec["yOffsets"])))
    return {"mapping": {"scale": scale, "xOffset": dx, "yOffset": dy, "insideGrid": inside_grid},
            "calibrationMean": mean, "calibrationScores": dict(zip(spec["calibration"], scores)),
            "holdouts": holdout_results, "holdoutsPassing": total,
            "supported": inside_grid and mean >= gates["minimumCalibrationMean"] and total >= gates["minimumHoldouts"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    raw = PROTOCOL.read_bytes()
    protocol = json.loads(raw)
    images = {name: read_image(args.assets, spec) for name, spec in protocol["assets"].items()}
    cases = {name: compare(spec, images, protocol["gates"]) for name, spec in protocol["comparisons"].items()}
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()), "cases": cases}
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
