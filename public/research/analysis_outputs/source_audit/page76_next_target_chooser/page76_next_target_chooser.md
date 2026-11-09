# Page 76 Next Target Chooser

Scope: rank corrected page-76 corridor lines by already-logged independent evidence. No key derivation, hashing, seed phrases, WIF checks, or address checks were run.

- Created: `2026-05-20T09:36:05`

## Decision

- Primary manual target: L32 / corridor 14 `Maybe because he's a shitcoiner at heart.` score `32.75`.
- Required paired target: L27 / corridor 9 `collateralized “Volcano Bonds” to pay off the IMF` score `16.75`.
- Broad source-band target: L26 / corridor 8 `billions worth of future bitcoin earnings` score `10.0`.

## Ranked Lines

| rank | line | corridor | score | text | main evidence |
|---:|---:|---:|---:|---|---|
| 1 | 32 | 14 | 32.75 | `Maybe because he's a shitcoiner at heart.` | line-offset landing score(8.0); supported landing sequence(1.0); target convergence(15.0); p78 frame edge(3.0) |
| 2 | 27 | 9 | 16.75 | `collateralized “Volcano Bonds” to pay off the IMF` | target convergence(11.0); p78 frame edge(1.5); p78 frame edge(1.5); minimal frame phrase(2.0) |
| 3 | 25 | 7 | 10.75 | `$1 billion in bitcoin — that he should sell` | target convergence(2.0); p78 frame edge(3.0); p78 frame edge(3.0); minimal frame phrase(2.0) |
| 4 | 26 | 8 | 10.00 | `billions worth of future bitcoin earnings` | line-offset landing score(6.0); supported landing sequence(1.0); p78 frame edge(3.0) |
| 5 | 29 | 11 | 7.50 | `Novogratz in the tweet, figuring he could sell a` | line-offset landing score(5.0); supported landing sequence(1.0); p78 frame edge(1.5) |
| 6 | 22 | 4 | 2.75 | `He's taunting them, telling them he's “buying the dip.”` | target convergence(2.0); announcement/media corridor term(0.75) |
| 7 | 28 | 10 | 1.50 | `loan and get rid of those leeches. I tagged Mike` | p78 frame edge(1.5) |
| 8 | 31 | 13 | 1.50 | `hasn't moved on it. I don't really trust that guy.` | p78 frame edge(1.5) |
| 9 | 20 | 2 | 0.75 | `Have you seen the president of El Salvador` | announcement/media corridor term(0.75) |
| 10 | 21 | 3 | 0.75 | `trolling the International Monetary Fund (IMF) on Twitter?` | announcement/media corridor term(0.75) |
| 11 | 23 | 5 | 0.75 | `I tweeted President Nayib Bukele when he announced` | announcement/media corridor term(0.75) |
| 12 | 24 | 6 | 0.75 | `he was going to tap his nation's volcanoes to mine` | announcement/media corridor term(0.75) |
| 13 | 19 | 1 | 0.00 | `Don't believe me?` | - |
| 14 | 30 | 12 | 0.00 | `bunch to his Wall Street crony pals, but so far he` | - |

## Top Evidence Details

### L32 `Maybe because he's a shitcoiner at heart.`
- line-offset landing score +8.0: B5 lands here; layers=highlight target, reflected highlight graph, target convergence
- supported landing sequence +1.0: B5 / preferred term `heart`
- target convergence +15.0: O5 `shitcoiner at heart` across 5 independent layers
- p78 frame edge +3.0: left edge cuts `shitcoiner at heart` distance=None
- p78 frame edge +3.0: bottom edge cuts `shitcoiner at heart` distance=None
- minimal frame phrase +2.0: `should sell | Volcano Bonds | shitcoiner at heart`
- announcement/media corridor term +0.75: shitcoiner at heart

### L27 `collateralized “Volcano Bonds” to pay off the IMF`
- target convergence +11.0: G5 `Volcano Bonds` across 4 independent layers
- p78 frame edge +1.5: left edge left-adjacent `pay off the IMF` distance=None
- p78 frame edge +1.5: left edge right-adjacent `Volcano Bonds` distance=None
- minimal frame phrase +2.0: `should sell | Volcano Bonds | shitcoiner at heart`
- announcement/media corridor term +0.75: Volcano Bonds

### L25 `$1 billion in bitcoin — that he should sell`
- target convergence +2.0: G4 `$1 billion` across 1 independent layers
- p78 frame edge +3.0: top edge cuts `should sell` distance=None
- p78 frame edge +3.0: left edge cuts `should sell` distance=None
- minimal frame phrase +2.0: `should sell | Volcano Bonds | shitcoiner at heart`
- announcement/media corridor term +0.75: $1 billion

### L26 `billions worth of future bitcoin earnings`
- line-offset landing score +6.0: O4 lands here; layers=p78_bbox_words, p78_dark_words, reflected highlight graph
- supported landing sequence +1.0: O4 / preferred term `earnings`
- p78 frame edge +3.0: left edge cuts `earnings` distance=None

### L29 `Novogratz in the tweet, figuring he could sell a`
- line-offset landing score +5.0: B4 lands here; layers=p78_bbox_words, p78_dark_words, p78_hole_words
- supported landing sequence +1.0: B4 / preferred term `sell`
- p78 frame edge +1.5: left edge left-adjacent `could sell` distance=None

## Assessment

- L32/O5 is the next manual target for any future source comparison, not a solved extraction unit.
- L27/G5 must travel with it because the strongest target is a pair: `Volcano Bonds` / `shitcoiner at heart`.
- L26-L29 explains the #4/p78 graphic band conflict and should be cropped as a band if a new source appears.
- No local line-ranking result justifies new key derivation without a new source rule.

## Next Move

- For future Canva/original-layout/physical scans, score these in order: L32/O5, L27/G5, then L26-L29. Require a named extraction unit before trying keys again.
