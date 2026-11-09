# Current PDF Leaf Image Identity Gate

Scope: checked embedded PDF images and root scan page rasters for article pages 75/76 against the current canonical scan. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T03:48:13`
- Sheet: `analysis_outputs/source_audit/current_pdf_leaf_image_identity_gate/current_pdf_leaf_image_identity_gate_sheet.jpg`
- Image records / leaf pair rows: `12` / `6`
- Exact current-scan records: `2`
- Derivative-like records: `12`
- Exact current-scan leaf pairs: `1`
- Derivative-like leaf pairs: `6`
- Higher-resolution records / pairs: `0` / `0`
- Distinct improved/original-layout candidates: `0`
- PDF soft-mask / multi-image page candidates: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `records=12|pairs=6|exactRecords=2|derivativeRecords=12|exactPairs=1|derivativePairs=6|higherRecords=0|higherPairs=0|distinctImproved=0|softMasks=0|multiImagePages=0|sourceR3=0|triggers=0/9|selectors=0`

## Leaf Pair Rows

| kind | family | p75 size | p76 size | p75 MAD | p76 MAD | exact pair | derivative pair | higher-res |
|---|---|---|---|---:|---:|---:|---:|---:|
| `canonical_source_image` | `canonical_source_images` | `2544x3264` | `2544x3264` | 0.0000 | 0.0000 | True | True | False |
| `pdf_embedded_primary_image` | `analysis_outputs/external_clues/google_drive_article_download.pdf` | `2040x2805` | `2040x2805` | 51.3580 | 59.8367 | False | True | False |
| `pdf_embedded_primary_image` | `keyser bitcoin .pdf` | `2040x2805` | `2040x2805` | 51.3580 | 59.8367 | False | True | False |
| `pdf_embedded_primary_image` | `magazine.pdf` | `2544x3264` | `2544x3264` | 0.2775 | 0.2517 | False | True | False |
| `root_page_image` | `keyser bitcoin` | `2040x2805` | `2040x2805` | 51.3580 | 59.8367 | False | True | False |
| `root_page_image` | `magazine` | `2544x3264` | `2544x3264` | 0.2775 | 0.2517 | False | True | False |

## Decision

- `current_pdf_leaf_image_identity_no_distinct_source`
- The current PDFs and root scan images do not contain a distinct higher-resolution or original-layout raster for the 75/76 leaf pair.
- `magazine.pdf`/`magazine-*_1.jpg` preserve the current 2544x3264 scan; `keyser bitcoin .pdf` and the Google Drive article download are matching lower-resolution derivatives with the same page-pair identity.
- No soft mask, multi-image page, per-page identity split, or source-backed instruction/reopen trigger was found.

## Next Move

- Keep using `analysis_outputs/source_images/magazine_page_75.jpg` and `magazine_page_76.jpg` as the current-scan light-table source. Do not reopen extraction from the current PDFs unless a new physical/original source differs from these identity rows and passes R1-R5 plus R3.
