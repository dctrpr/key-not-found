# G08 — Literal machine-readable codes

Completed **2026-11-10T05:29:08.958Z**. Outcome: **no-decodable-machine-readable-payload-in-declared-views**.

All 384 fixed views were scanned for QR, DataMatrix, Aztec and Code128. 0 payload occurrences. All 16 planted barcode-control views passed. No detector-readable payload in this exact view set; damaged or other codes remain possible.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No decoded payload excludes only the declared Vision-readable code formats/views.

- No explicit creator QR clue known. Nonstandard, damaged or artistic codes remain possible.
- DataMatrix control is a pinned unmodified official ZXing fixture; other controls are CoreImage generated.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G08 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G08-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.
