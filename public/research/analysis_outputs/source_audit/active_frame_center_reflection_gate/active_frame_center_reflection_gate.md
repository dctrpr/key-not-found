# Active Frame-Center Reflection Gate

Scope: project locked O4/B4/G5/O5 boxes through p78 same-layout and current-mirror frame centers using point reflection, vertical-axis reflection, and horizontal-axis reflection. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:25:00`
- Same-layout frame center: `[802.0, 2674.0]`
- Current-mirror frame center: `[1742.0, 2674.0]`
- Total scenarios: `6`
- Total projections: `24`
- In-bounds projections: `22`
- Hard instruction hits: `0`
- Active-target re-hits: `2` total, `0` strong
- Max active-target re-hit overlap: `0.198042`
- Sheet: `analysis_outputs/source_audit/active_frame_center_reflection_gate/active_frame_center_reflection_gate_sheet.jpg`

## Scenario Summary

| scenario | in bounds | projections with words | projections with highlights | active target re-hits | instruction hits |
|---|---:|---:|---:|---:|---|
| `same_layout_point` | `4` | `2` | `1` | `2` | `-` |
| `same_layout_vertical_axis` | `4` | `3` | `0` | `0` | `-` |
| `same_layout_horizontal_axis` | `4` | `3` | `0` | `0` | `-` |
| `current_mirror_point` | `3` | `0` | `0` | `0` | `-` |
| `current_mirror_vertical_axis` | `3` | `0` | `1` | `0` | `-` |
| `current_mirror_horizontal_axis` | `4` | `3` | `0` | `0` | `-` |

## Landing Previews

### same_layout_point
- `one_billion` -> `he's a`
- `volcano_bonds` -> `bunch to his Wall`

### same_layout_vertical_axis
- `one_billion` -> `— that he`
- `volcano_bonds` -> `collateralized`
- `shitcoiner_heart` -> `Maybe`

### same_layout_horizontal_axis
- `one_billion` -> `Maybe`
- `volcano_bonds` -> `Wall Street crony`
- `shitcoiner_heart` -> `that he should sell`

### current_mirror_horizontal_axis
- `one_billion` -> `Maybe`
- `volcano_bonds` -> `Wall Street crony`
- `shitcoiner_heart` -> `that he should sell`

## Decision

- Frame-center reflection does not create a selector from O4/B4/G5/O5.
- The projections either land off-page, on ordinary body prose, or on non-instructional highlight/active geometry.
- The only active-target re-hits are weak partial B4/O5 contacts under same-layout point reflection; the maximum overlap is `0.198042`, below a usable target-transfer threshold.
- No hard instruction term and no strong active-target re-hit was produced across all six bounded reflection modes.
- Keep p78 frame centers as source-comparison landmarks only; reopen only if source wording names center reflection, frame-center axis, or same-slot frame flipping.
