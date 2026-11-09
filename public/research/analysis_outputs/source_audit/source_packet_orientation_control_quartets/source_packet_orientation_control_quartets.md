# Source Packet Orientation Control Quartets

Scope: bounded control audit for the active source-packet orientation fingerprint. No OCR extraction, key candidates, hashes, WIF, seed, address checks, BIP39, or broad brute force were run.

- Created: `2026-05-21T07:33:51`
- Sheet: `analysis_outputs/source_audit/source_packet_orientation_control_quartets/source_packet_orientation_control_quartets_sheet.jpg`
- Fingerprint: `ykCombos=70|YKKY=11|YKKYNonExact=10|windows=5|windowYKKY=1|lineCombos=70|lineGaps325=1|dx=-++|dy=+++|sourceR3=0|selectors=0`

## Summary

- Full-page Y/K quartets tested: `70`.
- Full-page Y/K `YKKY` quartets: `11`; non-exact/mixed controls: `10`.
- Contiguous full-page Y/K windows tested: `5`; `YKKY` windows: `1`.
- C9 format-line quartets tested: `70`; exact `3/2/5` line-gap matches: `1`.
- C9 format-line sliding windows tested: `5`; exact `3/2/5` sliding-window matches: `0`.
- Full-page Y/K groups without pixel box geometry in the Y/K filter report: `8`; non-active groups among them: `4`.
- Source-backed R3 bridge hits: `0`; satisfied reopen triggers: `0`; selector unlocks: `0`.

## Active Geometry

- Target order: `buying_dip / one_billion / volcano_bonds / shitcoiner_heart`.
- Visual state: `YKKY`.
- Page lines / corridors: `22 25 27 32` / `4 7 9 14`.
- Group indexes / gaps: `12 14 15 19` / `2 1 4`.
- Center-step signs: dx `-++`, dy `+++`.
- C9 normalized centers: `0.651,0.028; 0.136,0.289; 0.359,0.462; 0.540,0.921`.

## Findings

- YKKY visual-state pattern is not unique as an unordered local quartet. Evidence: 11 of 70 full-page Y/K combinations form YKKY; 10 include non-active or mixed controls. Decision: `reject_pattern_only_orientation_or_selector`.
- The active quartet is the only contiguous full-page Y/K window with YKKY. Evidence: 1 of 5 sliding Y/K windows match YKKY, and the matching window is groups 12/14/15/19. Decision: `keep_as_source_registration_discriminator`.
- The exact readable line/corridor gap pattern is unique among C9 format-line combinations. Evidence: 1 of 70 format-line quartets match 3/2/5 gaps; no sliding format-line window matches. Decision: `keep_as_readable_upright_geometry_check`.
- Non-active Y/K pixel geometry remains unavailable in the current handoff. Evidence: 4 non-active Y/K groups lack page-line, box, and center coordinates in the Y/K filter report. Decision: `do_not_claim_controlled_pixel_center_uniqueness`.
- No R3 or reopen trigger is supplied by the control pass. Evidence: source-backed R3 hits 0; satisfied reopen triggers 0; selector unlocks 0. Decision: `location_and_orientation_only`.

## YKKY Combination Controls

| group indexes | gaps | active count | targets |
|---|---:|---:|---|
| `1 6 10 12` | `5 4 2` | `1` | `open_heart / calibration_black / stun_gun / buying_dip` |
| `1 6 10 19` | `5 4 9` | `1` | `open_heart / calibration_black / stun_gun / shitcoiner_heart` |
| `1 6 14 19` | `5 8 5` | `2` | `open_heart / calibration_black / one_billion / shitcoiner_heart` |
| `1 6 15 19` | `5 9 4` | `2` | `open_heart / calibration_black / volcano_bonds / shitcoiner_heart` |
| `1 10 14 19` | `9 4 5` | `2` | `open_heart / stun_gun / one_billion / shitcoiner_heart` |
| `1 10 15 19` | `9 5 4` | `2` | `open_heart / stun_gun / volcano_bonds / shitcoiner_heart` |
| `1 14 15 19` | `13 1 4` | `3` | `open_heart / one_billion / volcano_bonds / shitcoiner_heart` |
| `9 10 14 19` | `1 4 5` | `2` | `rancid_catnip / stun_gun / one_billion / shitcoiner_heart` |
| `9 10 15 19` | `1 5 4` | `2` | `rancid_catnip / stun_gun / volcano_bonds / shitcoiner_heart` |
| `9 14 15 19` | `5 1 4` | `3` | `rancid_catnip / one_billion / volcano_bonds / shitcoiner_heart` |

## Decision

- `YKKY` alone remains ruled out as orientation proof because it appears in multiple mixed/non-active quartets.
- The readable/upright discriminator is stronger than pattern-only evidence: the active quartet is the only contiguous filtered Y/K window and the only C9 format-line combination with exact `3/2/5` line/corridor gaps.
- This pass does not unlock extraction because the selectivity is still source-registration/location evidence and supplies no source-backed R3 unit/order instruction.
- Pixel-center uniqueness against earlier non-active Y/K controls remains unclaimed because those controls do not carry box/center coordinates in the current handoff.
