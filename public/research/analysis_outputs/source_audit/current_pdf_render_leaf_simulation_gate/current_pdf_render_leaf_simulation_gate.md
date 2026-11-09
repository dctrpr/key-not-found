# Current PDF Render Leaf Simulation Gate

Scope: measured the physically valid article page 75 -> page 76 held-to-light model using canonical scan pages, PDF-rendered pages, and embedded PDF rasters. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T03:55:05`
- Sheet: `analysis_outputs/source_audit/current_pdf_render_leaf_simulation_gate/current_pdf_render_leaf_simulation_gate_sheet.jpg`
- Pair rows / target rows: `7` / `28`
- Render-vs-embedded PDF rows: `3`
- Max mean source-only coverage: `0.2119`
- Max targets >=10% / >=25% source-only: `2` / `2`
- All-four >=10% / >=25% pair counts: `0` / `0`
- Max render-vs-embedded page MAD: `37.2097`
- Max render-vs-embedded active-box MAD: `26.9905`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pairs=7|targets=28|renderRows=3|maxMean=0.2119|max10=2|max25=2|all10=0|all25=0|maxRenderMAD=37.2097|maxActiveRenderMAD=26.9905|sourceR3=0|triggers=0/9|selectors=0`

## Pair Rows

| pair | mean src-only | min src-only | >=.10 | >=.25 | all4 >=.10 | all4 >=.25 | O4 | B4 | G5 | O5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `canonical_source_images` | 0.0032 | 0.0000 | 0 | 0 | False | False | 0.0037 | 0.0000 | 0.0058 | 0.0032 |
| `magazine.pdf:rendered_300dpi` | 0.0033 | 0.0000 | 0 | 0 | False | False | 0.0042 | 0.0000 | 0.0058 | 0.0031 |
| `magazine.pdf:embedded_primary_image` | 0.0033 | 0.0000 | 0 | 0 | False | False | 0.0042 | 0.0000 | 0.0058 | 0.0032 |
| `keyser bitcoin .pdf:rendered_300dpi` | 0.2119 | 0.0003 | 2 | 2 | False | False | 0.5128 | 0.2693 | 0.0652 | 0.0003 |
| `keyser bitcoin .pdf:embedded_primary_image` | 0.1743 | 0.0003 | 1 | 1 | False | False | 0.5790 | 0.0553 | 0.0628 | 0.0003 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:rendered_300dpi` | 0.2119 | 0.0003 | 2 | 2 | False | False | 0.5128 | 0.2693 | 0.0652 | 0.0003 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:embedded_primary_image` | 0.1743 | 0.0003 | 1 | 1 | False | False | 0.5790 | 0.0553 | 0.0628 | 0.0003 |

## Render vs Embedded Residuals

| PDF | p75 page MAD | p75 active max MAD | p76 page MAD | p76 active max MAD |
|---|---:|---:|---:|---:|
| `magazine.pdf` | 0.0407 | 1.2554 | 0.0348 | 1.6097 |
| `keyser bitcoin .pdf` | 16.2490 | 10.9723 | 37.2097 | 26.9905 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 16.2490 | 10.9723 | 37.2097 | 26.9905 |

## Decision

- `current_pdf_render_leaf_simulation_no_selector`
- Rendering the current PDFs does not create an all-four O4/B4/G5/O5 valid-leaf held-to-light selector.
- The largest source-only coverage appears only in low-resolution derivative render/embedded surfaces and still reaches only O4/B4 above 10%, with zero all-four >=10% or >=25% pairs.
- Render-vs-embedded residuals are ordinary renderer/compression differences; they do not reveal visible original-layout objects or source-backed instruction layers.

## Next Move

- Keep the current PDF render path closed unless a new physical/original-layout source differs from these rows and passes R1-R5 plus source-backed R3. Future work should prioritize new-source validation or raw clue wording, not more renderer toggles.
