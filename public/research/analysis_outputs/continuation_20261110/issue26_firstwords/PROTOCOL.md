# Issue 26 printed-first-word procedure

Registered before any target record validation. [Machine protocol](PROTOCOL.json) freezes exact source/code bytes, parameters, controls and completeness checks. This is one procedure with correlated conventions, not 39,744 independent theories.

## Why this source

The [publisher contents](https://bitcoinmagazine.com/2022-censorship-resistant-issue) identifies a Q2 2022 print release and the matching Keiser title/subtitle. It predates his December 2022 plural hidden-key statement. That statement does not name an issue, so this is a source-motivated column to test. It is not authenticated as the March 2023 20-BTC target. [Retained witnesses and source review](../../../sources/issue26/README.md) are public.

All 114 leading-word objects were independently reviewed against the source pixels: 113 regular text rows plus the separate STOP side label. Twenty-three full-line endings remain gutter-obscured. **Only leading words are used. Full alternate-line text is outside scope.**

## Fixed readings

- Units: whole article, each of 3 printed pages, each of 19 source flow blocks (23 units).
- Populations: all text; the 94 prose rows; the 19 emphasis/heading/callout/closer rows.
- Token surfaces: the frozen literal printed-token convention and its conventional lexical alternative. Fused text and printed fragments remain as reviewed. Original digital Unicode/punctuation bytes are unknown.
- STOP: exclude the side label; replace the anchored first callout token with STOP; or insert the label before that token. Its original row-ID suffix never determines parity.
- All/odd/even rows, with parity ranked within each unit before or after population filtering; forward/reverse row order; spaced words, joined words, initials or finals; normal or codepoint-reversed output. Empty readings remain labeled and are deduplicated for validation.

These fixed conventions produce 39,744 labeled readings, capped at 50,000. Each true text form and candidate is deduplicated. The source fields and reading order are fixed before validation, not selected for an appealing message.

## Evaluation

Strict literal WIF, 22/30-character minikey, boundary-delimited 64hex scalar, unfiltered contiguous BIP39, BIP32/SLIP132 extended private record, BIP38 encrypted record, Bitcoin mainnet address and SEC public-point formats. Shared published-vector and negative controls run before the article. BIP39 lowercases lexical words without discarding non-dictionary words; invalid decoded groups remain hard boundaries. No prose-hash wrappers, arbitrary ASCII scalars, password guesses, child-key derivation, address queries, wallet imports or transactions.

An unverified/empty source first word, pin mismatch, failed control or incomplete count gives an inconclusive result. A valid serialized record requires separate review. A zero result excludes only these declared first-word-derived readings and formats. It does not exhaust either creator clue, another issue, or the puzzle.

## Reproduce

Python 3.10+ standard library only. From the research archive root, use fresh outputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue26_firstword_probe.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue26_firstword_probe.py --run --protocol analysis_outputs/continuation_20261110/issue26_firstwords/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out issue26-firstwords-rerun
```

Replace REGISTRATION_COMMIT with the first public protocol commit. Raw JSONL records every convention and exact source-word choice. Keep raw outputs private if the safe result reports a lead.
