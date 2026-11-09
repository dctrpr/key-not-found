# Current Scan Source-Layer Miss-Distance Gate

Scope: measured how far mirrored page-75 source-layer pixels sit from page-76 O4/B4/G5/O5 active boxes under natural, all-content, and lower-half content-box registration. This is source/geometry validation only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:26:25+02:00`
- Modes checked: `3`
- Layers checked: `['black', 'orange', 'grey', 'feature', 'broad']`
- Active distance rows: `60`
- Control distance rows: `360`
- B4 min expansion any / feature / broad: `22` / `136` / `22` px
- B4 tiny miss candidate <= `16` px: `0`
- All-four within expansion layer/modes: `{'4': 0, '8': 0, '16': 0, '32': 1, '64': 1, '128': 3}`
- Best all-four expansion layer/mode: `all_content_box_translation:broad:22px`
- Hidden miss-distance candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/current_scan_source_layer_miss_distance_gate_sheet.jpg`
- Fingerprint: `modes=3|layers=black,orange,grey,feature,broad|rows=60|controls=360|b4MinAny=22|b4MinFeature=136|b4MinBroad=22|b4Tiny=0|allFourWithin16=0|bestAllFour=all_content_box_translation:broad:22px|b4=natural_hflip:black:136,natural_hflip:orange:288,natural_hflip:grey:136,natural_hflip:feature:136,natural_hflip:broad:67,all_content_box_translation:black:203,all_content_box_translation:orange:>260,all_content_box_translation:grey:202,all_content_box_translation:feature:202,all_content_box_translation:broad:22,lower_half_content_box_translation:black:161,lower_half_content_box_translation:orange:>260,lower_half_content_box_translation:grey:160,lower_half_content_box_translation:feature:160,lower_half_content_box_translation:broad:71|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Distance Rows

| mode | layer | O4 px | B4 px | G5 px | O5 px | <=8 | <=16 | <=32 | <=64 | all-four max px | B4 side |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `natural_hflip` | `black` | `0` | `136` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `136` | `top_right` |
| `natural_hflip` | `orange` | `61` | `288` | `>260` | `>260` | `0/4` | `0/4` | `0/4` | `1/4` | `>260` | `top_right` |
| `natural_hflip` | `grey` | `0` | `136` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `136` | `top_right` |
| `natural_hflip` | `feature` | `0` | `136` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `136` | `top_right` |
| `natural_hflip` | `broad` | `0` | `67` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `67` | `bottom` |
| `all_content_box_translation` | `black` | `0` | `203` | `0` | `24` | `2/4` | `2/4` | `3/4` | `3/4` | `203` | `top_right` |
| `all_content_box_translation` | `orange` | `28` | `>260` | `>260` | `>260` | `0/4` | `0/4` | `1/4` | `1/4` | `>260` | `>260px` |
| `all_content_box_translation` | `grey` | `0` | `202` | `0` | `11` | `2/4` | `3/4` | `3/4` | `3/4` | `202` | `top_right` |
| `all_content_box_translation` | `feature` | `0` | `202` | `0` | `11` | `2/4` | `3/4` | `3/4` | `3/4` | `202` | `top_right` |
| `all_content_box_translation` | `broad` | `0` | `22` | `0` | `0` | `3/4` | `3/4` | `4/4` | `4/4` | `22` | `bottom_right` |
| `lower_half_content_box_translation` | `black` | `0` | `161` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `161` | `top_right` |
| `lower_half_content_box_translation` | `orange` | `29` | `>260` | `>260` | `>260` | `0/4` | `0/4` | `1/4` | `1/4` | `>260` | `>260px` |
| `lower_half_content_box_translation` | `grey` | `0` | `160` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `160` | `top_right` |
| `lower_half_content_box_translation` | `feature` | `0` | `160` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `160` | `top_right` |
| `lower_half_content_box_translation` | `broad` | `0` | `71` | `0` | `0` | `3/4` | `3/4` | `3/4` | `3/4` | `71` | `bottom_right` |

## Decision

- `current_scan_source_layer_miss_distance_no_tiny_miss`
- B4 has no source layer within the 16px tiny-miss band under the tested registrations, so the zero B4 landing is not a small crop or threshold miss.
- All-four small-expansion support remains absent at the selector thresholds, and source-backed R3 remains 0.

## Next Move

- Keep current-scan held-to-light closed except as source-review evidence. Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
