# Current Scan RGB Registration Gate

Scope: inspected current page-76 scan RGB channel registration in active target boxes, shifted controls, and projected C9/OVERDOSE slots. This checks local scan/color displacement and chromatic artifact behavior; it is not steganographic extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T09:31:16`
- Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`
- Search radius: `+-3px`
- Reliable active boxes: `4` / `4`
- Active nonzero channel-registration rows: `0` (``)
- Active confidence-gain outliers above shifted-control p95: `0` (``)
- All-four active nonzero / confidence outlier: `0` / `0`
- Active shift signatures: `RG+0,+0|BG+0,+0,RG+0,+0|BG+0,+0,RG+0,+0|BG+0,+0,RG+0,+0|BG+0,+0`
- Shared active signature / matching controls / matching OVERDOSE slots: `RG+0,+0|BG+0,+0` / `16` / `8`
- Max active/control/OVERDOSE shift magnitude: `0.0` / `0.0` / `0.0` px
- Max active/control/OVERDOSE confidence gain: `0.000` / `0.000` / `0.000`
- Control p95 shift/gain: `0.0` / `0.000`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_rgb_registration_gate/current_scan_rgb_registration_gate_sheet.jpg`
- Fingerprint: `active=4|controls=16|slots=8|radius=3|reliableActive=4|activeNonzero=0|activeGainOutliers=0|allFourNonzero=0|allFourGain=0|commonSig=RG+0,+0|BG+0,+0|controlCommon=16|slotCommon=8|shiftMax=0.0/0.0/0.0|gainMax=0.000/0.000/0.000|controlP95=0.0/0.000|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | signature | max shift | max gain | nonzero pairs | edge std | reliable |
|---|---|---|---:|---:|---:|---:|---:|
| `active` | `O4` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 23.05 | 1 |
| `active` | `B4` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 45.11 | 1 |
| `active` | `G5` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 50.08 | 1 |
| `active` | `O5` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 22.07 | 1 |
| `shifted_control` | `O4_dy-292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 0.64 | 0 |
| `shifted_control` | `O4_dy-146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 25.69 | 1 |
| `shifted_control` | `O4_dy+146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 35.52 | 1 |
| `shifted_control` | `O4_dy+292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 24.18 | 1 |
| `shifted_control` | `B4_dy-292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 44.23 | 1 |
| `shifted_control` | `B4_dy-146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 43.61 | 1 |
| `shifted_control` | `B4_dy+146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 44.95 | 1 |
| `shifted_control` | `B4_dy+292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 45.85 | 1 |
| `shifted_control` | `G5_dy-292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 43.47 | 1 |
| `shifted_control` | `G5_dy-146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 42.01 | 1 |
| `shifted_control` | `G5_dy+146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 45.88 | 1 |
| `shifted_control` | `G5_dy+292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 40.97 | 1 |
| `shifted_control` | `O5_dy-292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 29.93 | 1 |
| `shifted_control` | `O5_dy-146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 30.57 | 1 |
| `shifted_control` | `O5_dy+146` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 0.68 | 0 |
| `shifted_control` | `O5_dy+292` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 0.73 | 0 |
| `overdose_slot` | `slot0_O` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 25.89 | 1 |
| `overdose_slot` | `slot1_V` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 37.17 | 1 |
| `overdose_slot` | `slot2_E` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 36.41 | 1 |
| `overdose_slot` | `slot3_R` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 36.02 | 1 |
| `overdose_slot` | `slot4_D` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 34.04 | 1 |
| `overdose_slot` | `slot5_O` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 22.28 | 1 |
| `overdose_slot` | `slot6_S` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 5.55 | 1 |
| `overdose_slot` | `slot7_E` | `RG+0,+0|BG+0,+0` | 0.0 | 0.000 | 0 | 4.87 | 1 |

## Decision

- `current_scan_rgb_registration_no_selector`
- Active boxes and projected OVERDOSE slots do not produce a unique RGB channel-registration signature against shifted controls.
- Color-channel displacement remains scan/source-quality evidence only and does not supply source-backed unit/order/transform evidence.

## Next Move

- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.
