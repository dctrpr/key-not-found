# Active Quartet Pair Symmetry Gate

Scope: test whether the locked page-76 `OBBO` / `YKKY` quartet supplies a fold-pair, mirror-pair, or p78-frame midpoint rule. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:20:17`
- Active pattern: `OBBO` / `YKKY`
- Active line order: `22 25 27 32`
- Active corridor order: `4 7 9 14`
- One-line tolerance benchmark: `73.73 px`
- Sheet: `analysis_outputs/source_audit/active_quartet_pair_symmetry_gate/active_quartet_pair_symmetry_gate_sheet.jpg`

## Natural Color Pair Test

| test | value | pass within one line pitch? |
|---|---:|---|
| horizontal fold max error | `436.0 px` | `False` |
| vertical fold max error | `756.0 px` | `False` |
| point-reflection midpoint spread | `686.69 px` | `False` |

Natural pairs:
- `buying_dip` <-> `shitcoiner_heart` midpoint `[1459.0, 2579.0]`, dx `217.0 px`, dy `756.0 px`, line gap `10`, corridor gap `10`.
- `one_billion` <-> `volcano_bonds` midpoint `[777.5, 2494.75]`, dx `436.0 px`, dy `146.5 px`, line gap `2`, corridor gap `2`.

## P78 Frame Relation

| frame | best pair | 2D distance to frame center | within one line pitch? |
|---|---|---:|---|
| `same_layout_p78_source_slot` | `one_billion` <-> `volcano_bonds` | `180.92 px` | `False` |
| `current_p78_to_p76_mirror_frame` | `buying_dip` <-> `shitcoiner_heart` | `298.52 px` | `False` |

## Decision

- The palindromic `OBBO` / `YKKY` color-state order does not create a clean current-scan fold axis.
- The black B4/G5 midpoint nearly matches the p78 same-layout frame in X, but misses the frame center by more than two line pitches in 2D; this supports same-slot validation only.
- The current p78->p76 mirror frame does not center either color pair cleanly.
- No selector was unlocked. Reopen only if source wording names color-pair folding, pair midpoints, or an axis.
