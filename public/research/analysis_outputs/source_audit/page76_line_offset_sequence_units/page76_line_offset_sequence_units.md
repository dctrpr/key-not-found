# Page 76 Line-Offset Sequence Units Audit

Scope: check whether the partial line-offset hit sequence carries a simple color/order message. No key candidates or hashing were generated.

- Created: `2026-05-20T05:44:36`

## Hit Sequence

| source | target | transition | source first | target first | target line first |
|---|---|---|---|---|---|
| O1 | O2 | OO | `Get` | `Bitcoin` | `Bitcoin` |
| B1 | B2 | BB | `Gotta` | `nonsense` | `nonsense` |
| O3 | B3 | OB | `by` | `It` | `laundering` |
| B5 | O5 | BO | `Volcano` | `shitcoiner` | `Maybe` |

## Streams

- `hitSourceIds`: `O1 B1 O3 B5`
- `hitTargetIds`: `O2 B2 B3 O5`
- `hitTransitions`: `OO BB OB BO`
- `sameColorBits_same0_cross1`: `0011`
- `allDownHitMissBits_hit1_miss0`: `1010100010`
- `hitSourceFirstWords`: `Get Gotta by Volcano`
- `hitTargetFirstWords`: `Bitcoin nonsense It shitcoiner`
- `hitTargetLineFirstWords`: `Bitcoin nonsense laundering Maybe`
- `hitSourceInitials`: `GGbV`
- `hitTargetInitials`: `BnIs`
- `hitTargetLineInitials`: `BnlM`
- `hitSourceLastLetters`: `oyys`
- `hitTargetLastLetters`: `nest`
- `missTargetLineFirstWords`: `but have Don billions Novogratz -`
- `missTargetLineInitials`: `bhDbN`
- `allDownTargetLineFirstWords`: `Bitcoin but nonsense have laundering Don billions Novogratz Maybe -`
- `allDownTargetLineInitials`: `BbnhlDbNM`

## Misses

| source | target line | first word | line text |
|---|---:|---|---|
| O2 | 3 | `but` | but George Clinton and James Brown clones. It's Martin Luther |
| B2 | 9 | `have` | have dulled shitcoiners' and nocoiners' minds. |
| B3 | 19 | `Don` | Don't believe me? |
| O4 | 26 | `billions` | billions worth of future bitcoin earnings |
| B4 | 29 | `Novogratz` | Novogratz in the tweet, figuring he could sell a |
| O5 | 37 | `-` |  |

## Assessment

- The color transition sequence is balanced (`OO BB OB BO`) but does not give a readable instruction.
- Hit/miss, first-word, initial, last-letter, and failed-landing streams are not instruction-like.
- This closes the color/order sequence as a standalone selector under the current text model.
- Next best move: seek source/provenance or physical-registration evidence that explains why the partial locator pattern exists and what unit it should select.
