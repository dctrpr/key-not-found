# C9 Target Horizontal Chord Gate

Scope: use exact O4/B4/G5/O5 target-center y coordinates as horizontal chords through the p76 C9 OVERDOSE frame, with non-active focus-row controls inside the same frame. This measures existing word/highlight/active-target intersections and strict instruction terms only; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.

## Summary
- active chords: `4`
- control chords: `6`
- active strict instruction hits: `0`
- control strict instruction hits: `0`
- active all-quartet chords: `0`
- active chord active-target hit counts: `[1, 1, 1, 1]`
- control chord active-target hit counts: `[0, 0, 0, 0, 0, 0]`
- active chord highlight-hit counts: `[1, 0, 0, 1]`
- control chord highlight-hit counts: `[0, 0, 0, 0, 0, 0]`
- active word hit counts: `[7, 8, 6, 5]`
- control word hit counts: `[8, 10, 6, 10, 8, 11]`
- selector unlocked: `False`

## Active Chords

| target | y | active hits | words | highlights | strict hits | preview |
|---|---:|---:|---:|---:|---|---|
| buying_dip | 2201.0 | 1 | 7 | 1 | - | He's taunting them, telling them he's ByiiREeraipy" |
| one_billion | 2421.5 | 1 | 8 | 0 | - | eis in bitcoin — that he should sell |
| volcano_bonds | 2568.0 | 1 | 6 | 0 | - | collateralized to pay off the IMF |
| shitcoiner_heart | 2957.0 | 1 | 5 | 1 | - | Maybe because he's a siukbeodmensertslveaarty |

## Control Chords

- `c9_focus_row_2` y `2265.93` active hits `0` words `8` highlights `0` strict `-` preview `I tweeted President Nayib Bukele when he announced`
- `c9_focus_row_3` y `2340.82` active hits `0` words `10` highlights `0` strict `-` preview `he was going to tap his nation's volcanoes to mine`
- `c9_focus_row_5` y `2487.2` active hits `0` words `6` highlights `0` strict `-` preview `billions worth of future bitcoin earnings`
- `c9_focus_row_7` y `2631.37` active hits `0` words `10` highlights `0` strict `-` preview `loan and get rid of those leeches. I tagged Mike`
- `c9_focus_row_8` y `2706.26` active hits `0` words `8` highlights `0` strict `-` preview `Novogratz in the tweet, figuring he could sella`
- `c9_focus_row_9` y `2778.92` active hits `0` words `11` highlights `0` strict `-` preview `bunch to his Wall Street crony pals, but so far he`

## Decision

- Do not promote exact target-y C9 horizontal chords as a selector.
- Active rows are ordinary article rows around the locked targets and have 0 strict instruction hits.
- Control focus rows inside the same C9 frame are comparable ordinary rows, so this adds no unit/order permission.

## Outputs
- JSON: `analysis_outputs/source_audit/c9_target_horizontal_chord_gate/c9_target_horizontal_chord_gate.json`
- visual sheet: `analysis_outputs/source_audit/c9_target_horizontal_chord_gate/c9_target_horizontal_chord_gate_sheet.jpg`
