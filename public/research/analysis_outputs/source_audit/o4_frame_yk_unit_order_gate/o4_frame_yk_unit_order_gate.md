# O4 Frame Y/K Unit/Order Gate

Scope: check whether the clean `Y/K + frame` quartet supplies a source-backed unit/order. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T02:00:53`
- Isolated target count: `4`
- Group/vertical target order: `['buying_dip', 'one_billion', 'volcano_bonds', 'shitcoiner_heart']`
- Left-to-right target order: `['one_billion', 'volcano_bonds', 'shitcoiner_heart', 'buying_dip']`
- Group-order layer codes: `YKKY`
- Page lines: `[22, 25, 27, 32]`
- Corridor indexes: `[4, 7, 9, 14]`
- Group index gaps: `[2, 1, 4]`
- Page/corridor gaps: `[3, 2, 5]` / `[3, 2, 5]`
- Bounded streams checked: `20`
- Total hard instruction hits: `[]`
- Source-backed unit/order: `False`
- Sheet: `analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate_sheet.jpg`

## Order Comparison

| order mode | target ids | source |
|---|---|---|
| group/vertical | `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart` | existing p76 signal group order / readable line order |
| left-to-right | `one_billion -> volcano_bonds -> shitcoiner_heart -> buying_dip` | x-center spatial order |

## Bounded Streams

| stream | values | hard hits |
|---|---|---|
| `group_order_target_ids` | `buying_dip one_billion volcano_bonds shitcoiner_heart` | `-` |
| `reverse_group_order_target_ids` | `shitcoiner_heart volcano_bonds one_billion buying_dip` | `-` |
| `left_to_right_target_ids` | `one_billion volcano_bonds shitcoiner_heart buying_dip` | `-` |
| `right_to_left_target_ids` | `buying_dip shitcoiner_heart volcano_bonds one_billion` | `-` |
| `group_order_layer_codes` | `Y K K Y` | `-` |
| `group_indexes` | `12 14 15 19` | `-` |
| `group_index_gaps` | `2 1 4` | `-` |
| `page_lines` | `22 25 27 32` | `-` |
| `page_line_gaps` | `3 2 5` | `-` |
| `corridor_indexes` | `4 7 9 14` | `-` |
| `corridor_gaps` | `3 2 5` | `-` |
| `sentence_rows` | `44 45 45 48` | `-` |
| `phrase_initials` | `btd 1b vb sah` | `-` |
| `phrase_edges` | `bp 1n vs st` | `-` |
| `left_boundary_words` | `he's - collateralized a` | `-` |
| `right_boundary_words` | `- in to -` | `-` |
| `above_words` | `on was future trust` | `-` |
| `below_words` | `announced billions those -` | `-` |
| `x_center_order_target_ids` | `one_billion volcano_bonds shitcoiner_heart buying_dip` | `-` |
| `y_center_order_target_ids` | `buying_dip one_billion volcano_bonds shitcoiner_heart` | `-` |

## Decision

- `Y/K + frame` is a strong locator: it isolates exactly O4/B4/G5/O5.
- It still does not provide a source-backed unit/order rule.
- Group/vertical order and left-to-right spatial order disagree, and color/state patterns are palindromic, so orientation/order cannot be inferred from color alone.
- Keep the quartet as a validation surface only until source wording names a unit and order.
