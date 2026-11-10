# G09 — Corrected-leaf alignment specificity

Completed **2026-11-10T05:25:30.357Z**. Outcome: **alignment-claim-not-supported-by-controls**.

True-leaf mean overlap was 0.03085; the strongest wrong pair scored 0.03970. Shift rank was 0.03125, but the preregistered screen also required beating every wrong pair and failed. This weakens that exact alignment claim; it is not proof against all mirror methods.

Registered before target execution in commit [`90ad1d694b0eb236494ae199b87de05db5e3d331`](https://github.com/dctrpr/key-not-found/commit/90ad1d694b0eb236494ae199b87de05db5e3d331). [Fixed protocol](../GEOMETRY_PROTOCOL.json), [machine result](RESULT.json), [exact procedure details](DETAILS.json).

## Scope and limitations

Failure to distinguish exact normalized alignment from the declared controls does not support that alignment claim.

- Evidence audit, not a key decoder. Nonsignificance is not absence proof.
- Old leaf controls largely used wrong pairs; symmetric directions are not independent observations.

All applicable synthetic controls passed. No network request, wallet import or transaction occurred. Inconclusive source coverage is not counted as a ruled-out cipher.

## Reproduce

From the research archive root, with Python, Pillow, NumPy and PyMuPDF (G06–G08 also macOS/Swift/Vision), use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_geometry.py --run G09 --protocol analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json --registration-commit 90ad1d694b0eb236494ae199b87de05db5e3d331 --out G09-rerun
```

[Saved streams](STREAMS.json) and [independent count/checksum audit](INDEPENDENT_CHECK.json) allow inspection. That audit checks saved outputs; it does not independently regenerate the image selector or detector.

[Saved statistic recheck](STATISTIC_CHECK.json) independently recomputes the declared mean/rank/joint screen from the saved control scores.
