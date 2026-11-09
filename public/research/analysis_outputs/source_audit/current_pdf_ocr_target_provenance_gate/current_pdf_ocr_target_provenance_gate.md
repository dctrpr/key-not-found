# Current PDF OCR Target Provenance Gate

Scope: inspect page-76 PDF text overlays for exact O4/B4/G5/O5 target text, component-token false positives, approximate target-box OCR, OVERDOSE header text, and strict unit/order wording. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.

- Created: `2026-05-21T15:24:30`
- PDFs checked: `3`
- Exact active phrase rows: `0`
- PDFs with all four exact active phrases: `0`
- Component exact/stem-like hit rows: `4` / `6`
- Approximate target-box word rows / exact phrase rows: `8` / `0`
- Strict unit/order terms: `-`
- OVERDOSE header PDFs: `2`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_target_provenance_gate/current_pdf_ocr_target_provenance_gate_sheet.jpg`
- Fingerprint: `pdfs=3|exactPhraseRows=0|allFourExactPdfs=0|componentExactRows=4|componentStemRows=6|approxBoxWordRows=8|approxBoxExactRows=0|strictTerms=-|overdosePdfs=2|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | rotation | words | exact active phrases | component exact/stem rows | approx box words | strict terms | OVERDOSE hits |
|---|---:|---:|---:|---:|---:|---|---:|
| `magazine.pdf` | `180` | `245` | `0/4` | `0/0` | `2/4` | `-` | `0` |
| `keyser bitcoin .pdf` | `0` | `265` | `0/4` | `2/3` | `3/4` | `-` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `0` | `265` | `0/4` | `2/3` | `3/4` | `-` | `1` |

## Target Detail

### `magazine.pdf`

- O4 `buying the dip` exact phrase hits: `-`
- B4 `$1 billion` exact phrase hits: `-`
- G5 `Volcano Bonds` exact phrase hits: `-`
- O5 `shitcoiner at heart` exact phrase hits: `-`
- O4 component exact hits: `-`
- O4 component stem-like hits: `-`
- B4 component exact hits: `-`
- B4 component stem-like hits: `-`
- G5 component exact hits: `-`
- G5 component stem-like hits: `-`
- O5 component exact hits: `-`
- O5 component stem-like hits: `-`
- Approx O4 box OCR words: `a^€LI`
- Approx B4 box OCR words: `-`
- Approx G5 box OCR words: `oe} srlf 'sun}€ulr1ln`
- Approx O5 box OCR words: `-`

### `keyser bitcoin .pdf`

- O4 `buying the dip` exact phrase hits: `-`
- B4 `$1 billion` exact phrase hits: `-`
- G5 `Volcano Bonds` exact phrase hits: `-`
- O5 `shitcoiner at heart` exact phrase hits: `-`
- O4 component exact hits: `buying [(and loyears of watching Peter Schiff miss buying bitcoin since I started honéy-badgering him to]`
- O4 component stem-like hits: `-`
- B4 component exact hits: `-`
- B4 component stem-like hits: `billions [in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized to]`
- G5 component exact hits: `-`
- G5 component stem-like hits: `volcanoes [he was going to tap his nation's volcanoes to mine eis in bitcoin — that]`
- O5 component exact hits: `heart [some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto]`
- O5 component stem-like hits: `shitcoiners' [at $1 back in 2011) have dulled shitcoiners' and nocoiners' minds. The collective unconscious, controlled]`
- Approx O4 box OCR words: `sell`
- Approx B4 box OCR words: `loan and get`
- Approx G5 box OCR words: `Street crony`
- Approx O5 box OCR words: `-`

### `analysis_outputs/external_clues/google_drive_article_download.pdf`

- O4 `buying the dip` exact phrase hits: `-`
- B4 `$1 billion` exact phrase hits: `-`
- G5 `Volcano Bonds` exact phrase hits: `-`
- O5 `shitcoiner at heart` exact phrase hits: `-`
- O4 component exact hits: `buying [(and loyears of watching Peter Schiff miss buying bitcoin since I started honéy-badgering him to]`
- O4 component stem-like hits: `-`
- B4 component exact hits: `-`
- B4 component stem-like hits: `billions [in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized to]`
- G5 component exact hits: `-`
- G5 component stem-like hits: `volcanoes [he was going to tap his nation's volcanoes to mine eis in bitcoin — that]`
- O5 component exact hits: `heart [some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto]`
- O5 component stem-like hits: `shitcoiners' [at $1 back in 2011) have dulled shitcoiners' and nocoiners' minds. The collective unconscious, controlled]`
- Approx O4 box OCR words: `sell`
- Approx B4 box OCR words: `loan and get`
- Approx G5 box OCR words: `Street crony`
- Approx O5 box OCR words: `-`

## Decision

- Do not reopen PDF OCR active-box text.
- The text overlays are derivative OCR witnesses. The low-resolution duplicate PDFs contain scattered component words such as `buying`, `billions`, `volcanoes`, `shitcoiners`, and `heart`, but not the locked exact target phrases and not a source-side unit/order instruction.
- The high-resolution `magazine.pdf` text layer is rotated/OCR-corrupt and contains no useful active target words on page 76.
- OVERDOSE appearing in the low-resolution PDF text layer confirms only the article header, not an extraction rule.

## Next Move

- Treat PDF OCR as context only. Future local passes should be source-intake/reopen-gate checks unless new source/original-layout evidence arrives.
