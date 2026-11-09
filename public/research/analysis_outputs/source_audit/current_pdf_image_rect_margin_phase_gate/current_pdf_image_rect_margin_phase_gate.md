# Current PDF Image Rect Margin Phase Gate

Scope: mapped current page-76 O4/B4/G5/O5 boxes, page-76 non-active highlights, and C9/OVERDOSE slots into the current PDFs' embedded image rectangles. Tested image-rect fractions, trim margins, and margin-derived 18pt units. This is geometry inspection only; no key extraction, candidates, hashing, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T10:44:19`
- PDFs / active / highlight-control / OVERDOSE-slot regions: `3` / `4` / `7` / `8`
- Fraction rulers: `halves, thirds, quarters, eighths, sixteenths`
- Margin units seen: `18.0, 18.0` pt
- Any all-four fraction close <=0.001 / <=0.0025 / <=0.005: `0` / `0` / `0`
- Any all-four margin-unit close <=0.25 / <=0.5 / <=1.0 pt: `0` / `0` / `0`
- Best fraction active/control close <=0.005: `0` / `0`
- Best margin-unit active/control close <=1.0 pt: `0` / `0`
- Best summary row: `analysis_outputs/external_clues/google_drive_article_download.pdf` / `pdfBottomOrigin` / `sixteenths`
- Margin phase candidate / hidden candidate: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_image_rect_margin_phase_gate/current_pdf_image_rect_margin_phase_gate_sheet.jpg`
- Fingerprint: `pdfs=3|regions=4/7/8|fractionRulers=halves,thirds,quarters,eighths,sixteenths|marginUnits=18.0,18.0|allFourFrac001=0|allFourFrac0025=0|allFourFrac005=0|allFourMargin025=0|allFourMargin050=0|allFourMargin100=0|bestFracActive005=0|bestFracControl005=0|bestMarginActive100=0|bestMarginControl100=0|best=analysis_outputs/external_clues/google_drive_article_download.pdf:pdfBottomOrigin:sixteenths|marginCandidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Best Phase Rows

| pdf | mode | ruler | kind | active close | control close | slot close | active mean residual | control mean residual |
|---|---|---|---|---:|---:|---:|---:|---:|
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `pdfBottomOrigin` | `sixteenths` | `fraction` | `0` | `0` | `0` | `0.02050709` | `0.01880103` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `visualTopOrigin` | `sixteenths` | `fraction` | `0` | `0` | `0` | `0.02050709` | `0.01880103` |
| `keyser bitcoin .pdf` | `pdfBottomOrigin` | `sixteenths` | `fraction` | `0` | `0` | `0` | `0.02050709` | `0.01880103` |
| `keyser bitcoin .pdf` | `visualTopOrigin` | `sixteenths` | `fraction` | `0` | `0` | `0` | `0.02050709` | `0.01880103` |
| `magazine.pdf` | `pdfBottomOrigin` | `sixteenths` | `fraction` | `0` | `0` | `0` | `0.02050709` | `0.01880103` |
| `magazine.pdf` | `visualTopOrigin` | `sixteenths` | `fraction` | `0` | `0` | `0` | `0.02050709` | `0.01880103` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `pdfBottomOrigin` | `eighths` | `fraction` | `0` | `0` | `0` | `0.02640476` | `0.02712719` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `visualTopOrigin` | `eighths` | `fraction` | `0` | `0` | `0` | `0.02640476` | `0.02712719` |
| `keyser bitcoin .pdf` | `pdfBottomOrigin` | `eighths` | `fraction` | `0` | `0` | `0` | `0.02640476` | `0.02712719` |
| `keyser bitcoin .pdf` | `visualTopOrigin` | `eighths` | `fraction` | `0` | `0` | `0` | `0.02640476` | `0.02712719` |
| `magazine.pdf` | `pdfBottomOrigin` | `eighths` | `fraction` | `0` | `0` | `0` | `0.02640476` | `0.02712719` |
| `magazine.pdf` | `visualTopOrigin` | `eighths` | `fraction` | `0` | `0` | `0` | `0.02640476` | `0.02712719` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `pdfBottomOrigin` | `quarters` | `fraction` | `0` | `0` | `0` | `0.06254805` | `0.06644403` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `visualTopOrigin` | `quarters` | `fraction` | `0` | `0` | `0` | `0.06254805` | `0.06644403` |
| `keyser bitcoin .pdf` | `pdfBottomOrigin` | `quarters` | `fraction` | `0` | `0` | `0` | `0.06254805` | `0.06644403` |
| `keyser bitcoin .pdf` | `visualTopOrigin` | `quarters` | `fraction` | `0` | `0` | `0` | `0.06254805` | `0.06644403` |
| `magazine.pdf` | `pdfBottomOrigin` | `quarters` | `fraction` | `0` | `0` | `0` | `0.06254805` | `0.06644403` |
| `magazine.pdf` | `visualTopOrigin` | `quarters` | `fraction` | `0` | `0` | `0` | `0.06254805` | `0.06644403` |

## Decision

- `current_pdf_image_rect_margin_phase_no_selector`
- Current-PDF image rectangle, trim-margin, and 18pt side-margin phase do not create a selective active-box rule.
- Loose all-four active phase alignments are matched or exceeded by non-active page-76 highlight controls.

## Next Move

- Keep using current PDFs as source-registration evidence only unless a distinct original-layout source or raw clue supplies unit/order wording.
