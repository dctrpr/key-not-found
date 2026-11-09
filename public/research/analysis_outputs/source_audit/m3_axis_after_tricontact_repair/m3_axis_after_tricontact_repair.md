# M3 Axis After Tri-Contact Repair

Scope: test whether the dx=-38/-40 p78-frame repair changes the M3-axis read into an instruction. No key derivation was run.

- Created: `2026-05-20T08:22:06`
- Source tri-contact report: `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json`
- Overlay: `analysis_outputs/source_audit/m3_axis_after_tricontact_repair/m3_axis_after_tricontact_repair_overlay.jpg`

## Scenario Summary

| scenario | dx/dy | tri-contact | M3 contact | within-frame read | left-continuation reverse | instruction hits |
|---|---:|---|---|---|---|---|
| `current` | `0.0,0.0` | `False` | `True` | `guy that trust` | `Maybe because he's a really trust that guy` | `{}` |
| `g5_edge_touch` | `-38.0,0.0` | `True` | `True` | `guy that trust` | `Maybe because he's a really trust that guy` | `{}` |
| `nearest_grid_dx_-40` | `-40.0,0.0` | `True` | `True` | `guy that trust` | `Maybe because he's a really trust that guy` | `{}` |
| `best_overlap_dx_-160_dy_35` | `-160.0,35.0` | `False` | `False` | `guy that trust really` | `Maybe because he's a really trust that guy` | `{}` |

## Frame Crossings

### current
- right edge: `[2250.0, 2763.33]` near row `31`: bunch to his Wall Street crony pals, but so far he
- left edge: `[1234.0, 2874.64]` near row `32`: hasn't moved on it. I don't really trust that guy.
- within-frame initials: `gtt`
- continuation initials: `gttrahbM`
### g5_edge_touch
- right edge: `[2212.0, 2767.5]` near row `31`: bunch to his Wall Street crony pals, but so far he
- left edge: `[1196.0, 2878.81]` near row `32`: hasn't moved on it. I don't really trust that guy.
- within-frame initials: `gtt`
- continuation initials: `gttrahbM`
### nearest_grid_dx_-40
- right edge: `[2210.0, 2767.71]` near row `31`: bunch to his Wall Street crony pals, but so far he
- left edge: `[1194.0, 2879.02]` near row `32`: hasn't moved on it. I don't really trust that guy.
- within-frame initials: `gtt`
- continuation initials: `gttrahbM`
### best_overlap_dx_-160_dy_35
- right edge: `[2090.0, 2780.86]` near row `31`: bunch to his Wall Street crony pals, but so far he
- left edge: `[1074.0, 2892.17]` near row `32`: hasn't moved on it. I don't really trust that guy.
- within-frame initials: `gttr`
- continuation initials: `gttrahbM`

## Assessment

- The dx=-38 and dx=-40 tri-contact repairs do not materially change the M3 axis read.
- Current within-frame stream is `guy that trust`; dx=-38 is `guy that trust`; dx=-40 is `guy that trust`.
- The left continuation still reconstructs the same local distrust/heart prose: `Maybe because he's a really trust that guy`.
- The corrected frame improves source registration but still does not name a word, letter, line, or key extraction unit.
- The heavier dx=-160/dy=35 fit changes the contact model by breaking M3 as a frame-side mark, so it remains a lower-confidence overlap fit.

## Next Move

- Keep dx=-38/-40 as registration evidence only. Next, test source fidelity against a higher-resolution/original Canva export or physical scan; do not keep reading M3-axis prose as key material.
