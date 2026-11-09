# G5/O5 Gap Rarity Audit

Scope: compare the G5/O5 `3/5/5` gap against nearby page-76 corridor anchors. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.

- Created: `2026-05-20T11:29:34`
- Anchor count: `10`
- Pair count: `45`
- G5/O5 gap triple: `3/5/5`
- Same-gap pair count: `2`
- Same style+gap pair count: `1`

## Same `3/5/5` Gap Pairs

| left | right | style pair | gap | note |
|---|---|---|---|---|
| `Volcano Bonds` | `shitcoiner at heart` | `grey->orange` | `3/5/5` | G5/O5 |
| `IMF loan` | `shitcoiner at heart` | `bold->orange` | `3/5/5` | same printed coordinate as G5 |

## All Target Pair Gaps

| left | right | style pair | gap |
|---|---|---|---|
| `buying the dip` | `Novogratz` | `orange->bold_partial` | `2/7/7` |
| `buying the dip` | `trust that guy` | `orange->bold_partial` | `3/9/9` |
| `buying the dip` | `shitcoiner at heart` | `orange->orange` | `4/10/10` |
| `$1 billion` | `Novogratz` | `grey->bold_partial` | `1/4/4` |
| `$1 billion` | `trust that guy` | `grey->bold_partial` | `2/6/6` |
| `$1 billion` | `shitcoiner at heart` | `grey->orange` | `3/7/7` |
| `Volcano Bonds` | `Novogratz` | `grey->bold_partial` | `1/2/2` |
| `Volcano Bonds` | `trust that guy` | `grey->bold_partial` | `2/4/4` |
| `Volcano Bonds` | `shitcoiner at heart` | `grey->orange` | `3/5/5` |
| `IMF loan` | `Novogratz` | `bold->bold_partial` | `1/2/2` |
| `IMF loan` | `trust that guy` | `bold->bold_partial` | `2/4/4` |
| `IMF loan` | `shitcoiner at heart` | `bold->orange` | `3/5/5` |

## Streams

| stream | value | instruction hits |
|---|---|---|
| `g5o5GapTriple` | `3/5/5` | `[]` |
| `sameGapPairs` | `Volcano Bonds->shitcoiner at heart | IMF loan->shitcoiner at heart` | `[]` |
| `sameStyleGapPairs` | `Volcano Bonds->shitcoiner at heart` | `[]` |
| `allGapTriplesByPair` | `S43_EL->S43_IMF=0/1/1 ; S43_EL->O4_DIP=1/2/2 ; S43_EL->G4_1B=2/5/5 ; S43_EL->G5_VOLCANO=2/7/7 ; S43_EL->B_IMF=2/7/7 ; S43_EL->B_MIKE=3/8/8 ; S43_EL->B_NOVO=3/9/9 ; S43_EL->B_TRUST=4/11/11 ; S43_EL->O5_HEART=5/12/12 ; S43_IMF->O4_DIP=1/1/1 ;...` | `[]` |
| `gapTripleFrequency` | `0/0/0:1 ; 0/1/1:2 ; 0/2/2:2 ; 1/1/1:4 ; 1/2/2:4 ; 1/3/3:3 ; 1/4/4:1 ; 1/5/5:2 ; 2/3/3:1 ; 2/4/4:4 ; 2/5/5:1 ; 2/6/6:4 ; 2/7/7:3 ; 3/5/5:2 ; 3/7/7:2 ; 3/8/8:2 ; 3/9/9:2 ; 4/10/10:2 ; 4/11/11:1 ; 5/11/11:1 ; 5/12/12:1` | `[]` |

## Assessment

- The G5/O5 locator gap is sentence/page-line/corridor `3/5/5`.
- The exact `3/5/5` gap is shared by `IMF loan -> shitcoiner at heart` because `IMF` sits on the same printed line as `Volcano Bonds`.
- Within grey-to-orange pairs, `Volcano Bonds -> shitcoiner at heart` is the only `3/5/5` pair, while `$1 billion -> shitcoiner at heart` is `3/7/7`.
- This makes `3/5/5` useful as a locator tied to line 27 -> 32, but not a unique extraction instruction.
- No gap-frequency or pair-label stream names a procedural unit.

## Decision

- Treat the `3/5/5` G5/O5 gap as locator evidence only, not as an extraction rule.

## Next Move

- Reopen gap arithmetic only if a future source/clue explicitly names gap, line, sentence, or count units.
