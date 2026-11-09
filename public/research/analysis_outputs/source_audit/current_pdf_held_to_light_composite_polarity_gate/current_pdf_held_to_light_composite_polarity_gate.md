# Current PDF Held-to-Light Composite Polarity Gate

Scope: created a held-to-light simulator from each current PDF's embedded page-75 and page-76 article images, using only exact page placement and four fixed physical orientation hypotheses. No shift search, OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39 checks, or brute force was run.

- Created: `2026-05-24T07:23:07`
- Decision: `current_pdf_held_to_light_composite_polarity_no_selector`
- PDFs / transforms / variants: `3` / `4` / `12`
- Active rows / projected OVERDOSE slot rows: `48` / `96`
- Best active >=10% / above control p95 / clean-through >=10%: `3` / `0` / `3`
- All-four >=10% / above p95 / clean-through variants: `0` / `0` / `0`
- Best mean active source-only coverage: `0.1431`
- Magazine physical-back active >=10% / mean source-only: `0` / `0.0033`
- Max active / max control / max OVERDOSE-slot source-only coverage: `0.5800` / `0.9998` / `0.6341`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/current_pdf_held_to_light_composite_polarity_gate_sheet.jpg`
- Simulator images: `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/magazine_physical_back_mirror_held_to_light_full.jpg, analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/magazine_physical_back_mirror_held_to_light_active_crop.jpg`
- Fingerprint: `pdfs=3|transforms=4|variants=12|activeRows=48|slots=96|best10=3|bestP95=0|all10=0|allP95=0|magPhys10=0|magPhysMean=0.0033|activeMax=0.5800|controlMax=0.9998|slotMax=0.6341|sourceR3=0|triggers=0/9|selectors=0`

## Variant Rows

| PDF | transform | mean active | min active | max active | >=10 | >p95 | clean10 | slot max |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `magazine.pdf` | `physical_back_mirror` | 0.0033 | 0.0000 | 0.0058 | 0 | 0 | 0 | 0.2487 |
| `magazine.pdf` | `same_side_no_mirror` | 0.0350 | 0.0033 | 0.1118 | 1 | 0 | 0 | 0.1979 |
| `magazine.pdf` | `back_mirror_rotate180` | 0.0199 | 0.0000 | 0.0643 | 0 | 0 | 0 | 0.1122 |
| `magazine.pdf` | `front_rotate180` | 0.0025 | 0.0000 | 0.0067 | 0 | 0 | 0 | 0.1359 |
| `keyser bitcoin .pdf` | `physical_back_mirror` | 0.1764 | 0.0004 | 0.5800 | 1 | 1 | 1 | 0.6341 |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | 0.0644 | 0.0011 | 0.1745 | 1 | 0 | 1 | 0.6175 |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | 0.1431 | 0.0804 | 0.2719 | 3 | 0 | 3 | 0.2923 |
| `keyser bitcoin .pdf` | `front_rotate180` | 0.1150 | 0.0001 | 0.2296 | 2 | 0 | 2 | 0.3122 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | 0.1764 | 0.0004 | 0.5800 | 1 | 1 | 1 | 0.6341 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | 0.0644 | 0.0011 | 0.1745 | 1 | 0 | 1 | 0.6175 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | 0.1431 | 0.0804 | 0.2719 | 3 | 0 | 3 | 0.2923 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | 0.1150 | 0.0001 | 0.2296 | 2 | 0 | 2 | 0.3122 |

## Decision

- Do not promote exact PDF-native held-to-light orientation/polarity variants as selectors.
- The original-resolution `magazine.pdf` physical-back simulation produces no active box above 10% source-only coverage and no active row above the same-size control p95.
- The low-resolution derivative PDFs can still make isolated O4/slot coverage spikes, but no transform produces an all-four O4/B4/G5/O5 rule, and controls remain stronger.
- The simulator is useful for visual review, but it supplies no source-backed unit/order wording and satisfies 0/9 reopen triggers.

## Next Move

- Stop cycling local held-to-light polarity/orientation variants unless a new source changes the physical page geometry. The next useful move is external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.
