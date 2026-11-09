# P78 Frame Source-Side Fit Audit

Scope: compare whether current or dx=-38/-40 repaired p78 frames better fit the actual p78 brush/pull-quote graphic. No OCR extraction, key derivation, seed, WIF, or address checks were run.

- Created: `2026-05-20T11:51:11`
- Detected p78 graphic box: `[294, 2398, 1310, 2950]`
- Graphic mask pixels: `233509`
- Sheet: `analysis_outputs/source_audit/p78_frame_source_side_fit/p78_frame_source_side_fit_sheet.jpg`
- Source-side fit favors current detected box: `True`

## Frame Fit

| frame | p78 upright box | mask capture | mask outside | density | offset from detected L/T/R/B |
|---|---|---:|---:|---:|---|
| `current` | `[294, 2398, 1310, 2950]` | `1.0` | `0` | `0.416362` | `0/0/0/0` |
| `g5_edge_touch_dx_-38` | `[332, 2398, 1348, 2950]` | `0.991782` | `1919` | `0.41294` | `38/0/38/0` |
| `nearest_grid_dx_-40` | `[334, 2398, 1350, 2950]` | `0.991161` | `2064` | `0.412682` | `40/0/40/0` |

## Assessment

- The current p78 source frame is the detected graphic bounding box and captures the full detected dark graphic mask.
- The dx=-38/-40 repaired frames shift the p78 source box right by 38-40 px, losing a small amount of left-side source graphic while adding right-side whitespace.
- Therefore dx=-38/-40 is better described as a target-side/source-registration repair that improves the p76 G5/M3/O5 tri-contact, not as a better p78 source-object bounding box.
- This does not weaken the repaired frame as a validation signature; it narrows what the repair means.

## Next Move

- Keep current p78 box for source-object detection and dx=-38/-40 for p76 registration validation; do not treat the repair itself as an extraction instruction.
