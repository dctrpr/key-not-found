# Current PDF OVERDOSE Body-Offset Column Gate

Scope: derived the four page-76 active body-row offsets and x positions from the repeated OCR `OVERDOSE` body grid, transferred those row-plus-column points to repeated `OVERDOSE` pages 74/76/78 in the current PDFs, kept only the nearest OCR word on each landed row, and checked for target terms, strict unit/order words, all-four coverage, active target order, and source-backed R3. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T15:45:00`
- Decision: `current_pdf_overdose_body_offset_column_no_selector`
- PDFs checked / OVERDOSE header rows / source points: `3` / `6` / `8`
- Column landing pages / landed word rows: `4` / `16`
- Target-word hits / own-target word hits / strict-word hits: `0` / `0` / `0`
- All-four pages / active-order pages / candidates: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate/current_pdf_overdose_body_offset_column_gate_sheet.jpg`
- Fingerprint: `pdfs=3|headers=6|sourcePoints=8|columnPages=4|wordRows=16|targetWordRows=0|ownWordRows=0|strictWordRows=0|allFourPages=0|activeOrderPages=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Source Points

| PDF | source page | target | row offset | x pt | x fraction | source nearest word | distance | source line |
|---|---:|---|---:|---:|---:|---|---:|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `35` | `372.9057` | `0.616156` | `eis` | `237.0357` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `40` | `144.6792` | `0.219929` | `and` | `7.4507` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `42` | `243.3962` | `0.391313` | `Street` | `14.1615` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `44` | `323.7736` | `0.530857` | `siukbeodmensertslveaarty` | `3.048` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `35` | `372.9057` | `0.616156` | `eis` | `237.0357` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `40` | `144.6792` | `0.219929` | `and` | `7.4507` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `42` | `243.3962` | `0.391313` | `Street` | `14.1615` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `44` | `323.7736` | `0.530857` | `siukbeodmensertslveaarty` | `3.048` | `Maybe because he's a siukbeodmensertslveaarty` |

## Variant Pages

| PDF | article page | available words | target word hits | own-target hits | strict words | target sequence | nearest-word stream | candidate |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `keyser bitcoin .pdf` | `76` | `4` | `0` | `0` | `0` | `-` | `eis and Street siukbeodmensertslveaarty` | `0` |
| `keyser bitcoin .pdf` | `78` | `4` | `0` | `0` | `0` | `-` | `@ economy aa efficie:` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `4` | `0` | `0` | `0` | `-` | `eis and Street siukbeodmensertslveaarty` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `4` | `0` | `0` | `0` | `-` | `@ economy aa efficie:` | `0` |

## Landed Words

| PDF | article page | source target | row offset | x pt | nearest word | token | distance | target id | own hit | strict word | body line |
|---|---:|---|---:|---:|---|---|---:|---|---:|---:|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `35` | `372.9059` | `eis` | `eis` | `237.0359` | `-` | `0` | `0` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `40` | `144.6791` | `and` | `and` | `7.4509` | `-` | `0` | `0` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `42` | `243.3963` | `Street` | `street` | `14.1615` | `-` | `0` | `0` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `44` | `323.7736` | `siukbeodmensertslveaarty` | `siukbeodmensertslveaarty` | `3.0481` | `-` | `0` | `0` | `Maybe because he's a siukbeodmensertslveaarty` |
| `keyser bitcoin .pdf` | `78` | `O4` | `35` | `372.9059` | `@` | `-` | `142.2648` | `-` | `0` | `0` | `@` |
| `keyser bitcoin .pdf` | `78` | `B4` | `40` | `144.6791` | `economy` | `economy` | `24.9284` | `-` | `0` | `0` | `economy O` |
| `keyser bitcoin .pdf` | `78` | `G5` | `42` | `243.3963` | `aa` | `aa` | `114.4029` | `-` | `0` | `0` | `aa` |
| `keyser bitcoin .pdf` | `78` | `O5` | `44` | `323.7736` | `efficie:` | `efficie` | `159.4276` | `-` | `0` | `0` | `more © efficie:` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `35` | `372.9059` | `eis` | `eis` | `237.0359` | `-` | `0` | `0` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `40` | `144.6791` | `and` | `and` | `7.4509` | `-` | `0` | `0` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `42` | `243.3963` | `Street` | `street` | `14.1615` | `-` | `0` | `0` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `44` | `323.7736` | `siukbeodmensertslveaarty` | `siukbeodmensertslveaarty` | `3.0481` | `-` | `0` | `0` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O4` | `35` | `372.9059` | `@` | `-` | `142.2648` | `-` | `0` | `0` | `@` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `B4` | `40` | `144.6791` | `economy` | `economy` | `24.9284` | `-` | `0` | `0` | `economy O` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `G5` | `42` | `243.3963` | `aa` | `aa` | `114.4029` | `-` | `0` | `0` | `aa` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O5` | `44` | `323.7736` | `efficie:` | `efficie` | `159.4276` | `-` | `0` | `0` | `more © efficie:` |

## Decision

- `current_pdf_overdose_body_offset_column_no_selector`.
- The row-plus-column point selector lands on concrete OCR words, but the nearest-word streams are ordinary OCR noise/prose rather than target or instruction words.
- The source calibration page itself does not recover the expected target words at those row/column points.
- No landed word supplies target recovery, strict unit/order wording, active-order coverage, a selector candidate, or source-backed R3.

## Next Move

- Keep repeated OVERDOSE body-offset column mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a row-plus-column word unit/order rule.
