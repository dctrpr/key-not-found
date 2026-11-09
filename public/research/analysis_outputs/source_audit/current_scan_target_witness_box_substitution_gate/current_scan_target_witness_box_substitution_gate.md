# Current Scan Target Witness Box Substitution Gate

Scope: bounded current-scan/PDF witness-box substitution control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.

- Created: `2026-05-24T13:13:38`
- Unique per-target geometry variants: `8`
- Per-target option counts: `O4:2, B4:2, G5:2, O5:1`
- Line-gap `3/2/5` hits: `2`
- Slot-stream `OVED` hits: `1`
- Combined fingerprint hits: `1`
- Combined hits using substituted/non-exact boxes: `0`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `options=O4:2,B4:2,G5:2,O5:1|variants=8|line325=2|slotOVED=1|lineAndSlot=1|combined=1|subCombined=0|sourceR3=0|triggers=0/9|selectors=0`

## Witness Options

| target | witness ids | state/color | slot | center | exact active box | label |
|---|---|---|---|---|---|---|
| `O4` | `O4_active_index + p76_orange_4` | `Y/O` | `O5` | `1567.5,2201.0` | `True` | buying the dip |
| `O4` | `annotated_13_orange` | `Y/O` | `D4` | `1273.65,2265.93` | `False` | buying the dip |
| `B4` | `B4_active_index` | `K/B` | `V1` | `559.5,2421.5` | `True` | $1 billion |
| `B4` | `annotated_14_grey` | `K/B` | `E2` | `961.885,2450.34` | `False` | $1 billion |
| `G5` | `G5_active_index` | `K/B` | `E2` | `995.5,2568.0` | `True` | Volcano Bonds |
| `G5` | `annotated_15_grey` | `K/B` | `V1` | `765.625,2631.37` | `False` | Volcano Bonds |
| `O5` | `O5_active_index + p76_orange_5` | `Y/O` | `D4` | `1350.5,2957.0` | `True` | shitcoiner at heart |

## Variants

| # | witnesses | line gaps | slots | exact boxes | combined hit |
|---|---|---|---|---|---|
| `1` | `O4_active_index+p76_orange_4 / B4_active_index / G5_active_index / O5_active_index+p76_orange_5` | `3/2/5` | `OVED` | `4/4` | `True` |
| `2` | `O4_active_index+p76_orange_4 / B4_active_index / annotated_15_grey / O5_active_index+p76_orange_5` | `3/3/4` | `OVVD` | `3/4` | `False` |
| `3` | `O4_active_index+p76_orange_4 / annotated_14_grey / G5_active_index / O5_active_index+p76_orange_5` | `3/2/5` | `OEED` | `3/4` | `False` |
| `4` | `O4_active_index+p76_orange_4 / annotated_14_grey / annotated_15_grey / O5_active_index+p76_orange_5` | `3/2/4` | `OEVD` | `2/4` | `False` |
| `5` | `annotated_13_orange / B4_active_index / G5_active_index / O5_active_index+p76_orange_5` | `2/2/5` | `DVED` | `3/4` | `False` |
| `6` | `annotated_13_orange / B4_active_index / annotated_15_grey / O5_active_index+p76_orange_5` | `2/3/4` | `DVVD` | `2/4` | `False` |
| `7` | `annotated_13_orange / annotated_14_grey / G5_active_index / O5_active_index+p76_orange_5` | `2/2/5` | `DEED` | `2/4` | `False` |
| `8` | `annotated_13_orange / annotated_14_grey / annotated_15_grey / O5_active_index+p76_orange_5` | `2/2/4` | `DEVD` | `1/4` | `False` |

## Decision

- keep_exact_target_boxes_as_registration_authority_only.
- Reason: Only the exact active target boxes preserve both line gaps 3/2/5 and C9 slot stream OVED. Annotation substitutions break either slot stream or line-gap phase, so they do not create a hidden selector or an alternate read path.
- Next move: Use exact active boxes plus visual duplicate boxes as future source-validation witnesses; treat broad annotation boxes as text-authority/context witnesses, not geometry selectors.

Sheet: `analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate/current_scan_target_witness_box_substitution_gate_sheet.jpg`
