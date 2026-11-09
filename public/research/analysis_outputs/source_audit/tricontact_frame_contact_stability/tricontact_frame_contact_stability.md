# Tri-Contact Frame Contact Stability

Scope: compare p78 frame edge-contact order before and after the dx=-38/-40 tri-contact repair. No key derivation was run.

- Created: `2026-05-20T08:26:00`
- Overlay: `analysis_outputs/source_audit/tricontact_frame_contact_stability/tricontact_frame_contact_stability_overlay.jpg`
- Current vs dx=-38 top-down stable: `True`
- Instruction hits across all streams: `{}`

## Streams

| scenario | event count | top-down compact stream | initials | cut labels | instruction hits |
|---|---:|---|---|---|---|
| `current` | 8 | `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart` | `sepVIcts` | `should sell | earnings | pay off the IMF | I tagged Mike | could sell | trust that guy | shitcoiner at heart` | `{}` |
| `g5_edge_touch_dx_minus_38` | 8 | `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart` | `sepVIcts` | `should sell | earnings | pay off the IMF | I tagged Mike | could sell | trust that guy | shitcoiner at heart` | `{}` |
| `nearest_grid_dx_minus_40` | 8 | `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart` | `sepVIcts` | `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart` | `{}` |
| `best_overlap_dx_minus_160_dy_35` | 8 | `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart` | `sepVIcts` | `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart` | `{}` |

## Contact Deltas

### current

| order | id | label | overlap | primary contact | all contacts |
|---:|---|---|---:|---|---|
| 1 | `should_sell` | should sell | `0.76351` | top cuts 0.0px | left cuts 0.0px; top cuts 0.0px |
| 2 | `earnings` | earnings | `0.93307` | left cuts 0.0px | left cuts 0.0px; top above-adjacent 69.15px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | left left-adjacent 44.51px | left left-adjacent 44.51px |
| 4 | `G5` | Volcano Bonds | `0.0` | left right-adjacent 38.0px | left right-adjacent 38.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | left left-adjacent 24.41px | left left-adjacent 24.41px |
| 6 | `could_sell` | could sell | `1.0` | left left-adjacent 51.54px | left left-adjacent 51.54px |
| 7 | `trust_guy` | trust that guy | `1.0` | left left-adjacent 11.34px | left left-adjacent 11.34px; bottom below-adjacent 78.36px |
| 8 | `O5` | shitcoiner at heart | `0.24754` | bottom cuts 0.0px | left cuts 0.0px; bottom cuts 0.0px |

### g5_edge_touch_dx_minus_38

| order | id | label | overlap | primary contact | all contacts |
|---:|---|---|---:|---|---|
| 1 | `should_sell` | should sell | `0.88581` | top cuts 0.0px | left left-adjacent 5.11px; top cuts 0.0px |
| 2 | `earnings` | earnings | `1.0` | left left-adjacent 26.22px | left left-adjacent 26.22px; top above-adjacent 69.15px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | left left-adjacent 82.51px | left left-adjacent 82.51px |
| 4 | `G5` | Volcano Bonds | `0.0` | left cuts 0.0px | left cuts 0.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | left left-adjacent 62.41px | left left-adjacent 62.41px |
| 6 | `could_sell` | could sell | `1.0` | left left-adjacent 89.54px | left left-adjacent 89.54px |
| 7 | `trust_guy` | trust that guy | `1.0` | left left-adjacent 49.34px | left left-adjacent 49.34px; bottom below-adjacent 78.36px |
| 8 | `O5` | shitcoiner at heart | `0.26957` | bottom cuts 0.0px | left cuts 0.0px; bottom cuts 0.0px |

### nearest_grid_dx_minus_40

| order | id | label | overlap | primary contact | all contacts |
|---:|---|---|---:|---|---|
| 1 | `should_sell` | should sell | `0.88581` | top cuts 0.0px | left left-adjacent 7.11px; top cuts 0.0px |
| 2 | `earnings` | earnings | `1.0` | left left-adjacent 28.22px | left left-adjacent 28.22px; top above-adjacent 69.15px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | left left-adjacent 84.51px | left left-adjacent 84.51px |
| 4 | `G5` | Volcano Bonds | `0.00499` | left cuts 0.0px | left cuts 0.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | left left-adjacent 64.41px | left left-adjacent 64.41px |
| 6 | `could_sell` | could sell | `1.0` | - | - |
| 7 | `trust_guy` | trust that guy | `1.0` | left left-adjacent 51.34px | left left-adjacent 51.34px; bottom below-adjacent 78.36px |
| 8 | `O5` | shitcoiner at heart | `0.27072` | bottom cuts 0.0px | left cuts 0.0px; bottom cuts 0.0px |

### best_overlap_dx_minus_160_dy_35

| order | id | label | overlap | primary contact | all contacts |
|---:|---|---|---:|---|---|
| 1 | `should_sell` | should sell | `0.01321` | top cuts 0.0px | top cuts 0.0px |
| 2 | `earnings` | earnings | `1.0` | top above-adjacent 34.15px | top above-adjacent 34.15px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | - | - |
| 4 | `G5` | Volcano Bonds | `0.30424` | left cuts 0.0px | left cuts 0.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | - | - |
| 6 | `could_sell` | could sell | `1.0` | - | - |
| 7 | `trust_guy` | trust that guy | `1.0` | - | - |
| 8 | `O5` | shitcoiner at heart | `0.94525` | left cuts 0.0px | left cuts 0.0px; bottom below-adjacent 3.0px |

## Assessment

- The exact dx=-38 tri-contact repair preserves the same top-down corridor ladder as the current frame.
- Current compact stream: `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart`.
- dx=-38 compact stream: `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart`.
- The relation changes are geometric, not semantic: #4 words become slightly more edge-adjacent while G5 becomes exact edge contact and O5 remains bottom-clipped.
- No read/take/fold/mirror/word/letter/key instruction appears in the repaired contact streams.
- The heavier dx=-160/dy=35 fit changes contacts more aggressively and remains less source-like because it breaks the M3 tri-contact signature.

## Next Move

- Use dx=-38/-40 as a source-registration acceptance test only. The next high-value move is still obtaining or inspecting a higher-resolution Canva/original-layout image or a physical scan/photo that naturally explains the same contacts.
