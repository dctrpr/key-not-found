#!/usr/bin/env python3
"""Check a fixed high-to-low optical transfer on one disputed printed glyph."""
import argparse
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "analysis_outputs/continuation_20261111/p77_initial_transfer/PROTOCOL.json"


def digest(raw):
    return sha256(raw).hexdigest()


def load(spec):
    raw = (ROOT / spec["path"]).read_bytes()
    if digest(raw) != spec["sha256"]:
        raise ValueError("Source crop hash differs")
    with Image.open(BytesIO(raw)) as image:
        if list(image.size) != spec["size"]:
            raise ValueError("Source crop dimensions differ")
        return image.convert("L")


def checked_crop(image, box):
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height):
        raise ValueError(f"Box outside pinned crop: {box}")
    return image.crop(tuple(box))


def fit_patch(hi, lo, box):
    high = checked_crop(hi, box["high"])
    low = checked_crop(lo, box["low"])
    return high.resize(low.size, Image.Resampling.LANCZOS), np.asarray(low, dtype=float)


def blur(image, sigma, pad):
    if sigma == 0:
        return np.asarray(image, dtype=float)
    pixels = np.pad(np.asarray(image), pad, mode="edge")
    filtered = np.asarray(Image.fromarray(pixels).filter(ImageFilter.GaussianBlur(sigma)), dtype=float)
    return filtered[pad:-pad, pad:-pad]


def interior(pixels, dx, dy, rim):
    h, w = pixels.shape
    return pixels[rim - dy:h - rim - dy, rim - dx:w - rim - dx]


def contrast_fit(xs, ys):
    xm, ym = np.mean([x.mean() for x in xs]), np.mean([y.mean() for y in ys])
    variance = np.mean([np.mean((x - xm) ** 2) for x in xs])
    if variance < 1e-9:
        raise ValueError("Insufficient contrast in fitting patches")
    gain = np.mean([np.mean((x - xm) * (y - ym)) for x, y in zip(xs, ys)]) / variance
    return float(gain), float(ym - gain * xm)


def transform(image, model, settings):
    pixels = blur(image, model["sigma"], settings["blurPadding"])
    return np.clip(model["gain"] * pixels + model["offset"], 0, 255)


def compare(prediction, observation, span):
    a, b = prediction - prediction.mean(), observation - observation.mean()
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    ncc = float(np.sum(a * b) / norm) if norm > 1e-8 else 0.0
    mae = float(np.mean(np.abs(prediction - observation)))
    return {"maeGrayLevels": mae, "normalizedMae": mae / span, "correlation": ncc}


def fit_model(patches, settings):
    rim, pad = settings["comparisonRim"], settings["blurPadding"]
    observed = [interior(low, 0, 0, rim) for _, low in patches]
    foreground_span = float(np.median([np.percentile(low, 95) - np.percentile(low, 15) for low in observed]))
    if foreground_span < settings["minimumForegroundSpan"]:
        raise ValueError("Fitting patches have insufficient lower-scan contrast")
    search = range(-settings["translationLimit"], settings["translationLimit"] + 1)
    candidates = []
    for sigma in settings["sigmaGrid"]:
        filtered = [blur(high, sigma, pad) for high, _ in patches]
        for dx, dy in product(search, repeat=2):
            predicted = [interior(high, dx, dy, rim) for high in filtered]
            gain, offset = contrast_fit(predicted, observed)
            if not (0.2 <= gain <= 1.5 and -40 <= offset <= 160):
                continue
            error = np.mean([np.mean((np.clip(gain * x + offset, 0, 255) - y) ** 2)
                             for x, y in zip(predicted, observed)])
            candidates.append({"sigma": sigma, "translationXY": [dx, dy], "gain": gain, "offset": offset,
                               "fitRmseGrayLevels": float(np.sqrt(error))})
    if not candidates:
        raise ValueError("No fitted scan model met the declared coefficient bounds")
    rank = lambda row: (row["fitRmseGrayLevels"], row["sigma"], sum(abs(x) for x in row["translationXY"]))
    return min(candidates, key=rank), min((row for row in candidates if row["sigma"] == 0), key=rank, default=None), foreground_span


def transfer_measure(high, low, model, span, settings):
    rim = settings["comparisonRim"]
    dx, dy = model["translationXY"]
    transformed = transform(high, model, settings)
    return compare(interior(transformed, dx, dy, rim), interior(low, 0, 0, rim), span)


def ink_ratio(pixels, background, settings):
    y, x = np.indices(pixels.shape)
    x, y = (x + 0.5) / pixels.shape[1], (y + 0.5) / pixels.shape[0]
    left, right = settings["lobeX"]
    top0, top1 = settings["upperLobeY"]
    bottom0, bottom1 = settings["lowerLobeY"]
    columns = (x >= left) & (x < right)
    upper = columns & (y >= top0) & (y < top1)
    lower = columns & (y >= bottom0) & (y < bottom1)
    ink = np.maximum(pixels - background, 0)
    upper_mean, lower_mean = float(ink[upper].mean()), float(ink[lower].mean())
    return {"upperMeanInk": upper_mean, "lowerMeanInk": lower_mean,
            "upperToLowerRatio": upper_mean / lower_mean if lower_mean >= settings["minimumLowerInk"] else None}


def shifted_image(pixels, dx, dy):
    height, width = pixels.shape
    yy = np.clip(np.arange(height) - dy, 0, height - 1)
    xx = np.clip(np.arange(width) - dx, 0, width - 1)
    return pixels[np.ix_(yy, xx)]


def case_measure(hi, lo, boxes, model, backgrounds, span, settings):
    high, low = fit_patch(hi, lo, boxes)
    transformed = shifted_image(transform(high, model, settings), *model["translationXY"])
    native_high = np.asarray(checked_crop(hi, boxes["high"]), dtype=float)
    return {"high": ink_ratio(native_high, backgrounds[0], settings),
            "predictedLow": ink_ratio(transformed, backgrounds[1], settings),
            "observedLow": ink_ratio(low, backgrounds[1], settings),
            **transfer_measure(high, low, model, span, settings)}


def case_class(value, threshold, margin):
    if value is None or abs(value - threshold) < margin:
        return "ambiguous"
    return "upper-rich" if value > threshold else "upper-poor"


def low_target_box(high_box, neighbor):
    hx0, hy0, hx1, hy1 = neighbor["high"]
    lx0, ly0, lx1, ly1 = neighbor["low"]
    sx, sy = (lx1 - lx0) / (hx1 - hx0), (ly1 - ly0) / (hy1 - hy0)
    x0, y0, x1, y1 = high_box
    return [round(lx0 + (x0 - hx0) * sx), round(ly0 + (y0 - hy0) * sy),
            round(lx0 + (x1 - hx0) * sx), round(ly0 + (y1 - hy0) * sy)]


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def analyze(spec):
    hi, lo = [load(source) for source in spec["sources"]]
    settings = spec["settings"]
    neighbor = next(pair for pair in spec["ordinaryPairs"] if pair["id"] == spec["requiredNearTargetHoldout"])
    target_boxes = {"high": spec["targetHighBox"], "low": low_target_box(spec["targetHighBox"], neighbor)}
    all_controls = [*spec["ordinaryPairs"], *spec["caseControls"].values()]
    for resolution in ("high", "low"):
        if any(overlaps(target_boxes[resolution], pair[resolution]) for pair in all_controls):
            raise ValueError("A control intersects the disputed glyph crop")
    training = [pair for pair in spec["ordinaryPairs"] if pair["role"] == "fit"]
    model, zero_blur, span = fit_model([fit_patch(hi, lo, pair) for pair in training], settings)
    backgrounds = [float(np.median([np.percentile(np.asarray(checked_crop(image, pair[resolution])), 15)
                                    for pair in training])) for image, resolution in [(hi, "high"), (lo, "low")]]
    held_out = []
    for pair in spec["ordinaryPairs"]:
        if pair["role"] == "holdout":
            measured = transfer_measure(*fit_patch(hi, lo, pair), model, span, settings)
            passes = (measured["normalizedMae"] <= settings["holdoutMaxNormalizedMae"]
                      and measured["correlation"] >= settings["holdoutMinCorrelation"])
            held_out.append({"id": pair["id"], **measured, "pass": passes})
    controls = {case: case_measure(hi, lo, boxes, model, backgrounds, span, settings)
                for case, boxes in spec["caseControls"].items()}
    channels = ("high", "predictedLow", "observedLow")
    gaps, thresholds = {}, {}
    for channel in channels:
        upper = controls["B"][channel]["upperToLowerRatio"]
        lower = controls["b"][channel]["upperToLowerRatio"]
        gaps[channel] = upper - lower if upper is not None and lower is not None else None
        thresholds[channel] = (upper + lower) / 2 if gaps[channel] is not None else None
    qualified = [row for row in held_out if row["pass"]]
    ordinary_pass = len(qualified) >= settings["minimumOrdinaryHoldouts"] and any(
        row["id"] == spec["requiredNearTargetHoldout"] for row in qualified)
    case_pass = all(gap is not None and gap >= settings["minimumCaseControlGap"] for gap in gaps.values())
    case_fit_pass = all(control["normalizedMae"] <= settings["holdoutMaxNormalizedMae"]
                        and control["correlation"] >= settings["holdoutMinCorrelation"] for control in controls.values())
    result = {"model": model, "bestZeroAddedBlurModel": zero_blur, "foregroundSpan": span,
              "backgroundGrayLevels": backgrounds, "ordinaryHoldouts": held_out,
              "caseControls": controls, "caseControlGaps": gaps, "caseThresholds": thresholds,
              "ordinaryGatePass": ordinary_pass, "caseSeparationGatePass": case_pass, "targetBoxes": target_boxes,
              "caseTransferGatePass": case_fit_pass, "targetScored": False, "outcome": "controls-insufficient"}
    if not (ordinary_pass and case_pass and case_fit_pass):
        return result
    target = case_measure(hi, lo, target_boxes, model, backgrounds, span, settings)
    classes = {channel: case_class(target[channel]["upperToLowerRatio"], thresholds[channel], settings["ambiguityMargin"])
               for channel in channels}
    model_agrees = (target["normalizedMae"] <= settings["holdoutMaxNormalizedMae"]
                    and target["correlation"] >= settings["holdoutMinCorrelation"])
    if "ambiguous" in classes.values():
        outcome = "case-metric-ambiguous"
    elif model_agrees and tuple(classes.values()) == ("upper-rich", "upper-poor", "upper-poor"):
        outcome = "degradation-compatible"
    elif model_agrees and len(set(classes.values())) == 1:
        outcome = "consistent-case-metric"
    else:
        outcome = "fixed-model-insufficient"
    return {**result, "targetScored": True, "target": {**target, "classes": classes,
                                                       "wholeGlyphTransferPass": model_agrees}, "outcome": outcome}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    raw = PROTOCOL.read_bytes()
    result = {"protocolSha256": digest(raw), "scriptSha256": digest(Path(__file__).read_bytes()),
              **analyze(json.loads(raw))}
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
