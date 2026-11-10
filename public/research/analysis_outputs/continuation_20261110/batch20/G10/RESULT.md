# G10 — Current raster least-bit payload

Completed **2026-11-10T05:27:05.026Z**. Outcome: **no-valid-literal-key-in-declared-complete-readings**.

Checked 768 current-raster RGB least-bit serializations, with strict literal-format validation and no arbitrary scalar/hash guesses. No declared literal key. This is a weak file sanity check; printing, scanning or JPEG may erase an earlier payload.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No validated literal key excludes only these768 current-raster serializations.

- A weak file sanity check: physical printing/scanning/JPEG may erase an earlier digital payload.
- No arbitrary pixel-buffer hashes or32-byte scalar guesses. This does not rule out print-origin encoding.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G10 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G10-rerun
```

[Stream descriptors](STREAM_DESCRIPTORS.json) contain safe domain-separated digests for every serialization. The exact 24 packed source bitplanes are generated locally from the pinned PDF; they are not duplicated in this public archive. Incremental/bulk scanner agreement is synthetic validation, not an independent target rerun.
