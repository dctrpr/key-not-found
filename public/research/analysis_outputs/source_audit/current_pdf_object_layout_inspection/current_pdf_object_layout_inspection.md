# Current PDF Object/Layout Inspection

Scope: inspected the available Bitcoin article PDFs as PDF objects, not as extracted prose or key material. This checks for live text, embedded fonts, vector drawings, partial image placements, hidden layout resources, and page-76 image provenance. No key derivation, seed/WIF/address checks, hashes, or broad candidate generation was run.

- Created: `2026-05-21T14:31:30`
- PDFs checked: `3`
- PDF pages checked: `24`
- Page-76 candidate pages: `3`
- Page-76 raster-dominated pages: `3`
- Page-76 OCR/text-layer pages: `3`
- Page-76 native original-layout object evidence: `0`
- Page-76 text/fonts/vectors/partial-images: `94` / `3` / `0` / `2`
- Page-76 active phrase OCR hits / strict unit-order term hits: `0` / `0`
- Page-76 largest image dimensions: `2040x2805, 2544x3264`
- Higher-than-magazine page-76 image count: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_object_layout_inspection/current_pdf_object_layout_inspection_sheet.jpg`
- Fingerprint: `pdfs=3|sha=2|pages=24|p76=3|p76Raster=3|p76OcrText=3|p76NativeLayout=0|p76Text=94|p76Fonts=3|p76Vectors=0|p76PartialImages=2|activePhraseHits=0|unitTermHits=0|higherP76=0|sourceR3=0|triggers=0/9|selectors=0`

## Page-76 Object Rows

| PDF | pdf page | rotation | images | largest image | max coverage | text blocks | OCR active hits | unit/order terms | fonts | vectors | verdict |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | 4 | 180 | 1 | `2544x3264` | 1.000000 | 28 | `-` | `-` | 1 | 0 | raster + OCR text |
| `keyser bitcoin .pdf` | 4 | 0 | 1 | `2040x2805` | 0.941176 | 33 | `-` | `-` | 1 | 0 | raster + OCR text |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 4 | 0 | 1 | `2040x2805` | 0.941176 | 33 | `-` | `-` | 1 | 0 | raster + OCR text |

## PDF-Level Notes

- `magazine.pdf`: pages `8`, sha `a0714dcbe503ecdf`, raster/OCR/native-layout pages `8/8/0`, text/font/vector pages `8/8/0`, image dimensions `2544x3264`.
- `keyser bitcoin .pdf`: pages `8`, sha `0078fe23401fab48`, raster/OCR/native-layout pages `8/8/0`, text/font/vector pages `8/8/0`, image dimensions `2040x2805`.
- `analysis_outputs/external_clues/google_drive_article_download.pdf`: pages `8`, sha `0078fe23401fab48`, raster/OCR/native-layout pages `8/8/0`, text/font/vector pages `8/8/0`, image dimensions `2040x2805`.

## Decision

- `raster_plus_ocr_text_no_original_layout_selector`
- The current PDFs expose page 76 as raster page images with OCR/text overlays, not native original-layout design objects. The text layer is a source witness but it is corrupt/derivative and does not add fonts, vectors, hidden partial placements, higher-resolution assets, or strict unit/order wording that would unlock extraction.
- Keep using the current held-to-light simulator, but move the next bounded pass to a crop-level light-table inspection of the valid 75->76 leaf and the best 79->76 visual-registration benchmark around O4/B4/G5/O5. Do not re-open key extraction from PDF object structure.
