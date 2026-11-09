# Active Target Envelope Density Gate

Scope: test whether the minimal O4/B4/G5/O5 page-76 envelope is a selector or only a broad source-validation surface. No new OCR, key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-21T05:05:32`
- Active envelope: `[428, 2177, 1801, 2982]`
- Line pitch: `73.73` px
- Active targets covered: `4/4`
- Active envelope words: `89`
- OCR target words inside envelope: `3`
- Non-target words inside envelope: `86`
- Active strict instruction terms: `[]`
- Active context terms: `['billions', 'bitcoin', 'bukele', 'imf', 'loan', 'sell', 'trust']`
- Active highlight hits: `['p76_orange_4', 'p76_orange_5']`
- Control shifts tested: `25`
- Control median/max word count: `64` / `92`
- Comparable control shifts (>=75% active word count): `[-22, -21, -20, -19, -18, -17, -4, -3, -2, -1, 1, 2]`
- Control strict-instruction rows: `[]`
- Sheet: `analysis_outputs/source_audit/active_target_envelope_density_gate/active_target_envelope_density_gate_sheet.jpg`

## Active Row Groups

| row | y | words | strict terms | context terms | text |
|---:|---:|---:|---|---|---|
| 1 | 2191.04 | 7 | `[]` | `[]` | He's taunting them, telling them he's ByiiREeraipy" |
| 2 | 2265.93 | 8 | `[]` | `['bukele']` | I tweeted President Nayib Bukele when he announced |
| 3 | 2340.82 | 10 | `[]` | `[]` | he was going to tap his nation's volcanoes to mine |
| 4 | 2413.48 | 8 | `[]` | `['bitcoin', 'sell']` | eis in bitcoin — that he should sell |
| 5 | 2487.2 | 6 | `[]` | `['billions', 'bitcoin']` | billions worth of future bitcoin earnings |
| 6 | 2557.64 | 6 | `[]` | `['imf']` | collateralized to pay off the IMF |
| 7 | 2631.37 | 10 | `[]` | `['loan']` | loan and get rid of those leeches. I tagged Mike |
| 8 | 2706.26 | 8 | `[]` | `[]` | Novogratz in the tweet, figuring he could sella |
| 9 | 2778.92 | 11 | `[]` | `[]` | bunch to his Wall Street crony pals, but so far he |
| 10 | 2849.36 | 10 | `[]` | `['trust']` | hasn't moved on it. I don't really trust that guy |
| 11 | 2939.4 | 5 | `[]` | `[]` | Maybe because he's a siukbeodmensertslveaarty |

## Densest Shift Controls

| shift | words | highlights | strict terms | text preview |
|---:|---:|---|---|---|
| -1 | 92 | `['p76_orange_4']` | `[]` | trolling the International Monetary Fund (IMF) on Twitter? He's taunting them, telling them he's ByiiREeraipy" I tweeted President Nayib Bukele when he announced he was going to tap his nation's volcanoes to mine eis in bitcoin — that he should sell billions w |
| -2 | 90 | `['p76_orange_4']` | `[]` | Have you seen the president of El Salvador trolling the International Monetary Fund (IMF) on Twitter? He's taunting them, telling them he's ByiiREeraipy" I tweeted President Nayib Bukele when he announced he was going to tap his nation's volcanoes to mine eis  |
| 1 | 82 | `['p76_orange_5']` | `[]` | I tweeted President Nayib Bukele when he announced he was going to tap his nation's volcanoes to mine eis in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized to pay off the IMF loan and get rid of those leeches. I tagged M |
| -3 | 82 | `['p76_orange_4']` | `[]` | Don't believe me? Have you seen the president of El Salvador trolling the International Monetary Fund (IMF) on Twitter? He's taunting them, telling them he's ByiiREeraipy" I tweeted President Nayib Bukele when he announced he was going to tap his nation's volc |
| -20 | 81 | `['p76_orange_3']` | `[]` | ripped off live central bankers tied to a Gotta be S way. Forty years of dumb post-1971 RRECECy (and loyears of watching Peter Schiff miss since I started honéy-badgering him to buy some at have dulled shitcoiners' and The collective unconscious, controlled no |
| -21 | 81 | `['p76_orange_3']` | `[]` | nailing the Vatican with ultimatums. It's the sound ripped off live central bankers tied to a Gotta be S way. Forty years of dumb post-1971 RRECECy (and loyears of watching Peter Schiff miss since I started honéy-badgering him to buy some at have dulled shitco |
| -18 | 80 | `['p76_orange_3']` | `[]` | Gotta be S way. Forty years of dumb post-1971 RRECECy (and loyears of watching Peter Schiff miss since I started honéy-badgering him to buy some at have dulled shitcoiners' and The collective unconscious, controlled now by psychotic cats, plays "I'riends" reru |
| -19 | 80 | `['p76_orange_3']` | `[]` | Gotta be S way. Forty years of dumb post-1971 RRECECy (and loyears of watching Peter Schiff miss since I started honéy-badgering him to buy some at have dulled shitcoiners' and The collective unconscious, controlled now by psychotic cats, plays "I'riends" reru |
| -22 | 79 | `['p76_orange_3']` | `[]` | but George Clinton and James Brown clones. It's nailing the Vatican with ultimatums. It's the sound ripped off live central bankers tied to a Gotta be S way. Forty years of dumb post-1971 RRECECy (and loyears of watching Peter Schiff miss since I started honéy |
| 2 | 74 | `['p76_orange_5']` | `[]` | he was going to tap his nation's volcanoes to mine eis in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized to pay off the IMF loan and get rid of those leeches. I tagged Mike Novogratz in the tweet, figuring he could sella |

## Decision

- Do not promote the active target bbox/hull envelope as a selector.
- The envelope contains `89` OCR words, of which `86` are not target-overlap words.
- It covers all four active target boxes and hits `['p76_orange_4', 'p76_orange_5']`, but that confirms source-validation geometry rather than extraction permission.
- It has `0` strict instruction-term hits; context terms such as `sell`, `bitcoin`, `IMF`, and `trust` are article prose, not unit/order commands.
- `12` same-size line-pitch shifted controls have at least 75% of the active envelope's word density, so density alone is not selective.
- Next best move: keep this envelope as validation geometry and require new source/clue wording before reopening envelope-based extraction.
