# Current PDF Page Thumbnail Gate

Scope: inspected embedded `/Thumb` streams in the current PDFs as auxiliary source rasters, with page 76 treated as the target page. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:45:32`
- PDFs / pages checked: `3` / `24`
- Pages with thumbnails / page-76 thumbnails: `8` / `1`
- Unique thumbnail images / total thumbnail bytes: `8` / `87231`
- Higher-resolution page-76 thumbnails / distinct source carriers: `0` / `0`
- Strict instruction hits / context hits: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Contact sheet: `analysis_outputs/source_audit/current_pdf_page_thumbnail_gate/current_pdf_page_thumbnail_gate_sheet.jpg`
- Fingerprint: `pdfs=3|pages=24|thumbPages=8|p76Thumbs=1|uniqueThumbs=8|thumbBytes=87231|contentXrefMatches=0|higherP76=0|distinctCarrier=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | pages | thumbnail pages | page-76 thumbnails |
|---|---:|---:|---:|
| `magazine.pdf` | 8 | 8 | 1 |
| `keyser bitcoin .pdf` | 8 | 0 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 8 | 0 | 0 |

## Thumbnail Rows

| PDF | article page | thumb xref | thumb size | bytes | largest page image | pixel ratio | best downsample MAD | higher than page image |
|---|---:|---:|---|---:|---|---:|---:|---|
| `magazine.pdf` | 73 | 17 | 82x106 | 10926 | 2544x3264 | 0.00104677 | 11.1021 | no |
| `magazine.pdf` | 74 | 24 | 82x106 | 12678 | 2544x3264 | 0.00104677 | 16.1711 | no |
| `magazine.pdf` | 75 | 31 | 82x106 | 9524 | 2544x3264 | 0.00104677 | 16.4023 | no |
| `magazine.pdf` | 76 | 38 | 82x106 | 9867 | 2544x3264 | 0.00104677 | 15.2244 | no |
| `magazine.pdf` | 77 | 45 | 82x106 | 12751 | 2544x3264 | 0.00104677 | 20.3258 | no |
| `magazine.pdf` | 78 | 52 | 82x106 | 9885 | 2544x3264 | 0.00104677 | 15.0622 | no |
| `magazine.pdf` | 79 | 59 | 82x106 | 9027 | 2544x3264 | 0.00104677 | 14.1596 | no |
| `magazine.pdf` | 80 | 66 | 82x106 | 12573 | 2544x3264 | 0.00104677 | 9.3285 | no |

## Decision

- `current_pdf_page_thumbnail_no_distinct_source_carrier`
- Only `magazine.pdf` exposes page thumbnails: one tiny `82x106` DCT stream for each article page `73-80`.
- The derivative OCR PDFs expose no `/Thumb` streams.
- The page-76 thumbnail is not a higher-resolution or independent layout/source carrier; it is roughly `0.105%` of the page-image pixels and has no separate text, layer, annotation, or instruction payload.
- Do not reopen PDF page thumbnails as an extraction path.

## Next Move

- Treat embedded thumbnails as provenance-only previews. The next useful direction remains true source/original-layout comparison or raw clue wording that explicitly names the extraction unit/order/transform.
