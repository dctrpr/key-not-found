# Current PDF OCR Reverse-Leaf Source Trace

Scope: aligned the current PDF page-75 OCR/text layers to the page-75 OCR map, then mirrored O4/B4/G5/O5 page-76 active boxes back onto page 75 under the valid held-to-light transform. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:11:52`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_reverse_leaf_source_trace/current_pdf_ocr_reverse_leaf_source_trace_sheet.jpg`
- PDF rows / fit rows: `3` / `2`
- Token pairs / inliers: `232` / `232`
- Target rows / PDF word rows / exact-box word rows: `12` / `6` / `6`
- Strict instruction rows / context rows: `0` / `2`
- All-four exact-box PDF trace pairs: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|fits=2|pairs=232|inliers=232|targets=12|pdfWordRows=6|exactRows=6|strictRows=0|contextRows=2|allFourExact=0|sourceR3=0|triggers=0/9|selectors=0`

## Target Rows

| PDF | target | pdf words | exact words | strict tokens | context tokens | PDF OCR snippet | article-map snippet |
|---|---:|---:|---:|---|---|---|---|
| `magazine.pdf` | O4 | 0 | 0 | - | - | (fit unavailable) | Buterin came up with |
| `magazine.pdf` | B4 | 0 | 0 | - | - | (fit unavailable) | (no PDF OCR words) |
| `magazine.pdf` | G5 | 0 | 0 | - | - | (fit unavailable) | experience. |
| `magazine.pdf` | O5 | 0 | 0 | - | - | (fit unavailable) | for the gullible and unloved. |
| `keyser bitcoin .pdf` | O4 | 8 | 4 | - | bitcoins, buterin | by riding Bitcoins Buterin came up with the | Buterin came up with |
| `keyser bitcoin .pdf` | B4 | 0 | 0 | - | - | (no PDF OCR words) | (no PDF OCR words) |
| `keyser bitcoin .pdf` | G5 | 1 | 1 | - | - | experience. | experience. |
| `keyser bitcoin .pdf` | O5 | 5 | 5 | - | - | for the gullible and unloved. | for the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | O4 | 8 | 4 | - | bitcoins, buterin | by riding Bitcoins Buterin came up with the | Buterin came up with |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | B4 | 0 | 0 | - | - | (no PDF OCR words) | (no PDF OCR words) |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | G5 | 1 | 1 | - | - | experience. | experience. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | O5 | 5 | 5 | - | - | for the gullible and unloved. | for the gullible and unloved. |

## Decision

- `current_pdf_ocr_reverse_leaf_source_trace_no_instruction_source`
- The low-resolution PDF OCR layers align cleanly to page 75, but the reverse-leaf source boxes contain ordinary prose, blank regions, or isolated context words, not extraction instructions.
- The full-resolution `magazine.pdf` OCR layer remains rotated/garbled enough that it cannot supply a stable reverse-leaf source trace.
- No current PDF OCR layer supplies a source-backed instruction for fold, mirror, order, slot, read/take, or extraction.

## Next Move

- Keep PDF OCR reverse-leaf source tracing closed. The next useful move is still distinct source/original-layout validation or raw clue wording that names the active unit/order/transform.
