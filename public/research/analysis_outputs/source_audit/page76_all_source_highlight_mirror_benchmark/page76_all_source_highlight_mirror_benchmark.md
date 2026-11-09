# Page 76 All-Source Highlight Mirror Benchmark

Scope: apply the same raw horizontal mirror to every non-page-76 orange/grey highlight set and measure contacts against verified page-76 orange/grey targets. No OCR extraction, key derivation, hashing, seed checking, WIF checking, or address checking was run.

- Created: `2026-05-20T09:55:38`
- Sheet: `analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/page76_all_source_highlight_mirror_benchmark_sheet.jpg`

## Summary

| source page | source boxes | meaningful edges | strong edges | strong targets | score |
|---:|---:|---:|---:|---|---:|
| `79` | `11` | `5` | `5` | `G1 G2 O1 O2` | `183.829` |
| `77` | `5` | `2` | `2` | `G1 O3` | `119.689` |
| `78` | `7` | `1` | `1` | `O3` | `65.424` |
| `75` | `11` | `0` | `0` | `-` | `0` |
| `80` | `2` | `0` | `0` | `-` | `0` |

## Top Edges

### p79 -> p76
- orange 2 `That’s right, Bitcoin will take` -> G1 `Gotta be this way... post-1971 fiat money` (source=0.70588, target=0.43081, dist=297.83)
- grey 1 `war and violence economy` -> O2 `Bitcoin.` (source=0.12793, target=0.42553, dist=49.04)
- orange 3 `all the energy.` -> G1 `Gotta be this way... post-1971 fiat money` (source=0.25758, target=0.05854, dist=420.19)
- grey 1 `war and violence economy` -> O1 `Get some toxicity. Get some bitcoin. Open your heart to` (source=0.26581, target=0.11757, dist=565.25)
- orange 2 `That’s right, Bitcoin will take` -> G2 `nonsense` (source=0.02223, target=0.06759, dist=508.66)

### p77 -> p76
- grey 2 `shitcoiners, useless Royals` -> O3 `by the rancid catnip of fiat money.` (source=0.43267, target=0.85405, dist=151.63)
- grey 1 `Sorry Bhutan... shitcoin hell` -> G1 `Gotta be this way... post-1971 fiat money` (source=0.138, target=0.25224, dist=142.43)

### p78 -> p76
- orange 3 `BILLION worth of hate toys in Afghanistan, / $2 trillion fiat cuck-bucks.` -> O3 `by the rancid catnip of fiat money.` (source=0.16357, target=0.64994, dist=557.05)

### p75 -> p76
- No meaningful contacts.

### p80 -> p76
- No meaningful contacts.

## Decision

- Raw page-center highlight mirroring to page 76 does not produce a final selector. It makes p79 the strongest uniform source and leaves p75/p80 empty, but p77 also creates mid-page contacts; therefore raw mirrored highlight boxes alone are too permissive. The useful contacts remain regional, not a word/letter extraction unit.
- p78/p79 strong targets: `G1 G2 O1 O2 O3`.
- Other-page strong targets: `G1 O3`.
- This benchmark reinforces the current priority stack but does not supply the missing selector.

## Next Move

- Keep p78/p79-to-page76 highlight mirror evidence as orientation/target evidence only; the next useful move is a source/physical transform or an external rule naming exact unit/order.
