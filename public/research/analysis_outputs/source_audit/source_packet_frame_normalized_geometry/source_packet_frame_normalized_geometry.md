# Source Packet Frame-Normalized Geometry

Scope: normalize O4/B4/G5/O5 geometry inside the C9/Y-K frame and reflected p78 frame, and test simple C9-frame mirror controls. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T06:12:04`
- Active order: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`
- Visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- C9 frame: `[294, 2177, 2250, 3024]`
- C9 normalized center stream: `[[0.651074, 0.028335], [0.135736, 0.288666], [0.35864, 0.461629], [0.540133, 0.920897]]`
- C9 active full-inside count: `4/4`
- Reflected p78 frame: `[1234, 2398, 2250, 2950]`
- Reflected p78 full-inside count: `0/4`
- Reflected p78 partial-overlap ids: `['shitcoiner_heart']`
- C9 mirror hit counts by threshold: `{'horizontal_mirror': {'4': 0, '25': 0, '50': 0}, 'vertical_mirror': {'4': 0, '25': 0, '50': 0}, 'point_mirror': {'4': 0, '25': 0, '50': 0}}`
- C9 mirror all-four rehit by threshold: `{'horizontal_mirror': {'4': False, '25': False, '50': False}, 'vertical_mirror': {'4': False, '25': False, '50': False}, 'point_mirror': {'4': False, '25': False, '50': False}}`
- Frame-normalized fingerprint: `c9NormCenters=0.651,0.028;0.136,0.289;0.359,0.462;0.540,0.921|c9Inside=4/4|p78Inside=0/4|p78Partial=shitcoiner_heart|mirrorAllFour4px=none`
- Sheet: `analysis_outputs/source_audit/source_packet_frame_normalized_geometry/source_packet_frame_normalized_geometry_sheet.jpg`

## C9 Normalized Active Centers

| id | state | line/corridor | normalized center | full inside C9 | reflected p78 overlap fraction |
|---|---|---:|---:|---:|---:|
| `buying_dip` | `Y` | `22/4` | `[0.651074, 0.028335]` | `True` | `0.0` |
| `one_billion` | `K` | `25/7` | `[0.135736, 0.288666]` | `True` | `0.0` |
| `volcano_bonds` | `K` | `27/9` | `[0.35864, 0.461629]` | `True` | `0.0` |
| `shitcoiner_heart` | `Y` | `32/14` | `[0.540133, 0.920897]` | `True` | `0.247536` |

## Decision

- Keep this as source-validation/registration evidence only.
- C9/Y-K frame-normalized coordinates are useful for future source scaling checks.
- The reflected p78 frame alone has `0/4` full active target containment and only a partial O5 overlap.
- Simple C9-frame horizontal, vertical, and point mirrors do not re-hit all four active centers under the current alignment-tolerance thresholds.
- This does not reopen folded/mirrored 3D geometry, p78 frame, C9 frame, or OVERDOSE layout mechanics as selectors.
