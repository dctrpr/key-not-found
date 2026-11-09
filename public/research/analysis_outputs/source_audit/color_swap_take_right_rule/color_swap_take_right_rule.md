# Color-Swap Take-Right Rule Audit

Scope: test the only procedural-looking words from the p79 color-swap source phrase, `right` and `take`, as literal right-side/edge extraction on page 76. No key derivation, hashing, seed checking, WIF checking, address checking, or broad brute force was run.

- Created: `2026-05-20T10:04:32`
- Overlay: `analysis_outputs/source_audit/color_swap_take_right_rule/color_swap_take_right_rule_overlay.jpg`
- Selected p79 color-swap contacts: `5`

## Records

| target | source phrase | target words | intersection | right edge | right of intersection |
|---|---|---|---|---|---|
| `G1` | `That’s right, Bitcoin will take` | `Gotta be S way. Forty years of dumb post-1971 flat money` | `Gotta be S way. Forty years` | `money` | `of dumb post-1971` |
| `G1` | `all the energy.` | `Gotta be S way. Forty years of dumb post-1971 flat money` | `` | `money` | `flat money` |
| `G2` | `That’s right, Bitcoin will take` | `RRECECy` | `RRECECy` | `RRECECy` | `RRECECy (and loyears` |
| `O1` | `war and violence economy` | `Get some toxicity. Get some bitcoin. Open your heart to` | `Get some toxicity.` | `to` | `Get some bitcoin.` |
| `O2` | `war and violence economy` | `Biteoiny` | `Biteoiny` | `Biteoiny` | `It's the freaking` |

## Streams

- `intersectionWords`: `Gotta be S way. Forty years | RRECECy | Get some toxicity. | Biteoiny`
- `targetRightHalf`: `years of dumb post-1971 flat money | years of dumb post-1971 flat money | RRECECy | bitcoin. Open your heart to | Biteoiny`
- `rightEdgeWords`: `money money RRECECy to Biteoiny`
- `firstWordsRightOfTarget`: `RRECECy It's`
- `rightOfIntersections`: `of dumb post-1971 | flat money | RRECECy (and loyears | Get some bitcoin. | It's the freaking`
- `rightOfReflectedBoxes`: `of dumb post-1971 | flat money | Peter Schiff miss | Get some bitcoin. | freaking UTXO`
- `leftOfReflectedBoxes`: `Forty years of`

## Decision

- Literal take-right operations on the p79 color-swap contacts produce ordinary upper-page-76 prose and short fragments such as `to`, `Bitcoin`, `money`, and `nonsense`. The streams do not contain a procedural read/take/word/letter/key instruction, so `take/right` remains printed phrase content rather than a usable rule.

## Next Move

- Do not keep drilling the upper p79 color-swap cluster locally. Return to lower-corridor source/physical registration or wait for a source clue that names color-swap/right-side extraction.
