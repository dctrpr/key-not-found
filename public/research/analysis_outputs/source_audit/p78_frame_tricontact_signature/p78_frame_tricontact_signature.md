# P78 Frame Tri-Contact Signature

Scope: test whether the p78 reflected frame can simultaneously explain trusted G5, O5, and M3 contacts under the smallest G5 repair. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T08:14:47`
- Overlay: `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg`
- Base frame: `[1234.0, 2398.0, 2250.0, 2950.0]`
- Edge-touch dx: `-38.0`

## Scenario Metrics

| scenario | dx | dy | G5 edge gap/overlap | G5 overlap | M3 right-edge cut | M3 axis in mark | O5 bottom cut width | O5 overlap | tri-contact |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| `current` | `0.0` | `0.0` | `38.0` | `0.0` | `265.0` | `True` | `427.0` | `0.24754` | `False` |
| `g5_edge_touch` | `-38.0` | `0.0` | `0.0` | `0.0` | `265.0` | `True` | `465.0` | `0.26957` | `True` |
| `nearest_grid_dx_-40` | `-40.0` | `0.0` | `-2.0` | `0.00499` | `265.0` | `True` | `467.0` | `0.27072` | `True` |
| `best_overlap_dx_-160_dy_35` | `-160.0` | `35.0` | `-122.0` | `0.30424` | `0.0` | `False` | `0.0` | `0.94525` | `False` |

## Assessment

- The G5 repair is not just an arbitrary loose shift: the exact edge-touch shift is dx=-38, matching the previously observed ~40px repair.
- At dx=-38, the frame's left edge touches trusted G5, the right edge still cuts M3 with the full vertical mark overlap, and the bottom edge still clips O5.
- The heavier best-overlap shift dx=-160, dy=35 improves G5/O5 area overlap but breaks the M3 right-edge contact, so it looks less source-like.
- This promotes dx≈-38/-40 as a three-object source-registration signature, not as an extraction rule.
- No word, letter, line, or key unit is created by this contact geometry.

## Next Best Move

- Use dx≈-38/-40 as a source-registration validation signature for any new scan/source image. Do not read it as key material unless a source clue names the extraction unit.
