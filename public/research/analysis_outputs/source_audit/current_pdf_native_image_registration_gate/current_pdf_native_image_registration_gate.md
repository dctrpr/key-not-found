# Current PDF Native Image Registration Gate

Scope: used each PDF's embedded page images and image placement boxes to simulate the valid page 75 -> page 76 light-table view with no free registration search. No key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T07:07:47`
- Decision: `current_pdf_native_image_registration_no_selector`
- PDFs / pairs: `3` / `3`
- Active rows / projected OVERDOSE slots: `12` / `24`
- Same image rect pairs / placement offset pairs / side-margin pairs: `3` / `0` / `2`
- Active above control p95 / >=10% / >=25%: `2` / `2` / `2`
- All-four active above p95 PDFs / all-four >=10% PDFs: `0` / `0`
- Max active / mean active / max control source-only coverage: `0.5800` / `0.1187` / `0.8795`
- Max projected OVERDOSE-slot source-only coverage / slots >=25%: `0.6341` / `2`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_native_image_registration_gate/current_pdf_native_image_registration_gate_sheet.jpg`
- Fingerprint: `pdfs=3|pairs=3|activeRows=12|slots=24|sameRects=3|offsetPairs=0|sideMargins=2|activeMax=0.5800|activeMean=0.1187|activeP95=2|active10=2|active25=2|allFourP95=0|allFour10=0|controlMax=0.8795|slotMax=0.6341|slot25=2|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | image size | same rect | rect delta pt | orientation | active max | active >=10 | active >p95 | slot max | slot >=25 |
|---|---:|---|---|---|---:|---:|---:|---:|---:|
| `magazine.pdf` | `2544x3264` | `True` | `[0.0, 0.0, 0.0, 0.0]` | `rotate180` | 0.0058 | 0 | 0 | 0.2487 | 0 |
| `keyser bitcoin .pdf` | `2040x2805` | `True` | `[0.0, 0.0, 0.0, 0.0]` | `identity` | 0.5800 | 1 | 1 | 0.6341 | 1 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `2040x2805` | `True` | `[0.0, 0.0, 0.0, 0.0]` | `identity` | 0.5800 | 1 | 1 | 0.6341 | 1 |

## Active Rows

| PDF | target | coverage | control p95 | control percentile | >=10 | >=25 |
|---|---|---:|---:|---:|---|---|
| `magazine.pdf` | `O4` | 0.0042 | 0.5038 | 0.269 | `False` | `False` |
| `magazine.pdf` | `B4` | 0.0000 | 0.4771 | 0.346 | `False` | `False` |
| `magazine.pdf` | `G5` | 0.0058 | 0.5305 | 0.320 | `False` | `False` |
| `magazine.pdf` | `O5` | 0.0032 | 0.4359 | 0.255 | `False` | `False` |
| `keyser bitcoin .pdf` | `O4` | 0.5800 | 0.4677 | 1.000 | `True` | `True` |
| `keyser bitcoin .pdf` | `B4` | 0.0559 | 0.7198 | 0.508 | `False` | `False` |
| `keyser bitcoin .pdf` | `G5` | 0.0694 | 0.5623 | 0.398 | `False` | `False` |
| `keyser bitcoin .pdf` | `O5` | 0.0004 | 0.3595 | 0.123 | `False` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O4` | 0.5800 | 0.4677 | 1.000 | `True` | `True` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `B4` | 0.0559 | 0.7198 | 0.508 | `False` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `G5` | 0.0694 | 0.5623 | 0.398 | `False` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O5` | 0.0004 | 0.3595 | 0.123 | `False` | `False` |

## Decision

- `current_pdf_native_image_registration_no_selector`
- Do not promote PDF-native image placement, page-image rect parity, side margins, or exact PDF embedded-image registration as selectors.
- The PDFs preserve the same page 75/page 76 image rectangles within each pair; no placement offset or hidden registration cue appears, and exact native registration does not make the active quartet an all-four outlier.
- Next move: require distinct physical/original-layout source material or raw clue wording that explicitly names transform, unit, and order before reopening selector/key checks.
