# Current PDF OVERDOSE Body-Fraction Column Gate

Scope: derived the four page-76 active normalized body-row fractions and x positions from the repeated OCR `OVERDOSE` body grid, transferred those fraction-plus-column points to repeated `OVERDOSE` pages 74/76/78 in the current PDFs, kept only the nearest OCR word on each landed row, and checked for target terms, strict unit/order words, all-four coverage, active target order, and source-backed R3. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T15:56:35`
- Decision: `current_pdf_overdose_body_fraction_column_no_selector`
- PDFs checked / OVERDOSE header rows / source fractions: `3` / `6` / `8`
- Fraction landing pages / landed word rows: `4` / `16`
- Target-word hits / own-target word hits / strict-word hits: `0` / `0` / `0`
- All-four pages / active-order pages / candidates: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_body_fraction_column_gate/current_pdf_overdose_body_fraction_column_gate_sheet.jpg`
- Fingerprint: `pdfs=3|headers=6|sourceFractions=8|fractionPages=4|wordRows=16|targetWordRows=0|ownWordRows=0|strictWordRows=0|allFourPages=0|activeOrderPages=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Source Fractions

| PDF | source page | target | source rows | row index | row fraction | x fraction | source nearest word | source line |
|---|---:|---|---:|---:|---:|---:|---|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `45` | `35` | `0.795455` | `0.616156` | `eis` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `45` | `40` | `0.909091` | `0.219929` | `and` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `45` | `42` | `0.954545` | `0.391313` | `Street` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `45` | `44` | `1.0` | `0.530857` | `siukbeodmensertslveaarty` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `45` | `35` | `0.795455` | `0.616156` | `eis` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `45` | `40` | `0.909091` | `0.219929` | `and` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `45` | `42` | `0.954545` | `0.391313` | `Street` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `45` | `44` | `1.0` | `0.530857` | `siukbeodmensertslveaarty` | `Maybe because he's a siukbeodmensertslveaarty` |

## Variant Pages

| PDF | article page | landed rows | target word hits | own-target hits | strict words | target sequence | nearest-word stream | candidate |
|---|---:|---|---:|---:|---:|---|---|---:|
| `keyser bitcoin .pdf` | `76` | `35,40,42,44` | `0` | `0` | `0` | `-` | `eis and Street siukbeodmensertslveaarty` | `0` |
| `keyser bitcoin .pdf` | `78` | `36,41,43,45` | `0` | `0` | `0` | `-` | `nrot peste 4 ware` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `35,40,42,44` | `0` | `0` | `0` | `-` | `eis and Street siukbeodmensertslveaarty` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `36,41,43,45` | `0` | `0` | `0` | `-` | `nrot peste 4 ware` | `0` |

## Landed Words

| PDF | article page | source target | row fraction | landed row | nearest word | token | distance | target id | own hit | strict word | body line |
|---|---:|---|---:|---:|---|---|---:|---|---:|---:|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `0.795455` | `35` | `eis` | `eis` | `237.0359` | `-` | `0` | `0` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `0.909091` | `40` | `and` | `and` | `7.4509` | `-` | `0` | `0` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `0.954545` | `42` | `Street` | `street` | `14.1615` | `-` | `0` | `0` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `1.0` | `44` | `siukbeodmensertslveaarty` | `siukbeodmensertslveaarty` | `3.0481` | `-` | `0` | `0` | `Maybe because he's a siukbeodmensertslveaarty` |
| `keyser bitcoin .pdf` | `78` | `O4` | `0.795455` | `36` | `nrot` | `nrot` | `77.9106` | `-` | `0` | `0` | `nrot` |
| `keyser bitcoin .pdf` | `78` | `B4` | `0.909091` | `41` | `peste` | `peste` | `31.8599` | `-` | `0` | `0` | `peste aed` |
| `keyser bitcoin .pdf` | `78` | `G5` | `0.954545` | `43` | `4` | `4` | `51.3137` | `-` | `0` | `0` | `4` |
| `keyser bitcoin .pdf` | `78` | `O5` | `1.0` | `45` | `ware` | `ware` | `127.6327` | `-` | `0` | `0` | `Ca nate a ware` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `0.795455` | `35` | `eis` | `eis` | `237.0359` | `-` | `0` | `0` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `0.909091` | `40` | `and` | `and` | `7.4509` | `-` | `0` | `0` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `0.954545` | `42` | `Street` | `street` | `14.1615` | `-` | `0` | `0` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `1.0` | `44` | `siukbeodmensertslveaarty` | `siukbeodmensertslveaarty` | `3.0481` | `-` | `0` | `0` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O4` | `0.795455` | `36` | `nrot` | `nrot` | `77.9106` | `-` | `0` | `0` | `nrot` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `B4` | `0.909091` | `41` | `peste` | `peste` | `31.8599` | `-` | `0` | `0` | `peste aed` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `G5` | `0.954545` | `43` | `4` | `4` | `51.3137` | `-` | `0` | `0` | `4` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O5` | `1.0` | `45` | `ware` | `ware` | `127.6327` | `-` | `0` | `0` | `Ca nate a ware` |

## Decision

- `current_pdf_overdose_body_fraction_column_no_selector`.
- Normalizing active row positions by body-line count changes the page-78 landing rows, but the nearest-word streams remain ordinary OCR noise/prose rather than target or instruction words.
- The source calibration page still does not recover expected target words at those fraction-plus-column points.
- No landed word supplies target recovery, strict unit/order wording, active-order coverage, a selector candidate, or source-backed R3.

## Next Move

- Keep repeated OVERDOSE body-fraction column mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a normalized row-plus-column word unit/order rule.
