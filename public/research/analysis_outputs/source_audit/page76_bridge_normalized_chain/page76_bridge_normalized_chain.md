# Page 76 Bridge-Normalized Chain

Scope: normalize the page-76 line-offset chain using the B3 bridge (`B3 -> Don't believe me? -> O4`) and check whether the resulting ordered chain names an extraction unit. No key candidates, hashes, seed phrases, or address checks were generated.

- Created: `2026-05-20T06:30:26`
- Overlay: `analysis_outputs/source_audit/page76_bridge_normalized_chain/page76_bridge_normalized_chain_overlay.jpg`

## Strict Chain

| source | class | steps | normalized target | preferred term | evidence |
|---|---|---|---|---|---|
| `O1` | `highlight-hit` | `+1` | L1 `Bitcoin. It's the freaking UTXO ghetto up in here, y'all.` | `bitcoin` | highlight target, reflected highlight graph |
| `B1` | `highlight-hit` | `+1` | L7 `nonsense (and 10 years of watching Peter Schiff miss buying bitcoin` | `nonsense` | highlight target, reflected highlight graph |
| `O3` | `highlight-hit` | `+3` | L16 `laundering lobotomy. It’s a stun gun to the genitals.` | `stun` | highlight target, reflected highlight graph |
| `B3` | `bridge-hit` | `+3 then +3` | L22 `He's taunting them, telling them he's “buying the dip.”` | `buying dip` | bridge prompt, highlight target |
| `O4` | `source-supported-line` | `+4` | L26 `billions worth of future bitcoin earnings` | `earnings` | p78_bbox_words, p78_dark_words, reflected highlight graph |
| `B4` | `source-supported-line` | `+4` | L29 `Novogratz in the tweet, figuring he could sell a` | `sell` | p78_bbox_words, p78_dark_words, p78_hole_words |
| `B5` | `highlight-hit` | `+5` | L32 `Maybe because he's a shitcoiner at heart.` | `heart` | highlight target, reflected highlight graph, target convergence |

## Streams

- `strictSourceIds`: `O1 B1 O3 B3 O4 B4 B5`
- `strictColors`: `OBOBOBB`
- `strictIndices`: `1133445`
- `strictTargetLines`: `1 7 16 22 26 29 32`
- `strictPreferredTerms`: `bitcoin nonsense stun buying dip earnings sell heart`
- `strictPreferredInitials`: `bnsbesh`
- `strictPreferredLastLetters`: `nenpslt`
- `allNondeadSourceIds`: `O1 O2 B1 B2 O3 B3 O4 B4 B5`
- `allNondeadPreferredTerms`: `bitcoin but george nonsense have dulled stun buying dip earnings sell heart`
- `strictPreferredTermsReversed`: `heart sell earnings dip buying stun nonsense bitcoin`
- `strictPreferredInitialsReversed`: `hsebsnb`
- Instruction-term hits: none

## All Records

| source | class | first landing | normalized target |
|---|---|---|---|
| `O1` | `highlight-hit` | L1 `Bitcoin. It's the freaking UTXO ghetto up in here, y'all.` | L1 `Bitcoin. It's the freaking UTXO ghetto up in here, y'all.` |
| `O2` | `weak-secondary-line` | L3 `but George Clinton and James Brown clones. It's Martin Luther` | L3 `but George Clinton and James Brown clones. It's Martin Luther` |
| `B1` | `highlight-hit` | L7 `nonsense (and 10 years of watching Peter Schiff miss buying bitcoin` | L7 `nonsense (and 10 years of watching Peter Schiff miss buying bitcoin` |
| `B2` | `weak-secondary-line` | L9 `have dulled shitcoiners' and nocoiners' minds.` | L9 `have dulled shitcoiners' and nocoiners' minds.` |
| `O3` | `highlight-hit` | L16 `laundering lobotomy. It’s a stun gun to the genitals.` | L16 `laundering lobotomy. It’s a stun gun to the genitals.` |
| `B3` | `bridge-hit` | L19 `Don't believe me?` | L22 `He's taunting them, telling them he's “buying the dip.”` |
| `O4` | `source-supported-line` | L26 `billions worth of future bitcoin earnings` | L26 `billions worth of future bitcoin earnings` |
| `B4` | `source-supported-line` | L29 `Novogratz in the tweet, figuring he could sell a` | L29 `Novogratz in the tweet, figuring he could sell a` |
| `B5` | `highlight-hit` | L32 `Maybe because he's a shitcoiner at heart.` | L32 `Maybe because he's a shitcoiner at heart.` |
| `O5` | `out-of-range` | L37 `-` | L37 `-` |

## Assessment

- The B3 bridge makes the locator map cleaner: the strict chain is O1, B1, O3, B3, O4, B4, B5.
- The resulting strict color/index stream is OBOBOBB / 1133445, and the preferred term stream is `bitcoin nonsense stun buying dip earnings sell heart`.
- Those streams do not contain extraction instructions such as read/take/use/fold/mirror/word/letter/key.
- The bridge strengthens O4 as part of the path, but it still does not specify whether to extract a word, letter, row, edge, or adjacent phrase.
- Keep the bridge-normalized chain as structural evidence; close the chain streams as standalone instructions.

Next move: Use the bridge-normalized chain to inspect the #4 lower corridor more narrowly: O4/B4/B5 are now the unresolved segment where exact unit/order still needs a source rule.
