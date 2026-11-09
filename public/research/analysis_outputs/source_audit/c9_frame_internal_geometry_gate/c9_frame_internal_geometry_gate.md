# C9 Frame Internal Geometry Gate

Scope: inspect only O4/B4/G5/O5 positions inside the C9 frame: edge contacts, centerlines, diagonals, normalized positions, and mirror-pair relations. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T02:22:25`
- C9 frame: `[294.0, 2176.81, 2250.0, 3023.73]`
- Frame center: `[1272.0, 2600.27]`
- Frame size: `[1956.0, 846.92]`
- Sheet: `analysis_outputs/source_audit/c9_frame_internal_geometry_gate/c9_frame_internal_geometry_gate_sheet.jpg`

## Target Geometry

| target | visual | line/corridor | normalized center | nearest frame edge | centerline distances | diagonal distances |
|---|---|---:|---|---|---|---|
| `O4 O4 buying the dip` | `Y` | `L22/C4` | `[0.651074, 0.028562]` | `top 0.19px` | `{'verticalCenterline': 295.5, 'horizontalCenterline': 399.27}` | `{'topLeftToBottomRight': 483.81, 'topRightToBottomLeft': 248.99}` |
| `B4 B4 $1 billion` | `K` | `L25/C7` | `[0.135736, 0.288917]` | `left 134.0px` | `{'verticalCenterline': 712.5, 'horizontalCenterline': 178.77}` | `{'topLeftToBottomRight': 119.05, 'topRightToBottomLeft': 447.16}` |
| `G5 G5 Volcano Bonds` | `K` | `L27/C9` | `[0.35864, 0.461897]` | `top 367.19px` | `{'verticalCenterline': 276.5, 'horizontalCenterline': 32.27}` | `{'topLeftToBottomRight': 80.25, 'topRightToBottomLeft': 139.48}` |
| `O5 O5 shitcoiner at heart` | `Y` | `L32/C14` | `[0.540133, 0.921209]` | `bottom 41.73px` | `{'verticalCenterline': 78.5, 'horizontalCenterline': 356.73}` | `{'topLeftToBottomRight': 296.17, 'topRightToBottomLeft': 358.55}` |

## Pair Symmetry

| pair | midpoint delta from frame center | midpoint distance | x-mirror delta | y-mirror delta | point-reflection delta |
|---|---|---:|---:|---:|---:|
| `O4-B4` | `[-208.5, -289.02]` | `356.38` | `471.71` | `1161.98` | `712.75` |
| `O4-G5` | `[9.5, -215.77]` | `215.98` | `367.49` | `716.53` | `431.96` |
| `O4-O5` | `[187.0, -21.27]` | `188.21` | `843.45` | `221.13` | `376.41` |
| `B4-G5` | `[-494.5, -105.52]` | `505.63` | `999.79` | `484.39` | `1011.27` |
| `B4-O5` | `[-317.0, 88.98]` | `329.25` | `829.89` | `810.77` | `658.5` |
| `G5-O5` | `[-99.0, 162.23]` | `190.05` | `436.49` | `480.94` | `380.1` |

## Findings

- Strict edge contacts <=4 px: `1` (`O4:top=0.19px`).
- Centerline/diagonal center hits <=25 px: `0`.
- Mirror-pair hits <=25 px: `0`.
- Closest pair midpoint to frame center: `O4-O5` at `188.21 px`.
- Group/vertical order remains `['buying_dip', 'one_billion', 'volcano_bonds', 'shitcoiner_heart']`; left-to-right order remains `['one_billion', 'volcano_bonds', 'shitcoiner_heart', 'buying_dip']`.

## Assessment

- Only O4 has a strict edge coincidence: its top edge is effectively the C9 frame top edge.
- That contact is not independent extraction permission because the C9 frame was already derived as the active-quartet full-coverage envelope.
- No active target center sits on a C9 centerline or diagonal within 25 px.
- No active pair forms a horizontal, vertical, or point-reflection mirror pair within 25 px.
- Internal C9 geometry therefore does not resolve the group-order versus left-to-right order conflict.

## Decision

- Do not promote internal C9 edge/axis/diagonal/pair geometry as a selector.
- O4 top-edge coincidence is useful as a future source-registration check, but it is not independent extraction permission.
- Keep C9 as source-validation geometry only. Reopen extraction only if a new source/clue names frame edge, centerline, diagonal, or target-order operation.
