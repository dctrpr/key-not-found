# Monetizing Near-Miss Unit Audit

Scope: pressure-test p77 `It does this by monetizing` as a possible C3 extraction-unit clue. No key candidates were generated.

- Created: `2026-05-20T12:19:43`
- Near miss: page `77` `It does this by monetizing` -> `O5`.
- Required touch shift: `(0.0, -71.93)`, magnitude `71.93` px.
- Forced nudge trusted-hit count: `1`.

## Phrase Audit

- Exact extraction terms: `none`.
- Context extraction terms: `first`.
- Exact thematic terms: `monetizing`.
- Context thematic terms: `bitcoin, monetizing, demonetizes, peace, love, understanding, war, violence, hatred, state`.
- Deictic terms in exact phrase: `it, this`.

## C3 Criteria

| criterion | status | evidence |
|---|---|---|
| names an extraction unit | `FAIL` | Exact phrase contains no word/letter/line/edge/font/color/take/read/select term. |
| names an order or direction | `WEAK` | Immediate context contains `first time`, but it names historical timing, not which word/letter/line to take. |
| names a unique target object | `FAIL` | `Monetizing` is semantically related to both Volcano Bonds and shitcoiner/bitcoin language, but it does not choose one or define a unit. |
| survives physical/visual repetition check | `FAIL` | Near-miss repair creates only 1 trusted O5/G5 hit, not a repeated selector. |
| produces instruction-like local outputs | `FAIL` | Initials/endings/reversal and first-cue target reads produce short thematic fragments, not procedural text. |

## Low-Parameter Checks

| test | output | instruction hits | verdict |
|---|---|---|---|
| exact phrase initials | `idtbm` | `none` | not instruction-like |
| exact phrase endings | `tssyg` | `none` | not instruction-like |
| exact phrase word reversal | `monetizing by this does It` | `none` | still only ordinary prose |
| exact phrase character reversal | `gnizitenom yb siht seod tI` | `none` | still no extraction unit |
| peace/love/understanding initials from immediate context | `plu` | `none` | thematic phrase only; no unit/order |

## First-Cue Target Reads

| order | first words | first letters | target word initials | instruction hits |
|---|---|---|---|---|
| G5 then O5 | `Volcano shitcoiner` | `Vs` | `vb sah` | `none` |
| O5 then G5 | `shitcoiner Volcano` | `sV` | `sah vb` | `none` |

## Assessment

- `It does this by monetizing` is a good semantic near miss because it sits close to O5 and echoes the money/Bitcoin theme.
- It does not satisfy C3: it does not name a concrete unit such as word, letter, line, font, color, edge, or direction.
- The only procedural-looking context word is `first`, but the phrase is `for the first time in human history`; applying `first` to G5/O5 yields ordinary target words/initials, not an instruction.
- Keep this phrase as a future physical-scan benchmark, not as extraction material under the current scan.

Decision: `do_not_promote_to_selector`.

Next move: Only revisit if a physical/original-layout source makes the p77 phrase directly and repeatedly contact O5/G5, or if an external clue uses monetizing/first-time language as an explicit instruction.
