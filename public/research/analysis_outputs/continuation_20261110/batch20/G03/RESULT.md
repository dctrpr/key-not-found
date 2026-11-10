# G03 — Orange/black two-alphabet channel

Completed **2026-11-10T05:25:28.052Z**. Outcome: **no-valid-literal-key-in-declared-complete-readings**.

46 physical orange/black fragments were serialized at fragment, word and letter resolution: 1296 labeled decodes, 616 distinct forms. No declared literal key. This excludes only the fixed color-state/Bacon/ASCII serializations.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

No validated literal key excludes the exact declared color-state serializations/decodes.

- Color encoding was not specified by the creator; no DOCM/manual partial-bold state is used.
- Readable-looking fragments or a weak checksum do not establish intentional encoding.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G03 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G03-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.
