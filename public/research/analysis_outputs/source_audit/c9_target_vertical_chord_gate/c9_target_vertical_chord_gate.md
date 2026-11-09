# C9 Target Vertical Chord Gate

Scope: use exact O4/B4/G5/O5 target-center x coordinates as vertical chords through the p76 C9 OVERDOSE frame, with non-active page-76 highlight controls. This measures existing word/highlight/active-target intersections and strict instruction terms only; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.

## Summary
- active chords: `4`
- control chords: `3`
- active slot stream: `OVED`
- control slot stream: `DEE`
- active strict instruction hits: `0`
- control strict instruction hits: `0`
- active all-quartet chords: `0`
- active chord active-target hit counts: `[2, 1, 1, 2]`
- control chord active-target hit counts: `[2, 1, 1]`
- active chord highlight-hit counts: `[2, 0, 0, 2]`
- control chord highlight-hit counts: `[2, 0, 0]`
- selector unlocked: `False`

## Active Chords

| target | slot | active hits | words | highlights | strict hits | preview |
|---|---|---:|---:|---:|---|---|
| buying_dip | O5 | 2 | 6 | 2 | - | ByiiREeraipy" announced mine IMF he siukbeodmensertslveaarty |
| one_billion | V1 | 1 | 9 | 0 | - | tweeted was billions collateralized loan Novogratz bunch hasn't Maybe |
| volcano_bonds | E2 | 1 | 6 | 0 | - | telling Nayib future those Street don't |
| shitcoiner_heart | D4 | 2 | 8 | 2 | - | ByiiREeraipy" when volcanoes earnings tagged could but siukbeodmensertslveaarty |

## Control Chords

- `p76_orange_1` slot `D4` active hits `2` words `8` highlights `2` strict `-` preview `ByiiREeraipy" announced mine Mike sella far guy siukbeodmensertslveaarty`
- `p76_orange_2` slot `E2` active hits `1` words `5` highlights `0` strict `-` preview `bitcoin future tweet, Street he's`
- `p76_orange_3` slot `E2` active hits `1` words `6` highlights `0` strict `-` preview `them, President tap bitcoin of it.`

## Decision

- Do not promote exact target-x C9 vertical chords as a selector.
- The active slot stream again repeats the already-known `OVED` center-slot result and adds no unit/order instruction.
- Active chords do not traverse the full active quartet; control chords can touch active targets too, so this remains visual/layout context.

## Outputs
- JSON: `analysis_outputs/source_audit/c9_target_vertical_chord_gate/c9_target_vertical_chord_gate.json`
- visual sheet: `analysis_outputs/source_audit/c9_target_vertical_chord_gate/c9_target_vertical_chord_gate_sheet.jpg`
