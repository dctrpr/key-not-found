# Priority Crops vs bitcoin4

Scope: map the current page-76 priority crop pack into the lower-quality `bitcoin4.pdf` Issue 24 witness. No text extraction, hashing, seed checking, or address checking was run.

- Created: `2026-05-20T09:44:24`
- Sheet: `analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison_sheet.jpg`
- High-res page size: `[2544, 3264]`
- bitcoin4 page size: `[2040, 2805]`
- p76 transform residual source: `analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.json`

## Crop Results

| Crop | bitcoin4 mapped crop | Orange high/bitcoin4 | Dark high/bitcoin4 | Edge high/bitcoin4 | Hash diff | Resize MAD |
|---|---:|---:|---:|---:|---:|---:|
| `L32_O5_primary` | `[682, 2258, 1413, 2400]` | `0.130581` / `0.133051` | `0.079006` / `0.063294` | `0.045397` / `0.035069` | `14` | `39.775` |
| `L27_G5_pair` | `[579, 1975, 1317, 2071]` | `0.0` / `0.0` | `0.157249` / `0.133596` | `0.065663` / `0.071201` | `26` | `55.921` |
| `L25_should_sell` | `[579, 1856, 1210, 1935]` | `0.0` / `0.0` | `0.065333` / `0.032318` | `0.067349` / `0.062465` | `36` | `49.51` |
| `L26_L29_source_band` | `[579, 1923, 1345, 2166]` | `0.0` / `0.0` | `0.109352` / `0.077276` | `0.074847` / `0.077483` | `24` | `52.861` |
| `L25_L32_frame_context` | `[579, 1852, 1397, 2405]` | `0.029872` / `0.030531` | `0.086543` / `0.059327` | `0.063872` / `0.062554` | `25` | `48.031` |

## Decision

- bitcoin4 preserves the same priority regions well enough for rough visual source-fidelity checks, but its lower resolution and page-specific distortion keep it unsuitable as geometry truth or extraction material.
- The mapped crops still show the same visual regions, so bitcoin4 can help catch gross source mismatches.
- The metrics and prior p78 frame test still make bitcoin4 a weak witness for exact geometry.

## Next Move

- Use the crop pack as the future-source baseline, and only revisit bitcoin4 if a new external clue names the lower-quality scan or says to compare source differences directly.
