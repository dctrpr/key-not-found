# Current PDF OVERDOSE Body-Basis Reflection Gate

Scope: used repeated OCR `OVERDOSE` pages with a readable first body line, reflected locked O4/B4/G5/O5 boxes across the header-to-body axis and the perpendicular body-start axis, and checked reflected boxes for OCR words, target terms, strict unit/order words, all-four target coverage, and active-order structure. This is a bounded layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T15:24:15`
- Decision: `current_pdf_overdose_body_basis_reflection_no_selector`
- PDFs checked / body-basis rows / transform variants: `3` / `4` / `8`
- Reflected boxes / in-page boxes / text-hit boxes: `32` / `10` / `2`
- Target-term boxes / strict-term boxes: `0` / `0`
- All-four variants / active-order variants / candidates: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate/current_pdf_overdose_body_basis_reflection_gate_sheet.jpg`
- Fingerprint: `pdfs=3|basisRows=4|variants=8|boxRows=32|inPage=10|textRows=2|targetRows=0|strictRows=0|allFourVariants=0|activeOrderVariants=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Body-Basis Rows

| PDF | article page | body vector | angle | first body line |
|---|---:|---|---:|---|
| `keyser bitcoin .pdf` | `76` | `[-179.2271, 50.7435]` | `164.1919` | `Get some toxicity. Get some bitcoin. Open your heart to` |
| `keyser bitcoin .pdf` | `78` | `[-313.1291, 50.6329]` | `170.8148` | `We've never had an economy and a money` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `[-179.2271, 50.7435]` | `164.1919` | `Get some toxicity. Get some bitcoin. Open your heart to` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `[-313.1291, 50.6329]` | `170.8148` | `We've never had an economy and a money` |

## Transform Variants

| PDF | article page | transform | in-page boxes | text-hit boxes | target boxes | strict boxes | target ids | target order | candidate |
|---|---:|---|---:|---:|---:|---:|---|---|---:|
| `keyser bitcoin .pdf` | `76` | `body_axis_mirror` | `0` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `76` | `body_start_perpendicular_mirror` | `1` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `78` | `body_axis_mirror` | `0` | `0` | `0` | `0` | `-` | `-` | `0` |
| `keyser bitcoin .pdf` | `78` | `body_start_perpendicular_mirror` | `4` | `1` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `body_axis_mirror` | `0` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `body_start_perpendicular_mirror` | `1` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `body_axis_mirror` | `0` | `0` | `0` | `0` | `-` | `-` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `body_start_perpendicular_mirror` | `4` | `1` | `0` | `0` | `-` | `-` | `0` |

## Text-Hit Reflected Boxes

| PDF | article page | transform | target | words | target ids | strict | preview |
|---|---:|---|---|---:|---|---:|---|
| `keyser bitcoin .pdf` | `78` | `body_start_perpendicular_mirror` | `O4` | `4` | `-` | `0` | `aé economy O aed` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `body_start_perpendicular_mirror` | `O4` | `4` | `-` | `0` | `aé economy O aed` |

## Decision

- `current_pdf_overdose_body_basis_reflection_no_selector`.
- Body-axis and body-start perpendicular reflections do not produce all-four target coverage, active-order target coverage, or strict unit/order wording.
- Text contacts, where present, are ordinary prose contacts rather than source-backed extraction instructions.

## Next Move

- Keep OVERDOSE body-basis reflection mechanics closed for the current PDFs. Reopen only if a true source asset or raw clue names a body-axis, mirror, fold, or unit/order rule.
