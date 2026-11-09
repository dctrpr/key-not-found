# Current Scan Page-76 Image Witness Micro-Registration Gate

Scope: bounded exact page-76 image witness local-shift control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.

- Created: `2026-05-24T13:24:10`
- Exact page-76 witnesses checked: `3`
- Active target shift rows: `12`
- Search radius: `+/-8 px`
- Nonzero best shifts: `0`
- Max absolute best shift: `0` px
- Max zero-shift diff: `6.455416`
- Max zero-to-best improvement: `0.0`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `witnesses=3|targets=12|radius=8|nonZeroShift=0|maxAbsShift=0|maxZeroDiff=6.455|maxImprove=0.000|sourceR3=0|triggers=0/9|selectors=0`

## Shift Rows

| witness | target | zero diff | best diff | best dx | best dy | improvement | zero shift best |
|---|---|---|---|---|---|---|---|
| `analysis_outputs/3d_article_map/page_76_upright.jpg` | `O4` | `0.0` | `0.0` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/3d_article_map/page_76_upright.jpg` | `B4` | `0.0` | `0.0` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/3d_article_map/page_76_upright.jpg` | `G5` | `0.0` | `0.0` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/3d_article_map/page_76_upright.jpg` | `O5` | `0.0` | `0.0` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/source_images/magazine_page_76.jpg` | `O4` | `2.896443` | `2.896443` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/source_images/magazine_page_76.jpg` | `B4` | `1.060594` | `1.060594` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/source_images/magazine_page_76.jpg` | `G5` | `1.109483` | `1.109483` | `0` | `0` | `0.0` | `True` |
| `analysis_outputs/source_images/magazine_page_76.jpg` | `O5` | `2.979356` | `2.979356` | `0` | `0` | `0.0` | `True` |
| `magazine-4_1.jpg` | `O4` | `6.176005` | `6.176005` | `0` | `0` | `0.0` | `True` |
| `magazine-4_1.jpg` | `B4` | `1.546477` | `1.546477` | `0` | `0` | `0.0` | `True` |
| `magazine-4_1.jpg` | `G5` | `1.623788` | `1.623788` | `0` | `0` | `0.0` | `True` |
| `magazine-4_1.jpg` | `O5` | `6.455416` | `6.455416` | `0` | `0` | `0.0` | `True` |

## Decision

- exact_page76_image_witnesses_have_no_active_microregistration_drift.
- Reason: Across all exact page-76 image witnesses and all four active boxes, the best +/-8 px local match is the zero-shift crop. The small remaining differences are raster/JPEG differences, not geometry shifts or a hidden layer.
- Next move: Keep exact page-76 witnesses as aligned duplicate rasters. Reopen active-box geometry only for a distinct physical/original-layout source or raw clue wording.

Sheet: `analysis_outputs/source_audit/current_scan_page76_image_witness_microregistration_gate/current_scan_page76_image_witness_microregistration_gate_sheet.jpg`
