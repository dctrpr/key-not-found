# Current PDF Content Transform Matrix Gate

Scope: inspected numeric content-stream placement matrices around image and OCR-form `Do` calls in the current PDFs. This checks whether the actual raster/form placement transforms supply a page, fold, original-layout, or OVERDOSE selector. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:44:07`
- PDFs / pages / placements: `3` / `24` / `40`
- Image/form/unknown Do placements: `24` / `16` / `0`
- Placement signature groups / distinct cumulative matrices: `3` / `3`
- Page 76 placements / unique placement groups: `5` / `0`
- Active unique placement groups: `0`
- Strict/context wrapper hits: `0` / `0`
- Structural stream-order matches: `5` / `5`
- Active-subset stream-order matches: `5` / `5`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pages=24|placements=40|imageDo=24|formDo=16|unknownDo=0|matrixGroups=3|distinctMatrices=3|p76Placements=5|p76UniqueGroups=0|activeUniqueGroups=0|strict=0|context=0|streamOrder=5/5|activeSubset=5/5|sourceR3=0|triggers=0/9|selectors=0`

## Placement Groups

| group | records | roles | normalized names | PDFs | article pages | p76 records | matrix | unit bbox | det | sign |
|---|---:|---|---|---|---|---:|---|---|---:|---|
| M1 | 8 | `image` | `Obj#` | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `610.56,0.0,0.0,783.36,0.0,0.0` | `0.0,0.0,610.56,783.36` | 478288.2816 | `positive` |
| M2 | 16 | `form` | `OL#` | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `1.0,0.0,0.0,1.0,0.0,0.119995` | `0.0,0.119995,1.0,1.119995` | 1.0 | `positive` |
| M3 | 16 | `image` | `I#` | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `576.0,0.0,0.0,792.0,18.0,0.0` | `18.0,0.0,594.0,792.0` | 456192.0 | `positive` |

## Page 76 Placements

| PDF | stream xref | resource | role | cm count | matrix | unit bbox | sign |
|---|---:|---|---|---:|---|---|---|
| `magazine.pdf` | 33 | `Obj5` | `image` | 1 | `610.56,0.0,0.0,783.36,0.0,0.0` | `0.0,0.0,610.56,783.36` | `positive` |
| `keyser bitcoin .pdf` | 29 | `I4` | `image` | 2 | `576.0,0.0,0.0,792.0,18.0,0.0` | `18.0,0.0,594.0,792.0` | `positive` |
| `keyser bitcoin .pdf` | 31 | `OL2` | `form` | 1 | `1.0,0.0,0.0,1.0,0.0,0.119995` | `0.0,0.119995,1.0,1.119995` | `positive` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 29 | `I4` | `image` | 2 | `576.0,0.0,0.0,792.0,18.0,0.0` | `18.0,0.0,594.0,792.0` | `positive` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 31 | `OL2` | `form` | 1 | `1.0,0.0,0.0,1.0,0.0,0.119995` | `0.0,0.119995,1.0,1.119995` | `positive` |

## Stream Order Checks

| PDF | role | article order | stream-xref order | active subset | order match |
|---|---|---|---|---|---:|
| `magazine.pdf` | `image` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `76-78-79-80` | `1` |
| `keyser bitcoin .pdf` | `form` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `76-78-79-80` | `1` |
| `keyser bitcoin .pdf` | `image` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `76-78-79-80` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `form` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `76-78-79-80` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `image` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `76-78-79-80` | `1` |

## Decision

- `current_pdf_content_transform_matrix_no_selector`
- The placement matrices collapse to ordinary renderer/OCR placement groups: full-page raster placement in `magazine.pdf`, page-image placement in the duplicate OCR PDFs, and an `OL2` OCR-form placement in the duplicate PDFs.
- Page 76 has no unique placement signature, and the active quartet has no unique placement signature.
- Stream xref ordering follows PDF construction order, so the active subset inherits page order but does not supply source-backed R3.
- No placement stream contains strict instruction/context terms after stripping PDF resource names and payloads.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
