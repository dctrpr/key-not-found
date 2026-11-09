# Active Frame Edge/Axis Gate

Scope: test whether p78 same-layout/current-mirror frame edges or centerlines select O4/B4/G5/O5 or instruction-bearing words. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:28:56`
- Same-layout frame: `[294.0, 2398.0, 1310.0, 2950.0]`
- Current-mirror frame: `[1234.0, 2398.0, 2250.0, 2950.0]`
- Lines checked: `12`
- Active target contacts: `6` total, `3` strong
- Hard instruction hits: `0`
- Sheet: `analysis_outputs/source_audit/active_frame_edge_axis_gate/active_frame_edge_axis_gate_sheet.jpg`

## Contact Table

| line | role | active hits | strong hits | words touched | instruction hits | preview |
|---|---|---|---:|---:|---|---|
| `same_layout_left` | `left` | - | `0` | `0` | `-` | `` |
| `same_layout_right` | `right` | shitcoiner_heart:0.36 | `0` | `7` | `-` | `should earnings pay tagged could trust siukbeodmensertslveaarty` |
| `same_layout_center_x` | `center_x` | volcano_bonds:1.0 | `1` | `5` | `-` | `rid the Wall on because` |
| `same_layout_top` | `top` | one_billion:1.0 | `1` | `7` | `-` | `eis in bitcoin — that he should` |
| `same_layout_bottom` | `bottom` | shitcoiner_heart:0.434783 | `0` | `5` | `-` | `Maybe because he's a siukbeodmensertslveaarty` |
| `same_layout_center_y` | `center_y` | - | `0` | `0` | `-` | `` |
| `current_mirror_left` | `left` | shitcoiner_heart:0.36 | `0` | `6` | `-` | `should earnings to he pals, siukbeodmensertslveaarty` |
| `current_mirror_right` | `right` | - | `0` | `0` | `-` | `` |
| `current_mirror_center_x` | `center_x` | - | `0` | `0` | `-` | `` |
| `current_mirror_top` | `top` | - | `0` | `2` | `-` | `should sell` |
| `current_mirror_bottom` | `bottom` | shitcoiner_heart:0.687601 | `1` | `1` | `-` | `siukbeodmensertslveaarty` |
| `current_mirror_center_y` | `center_y` | - | `0` | `0` | `-` | `` |

## Decision

- Frame edges/centerlines do not create a selector from the active quartet.
- Same-layout frame lines touch B4/G5/O5, and current-mirror lines touch O5/O4-adjacent highlight geometry, but the contacts are expected from the already-known frame placement.
- No frame line touches all four active targets, no line creates an ordered `O4/B4/G5/O5` transfer, and no touched words contain hard instruction terms.
- Keep p78 frame edges/centerlines as layout/source-comparison landmarks only; reopen only if source wording names frame edge, centerline, axis, or boundary reading.
