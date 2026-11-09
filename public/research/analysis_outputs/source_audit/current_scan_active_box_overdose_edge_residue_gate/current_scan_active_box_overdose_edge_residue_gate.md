# Current Scan Active Box OVERDOSE Edge-Residue Gate

Scope: bounded current-scan/PDF witness-box edge-residue control. No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T13:35:33`
- Witness variants checked: `8`
- Exact active nearest-center streams left/center/right: `DOER` / `OVED` / `SVRO`
- Exact active close rows any/left-boundary/center-slot/right-boundary at <=16px: `3` / `2` / `0` / `0`
- Variants with all-four any-anchor closeness at <=16px: `1`
- All-four close variants using substituted boxes: `1`
- Hidden edge-residue candidates: `0`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `variants=8|exactCenter=OVED|exactEdges=DOER/SVRO|exactClose=3/2/0/0|allFourAny=1|subAllFourAny=1|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Variant Rows

| # | witnesses | left-center stream | center stream | right-center stream | close rows any/L/C/R | mean nearest residue | all exact | edge candidate |
|---|---|---|---|---|---|---|---|---|
| `1` | `O4_active_index+p76_orange_4 / B4_active_index / G5_active_index / O5_active_index+p76_orange_5` | `DOER` | `OVED` | `SVRO` | `3/2/0/0` | `31.916667` | `True` | `False` |
| `2` | `O4_active_index+p76_orange_4 / B4_active_index / annotated_15_grey / O5_active_index+p76_orange_5` | `DOVR` | `OVVD` | `SVEO` | `2/1/0/0` | `33.135417` | `False` | `False` |
| `3` | `O4_active_index+p76_orange_4 / annotated_14_grey / G5_active_index / O5_active_index+p76_orange_5` | `DOER` | `OEED` | `SDRO` | `2/2/0/0` | `39.647917` | `False` | `False` |
| `4` | `O4_active_index+p76_orange_4 / annotated_14_grey / annotated_15_grey / O5_active_index+p76_orange_5` | `DOVR` | `OEVD` | `SDEO` | `1/1/0/0` | `40.866667` | `False` | `False` |
| `5` | `annotated_13_orange / B4_active_index / G5_active_index / O5_active_index+p76_orange_5` | `ROER` | `DVED` | `DVRO` | `4/2/0/0` | `27.08` | `False` | `False` |
| `6` | `annotated_13_orange / B4_active_index / annotated_15_grey / O5_active_index+p76_orange_5` | `ROVR` | `DVVD` | `DVEO` | `3/1/0/0` | `28.29875` | `False` | `False` |
| `7` | `annotated_13_orange / annotated_14_grey / G5_active_index / O5_active_index+p76_orange_5` | `ROER` | `DEED` | `DDRO` | `3/2/0/0` | `34.81125` | `False` | `False` |
| `8` | `annotated_13_orange / annotated_14_grey / annotated_15_grey / O5_active_index+p76_orange_5` | `ROVR` | `DEVD` | `DDEO` | `2/1/0/0` | `36.03` | `False` | `False` |

## Decision

- current_scan_active_box_overdose_edge_residue_no_selector.
- Reason: Exact active centers repeat the known OVED stream, but 0/4 exact active centers are close to slot centers at <=16px and the exact left/right edge streams are mixed. A substituted annotated O4 variant has better all-four any-anchor closeness than the exact active boxes, so edge residue is not exact-active-specific and has no source-backed R3 permission.
- Next move: Do not pursue active-box edge/center residue as an extraction selector. The next useful local pass should inspect a different source/provenance surface, or stop until a true physical/original-layout asset or raw clue wording supplies unit/order/transform.

Sheet: `analysis_outputs/source_audit/current_scan_active_box_overdose_edge_residue_gate/current_scan_active_box_overdose_edge_residue_gate_sheet.jpg`
