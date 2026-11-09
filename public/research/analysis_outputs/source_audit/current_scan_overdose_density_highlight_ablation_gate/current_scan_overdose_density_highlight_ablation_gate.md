# Current Scan OVERDOSE Density Highlight Ablation Gate

Scope: removes mirrored page-75 source-highlight rectangles from the natural 75->76 held-to-light source mask, then checks whether the density-calibrated OVERDOSE slot outliers survive. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T12:38:15`
- Slot columns checked: `8`
- Baseline outlier slots / letters: `slot_3_R, slot_5_O, slot_6_S` / `ROS`
- Ablated mirrored source highlight ids: `p75_orange_6, p75_orange_7, p75_orange_8`
- Outlier survivors after outlier-highlight ablation: `2` / `3`
- Surviving letters after outlier-highlight ablation: `OS`
- Outlier survivors after all-highlight ablation: `2` / `3`
- Mean outlier drop after outlier-highlight ablation: `30.373%`
- Non-outlier highlight-control status flips: `0`
- Hidden highlight-ablation candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_overdose_density_highlight_ablation_gate/current_scan_overdose_density_highlight_ablation_gate_sheet.jpg`
- Fingerprint: `slots=8|baselineOutliers=3|letters=ROS|outlierHighlightIds=p75_orange_6,p75_orange_7,p75_orange_8|surviveOutlierAblation=2|surviveLetters=OS|surviveAllAblation=2|meanDropPct=30.4|nonOutlierControlFlips=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Slot Ablation Trace

| slot | letter | baseline | other max | outlier | after outlier-highlight ablation | drop | survives | after all-highlight ablation | non-outlier highlight control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `slot_0_O` | `O` | 0.000359 | 1.021533 | 0 | 0.000359 | 0.000% | 0 | 0.000359 | 0.000359 |
| `slot_1_V` | `V` | 0.038906 | 1.004983 | 0 | 0.038906 | 0.000% | 0 | 0.038906 | 0.038906 |
| `slot_2_E` | `E` | 0.990051 | 0.993657 | 0 | 0.763975 | 22.835% | 0 | 0.763975 | 0.990051 |
| `slot_3_R` | `R` | 1.616861 | 1.443580 | 1 | 1.014488 | 37.256% | 0 | 1.014488 | 1.616861 |
| `slot_4_D` | `D` | 1.587506 | 1.672578 | 0 | 1.585097 | 0.152% | 0 | 1.585097 | 1.587506 |
| `slot_5_O` | `O` | 2.124800 | 1.025745 | 1 | 1.773875 | 16.516% | 1 | 1.773875 | 2.124800 |
| `slot_6_S` | `S` | 2.868161 | 1.016470 | 1 | 1.796976 | 37.347% | 1 | 1.796976 | 2.868161 |
| `slot_7_E` | `E` | 0.904049 | 1.058731 | 0 | 0.691970 | 23.459% | 0 | 0.691970 | 0.904049 |

## Decision

- `current_scan_overdose_density_highlight_ablation_no_selector`
- The slot-density signal depends on mirrored page-75 highlight regions and still supplies no source-backed unit/order rule.
- Do not tune `ROS`/`SOR` slot density unless a new clue specifically names source-highlight bleed-through, slots, density, or a reading order.

## Next Move

- Continue with physical/original-layout source validation or raw clue wording that names unit/order/transform.
- If staying local-only, move away from OVERDOSE density and inspect a different mechanism such as original-layout source acquisition or a constrained folded-geometry witness.
