# Page-75 R-K-Y Reflection Selection

Scope: check whether page79->page75 reflected-highlight boxes select the unique adjacent page-75 `R-K-Y` style run. No key derivation was run.

- Created: `2026-05-20T08:41:47`
- Overlay: `analysis_outputs/source_audit/page75_rky_reflection_selection/page75_rky_reflection_selection_overlay.jpg`
- Direct overlap total: `0`
- Near-miss total: `1`

## R-K-Y Groups

| style | label | OCR text | box | direct overlaps | near misses | nearest reflected box |
|---|---|---|---|---:|---:|---|
| `R` | epithet / proof of stake / mEthereum lab | `epithet. Now he's slinging proof of stake at the mEthereum lab.` | `[506.66, 2186.99, 1763.36, 2307.5]` | 0 | 1 | `79_75_5` gap h/v `0.0/35.62` text `only the language of the shameless opportunists trying cash in by riding Bitcoin` |
| `K` | Don't fall for shitcoinery. | `Don't fa or shitcoinery.` | `[518.75, 2335.57, 1126.05, 2380.1]` | 0 | 0 | `79_75_5` gap h/v `0.0/184.2` text `only the language of the shameless opportunists trying cash in by riding Bitcoin` |
| `Y` | Keep your dignity. | `Keep your dignity.` | `[484.49, 2408.71, 932.05, 2466.6]` | 0 | 0 | `79_75_5` gap h/v `0.0/257.34` text `only the language of the shameless opportunists trying cash in by riding Bitcoin` |

## Best Checks

### R epithet / proof of stake / mEthereum lab

| reflection | overlap group | overlap reflection | hgap | vgap | distance | text |
|---|---:|---:|---:|---:|---:|---|
| `79_75_5` | `0.0` | `0.0` | `0.0` | `35.62` | `177.35` | `only the language of the shameless opportunists trying cash in by riding Bitcoins coattail` |
| `79_75_4` | `0.0` | `0.0` | `0.0` | `116.01` | `241.75` | `It's only the language of the shameless opportunists trying` |
| `79_75_8` | `0.0` | `0.0` | `178.88` | `269.68` | `909.53` | `` |
| `79_75_7` | `0.0` | `0.0` | `361.54` | `126.49` | `1044.72` | `` |
| `79_75_6` | `0.0` | `0.0` | `626.08` | `73.73` | `1289.43` | `` |

### K Don't fall for shitcoinery.

| reflection | overlap group | overlap reflection | hgap | vgap | distance | text |
|---|---:|---:|---:|---:|---:|---|
| `79_75_5` | `0.0` | `0.0` | `0.0` | `184.2` | `492.57` | `only the language of the shameless opportunists trying cash in by riding Bitcoins coattail` |
| `79_75_4` | `0.0` | `0.0` | `0.0` | `264.59` | `535.44` | `It's only the language of the shameless opportunists trying` |
| `79_75_8` | `0.0` | `0.0` | `816.19` | `197.08` | `1174.5` | `` |
| `79_75_7` | `0.0` | `0.0` | `998.85` | `53.89` | `1339.62` | `` |
| `79_75_6` | `0.0` | `0.0` | `1263.39` | `1.13` | `1592.03` | `` |

### Y Keep your dignity.

| reflection | overlap group | overlap reflection | hgap | vgap | distance | text |
|---|---:|---:|---:|---:|---:|---|
| `79_75_5` | `0.0` | `0.0` | `0.0` | `257.34` | `631.44` | `only the language of the shameless opportunists trying cash in by riding Bitcoins coattail` |
| `79_75_4` | `0.0` | `0.0` | `0.0` | `337.73` | `674.63` | `It's only the language of the shameless opportunists trying` |
| `79_75_8` | `0.0` | `0.0` | `1010.19` | `110.58` | `1273.13` | `` |
| `79_75_7` | `0.0` | `0.0` | `1192.85` | `0.0` | `1450.15` | `` |
| `79_75_6` | `0.0` | `0.0` | `1457.39` | `0.0` | `1705.25` | `` |

## Assessment

- The page79->page75 reflected-highlight system does not directly select the unique page-75 adjacent R-K-Y run.
- Direct overlaps across the three R-K-Y groups: `0`.
- Near misses across the three R-K-Y groups: `1`; the only meaningful near miss is the regular R group sitting just below reflection `79_75_5`.
- That nearest reflected box selects earlier prose (`only the language of the shameless opportunists trying cash in by riding Bitcoins coattail`), not the `epithet/proof-of-stake` R group itself.
- K (`Don't fall for shitcoinery`) and Y (`Keep your dignity`) are not selected by the page79->page75 reflection boxes.

## Next Move

- Close the unique page-75 R-K-Y run as mirror-selected evidence under the current map. Keep focus on the p76 repaired exact-edge trio and source/physical validation.
