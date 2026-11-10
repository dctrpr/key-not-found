# Global mirror boundary language audit — checksum lead

Completed **2026-11-10T07:18:12.995Z**. **The puzzle remains unsolved.**

All 24 registered language checks completed. Their candidate union contained **382 distinct minikey-shaped strings**. One 30-character string passed the minikey format’s **8-bit checksum**. No WIF, 64hex scalar or contiguous BIP39 candidate was present. The raw value stays private pending review.

A checksum pass alone is weak evidence. Under a rough uniform-checksum benchmark, each shaped string has a 1/256 chance of passing, so 382 strings would yield about **1.49 passes on average**. The observed single pass does not establish intentional encoding, prize funding, ownership or a connection to Max Keiser’s 20-BTC claim.

## What was covered

The exact graph search covered the candidate-set union of four global families: one mask class and first/last-word edge held fixed across the directed pairs 76→77, 77→76, 78→79 and 79→78, with both whole-sequence row orders and three projections. The source model contains **43,347,744 selection paths**. Those paths were represented as graphs; full readings were not expanded or counted as individual checks.

The run visited 61,815 product/prefix states, below the fixed 2,000,000-state cap, and validated the 382 unique shaped values. Controls and all language-completeness checks passed. The guards, rectangle masks and independent membership alternatives remain investigator assumptions; some joint choices may be physically inconsistent. This result does not authenticate a creator-selected stencil.

The protocol and implementation were public before execution in commit [`115f477f29fe7d57785276529026e92b8c9e49cb`](https://github.com/dctrpr/key-not-found/commit/115f477f29fe7d57785276529026e92b8c9e49cb). See the [registered method](PROTOCOL.md), [frozen machine protocol](PROTOCOL.json) and [safe machine result](RESULT.json). Candidate-set counts differ from occurrences, distinct full readings and independent theories.

## Current lead and next check

Public lead identifier — domain-separated SHA-256 fingerprint:

```text
8e402211e9f5aac9587c39f4a38ad620c797d042f76ed75bd24dca426b1cb09a
```

Only the safe fingerprint and aggregate result are published. The candidate value and any reconstructed path witness remain private during review. The extraction engine stores candidate values. A subsequent [source-witness review](SOURCE_WITNESS_REVIEW.json) reconstructed a matching allowed path without geometry or character changes: black/leftmost, reverse whole sequence, joined words. The frozen nominal center reading does not match; uncertain boundary choices are required. Exact occurrence and row-choice details stay private. This confirms reachability within the model, not physical plausibility or intentional encoding.

A **read-only address/history check** has its own [fixed protocol](../global_minikey_history/PROTOCOL.md), to be published before target derivation or any query. It must distinguish a format-valid string from evidence of an actual prize and record any lookup error as an error. At this checkpoint, **no address/history query, wallet import, signing operation or transaction has run**. Source-witness and physical-plausibility review also remain open.

## Reproduce

From the research archive root, using Python 3.10+ standard library and a fresh private output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/global_mirror_envelope.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/global_mirror_envelope.py --run --protocol analysis_outputs/continuation_20261110/mirror_global_envelope/PROTOCOL.json --registration-commit 115f477f29fe7d57785276529026e92b8c9e49cb --out global-mirror-rerun
```

The run preserves raw candidates privately and emits safe domain-separated fingerprints. A cap, control, source/code pin or validation failure is inconclusive. This completed run is a weak checksum lead requiring further evidence and review.


---

## Follow-up — 2026-11-10T07:40:54.968Z

The separately registered [five-construction history check](../global_minikey_history/RESULT.md) is complete. Python and Node agreed on all five derived addresses. Blockstream and mempool.space returned ten successful responses with all chain and mempool statistics zero. This supplies no evidence of a funded key through those five constructions at the recorded times. The checksum pass remains format-valid; other wallet constructions and the whole puzzle remain outside this scoped result. Raw candidate and address association stay private. The [original extraction result JSON](RESULT.json) is unchanged.
