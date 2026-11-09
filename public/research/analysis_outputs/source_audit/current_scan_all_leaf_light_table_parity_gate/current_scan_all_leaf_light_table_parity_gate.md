# Current Scan All-Leaf Light-Table Parity Gate

Scope: compared natural held-to-light overlays for valid current-scan leaf pairs `75->76`, `77->78`, and `79->80`. Each odd source page was normalized to readable/upright coordinates, horizontally mirrored, and overlaid on its even target page with no translation search. The same O4/B4/G5/O5 boxes, matched line-shift controls, and C9/OVERDOSE slot columns were measured. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T12:14:26`
- Valid leaf pairs: `3`
- Active same-coordinate rows / line-shift controls / OVERDOSE slot rows: `12` / `72` / `24`
- Page-76 active ink / feature outliers: `0` / `0`
- All-four page-76 active ink / feature outlier: `0` / `0`
- Page-76 OVERDOSE slot ink / feature outliers: `0` / `0`
- Hidden all-leaf light-table candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/current_scan_all_leaf_light_table_parity_gate_sheet.jpg`
- Fingerprint: `pairs=3|activeRows=12|slots=24|controls=72|p76ActiveInkOutliers=0|p76ActiveFeatureOutliers=0|all4Ink=0|all4Feature=0|slotInkOutliers=0|slotFeatureOutliers=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Active Same-Coordinate Rows

| pair | target page | target | source ink | source feature | dark | orange | grey |
|---|---:|---|---:|---:|---:|---:|---:|
| `valid_75_to_76` | 76 | `O4` | 0.140212 | 0.122323 | 0.105237 | 0.000000 | 0.122323 |
| `valid_75_to_76` | 76 | `B4` | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| `valid_75_to_76` | 76 | `G5` | 0.059643 | 0.052629 | 0.043277 | 0.000000 | 0.052629 |
| `valid_75_to_76` | 76 | `O5` | 0.194042 | 0.165411 | 0.142899 | 0.000000 | 0.165411 |
| `valid_77_to_78` | 78 | `O4` | 0.982780 | 0.951374 | 0.925054 | 0.000000 | 0.951374 |
| `valid_77_to_78` | 78 | `B4` | 0.974274 | 0.921932 | 0.895478 | 0.000000 | 0.921689 |
| `valid_77_to_78` | 78 | `G5` | 0.974283 | 0.919420 | 0.886118 | 0.000000 | 0.919057 |
| `valid_77_to_78` | 78 | `O5` | 0.975556 | 0.928084 | 0.885056 | 0.000000 | 0.928052 |
| `valid_79_to_80` | 80 | `O4` | 0.010082 | 0.009145 | 0.008075 | 0.000000 | 0.009145 |
| `valid_79_to_80` | 80 | `B4` | 0.079201 | 0.071353 | 0.066580 | 0.000000 | 0.071353 |
| `valid_79_to_80` | 80 | `G5` | 0.000675 | 0.000156 | 0.000104 | 0.000000 | 0.000156 |
| `valid_79_to_80` | 80 | `O5` | 0.220902 | 0.210918 | 0.199324 | 0.000000 | 0.210918 |

## Page-76 Active Parity Comparison

| target | p76 ink | other-leaf ink max | line-control ink p95 | ink outlier | p76 feature | other-leaf feature max | line-control feature p95 | feature outlier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `O4` | 0.140212 | 0.982780 | 0.987828 | 0 | 0.122323 | 0.951374 | 0.972470 | 0 |
| `B4` | 0.000000 | 0.974274 | 0.983282 | 0 | 0.000000 | 0.921932 | 0.947533 | 0 |
| `G5` | 0.059643 | 0.974283 | 0.977860 | 0 | 0.052629 | 0.919420 | 0.940947 | 0 |
| `O5` | 0.194042 | 0.975556 | 1.000000 | 0 | 0.165411 | 0.928084 | 1.000000 | 0 |

## OVERDOSE Slot Parity

| slot | letter | p76 ink | other-leaf ink max | ink outlier | p76 feature | other-leaf feature max | feature outlier |
|---|---|---:|---:|---:|---:|---:|---:|
| `0` | `O` | 0.000034 | 0.982040 | 0 | 0.000000 | 0.951483 | 0 |
| `1` | `V` | 0.003658 | 0.966129 | 0 | 0.003169 | 0.927594 | 0 |
| `2` | `E` | 0.093087 | 0.955242 | 0 | 0.083170 | 0.914633 | 0 |
| `3` | `R` | 0.152022 | 0.954608 | 0 | 0.139107 | 0.914452 | 0 |
| `4` | `D` | 0.149261 | 0.977438 | 0 | 0.133484 | 0.943031 | 0 |
| `5` | `O` | 0.199779 | 0.986089 | 0 | 0.182152 | 0.961920 | 0 |
| `6` | `S` | 0.269672 | 0.977173 | 0 | 0.250883 | 0.939942 | 0 |
| `7` | `E` | 0.085001 | 0.947007 | 0 | 0.078464 | 0.878472 | 0 |

## Decision

- `current_scan_all_leaf_light_table_parity_no_selector`
- Natural all-leaf held-to-light parity does not make O4/B4/G5/O5 an all-four page-76 outlier.
- The current scan remains useful as a source-review witness, but it still does not provide a source-backed unit/order rule.

## Next Move

- Continue only with physical/original-layout source validation or raw clue wording that names a unit, order, or transform.
- Do not run more current-scan held-to-light extraction variants without new source evidence.
