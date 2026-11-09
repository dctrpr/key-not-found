# Active Target Center Path Gate

Scope: test whether narrow connector paths through O4/B4/G5/O5 centers act as selectors. No new OCR, key derivation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-21T05:14:32`
- Buffer half-width: `24.0` px
- Line pitch: `73.73` px
- Primary path: `['buying_dip', 'one_billion', 'volcano_bonds', 'shitcoiner_heart']`
- Primary path words: `9`
- Primary non-target words: `6`
- Primary strict instruction terms: `[]`
- Primary context terms: `['bukele']`
- Variant strict-instruction path count: `0`
- Shift controls tested: `14`
- Control median/max word count: `6.0` / `10`
- Comparable shifted controls (>=75% primary word count): `[-9, -6, -5, -4, -3, -2, -1, 1, 2, 4]`
- Control strict instruction shifts: `[]`
- Sheet: `analysis_outputs/source_audit/active_target_center_path_gate/active_target_center_path_gate_sheet.jpg`

## Path Variants

| path | order | words | non-target | strict terms | context terms | text |
|---|---|---:|---:|---|---|---|
| `line_order_o4_b4_g5_o5` | `['buying_dip', 'one_billion', 'volcano_bonds', 'shitcoiner_heart']` | 9 | 6 | `[]` | `['bukele']` | ByiiREeraipy" Bukele when tap his eis worth figuring siukbeodmensertslveaarty |
| `x_order_b4_g5_o5_o4` | `['one_billion', 'volcano_bonds', 'shitcoiner_heart', 'buying_dip']` | 7 | 5 | `[]` | `[]` | mine eis worth the figuring so siukbeodmensertslveaarty |
| `orange_then_black_mirror_pair_path` | `['buying_dip', 'shitcoiner_heart', 'volcano_bonds', 'one_billion']` | 7 | 5 | `[]` | `[]` | mine eis worth the figuring so siukbeodmensertslveaarty |
| `black_pair_then_orange_path` | `['one_billion', 'volcano_bonds', 'buying_dip', 'shitcoiner_heart']` | 10 | 7 | `[]` | `['bitcoin']` | ByiiREeraipy" he mine eis should worth bitcoin the so siukbeodmensertslveaarty |

## Densest Shift Controls

| shift | words | strict terms | text preview |
|---:|---:|---|---|
| -1 | 10 | `[]` | on he's Nayib was going in future leeches. pals, trust |
| -2 | 10 | `[]` | Monetary Fund them, telling tweeted going to — he but |
| -3 | 10 | `[]` | El Salvador International taunting President his that bitcoin I could |
| 2 | 9 | `[]` | mine should of future collateralized get rid tweet, really |
| 4 | 9 | `[]` | to pay off of those Novogratz his I don't |
| 1 | 7 | `[]` | announced volcanoes bitcoin — billions those crony |
| -4 | 6 | `[]` | the president trolling Nayib he to |
| -5 | 6 | `[]` | me? you the telling nation's pay |
| -6 | 6 | `[]` | believe seen the International should earnings |
| -9 | 6 | `[]` | to the of Monetary he's when |

## Decision

- Do not promote active target-center connector paths as a selector.
- The primary path touches `9` OCR-map words, `6` of them non-target words, and has `0` strict instruction-term hits.
- The alternative target-center paths have `0` strict-instruction path hits across `4` variants.
- The shifted controls have median/max word counts `6.0` / `10` and `0` strict-instruction rows.
- Next best move: keep center paths as visual/source-validation context only unless a new source/clue names path/rail/connector geometry and a unit/order rule.
