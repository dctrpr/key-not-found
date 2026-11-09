# Active Target Center-Path Bold Gate

Scope: project trusted DOCM bold state onto the existing active target center-path geometry. No new OCR, key derivation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-21T05:27:21`
- Bold authority: `Article with Fonts.docm` run export; Markdown bold is not used as font authority.
- Primary path: `['buying_dip', 'one_billion', 'volcano_bonds', 'shitcoiner_heart']`
- Primary rail words: `9`
- Primary bold rail words: `4`
- Primary non-active bold rail words: `1`
- Primary direct active target bold units: `4`
- Primary direct target bold text: `buying the dip $1 billion Volcano Bonds shitcoiner at heart`
- Primary non-active rail bold text: `Bukele`
- Primary strict instruction terms: `[]`
- Primary non-active strict instruction terms: `[]`
- Variant strict-instruction path count: `0`
- Shift controls tested: `14`
- Controls with non-active bold count >= primary: `[-10, -7, -4, -3, -1]`
- Control strict instruction shifts: `[]`
- Sheet: `analysis_outputs/source_audit/active_target_center_path_bold_gate/active_target_center_path_bold_gate_sheet.jpg`

## Path Variants

| path | direct targets | bold rail words | non-active bold rail words | strict terms | non-active bold text |
|---|---:|---:|---:|---|---|
| `line_order_o4_b4_g5_o5` | 4 | 4 | 1 | `[]` | Bukele |
| `x_order_b4_g5_o5_o4` | 4 | 2 | 0 | `[]` |  |
| `orange_then_black_mirror_pair_path` | 4 | 2 | 0 | `[]` |  |
| `black_pair_then_orange_path` | 4 | 3 | 0 | `[]` |  |

## Densest Non-Active Bold Controls

| shift | non-active bold words | bold rail words | strict terms | non-active bold text |
|---:|---:|---:|---|---|
| -10 | 2 | 2 | `[]` | stun gun |
| -7 | 1 | 1 | `[]` | Bukele |
| -4 | 1 | 1 | `[]` | Nayib |
| -3 | 1 | 1 | `[]` | President |
| -1 | 1 | 1 | `[]` | Nayib |
| -9 | 0 | 0 | `[]` |  |
| -8 | 0 | 0 | `[]` |  |
| -6 | 0 | 0 | `[]` |  |
| -5 | 0 | 0 | `[]` |  |
| -2 | 0 | 0 | `[]` |  |

## Decision

- Do not promote active target-center rail bold projection as a selector.
- The primary rail necessarily re-hits `4` active bold target units and touches `1` non-active DOCM-bold rail word(s): `Bukele`.
- The combined bold text has `0` strict instruction-term hits; the non-active bold rail text has `0`.
- Shifted controls with non-active bold counts at least as high as primary: `[-10, -7, -4, -3, -1]`.
- Next best move: preserve this as a guardrail and only reopen rail/path mechanics if a source or clue explicitly names path/rail/connector plus a word/letter unit and order.
