# Current PDF Color Management / ExtGState Gate

Scope: inspected current PDFs for color-management and graphics-state carriers: catalog OutputIntents, page ColorSpace/ExtGState resources, blend/opacity/transfer/overprint keys, image Decode/Intent/Interpolate keys, and color operators. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T09:39:24`
- PDFs / page rows: `3` / `24`
- OutputIntent objects: `0`
- Page-76 unique resource signatures: `0`
- ExtGState objects / page-76 ExtGState objects: `0` / `0`
- Blend/opacity/transfer/overprint ExtGState objects: `0` / `0` / `0` / `0`
- ColorSpace objects / page-76 ColorSpace objects: `0` / `0`
- ICCBased / Separation-or-DeviceN ColorSpace objects: `0` / `0`
- Image objects / page-76 image objects: `24` / `3`
- Image Decode-array rows / special image color-key rows: `0` / `0`
- Strict/context hits: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pages=24|outputIntents=0|page76UniqueRes=0|ext=0|p76ext=0|bm=0|opacity=0|transfer=0|overprint=0|colorspaces=0|p76colorspaces=0|icc=0|sep=0|images=24|decode=0|specialImages=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | catalog keys | output intents | page76 res sigs | page76 ExtGState | page76 ColorSpace | page76 images |
|---|---:|---:|---:|---:|---:|---:|
| `magazine.pdf` | 0 | 0 | 1 | 0 | 0 | 1 |
| `keyser bitcoin .pdf` | 0 | 0 | 1 | 0 | 0 | 1 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 0 | 0 | 1 | 0 | 0 | 1 |

## Decision

- `current_pdf_color_management_extgstate_no_selector`
- No current PDF exposes a page-76-unique color-management, OutputIntent, ColorSpace, ExtGState, blend/opacity/transfer, or image Decode carrier.
- This keeps current PDFs as raster/OCR witnesses only, not original-layout extraction authority.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
