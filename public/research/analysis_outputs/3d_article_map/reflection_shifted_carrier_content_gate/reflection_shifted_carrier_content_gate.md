# 3D Reflection Shifted Carrier Content Gate

Scope: inspect the three reflected page-76 carriers that can touch O4/B4/G5/O5 after integer line-pitch shifts. This reads existing 3D-map OCR boxes only; no new OCR, extraction, hashes, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T04:51:40`
- Sheet: `analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate/reflection_shifted_carrier_content_gate_sheet.jpg`
- Carriers: `3`
- Shifted active slices: `12`
- Active page-line gaps: `[3, 2, 5]`
- Common carrier shift-gap patterns: `[[3, 2, 5]]`
- Inferred base lines: `[20, 21]`
- Strict instruction hits: `0`
- Target-phrase isolated slices: `0`

## Carrier Phase

| carrier | carrier text | base line | shifts | shift gaps | page-line gaps match? | slice word counts | non-target word counts |
|---|---|---:|---|---|---|---|---|
| `78_76_4` | Have you seen the president of El Salvador | `20` | `[2, 5, 7, 12]` | `[3, 2, 5]` | `True` | `[7, 8, 6, 5]` | `[6, 7, 6, 4]` |
| `79_76_4` | Have you seen the president of El Salvador | `20` | `[2, 5, 7, 12]` | `[3, 2, 5]` | `True` | `[7, 8, 6, 5]` | `[6, 7, 6, 4]` |
| `79_76_5` | trolling the International Monetary Fund (IMF) on Twitter? taunting them, telling them he's ByiiREeraipy" | `21` | `[1, 4, 6, 11]` | `[3, 2, 5]` | `True` | `[7, 8, 6, 5]` | `[6, 7, 6, 4]` |

## Shifted Slices

| carrier | target | shift | overlap | words | non-target words | instruction hits | slice text |
|---|---|---:|---:|---:|---:|---|---|
| `78_76_4` | `buying_dip` | `2` | `0.439931` | `7` | `6` | - | He's taunting them, telling them he's ByiiREeraipy" |
| `78_76_4` | `one_billion` | `5` | `0.730638` | `8` | `7` | - | eis in bitcoin — that he should sell |
| `78_76_4` | `volcano_bonds` | `7` | `0.745833` | `6` | `6` | - | collateralized to pay off the IMF |
| `78_76_4` | `shitcoiner_heart` | `12` | `0.308746` | `5` | `4` | - | Maybe because he's a siukbeodmensertslveaarty |
| `79_76_4` | `buying_dip` | `2` | `1.0` | `7` | `6` | - | He's taunting them, telling them he's ByiiREeraipy" |
| `79_76_4` | `one_billion` | `5` | `0.694639` | `8` | `7` | - | eis in bitcoin — that he should sell |
| `79_76_4` | `volcano_bonds` | `7` | `1.0` | `6` | `6` | - | collateralized to pay off the IMF |
| `79_76_4` | `shitcoiner_heart` | `12` | `0.9828` | `5` | `4` | - | Maybe because he's a siukbeodmensertslveaarty |
| `79_76_5` | `buying_dip` | `1` | `1.0` | `7` | `6` | - | He's taunting them, telling them he's ByiiREeraipy" |
| `79_76_5` | `one_billion` | `4` | `0.694639` | `8` | `7` | - | eis in bitcoin — that he should sell |
| `79_76_5` | `volcano_bonds` | `6` | `1.0` | `6` | `6` | - | collateralized to pay off the IMF |
| `79_76_5` | `shitcoiner_heart` | `11` | `1.0` | `5` | `4` | - | Maybe because he's a siukbeodmensertslveaarty |

## Findings

- The all-four reflected carriers infer ordinary base rows L20/L21; the active shift gaps match page-line gaps 3/2/5 because the operation is walking article rows by line pitch.
- None of the shifted slices isolates a target phrase: every active slice carries surrounding row prose, and the 12 slices include more non-target words than target-box OCR words.
- The shifted slice text and the carrier text contain 0 strict instruction terms.
- The 3D OCR in these shifted slices is not text authority: the trusted G5 target is geometrically hit, but its target phrase is not recovered as clean OCR text inside the slices.
- This keeps reflected carriers useful as orientation/row-registration evidence only, not as a source-backed unit/order selector.

## Decision

- shifted_carriers_are_row_context_not_selector.
- Next move: Do not promote shifted 3D reflection carrier rows as extraction permission. Reopen only if a source/clue names a specific carrier, base row, target-shift sequence, and unit/order rule.
