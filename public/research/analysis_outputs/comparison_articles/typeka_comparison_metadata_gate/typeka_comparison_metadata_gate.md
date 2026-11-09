# Typeka Comparison Metadata Gate

Scope: gate the user-supplied Typeka comparison claim against local metadata. No extraction, key derivation, hashing, OCR extraction, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:02:20`
- Sheet: `analysis_outputs/comparison_articles/typeka_comparison_metadata_gate/typeka_comparison_metadata_gate_sheet.jpg`
- Decision: `typeka_comparison_metadata_closed_as_r3_selector`

## Source Rows

| source | kind | fonts | text chars | Typeka evidence | use |
|---|---|---|---:|---:|---|
| `issue24_best_scan` | `PDF` | `['Helvetica']` | `7785` | `False` | scan/witness, not font layer |
| `issue24_desktop_scan` | `PDF` | `['Helvetica']` | `7785` | `False` | scan/witness, not font layer |
| `issue26_comparison` | `PDF` | `[]` | `0` | `False` | style control only |
| `issue27_comparison` | `PDF` | `[]` | `0` | `False` | style control only |
| `bitcoin3_comparison` | `PDF` | `[]` | `0` | `False` | style control only |
| `bitcoin4_issue24_witness` | `PDF` | `[]` | `0` | `False` | scan/witness, not font layer |
| `article_with_fonts` | `DOCM` | `['Typeka', 'Typeka Mix', 'Stencil', 'LonestarW00-Regular']` | `7478` | `7451` | font witness |
| `bold_docm` | `DOCM` | `['Typeka', 'Stencil']` | `1393` | `1374` | annotation/generated witness |

## Gate Result

| gate | status | evidence |
|---|---|---|
| R1 source identity | `PARTIAL` | Article with Fonts.docm is a local font witness; comparison PDFs are flattened article images, not source layout files. |
| R2 target preservation | `PASS as corroboration` | Article with Fonts.docm records Typeka/Typeka Mix across Issue 24 with 7451 Typeka-family chars. |
| R3 unit/order evidence | `FAIL` | Comparison PDFs expose zero Typeka font resources and no word/letter/line/font-order instruction. |
| R4 orientation/source discipline | `PASS` | PDF raster witnesses are separated from DOCM font-state witnesses; scan OCR Helvetica is not treated as printed typography. |
| R5 controlled improvement | `FAIL` | The comparison metadata does not improve page-76 registration or select O4/B4/G5/O5 units. |

## Assessment

- Independent comparison PDFs checked: `3`.
- Comparison PDFs with embedded font witnesses: `0`.
- Comparison PDFs with Typeka font resources: `0`.
- Comparison PDFs classified image-only/raster witnesses: `3`.
- `Article with Fonts.docm` Typeka-family character count: `7451`.
- The comparison PDFs can support broad visual/style comparisons, but they cannot prove or disprove visible printed Typeka usage by metadata because the pages are flattened images.
- The Issue 24 scan exposes only Helvetica OCR/text-layer resources; that layer remains non-authoritative for printed typography.
- Typeka remains a real Issue 24 Word-format witness, but still fails R3 because no source-backed rule names font-state units/order.

## Next Move

- Treat Article with Fonts.docm as the Typeka witness and comparison PDFs as style controls only; reopen Typeka extraction only with a source/clue that names font-state units or original layout metadata.
