# Priority Crop Pack Source-Fidelity Audit

Scope: compare the existing page-76 priority crop pack against the current source scan. No OCR extraction, key derivation, seed, WIF, or address checks were run.

- Created: `2026-05-20T11:41:04`
- Existing crop-pack source: `analysis_outputs/3d_article_map/page_76_upright.jpg`
- Current source image: `analysis_outputs/source_images/magazine_page_76.jpg`
- Current source transform: `rotate180`
- Comparison/source-render sheet: `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/priority_crop_pack_source_fidelity_sheet.jpg`
- Any high 3D-vs-source crop difference after transform: `False`
- Raw RMS range: `1.132865` to `2.070533`

## Crop Differences

| crop | old source | current source-rendered output | raw RMS | raw max | assessment |
|---|---|---|---:|---:|---|
| `L32_O5_primary` | `analysis_outputs/source_audit/page76_priority_crop_pack/L32_O5_primary.jpg` | `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/L32_O5_primary_source.jpg` | `2.070533` | `25` | source-faithful after rotate180 |
| `L27_G5_pair` | `analysis_outputs/source_audit/page76_priority_crop_pack/L27_G5_pair.jpg` | `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/L27_G5_pair_source.jpg` | `1.132865` | `15` | source-faithful after rotate180 |
| `L25_should_sell` | `analysis_outputs/source_audit/page76_priority_crop_pack/L25_should_sell.jpg` | `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/L25_should_sell_source.jpg` | `1.183482` | `12` | source-faithful after rotate180 |
| `L26_L29_source_band` | `analysis_outputs/source_audit/page76_priority_crop_pack/L26_L29_source_band.jpg` | `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/L26_L29_source_band_source.jpg` | `1.267788` | `15` | source-faithful after rotate180 |
| `L25_L32_frame_context` | `analysis_outputs/source_audit/page76_priority_crop_pack/L25_L32_frame_context.jpg` | `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/L25_L32_frame_context_source.jpg` | `1.461144` | `25` | source-faithful after rotate180 |

## Assessment

- The existing priority crop pack was rendered from the 3D upright image layer.
- After rotating the native source image 180 degrees into readable orientation, the same crop windows visually match the 3D upright layer at JPEG-resave tolerance.
- The earlier stale-crop conclusion was caused by comparing readable-upright crop coordinates against native upside-down source coordinates.
- The old crop pack remains valid as readable-orientation geometry, provided future source comparisons apply the same 180-degree source transform.

## Next Move

- For future source comparisons, rotate source_images/fresh PDF extraction 180 degrees before applying existing upright page-76 crop coordinates.
