# Current PDF Repeated OVERDOSE Header Lane Gate

Scope: used the repeated OCR `OVERDOSE` page-start rows in the current PDFs as controls, split each header into normal/mirrored/reversed vertical letter lanes, and checked whether those lanes carry target terms, strict unit/order words, or active-order structure. This is a bounded layout/OCR-overlay check only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T14:31:12`
- Decision: `current_pdf_repeated_overdose_header_lane_no_selector`
- PDFs checked / OVERDOSE header rows / lane rows checked: `3` / `6` / `24`
- Target lane rows / strict lane rows: `0` / `0`
- All-four lane rows / active-order lane rows: `0` / `0`
- Page-76 target lane rows / candidates: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate/current_pdf_repeated_overdose_header_lane_gate_sheet.jpg`
- Fingerprint: `pdfs=3|overdoseHeaders=6|laneRows=24|targetRows=0|strictRows=0|allFourRows=0|activeOrderRows=0|page76TargetRows=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Header Rows

| PDF | article page | word count | header bbox |
|---|---:|---:|---|
| `keyser bitcoin .pdf` | `74` | `1` | `[504.24, 35.92, 537.75, 41.926]` |
| `keyser bitcoin .pdf` | `76` | `265` | `[514.32, 29.4, 547.814, 36.407]` |
| `keyser bitcoin .pdf` | `78` | `202` | `[502.08, 30.88, 535.36, 36.886]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `1` | `[504.24, 35.92, 537.75, 41.926]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `265` | `[514.32, 29.4, 547.814, 36.407]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `202` | `[502.08, 30.88, 535.36, 36.886]` |

## Lane Rows

| PDF | article page | variant | lane words | strict | targets | target order | candidate | target lane stream |
|---|---:|---|---:|---:|---|---|---:|---|
| `keyser bitcoin .pdf` | `74` | `normal` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `74` | `reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `74` | `x_mirror` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `74` | `x_mirror_reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `76` | `normal` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `76` | `reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `76` | `x_mirror` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `76` | `x_mirror_reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `78` | `normal` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `78` | `reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `78` | `x_mirror` | `13` | `0` | `-` | `-` | `0` | `-` |
| `keyser bitcoin .pdf` | `78` | `x_mirror_reverse_labels` | `13` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `normal` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `x_mirror` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `x_mirror_reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `normal` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `x_mirror` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `x_mirror_reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `normal` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `reverse_labels` | `0` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `x_mirror` | `13` | `0` | `-` | `-` | `0` | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `x_mirror_reverse_labels` | `13` | `0` | `-` | `-` | `0` | `-` |

## Decision

- `current_pdf_repeated_overdose_header_lane_no_selector`.
- Repeated `OVERDOSE` page-start lanes do not combine strict unit/order wording with all-four active target coverage or active target order.
- Page 76 target-lane hits are sparse context, and the repeated page-start controls do not supply a source-backed extraction rule.

## Next Move

- Keep repeated `OVERDOSE` header lane mechanics closed for the current PDFs. Continue only with source/provenance evidence that names a unit/order, or with a true source asset that materially changes the page registration.
