# Orange Party body source: full row review

All **312 historically classified body rows** were inspected against the retained printed-page scans, including interiors and line endings. This creates a separate reviewed source model; the earlier registered OCR and replay results remain unchanged. The [row model](BODY_ROWS.json) preserves each original row ordinal/text, proposed printed text, model text, normalized source box and uncertainty.

| Printed page | Rows inspected | Confirmed | Corrected | Remaining uncertainty |
| --- | ---: | ---: | ---: | --- |
| 79 | 109 | 84 | 23 | 2 punctuation glyphs |
| 80 | 116 | 83 | 33 | None observed in body rows |
| 81 | 87 | 72 | 12 | 3 word prefixes |

**68 rows changed**, including typographic apostrophes and quotation marks; this is not a claim of 68 different word errors. Examples of lexical repairs include `interierence` → `interference`, `stuil` → `stuff`, and `periect` → `perfect`. The [complete change list](ROW_CORRECTIONS.json) distinguishes actual source repairs from a decoder’s interpretation. The printed word `peak` is retained rather than silently changing it to an expected word.

Both recovery-paragraph copies are visibly printed and retained, including their different wrap/hyphen presentation. The end of one copy and start of the other share one physical row. No row, duplicate, hard-wrap fragment or inconvenient word was deleted; no case change, joining or source-order change was applied.

## Remaining uncertainty

On page 79, a leading elision quote and a standalone long-dash glyph have uncertain Unicode typography; their lexical content and boundaries are clear. The model keeps the prior glyph spelling with an explicit flag.

On page 81, the first-word prefixes of left-column rows 2–4 remain gutter-softened. The existing OCR candidates are retained only in `modelText`; `printedText` remains null, and these words are not promoted to exact pixel transcriptions. An additional [blinded gutter review](GUTTER_REVIEW.json) confirms word counts and the final glyphs `l`, `e`, `s` while preserving prefix uncertainty. Word and initial-glyph readings that select these tokens need an uncertainty flag; final-glyph readings can use the confirmed terminal glyphs. This distinction does not authenticate any cipher.

## A fixed population for the next test

The historical body classification and conventional region order are investigator assumptions, not creator instructions. They exclude existing headings, pull quotes and separately labelled introductions, while retaining the two page-80 and five page-81 wide body-lead rows. The population and classification are not chosen after a decoding result.

Whole-source preparation under the proposed literal-chunk rule counts **2,018 chunks**: 669 / 707 / 642 on pages 79 / 80 / 81. This count applies an explicit whitespace/outer-wrapper convention; it is not an authenticated count of linguistic words. Internal dots/apostrophes, censor stars, hyphens, slash and currency symbols remain literal. No hard-wrap joining occurs. The [population receipt](TOKEN_POPULATION.json) performed no stride, projection or key-format checks.

The proposed every-twelfth-token test must publish its exact code, source pins, limits and source-uncertainty policy before target selection or checksum validation. A fixed-model negative will not exclude alternative uncertain letters, linguistic token definitions, joined words, other article populations or the puzzle generally.

## Source identity and rights

The unchanged [retained scans and bibliography](../../comparison_articles/overdose_style_uniqueness/issue27/SOURCE_REGISTER.md) identify the Orange Party column and Fall 2022 publisher contents. The inherited Issue 27 number and exact publication day remain unverified. This is relevant to the broad December plural-key claim; it is not authenticated as the March 2023 Issue 24 / 20-BTC target. Whole-image/source hashes identify bytes, not the correctness of a transcription. Readers can challenge any row against its source box.

Article: Max Keiser. Magazine: Bitcoin Magazine. Third-party source rights remain as recorded in the [rights policy](../../../DATA_LICENSE.md). No new source-license grant is made by this transcript.
