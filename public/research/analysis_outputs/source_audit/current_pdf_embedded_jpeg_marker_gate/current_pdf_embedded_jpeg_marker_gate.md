# Current PDF Embedded JPEG Marker Gate

Scope: inspected raw JPEG marker wrappers in embedded page images and page thumbnails from the current PDFs, especially page 76. This checks for APP/COM marker payloads such as EXIF, XMP, ICC, Photoshop, comments, or readable instruction/context strings. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:11:15`
- PDFs / JPEG records: `3` / `32`
- Page images / thumbnails / page-76 records: `24` / `8` / `4`
- JPEG records / parse warnings: `32` / `0`
- APP / COM marker segments: `40` / `0`
- Structural JFIF segments: `32`
- Non-structural APP/COM segments: `8`
- Provenance metadata segments: `8`
- Source-instruction carrier segments: `0`
- Strict/context marker hits: `0` / `0`
- Unique page-image / thumbnail hashes: `16` / `8`
- Unique marker signatures: `3`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|records=32|pageImages=24|thumbs=8|p76Records=4|jpeg=32|warn=0|app=40|com=0|jfif=32|nonstruct=8|metadata=8|instrCarrier=0|strict=0|context=0|pageHashes=16|thumbHashes=8|markerSigs=3|sourceR3=0|triggers=0/9|selectors=0`

## Page 76 Records

| PDF | role | xref | px | bytes | APP/COM | metadata | instruction carrier | hits | marker signature |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `magazine.pdf` | `page_image` | 37 | `2544x3264` | 606236 | 1 | 0 | 0 | - | `SOI:structural:0,APP0:structural_jfif:14,DQT:marker:130,DHT:marker:416,SOF0:marker:15,SOS:marker:10` |
| `magazine.pdf` | `page_thumbnail` | 38 | `82x106` | 9867 | 2 | 1 | 0 | - | `SOI:structural:0,APP0:structural_jfif:14,APP1:exif:282,DQT:marker:65,DQT:marker:65,SOF0:marker:15,DHT:marker:29,DHT:mark` |
| `keyser bitcoin .pdf` | `page_image` | 59 | `2040x2805` | 765780 | 1 | 0 | 0 | - | `SOI:structural:0,APP0:structural_jfif:14,DQT:marker:65,DQT:marker:65,SOF0:marker:15,DHT:marker:29,DHT:marker:179,DHT:mar` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `page_image` | 59 | `2040x2805` | 765780 | 1 | 0 | 0 | - | `SOI:structural:0,APP0:structural_jfif:14,DQT:marker:65,DQT:marker:65,SOF0:marker:15,DHT:marker:29,DHT:marker:179,DHT:mar` |

## PDF Summary Rows

| PDF | records | page images | thumbnails | metadata segments | instruction carriers | marker hits |
|---|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | 16 | 8 | 8 | 8 | 0 | - |
| `keyser bitcoin .pdf` | 8 | 8 | 0 | 0 | 0 | - |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 8 | 8 | 0 | 0 | 0 | - |

## Thumbnail EXIF Provenance Rows

| PDF | article page | xref | sample | hits |
|---|---:|---:|---|---|
| `magazine.pdf` | 73 | 17 | `Exif Canon 2025:10:01 16:19:01 0221 0100` | - |
| `magazine.pdf` | 74 | 24 | `Exif Canon 2025:10:01 16:22:52 0221 0100` | - |
| `magazine.pdf` | 75 | 31 | `Exif Canon 2025:10:01 16:21:45 0221 0100` | - |
| `magazine.pdf` | 76 | 38 | `Exif Canon 2025:10:01 16:26:26 0221 0100` | - |
| `magazine.pdf` | 77 | 45 | `Exif Canon 2025:10:01 16:27:50 0221 0100` | - |
| `magazine.pdf` | 78 | 52 | `Exif Canon 2025:10:01 16:23:58 0221 0100` | - |
| `magazine.pdf` | 79 | 59 | `Exif Canon 2025:10:01 16:25:19 0221 0100` | - |
| `magazine.pdf` | 80 | 66 | `Exif Canon 2025:10:01 16:28:58 0221 0100` | - |

## Marker Notes

- Every inspected DCT stream begins with normal JPEG SOI and contains a structural JFIF APP0 segment.
- The full embedded page images have no EXIF, XMP, ICC profile payloads, Photoshop APP13 payloads, COM comments, or other non-structural APP marker carriers.
- The eight tiny `magazine.pdf` page thumbnails have small Canon EXIF APP1 provenance blocks with timestamps, including page 76, but those blocks contain no strict instruction or puzzle context terms.
- Page 76's main image has only ordinary JPEG wrapper markers; its thumbnail has only JFIF plus the small Canon timestamp EXIF block already constrained to thumbnail provenance.

## Decision

- `current_pdf_embedded_jpeg_marker_no_source_carrier`
- Do not reopen embedded JPEG marker metadata as source/original-layout evidence.
- Treat these wrappers as normal image encoding metadata, not puzzle instructions.

## Next Move

- Continue source/original-layout validation only if a distinct source asset or raw clue wording changes the unit/order/transform evidence.
