# Current PDF OVERDOSE Header Delta Transfer Gate

Scope: measured repeated OCR `OVERDOSE` header-center deltas from article page 76 to pages 74/78 in the current PDFs, applied direct and mirrored transfers to locked page-76 O4/B4/G5/O5 target boxes, and checked whether transferred boxes land on target terms, strict unit/order words, or all-four/active-order structure. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T14:36:50`
- Decision: `current_pdf_overdose_header_delta_transfer_no_selector`
- PDFs checked / OVERDOSE header rows: `3` / `6`
- Transfer variants / transferred target boxes: `12` / `48`
- Text-hit boxes / target-term boxes / strict-term boxes: `0` / `0` / `0`
- All-four variants / active-order variants / candidates: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate/current_pdf_overdose_header_delta_transfer_gate_sheet.jpg`
- Fingerprint: `pdfs=3|headers=6|variants=12|boxRows=48|textRows=0|targetRows=0|strictRows=0|allFourVariants=0|activeOrderVariants=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Header Rows

| PDF | article page | header center | header bbox | word count |
|---|---:|---|---|---:|
| `keyser bitcoin .pdf` | `74` | `[520.995, 38.923]` | `[504.24, 35.92, 537.75, 41.926]` | `1` |
| `keyser bitcoin .pdf` | `76` | `[531.067, 32.904]` | `[514.32, 29.4, 547.814, 36.407]` | `265` |
| `keyser bitcoin .pdf` | `78` | `[518.72, 33.883]` | `[502.08, 30.88, 535.36, 36.886]` | `202` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `[520.995, 38.923]` | `[504.24, 35.92, 537.75, 41.926]` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `[531.067, 32.904]` | `[514.32, 29.4, 547.814, 36.407]` | `265` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `[518.72, 33.883]` | `[502.08, 30.88, 535.36, 36.886]` | `202` |

## Transfer Variant Rows

| PDF | destination page | variant | header delta | text rows | target rows | strict rows | target ids | target order | candidate |
|---|---:|---|---|---:|---:|---:|---|---|---:|
| `keyser bitcoin .pdf` | `74` | `direct_delta` | `[-10.072, 6.0195]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `74` | `x_mirror_about_header_delta` | `[-10.072, 6.0195]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `74` | `x_mirror_about_page_center_delta` | `[-10.072, 6.0195]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `78` | `direct_delta` | `[-12.3472, 0.9795]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `78` | `x_mirror_about_header_delta` | `[-12.3472, 0.9795]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `78` | `x_mirror_about_page_center_delta` | `[-12.3472, 0.9795]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `direct_delta` | `[-10.072, 6.0195]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `x_mirror_about_header_delta` | `[-10.072, 6.0195]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `x_mirror_about_page_center_delta` | `[-10.072, 6.0195]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `direct_delta` | `[-12.3472, 0.9795]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `x_mirror_about_header_delta` | `[-12.3472, 0.9795]` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `x_mirror_about_page_center_delta` | `[-12.3472, 0.9795]` | `0` | `0` | `0` | `-` | `-` | `0` |

## Nonempty Transferred Boxes

| PDF | dest | variant | target box | words | target hits | strict hits |
|---|---:|---|---|---|---:|---:|

## Decision

- `current_pdf_overdose_header_delta_transfer_no_selector`.
- Measured `OVERDOSE` header offsets do not turn the page-76 active boxes into an all-four, active-order, or instruction-bearing selector on pages 74/78.
- The transfer rows remain ordinary prose/layout contacts and source-backed R3 remains absent.

## Next Move

- Keep repeated `OVERDOSE` header-offset transfer mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue supplies a named unit/order or materially different page registration.
