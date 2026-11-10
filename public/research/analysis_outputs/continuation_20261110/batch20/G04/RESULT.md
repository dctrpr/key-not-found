# G04 — Fixed interword-gap binary channel

Completed **2026-11-10T05:25:28.989Z**. Outcome: **inconclusive-source-or-detector-coverage**.

Measured 811 ink gaps across 104 of 142 rows. 38 rows failed source/ink guards and no full page was complete. No page/global bit string was decoded; spacing remains inconclusive.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No literal validated key excludes the exact1.5×median measured ink-gap serialization, not all spacing ciphers.

- Word boxes are machine-verified source geometry, not a claim of original font metadata.
- Incomplete rows, nonpositive gaps or unknown geometry make relevant scope inconclusive.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G04 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G04-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.
