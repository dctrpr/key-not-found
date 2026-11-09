# Current PDF Container Metadata Gate

Scope: inspected the current PDFs for hidden/container-level source carriers: metadata, XMP, name trees, attachments, annotations, widgets, links, optional content/layers, actions, and special catalog/page keys. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:36:38`
- PDFs / pages checked: `3` / `24`
- Signal metadata fields / XML metadata streams: `4` / `0`
- Name trees / non-empty name trees: `2` / `0`
- Attachments / annotations / widgets / links: `0` / `0` / `0` / `0`
- Optional-content groups / layers / layer UI configs: `0` / `0` / `0`
- Special action object rows: `0`
- Strict instruction hits / context hits: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pages=24|metadata=4|xml=0|names=2|nonEmptyNames=0|emb=0|annots=0|widgets=0|links=0|ocg=0|layers=0|actions=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | metadata | names | non-empty names | XML | attach | annots | widgets | links | OCG/layers | actions | strict | context |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|
| `magazine.pdf` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0 | - | - |
| `keyser bitcoin .pdf` | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0 | - | - |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0 | - | - |

## Container Notes

- `magazine.pdf` metadata: format=PDF 1.3
  - Catalog specials: -
  - Object pattern rows: -
- `keyser bitcoin .pdf` metadata: format=PDF 1.3, creator=PDF24 Tools - OCR, creationDate=D:20230329010247+00'00'
  - Catalog specials: Names=xref:3 0 R
  - Object pattern rows: xref 1 /Names; xref 3 /Names,/Dests
- `analysis_outputs/external_clues/google_drive_article_download.pdf` metadata: format=PDF 1.3, creator=PDF24 Tools - OCR, creationDate=D:20230329010247+00'00'
  - Catalog specials: Names=xref:3 0 R
  - Object pattern rows: xref 1 /Names; xref 3 /Names,/Dests

## Decision

- `current_pdf_container_metadata_no_hidden_source_carrier`
- The current PDFs do not expose hidden source carriers: no attachments, annotations, widgets, links, optional-content layers, JavaScript/action entries, XMP metadata, or non-empty name trees.
- The only container signal in the derivative duplicate PDFs is `PDF24 Tools - OCR` plus an empty destination name tree, matching already-closed derivative/OCR provenance.
- Do not reopen PDF container metadata as an extraction path.

## Next Move

- Continue to treat the current PDFs as raster/OCR witnesses only. The best direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.
