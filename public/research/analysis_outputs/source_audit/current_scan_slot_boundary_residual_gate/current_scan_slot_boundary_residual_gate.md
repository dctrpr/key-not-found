# Current Scan Slot Boundary Residual Gate

Scope: inspected current page-76 active target box starts, centers, and ends against the actual C9/OVERDOSE glyph-slot boundaries and centers, with page-76 non-active highlight controls. This is geometry inspection only. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T10:20:26`
- Active/highlight-control/vertical-control boxes: `4` / `7` / `16`
- Thresholds checked: `[4, 8, 16, 32]` px
- Signature threshold: `16` px
- All-four any anchor close <=16 px: `0`
- All-four left-boundary close <=16 px: `0`
- All-four center close <=16 px: `0`
- All-four right-boundary close <=16 px: `0`
- Active common slot-boundary signature: `mixed`
- Matching highlight / vertical controls for common signature: `0` / `0`
- Active nearest-center streams L/C/R: `DOER` / `OVED` / `SVRO`
- Active nearest-boundary streams L/C/R: `4123` / `5134` / `6246`
- Mean active/highlight-control anchor residual: `31.90` / `26.00` px
- Shared active slot-boundary carrier / hidden slot-boundary candidate: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/current_scan_slot_boundary_residual_gate_sheet.jpg`
- Fingerprint: `active=4|highlightControls=7|verticalControls=16|thresholds=4,8,16,32|allFourAny16=0|allFourLeftB16=0|allFourCenter16=0|allFourRightB16=0|commonSig=mixed|streamsC=DOER/OVED/SVRO|streamsB=4123/5134/6246|meanResidual=31.90/26.00|sharedCarrier=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Region Rows

| kind | region | signature | close16 | left boundary | center slot | right boundary | mean residual | max residual |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `active` | `O4` | `LC4:60N|CB5:51N|RB6:40N` | `0` | 0 | 0 | 0 | 50.41 | 60.28 |
| `active` | `B4` | `LC0:12Y|CB1:21N|RC1:30N` | `1` | 0 | 0 | 0 | 20.95 | 30.22 |
| `active` | `G5` | `LB2:12Y|CB3:32N|RC3:46N` | `1` | 1 | 0 | 0 | 30.09 | 46.22 |
| `active` | `O5` | `LB3:12Y|CC4:44N|RC5:22N` | `1` | 1 | 0 | 0 | 26.14 | 43.78 |
| `highlight_control` | `hl_O2` | `LB2:30N|CC2:11Y|RB3:8Y` | `2` | 0 | 1 | 1 | 16.26 | 30.00 |
| `highlight_control` | `hl_O1` | `LB2:25N|CB5:5Y|RB8:35N` | `1` | 0 | 0 | 0 | 21.69 | 35.00 |
| `highlight_control` | `hl_G3` | `LB3:26N|CC4:44N|RC6:8Y` | `1` | 0 | 0 | 0 | 26.02 | 44.22 |
| `highlight_control` | `hl_G4` | `LC0:4Y|CC1:48N|RB2:31N` | `1` | 0 | 0 | 0 | 27.69 | 47.78 |
| `highlight_control` | `hl_G2` | `LC0:42N|CB1:1Y|RC1:40N` | `1` | 0 | 0 | 0 | 27.86 | 42.28 |
| `highlight_control` | `hl_O3` | `LC0:13Y|CC2:38N|RB4:34N` | `1` | 0 | 0 | 0 | 28.17 | 37.78 |
| `highlight_control` | `hl_G1` | `LC0:33N|CC4:53N|RB8:17N` | `0` | 0 | 0 | 0 | 34.33 | 53.28 |

## Decision

- `current_scan_slot_boundary_residual_no_selector`
- The active boxes do not share a repeatable C9/OVERDOSE slot-boundary or slot-center residual.
- O4 breaks the left-boundary near-hit pattern, no all-four center/right-edge pattern appears, and no source-backed unit/order/transform clue is present.

## Next Move

- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.
