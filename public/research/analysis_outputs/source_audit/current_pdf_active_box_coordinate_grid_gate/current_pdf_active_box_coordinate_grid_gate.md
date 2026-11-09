# Current PDF Active Box Coordinate Grid Gate

Scope: mapped current page-76 O4/B4/G5/O5 boxes, page-76 non-active highlight controls, and C9/OVERDOSE slots into the current PDFs' point-coordinate systems. Tested visual top-origin and PDF bottom-origin coordinates against fixed point grids. This is geometry inspection only; no key extraction, candidates, hashing, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T10:37:16`
- PDFs / active / highlight-control / OVERDOSE-slot regions: `3` / `4` / `7` / `8`
- Modes checked: `visualTopOrigin`, `pdfBottomOrigin`
- Grids checked: `1pt, 0.5pt, 0.25pt, 6pt, 12pt, 72pt`
- Tolerances: `[0.05, 0.12]` pt
- Any all-four active center close <=0.05 / <=0.12 pt: `0` / `1`
- Any all-four active edge close <=0.05 / <=0.12 pt: `0` / `1`
- Best active center close count <=0.05 / <=0.12 pt: `1` / `4`
- Best control center close count <=0.05 / <=0.12 pt: `2` / `7`
- Best grid row: `analysis_outputs/external_clues/google_drive_article_download.pdf` / `pdfBottomOrigin` / `0.25pt`
- Grid alignment candidate / hidden PDF coordinate candidate: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_active_box_coordinate_grid_gate/current_pdf_active_box_coordinate_grid_gate_sheet.jpg`
- Fingerprint: `pdfs=3|regions=4/7/8|modes=visualTop,pdfBottom|grids=1pt,0.5pt,0.25pt,6pt,12pt,72pt|allFourCenter05=0|allFourCenter12=1|allFourEdges05=0|allFourEdges12=1|bestCenter05=1|bestCenter12=4|controlBest05=2|controlBest12=7|best=analysis_outputs/external_clues/google_drive_article_download.pdf:pdfBottomOrigin:0.25pt|gridCandidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Best Grid Rows

| pdf | mode | grid | active center <=0.05 | active center <=0.12 | control center <=0.05 | control center <=0.12 | active mean center residual | control mean center residual |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `pdfBottomOrigin` | `0.25pt` | `1` | `4` | `1` | `6` | `0.0692` | `0.0565` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `visualTopOrigin` | `0.25pt` | `1` | `4` | `1` | `6` | `0.0692` | `0.0565` |
| `keyser bitcoin .pdf` | `pdfBottomOrigin` | `0.25pt` | `1` | `4` | `1` | `6` | `0.0692` | `0.0565` |
| `keyser bitcoin .pdf` | `visualTopOrigin` | `0.25pt` | `1` | `4` | `1` | `6` | `0.0692` | `0.0565` |
| `magazine.pdf` | `visualTopOrigin` | `0.25pt` | `0` | `3` | `1` | `5` | `0.0650` | `0.0650` |
| `magazine.pdf` | `pdfBottomOrigin` | `0.25pt` | `0` | `2` | `2` | `7` | `0.0700` | `0.0436` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `pdfBottomOrigin` | `0.5pt` | `0` | `2` | `0` | `0` | `0.1081` | `0.1709` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `visualTopOrigin` | `0.5pt` | `0` | `2` | `0` | `0` | `0.1081` | `0.1709` |
| `keyser bitcoin .pdf` | `pdfBottomOrigin` | `0.5pt` | `0` | `2` | `0` | `0` | `0.1081` | `0.1709` |
| `keyser bitcoin .pdf` | `visualTopOrigin` | `0.5pt` | `0` | `2` | `0` | `0` | `0.1081` | `0.1709` |
| `magazine.pdf` | `pdfBottomOrigin` | `0.5pt` | `0` | `1` | `2` | `3` | `0.1450` | `0.1271` |
| `magazine.pdf` | `pdfBottomOrigin` | `1pt` | `0` | `1` | `0` | `0` | `0.1700` | `0.2571` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `pdfBottomOrigin` | `1pt` | `0` | `1` | `0` | `0` | `0.2680` | `0.2834` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `visualTopOrigin` | `1pt` | `0` | `1` | `0` | `0` | `0.2680` | `0.2834` |
| `keyser bitcoin .pdf` | `pdfBottomOrigin` | `1pt` | `0` | `1` | `0` | `0` | `0.2680` | `0.2834` |
| `keyser bitcoin .pdf` | `visualTopOrigin` | `1pt` | `0` | `1` | `0` | `0` | `0.2680` | `0.2834` |
| `magazine.pdf` | `visualTopOrigin` | `0.5pt` | `0` | `0` | `0` | `1` | `0.1725` | `0.1400` |
| `magazine.pdf` | `visualTopOrigin` | `1pt` | `0` | `0` | `0` | `1` | `0.2150` | `0.1400` |

## Decision

- `current_pdf_active_box_coordinate_grid_no_selector`
- The current PDFs do not expose a hidden point-coordinate selector for O4/B4/G5/O5.
- Active centers/edges do not achieve a distinctive all-four grid landing, and comparable controls land near the same grids.

## Next Move

- Keep using the PDF only as current-scan/source-registration evidence unless a distinct original-layout source or raw clue names a unit/order.
