# Page 76 Line-Count Models Audit

Scope: compare line-counting models for the partial highlight-number offset pattern. No key candidates or hashing were generated.

- Created: `2026-05-20T05:48:59`

## Summary

| model | hit count | hits |
|---|---:|---|
| `corrected_with_blank_lines` | 4 | `O1->O2, B1->B2, O3->B3, B5->O5` |
| `corrected_nonblank_lines` | 3 | `O1->O2, B1->B2, B5->O5` |
| `paragraph_local_nonblank_lines` | 3 | `O1->O2, B1->B2, B5->O5` |
| `highres_highlight_row_order` | 6 | `O1->O2, O2->B2, B1->B2, B2->B3, O3->B4, B3->O5,B5` |

## Corrected With Blank Lines

| source | target line | target units | target text |
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

## Assessment

- The partial pattern is most coherent only when using corrected printed line layout with blank rows preserved.
- Removing blank rows breaks `O3 -> B3`; paragraph-local counting also breaks that cross-paragraph bridge.
- High-res highlight-row order creates a different, less meaningful hit set, so it is not the right counting model.
- The #2/#4 failures are not explained away by alternate line counting.
- Next best move: preserve the corrected-with-blank-lines locator, but seek a source/provenance or physical-registration rule for the missing extraction unit.
