# P78 Frame Gap-Repair Selector

Scope: test whether the smallest trusted-G5 gap repair turns the p78 frame into a clean selector. No key derivation was run.

- Created: `2026-05-20T07:24:40`
- Overlay: `analysis_outputs/source_audit/p78_frame_gap_repair_selector/p78_frame_gap_repair_selector_overlay.jpg`

## current

- Frame: `[1234.0, 2398.0, 2250.0, 2950.0]`
- Event count: `8`
- `topDownLabels` hits=none: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `topDownInitials` hits=none: `sepVIcts`
- `topDownLasts` hits=none: `lsFselyt`
- `cutLabels` hits=none: `should sell | earnings | pay off the IMF | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `cutInitials` hits=none: `sepIcts`
- `cutLasts` hits=none: `lsFelyt`
- `minimalCornerLike` hits=none: `should sell | Volcano Bonds | shitcoiner at heart`

| order | id | label | overlap | contacts |
|---:|---|---|---:|---|
| 1 | `should_sell` | should sell | `0.76351` | left cuts 0.0px; top cuts 0.0px |
| 2 | `earnings` | earnings | `0.93307` | left cuts 0.0px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | left left-adjacent 44.51px |
| 4 | `G5` | Volcano Bonds | `0.0` | left right-adjacent 38.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | left left-adjacent 24.41px |
| 6 | `could_sell` | could sell | `1.0` | left left-adjacent 51.54px |
| 7 | `trust_guy` | trust that guy | `1.0` | left left-adjacent 11.34px |
| 8 | `O5` | shitcoiner at heart | `0.24754` | left cuts 0.0px; bottom cuts 0.0px |

## nearest_g5_touch_dx_minus_40

- Frame: `[1194.0, 2398.0, 2210.0, 2950.0]`
- Event count: `8`
- `topDownLabels` hits=none: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `topDownInitials` hits=none: `sepVIcts`
- `topDownLasts` hits=none: `lsFselyt`
- `cutLabels` hits=none: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `cutInitials` hits=none: `sepVIcts`
- `cutLasts` hits=none: `lsFselyt`
- `minimalCornerLike` hits=none: `should sell | Volcano Bonds | shitcoiner at heart`

| order | id | label | overlap | contacts |
|---:|---|---|---:|---|
| 1 | `should_sell` | should sell | `0.88581` | left left-adjacent 7.11px; top cuts 0.0px |
| 2 | `earnings` | earnings | `1.0` | left left-adjacent 28.22px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | - |
| 4 | `G5` | Volcano Bonds | `0.00499` | left cuts 0.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | - |
| 6 | `could_sell` | could sell | `1.0` | - |
| 7 | `trust_guy` | trust that guy | `1.0` | left left-adjacent 51.34px |
| 8 | `O5` | shitcoiner at heart | `0.27072` | left cuts 0.0px; bottom cuts 0.0px |

## heavy_best_overlap_dx_minus_160_dy_35

- Frame: `[1074.0, 2433.0, 2090.0, 2985.0]`
- Event count: `8`
- `topDownLabels` hits=none: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `topDownInitials` hits=none: `sepVIcts`
- `topDownLasts` hits=none: `lsFselyt`
- `cutLabels` hits=none: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `cutInitials` hits=none: `sepVIcts`
- `cutLasts` hits=none: `lsFselyt`
- `minimalCornerLike` hits=none: `should sell | Volcano Bonds | shitcoiner at heart`

| order | id | label | overlap | contacts |
|---:|---|---|---:|---|
| 1 | `should_sell` | should sell | `0.01321` | top cuts 0.0px |
| 2 | `earnings` | earnings | `1.0` | top above-adjacent 34.15px |
| 3 | `pay_imf` | pay off the IMF | `1.0` | - |
| 4 | `G5` | Volcano Bonds | `0.30424` | left cuts 0.0px |
| 5 | `tagged_mike` | I tagged Mike | `1.0` | - |
| 6 | `could_sell` | could sell | `1.0` | - |
| 7 | `trust_guy` | trust that guy | `1.0` | - |
| 8 | `O5` | shitcoiner at heart | `0.94525` | left cuts 0.0px; bottom below-adjacent 3.0px |

## Assessment

- The smallest G5-gap repair (dx=-40) makes trusted G5 a true frame cut but does not create an instruction stream.
- The repaired top-down stream remains corridor prose: should sell, earnings, G5, pay/IMF, tagged Mike, could sell, trust guy, O5.
- The repair changes geometry confidence, not extraction semantics; it still does not name word/letter/line/key/mirror.
- A heavier shift can increase overlaps, but that is arbitrary local fitting and should not be promoted without an external source transform.

## Next Move

- Close the local p78-frame gap-repair selector. Use dx=-40 only as a validation signature for a new source/physical registration, not as an extraction rule.
