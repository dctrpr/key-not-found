# Exact Trio Sell-Removal Rule

Scope: test `sell` as a literal remove/sell-off operation on the repaired exact-edge trio. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T11:03:55`
- Trio: `should sell | Volcano Bonds | shitcoiner at heart`

## Scenarios

| scenario | operation | remaining phrases | exposed boundary |
|---|---|---|---|
| `sell_off_middle_phrase` | remove `Volcano Bonds` from the exact-edge trio | `['should sell', 'shitcoiner at heart']` | `{'leftWord': 'sell', 'rightWord': 'shitcoiner', 'lastFirst': 'ls', 'firstLast': 'sr', 'joinedWords': 'sell shitcoiner'}` |
| `sell_off_sell_word` | remove the word `sell` from `should sell` | `['should', 'Volcano Bonds', 'shitcoiner at heart']` | `{'leftWord': 'should', 'rightWord': 'Volcano', 'lastFirst': 'dv', 'firstLast': 'so', 'joinedWords': 'should Volcano'}` |
| `sell_off_command_phrase` | remove the whole `should sell` phrase | `['Volcano Bonds', 'shitcoiner at heart']` | `{'leftWord': 'Bonds', 'rightWord': 'shitcoiner', 'lastFirst': 'ss', 'firstLast': 'br', 'joinedWords': 'Bonds shitcoiner'}` |

## Streams

| stream | value | raw hits | actionable hits |
|---|---|---|---|
| `sell_off_middle_phrase_joined` | `should sell shitcoiner at heart` | `['heart', 'sell']` | `[]` |
| `sell_off_middle_phrase_compact` | `shouldsellshitcoineratheart` | `[]` | `[]` |
| `sell_off_middle_phrase_initials` | `ss` | `[]` | `[]` |
| `sell_off_middle_phrase_lasts` | `lt` | `[]` | `[]` |
| `sell_off_middle_phrase_boundaryLastFirst` | `ls` | `[]` | `[]` |
| `sell_off_middle_phrase_boundaryFirstLast` | `sr` | `[]` | `[]` |
| `sell_off_middle_phrase_boundaryWords` | `sell shitcoiner` | `['sell']` | `[]` |
| `sell_off_sell_word_joined` | `should Volcano Bonds shitcoiner at heart` | `['heart']` | `[]` |
| `sell_off_sell_word_compact` | `shouldvolcanobondsshitcoineratheart` | `[]` | `[]` |
| `sell_off_sell_word_initials` | `svs` | `[]` | `[]` |
| `sell_off_sell_word_lasts` | `dst` | `[]` | `[]` |
| `sell_off_sell_word_boundaryLastFirst` | `dv` | `[]` | `[]` |
| `sell_off_sell_word_boundaryFirstLast` | `so` | `[]` | `[]` |
| `sell_off_sell_word_boundaryWords` | `should Volcano` | `[]` | `[]` |
| `sell_off_command_phrase_joined` | `Volcano Bonds shitcoiner at heart` | `['heart']` | `[]` |
| `sell_off_command_phrase_compact` | `volcanobondsshitcoineratheart` | `[]` | `[]` |
| `sell_off_command_phrase_initials` | `vs` | `[]` | `[]` |
| `sell_off_command_phrase_lasts` | `st` | `[]` | `[]` |
| `sell_off_command_phrase_boundaryLastFirst` | `ss` | `[]` | `[]` |
| `sell_off_command_phrase_boundaryFirstLast` | `br` | `[]` | `[]` |
| `sell_off_command_phrase_boundaryWords` | `Bonds shitcoiner` | `[]` | `[]` |

## Assessment

- The `sell` rule is locally justified only because `should sell` is part of the repaired exact-edge trio.
- Removing `Volcano Bonds`, removing `sell`, or removing the whole `should sell` phrase leaves ordinary phrase joins such as `sell shitcoiner`, `should Volcano`, and `Bonds shitcoiner`.
- The resulting initials, lasts, compact text, and exposed boundary pairs do not create a new instruction or extraction unit.
- This closes literal `sell off/remove` extraction from the exact trio as a standalone selector.

## Decision

- Close literal sell/remove extraction from the exact trio as a selector.

## Next Move

- The exact trio remains registration evidence only until a source-backed unit/order is found.
