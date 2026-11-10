# Issue 27: one literal stride-12 test

**Registration before target extraction and key-format checks.** This is one exploratory model, not 72 independent cipher theories. The printed repeated `12-step` passage and nearby routine/recursion language motivate the interval; ordinary rhetoric or an editorial repetition remain plausible. The body source and scope are fixed before outputs are inspected.

## Fixed source

Use the separately [reviewed body model](../issue27_body_source/SOURCE.md): exactly 312 historical body rows in their existing conventional order, containing 2,018 literal chunks under the declared tokenizer. Both printed recovery copies remain, as do actual hard-wrap fragments. Source image, original extraction, reviewed row-model and implementation hashes must match the machine protocol and their actual bytes in the supplied published Git registration commit.

Three gutter-softened first-word prefixes remain provisional in the fixed OCR model. Their prior spellings are unchanged, not guessed into verified printed text. The independent [blinded gutter review](../issue27_body_source/GUTTER_REVIEW.json) confirms their word counts and final glyphs. These uncertainties must propagate to each reading by projection.

## One operation

Split each row on the six ASCII whitespace characters. Keep a chunk only if it contains an ASCII letter or digit. Strip only the exact 18 outer-wrapper glyphs in [the frozen policy proposal](POLICY_PROPOSAL.json): ordinary sentence punctuation, brackets and both curly quote orientations. Retain every remaining character literally, including internal dots/apostrophes, censor stars, all hyphens, slash and currency symbols. No Unicode normalization, case conversion, letter-only filtering, hard-wrap joining or BIP39 word filtering is allowed.

Concatenate all tokens globally without page, region, row or paragraph resets. Use the forward sequence and the reversed token sequence. For each direction, declare all twelve offsets 0–11 and select every twelfth token to the end. Emit selected chunks joined with one ASCII space, their literal first glyphs, and their literal final glyphs: **2 directions × 12 phases × 3 projections = 72 labelled readings**. Phase labels 1–12 correspond to offsets 0–11. Reverse the input before selection; do not reverse letters within a token.

“Initials” and “finals” name literal glyph projections here. For example, a censor star or printed wrap hyphen can be a final glyph; it is not silently converted to an inferred last linguistic letter. This is one declared counting/letter policy.

Evaluate all 72 fixed-model records using the unchanged four-format scanner: embedded WIF, embedded 22/30-character minikey, bounded 64-hex valid-range scalar and contiguous unfiltered English BIP39. Exact and whitespace-only-compacted forms are deduplicated. Also report a separate evaluation of entire readings whose selected glyphs avoid the source uncertainty; never delete individual uncertain words from a reading to manufacture a phrase.

## Source uncertainty and interpretation

The three prefix tokens affect whole-word and initial-glyph readings that select them. Final-glyph readings use their independently confirmed terminal glyphs. Record source completeness per reading and distinguish computational completion of the fixed model from physical-source completeness.

A complete model-negative means no valid record in these exact 72 readings, with passed controls, pins, bounds and full model coverage. A separate source-known subset negative excludes only that subset. A source-affected reading cannot exclude its corresponding physical-source reading. No result rules out other token conventions, joined words, other source populations, alternate uncertain prefixes or the whole puzzle.

Any source/code drift, control failure, population omission, cap violation or unsupported output is inconclusive. Any format-valid record stays a review lead; an eight-bit minikey or checksum-free hex value especially does not authenticate intent or funding. No address derivation, seed derivation, explorer query, wallet import, signing or transaction is included.

## Reproduction and publication

Offline controls and independent implementation review precede target execution. All protocol and implementation files must be public in the registration commit before running. Raw token/reading files use fresh private directories and private file modes; public output is restricted to aggregate counts, approved format metadata and domain-separated fingerprints. Never publish a candidate’s bare SHA-256 when that value is its private scalar.

The public source text is reproducible and does not guarantee secrecy of a value derived from it. New result summaries omit selected values, source locators and candidate-associated addresses. The experiment is relevant to the broad December plural-key claim; the Orange Party column is not authenticated as the March 2023 Issue 24 / 20-BTC target.

Exact executable commands, code hashes and the independent saved-output verifier are added with the machine registration before execution. No target stride or checksum result is claimed in this protocol.


## Executable commands

From `public/research` in a Git checkout containing the first public registration commit:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue27_stride12.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_issue27_stride12.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue27_stride12.py --run --protocol analysis_outputs/continuation_20261110/issue27_stride12/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out /tmp/key404-private/stride12-rerun
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_issue27_stride12.py --verify --result /tmp/key404-private/stride12-rerun/RESULT.json --tokens /tmp/key404-private/stride12-rerun/TOKENS.private.json --readings /tmp/key404-private/stride12-rerun/READINGS.private.jsonl --source analysis_outputs/continuation_20261110/issue27_body_source/BODY_ROWS.json --out /tmp/key404-private/stride12-independent
```

Replace `REGISTRATION_COMMIT` with the first published protocol commit. Create the private parent directory first and use fresh output paths. The machine protocol pins all nine source and four implementation files. The independent checker uses its own token boundary walk and index stepping, plus the separately reviewed independent format calculator; it imports no primary runner or shared scanner. It must reproduce every saved token/reading and both complete evaluations, including actual positive records, source flags and counts.

See the [primary controls](CONTROLS.json), [synthetic failure controls](LIFECYCLE_CONTROLS.json), [independent controls](INDEPENDENT_CONTROLS.json) and [source merge review](../issue27_body_source/SOURCE_MERGE_REVIEW.json). These control receipts contain no target selection or checksum result.

The final code received a [separate pre-execution review](INDEPENDENT_CODE_REVIEW.json), with an additional [synthetic contract comparison](INDEPENDENT_PEER_REVIEW.json). No target decoding was used for these reviews.
