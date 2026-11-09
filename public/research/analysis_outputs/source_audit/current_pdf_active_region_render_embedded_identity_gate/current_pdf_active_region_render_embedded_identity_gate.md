# Current PDF Active-Region Render/Embedded Identity Gate

Scope: compared page-76 visible PDF renders with reconstructed embedded page-image canvases at O4/B4/G5/O5, C9 OVERDOSE slots, and nearby shifted controls. This checks for render-only or layout-only active pixels. No OCR-to-key extraction, seed/WIF/address checks, hashes, or broad brute force were run.

- Created: `2026-05-24T09:20:47`
- PDFs checked: `3`
- Region rows: `60`
- Active render-vs-embedded mismatches: `0`
- All-four active mismatch PDF count: `0`
- OVERDOSE-slot render-vs-embedded mismatches: `0`
- Control render-vs-embedded mismatches: `0`
- Max active render-vs-embedded mean abs diff: `7.198912`
- Max OVERDOSE-slot render-vs-embedded mean abs diff: `3.121697`
- Active/control p95 render-vs-embedded mean abs diff: `6.708294` / `5.030696`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_active_region_render_embedded_identity_gate/current_pdf_active_region_render_embedded_identity_gate_sheet.jpg`
- Fingerprint: `pdfs=3|regions=60|activeMismatch=0|all4Pdf=0|slotMismatch=0|controlMismatch=0|maxActive=7.199|maxSlot=3.122|activeP95=6.708|controlP95=5.031|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | render orientation | embedded orientation | active mismatches | slot mismatches | control mismatches | max active MAD | max slot MAD |
|---|---|---|---:|---:|---:|---:|---:|
| `magazine.pdf` | `as_is` | `rotate180` | `0` | `0` | `0` | `7.198912` | `3.121697` |
| `keyser bitcoin .pdf` | `as_is` | `as_is` | `0` | `0` | `0` | `2.423490` | `1.707806` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `as_is` | `as_is` | `0` | `0` | `0` | `2.423490` | `1.707806` |

## Active Targets

| PDF | target | render-vs-embedded MAD | large-diff ratio | render-vs-baseline MAD | embedded-vs-baseline MAD | mismatch |
|---|---|---:|---:|---:|---:|---|
| `magazine.pdf` | `O4` | `4.583794` | `0.000178` | `8.018722` | `6.176005` | `False` |
| `magazine.pdf` | `B4` | `6.306879` | `0.006094` | `6.606423` | `1.546477` | `False` |
| `magazine.pdf` | `G5` | `7.198912` | `0.006252` | `7.514131` | `1.623788` | `False` |
| `magazine.pdf` | `O5` | `4.314589` | `0.000161` | `7.923156` | `6.455416` | `False` |
| `keyser bitcoin .pdf` | `O4` | `1.080047` | `0.000000` | `113.415209` | `113.858895` | `False` |
| `keyser bitcoin .pdf` | `B4` | `2.248497` | `0.000000` | `146.850983` | `147.376803` | `False` |
| `keyser bitcoin .pdf` | `G5` | `2.423490` | `0.000000` | `150.954021` | `151.487167` | `False` |
| `keyser bitcoin .pdf` | `O5` | `0.816586` | `0.000000` | `121.459624` | `121.871873` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O4` | `1.080047` | `0.000000` | `113.415209` | `113.858895` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `B4` | `2.248497` | `0.000000` | `146.850983` | `147.376803` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `G5` | `2.423490` | `0.000000` | `150.954021` | `151.487167` | `False` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O5` | `0.816586` | `0.000000` | `121.459624` | `121.871873` | `False` |

## Decision

- `current_pdf_render_embedded_identity_no_selector`
- The visible PDF render does not expose a hidden active-box or OVERDOSE layer outside the embedded raster page image.
- Do not reopen extraction from current-PDF render differences; the current PDFs remain raster witnesses plus invisible OCR wrappers.

## Next Move

- Best direction remains original-layout/physical source acquisition or raw clue wording scored against R1-R5 and the source-acquisition packet.
