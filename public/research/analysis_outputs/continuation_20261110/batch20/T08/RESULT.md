# T08 — BIP38 encrypted private-key records

Completed **2026-11-10T05:14:17.603Z**.

42 labeled readings (42 distinct texts), 42 distinct exact/whitespace-compacted forms. 0 shape occurrences (0 distinct); zero valid declared records. Independent form counts and checksums agreed.

Registered before execution in commit [`8f4fa38bf24db7e432410c4daaa29e9de486156c`](https://github.com/dctrpr/key-not-found/commit/8f4fa38bf24db7e432410c4daaa29e9de486156c). See [fixed protocol](../TEXT_PROTOCOL.json), [machine result](RESULT.json), [exact outputs](STREAMS.json), and [independent check](INDEPENDENT_CHECK.json).

## What this tested

Family: `encrypted-private-record-coverage`. Exact parameters are preserved in the machine result and protocol. All synthetic controls passed before target execution.

## What can be ruled out

No valid declared literal record excludes only this exact extraction, source population and record-format scope; it does not exclude another cipher, format or selector. No address queries, wallet imports or transactions occurred.

- A structural encrypted record would require a separate passphrase/source lead.
- No password guessing, decryption or spendable-secret claim is part of this test.

## Reproduce

From the research archive root, use a fresh output path:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_text.py --run T08 --protocol analysis_outputs/continuation_20261110/batch20/TEXT_PROTOCOL.json --registration-commit 8f4fa38bf24db7e432410c4daaa29e9de486156c --out T08-rerun
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_batch20_text.py analysis_outputs/continuation_20261110/batch20/T08/RESULT.json analysis_outputs/continuation_20261110/batch20/T08/STREAMS.json T08-independent-rerun.json
```

The independent audit checks saved forms and their actual checksum candidates; it does not independently regenerate the selector. No output was passed through a prose-hash or arbitrary-ASCII-scalar wrapper.
