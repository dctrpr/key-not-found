# OVERDOSE Style Uniqueness Audit

Scope: compare Issue 24 against local Max/OVERDOSE comparison PDFs for recurring layout motifs. No key derivation, hashing, address checking, or OCR extraction was run.

- Created: `2026-05-24T18:14:57`
- Contact sheet: `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness_contact_sheet.jpg`

## Decision

- `bitcoin4.pdf` is a lower-quality duplicate/witness of the Issue 24 article, not an independent comparison article. Among the independent comparison PDFs, OVERDOSE branding and broad graphic color recur, but the sustained Issue 24 body-text orange/grey highlighter system remains distinctive. The comparison PDFs do not provide Issue 24 geometry or the missing extraction unit.

## Source Summaries

| source | text layer | highlighter-like pages | orange-band pages | dark/grey-band pages | small capsule-like pages | very colorful pages | max highlight score |
|---|---|---|---|---|---|---|---|
| Issue 24 / BITCOIN IS TOXIC AF | 7317 chars / fonts Helvetica | [3, 4, 5, 6, 7, 8] | [3, 4, 5, 6, 7, 8] | [1, 2, 3, 4, 5, 6, 7] | [1, 2, 3, 4, 5, 6, 7, 8] | [8] | 69 |
| Issue_26.pdf | image-only | [4, 5] | [4, 5] | [1, 2, 3, 4, 5] | [2, 3, 4, 5] | [] | 29 |
| Issue_27.pdf | image-only | [1] | [1] | [1, 2, 4, 5, 6, 7, 8] | [1, 5, 8] | [] | 32 |
| bitcoin3.pdf | image-only | [7, 8] | [7, 8] | [1, 2, 3, 4, 5, 6, 7, 8] | [4, 6, 7, 8] | [7, 8] | 63 |
| bitcoin4.pdf | image-only | [2, 3, 4, 5, 6, 7, 8] | [3, 4, 5, 6, 7, 8] | [1, 2, 3, 4, 5, 6, 7, 8] | [1, 2, 3, 4, 5, 6, 7, 8] | [8] | 111 |

## Issue 24 Signals

- Issue 24 highlighter-like pages by metric: `[3, 4, 5, 6, 7, 8]`.
- These correspond to the article body pages rather than only the opening/product art.
- The body-text orange/dark-bar system remains higher priority than the generic OVERDOSE label or broad colored art.

## Comparison Result

- `bitcoin4.pdf` visually reproduces the Issue 24 article in lower-quality/alternate geometry, so it is a source-fidelity witness, not an independent style comparison.
- `issue26` has highlighter-like metric pages `[4, 5]`, but visual review/contact-sheet context is needed because colored text/art can trigger the metric.
- `issue27` has highlighter-like metric pages `[1]`, but visual review/contact-sheet context is needed because colored text/art can trigger the metric.
- `bitcoin3` has highlighter-like metric pages `[7, 8]`, but visual review/contact-sheet context is needed because colored text/art can trigger the metric.
- All four comparison PDFs are image-only, so PDF font extraction cannot verify Typeka usage inside them.
- `Article with Fonts.docm` remains the best local font witness for Typeka/Typeka Mix on Issue 24.
- Comparison pages can downgrade generic Max/OVERDOSE motifs, but they cannot replace source geometry for page 76.

## Closest Coarse Visual Matches

Average-hash matches are only a rough composition check.
- Issue 24 p01 -> `bitcoin4` p01: hamming `18`, highlightDelta `25`
- Issue 24 p02 -> `bitcoin4` p02: hamming `51`, highlightDelta `20`
- Issue 24 p08 -> `issue27` p07: hamming `59`, highlightDelta `8`
- Issue 24 p08 -> `bitcoin3` p03: hamming `63`, highlightDelta `29`
- Issue 24 p08 -> `issue26` p05: hamming `69`, highlightDelta `14`
- Issue 24 p08 -> `issue27` p06: hamming `71`, highlightDelta `17`
- Issue 24 p08 -> `bitcoin4` p08: hamming `80`, highlightDelta `18`
- Issue 24 p01 -> `issue26` p03: hamming `80`, highlightDelta `26`
- Issue 24 p01 -> `issue27` p05: hamming `80`, highlightDelta `30`
- Issue 24 p08 -> `bitcoin3` p05: hamming `81`, highlightDelta `18`
- Issue 24 p01 -> `issue27` p03: hamming `86`, highlightDelta `38`
- Issue 24 p02 -> `issue26` p04: hamming `87`, highlightDelta `1`

## Next Move

- Treat `OVERDOSE` label, dark pages, and broad colored art as house-style/provenance unless they interact with the page-76 mirror corridor.
- Keep exact Issue 24 orange/grey body highlights and page-76/p79 registration as active signals.
- Do not reopen Typeka/font-state extraction unless a source rule selects exact words/lines or a new source file exposes real font-layer metadata.
