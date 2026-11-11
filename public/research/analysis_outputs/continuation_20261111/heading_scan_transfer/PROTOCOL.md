# Predict the faint trace from same-face landmarks

The higher-resolution scan previously supported a local shift of (−44, −1) pixels from upright page 75 to horizontally reflected page 74. The second scan’s two heading peaks did not support one translation. This test asks whether independently measured page geometry predicts correspondence in the second scan. Both earlier outcomes were known when the design was chosen. [Earlier experiment](../heading_pixel_match/RESULT.md)

## Calibration and validation

For each face separately, fit one affine map from higher-resolution upright coordinates to lower-resolution upright coordinates by ordinary least squares on the fixed calibration landmarks. Record the center-and-scale-normalized design condition number and signed area factor. Keep every landmark in its assigned role. No residual trimming, alternate transforms or refitting after validation.

Page 74 uses manually identified printed features from the orange section label and dark printed artwork, outside the faint-band region under study. The ordinary artwork landmark set includes left-side subject features and printed details below or to the right of the study areas. Approximate visual centers are used, so the resulting residuals include annotation error. Page 75 uses visually selected ordinary print outside the seven original matching boxes. The fixed page 75 patch matching procedure and verified coordinates are saved separately. Convert its half-open crop midpoints to pixel-center coordinates by subtracting 0.5 on each axis. All fit, holdout and scoring coordinates are thus native upright pixel-index centers, with zero at the first pixel center. [Landmarks and parameters](PROTOCOL.json) · [Page 74 survey](P74_LANDMARK_SURVEY.json) · [Page 75 refinement](P75_LANDMARK_REFINEMENT.json)

Each page must satisfy all of these criteria on held-out same-face landmarks: forward RMS at most 7 low-resolution pixels, maximum at most 12 low-resolution pixels, and maximum inverse error at most 16 high-resolution pixels. A fit also needs a normalized design condition number at most 12 and a positive determinant in [0.3, 1.3]. The same measurements are reported for failed fits. These thresholds constrain how far a predicted faint match can drift without any optimization on its pixels.

## Predict and, where supported, score

Reuse all seven higher-resolution template footprints and the earlier registered shift. For every template pixel `p`, sample the low page 75 at `A75(p)` and low page 74 at `A74(reflect_high(p + shift))`. Here `A74` and `A75` are the fitted upright maps and `reflect_high(x, y)` is `(W−1−x, y)`. The composition gives a fixed correspondence without fitting to low-resolution faint print.

For each face, a high-resolution sample point and its predicted low-resolution position must be inside the corresponding calibration convex hull. The high-resolution point must also lie within 500 pixels of a held-out same-face landmark. Intersect the two face masks with their horizontal reversal within the original template box so wrong-handed control sampling has the same support. A window is eligible only when both page geometry checks pass and at least 75% of the original window remains in the symmetric common mask. Report the support fractions for every original window. If none is eligible, stop before loading target pixels. A hull is a conservative coverage requirement, rather than proof that distortion is uniform inside it.

On eligible samples, apply the earlier native grayscale 3-minus-25-pixel box-blur filter and clip receiver contrast at ±18. Sample bilinearly at fixed positions. Compare zero-mean normalized correlation against wrong-handed, wrong-page 76 and 78, and same-receiver displaced controls at ±160 high-resolution vertical pixels. These are fixed comparisons with no shift search. The injected control adds 18% of the centered template to the wrong-page-76 sample. An injected score must reach 0.27 and improve by at least 0.05 over its unmodified score. The intended prediction must reach 0.27 and beat each control by at least 0.05. A shared prediction is supported only if both heading halves and two body windows at least 100 high-resolution pixels apart vertically pass. Retain any smaller success as partial, and keep insufficient geometry distinct from a failed pixel match.

The test concerns local content correspondence. Neither raster establishes physical paper registration, independent acquisition, an optical cause or a rule for selecting words. No character recognition or key checking occurs.

## Replay

From the repository root with Python, PyMuPDF 1.26.5, Pillow 11.3.0 and NumPy 2.0.2:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/replay_issue24_p75_landmarks.py --site . --out p75-landmark-replay.json
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/transfer_issue24_heading_geometry.py --out heading-scan-transfer.json
```
