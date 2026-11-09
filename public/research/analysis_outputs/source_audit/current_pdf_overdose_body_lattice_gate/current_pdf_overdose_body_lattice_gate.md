# Current PDF OVERDOSE Body-Line Lattice Gate

Scope: used repeated OCR `OVERDOSE` page starts with readable body text, mapped locked O4/B4/G5/O5 boxes into PDF coordinates, assigned each to its nearest OCR body line, and checked for target terms, strict unit/order words, all-four line coverage, and active row order. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T15:30:41`
- Decision: `current_pdf_overdose_body_lattice_no_selector`
- PDFs checked / body-lattice pages / mapped rows: `3` / `4` / `16`
- Own-target rows / strict mapped rows: `0` / `0`
- All-four variants / active-row-order variants / candidates: `0` / `4` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate/current_pdf_overdose_body_lattice_gate_sheet.jpg`
- Fingerprint: `pdfs=3|latticePages=4|mappedRows=16|ownTargetRows=0|strictRows=0|allFourVariants=0|activeOrderVariants=4|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Variant Rows

| PDF | article page | own-target rows | strict rows | row order | all four | active order | candidate |
|---|---:|---:|---:|---|---:|---:|---:|
| `keyser bitcoin .pdf` | `76` | `0` | `0` | `O4-B4-G5-O5` | `0` | `1` | `0` |
| `keyser bitcoin .pdf` | `78` | `0` | `0` | `O4-B4-G5-O5` | `0` | `1` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `0` | `0` | `O4-B4-G5-O5` | `0` | `1` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `0` | `0` | `O4-B4-G5-O5` | `0` | `1` | `0` |

## Mapped Rows

| PDF | article page | target | body row | row distance | column fraction | own target hit | strict hits | nearest line target ids | nearest line |
|---|---:|---|---:|---:|---:|---:|---|---|---|
| `keyser bitcoin .pdf` | `76` | `O4` | `35` | `3.0383` | `120.2199` | `0` | `-` | `-` | `eis` |
| `keyser bitcoin .pdf` | `76` | `B4` | `40` | `1.5248` | `0.1111` | `0` | `-` | `-` | `loan and get rid of those leeches. I tagged Mike` |
| `keyser bitcoin .pdf` | `76` | `G5` | `42` | `3.9331` | `0.4847` | `0` | `-` | `-` | `bunch to his Wall Street crony pals, but so far he` |
| `keyser bitcoin .pdf` | `76` | `O5` | `44` | `62.2779` | `0.7635` | `0` | `-` | `-` | `Maybe because he's a siukbeodmensertslveaarty` |
| `keyser bitcoin .pdf` | `78` | `O4` | `39` | `40.9583` | `43.7366` | `0` | `-` | `-` | `aé` |
| `keyser bitcoin .pdf` | `78` | `B4` | `41` | `4.1852` | `-0.2853` | `0` | `-` | `-` | `peste aed` |
| `keyser bitcoin .pdf` | `78` | `G5` | `45` | `5.2402` | `1.3798` | `0` | `-` | `-` | `Ca nate a ware` |
| `keyser bitcoin .pdf` | `78` | `O5` | `45` | `99.6299` | `2.1917` | `0` | `-` | `-` | `Ca nate a ware` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O4` | `35` | `3.0383` | `120.2199` | `0` | `-` | `-` | `eis` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `B4` | `40` | `1.5248` | `0.1111` | `0` | `-` | `-` | `loan and get rid of those leeches. I tagged Mike` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `G5` | `42` | `3.9331` | `0.4847` | `0` | `-` | `-` | `bunch to his Wall Street crony pals, but so far he` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `O5` | `44` | `62.2779` | `0.7635` | `0` | `-` | `-` | `Maybe because he's a siukbeodmensertslveaarty` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O4` | `39` | `40.9583` | `43.7366` | `0` | `-` | `-` | `aé` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `B4` | `41` | `4.1852` | `-0.2853` | `0` | `-` | `-` | `peste aed` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `G5` | `45` | `5.2402` | `1.3798` | `0` | `-` | `-` | `Ca nate a ware` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `O5` | `45` | `99.6299` | `2.1917` | `0` | `-` | `-` | `Ca nate a ware` |

## Decision

- `current_pdf_overdose_body_lattice_no_selector`.
- The mapped boxes preserve the geometric O4-B4-G5-O5 row order, but the same order also appears on page-78 controls because it comes from fixed box height positions.
- The nearest OCR body lines do not recover own-target terms, all-four target text, or strict unit/order wording.
- No mapped row supplies a source-backed extraction instruction.

## Next Move

- Keep OVERDOSE body-line lattice mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a row/column/body-line unit rule.
