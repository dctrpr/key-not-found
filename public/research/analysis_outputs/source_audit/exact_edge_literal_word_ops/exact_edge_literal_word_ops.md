# Exact-Edge Literal Word Operations

Scope: test a tiny set of literal human-readable operations suggested by the repaired exact-edge trio: `should sell | Volcano Bonds | shitcoiner at heart`. No key derivation was run.

- Created: `2026-05-20T09:01:35`
- Exact trio: `should sell | Volcano Bonds | shitcoiner at heart`
- Line indexes: should sell `25`, Volcano Bonds `27`, shitcoiner at heart `32`
- Corridor indexes: `7`, `9`, `14`
- Line differences: `[2, 5]`
- Corridor differences: `[2, 5]`

## Operations

| operation | reason | output | instruction hits | letters |
|---|---|---|---|---:|
| `exact_stream` | read selected trio directly | `should sell | Volcano Bonds | shitcoiner at heart` | `[]` | 39 |
| `exact_reversed_words` | mirror-writing order reversal | `shitcoiner at heart | Volcano Bonds | should sell` | `[]` | 39 |
| `exact_reversed_chars` | literal mirror-writing character reversal | `traeh ta renioctihs | sdnoB onacloV | lles dluohs` | `[]` | 39 |
| `word_centers` | `heart` as center letters of selected words | `ouelcncoata` | `[]` | 11 |
| `phrase_centers` | `heart` as center of each selected phrase | `ldnoe` | `[]` | 5 |
| `endpoints_bonded` | `bonds` as connect word endpoints | `sdslVoBssratht` | `[]` | 14 |
| `sell_remove_volcano_from_heart` | `sell` as remove/sell away Volcano Bonds letters from shitcoiner at heart | `hitierathert` | `[]` | 12 |
| `sell_remove_heart_from_volcano` | `sell` as remove/sell away shitcoiner-at-heart letters from Volcano Bonds | `volnobd` | `[]` | 7 |
| `sell_remove_volcano_from_exact` | `sell` as remove/sell away the black-highlighted phrase from the exact stream | `shouldsellocanshitierathert` | `[]` | 27 |
| `g5_o5_interval_full` | `Volcano Bonds` to `shitcoiner at heart` interval | `collateralized “Volcano Bonds” to pay off the IMF | loan and get rid of those leeches. I tagged Mike | Novogratz in the…` | `[]` | 226 |
| `g5_o5_interval_heart_lines` | `heart` as middle of the G5-to-O5 six-line interval | `Novogratz in the tweet, figuring he could sell a | bunch to his Wall Street crony pals, but so far he` | `[]` | 78 |
| `sell_to_sell_interval` | from `should sell` to the next `could sell` | `$1 billion in bitcoin — that he should sell | billions worth of future bitcoin earnings | collateralized “Volcano Bonds…` | `[]` | 186 |
| `line_index_words` | use exact phrase corridor indexes as same-line word positions | `should | |` | `[]` | 6 |
| `page_line_index_words` | use exact phrase page-line indexes as same-line word positions | `| |` | `[]` | 0 |

## Assessment

- Literal `heart` operations select centers/middle lines but produce ordinary fragments, not a selector instruction.
- Literal `sell` operations as remove/interval produce letter debris or the ordinary corridor story, not a word/letter/key rule.
- The G5-to-O5 interval heart is the middle two lines around Novogratz / could sell, reinforcing the existing lower-corridor focus but not choosing an extraction unit.
- Using line/corridor indexes as same-line word positions is empty or ordinary text, not a clean rule.

## Next Move

- Close literal sell/heart/bond wordplay as a current-scan selector. Keep the exact-edge trio only as source-registration evidence unless a new source clue names one of these operations explicitly.
