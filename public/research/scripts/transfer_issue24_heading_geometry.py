#!/usr/bin/env python3
"""Predict a second-scan correspondence from independent same-face landmarks."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "analysis_outputs/continuation_20261111/heading_scan_transfer"


def digest(raw):
    return sha256(raw).hexdigest()


def apply(matrix, points):
    x, y = np.asarray(points, dtype=float).T
    return np.column_stack((matrix[0, 0] * x + matrix[0, 1] * y + matrix[0, 2],
                            matrix[1, 0] * x + matrix[1, 1] * y + matrix[1, 2]))


def reflect(points, width):
    return np.column_stack((width - 1 - points[:, 0], points[:, 1]))


def affine(source, target):
    center = source.mean(axis=0)
    scale = np.ptp(source, axis=0).max()
    if scale <= 0:
        raise ValueError("Landmarks have no spatial extent")
    design = np.column_stack(((source - center) / scale, np.ones(len(source))))
    coeff, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    if rank != 3:
        raise ValueError("Calibration landmarks do not determine an affine map")
    linear = coeff[:2].T / scale
    translation = coeff[2] - linear @ center
    matrix = np.vstack((np.column_stack((linear, translation)), [0, 0, 1]))
    return matrix, float(np.linalg.cond(design))


def convex_hull(points):
    def half(points):
        stack = []
        for point in points:
            while len(stack) >= 2 and cross(stack[-2], stack[-1], point) <= 0:
                stack.pop()
            stack.append(point)
        return stack

    ordered = sorted(set(map(tuple, points.tolist())))
    return half(ordered)[:-1] + half(reversed(ordered))[:-1]


def cross(a, b, point):
    return (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])


def covered(hull, points):
    return np.logical_and.reduce([cross(a, b, points.T) >= -1e-6
                                  for a, b in zip(hull, hull[1:] + hull[:1])])


def nearest(point, coordinates):
    return float(np.linalg.norm(coordinates - point, axis=1).min())


def validate_face(landmarks, settings):
    calibration = [item for item in landmarks if item["role"] == "calibration"]
    held_out = [item for item in landmarks if item["role"] == "holdout"]
    high = np.array([item["highXY"] for item in calibration])
    low = np.array([item["lowXY"] for item in calibration])
    high_holdout = np.array([item["highXY"] for item in held_out])
    low_holdout = np.array([item["lowXY"] for item in held_out])
    matrix, condition = affine(high, low)
    prediction = apply(matrix, high_holdout)
    error = np.linalg.norm(prediction - low_holdout, axis=1)
    reverse_error = np.linalg.norm(apply(np.linalg.inv(matrix), low_holdout) - high_holdout, axis=1)
    rms = float(np.sqrt(np.mean(error ** 2)))
    max_error = float(error.max())
    det = float(np.linalg.det(matrix[:2, :2]))
    valid = bool(condition <= settings["maxCondition"] and 0.3 <= det <= 1.3
                 and rms <= settings["maxHoldoutRmsLowPixels"]
                 and max_error <= settings["maxHoldoutLowPixels"]
                 and reverse_error.max() <= settings["maxReverseHoldoutHighPixels"])
    per_anchor = [{**item, "predictedLowXY": point.tolist(), "lowResidual": float(residual),
                   "highResidual": float(reverse)}
                  for item, point, residual, reverse in zip(held_out, prediction, error, reverse_error)]
    return {"highToLow": matrix.tolist(), "condition": condition, "determinant": det,
            "heldOutRmsLowPixels": rms, "heldOutMaximumLowPixels": max_error,
            "calibrationHullHigh": convex_hull(high), "calibrationHullLow": convex_hull(low),
            "geometryPass": valid, "holdouts": per_anchor}


def feature_support(feature, geometry, source, shift, settings):
    x0, y0, x1, y1 = feature["box"]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    reference = np.column_stack((xx.ravel(), yy.ravel()))
    corners = reference[[0, x1 - x0 - 1, -1, -(x1 - x0)]]
    high_width = source[0]["dimensions"][0]
    supports, masks = {}, {}
    for page in ("74", "75"):
        points = reflect(reference + shift, high_width) if page == "74" else reference
        footprint = reflect(corners + shift, high_width) if page == "74" else corners
        face = geometry[page]
        matrix = np.asarray(face["highToLow"])
        low = apply(matrix, points)
        holdouts = np.array([item["highXY"] for item in face["holdouts"]])
        max_distance = max(nearest(point, holdouts) for point in footprint)
        inside = covered(face["calibrationHullHigh"], points) & covered(face["calibrationHullLow"], low)
        nearby = np.logical_or.reduce([np.sum((points - anchor) ** 2, axis=1) <= settings["holdoutProximityHighPixels"] ** 2
                                       for anchor in holdouts])
        masks[page] = (inside & nearby).reshape(yy.shape)
        supports[page] = {"highFootprintXY": footprint.tolist(), "lowFootprintXY": apply(matrix, footprint).tolist(),
                          "fractionWithinBothHulls": float(inside.mean()),
                          "fractionWithinHullsAndHoldoutProximity": float(masks[page].mean()),
                          "maxCornerDistanceToHeldOutHighPixels": max_distance}
    common = masks["74"] & masks["75"]
    balanced = common & common[:, ::-1]
    fraction = float(balanced.mean())
    eligible = all(face["geometryPass"] for face in geometry.values()) and fraction >= settings["minimumCoverageFraction"]
    return {**feature, "support": supports, "symmetricCommonSupportFraction": fraction, "targetEligible": eligible}, balanced


def sample(image, points):
    x, y = points.T
    left, top = np.floor(x).astype(int), np.floor(y).astype(int)
    if np.any(left < 0) or np.any(top < 0) or np.any(left + 1 >= image.shape[1]) or np.any(top + 1 >= image.shape[0]):
        raise ValueError("Predicted sampling footprint exceeds the native raster")
    fx, fy = x - left, y - top
    return ((1 - fy) * ((1 - fx) * image[top, left] + fx * image[top, left + 1])
            + fy * ((1 - fx) * image[top + 1, left] + fx * image[top + 1, left + 1]))


def correlation(a, b):
    a, b = a - a.mean(), b - b.mean()
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denominator) if denominator > 1e-8 else 0.0


def score(feature, mask, filters, geometry, high_width, shift, settings):
    x0, y0, x1, y1 = feature["box"]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    points = np.column_stack((xx[mask], yy[mask]))
    map74 = np.asarray(geometry["74"]["highToLow"])
    map75 = np.asarray(geometry["75"]["highToLow"])
    template = sample(filters[75], apply(map75, points))
    reversed_points = np.column_stack((x0 + x1 - 1 - points[:, 0], points[:, 1]))
    reversed_template = sample(filters[75], apply(map75, reversed_points))

    def receiver(page, dy=0):
        high_points = reflect(points + shift + [0, dy], high_width)
        return sample(filters[page], apply(map74, high_points))

    intended = receiver(74)
    wrong = receiver(76)
    controls = {"wrong-handed": correlation(intended, reversed_template),
                "wrong-receiver-p76": correlation(wrong, template),
                "wrong-receiver-p78": correlation(receiver(78), template),
                "displaced-minus-160": correlation(receiver(74, -160), template),
                "displaced-plus-160": correlation(receiver(74, 160), template)}
    predicted = correlation(intended, template)
    injected = correlation(wrong + settings["syntheticScale"] * (template - template.mean()), template)
    sensitivity = injected >= settings["minimumScore"] and injected - controls["wrong-receiver-p76"] >= settings["minimumGap"]
    passes = sensitivity and predicted >= settings["minimumScore"] and predicted - max(controls.values()) >= settings["minimumGap"]
    return {"scoreAtFixedPrediction": predicted, "controls": controls, "injectedScore": injected,
            "sensitivityPass": sensitivity, "pass": passes}


def analyze(spec):
    previous = (ROOT / spec["previousProtocol"]["path"]).read_bytes()
    previous_result = (ROOT / spec["previousResult"]["path"]).read_bytes()
    if digest(previous) != spec["previousProtocol"]["sha256"] or digest(previous_result) != spec["previousResult"]["sha256"]:
        raise ValueError("Earlier registered measurements differ")
    survey = (DIRECTORY / "P74_LANDMARK_SURVEY.json").read_bytes()
    if digest(survey) != spec["p74LandmarkSurveySha256"]:
        raise ValueError("Page 74 landmark survey differs")
    surveyed = {row["id"]: row for row in json.loads(survey)["landmarks"]}
    if len(surveyed) != len(spec["landmarks"]["74"]):
        raise ValueError("Registered page 74 landmark count differs")
    for anchor in spec["landmarks"]["74"]:
        if any(anchor[axis + "XY"] != surveyed[anchor["id"]][axis]["pointXY"] for axis in ("high", "low")):
            raise ValueError("Registered page 74 landmark differs from the survey")
    refinement = (DIRECTORY / "P75_LANDMARK_REFINEMENT.json").read_bytes()
    if digest(refinement) != spec["p75LandmarkRefinementSha256"]:
        raise ValueError("Page 75 refinement receipt differs")
    recovered = {row["feature"]: row for row in json.loads(refinement)["landmarks"]}
    if len(recovered) != len(spec["landmarks"]["75"]):
        raise ValueError("Registered page 75 landmark count differs")
    for anchor in spec["landmarks"]["75"]:
        source = recovered[anchor["id"]]
        if any(anchor[axis + "XY"] != [coord - 0.5 for coord in source[axis]] for axis in ("high", "low")):
            raise ValueError("Registered page 75 landmark differs from the refinement receipt")
    sources = json.loads(previous)["sources"]
    shift = np.asarray(json.loads(previous_result)["high"]["shiftXY"])
    settings = spec["settings"]
    geometry = {page: validate_face(landmarks, settings) for page, landmarks in spec["landmarks"].items()}
    supported = [feature_support(feature, geometry, sources, shift, settings) for feature in sources[0]["features"]]
    targets = [(feature, mask) for feature, mask in supported if feature["targetEligible"]]
    hashes = {}
    if targets:
        from measure_issue24_heading_pixels import box_blur, load_pages

        images, hashes = load_pages(sources[1], [74, 75, 76, 78])
        filters = {}
        for page, image in images.items():
            filtered = box_blur(image, 1) - box_blur(image, 12)
            filters[page] = filtered if page == 75 else np.clip(filtered, -18, 18)
        for feature, mask in targets:
            feature["target"] = score(feature, mask, filters, geometry, sources[0]["dimensions"][0], shift, settings)
    passed = [feature for feature, _ in targets if feature["target"]["pass"]]
    body = [feature for feature in passed if feature["role"] == "holdout"]
    separated = any(abs(a["box"][1] - b["box"][1]) >= settings["minimumBodySeparationHighPixels"]
                    for a in body for b in body)
    heading_count = sum(feature["role"] == "calibration" for feature in passed)
    if not targets:
        outcome = "geometry-insufficient"
    elif heading_count == 2 and separated:
        outcome = "fixed-prediction-supported"
    else:
        outcome = "partial-fixed-prediction" if passed else "no-match-at-fixed-prediction"
    return {"higherResolutionShiftXY": shift.tolist(), "geometry": geometry, "features": [feature for feature, _ in supported],
            "targetWindowsScored": len(targets), "targetRasterEmbeddedJpegSha256": hashes,
            "targetWindowsPassed": len(passed), "outcome": outcome}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = (DIRECTORY / "PROTOCOL.json").read_bytes()
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              **analyze(json.loads(raw))}
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, allow_nan=False)
        output.write("\n")


if __name__ == "__main__":
    main()
