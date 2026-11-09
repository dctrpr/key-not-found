# Current PDF Trailer/Xref Integrity Gate

Scope: inspected PDF trailer/xref/file-storage integrity, incremental-update markers, object streams, document IDs, catalog carriers, and page object order in the current PDFs. This checks file storage/provenance below page dictionaries; it does not treat OCR text as key material. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:57:31`
- PDFs / unique file hashes: `3` / `2`
- Xref object total: `301`
- startxref / EOF markers: `3` / `3`
- Incremental-update candidates: `0`
- Object streams / xref streams: `0` / `0`
- Encrypted PDFs / nonzero-generation objects: `0` / `0`
- Hidden trailer/storage carrier markers: `0`
- Trailer ID present count: `3`
- Document carrier rows: `2`
- Strict/context storage hits: `0` / `0`
- Structural page-xref order matches: `3` / `3`
- Active-subset page-xref order matches: `3` / `3`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|uniqueSha=2|xrefObjects=301|startxref=3|eof=3|incremental=0|objStm=0|xrefStm=0|encrypted=0|nonzeroGen=0|hiddenTrailer=0|idPresent=3|strict=0|context=0|pageOrder=3/3|activeSubset=3/3|sourceR3=0|triggers=0/9|selectors=0`

## PDF Storage Rows

| PDF | sha16 | size | format | creator | xref len | startxref | EOF | ID count | root | info | repaired | encrypted |
|---|---|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| `magazine.pdf` | `a0714dcbe503ecdf` | 6904582 | `PDF 1.3` | `` | 67 | `6903098` | 1 | 2 | 1 |  | 0 | 0 |
| `keyser bitcoin .pdf` | `0078fe23401fab48` | 6512512 | `PDF 1.3` | `PDF24 Tools - OCR` | 117 | `6510013` | 1 | 2 | 1 | 4 | 0 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `0078fe23401fab48` | 6512512 | `PDF 1.3` | `PDF24 Tools - OCR` | 117 | `6510013` | 1 | 2 | 1 | 4 | 0 | 0 |

## Page 76 Storage Rows

| PDF | page xref | content xrefs | image xrefs | form xrefs | rotation |
|---|---:|---|---|---|---:|
| `magazine.pdf` | 6 | `32-33-34` | `37` | `` | 180 |
| `keyser bitcoin .pdf` | 8 | `28-29-30-31` | `59` | `60` | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 8 | `28-29-30-31` | `59` | `60` | 0 |

## Page Xref Order Checks

| PDF | article order | page-xref order | page xrefs | active subset | order match |
|---|---|---|---|---|---:|
| `magazine.pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `3-4-5-6-7-8-9-10` | `76-78-79-80` | `1` |
| `keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `5-6-7-8-9-10-11-12` | `76-78-79-80` | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `73-74-75-76-77-78-79-80` | `73-74-75-76-77-78-79-80` | `5-6-7-8-9-10-11-12` | `76-78-79-80` | `1` |

## Decision

- `current_pdf_trailer_xref_integrity_no_source_carrier`
- The current PDFs are simple non-incremental PDF 1.3 files at this layer: one `startxref` per file, no `/Prev`, no xref streams, no object streams, no encryption, and no nonzero-generation object carrier.
- Trailer IDs and duplicate-PDF `/Info` records are provenance metadata only; they do not distinguish page 76 or the active quartet.
- Page xref order follows article/page order in all 3 PDFs, and the active subset remains `76-78-79-80`; object chronology supplies no independent selector.
- No document-level carrier keys, strict instruction terms, context terms, or source-backed R3 trigger hits appear at this file-storage layer.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
