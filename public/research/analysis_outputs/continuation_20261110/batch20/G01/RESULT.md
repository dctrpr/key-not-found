# G01 — Mirror first, then first selected word

Completed **2026-11-10T05:25:27.770Z**. Outcome: **inconclusive-source-or-detector-coverage**.

Only 12 of 120 labeled readings were complete; 36 of 40 selection scopes remained ambiguous at mask edges. The complete readings contain no declared literal key. This does not rule out mirror-first word selection.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No validated literal key in complete, unambiguous frozen readings excludes only these exact readings.

- Incomplete or boundary-ambiguous selected word geometry makes the affected stream inconclusive.
- Direction/projection variants are not independent theories.75→74 has no target body and is outside this scope.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G01 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G01-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.
