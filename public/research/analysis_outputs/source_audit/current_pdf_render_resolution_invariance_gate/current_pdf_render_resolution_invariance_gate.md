# Current PDF Render Resolution Invariance Gate

Scope: rendered page 76 of the current PDFs at zoom levels 1, 2, and 4, normalized each render to the readable/upright 2544x3264 frame, and compared low-vs-high render deltas in active target boxes, shifted controls, and projected C9/OVERDOSE slots. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T06:11:06`
- PDFs / zooms / render rows: `3` / `3` / `9`
- Comparison rows: `6`
- Active outliers above shifted-control p95: `4`
- All-four active outlier comparisons: `0`
- Max active/control/OVERDOSE-slot mean abs delta: `33.652` / `31.542` / `17.371`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_render_resolution_invariance_gate/current_pdf_render_resolution_invariance_gate_sheet.jpg`
- Fingerprint: `pdfs=3|zooms=3|renders=9|comparisons=6|activeOutliers=4|allFourOutliers=0|maxActive=33.652|maxControl=31.542|maxSlot=17.371|sourceR3=0|triggers=0/9|selectors=0`

## Comparison Rows

| PDF | comparison | active max | active mean | control p95 | control max | active outliers | OVERDOSE slot max |
|---|---|---:|---:|---:|---:|---|---:|
| `magazine.pdf` | `z1_vs_z4` | 33.652 | 25.833 | 30.428 | 31.542 | `B4,G5` | 17.371 |
| `magazine.pdf` | `z2_vs_z4` | 15.406 | 12.159 | 12.023 | 12.497 | `B4,G5` | 7.349 |
| `keyser bitcoin .pdf` | `z1_vs_z4` | 11.554 | 6.670 | 12.118 | 12.211 | `` | 6.826 |
| `keyser bitcoin .pdf` | `z2_vs_z4` | 3.223 | 2.071 | 3.434 | 3.603 | `` | 2.176 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `z1_vs_z4` | 11.554 | 6.670 | 12.118 | 12.211 | `` | 6.826 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `z2_vs_z4` | 3.223 | 2.071 | 3.434 | 3.603 | `` | 2.176 |

## Decision

- `render_resolution_invariance_no_selector`
- Higher-DPI page-76 rendering does not expose a separate active-box or projected OVERDOSE source carrier.
- Active-region render deltas are ordinary raster resampling effects and do not produce an all-four active selector against shifted controls.
- Current PDFs remain current-scan/duplicate render witnesses, not distinct original-layout evidence.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
