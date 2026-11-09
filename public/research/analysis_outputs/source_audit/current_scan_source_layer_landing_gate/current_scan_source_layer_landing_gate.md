# Current Scan Source-Layer Landing Gate

Scope: split mirrored page-75 source material into black, orange, grey, combined feature, and broad non-white masks, then measured landing inside page-76 O4/B4/G5/O5 under natural, all-content, and lower-half content-box registration. This is source/geometry validation only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:15:28+02:00`
- Modes checked: `3`
- Layers checked: `['black', 'orange', 'grey', 'feature', 'broad']`
- Active target layer rows: `60`
- B4 positive layer/mode count: `0`
- All-four supported layer/mode count: `0`
- All-four weak-supported layer/mode count: `0`
- Best layer/mode: `natural_hflip:feature` with `3/4` supported
- Hidden source-layer candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_source_layer_landing_gate/current_scan_source_layer_landing_gate_sheet.jpg`
- Fingerprint: `modes=3|layers=black,orange,grey,feature,broad|rows=60|b4PositiveLayerModes=0|allFour=0|allFourWeak=0|best=natural_hflip:feature:3/4|b4Ratios=natural_hflip:black:0.0000,natural_hflip:orange:0.0000,natural_hflip:grey:0.0000,natural_hflip:feature:0.0000,natural_hflip:broad:0.0000,all_content_box_translation:black:0.0000,all_content_box_translation:orange:0.0000,all_content_box_translation:grey:0.0000,all_content_box_translation:feature:0.0000,all_content_box_translation:broad:0.0000,lower_half_content_box_translation:black:0.0000,lower_half_content_box_translation:orange:0.0000,lower_half_content_box_translation:grey:0.0000,lower_half_content_box_translation:feature:0.0000,lower_half_content_box_translation:broad:0.0000|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Layer Landing Rows

| mode | layer | O4 | B4 | G5 | O5 | supported | weak supported | zero targets |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `natural_hflip` | `black` | `0.086724` | `0.000000` | `0.033510` | `0.116103` | `2/4` | `3/4` | `B4` |
| `natural_hflip` | `orange` | `0.000000` | `0.000000` | `0.000000` | `0.000000` | `0/4` | `0/4` | `O4,B4,G5,O5` |
| `natural_hflip` | `grey` | `0.044209` | `0.000000` | `0.022132` | `0.062158` | `1/4` | `3/4` | `B4` |
| `natural_hflip` | `feature` | `0.130933` | `0.000000` | `0.055642` | `0.178261` | `3/4` | `3/4` | `B4` |
| `natural_hflip` | `broad` | `0.156451` | `0.000000` | `0.067072` | `0.220644` | `3/4` | `3/4` | `B4` |
| `all_content_box_translation` | `black` | `0.038009` | `0.000000` | `0.050343` | `0.000000` | `1/4` | `2/4` | `B4,O5` |
| `all_content_box_translation` | `orange` | `0.000000` | `0.000000` | `0.000000` | `0.000000` | `0/4` | `0/4` | `O4,B4,G5,O5` |
| `all_content_box_translation` | `grey` | `0.024135` | `0.000000` | `0.015170` | `0.000000` | `0/4` | `2/4` | `B4,O5` |
| `all_content_box_translation` | `feature` | `0.062143` | `0.000000` | `0.065513` | `0.000000` | `2/4` | `2/4` | `B4,O5` |
| `all_content_box_translation` | `broad` | `0.073073` | `0.000000` | `0.074657` | `0.000354` | `2/4` | `2/4` | `B4` |
| `lower_half_content_box_translation` | `black` | `0.078248` | `0.000000` | `0.027120` | `0.118808` | `2/4` | `3/4` | `B4` |
| `lower_half_content_box_translation` | `orange` | `0.000000` | `0.000000` | `0.000000` | `0.000000` | `0/4` | `0/4` | `O4,B4,G5,O5` |
| `lower_half_content_box_translation` | `grey` | `0.044343` | `0.000000` | `0.018495` | `0.063865` | `1/4` | `3/4` | `B4` |
| `lower_half_content_box_translation` | `feature` | `0.122591` | `0.000000` | `0.045615` | `0.182673` | `2/4` | `3/4` | `B4` |
| `lower_half_content_box_translation` | `broad` | `0.148510` | `0.000000` | `0.054655` | `0.225700` | `3/4` | `3/4` | `B4` |

## Decision

- `current_scan_source_layer_landing_no_selector`
- B4 remains zero across black, orange, grey, combined feature, and broad non-white source layers under all tested registration modes.
- Orange source material does not land on any active target in this valid same-leaf geometry.
- The prior B4 failure is therefore not a dark-ink threshold artifact; it is a missing source-material landing.

## Next Move

- Keep current-scan held-to-light closed except as source-review evidence. Best direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit, order, or transform.
