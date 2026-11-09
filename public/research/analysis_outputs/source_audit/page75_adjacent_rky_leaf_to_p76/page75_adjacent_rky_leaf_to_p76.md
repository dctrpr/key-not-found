# Page-75 Adjacent R-K-Y Leaf Test

Scope: test whether the only adjacent `R-K-Y` style sequence, on page 75, maps onto the repaired page-76 exact-edge trio under physical leaf mirroring. No key derivation was run.

- Created: `2026-05-20T08:37:56`
- Overlay: `analysis_outputs/source_audit/page75_adjacent_rky_leaf_to_p76/page75_adjacent_rky_leaf_to_p76_overlay.jpg`

## Source And Target

| role | style | label | OCR/source text | box |
|---|---|---|---|---|
| page75 source | `R` | epithet / proof of stake / mEthereum lab | `epithet. Now he's slinging proof of stake at the mEthereum lab.` | `[506.66, 2186.99, 1763.36, 2307.5]` |
| page75 source | `K` | Don't fall for shitcoinery. | `Don't fa or shitcoinery.` | `[518.75, 2335.57, 1126.05, 2380.1]` |
| page75 source | `Y` | Keep your dignity. | `Keep your dignity.` | `[484.49, 2408.71, 932.05, 2466.6]` |
| page76 target | `R` | should sell | - | `[1201.11, 2393.42, 1439.33, 2433.53]` |
| page76 target | `K` | Volcano Bonds | - | `[795.0, 2544.0, 1196.0, 2592.0]` |
| page76 target | `Y` | shitcoiner at heart | - | `[1040.0, 2932.0, 1661.0, 2982.0]` |

## Transform Summary

| transform | dx | dy | overlaps | mean distance | max distance | total target overlap |
|---|---:|---:|---:|---:|---:|---:|
| `raw_leaf_hflip` | `0.0` | `0.0` | 0 | `551.7` | `755.9` | `0.0` |
| `prior_leaf_best_dx_0_dy_minus_180` | `0.0` | `-180.0` | 0 | `677.64` | `851.19` | `0.0` |
| `bounded_best_small_translation` | `-180.0` | `180.0` | 1 | `365.2` | `546.93` | `1.0` |
| `unconstrained_centroid_fit` | `-433.37` | `298.58` | 0 | `300.57` | `369.14` | `0.0` |

## Pair Details

### raw_leaf_hflip

| source -> target | distance | hgap | vgap | overlap source | overlap target |
|---|---:|---:|---:|---:|---:|
| `epithet / proof of stake / mEthereum lab` -> `should sell` | `188.45` | `0.0` | `85.92` | `0.0` | `0.0` |
| `Don't fall for shitcoinery.` -> `Volcano Bonds` | `755.9` | `221.95` | `163.9` | `0.0` | `0.0` |
| `Keep your dignity.` -> `shitcoiner at heart` | `710.75` | `0.0` | `465.4` | `0.0` | `0.0` |

### prior_leaf_best_dx_0_dy_minus_180

| source -> target | distance | hgap | vgap | overlap source | overlap target |
|---|---:|---:|---:|---:|---:|
| `epithet / proof of stake / mEthereum lab` -> `should sell` | `357.43` | `0.0` | `265.92` | `0.0` | `0.0` |
| `Don't fall for shitcoinery.` -> `Volcano Bonds` | `824.29` | `221.95` | `343.9` | `0.0` | `0.0` |
| `Keep your dignity.` -> `shitcoiner at heart` | `851.19` | `0.0` | `645.4` | `0.0` | `0.0` |

### bounded_best_small_translation

| source -> target | distance | hgap | vgap | overlap source | overlap target |
|---|---:|---:|---:|---:|---:|
| `epithet / proof of stake / mEthereum lab` -> `should sell` | `92.26` | `0.0` | `0.0` | `0.06309` | `1.0` |
| `Don't fall for shitcoinery.` -> `Volcano Bonds` | `546.93` | `41.95` | `0.0` | `0.0` | `0.0` |
| `Keep your dignity.` -> `shitcoiner at heart` | `456.42` | `0.0` | `285.4` | `0.0` | `0.0` |

### unconstrained_centroid_fit

| source -> target | distance | hgap | vgap | overlap source | overlap target |
|---|---:|---:|---:|---:|---:|
| `epithet / proof of stake / mEthereum lab` -> `should sell` | `369.14` | `0.0` | `52.04` | `0.0` | `0.0` |
| `Don't fall for shitcoinery.` -> `Volcano Bonds` | `305.79` | `0.0` | `42.15` | `0.0` | `0.0` |
| `Keep your dignity.` -> `shitcoiner at heart` | `226.77` | `0.0` | `166.82` | `0.0` | `0.0` |

## Assessment

- The only adjacent R-K-Y style sequence is real, but it does not land on the repaired page-76 exact-edge trio under raw page75->page76 hold-to-light mirroring.
- Raw hflip gives zero overlaps, mean center distance `551.7` px, max `755.9` px.
- The bounded best small translation is dx=`-180.0`, dy=`180.0`, at the edge of the allowed range; it creates only one weak/forced overlap, where the wide page-75 regular group covers `should sell`, while the K and Y groups still miss G5/O5.
- An unconstrained centroid fit would require dx=`-433.37`, dy=`298.58`, which is far outside the previously allowed physical crop-correction range and still does not create a clean human-readable registration.
- Therefore the page-75 adjacent R-K-Y rarity is a typography coincidence/provenance echo, not a physical leaf selector for the p76 repaired exact-edge trio under the current best scan.

## Next Move

- Keep p75 adjacent R-K-Y closed as a leaf selector. Continue using the p76 repaired exact-edge trio plus M3/O5/G5 tri-contact only as a benchmark for new source/physical material.
