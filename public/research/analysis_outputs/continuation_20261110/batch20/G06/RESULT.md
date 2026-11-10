# G06 — Reused capsule interior differences

Completed **2026-11-10T05:26:03.907Z**. Outcome: **no-valid-literal-key-in-declared-complete-readings**.

Five repeated capsule pairs produced 20 fixed residual OCR views plus combined readings (24 extracted text streams). Positive OCR controls passed; no declared literal key. This excludes only the registered detector-readable residual views, not all artwork encodings.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No OCR-readable validated literal key excludes the declared20 registered residual views only.

- Differences may be interpolation/compositing/printing artifacts. Shape reuse alone is not a selector.
- Vision failures or positive-control failure prevent a complete negative. Manual review remains useful.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G06 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G06-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.
