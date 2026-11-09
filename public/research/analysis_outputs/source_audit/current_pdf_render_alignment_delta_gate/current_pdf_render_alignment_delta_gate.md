# Current PDF Render Alignment Delta Gate

Scope: compare visible page-76 PDF rasters after OCR-derived alignment against the high-resolution page-76 baseline around O4/B4/G5/O5, orange highlights, and the OVERDOSE header. No OCR-to-key extraction, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.

- Created: `2026-05-21T15:40:18`
- PDFs checked: `3`
- Duplicate image SHA groups: `1`
- Non-baseline PDFs: `2`
- Active target material residuals: `6`
- Active target state mismatches: `0`
- Material residual regions: `12`
- State mismatch / expected-state mismatch regions: `0` / `2`
- Max mean abs diff / max large residual ratio: `97.405` / `0.4594`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_render_alignment_delta_gate/current_pdf_render_alignment_delta_gate_sheet.jpg`
- Fingerprint: `pdfs=3|dupeGroups=1|nonBase=2|activeMaterial=6|activeStateMismatch=0|materialRegions=12|stateMismatch=0|expectedMismatch=2|maxMean=97.405|maxLarge=0.4594|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | image size | alignment | active material | active state mismatch | material regions | state mismatch | max mean diff | max large residual |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `magazine.pdf` | `[2544, 3264]` | `baseline_highres` | `0` | `0` | `0` | `0` | `0.0` | `0.0` |
| `keyser bitcoin .pdf` | `[2040, 2805]` | `ocr_affine` | `3` | `0` | `6` | `0` | `97.405` | `0.4594` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `[2040, 2805]` | `ocr_affine` | `3` | `0` | `6` | `0` | `97.405` | `0.4594` |

## Active Target Detail

### `keyser bitcoin .pdf`

- O4 `buying the dip`: state `Y->Y`, expected `Y`, mean diff `43.941`, large residual `0.1471`, material `False`
- B4 `$1 billion`: state `K->K`, expected `K`, mean diff `97.405`, large residual `0.4594`, material `True`
- G5 `Volcano Bonds`: state `K->K`, expected `K`, mean diff `81.115`, large residual `0.3239`, material `True`
- O5 `shitcoiner at heart`: state `Y->Y`, expected `Y`, mean diff `45.571`, large residual `0.1749`, material `True`

### `analysis_outputs/external_clues/google_drive_article_download.pdf`

- O4 `buying the dip`: state `Y->Y`, expected `Y`, mean diff `43.941`, large residual `0.1471`, material `False`
- B4 `$1 billion`: state `K->K`, expected `K`, mean diff `97.405`, large residual `0.4594`, material `True`
- G5 `Volcano Bonds`: state `K->K`, expected `K`, mean diff `81.115`, large residual `0.3239`, material `True`
- O5 `shitcoiner at heart`: state `Y->Y`, expected `Y`, mean diff `45.571`, large residual `0.1749`, material `True`

## Decision

- Do not reopen the low-resolution PDF render layer as an extraction source.
- The duplicate PDFs share the same visible page image. After OCR-derived alignment, active target states are preserved and no source-side unit/order evidence appears.
- Residuals are expected downsample/render differences, not a new physical or original-layout layer.

## Next Move

- Keep the high-resolution page-76 scan as visual authority. Future useful work remains source-intake/reopen-gate validation unless new physical/original-layout/source evidence arrives.
