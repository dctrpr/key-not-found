# Page 76 Color-Swap Mirror Filter

Scope: test only mirrored highlight contacts where the source and target highlight colors swap, plus the stricter condition that a source page must contain both swap directions. No OCR extraction, hashing, seed checking, WIF checking, address checking, or key derivation was run.

- Created: `2026-05-20T10:00:52`
- Overlay: `analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter_overlay.jpg`
- Strong input edges: `8`
- Color-swap edges: `6`
- Bidirectional color-swap pages: `[79]`

## Page Summary

| source page | swap edges | transitions | targets | bidirectional |
|---:|---:|---|---|---:|
| `77` | `1` | `grey->orange` | `O3` | `False` |
| `79` | `5` | `grey->orange orange->grey` | `G1 G2 O1 O2` | `True` |

## Selected p79 Streams

- `sourceOrderSourceLabels`: `war and violence economy | war and violence economy | That’s right, Bitcoin will take | That’s right, Bitcoin will take | all the energy.` | instruction hits: `['take', 'right']`
- `sourceOrderTargetLabels`: `Bitcoin. | Get some toxicity. Get some bitcoin. Open your heart to | Gotta be this way... post-1971 fiat money | nonsense | Gotta be this way... post-1971 fiat money`
- `targetOrderSourceLabels`: `war and violence economy | war and violence economy | That’s right, Bitcoin will take | all the energy. | That’s right, Bitcoin will take` | instruction hits: `['take', 'right']`
- `targetOrderTargetLabels`: `Get some toxicity. Get some bitcoin. Open your heart to | Bitcoin. | Gotta be this way... post-1971 fiat money | Gotta be this way... post-1971 fiat money | nonsense`
- `scoreOrderTargetLabels`: `Gotta be this way... post-1971 fiat money | Bitcoin. | Gotta be this way... post-1971 fiat money | Get some toxicity. Get some bitcoin. Open your heart to | nonsense`
- `targetIds`: `O1 O2 G1 G1 G2`
- `transitions`: `grey->orange grey->orange orange->grey orange->grey orange->grey`
- `targetInitials`: `GBGGn`
- `sourceInitials`: `wwTTa`

## Selected Edges

- p79 orange `That’s right, Bitcoin will take` -> G1 grey `Gotta be this way... post-1971 fiat money` (source=0.70588, target=0.43081, dist=297.83)
- p79 grey `war and violence economy` -> O2 orange `Bitcoin.` (source=0.12793, target=0.42553, dist=49.04)
- p79 orange `all the energy.` -> G1 grey `Gotta be this way... post-1971 fiat money` (source=0.25758, target=0.05854, dist=420.19)
- p79 grey `war and violence economy` -> O1 orange `Get some toxicity. Get some bitcoin. Open your heart to` (source=0.26581, target=0.11757, dist=565.25)
- p79 orange `That’s right, Bitcoin will take` -> G2 grey `nonsense` (source=0.02223, target=0.06759, dist=508.66)

## Decision

- The color-swap filter is useful as a noise reducer because only p79 has both orange->grey and grey->orange contacts. But the surviving p79 set selects the upper page-76 energy/war/toxicity/fiat-nonsense contrast, not the lower G5/O5 corridor. Its only instruction-term hits are `take` and `right` inside the printed sentence `That’s right, Bitcoin will take`, not procedural commands, so the streams still name no extraction unit.
- This closes color-swap mirroring as a standalone selector under the current scan.

## Next Move

- Keep p79 color-swap as an orientation/concept filter only. Do not derive keys from it unless a future clue points specifically to color swapping, energy/war contrast, or the upper page-76 cluster.
