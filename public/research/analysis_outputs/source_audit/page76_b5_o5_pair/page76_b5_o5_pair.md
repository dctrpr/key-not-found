# Page 76 B5/O5 Pair Drilldown

Scope: inspect the single page-76 self-mirror pair found by the previous audit. No key candidates are generated.

- Axis: `orange_bbox_center`
- Crop: `analysis_outputs/source_audit/page76_b5_o5_pair/page76_b5_o5_pair_crop.jpg`

## Pair Coverage

### B5 -> O5

- Source: `Volcano Bonds`
- Target: `shitcoiner at heart.`
- Overlap: source `0.593`, target `0.908`, center distance `63.5px`
- Source original x-span estimate: `[0.0, 0.8896]` -> `Volcano Bond` (omits right approx `s`)
- Target x-span estimate: `[0.0, 0.9082]` -> `shitcoiner at heart` (omits right approx `.`)

### O5 -> B5

- Source: `shitcoiner at heart.`
- Target: `Volcano Bonds`
- Overlap: source `0.908`, target `0.593`, center distance `63.5px`
- Source original x-span estimate: `[0.0, 0.9082]` -> `shitcoiner at heart` (omits right approx `.`)
- Target x-span estimate: `[0.0, 0.8896]` -> `Volcano Bond` (omits right approx `s`)

## Canonical Page-76 Corridor

- line `9`: have dulled shitcoiners' and nocoiners' minds.
- line `21`: trolling the International Monetary Fund (IMF) on Twitter?  
- line `27`: collateralized “Volcano Bonds” to pay off the IMF  
- line `29`: Novogratz in the tweet, figuring he could sell a  
- line `32`: Maybe because he's a shitcoiner at heart.

## Assessment

- This pair does not provide a precise word or letter selector. The horizontal overlap covers nearly the whole phrase on both sides.
- The most defensible reading is semantic/registration: `Volcano Bonds` is being paired with `shitcoiner at heart` inside the El Salvador/IMF corridor.
- Keep this as a low-parameter anchor, but do not derive keys from it directly.

## Next Best Move

- Use this pair only if a source/provenance rule from p73/p79/p80 or a physical registration step says how to extract from the page-76 lower corridor.
