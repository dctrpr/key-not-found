# Current Scan Content-Box Registration Gate

Scope: tested whether the visible content envelope in the current page rasters can justify changing valid page-75 -> page-76 held-to-light registration. This is a bounded source/geometry pass only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:08:01+02:00`
- Pages checked: `[75, 76, 78, 79]`
- Valid pair / same canvas: `75->76` / `1`
- Valid all-content shift dx,dy: `[31.5, -61.0]`
- Valid lower-half shift dx,dy: `[32.5, -0.5]`
- All-content shift stable / lower-half shift stable: `0` / `1`
- Content-box registration candidate / hidden content-box candidate: `0` / `0`
- Best content-box landing: `natural_hflip` with `3/4` source-supported targets
- Best B4 source-ink ratio: `0.000000`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_content_box_registration_gate/current_scan_content_box_registration_gate_sheet.jpg`
- Fingerprint: `pages=4|pair=75->76|sameCanvas=1|allShift=31.5,-61.0|lowerShift=32.5,-0.5|allStable=0|lowerStable=1|natural=3/4:B4=0.0000|allContent=2/4:B4=0.0000|lowerContent=2/4:B4=0.0000|candidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Content Box Rows

| page | kind | box | width | height | center | edge/band clipped |
|---:|---|---|---:|---:|---|---|
| `75` | `all_content` | `[29, 134, 2544, 3264]` | `2515` | `3130` | `[1286.5, 1699.0]` | `1` |
| `75` | `lower_half_content` | `[29, 1632, 2544, 3264]` | `2515` | `1632` | `[1286.5, 2448.0]` | `1` |
| `76` | `all_content` | `[34, 13, 2544, 3263]` | `2510` | `3250` | `[1289.0, 1638.0]` | `1` |
| `76` | `lower_half_content` | `[36, 1632, 2544, 3263]` | `2508` | `1631` | `[1290.0, 2447.5]` | `1` |
| `78` | `all_content` | `[27, 16, 2477, 3264]` | `2450` | `3248` | `[1252.0, 1640.0]` | `1` |
| `78` | `lower_half_content` | `[34, 1632, 2543, 3264]` | `2509` | `1632` | `[1288.5, 2448.0]` | `1` |
| `79` | `all_content` | `[36, 0, 2544, 3264]` | `2508` | `3264` | `[1290.0, 1632.0]` | `1` |
| `79` | `lower_half_content` | `[36, 1632, 2544, 3264]` | `2508` | `1632` | `[1290.0, 2448.0]` | `1` |

## Pair Transforms

| pair | kind | dx | dy | magnitude | scale x | scale y | source edge/band | target edge/band |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `75->76` | `all_content` | `31.5` | `-61.0` | `68.653` | `0.998012` | `1.038339` | `1` | `1` |
| `75->76` | `lower_half_content` | `32.5` | `-0.5` | `32.504` | `0.997217` | `0.999387` | `1` | `1` |
| `78->79` | `all_content` | `-2.0` | `-8.0` | `8.246` | `1.023673` | `1.004926` | `1` | `1` |
| `78->79` | `lower_half_content` | `34.5` | `0.0` | `34.5` | `0.999601` | `1.0` | `1` | `1` |
| `76->75` | `all_content` | `31.5` | `61.0` | `68.653` | `1.001992` | `0.963077` | `1` | `1` |
| `76->75` | `lower_half_content` | `32.5` | `0.5` | `32.504` | `1.002791` | `1.000613` | `1` | `1` |
| `79->78` | `all_content` | `-2.0` | `8.0` | `8.246` | `0.976874` | `0.995098` | `1` | `1` |
| `79->78` | `lower_half_content` | `34.5` | `0.0` | `34.5` | `1.000399` | `1.0` | `1` | `1` |
| `75->78` | `all_content` | `-5.5` | `-59.0` | `59.256` | `0.974155` | `1.0377` | `1` | `1` |
| `75->78` | `lower_half_content` | `31.0` | `0.0` | `31.0` | `0.997614` | `1.0` | `1` | `1` |
| `76->79` | `all_content` | `35.0` | `-6.0` | `35.511` | `0.999203` | `1.004308` | `1` | `1` |
| `76->79` | `lower_half_content` | `36.0` | `0.5` | `36.003` | `1.0` | `1.000613` | `1` | `1` |

## Source-Ink Landing Rows

| mode | dx | dy | O4 | B4 | G5 | O5 | supported | weak supported | zero-source targets |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `natural_hflip` | `0.0` | `0.0` | `0.140212` | `0.000000` | `0.059643` | `0.194042` | `3/4` | `3/4` | `B4` |
| `all_content_box_translation` | `31.5` | `-61.0` | `0.066604` | `0.000000` | `0.069046` | `0.000032` | `2/4` | `2/4` | `B4` |
| `lower_half_content_box_translation` | `32.5` | `-0.5` | `0.132361` | `0.000000` | `0.048732` | `0.198744` | `2/4` | `3/4` | `B4` |

## Decision

- `current_scan_content_box_registration_no_selector`
- The all-page content envelope is not a stable registration frame: its vertical shift changes with page content.
- The lower-half envelope has a repeatable roughly 33 px horizontal bias, but it is clipped to canvas and band edges, so it is not an independent physical page-frame cue.
- Applying the lower-half content-box shift does not rescue the valid held-to-light landing: B4 remains at zero source ink, and no mode supports all four active boxes.
- This closes content-envelope normalization as a current-scan held-to-light selector.

## Next Move

- Best direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
