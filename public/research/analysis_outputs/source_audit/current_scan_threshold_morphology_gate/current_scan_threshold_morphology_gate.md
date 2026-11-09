# Current Scan Threshold Morphology Gate

Scope: inspected thresholded ink/component morphology in current page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots. This is a scan/source-quality gate, not extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T10:00:54`
- Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`
- Thresholds checked: `[64, 96, 128, 160, 192]`
- Signature thresholds: `[128, 160, 192]`
- Outlier abs-z threshold against shifted controls: `3.0`
- Active morphology outlier rows: `4` (`O4,B4,G5,O5`)
- All-four active morphology outlier: `1`
- Active common morphology signature: `mixed`
- Matching controls / OVERDOSE slots for common morphology signature: `0` / `0`
- Shared active morphology carrier / hidden morphology candidate: `0` / `0`
- Max active/control/OVERDOSE morphology abs-z: `78.91` / `2.48` / `30.19`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_threshold_morphology_gate/current_scan_threshold_morphology_gate_sheet.jpg`
- Fingerprint: `active=4|controls=16|slots=8|thresholds=64,96,128,160,192|activeMorphOutliers=4|allFourMorph=1|sharedCarrier=0|hiddenCandidate=0|commonMorph=mixed|controlCommon=0|slotCommon=0|maxMorphZ=78.91/2.48/30.19|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | morphology signature | outlier | max z | strongest metric | threshold | value |
|---|---|---|---:|---:|---|---:|---:|
| `active` | `O4` | `t128=d3c15l3b9|t160=d6c19l63b10|t192=d10c1l97b10` | 1 | 78.91 | `largestComponentAreaRatio` | `192` | `0.971` |
| `active` | `O5` | `t128=d3c18l2b10|t160=d6c25l59b10|t192=d9c1l94b10` | 1 | 76.54 | `largestComponentAreaRatio` | `192` | `0.942` |
| `active` | `G5` | `t128=d7c12l66b10|t160=d7c9l68b10|t192=d8c9l71b10` | 1 | 63.11 | `largestComponentAreaRatio` | `64` | `0.641` |
| `active` | `B4` | `t128=d7c6l64b9|t160=d7c7l66b9|t192=d7c7l68b10` | 1 | 61.17 | `largestComponentAreaRatio` | `64` | `0.622` |
| `overdose_slot` | `slot1_V` | `t128=d1c99l2b9|t160=d1c96l2b9|t192=d1c93l3b10` | 1 | 30.19 | `yProjectionRunCount` | `192` | `14.000` |
| `overdose_slot` | `slot0_O` | `t128=d1c44l2b4|t160=d1c45l2b4|t192=d1c47l2b4` | 1 | 29.18 | `yProjectionRunCount` | `64` | `15.000` |
| `overdose_slot` | `slot2_E` | `t128=d1c93l4b9|t160=d1c90l4b10|t192=d1c90l4b10` | 1 | 27.86 | `yProjectionRunCount` | `192` | `13.000` |
| `overdose_slot` | `slot4_D` | `t128=d1c95l0b9|t160=d1c84l3b9|t192=d2c81l6b10` | 1 | 25.53 | `yProjectionRunCount` | `192` | `12.000` |
| `overdose_slot` | `slot3_R` | `t128=d1c99l2b9|t160=d2c91l4b9|t192=d2c88l5b9` | 1 | 23.19 | `yProjectionRunCount` | `192` | `11.000` |
| `overdose_slot` | `slot5_O` | `t128=d1c43l0b9|t160=d1c30l4b9|t192=d1c30l5b9` | 1 | 22.98 | `yProjectionRunCount` | `64` | `12.000` |
| `overdose_slot` | `slot7_E` | `t128=d0c1l1b2|t160=d0c1l1b2|t192=d0c1l2b7` | 1 | 11.52 | `yProjectionRunCount` | `192` | `6.000` |
| `overdose_slot` | `slot6_S` | `t128=d0c3l0b8|t160=d0c3l0b8|t192=d0c2l1b8` | 1 | 6.86 | `yProjectionRunCount` | `192` | `4.000` |
| `shifted_control` | `O4_dy-292` | `t128=d0c0l0b0|t160=d0c0l0b0|t192=d0c0l0b0` | 0 | 2.48 | `yProjectionRunCount` | `192` | `0.000` |
| `shifted_control` | `O5_dy-146` | `t128=d1c22l0b9|t160=d1c22l0b9|t192=d1c23l1b9` | 0 | 2.32 | `yProjectionRunCount` | `96` | `2.000` |
| `shifted_control` | `B4_dy+292` | `t128=d2c12l4b9|t160=d2c11l4b9|t192=d2c11l4b9` | 0 | 2.29 | `largestComponentBboxAreaRatio` | `64` | `0.083` |
| `shifted_control` | `O5_dy-292` | `t128=d1c22l0b9|t160=d1c22l0b9|t192=d1c23l1b9` | 0 | 2.19 | `yProjectionRunCount` | `192` | `2.000` |
| `shifted_control` | `G5_dy-292` | `t128=d2c14l2b9|t160=d3c14l3b9|t192=d3c14l3b9` | 0 | 2.17 | `darkRatio` | `64` | `0.225` |
| `shifted_control` | `O5_dy+292` | `t128=d0c0l0b0|t160=d0c0l0b0|t192=d0c0l0b0` | 0 | 2.00 | `yProjectionRunCount` | `160` | `0.000` |
| `shifted_control` | `O5_dy+146` | `t128=d0c0l0b0|t160=d0c0l0b0|t192=d0c0l0b0` | 0 | 1.99 | `largestComponentFillRatio` | `192` | `0.000` |
| `shifted_control` | `G5_dy+292` | `t128=d1c18l2b8|t160=d2c17l2b9|t192=d2c18l2b9` | 0 | 1.81 | `largestComponentFillRatio` | `128` | `0.693` |
| `shifted_control` | `B4_dy-146` | `t128=d1c10l3b7|t160=d2c10l3b7|t192=d2c9l4b7` | 0 | 1.79 | `largestComponentAreaRatio` | `64` | `0.030` |
| `shifted_control` | `G5_dy-146` | `t128=d1c20l1b7|t160=d1c18l1b7|t192=d1c17l1b7` | 0 | 1.51 | `componentCount` | `64` | `24.000` |
| `shifted_control` | `O4_dy+292` | `t128=d0c5l1b1|t160=d0c4l1b1|t192=d0c4l1b1` | 0 | 1.21 | `inkBboxAreaRatio` | `128` | `0.124` |
| `shifted_control` | `G5_dy+146` | `t128=d1c18l2b8|t160=d2c17l2b8|t192=d2c16l2b9` | 0 | 1.17 | `largeComponentCount` | `64` | `16.000` |
| `shifted_control` | `O4_dy-146` | `t128=d0c5l2b2|t160=d1c5l2b2|t192=d1c5l2b2` | 0 | 1.06 | `inkBboxAreaRatio` | `160` | `0.180` |
| `shifted_control` | `B4_dy+146` | `t128=d1c12l2b7|t160=d2c12l2b7|t192=d2c12l2b7` | 0 | 1.05 | `columnOccupancyRatio` | `96` | `0.852` |
| `shifted_control` | `B4_dy-292` | `t128=d1c14l1b8|t160=d1c12l1b8|t192=d2c12l2b8` | 0 | 0.95 | `inkBboxAreaRatio` | `96` | `0.841` |
| `shifted_control` | `O4_dy+146` | `t128=d1c12l1b4|t160=d1c12l1b4|t192=d1c11l2b4` | 0 | 0.50 | `largestComponentFillRatio` | `192` | `0.456` |

## Decision

- `current_scan_threshold_morphology_no_selector`
- The active boxes stand out in thresholded morphology, but their component/shape signatures are mixed and do not form a shared all-four carrier.
- The component behavior follows visible target ink and still has no source-backed unit/order/transform clue.

## Next Move

- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.
