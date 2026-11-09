# Line-Offset Landing Evidence Audit

Scope: score each page-76 down-offset landing line against other logged visual/source evidence. No key candidates or hashing were generated.

- Created: `2026-05-20T05:52:24`

## Landing Scores

| source | target line | highlight target | score | layers | line text |
|---|---:|---|---:|---|---|
| O1 +1 | 1 | O2 | 5 | highlight target, reflected highlight graph | Bitcoin. It's the freaking UTXO ghetto up in here, y'all. |
| O2 +2 | 3 | - | 0 | - | but George Clinton and James Brown clones. It's Martin Luther |
| B1 +1 | 7 | B2 | 5 | highlight target, reflected highlight graph | nonsense (and 10 years of watching Peter Schiff miss buying bitcoin |
| B2 +2 | 9 | - | 0 | - | have dulled shitcoiners' and nocoiners' minds. |
| O3 +3 | 16 | B3 | 5 | highlight target, reflected highlight graph | laundering lobotomy. It’s a stun gun to the genitals. |
| B3 +3 | 19 | - | 0 | - | Don't believe me? |
| O4 +4 | 26 | - | 6 | p78_bbox_words, p78_dark_words, reflected highlight graph | billions worth of future bitcoin earnings |
| B4 +4 | 29 | - | 5 | p78_bbox_words, p78_dark_words, p78_hole_words | Novogratz in the tweet, figuring he could sell a |
| B5 +5 | 32 | O5 | 8 | highlight target, reflected highlight graph, target convergence | Maybe because he's a shitcoiner at heart. |
| O5 +5 | 37 | - | 0 | - |  |

## Supported Misses

- `O4 +4` -> line `26`: billions worth of future bitcoin earnings
  - p78_bbox_words terms: earnings
  - p78_dark_words terms: earnings
  - orange_7 strong terms=bitcoin; orange_7 strong terms=bitcoin; orange_7 medium terms=bitcoin
- `B4 +4` -> line `29`: Novogratz in the tweet, figuring he could sell a
  - p78_bbox_words terms: could, sell
  - p78_dark_words terms: could
  - p78_hole_words terms: could

## Assessment

- #4 is not a dead miss: both #4 landings sit in the p78 graphic reflection band.
- #2 remains weak under current logged evidence.
- The line-offset rule may be selecting landing lines rather than highlighted boxes, but no extraction unit is defined.
- Next best move: inspect p78/p79/p80 source/provenance layers for why #4 connects to the p78 graphic band and whether #2 has a missing source layer.
