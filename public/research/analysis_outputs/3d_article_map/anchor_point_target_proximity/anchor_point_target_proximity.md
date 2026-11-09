# 3D Anchor Point Target Proximity

Scope: check whether 3D page-76 anchor points directly select the locked O4/B4/G5/O5 page-76 targets. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T20:57:29`
- Page-76 anchors checked: `11`
- Anchors inside active targets: `0`
- Anchors within 50 px of active targets: `0`
- Overlay: `analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity_overlay.jpg`

## Anchor Proximity

| anchor | source | point | nearest target | distance | nearest word | word distance | instruction hits |
|---|---|---|---|---:|---|---:|---|
| `p79_pill_1_mirror` | `page79-mirrored-onto-page76` | `[2373.0, 2408.0]` | `buying_dip` (diagonal_gap) | 639.45 | `Bitcoin` | 531.18 | - |
| `p79_pill_2_mirror` | `page79-mirrored-onto-page76` | `[2122.5, 2454.5]` | `buying_dip` (diagonal_gap) | 428.51 | `Twitter?` | 541.08 | - |
| `p79_pill_3_mirror` | `page79-mirrored-onto-page76` | `[1938.0, 2608.5]` | `buying_dip` (diagonal_gap) | 421.89 | `IMF` | 367.52 | - |
| `p79_pill_4_mirror` | `page79-mirrored-onto-page76` | `[2107.0, 2780.5]` | `shitcoiner_heart` (diagonal_gap) | 471.03 | `he` | 542.69 | - |
| `p79_pill_5_mirror` | `page79-mirrored-onto-page76` | `[2360.5, 2968.0]` | `shitcoiner_heart` (horizontal_gap) | 699.5 | `he` | 818.33 | - |
| `p76_x_mark` | `page76-or-page79-mirrored` | `[2358.5, 2751.5]` | `shitcoiner_heart` (diagonal_gap) | 720.48 | `he` | 794.66 | - |
| `p76_dollar` | `page76-or-page79-mirrored` | `[1973.5, 3092.0]` | `shitcoiner_heart` (diagonal_gap) | 331.29 | `guy` | 506.71 | - |
| `p76_black_bar_1` | `page76-or-page79-mirrored` | `[1972.0, 859.5]` | `buying_dip` (diagonal_gap) | 1317.67 | `flat` | 18.53 | - |
| `p76_black_bar_2` | `page76-or-page79-mirrored` | `[1794.0, 1518.5]` | `buying_dip` (diagonal_gap) | 642.4 | `chest.` | 79.15 | - |
| `p76_wire_left_knot` | `page76-or-page79-mirrored` | `[1985.0, 132.0]` | `buying_dip` (diagonal_gap) | 2040.44 | `OVERDOSE` | 238.95 | - |
| `p76_wire_right_knot` | `page76-or-page79-mirrored` | `[2410.0, 327.0]` | `buying_dip` (diagonal_gap) | 1944.84 | `OVERDOSE` | 246.48 | - |

## Streams

- `page79-mirrored-onto-page76:nearestTargetIds` hits=none: `buying_dip buying_dip buying_dip shitcoiner_heart shitcoiner_heart`
- `page79-mirrored-onto-page76:nearestWords` hits=none: `Bitcoin | Twitter? | IMF | he | he`
- `page79-mirrored-onto-page76:nearestDistances` hits=none: `639.45 428.51 421.89 471.03 699.5`
- `page76-or-page79-mirrored:nearestTargetIds` hits=none: `buying_dip buying_dip shitcoiner_heart buying_dip buying_dip shitcoiner_heart`
- `page76-or-page79-mirrored:nearestWords` hits=none: `flat | chest. | guy | OVERDOSE | OVERDOSE | he`
- `page76-or-page79-mirrored:nearestDistances` hits=none: `1317.67 642.4 331.29 2040.44 1944.84 720.48`

## Findings

- No page-76 3D anchor point lands inside any locked O4/B4/G5/O5 active target box.
- No anchor point is within 50 px of an active target; the closest overall is `p76_dollar` to O5 at 331.29 px, and the closest mirrored-pill anchor is p79 pill 3 to O4 at 421.89 px, so the anchor layer is spatially separate from the active text anchors.
- Nearest-word streams around the anchor points are ordinary OCR/navigation labels in the art/right-side field, not extraction instructions.
- The anchor sequence therefore supports orientation and ray construction only; it does not provide a point-to-target order or unit.

## Decision

- Do not treat 3D anchor points as direct selectors into O4/B4/G5/O5 under the current scan.
- Next move: Keep using anchors only as orientation/provenance aids unless a future source transform moves them onto active target text or a clue names a specific anchor order.
