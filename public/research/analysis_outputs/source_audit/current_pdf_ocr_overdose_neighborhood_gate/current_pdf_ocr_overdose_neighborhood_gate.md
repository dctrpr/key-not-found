# Current PDF OCR OVERDOSE Neighborhood Gate

Scope: inspected fixed OCR word windows around the hidden page-76 `OVERDOSE` header in the current PDFs. This checks local unit/order wording and all-four target-component neighborhoods only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T14:11:10`
- Decision: `current_pdf_ocr_overdose_neighborhood_no_selector`
- PDFs checked / PDFs with OCR OVERDOSE: `3` / `2`
- OVERDOSE words / neighborhood rows checked: `2` / `8`
- Strict neighborhood rows / target-component rows: `0` / `4`
- All-four target neighborhoods / active-order neighborhoods: `0` / `0`
- Hidden OVERDOSE neighborhood candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_overdose_neighborhood_gate/current_pdf_ocr_overdose_neighborhood_gate_sheet.jpg`
- Fingerprint: `pdfs=3|overdosePdfs=2|overdoseWords=2|rows=8|strictRows=0|targetRows=4|allFourRows=0|activeOrderRows=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | words | OVERDOSE indexes | rows | strict rows | target rows | all-four rows | candidates |
|---|---:|---|---:|---:|---:|---:|---:|
| `magazine.pdf` | `245` | `-` | `0` | `0` | `0` | `0` | `0` |
| `keyser bitcoin .pdf` | `265` | `0` | `4` | `0` | `2` | `0` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `265` | `0` | `4` | `0` | `2` | `0` | `0` |

## Neighborhood Rows

| PDF | OVERDOSE index | radius | window span | strict hits | target ids | target order | candidate | window text |
|---|---:|---:|---|---|---|---|---:|---|
| `keyser bitcoin .pdf` | `0` | `4` | `0-4` | `-` | `-` | `-` | `0` | `OVERDOSE Get some toxicity. Get` |
| `keyser bitcoin .pdf` | `0` | `8` | `0-8` | `-` | `-` | `-` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your` |
| `keyser bitcoin .pdf` | `0` | `16` | `0-16` | `-` | `O5` | `O5` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto` |
| `keyser bitcoin .pdf` | `0` | `32` | `0-32` | `-` | `O5` | `O5` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto up in here, y'all. It's funkier than a whole parallel universe full of nothing but George` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `0` | `4` | `0-4` | `-` | `-` | `-` | `0` | `OVERDOSE Get some toxicity. Get` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `0` | `8` | `0-8` | `-` | `-` | `-` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `0` | `16` | `0-16` | `-` | `O5` | `O5` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `0` | `32` | `0-32` | `-` | `O5` | `O5` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto up in here, y'all. It's funkier than a whole parallel universe full of nothing but George` |

## Decision

- `current_pdf_ocr_overdose_neighborhood_no_selector`.
- The OCR `OVERDOSE` header is present only in the duplicate OCR PDFs, and its fixed local windows do not contain strict extraction wording or all-four active target components.
- This closes the local-neighborhood version of the hidden OCR header idea; it does not change the source-backed R3 score or reopen triggers.

## Next Move

- Keep current PDF OCR `OVERDOSE` as derivative context only. Continue toward distinct physical/original-layout/source material or raw clue wording that supplies R3 unit/order.
