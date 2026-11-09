# P78 Repair Lost Source Pixels Audit

Scope: localize the p78 graphic pixels lost when the current p78 source box is shifted to the dx `-38/-40` repaired boxes. No OCR extraction, key derivation, seed, WIF, or address checks were run.

- Created: `2026-05-20T11:54:46`
- Current source box: `[294, 2398, 1310, 2950]`
- Detected graphic box: `[294, 2398, 1310, 2950]`
- Graphic mask pixels: `233509`
- Sheet: `analysis_outputs/source_audit/p78_repair_lost_source_pixels/p78_repair_lost_source_pixels_sheet.jpg`

## Repair Losses

| repair | lost pixels | lost share | lost bbox | lost centroid | gained source pixels | top component loss |
|---|---:|---:|---|---|---:|---|
| `g5_edge_touch_dx_-38` | `1919` | `0.008218` | `[294, 2534, 332, 2630]` | `[317.86, 2586.52]` | `0` | component 4 1919px (1.0) |
| `nearest_grid_dx_-40` | `2064` | `0.008839` | `[294, 2534, 334, 2630]` | `[318.88, 2585.95]` | `0` | component 4 2064px (1.0) |

## Assessment

- The repair loss is a narrow left-edge strip of the p78 graphic, not a centered cut through the pull-quote text.
- The repaired frame gains right-side area, but that gained area contains no detected source-mask pixels.
- This supports treating dx=-38/-40 as a p76 registration alignment rather than a source-object crop instruction.

## Next Move

- Keep p78 current box as the source object and dx=-38/-40 as the p76 registration repair; do not use the lost strip as extraction material unless a future source clue names left-edge trim/crop.
