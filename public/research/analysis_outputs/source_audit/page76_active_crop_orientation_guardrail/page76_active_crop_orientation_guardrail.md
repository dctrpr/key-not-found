# Page-76 Active Crop Orientation Guardrail

Scope: verify that the completed O4/B4/G5/O5 boxes are in the readable/upright page-76 coordinate frame and document the 180-degree transform needed for native `source_images`. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.

- Created: `2026-05-20T23:53:24`
- Sheet: `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_crop_orientation_guardrail_sheet.jpg`
- Decision: `page76_active_crop_orientation_guardrail_pass_no_selector`

## Summary

- Upright image: `analysis_outputs/3d_article_map/page_76_upright.jpg`
- Native image: `analysis_outputs/source_images/magazine_page_76.jpg`
- Upright/native size: `2544x3264` / `2544x3264`
- Native rotated 180 vs upright mean abs diff: `0.2859`; max diff `31`; nonzero `12.1415%`
- Native direct vs upright mean abs diff: `27.6479`; max diff `255`; nonzero `26.766%`
- All upright boxes in bounds: `True`
- All native-transform boxes in bounds: `True`
- Orientation decision: `use_upright_boxes_after_rot180_for_native_source_images`
- Selector unlocked: `False`

## Target Boxes

| target | upright box | native rot180 box | line/corridor |
|---|---|---|---|
| `O4 buying the dip` | `[1334, 2177, 1801, 2225]` | `[743, 1039, 1210, 1087]` | `L22/C4` |
| `B4 $1 billion` | `[428, 2398, 691, 2445]` | `[1853, 819, 2116, 866]` | `L25/C7` |
| `G5 Volcano Bonds` | `[795, 2544, 1196, 2592]` | `[1348, 672, 1749, 720]` | `L27/C9` |
| `O5 shitcoiner at heart` | `[1040, 2932, 1661, 2982]` | `[883, 282, 1504, 332]` | `L32/C14` |

## Overlays

- Upright overlay: `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_targets_upright_overlay.jpg`
- Native source overlay: `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_targets_native_overlay.jpg`
- Native rotated-180 overlay: `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_targets_rot180_overlay.jpg`

## Next Move

- For any future source comparison, first normalize orientation to the readable/upright frame or transform O4/B4/G5/O5 boxes with the recorded 180-degree formula. R3 unit/order evidence is still required before extraction.
