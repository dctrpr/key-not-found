# Issue 24: readable-instruction review

Two AI reviewers read all **22 frozen body-only outputs (62,804 source codepoints each)** for an actionable intermediate instruction. Neither recognized one. This is an exploratory, unblinded, subjective reading result; it does not exclude a message or rule out a cipher family.

The packet contains 16 whole-line selections (8 normal and 8 character-reversed), 4 first-word lists and 2 initial strings. Ordinary essay fragments and rhetorical imperatives were distinguished from instructions specifying a puzzle operation. The reviewers added no selectors, transformations, word filters, cryptographic checks, derivations or network queries. The source transcription was not re-proofread in this review.

| Reviewer | Started (UTC) | Completed (UTC) | Fully read | Actionable instructions recognized |
| --- | --- | --- | ---: | ---: |
| A | 2026-11-10T11:34:06.393109+00:00 | 2026-11-10T11:36:31.848039+00:00 | 22/22 | 0 |
| B | 2026-11-10T11:34:24.096675Z | 2026-11-10T11:38:34.954521Z | 22/22 | 0 |

These are recorded wall-clock review intervals, including report and tool work. Agreement is not a calibrated meaning test, and the related outputs do not count as independent theories.

## Frozen provenance

- [Upstream saved JSON](../../../analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json) — SHA-256 `1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9`; 16,852,358 bytes.
- [Unchanged source builder](../../../scripts/minikey_window_audit.cjs) — SHA-256 `189c6f359a057021adbc060ddeaa8caa29e6f58c40a6976daeda62025d2182f0`; 21,076 bytes.
- Plain-text review packet export — SHA-256 `f0a4795960a333635e704aa9ed7781a1ca2e72d27b5757623eb1e1c2c228f406`; 66,415 bytes.
- Structured review packet export — SHA-256 `dbd23a556c478646bbc48e1c05a3111c778840880ad8d3134f1e1187e4a9dbde`; 153,605 bytes.

[REVIEW.json](REVIEW.json) preserves the two review receipt identities, per-reading source hashes, projection classes, coverage and recognition flags. Packet identities allow exact provenance checks; raw review strings and source locators are omitted from this package.

Only these exact saved strings were reviewed. Other source populations, visual interpretations, transformations, source accuracy and author intent remain outside this finding. A missed instruction remains possible.
