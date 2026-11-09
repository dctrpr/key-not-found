# Repaired Exact-Edge Stability Window

Scope: test whether the repaired p78 exact-edge signature is a fragile offset artifact or a stable source-registration benchmark. No key derivation was run.

- Created: `2026-05-20T08:46:24`
- Grid: dx `-80..0`, dy `-20..20`, cells `3321`
- Heatmap: `analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window_heatmap.jpg`
- Target exact signature: `should sell | Volcano Bonds | shitcoiner at heart` / styles `RKY`

## Stability Summary

| condition | count | dx range | dy range |
|---|---:|---|---|
| `targetExact` | 1075 | `-80..-38` | `-4..20` |
| `triContact` | 1599 | `-78..-38` | `-18..20` |
| `targetExactAndTriContact` | 1025 | `-78..-38` | `-4..20` |

## Most Common Exact-Edge Streams

| exact labels | styles | count | example dx/dy | instruction hits |
|---|---|---:|---|---|
| `should sell | Volcano Bonds | shitcoiner at heart` | `RKY` | 1075 | `-80,-4` | `{}` |
| `should sell | shitcoiner at heart` | `RY` | 944 | `-32,-18` | `{}` |
| `Volcano Bonds | shitcoiner at heart` | `KY` | 602 | `-80,-18` | `{}` |
| `should sell | earnings | shitcoiner at heart` | `RRY` | 468 | `-11,-18` | `{}` |
| `Volcano Bonds` | `K` | 86 | `-80,-20` | `{}` |
| `shitcoiner at heart` | `Y` | 70 | `-37,-18` | `{}` |
| `should sell` | `R` | 42 | `-32,-20` | `{}` |
| `should sell | earnings` | `RR` | 24 | `-11,-20` | `{}` |
| `(none)` | `` | 10 | `-37,-20` | `{}` |

## Assessment

- The repaired exact-edge trio is not a single-pixel accident inside the bounded source-like window.
- The same `should sell | Volcano Bonds | shitcoiner at heart` / `R K Y` signature survives across the central overlap of the small dx/dy search window.
- The M3/G5/O5 tri-contact and exact-edge trio overlap in a compact window, so the signature is a usable source-registration benchmark.
- The stable streams still do not name an extraction unit or instruction; this remains calibration evidence, not key material.

## Next Move

- Use this stability window to compare any future Canva/original-layout/physical source. Without new source imagery, move to a different unresolved layer: p80 package copy / dosage counts or original browser/Canva clue inspection.
