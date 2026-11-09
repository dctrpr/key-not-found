# Current PDF Page Resource Order Gate

Scope: inspected page dictionaries, resource dictionaries, XObject resource names, content/resource/thumb references, page rotation, and page xref order in the current PDFs. This checks the page wrapper above the image-object layer. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:39:12`
- PDFs / pages / page-76 rows: `3` / `24` / `3`
- Page/resource signature groups: `2` / `2`
- Page 76 unique page/resource groups: `0` / `0`
- Active unique page/resource groups: `0` / `0`
- Thumbnail-bearing pages: `8`
- Special page-key rows: `0`
- Strict/context wrapper hits: `0` / `0`
- Structural page-xref order matches: `3` / `3`
- Active-subset page-xref order matches: `3` / `3`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pages=24|p76=3|pageGroups=2|resourceGroups=2|p76UniquePageGroups=0|p76UniqueResourceGroups=0|activeUniquePageGroups=0|activeUniqueResourceGroups=0|thumbPages=8|special=0|strict=0|context=0|pageOrder=3/3|activeSubset=3/3|sourceR3=0|triggers=0/9|selectors=0`

## Page And Resource Groups

| kind | group | records | PDFs | article pages | p76 records | rotations | xobject names | form names | sample |
|---|---|---:|---|---|---:|---|---|---|---|
| page | G1 | 16 | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `0` | `I1,I2,I3,I4,I5,I6,I7,I8,OL2` | `OL2` | `<< /Type /Page /Parent <ref> /MediaBox [ 0 0 <n> <n> ] /Contents [ <ref> <ref> <ref> <ref> ] /Resources <ref> >>` |
| page | G2 | 8 | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `180` | `Obj5` | `` | `<< /Contents [ <ref> <ref> <ref> ] /MediaBox [ 0 0 <n>.<n> <n>.<n> ] /Parent <ref> /Resources << /Font << /F# <ref> >> /ProcSet [ /PDF /Text /ImageB /ImageC /ImageI ] /Subtype <ref` |
| resource | G1 | 8 | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `180` | `Obj5` | `` | `<</Font<</F# <ref>>>/ProcSet[/PDF/Text/ImageB/ImageC/ImageI]/Subtype <ref>/XObject<</Obj# <ref>>>>>` |
| resource | G2 | 16 | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `0` | `I1,I2,I3,I4,I5,I6,I7,I8,OL2` | `OL2` | `<< /ProcSet [ /PDF /Text /ImageB /ImageC /ImageI ] /XObject << /I# <ref> /OL# <ref> >> >>` |

## Page Xref Order Checks

| PDF | article order | page-xref order | page xrefs | xref deltas | active subset | page-order match |
|---|---|---|---|---|---|---:|
| `magazine.pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `3-4-5-6-7-8-9-10` | `1-1-1-1-1-1-1` | `76-78-79-80` | `1` |
| `keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `5-6-7-8-9-10-11-12` | `1-1-1-1-1-1-1` | `76-78-79-80` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `5-6-7-8-9-10-11-12` | `1-1-1-1-1-1-1` | `76-78-79-80` | `1` |

## Page 76 Rows

| PDF | page xref | rotation | resource kind/xref | content xrefs | thumb xrefs | image names | form names | xobject xrefs |
|---|---:|---:|---|---|---|---|---|---|
| `magazine.pdf` | 6 | 180 | `dict/None` | `32-33-34` | `38` | `Obj5` | `` | `37` |
| `keyser bitcoin .pdf` | 8 | 0 | `xref/32` | `28-29-30-31` | `` | `I4` | `OL2` | `59-60` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 8 | 0 | `xref/32` | `28-29-30-31` | `` | `I4` | `OL2` | `59-60` |

## Decision

- `current_pdf_page_resource_order_no_source_carrier`
- Page dictionaries and resource dictionaries are ordinary page wrappers: media/trim boxes, content references, resources, rotation, thumbnails in `magazine.pdf`, and XObject resource names.
- `magazine.pdf` has page rotation `180`, thumbnail references, and a stable page-image resource name `Obj5`; the duplicate PDFs use rotation `0`, no thumbnails, image names `I1` through `I8`, and OCR form name `OL2`.
- Page 76 has no unique normalized page-dictionary or resource-signature group, and the active quartet has no unique page/resource group.
- Page xref ordering follows normal PDF page construction order. The active subset inherits page order, so it is not a source-backed selector.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
