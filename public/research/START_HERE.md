# Max Keiser puzzle: active workspace

Work here: `.`.

Status on 9 November 2026: **unsolved**. No verified puzzle key or authenticated prize address has been established. Negative tests below cover their stated candidates, not every possible encoding.

## Migration

Copied 2,479 files (560,364,628 bytes) from the user-specified iCloud `maxkeiserpuzzle` directory. Source and destination SHA256 hashes matched for every copied file. Reinstallable `node_modules`, Git metadata, and Python bytecode caches were excluded. Historical files remain intact; new work lives under `analysis_outputs/continuation_20261109/` and new continuation scripts.

Migration evidence: [manifest](analysis_outputs/continuation_20261109/migration_manifest.json). Node dependencies were installed with `npm ci`; `.venv` contains Pillow, NumPy, and PyMuPDF.

## Creator evidence

- [26 December 2022](https://x.com/maxkeiser/status/1607378060172460032): physical magazine copies, his column, and private keys in the plural; links [George Sand's cryptography](https://ciphermysteries.com/2010/05/16/george-sands-cryptography). The linked examples select complete odd-numbered lines or the first word of every line. The poll's 10 BTC answer is not a verified payout. No issue is named.
- [4 March 2023](https://x.com/maxkeiser/status/1632068898169450497): singular private-key and 20-BTC claim, with the El Salvador Issue spread in the photograph.
- [5 March 2023](https://x.com/maxkeiser/status/1632391507008278528): links [Schott's mirror-writing paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/) and the March announcement. The paper discusses reversed glyphs and reading directions; it does not uniquely specify page overlays.

Fresh raw X responses and source interpretation: [George Sand verification](analysis_outputs/continuation_20261109/george_sand_research.md). The December plural-key clue may concern multiple columns; its application specifically to Issue #24 is an inference.

## Corrections that change the investigation

1. **Physical leaves:** visible gutters support 74/75, 76/77, and 78/79. The pairs 75/76, 77/78, and 79/80 are facing spreads. Many early duplex experiments used the wrong pairing.
2. **The old 17/17 page-76 graph is invalid evidence.** Its greedy phrase matcher skipped missing tokens and joined unrelated distant words into large boxes. All 17 medium/strong edges depend on noncontiguous matches. This does not invalidate every later independently measured scan box. See [phrase-box audit](analysis_outputs/continuation_20261109/phrase_box_audit/phrase_box_audit.md).
3. **Old R1-R5 gates are investigator assumptions.** They do not prohibit fresh tests on existing scans or require the creator to spell out every extraction step. The December clue now supplies explicit line/word mechanisms anyway.
4. **Old transcripts changed printed baselines.** `Really? Yes.` is one line, as is `Marty Bent — who…`. Faithful body counts are 32, 31, 32, 22, and 25 on pages 75–79, totaling 142. Two independent visual reviews checked the reconstructed lines and edge capitalization. Use [printed transcript](analysis_outputs/continuation_20261109/fresh_cryptanalysis/printed_lines.txt) and [coordinates/labels](analysis_outputs/continuation_20261109/fresh_cryptanalysis/printed_lines.json).
5. The annotated partial-bold count of 255 letters is not 256 bits. It comes from 610 positions in 113 partially bold words and strongly depends on the letter itself. Font behavior and investigator transcription remain plausible explanations; a hidden message has not been demonstrated.

## New tests and results

| Test | Declared scope | Result |
|---|---|---|
| Corrected orange-mask reflections | 20 ordered page pairs, 80 complete direct streams, fixed natural registration | No exact WIF/64-hex output |
| Corrected inverted masks | 19 visually checked physical bars across three correct leaves | Ordinary prose/art fragments; no valid WIF/64-hex output |
| Faithful George Sand/Musset readings | 10,080 labeled variants, 2,034 unique streams; page/paragraph parity, edges, mirrors, marked subsets | No valid WIF, literal hex, contiguous BIP39, minikey, or clear hidden instruction |
| Highlight-fragment readings | 45 physical baselines / 46 colored components, 540 variants | One weak minikey checksum hit; five derived address types had zero transactions |
| Literal ASCII keys | 12 exact 32-byte line-edge candidates from the two 32-line pages | 60 addresses checked successfully; zero confirmed or pending transactions |
| SHA256 first-word control | 36 exact case-preserving first-word strings, one SHA256 application | 180 addresses checked successfully; zero confirmed or pending transactions |
| Issue #27 alternative column | 356 OCR-assisted physical lines, 1,940 declared variants | No literal key or clear hidden instruction; duplicated paragraph changes only one wrapping boundary |

Variant counts include correlated/repeated formulations and do not measure independent theories. Address encodings were independently reviewed using public scalar-1 vectors, including independent SegWit/Taproot derivation. The ASCII and SHA256 interpretations are additional hypotheses, not author instructions. API errors are recorded as errors, not zero activity.

Evidence: [whole-body printed-line report](analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.md), [highlight test](analysis_outputs/continuation_20261109/george_sand/old_scope_and_next_step.md), [ASCII address checks](analysis_outputs/continuation_20261109/george_sand/printed_line_ascii_keys.json), [SHA256 address checks](analysis_outputs/continuation_20261109/george_sand/printed_firstword_sha256_keys.json), [Issue #27 report](analysis_outputs/continuation_20261109/george_sand_issue27/REPORT.md), [duplicate-wrap test](analysis_outputs/continuation_20261109/george_sand_issue27/duplicate_wrap_report.md).

## What remains unknown

There is still no reproducible source-to-key extraction. The source layer, text unit, traversal, and encoding remain unresolved. No evidence justifies treating a plausible Bitcoin-related phrase, a chance short-key checksum, or an unverified 20-BTC address list as a solution.

The most useful remaining work is evidence that discriminates author-controlled text from editorial layout, independent interpretations of the creator clues, and reviewable new extractions with a small declared parameter space. A new scan is not a mandatory prerequisite. Historical claims of entire classes being ruled out must be read within the exact scripts and candidate sets actually tested.

[Private context omitted from this public copy.]

[Private context omitted from this public copy.]

## Reproduce the new offline checks

From this directory:

```sh
python3 scripts/continue_corrected_duplex.py
python3 scripts/continuation_corrected_inverted_masks.py
python3 scripts/continuation_audit_phrase_boxes.py
node analysis_outputs/continuation_20261109/fresh_cryptanalysis/transcript_mirror_probe.js
node analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.js
python3 scripts/continuation_george_sand_highlight_lines.py
```

Read-only chain checking is separate: `node scripts/continue_printed_line_ascii_keys.js --check` or add `--firstword-sha256`. Successful address responses are cached. These scripts do not import wallets or submit transactions. Retain source hashes and actual API responses when updating an experiment.
