# Current PDF Image XObject Dictionary Gate

Scope: inspected image XObject dictionaries, thumbnail dictionaries, special image-object keys, and image xref numbering in the current PDFs. This checks the PDF object wrapper around page rasters, not raw JPEG metadata or compression internals. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:29:06`
- PDFs / image objects: `3` / `32`
- Page image / thumbnail objects: `24` / `8`
- Normalized dictionary groups: `3`
- Page 76 objects / unique dictionary groups: `4` / `0`
- Active unique dictionary groups: `0`
- Special image-key rows: `0`
- Strict/context dictionary hits: `0` / `0`
- Structural xref order matches: `4` / `4`
- Active-subset xref order matches: `4` / `4`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|objects=32|pageImages=24|thumbs=8|dictGroups=3|p76Objects=4|p76UniqueGroups=0|activeUniqueGroups=0|specialKeys=0|strict=0|context=0|structOrder=4/4|activeSubset=4/4|sourceR3=0|triggers=0/9|selectors=0`

## Dictionary Groups

| group | records | roles | PDFs | article pages | p76 records | keys | sample |
|---|---:|---|---|---|---:|---|---|
| D1 | 8 | `page_image` | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `BitsPerComponent,ColorSpace,DCTDecode,DeviceRGB,Filter,Height,Image,Length,Subtype,Type,Width,XObject` | `<< /BitsPerComponent 8 /ColorSpace /DeviceRGB /Filter /DCTDecode /Height 3264 /Subtype /Image /Type /XObject /Width 2544 /Length <n> >>` |
| D2 | 8 | `page_thumbnail` | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `BitsPerComponent,ColorSpace,DCTDecode,DeviceRGB,Filter,Height,Length,Width` | `<< /BitsPerComponent 8 /ColorSpace /DeviceRGB /Filter /DCTDecode /Height 106 /Width 82 /Length <n> >>` |
| D3 | 16 | `page_image` | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `BitsPerComponent,ColorSpace,DCTDecode,DeviceRGB,Filter,Height,Image,Length,Subtype,Type,Width,XObject` | `<< /Length <n> /Type /XObject /Subtype /Image /Filter /DCTDecode /BitsPerComponent 8 /Width 2040 /Height 2805 /ColorSpace /DeviceRGB >>` |

## Xref Order Checks

| PDF | role | article order | xref order | xref deltas | active subset | structural page-order match |
|---|---|---|---|---|---|---:|
| `magazine.pdf` | `page_image` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `7-7-7-7-7-7-7` | `76-78-79-80` | `1` |
| `magazine.pdf` | `page_thumbnail` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `7-7-7-7-7-7-7` | `76-78-79-80` | `1` |
| `keyser bitcoin .pdf` | `page_image` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `2-2-2-2-2-2-2` | `76-78-79-80` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `page_image` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `2-2-2-2-2-2-2` | `76-78-79-80` | `1` |

## Decision

- `current_pdf_image_xobject_dictionary_no_source_carrier`
- Image object dictionaries contain ordinary PDF image keys only: dimensions, color space, filter, bit depth, subtype/type, and length.
- No `/DecodeParms`, `/SMask`, `/Mask`, `/Metadata`, `/Alternates`, `/OC`, `/StructParent`, or comparable special image-object carrier appears.
- Page 76 has no unique normalized image-object dictionary group; active pages have no unique dictionary group.
- Xref numbering follows normal PDF page construction order. The active subset inherits page order from that structure, so it is not a source-backed selector.

## Next Move

- Continue source/original-layout validation only if a distinct physical scan, source export, or raw clue wording supplies a unit/order/transform.
