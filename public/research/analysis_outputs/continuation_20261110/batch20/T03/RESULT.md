# T03 — Mirror-axis centers of printed lines

Completed **2026-11-10T05:14:17.472Z**.

120 labeled readings (120 distinct texts), 168 distinct exact/whitespace-compacted forms. 16 shape occurrences (10 distinct); zero valid declared records. Independent form counts and checksums agreed.

Registered before execution in commit [`8f4fa38bf24db7e432410c4daaa29e9de486156c`](https://github.com/dctrpr/key-not-found/commit/8f4fa38bf24db7e432410c4daaa29e9de486156c). See [fixed protocol](../TEXT_PROTOCOL.json), [machine result](RESULT.json), [exact outputs](STREAMS.json), and [independent check](INDEPENDENT_CHECK.json).

## What this tested

Family: `line-mesostics`. Exact parameters are preserved in the machine result and protocol. All synthetic controls passed before target execution.

## What can be ruled out

No valid declared literal record excludes only this exact extraction, source population and record-format scope; it does not exclude another cipher, format or selector. No address queries, wallet imports or transactions occurred.

- The center selector is an exploratory mirror hypothesis.
- Logical centers are not physical page-fold intersections.

## Reproduce

From the research archive root, use a fresh output path:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_text.py --run T03 --protocol analysis_outputs/continuation_20261110/batch20/TEXT_PROTOCOL.json --registration-commit 8f4fa38bf24db7e432410c4daaa29e9de486156c --out T03-rerun
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_batch20_text.py analysis_outputs/continuation_20261110/batch20/T03/RESULT.json analysis_outputs/continuation_20261110/batch20/T03/STREAMS.json T03-independent-rerun.json
```

The independent audit checks saved forms and their actual checksum candidates; it does not independently regenerate the selector. No output was passed through a prose-hash or arbitrary-ASCII-scalar wrapper.
