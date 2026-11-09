# Current PDF OCR Instruction Scope Gate

Scope: scanned the current PDFs' OCR/text overlay tokens for bounded action-plus-unit instruction windows. This checks whether the current Bitcoin PDF text layer itself supplies a unit/order rule. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T20:07:41`
- PDFs / pages / tokens: `3` / `24` / `4160`
- Action / unit / transform / target term hits: `10` / `10` / `0` / `98`
- Action-plus-unit windows / candidate windows: `0` / `0`
- Hard phrase hits: `0`
- Visible painted text spans / invisible Type3 spans: `0` / `755`
- Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`
- Fingerprint: `pdfs=3|pages=24|tokens=4160|action=10|unit=10|transform=0|target=98|actionUnitWindows=0|candidates=0|hardPhrases=0|visible=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | pages | tokens | action | unit | transform | target | action+unit windows | candidates | hard phrases |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `magazine.pdf` | `8` | `1636` | `0` | `0` | `0` | `0` | `0` | `0` | `0` |
| `keyser bitcoin .pdf` | `8` | `1262` | `5` | `5` | `0` | `49` | `0` | `0` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `8` | `1262` | `5` | `5` | `0` | `49` | `0` | `0` | `0` |

## Isolated Strict Terms

| PDF | term counts |
|---|---|
| `magazine.pdf` | `-` |
| `keyser bitcoin .pdf` | `first:3, get:3, look:1, open:1, right:1, words:1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `first:3, get:3, look:1, open:1, right:1, words:1` |

## Candidate Windows

- None. No current PDF OCR action term appears within +/-6 tokens of a unit or transform term.

## Decision

- `current_pdf_ocr_instruction_scope_no_selector`
- The high-resolution `magazine.pdf` OCR layer has no strict action/unit/transform terms in this token pass.
- The two duplicate OCR PDFs contain only isolated ordinary words such as `look`, `words`, `get`, `open`, `first`, and `right`; none form a bounded action-plus-unit instruction window.
- All page-76/current-PDF text overlay spans remain invisible derivative OCR, with no visible painted text spans and no source-backed R3 bridge.

## Next Move

- Stop treating current PDF OCR/layout text as original-layout instruction evidence.
- Reopen OCR/layout text only for a distinct source PDF/export or raw clue wording that supplies action plus unit/order.
