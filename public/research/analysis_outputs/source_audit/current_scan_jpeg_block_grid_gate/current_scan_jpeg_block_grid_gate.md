# Current Scan JPEG Block Grid Gate

Scope: inspected page-76 current-scan JPEG 8x8 block-grid phase and block-boundary energy in active target boxes, shifted controls, and projected C9/OVERDOSE slots. This is a visual/source artifact gate, not steganographic extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T06:20:09`
- Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`
- Block size / edge tolerance: `8` / `1.0` px
- Active/control/OVERDOSE strict edge hits: `6` / `18` / `22`
- Active boundary-ratio outliers above shifted-control p95: `0` (``)
- All-four active boundary-ratio outlier: `0`
- Max active/control/OVERDOSE boundary ratio: `1.551` / `4.014` / `1.296`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_jpeg_block_grid_gate/current_scan_jpeg_block_grid_gate_sheet.jpg`
- Fingerprint: `active=4|controls=16|slots=8|edgeHits=6/18/22|activeOutliers=0|allFourOutliers=0|ratioMax=1.551/4.014/1.296|controlP95=3.361|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | ratio | boundary delta | edge hits | center hits | phase L/T/R/B |
|---|---|---:|---:|---:|---:|---|
| `shifted_control` | `O5_dy+146` | 4.014 | 0.050 | 2 | 1 | `0.0/6.0/5.0/0.0` |
| `shifted_control` | `O4_dy-292` | 3.143 | 0.077 | 1 | 1 | `6.0/5.0/1.0/5.0` |
| `shifted_control` | `O5_dy+292` | 2.833 | 0.107 | 3 | 0 | `0.0/0.0/5.0/0.0` |
| `active` | `B4` | 1.551 | 11.102 | 0 | 1 | `4.0/6.0/3.0/5.0` |
| `active` | `O4` | 1.307 | 4.378 | 3 | 2 | `6.0/1.0/1.0/1.0` |
| `overdose_slot` | `slot7_E` | 1.296 | 0.114 | 2 | 2 | `5.6/0.8/2.0/7.7` |
| `shifted_control` | `O4_dy-146` | 1.276 | 1.299 | 3 | 2 | `6.0/7.0/1.0/7.0` |
| `shifted_control` | `O5_dy-292` | 1.205 | 1.341 | 2 | 1 | `0.0/0.0/5.0/2.0` |
| `shifted_control` | `B4_dy-146` | 1.199 | 3.304 | 0 | 1 | `4.0/4.0/3.0/3.0` |
| `overdose_slot` | `slot3_R` | 1.148 | 1.608 | 3 | 1 | `3.6/0.8/8.0/7.7` |
| `overdose_slot` | `slot1_V` | 1.124 | 1.359 | 3 | 1 | `2.6/0.8/7.0/7.7` |
| `overdose_slot` | `slot4_D` | 1.117 | 1.165 | 3 | 1 | `8.0/0.8/4.6/7.7` |
| `overdose_slot` | `slot5_O` | 1.104 | 0.465 | 3 | 1 | `4.6/0.8/1.0/7.7` |
| `active` | `O5` | 1.103 | 1.458 | 1 | 0 | `0.0/4.0/5.0/6.0` |
| `shifted_control` | `G5_dy+146` | 1.089 | 1.675 | 0 | 0 | `3.0/2.0/4.0/2.0` |
| `overdose_slot` | `slot2_E` | 1.068 | 0.717 | 3 | 1 | `7.0/0.8/3.6/7.7` |
| `shifted_control` | `G5_dy-146` | 1.058 | 0.856 | 0 | 0 | `3.0/6.0/4.0/6.0` |
| `shifted_control` | `O5_dy-146` | 1.048 | 0.330 | 1 | 0 | `0.0/2.0/5.0/4.0` |
| `shifted_control` | `B4_dy+146` | 1.029 | 0.546 | 2 | 2 | `4.0/0.0/3.0/7.0` |
| `overdose_slot` | `slot6_S` | 1.017 | 0.009 | 3 | 1 | `1.0/0.8/5.6/7.7` |
| `shifted_control` | `O4_dy+146` | 1.005 | 0.048 | 1 | 1 | `6.0/3.0/1.0/3.0` |
| `shifted_control` | `G5_dy+292` | 1.001 | 0.010 | 0 | 0 | `3.0/4.0/4.0/4.0` |
| `shifted_control` | `G5_dy-292` | 0.989 | -0.191 | 0 | 0 | `3.0/4.0/4.0/4.0` |
| `overdose_slot` | `slot0_O` | 0.978 | -0.114 | 2 | 2 | `6.0/0.8/2.6/7.7` |
| `active` | `G5` | 0.971 | -0.652 | 2 | 1 | `3.0/0.0/4.0/0.0` |
| `shifted_control` | `O4_dy+292` | 0.870 | -0.538 | 1 | 1 | `6.0/5.0/1.0/5.0` |
| `shifted_control` | `B4_dy-292` | 0.865 | -2.528 | 1 | 1 | `4.0/2.0/3.0/1.0` |
| `shifted_control` | `B4_dy+292` | 0.846 | -3.124 | 1 | 1 | `4.0/2.0/3.0/1.0` |

## Decision

- `current_scan_jpeg_block_grid_no_selector`
- Active boxes and projected OVERDOSE slots do not produce a unique 8x8 JPEG block phase or boundary-energy signature against shifted controls.
- Edge/block coincidences are ordinary compression geometry and do not supply source-backed R3 unit/order/transform evidence.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
