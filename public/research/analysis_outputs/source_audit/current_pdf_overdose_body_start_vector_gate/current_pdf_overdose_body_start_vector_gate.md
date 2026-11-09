# Current PDF OVERDOSE Body-Start Vector Gate

Scope: used repeated OCR `OVERDOSE` page starts in the current PDFs, measured the vector from each header to the first readable body line, and checked fixed-width ray tubes for target terms, strict unit/order words, all-four target coverage, and active-order structure. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T15:17:19`
- Decision: `current_pdf_overdose_body_start_vector_no_selector`
- PDFs checked / OVERDOSE header rows / body-start rows: `3` / `6` / `4`
- Body vector rows / target rows / strict rows: `8` / `0` / `0`
- All-four rows / active-order rows / candidates: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate/current_pdf_overdose_body_start_vector_gate_sheet.jpg`
- Fingerprint: `pdfs=3|headers=6|bodyRows=4|vectorRows=8|targetRows=0|strictRows=0|allFourRows=0|activeOrderRows=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Body-Start Rows

| PDF | article page | body vector | angle | first body line |
|---|---:|---|---:|---|
| `keyser bitcoin .pdf` | `76` | `[-179.2271, 50.7435]` | `164.1919` | `Get some toxicity. Get some bitcoin. Open your heart to` |
| `keyser bitcoin .pdf` | `78` | `[-313.1291, 50.6329]` | `170.8148` | `We've never had an economy and a money` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `[-179.2271, 50.7435]` | `164.1919` | `Get some toxicity. Get some bitcoin. Open your heart to` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `[-313.1291, 50.6329]` | `170.8148` | `We've never had an economy and a money` |

## Vector Rows

| PDF | article page | width | ray words | targets | strict | target ids | target order | candidate | ray preview |
|---|---:|---:|---:|---:|---:|---|---|---:|---|
| `keyser bitcoin .pdf` | `76` | `10.0` | `8` | `0` | `0` | `-` | `-` | `0` | `some bitcoin. the freaking It's funkier than but` |
| `keyser bitcoin .pdf` | `76` | `20.0` | `15` | `0` | `0` | `-` | `-` | `0` | `Get some bitcoin. Open It's the freaking UTXO It's funkier than a but George nailing` |
| `keyser bitcoin .pdf` | `78` | `10.0` | `7` | `0` | `0` | `-` | `-` | `0` | `never had an economy and that incentivizes` |
| `keyser bitcoin .pdf` | `78` | `20.0` | `12` | `0` | `0` | `-` | `-` | `0` | `We've never had an economy and a money that incentivizes love Love` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `10.0` | `8` | `0` | `0` | `-` | `-` | `0` | `some bitcoin. the freaking It's funkier than but` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `20.0` | `15` | `0` | `0` | `-` | `-` | `0` | `Get some bitcoin. Open It's the freaking UTXO It's funkier than a but George nailing` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `10.0` | `7` | `0` | `0` | `-` | `-` | `0` | `never had an economy and that incentivizes` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `20.0` | `12` | `0` | `0` | `-` | `-` | `0` | `We've never had an economy and a money that incentivizes love Love` |

## Decision

- `current_pdf_overdose_body_start_vector_no_selector`.
- Repeated `OVERDOSE` header-to-body-start vectors do not create all-four target coverage, active-order target coverage, or strict unit/order wording.
- Page 76 body-start rays at most touch ordinary opening prose context; page 78 controls remain comparable and source-backed R3 remains absent.

## Next Move

- Keep repeated `OVERDOSE` body-start vector mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a unit/order or a specific header/body vector rule.
