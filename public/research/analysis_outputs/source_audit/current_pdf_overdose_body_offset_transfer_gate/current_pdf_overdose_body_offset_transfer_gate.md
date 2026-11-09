# Current PDF OVERDOSE Body-Offset Transfer Gate

Scope: derived the four page-76 active O4/B4/G5/O5 body-row offsets from the repeated OCR `OVERDOSE` body start, transferred those offsets to repeated `OVERDOSE` pages 74/76/78 in the current PDFs, and checked the landed body lines for target terms, strict unit/order words, all-four coverage, active target order, and source-backed R3. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T15:38:41`
- Decision: `current_pdf_overdose_body_offset_transfer_no_selector`
- PDFs checked / OVERDOSE header rows / body-offset pages: `3` / `6` / `4`
- Source offset rows / transferred offset rows: `8` / `16`
- Own-target offset hits / strict offset rows: `0` / `0`
- All-four pages / active-order pages / candidates: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate/current_pdf_overdose_body_offset_transfer_gate_sheet.jpg`
- Fingerprint: `pdfs=3|headers=6|sourceOffsets=8|offsetPages=4|offsetRows=16|ownTargetRows=0|strictRows=0|allFourPages=0|activeOrderPages=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Source Offsets

| PDF | source page | target | body-row offset | row distance | source line |
|---|---:|---|---:|---:|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `35` | `3.0383` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `40` | `1.5248` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `42` | `3.9331` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `44` | `62.2779` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `35` | `3.0383` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `40` | `1.5248` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `42` | `3.9331` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `44` | `62.2779` | `Maybe because he's a siukbeodmensertslveaarty` |

## Variant Pages

| PDF | article page | available offsets | own-target hits | strict rows | union target ids | active order | candidate |
|---|---:|---:|---:|---:|---|---:|---:|
| `keyser bitcoin .pdf` | `76` | `4` | `0` | `0` | `-` | `0` | `0` |
| `keyser bitcoin .pdf` | `78` | `4` | `0` | `0` | `-` | `0` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `4` | `0` | `0` | `-` | `0` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `4` | `0` | `0` | `-` | `0` | `0` |

## Transferred Rows

| PDF | article page | source target | offset | available | own target hit | strict hits | line target ids | landed body line |
|---|---:|---|---:|---:|---:|---|---|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `35` | `1` | `0` | `-` | `-` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `40` | `1` | `0` | `-` | `-` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `42` | `1` | `0` | `-` | `-` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `44` | `1` | `0` | `-` | `-` | `Maybe because he's a siukbeodmensertslveaarty` |
| `keyser bitcoin .pdf` | `78` | `O4` | `35` | `1` | `0` | `-` | `-` | `@` |
| `keyser bitcoin .pdf` | `78` | `B4` | `40` | `1` | `0` | `-` | `-` | `economy O` |
| `keyser bitcoin .pdf` | `78` | `G5` | `42` | `1` | `0` | `-` | `-` | `aa` |
| `keyser bitcoin .pdf` | `78` | `O5` | `44` | `1` | `0` | `-` | `-` | `more © efficie:` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `35` | `1` | `0` | `-` | `-` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `40` | `1` | `0` | `-` | `-` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `42` | `1` | `0` | `-` | `-` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `44` | `1` | `0` | `-` | `-` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O4` | `35` | `1` | `0` | `-` | `-` | `@` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `B4` | `40` | `1` | `0` | `-` | `-` | `economy O` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `G5` | `42` | `1` | `0` | `-` | `-` | `aa` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O5` | `44` | `1` | `0` | `-` | `-` | `more © efficie:` |

## Decision

- `current_pdf_overdose_body_offset_transfer_no_selector`.
- The derived page-76 active offset signature is `O4=35, B4=40, G5=42, O5=44` in both duplicate OCR PDFs.
- Transferring those offsets to repeated OVERDOSE body pages lands on ordinary OCR body lines, not own target terms or strict unit/order wording.
- Page 74 has repeated `OVERDOSE` headers but no readable body-line lattice in the duplicate OCR PDFs, so it cannot support this offset rule.
- No transferred offset page supplies all-four target coverage, measured active target order, a selector candidate, or source-backed R3.

## Next Move

- Keep repeated OVERDOSE body-offset transfer mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a body-row offset, line-number, or row-transfer rule.
