# Issue 26 printed-first-word result

Completed **2026-11-10T06:48:12.497Z**. **No valid declared record.**

The fixed procedure produced 39,744 correlated labeled readings and **1,746 distinct text forms** from the reviewed first words. Two distinct WIF-shaped strings and ten distinct minikey-shaped strings were present; **all 12 failed their checksums**. No boundary-delimited 64hex scalar, contiguous unfiltered BIP39 phrase, BIP32/SLIP132 extended private record, BIP38 record, Bitcoin address or SEC public-point candidate was present. An independent saved-output/count/checksum audit agreed. No network query, wallet action or transaction.

## Fixed source and procedure

113 text rows plus the STOP label on printed pages 102–104, in 23 declared article/page/flow-block units. All 114 leading-word objects were reviewed against source pixels by the source preparer and an independent review. The fixed choices include prose/emphasis/all-text populations, two source-token conventions, three STOP treatments, parity origins, row/character directions and four projections. These are correlated conventions within one procedure, not 39,744 independent theories.

[Source review](../../../sources/issue26/README.md), [protocol](PROTOCOL.md), [machine result](RESULT.json), [complete exact readings](READINGS.jsonl.gz), [independent check](INDEPENDENT_CHECK.json).

The protocol and source/code hashes were public in [`1af6d1f0cf07e6ca87d620db65c27d3b63949a12`](https://github.com/dctrpr/key-not-found/commit/1af6d1f0cf07e6ca87d620db65c27d3b63949a12) before target validation. The original source construction, review decisions and OCR are public; source-ID suffixes never determine parity.

## What this excludes

A complete zero result excludes only the declared literal/private/public records in these fixed first-word-derived readings from the pinned Issue 26 witnesses. It does not test full alternate lines, another source, arbitrary ciphers or authenticate the 20-BTC claim.

The column predates the creator’s December 2022 plural-key statement, but it is not authenticated as the March 2023 20-BTC target. Twenty-three full-line endings remain unreadable or unverified; **full alternate-line text was not tested**. This does not rule out another source unit, extraction, encoding or the creator claim itself.

## Reproduce

From the research archive root, Python 3.10+ standard library only, with fresh outputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue26_firstword_probe.py --run --protocol analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.json --registration-commit 1af6d1f0cf07e6ca87d620db65c27d3b63949a12 --out issue26-firstwords-rerun
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_firstword_readings.py analysis_outputs/continuation_20261110/issue26_firstwords/RESULT.json analysis_outputs/continuation_20261110/issue26_firstwords/READINGS.jsonl.gz issue26-independent-rerun.json
```

The independent audit validates saved form/counts and actual checksum candidates. It does not independently regenerate the image transcription or selector.
