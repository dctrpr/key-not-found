# Current Scan Highlight Edge-Halo Gate

Scope: inspected orange/black edge-halo behavior around current page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots. This is a scan/source-quality gate, not extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T10:11:51`
- Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`
- Outer pads checked: `[4, 8, 16, 32]`
- Inner strips checked: `[4, 8, 16]`
- Outlier abs-z threshold against shifted controls: `3.0`
- Active edge-halo outlier rows: `3` (`O4,B4,O5`)
- All-four active edge-halo outlier: `0`
- Active common color-sensitive halo signature: `mixed`
- Active common ink edge-bias signature: `mixed`
- Matching controls / OVERDOSE slots for common halo signature: `0` / `0`
- Matching controls / OVERDOSE slots for common edge-bias signature: `0` / `0`
- Shared active halo carrier / hidden halo candidate: `0` / `0`
- Max active/control/OVERDOSE halo abs-z: `19.49` / `3.72` / `11.78`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_highlight_edge_halo_gate/current_scan_highlight_edge_halo_gate_sheet.jpg`
- Fingerprint: `active=4|controls=16|slots=8|outerPads=4,8,16,32|innerStrips=4,8,16|activeHaloOutliers=3|allFourHalo=0|sharedCarrier=0|hiddenCandidate=0|commonHalo=mixed|commonEdge=mixed|controlHaloCommon=0|slotHaloCommon=0|controlEdgeCommon=0|slotEdgeCommon=0|maxHaloZ=19.49/3.72/11.78|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | halo signature | edge-bias signature | outlier | max z | strongest feature | value |
|---|---|---|---|---:|---:|---|---:|
| `active` | `B4` | `p8=KB2s4|p16=KB1s2` | `p8=IB4s4|p16=IB2s2` | 1 | 19.49 | `outer_p4_black_bottomRatio` | `0.399` |
| `active` | `O4` | `p8=OR2s3|p16=OR1s2` | `p8=IR4s3|p16=IR2s2` | 1 | 14.03 | `outer_p4_ink_bottomRatio` | `0.289` |
| `overdose_slot` | `slot6_S` | `p8=KB0s4|p16=KB1s4` | `p8=IB4s4|p16=IB4s4` | 1 | 11.78 | `outer_p16_blackTopMinusBottom` | `-0.183` |
| `active` | `O5` | `p8=OL1s4|p16=OL0s2` | `p8=IL4s3|p16=IL2s2` | 1 | 5.27 | `outer_p4_ink_bottomRatio` | `0.113` |
| `shifted_control` | `O5_dy-292` | `p8=KT2s4|p16=KT3s3` | `p8=IT4s4|p16=IT3s3` | 1 | 3.72 | `outer_p16_inkTopMinusBottom` | `0.065` |
| `shifted_control` | `O5_dy-146` | `p8=KT2s3|p16=KT3s3` | `p8=IT3s3|p16=IT3s3` | 1 | 3.30 | `outer_p32_blackTopMinusBottom` | `-0.103` |
| `shifted_control` | `G5_dy-292` | `p8=KL1s9|p16=KR1s6` | `p8=IL9s9|p16=IR6s6` | 0 | 2.70 | `outer_p8_ink_leftRatio` | `0.469` |
| `overdose_slot` | `slot4_D` | `p8=KL1s2|p16=KL1s2` | `p8=IR3s3|p16=IR3s3` | 0 | 2.60 | `outer_p8_inkRatio` | `0.104` |
| `overdose_slot` | `slot5_O` | `p8=OL1s2|p16=OL1s2` | `p8=IL4s4|p16=IL4s4` | 0 | 2.59 | `outer_p8_inkRatio` | `0.104` |
| `shifted_control` | `B4_dy+292` | `p8=KR0s5|p16=KR0s3` | `p8=IR5s5|p16=IR3s3` | 0 | 2.24 | `outer_p4_black_rightRatio` | `0.404` |
| `shifted_control` | `O4_dy-146` | `p8=KL0s6|p16=KL0s4` | `p8=IL6s6|p16=IL4s4` | 0 | 2.16 | `outer_p32_blackRightMinusLeft` | `-0.249` |
| `overdose_slot` | `slot3_R` | `p8=KL1s2|p16=KL1s2` | `p8=IR3s3|p16=IR2s2` | 0 | 1.97 | `outer_p8_inkRatio` | `0.084` |
| `shifted_control` | `B4_dy-146` | `p8=KR0s2|p16=KR0s4` | `p8=IR2s2|p16=IR4s4` | 0 | 1.93 | `outer_p32_blackRightMinusLeft` | `0.230` |
| `overdose_slot` | `slot2_E` | `p8=KR2s3|p16=KR2s2` | `p8=IR3s3|p16=IR3s3` | 0 | 1.81 | `outer_p8_inkRatio` | `0.079` |
| `overdose_slot` | `slot1_V` | `p8=KL2s3|p16=KL2s2` | `p8=IL3s3|p16=IL2s2` | 0 | 1.80 | `outer_p8_blackRatio` | `0.079` |
| `shifted_control` | `O4_dy-292` | `p8=OT0s0|p16=OT0s0` | `p8=IT0s0|p16=IT0s0` | 0 | 1.72 | `outer_p32_inkEdgeSpread` | `0.000` |
| `shifted_control` | `O5_dy+146` | `p8=OT0s0|p16=OT0s0` | `p8=IT0s0|p16=IT0s0` | 0 | 1.72 | `outer_p32_inkEdgeSpread` | `0.000` |
| `shifted_control` | `O5_dy+292` | `p8=OT0s0|p16=OT0s0` | `p8=IT0s0|p16=IT0s0` | 0 | 1.72 | `outer_p32_inkEdgeSpread` | `0.000` |
| `shifted_control` | `O4_dy+292` | `p8=KL0s5|p16=KL0s3` | `p8=IL5s5|p16=IL3s3` | 0 | 1.70 | `outer_p4_inkRightMinusLeft` | `-0.354` |
| `active` | `G5` | `p8=OT0s0|p16=KR0s0` | `p8=IT0s0|p16=IR0s0` | 0 | 1.59 | `outer_p16_blackDominantEdgeRatio` | `0.004` |
| `shifted_control` | `G5_dy+292` | `p8=KR0s5|p16=KR0s4` | `p8=IR5s5|p16=IR4s4` | 0 | 1.57 | `outer_p8_inkRightMinusLeft` | `0.221` |
| `shifted_control` | `G5_dy-146` | `p8=KR0s4|p16=KR0s5` | `p8=IR4s4|p16=IR5s5` | 0 | 1.43 | `outer_p16_ink_rightRatio` | `0.236` |
| `shifted_control` | `O4_dy+146` | `p8=KL0s4|p16=KL0s2` | `p8=IL4s4|p16=IL2s2` | 0 | 1.25 | `outer_p8_blackRightMinusLeft` | `-0.208` |
| `shifted_control` | `G5_dy+146` | `p8=KL0s3|p16=KL0s2` | `p8=IL3s3|p16=IL2s2` | 0 | 1.23 | `outer_p4_inkRightMinusLeft` | `-0.260` |
| `shifted_control` | `B4_dy-292` | `p8=KR0s1|p16=KR0s3` | `p8=IR1s1|p16=IR3s3` | 0 | 1.18 | `outer_p32_inkRightMinusLeft` | `0.142` |
| `shifted_control` | `B4_dy+146` | `p8=KR0s2|p16=KR0s2` | `p8=IR2s2|p16=IR2s2` | 0 | 1.11 | `outer_p32_inkRightMinusLeft` | `0.134` |
| `overdose_slot` | `slot7_E` | `p8=KR0s1|p16=KR0s1` | `p8=IR1s1|p16=IR1s1` | 0 | 1.09 | `outer_p4_inkEdgeSpread` | `0.055` |
| `overdose_slot` | `slot0_O` | `p8=KR1s2|p16=KR1s2` | `p8=IR2s2|p16=IR2s2` | 0 | 0.92 | `outer_p32_blackRightMinusLeft` | `0.111` |

## Decision

- `current_scan_highlight_edge_halo_no_selector`
- The active boxes show expected visible orange/black highlight-edge behavior, but there is no shared all-four halo carrier.
- Color-sensitive halo signatures and ink edge-bias signatures are mixed or control-matched, and no source-backed unit/order/transform clue is present.

## Next Move

- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.
