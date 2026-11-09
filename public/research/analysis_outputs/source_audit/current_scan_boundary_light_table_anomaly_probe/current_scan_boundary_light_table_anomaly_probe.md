# Current-Scan Boundary Light-Table Anomaly Probe

Created: `2026-05-21T15:09:42`

## Scope

Current-scan held-to-light boundary anomaly probe for page-76 O4/B4/G5/O5. Uses PDF-extracted page images, current light-table transforms, target outer edge strips, and crop-window edge strips only; no key derivation, hashing, WIF, seed, address, BIP39, OCR-to-key extraction, or broad candidate generation.

## Summary

- Scenarios / boundary rows / groups: `3` / `96` / `24`.
- All-four boundary groups at >=10% / >=25% / >=50% source coverage: `2` / `0` / `0`.
- Physically natural all-four >=10% groups: `0`.
- Forced/non-physical all-four >=10% groups: `2`.
- Weak all-four >=10% groups: `valid_75_to_76_forced_best:target_outer_edge:right, benchmark_79_to_76_best:target_outer_edge:top`.
- Best mean boundary group: `valid_75_to_76_forced_best:target_outer_edge:right` at `0.3757` with coverage `0.6912,0.1487,0.5278,0.1352`.
- Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
- Fingerprint: `scenarios=3|rows=96|groups=24|all10=2|all25=0|all50=0|naturalAll10=0|weak=valid_75_to_76_forced_best:target_outer_edge:right;benchmark_79_to_76_best:target_outer_edge:top|best=valid_75_to_76_forced_best:target_outer_edge:right:0.3757|sourceR3=0|triggers=0/9|selectors=0`.

## Group Rows

| scenario | class | kind | side | coverage O4,B4,G5,O5 | all10 | all25 | all50 |
|---|---|---|---|---:|---:|---:|---:|
| `valid_75_to_76_natural` | `physical_natural` | `target_outer_edge` | `left` | `0.1082,0.0000,0.0000,0.1281` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `target_outer_edge` | `right` | `0.1140,0.0000,0.1623,0.1694` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `target_outer_edge` | `top` | `0.1414,0.0000,0.0000,0.0070` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `target_outer_edge` | `bottom` | `0.1022,0.0000,0.0525,0.0000` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `crop_window_edge` | `left` | `0.2360,0.0000,0.0000,0.0478` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `crop_window_edge` | `right` | `0.1444,0.0334,0.1421,0.0777` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `crop_window_edge` | `top` | `0.2636,0.0352,0.0000,0.1012` | `False` | `False` | `False` |
| `valid_75_to_76_natural` | `physical_natural` | `crop_window_edge` | `bottom` | `0.0361,0.0000,0.0056,0.0000` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `target_outer_edge` | `left` | `0.7038,0.0000,0.0000,0.1781` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `target_outer_edge` | `right` | `0.6912,0.1487,0.5278,0.1352` | `True` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `target_outer_edge` | `top` | `0.1126,0.0000,0.0000,0.2631` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `target_outer_edge` | `bottom` | `0.0199,0.0000,0.0000,0.2300` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `crop_window_edge` | `left` | `0.3766,0.0000,0.0451,0.1194` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `crop_window_edge` | `right` | `0.0000,0.2538,0.2088,0.1968` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `crop_window_edge` | `top` | `0.3256,0.1389,0.5082,0.0038` | `False` | `False` | `False` |
| `valid_75_to_76_forced_best` | `physical_forced_shift` | `crop_window_edge` | `bottom` | `0.1345,0.0000,0.1240,0.1795` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `target_outer_edge` | `left` | `0.6907,0.0053,0.1922,0.0000` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `target_outer_edge` | `right` | `0.6959,0.1151,0.1796,0.0000` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `target_outer_edge` | `top` | `0.3559,0.2157,0.2496,0.2063` | `True` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `target_outer_edge` | `bottom` | `0.2474,0.2932,0.0000,0.2676` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `crop_window_edge` | `left` | `0.3925,0.0000,0.0987,0.0000` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `crop_window_edge` | `right` | `0.0000,0.1738,0.0443,0.0000` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `crop_window_edge` | `top` | `0.0002,0.0127,0.0000,0.0055` | `False` | `False` | `False` |
| `benchmark_79_to_76_best` | `nonphysical_benchmark` | `crop_window_edge` | `bottom` | `0.2522,0.2150,0.0003,0.1035` | `False` | `False` | `False` |

## Decision

- `weak_forced_or_nonphysical_boundary_contacts_no_selector`.
- Held-to-light source ink does not produce a strong, physically natural all-four boundary selector. The only all-four boundary contacts appear at a weak 10% threshold in forced/non-physical views, and no group survives the 25% or 50% thresholds.
- Next move: Use the boundary sheet as visual documentation only. Stop escalating current-scan boundary mechanics unless a new source names a side/edge rule or a distinct original-layout asset changes the physical registration.

## Artifacts

- Sheet: `analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe/current_scan_boundary_light_table_anomaly_probe_sheet.jpg`
