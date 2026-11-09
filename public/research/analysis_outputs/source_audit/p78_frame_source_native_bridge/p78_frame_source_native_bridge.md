# P78 Frame Source / Native Bridge

Scope: reconstruct the p78 source frame and bridge current/repaired frame boxes across p78/p76 and upright/native coordinate systems. No OCR extraction, key derivation, seed, WIF, or address checks were run.

- Created: `2026-05-20T11:47:33`
- Image size: `2544x3264`
- Sheet: `analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge_sheet.jpg`

## Coordinate Chain

- p78 upright source box --horizontal flip--> p76 upright reflected box
- upright box --rotate180--> native PDF/source box

## Frame Coordinates

| frame | dx/dy | p78 upright source | p76 upright reflected | p78 native source | p76 native reflected |
|---|---|---|---|---|---|
| `current` | `0.0/0.0` | `[294, 2398, 1310, 2950]` | `[1234, 2398, 2250, 2950]` | `[1234, 314, 2250, 866]` | `[294, 314, 1310, 866]` |
| `g5_edge_touch_dx_-38` | `-38.0/0.0` | `[332, 2398, 1348, 2950]` | `[1196, 2398, 2212, 2950]` | `[1196, 314, 2212, 866]` | `[332, 314, 1348, 866]` |
| `nearest_grid_dx_-40` | `-40.0/0.0` | `[334, 2398, 1350, 2950]` | `[1194, 2398, 2210, 2950]` | `[1194, 314, 2210, 866]` | `[334, 314, 1350, 866]` |

## Assessment

- The active p78 frame benchmark can now be compared in both the source page and target page coordinate systems.
- The current and dx=-38/-40 repaired frames keep the same simple transform chain: horizontal mirror between p78 and p76, then rotate180 for native source images.
- This preserves the repaired frame as a source-registration benchmark but does not provide a word/letter/line extraction unit.

## Next Move

- Use these coordinates when comparing any future physical/original-layout source against the p78-frame-to-p76 lower-corridor benchmark.
