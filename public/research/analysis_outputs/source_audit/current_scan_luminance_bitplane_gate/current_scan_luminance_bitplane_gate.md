# Current Scan Luminance Bitplane Gate

Scope: inspected low-order luminance bit planes and simple threshold masks in current page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots. This is a scan/source-quality gate, not extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T09:50:54`
- Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`
- Low-bit planes checked: `[0, 1, 2, 3]`
- Threshold planes checked: `[64, 96, 128, 160, 192]`
- Outlier abs-z threshold against shifted controls: `3.0`
- Active low-bit outlier rows: `4` (`O4,B4,G5,O5`)
- Active threshold-plane outlier rows: `4` (`O4,B4,G5,O5`)
- All-four active low-bit / threshold-plane outlier: `1` / `1`
- Active common low-bit signature: `mixed`
- Matching controls / OVERDOSE slots for common low-bit signature: `0` / `0`
- Shared active low-bit carrier / hidden bitplane candidate: `0` / `0`
- Max active/control/OVERDOSE low-bit abs-z: `4.62` / `1.81` / `1.50`
- Max active/control/OVERDOSE threshold abs-z: `10.15` / `2.17` / `1.29`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_luminance_bitplane_gate/current_scan_luminance_bitplane_gate_sheet.jpg`
- Fingerprint: `active=4|controls=16|slots=8|bits=0,1,2,3|thresholds=64,96,128,160,192|activeLowBitOutliers=4|activeThresholdOutliers=4|allFourLowBit=1|allFourThreshold=1|sharedCarrier=0|hiddenCandidate=0|commonLowBit=mixed|controlCommon=0|slotCommon=0|maxLowBitZ=4.62/1.81/1.50|maxThresholdZ=10.15/2.17/1.29|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | low-bit signature | threshold signature | low-bit outlier | threshold outlier | max bit z | max threshold z |
|---|---|---|---|---:|---:|---:|---:|
| `active` | `O5` | `b0=0.50|b1=0.50|b2=0.49|b3=0.49` | `t64=0.26|t96=0.28|t128=0.31|t160=0.62|t192=0.94` | 1 | 1 | 4.62 | 9.81 |
| `active` | `O4` | `b0=0.50|b1=0.50|b2=0.51|b3=0.49` | `t64=0.22|t96=0.24|t128=0.26|t160=0.64|t192=0.97` | 1 | 1 | 4.61 | 10.15 |
| `active` | `G5` | `b0=0.50|b1=0.50|b2=0.50|b3=0.51` | `t64=0.69|t96=0.70|t128=0.71|t160=0.73|t192=0.76` | 1 | 1 | 4.32 | 9.42 |
| `active` | `B4` | `b0=0.51|b1=0.53|b2=0.52|b3=0.53` | `t64=0.65|t96=0.66|t128=0.67|t160=0.68|t192=0.71` | 1 | 1 | 4.10 | 8.80 |
| `shifted_control` | `O5_dy+146` | `b0=1.00|b1=1.00|b2=1.00|b3=1.00` | `t64=0.00|t96=0.00|t128=0.00|t160=0.00|t192=0.00` | 0 | 0 | 1.81 | 1.41 |
| `shifted_control` | `O4_dy-292` | `b0=0.99|b1=0.99|b2=1.00|b3=1.00` | `t64=0.00|t96=0.00|t128=0.00|t160=0.00|t192=0.00` | 0 | 0 | 1.69 | 1.41 |
| `shifted_control` | `O5_dy+292` | `b0=0.99|b1=0.99|b2=1.00|b3=1.00` | `t64=0.00|t96=0.00|t128=0.00|t160=0.00|t192=0.00` | 0 | 0 | 1.66 | 1.41 |
| `overdose_slot` | `slot6_S` | `b0=0.98|b1=0.99|b2=0.99|b3=0.99` | `t64=0.00|t96=0.00|t128=0.01|t160=0.01|t192=0.01` | 0 | 0 | 1.50 | 1.29 |
| `overdose_slot` | `slot7_E` | `b0=0.98|b1=0.98|b2=0.99|b3=0.99` | `t64=0.01|t96=0.01|t128=0.01|t160=0.01|t192=0.02` | 0 | 0 | 1.45 | 1.23 |
| `shifted_control` | `G5_dy-292` | `b0=0.71|b1=0.72|b2=0.74|b3=0.76` | `t64=0.23|t96=0.23|t128=0.24|t160=0.25|t192=0.27` | 0 | 0 | 1.39 | 2.17 |
| `shifted_control` | `B4_dy+292` | `b0=0.71|b1=0.72|b2=0.74|b3=0.77` | `t64=0.17|t96=0.18|t128=0.19|t160=0.20|t192=0.23` | 0 | 0 | 1.29 | 1.35 |
| `shifted_control` | `B4_dy+146` | `b0=0.72|b1=0.73|b2=0.75|b3=0.79` | `t64=0.13|t96=0.14|t128=0.15|t160=0.16|t192=0.19` | 0 | 0 | 1.17 | 0.87 |
| `shifted_control` | `G5_dy+146` | `b0=0.73|b1=0.73|b2=0.76|b3=0.79` | `t64=0.13|t96=0.14|t128=0.14|t160=0.16|t192=0.18` | 0 | 0 | 1.13 | 0.72 |
| `shifted_control` | `B4_dy-292` | `b0=0.74|b1=0.74|b2=0.76|b3=0.80` | `t64=0.11|t96=0.12|t128=0.13|t160=0.15|t192=0.17` | 0 | 0 | 1.08 | 0.64 |
| `shifted_control` | `O4_dy+292` | `b0=0.95|b1=0.95|b2=0.95|b3=0.96` | `t64=0.03|t96=0.03|t128=0.03|t160=0.03|t192=0.04` | 0 | 0 | 1.08 | 0.96 |
| `shifted_control` | `O4_dy-146` | `b0=0.92|b1=0.93|b2=0.93|b3=0.94` | `t64=0.04|t96=0.05|t128=0.05|t160=0.05|t192=0.06` | 0 | 0 | 0.86 | 0.70 |
| `shifted_control` | `B4_dy-146` | `b0=0.75|b1=0.76|b2=0.78|b3=0.81` | `t64=0.13|t96=0.14|t128=0.15|t160=0.16|t192=0.18` | 0 | 0 | 0.83 | 0.76 |
| `overdose_slot` | `slot0_O` | `b0=0.92|b1=0.92|b2=0.93|b3=0.94` | `t64=0.05|t96=0.05|t128=0.06|t160=0.06|t192=0.07` | 0 | 0 | 0.78 | 0.59 |
| `shifted_control` | `G5_dy+292` | `b0=0.77|b1=0.78|b2=0.80|b3=0.82` | `t64=0.13|t96=0.14|t128=0.15|t160=0.16|t192=0.18` | 0 | 0 | 0.70 | 0.76 |
| `overdose_slot` | `slot5_O` | `b0=0.89|b1=0.90|b2=0.91|b3=0.91` | `t64=0.05|t96=0.05|t128=0.05|t160=0.09|t192=0.12` | 0 | 0 | 0.62 | 0.60 |
| `shifted_control` | `O5_dy-292` | `b0=0.89|b1=0.90|b2=0.90|b3=0.92` | `t64=0.05|t96=0.05|t128=0.06|t160=0.06|t192=0.07` | 0 | 0 | 0.54 | 0.58 |
| `shifted_control` | `O5_dy-146` | `b0=0.89|b1=0.90|b2=0.91|b3=0.92` | `t64=0.05|t96=0.05|t128=0.06|t160=0.06|t192=0.07` | 0 | 0 | 0.54 | 0.57 |
| `shifted_control` | `G5_dy-146` | `b0=0.80|b1=0.81|b2=0.82|b3=0.85` | `t64=0.10|t96=0.11|t128=0.11|t160=0.13|t192=0.14` | 0 | 0 | 0.54 | 0.30 |
| `overdose_slot` | `slot3_R` | `b0=0.80|b1=0.81|b2=0.83|b3=0.85` | `t64=0.11|t96=0.12|t128=0.12|t160=0.15|t192=0.18` | 0 | 0 | 0.50 | 0.74 |
| `overdose_slot` | `slot4_D` | `b0=0.80|b1=0.82|b2=0.83|b3=0.85` | `t64=0.09|t96=0.09|t128=0.10|t160=0.14|t192=0.18` | 0 | 0 | 0.48 | 0.78 |
| `overdose_slot` | `slot1_V` | `b0=0.83|b1=0.83|b2=0.85|b3=0.87` | `t64=0.10|t96=0.10|t128=0.11|t160=0.12|t192=0.13` | 0 | 0 | 0.32 | 0.18 |
| `overdose_slot` | `slot2_E` | `b0=0.83|b1=0.84|b2=0.85|b3=0.87` | `t64=0.11|t96=0.12|t128=0.12|t160=0.13|t192=0.14` | 0 | 0 | 0.31 | 0.40 |
| `shifted_control` | `O4_dy+146` | `b0=0.84|b1=0.84|b2=0.86|b3=0.88` | `t64=0.07|t96=0.08|t128=0.08|t160=0.09|t192=0.11` | 0 | 0 | 0.25 | 0.23 |

## Decision

- `current_scan_luminance_bitplane_no_selector`
- The active boxes do stand out in low-bit and threshold-plane metrics, but their low-bit signatures are mixed, not a shared all-four carrier.
- Threshold-plane contrast is visible ink/highlight behavior and still has no source-backed unit/order/transform clue.

## Next Move

- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.
