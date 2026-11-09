# Current PDF Logical Structure Gate

Scope: inspected the current PDFs for tagged-PDF/logical-structure carriers: StructTreeRoot, MarkInfo, ActualText, Alt text, MCID, Artifact, BDC/BMC/EMC marked-content operators, and related catalog keys. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T06:37:34`
- PDFs: `3`
- Tagged catalog count: `0`
- Logical object marker count: `0`
- Decoded content marker count / page-76 decoded marker count: `0` / `0`
- Raw-only BDC candidates: `1`
- Strict context hits: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_logical_structure_gate/current_pdf_logical_structure_gate_sheet.jpg`
- Fingerprint: `pdfs=3|taggedCatalogs=0|logicalObjects=0|contentMarkers=0|p76ContentMarkers=0|rawOnlyBDC=1|strict=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | tagged catalog | logical objects | decoded content markers | p76 markers | raw-only BDC | strict hits |
|---|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | `-` | 0 | 0 | 0 | 1 | `-` |
| `keyser bitcoin .pdf` | `-` | 0 | 0 | 0 | 0 | `-` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `-` | 0 | 0 | 0 | 0 | `-` |

## Decision

- `current_pdf_logical_structure_no_selector`
- No current PDF exposes StructTreeRoot, MarkInfo, ActualText, Alt text, MCID, or page-76 marked-content operators as a carrier.
- The lone raw-byte `BDC` occurrence is not present in decoded content streams and is not a logical page-content marker.
- PDF logical structure stays closed for the current scan/PDF set.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
