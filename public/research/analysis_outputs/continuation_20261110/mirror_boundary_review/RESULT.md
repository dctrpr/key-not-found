# Pair-local mirror boundary envelope — result

Completed **2026-11-10T06:27:56.096Z**. **No valid declared private-key record.**

The registered run covered every one of **17,108 modeled pair-local selection paths**, producing **102,648 correlated labeled readings** and **93,536 distinct text forms**. There were **222 distinct minikey-shaped strings** (521 occurrences); every one failed the minikey checksum. No WIF, boundary-delimited 64hex scalar or contiguous unfiltered BIP39 candidate was present. An independent saved-output/count/checksum audit agreed. No address query, wallet action or transaction was needed.

## What changed

The old G01 guard could block a row because of a word that could never become its first/last selected word. The new selector models relevance explicitly and enumerates every allowed row selection or omission. All 16 pair/color/edge scopes completed under the fixed cap. This expands the tested set instead of guessing a single reading through uncertain boundaries.

## What this rules out

A complete zero-result run excludes only the declared literal records from the registered pair-local modeled superset, at the pinned source/code bytes. It does not calibrate scan errors, test global concatenation or exhaust mirror/first-word ciphers.

The frozen review guards are heuristic. This result is not a measurement-confidence claim, proof of a creator-selected stencil, or exclusion of all mirror methods. **Global concatenations remain outside scope** (43,347,744 modeled paths). The original G01 report remains an accurate record of its incomplete coverage.

## Evidence

- [Protocol](PROTOCOL.md), first published in [`bed5239266a687a5e4ad474feb920b362b2cb670`](https://github.com/dctrpr/key-not-found/commit/bed5239266a687a5e4ad474feb920b362b2cb670) before target validation.
- [Machine result](RESULT.json) with pinned sources/code, actual counts and controls.
- [Complete exact readings, compressed](READINGS.jsonl.gz): contains all 102,648 reading IDs, texts and source-word choices. Reviewed for publication after the zero-valid-record result.
- [Source uncertainty model](SOURCE_MODEL.json), including states/options and word IDs without replacing missing geometry.
- [Independent saved-output audit](INDEPENDENT_CHECK.json); this checks counts and checksums, not independent geometry regeneration.

## Reproduce

From the research archive root, Python 3.10+ standard library, with fresh outputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/mirror_boundary_envelope.py --run --protocol analysis_outputs/continuation_20261110/mirror_boundary_review/PROTOCOL.json --registration-commit bed5239266a687a5e4ad474feb920b362b2cb670 --out mirror-envelope-rerun
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_mirror_boundary_envelope.py analysis_outputs/continuation_20261110/mirror_boundary_review/RESULT.json analysis_outputs/continuation_20261110/mirror_boundary_review/READINGS.jsonl.gz mirror-envelope-independent-rerun.json
```
