# Page 76 Spill Control Comparison

Scope: compare active O4/B4/G5/O5 side-spill behavior against other page-76 orange/grey highlight controls. This checks whether active spill/tail pixels are unique. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T21:25:57`
- Review sheet: `analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison_sheet.jpg`
- Records checked: `10` (`4` active, `6` controls)
- Dominant side counts: `{'bottom': 6, 'top': 1, 'right': 3}`
- Side-order counts: `{'BTLR': 3, 'TBRL': 1, 'BLRT': 1, 'RBLT': 2, 'BLTR': 1, 'BTRL': 1, 'RLBT': 1}`

## Records

| id | role | color | dominant | order | share | total spill | text |
|---|---|---|---|---|---:|---:|---|
| `p76_orange_1` | `control` | `orange` | `bottom` | `BTLR` | 0.7172 | 1241 | Get some toxicity. Get some bitcoin. Open your heart to |
| `p76_orange_2` | `control` | `orange` | `top` | `TBRL` | 0.6316 | 1341 | Bitcoin. |
| `p76_grey_1` | `grey_control` | `grey` | `bottom` | `BLRT` | 1.0 | 1526 | Gotta be this way... post-1971 fiat money |
| `p76_grey_2` | `grey_control` | `grey` | `right` | `RBLT` | 0.8733 | 1002 | nonsense |
| `p76_orange_3` | `control` | `orange` | `bottom` | `BTLR` | 0.4447 | 778 | by the rancid catnip of fiat money. |
| `p76_grey_3` | `grey_control` | `grey` | `bottom` | `BLTR` | 0.845 | 2026 | It's a stun gun to the genitals |
| `p76_orange_4` | `active_O4` | `orange` | `bottom` | `BTRL` | 0.7145 | 767 | “buying the dip.” |
| `one_billion` | `active_B4` | `grey` | `right` | `RBLT` | 0.8593 | 135 | $1 billion |
| `volcano_bonds` | `active_G5` | `grey` | `right` | `RLBT` | 0.4716 | 229 | Volcano Bonds |
| `p76_orange_5` | `active_O5` | `orange` | `bottom` | `BTLR` | 0.5296 | 540 | shitcoiner at heart. |

## Findings

- The active page-76 spill behavior is not an isolated physical marker grammar when compared with page-76 controls.
- Across all checked page-76 highlights, dominant sides are `{'bottom': 6, 'top': 1, 'right': 3}` and side-order counts are `{'BTLR': 3, 'TBRL': 1, 'BLRT': 1, 'RBLT': 2, 'BLTR': 1, 'BTRL': 1, 'RLBT': 1}`.
- Active side-order counts are `{'BTRL': 1, 'RBLT': 1, 'RLBT': 1, 'BTLR': 1}`; at least one active order also appears in controls.
- The visible side pixels track phrase/crop geometry, adjacent prose, and text band edges, not a deliberate four-anchor ordering cue.
- This reinforces the prior decision: active highlight boxes are target locators, not side/tail selectors under the current scan.

## Decision

- Close page-76 highlight spill uniqueness as a standalone selector; do not infer extraction direction from side/tail pixels.
- Next move: Prioritize source/original-layout evidence or explicit instruction wording. Use highlight side-spill only as a future-source comparison benchmark.
