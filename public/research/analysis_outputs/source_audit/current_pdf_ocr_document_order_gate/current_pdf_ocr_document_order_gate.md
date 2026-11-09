# Current PDF OCR Document-Order Gate

Scope: inspected invisible PDF OCR document order around page-76 O4/B4/G5/O5 active boxes. No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T13:55:35`
- PDFs checked: `3`
- PDFs with all four active boxes populated by OCR words: `0`
- PDFs with all four active component targets present somewhere in OCR order: `2`
- PDFs whose first component occurrences match active order O4/B4/G5/O5: `0`
- Strict unit/order hits near active boxes: `0`
- Hidden OCR document-order candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_document_order_gate/current_pdf_ocr_document_order_gate_sheet.jpg`
- Fingerprint: `pdfs=3|allFourBoxes=0|allFourComponents=2|activeOrder=0|strictNear=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | words | populated boxes | box OCR text | component first order | all components | active order | strict near | candidate |
|---|---:|---:|---|---|---:|---:|---:|---:|
| `magazine.pdf` | `245` | `2/4` | `a^€LI | - | oe} srlf 'sun}€ulr1ln | -` | `-` | `0` | `0` | `0` | `0` |
| `keyser bitcoin .pdf` | `265` | `3/4` | `sell | loan and get | Street crony | -` | `O5-O4-G5-B4` | `1` | `0` | `0` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `265` | `3/4` | `sell | loan and get | Street crony | -` | `O5-O4-G5-B4` | `1` | `0` | `0` | `0` |

## Active Box Detail

### `magazine.pdf`

| target | OCR words | word indexes | component hits | strict inside/near |
|---|---|---|---|---|
| `O4` | `a^€LI` | `167-167` | `-` | `-` |
| `B4` | `-` | `-` | `-` | `-` |
| `G5` | `oe} srlf 'sun}€ulr1ln` | `203-205` | `-` | `-` |
| `O5` | `-` | `-` | `-` | `-` |

### `keyser bitcoin .pdf`

| target | OCR words | word indexes | component hits | strict inside/near |
|---|---|---|---|---|
| `O4` | `sell` | `208-208` | `-` | `-` |
| `B4` | `loan and get` | `221-223` | `-` | `-` |
| `G5` | `Street crony` | `243-244` | `-` | `-` |
| `O5` | `-` | `-` | `-` | `-` |

### `analysis_outputs/external_clues/google_drive_article_download.pdf`

| target | OCR words | word indexes | component hits | strict inside/near |
|---|---|---|---|---|
| `O4` | `sell` | `208-208` | `-` | `-` |
| `B4` | `loan and get` | `221-223` | `-` | `-` |
| `G5` | `Street crony` | `243-244` | `-` | `-` |
| `O5` | `-` | `-` | `-` | `-` |

## Decision

- `current_pdf_ocr_document_order_no_selector`.
- Invisible OCR order is derivative page prose/context, not original-layout authority.
- No current PDF simultaneously provides all-four active-box OCR population, all-four target components in active order, and strict unit/order wording near the active boxes.

## Next Move

- Keep current PDF OCR as context only. Future progress still requires distinct physical/original-layout/source evidence or raw clue wording that supplies R3 unit/order before extraction.
