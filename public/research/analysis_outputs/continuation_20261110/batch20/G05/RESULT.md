# G05 — Printed-line displacement channel

Completed **2026-11-10T05:25:29.898Z**. Outcome: **inconclusive-source-or-detector-coverage**.

Obtained 98 of 142 row displacement proxies; 44 rows were unavailable or could not be detrended. No page/global decoding had complete coverage. The registered baseline channel remains inconclusive.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No literal validated key excludes only the registered ink-bottom residual-sign channel.

- The ink-bottom quantile is an optical baseline proxy, not original font metadata or an exact typographic baseline.
- Font/glyph shape, printing and scan noise can create residuals. No general baseline-steganography absence claim.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G05 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G05-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.
