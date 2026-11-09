# Current Scan Page-76 Image Witness State Stability Gate

Scope: bounded current-scan/PDF image-witness stability control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.

- Created: `2026-05-24T13:19:34`
- Full-page image candidates checked: `26`
- Exact page-76 witnesses: `3`
- Stable exact witnesses: `3`
- Near page-76 controls: `9`
- Hidden changed-state witness candidates: `0`
- Exact witness max active-crop diff: `6.455416`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `images=26|exact=3|stableExact=3|near=9|hiddenChanged=0|exactMaxDiff=6.455|sourceR3=0|triggers=0/9|selectors=0`

## Witness Rows

| path | class | orientation | MAD | state | color | slot | max crop diff |
|---|---|---|---|---|---|---|---|
| `analysis_outputs/3d_article_map/page_76_upright.jpg` | `exact_page76_witness` | `already_upright` | `0.0` | `YKKY` | `OBBO` | `OVED` | `0.0` |
| `analysis_outputs/source_images/magazine_page_76.jpg` | `exact_page76_witness` | `rot180_to_upright` | `0.054238` | `YKKY` | `OBBO` | `OVED` | `2.979356` |
| `magazine-4_1.jpg` | `exact_page76_witness` | `rot180_to_upright` | `0.092986` | `YKKY` | `OBBO` | `OVED` | `6.455416` |
| `fold_76_78.png` | `near_page76_control` | `already_upright` | `15.806295` | `YNNY` | `ONNO` | `OVED` | `96.008728` |
| `fold_75_79.png` | `near_page76_control` | `already_upright` | `23.393657` | `YYNN` | `OONN` | `OVED` | `167.639725` |
| `analysis_outputs/source_images/magazine_page_79.jpg` | `near_page76_control` | `rot180_to_upright` | `25.089723` | `NNNN` | `NNNN` | `OVED` | `177.59726` |
| `analysis_outputs/3d_article_map/page_79_upright.jpg` | `near_page76_control` | `already_upright` | `25.093235` | `NNNN` | `NNNN` | `OVED` | `177.596375` |
| `magazine-3_1.jpg` | `near_page76_control` | `rot180_to_upright` | `25.281966` | `YYNN` | `OONN` | `OVED` | `162.377213` |
| `analysis_outputs/source_images/magazine_page_75.jpg` | `near_page76_control` | `rot180_to_upright` | `25.289539` | `YYNN` | `OONN` | `OVED` | `162.268814` |
| `analysis_outputs/3d_article_map/page_75_upright.jpg` | `near_page76_control` | `already_upright` | `25.297172` | `YYNN` | `OONN` | `OVED` | `162.142456` |
| `analysis_outputs/source_images/magazine_page_78.jpg` | `near_page76_control` | `already_upright` | `29.435853` | `NNNN` | `NNNN` | `OVED` | `158.99115` |
| `analysis_outputs/3d_article_map/page_78_upright.jpg` | `near_page76_control` | `rot180_to_upright` | `29.441695` | `NNNN` | `NNNN` | `OVED` | `158.900436` |
| `keyser bitcoin -3_1.jpg` | `not_page76` | `already_upright` | `47.476292` | `NNNN` | `NNNN` | `OVED` | `153.62114` |
| `magazine-1_1.jpg` | `not_page76` | `rot180_to_upright` | `50.878193` | `KNNN` | `BNNN` | `OVED` | `175.199356` |
| `keyser bitcoin -7_1.jpg` | `not_page76` | `already_upright` | `51.039128` | `NNNN` | `NNNN` | `OVED` | `149.966675` |
| `keyser bitcoin -4_1.jpg` | `not_page76` | `already_upright` | `54.822504` | `NNNN` | `NNNN` | `OVED` | `150.473389` |
| `keyser bitcoin -6_1.jpg` | `not_page76` | `rot180_to_upright` | `56.667892` | `NNNN` | `NNNN` | `OVED` | `159.675522` |

## Decision

- current_page76_image_witnesses_are_stable_raster_duplicates.
- Reason: All exact page-76 image witnesses preserve the active YKKY/OBBO/OVED state and slot streams after orientation normalization. No local image witness changes active-box state or supplies source-backed R3 wording.
- Next move: Keep exact page-76 image witnesses as duplicate raster validation only; reopen source review only for a distinct physical/original-layout asset or raw clue wording that satisfies a source-reopen trigger.

Sheet: `analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate/current_scan_page76_image_witness_state_stability_gate_sheet.jpg`
