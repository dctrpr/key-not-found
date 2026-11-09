# Current PDF Form XObject Dictionary Gate

Scope: inspected Form XObject dictionaries, OCR form BBox/Matrix/resources, stream render mode, and form xref order in the current PDFs. This checks the duplicate-PDF `OL2` OCR form wrappers, not OCR text extraction as key material. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:50:17`
- PDFs / form objects: `3` / `16`
- Normalized dictionary groups: `1`
- Page 76 forms / unique dictionary groups: `2` / `0`
- Active unique dictionary groups: `0`
- Special form-key rows: `0`
- Visible text render-mode rows: `0`
- Strict/context wrapper hits: `0` / `0`
- Structural form-xref order matches: `3` / `3`
- Active-subset form-xref order matches: `3` / `3`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|forms=16|dictGroups=1|p76Forms=2|p76UniqueGroups=0|activeUniqueGroups=0|special=0|visibleText=0|strict=0|context=0|xrefOrder=3/3|activeSubset=3/3|sourceR3=0|triggers=0/9|selectors=0`

## Dictionary Groups

| group | records | PDFs | article pages | p76 records | names | bbox | matrix | keys | sample |
|---|---:|---|---|---:|---|---|---|---|---|
| F1 | 16 | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `OL2` | `[0 0 612 791.76]` | `[1 0 0 1 0 0]` | `BBox,Filter,FlateDecode,Font,Form,FormType,ImageB,ImageC,ImageI,Length,Matrix,PDF,ProcSet,Resources,Subtype,Text,Type,XObject,f` | `<< /Length <n> /Filter /FlateDecode /Type /XObject /Subtype /Form /Resources << /ProcSet [ /PDF /Text /ImageB /ImageI /ImageC ] /Font << /f-#-# <ref> >> >> /FormType <n> /BBox [ <n` |

## Page 76 Forms

| PDF | xref | name | bbox | matrix | stream bytes | text objects | render modes | visible Tr |
|---|---:|---|---|---|---:|---:|---|---:|
| `keyser bitcoin .pdf` | 60 | `OL2` | `[0 0 612 791.76]` | `[1 0 0 1 0 0]` | 15653 | 17 | `3` | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 60 | `OL2` | `[0 0 612 791.76]` | `[1 0 0 1 0 0]` | 15653 | 17 | `3` | 0 |

## Form Xref Order Checks

| PDF | article order | form-xref order | form xrefs | active subset | order match |
|---|---|---|---|---|---:|
| `magazine.pdf` | `` | `` | `` | `` | `1` |
| `keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `54-56-58-60-62-64-66-68` | `76-78-79-80` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `54-56-58-60-62-64-66-68` | `76-78-79-80` | `1` |

## Decision

- `current_pdf_form_xobject_dictionary_no_source_carrier`
- The duplicate-PDF OCR forms are ordinary `/Subtype /Form` wrappers named `OL2` with full-page BBox `[0 0 612 791.76]`, identity Matrix `[1 0 0 1 0 0]`, and a font resource.
- Page 76 has no unique normalized form dictionary group, and the active quartet has no unique form dictionary group.
- Form xref ordering follows normal PDF construction order; stream byte lengths vary with OCR payload density and do not supply a source-backed unit/order/transform.
- All OCR form text remains invisible render-mode `3`; no special form keys, visible text, or strict instruction terms appear.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
