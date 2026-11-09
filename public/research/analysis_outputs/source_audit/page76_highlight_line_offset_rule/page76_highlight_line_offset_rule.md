# Page 76 Highlight Line-Offset Rule Audit

Scope: test whether a highlighted unit's number tells us how many corrected text lines to move. No key candidates or hashing were generated.

- Created: `2026-05-20T05:41:25`

## Down-Offset Highlight Hits

| source | rule | target | target line text |
|---|---:|---|---|
| O1 `Get some toxicity / Open your heart to` | +1 lines | O2 | Bitcoin. It's the freaking UTXO ghetto up in here, y'all. |
| B1 `Gotta be this way... post-1971 fiat money` | +1 lines | B2 | nonsense (and 10 years of watching Peter Schiff miss buying bitcoin |
| O3 `by the rancid catnip of fiat money` | +3 lines | B3 | laundering lobotomy. It’s a stun gun to the genitals. |
| B5 `Volcano Bonds` | +5 lines | O5 | Maybe because he's a shitcoiner at heart. |

## All Down-Offset Landings

| source | target line | highlighted target | line text |
|---|---:|---|---|
| O1 +1 | 1 | O2 | Bitcoin. It's the freaking UTXO ghetto up in here, y'all. |
| O2 +2 | 3 | - | but George Clinton and James Brown clones. It's Martin Luther |
| B1 +1 | 7 | B2 | nonsense (and 10 years of watching Peter Schiff miss buying bitcoin |
| B2 +2 | 9 | - | have dulled shitcoiners' and nocoiners' minds. |
| O3 +3 | 16 | B3 | laundering lobotomy. It’s a stun gun to the genitals. |
| B3 +3 | 19 | - | Don't believe me? |
| O4 +4 | 26 | - | billions worth of future bitcoin earnings |
| B4 +4 | 29 | - | Novogratz in the tweet, figuring he could sell a |
| B5 +5 | 32 | O5 | Maybe because he's a shitcoiner at heart. |
| O5 +5 | 37 | - |  |

## Gap Matches

| source | target | line gap | source index | target index | same index |
|---|---|---:|---:|---:|---|
| O1 | O2 | 1 | 1 | 2 | False |
| B1 | B2 | 1 | 1 | 2 | False |
| O3 | B3 | 3 | 3 | 3 | True |
| B5 | O5 | 5 | 5 | 5 | True |

## Assessment

- The G5/O5 five-line locator is real, but it is not isolated.
- Down-offset hits appear for `O1 -> O2`, `B1 -> B2`, `O3 -> B3`, and `B5 -> O5`.
- The same-index subset is cleaner but shorter: `O3 -> B3` and `B5 -> O5`.
- The rule is incomplete because #2 and #4 do not land on highlighted target units under the same simple operation.
- Treat this as locator/orientation evidence. It still does not define whether to extract words, letters, colors, or adjacent text.
