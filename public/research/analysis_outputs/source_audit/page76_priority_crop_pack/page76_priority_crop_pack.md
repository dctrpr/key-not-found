# Page 76 Priority Crop Pack

> Orientation note: this crop pack is rendered from the readable/upright 3D layer. The current `source_images` / embedded PDF pages are the same scan in native upside-down orientation, so rotate them 180 degrees before comparing them to these crop coordinates. A corrected source-fidelity audit confirms this crop pack is source-faithful after that transform.

Scope: create high-res visual baselines for the current page-76 priority targets. No key derivation, hashing, seed phrases, WIF checks, OCR extraction, or address checks were run.

- Created: `2026-05-20T09:39:26`
- Source image: `analysis_outputs/3d_article_map/page_76_upright.jpg`
- Contact sheet: `analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg`

## Target Priority

- Primary: L32/O5 `Maybe because he's a shitcoiner at heart.`.
- Pair: L27/G5 `collateralized “Volcano Bonds” to pay off the IMF`.
- Broad source band: L26-L29 around `billions worth of future bitcoin earnings`.

## Crops

### Primary O5 / L32
- id: `L32_O5_primary`
- line: `32`
- text: `Maybe because he's a shitcoiner at heart.`
- crop: `[850, 2860, 1770, 3038]`
- output: `analysis_outputs/source_audit/page76_priority_crop_pack/L32_O5_primary.jpg`

### Paired G5 / L27
- id: `L27_G5_pair`
- line: `27`
- text: `collateralized Volcano Bonds to pay off the IMF`
- crop: `[720, 2505, 1650, 2625]`
- output: `analysis_outputs/source_audit/page76_priority_crop_pack/L27_G5_pair.jpg`

### Frame Top / L25
- id: `L25_should_sell`
- line: `25`
- text: `$1 billion in bitcoin - that he should sell`
- crop: `[720, 2355, 1515, 2455]`
- output: `analysis_outputs/source_audit/page76_priority_crop_pack/L25_should_sell.jpg`

### Broad p78 Source Band / L26-L29
- id: `L26_L29_source_band`
- line: `26-29`
- text: `earnings / Volcano Bonds / Mike / could sell band`
- crop: `[720, 2440, 1685, 2745]`
- output: `analysis_outputs/source_audit/page76_priority_crop_pack/L26_L29_source_band.jpg`

### Full Frame Context / L25-L32
- id: `L25_L32_frame_context`
- line: `25-32`
- text: `should sell -> Volcano Bonds -> shitcoiner at heart`
- crop: `[720, 2350, 1750, 3045]`
- output: `analysis_outputs/source_audit/page76_priority_crop_pack/L25_L32_frame_context.jpg`

## Assessment

- The crop pack turns the current line priority into a repeatable visual baseline.
- It does not solve the selector gap. Use it only to compare future source/original-layout/physical imagery.
- The p78 reflected frame edges are drawn in cyan where they intersect each crop, so a new source can be tested against the same O5/G5/frame signature.

## Next Move

- If a new source appears, compare O5/L32 first, G5/L27 second, and then the L26-L29 band. Require a named extraction unit before key checks resume.
