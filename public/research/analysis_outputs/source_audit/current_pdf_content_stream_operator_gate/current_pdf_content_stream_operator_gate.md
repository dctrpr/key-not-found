# Current PDF Content Stream Operator Gate

Scope: inspected decoded page content streams and form XObject streams in the current PDFs, with article page 76 treated as the target page. Invisible OCR text payload is summarized separately from PDF operator evidence. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:53:05`
- PDFs / pages checked: `3` / `24`
- Page content streams / form XObjects: `88` / `16`
- Image Do calls / form Do calls / unknown Do calls: `24` / `16` / `0`
- Text objects / text-show operators: `236` / `3854`
- Invisible text render-mode uses / visible text render-mode uses: `236` / `0`
- Vector paint / path / clip operators: `0` / `0` / `0`
- Operator strict/context hits: `0` / `0`
- OCR payload strict/context term rows: `8` / `14`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pages=24|streams=88|forms=16|imageDo=24|formDo=16|unknownDo=0|textObj=236|invisTr=236|visTr=0|paint=0|path=0|clip=0|opStrict=0|opContext=0|payloadStrictRows=8|payloadContextRows=14|p76VisTr=0|p76Paint=0|sourceR3=0|triggers=0/9|selectors=0`

## Page 76 Rows

| PDF | content streams | forms | image Do | form Do | text objects | invisible Tr | visible Tr | vector paint | operator hits | payload terms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `magazine.pdf` | 3 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | - | - |
| `keyser bitcoin .pdf` | 4 | 1 | 1 | 1 | 17 | 17 | 0 | 0 | - | bitcoin, bukele, heart, imf, overdose, sell |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 4 | 1 | 1 | 1 | 17 | 17 | 0 | 0 | - | bitcoin, bukele, heart, imf, overdose, sell |

## PDF Summary Rows

| PDF | pages | content streams | forms | image Do | form Do | visible Tr | vector paint | operator hits | OCR payload context rows |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| `magazine.pdf` | 8 | 24 | 0 | 8 | 0 | 0 | 0 | - | 0 |
| `keyser bitcoin .pdf` | 8 | 32 | 8 | 8 | 8 | 0 | 0 | - | 7 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 8 | 32 | 8 | 8 | 8 | 0 | 0 | - | 7 |

## Content Notes

- `magazine.pdf` page 76 has three page content streams: a producer comment, one full-page image `Do`, and one invisible OCR text stream using render mode `3`.
- The two duplicate OCR PDFs page 76 each have a page image `Do` plus an `OL2` form XObject; the `OL2` form is the OCR overlay and uses render mode `3` for hidden text.
- No page 76 stream contains visible text rendering, vector paint marks, clipping geometry, unknown `Do` resources, or operator/resource-name instruction terms.
- OCR payload context words are ordinary article text inside invisible OCR layers; they do not provide a source-backed unit/order/transform rule.

## Decision

- `current_pdf_content_stream_operator_no_source_layout_carrier`
- Do not reopen current PDF content streams as original-layout/source evidence.
- Treat content streams as raster page placement plus invisible OCR overlays only.

## Next Move

- Continue source/original-layout validation only if a distinct source asset or raw clue wording changes the rule space.
