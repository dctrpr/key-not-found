# XX/Wire Similarity Overfit Audit

Scope: force the two p78 X marks onto the two p79 wire knots with proper and reflected two-point similarity transforms, then inspect where the rest of the p78 graphic layer lands. No OCR, key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T10:43:38`
- Source inventory: `analysis_outputs/source_audit/graphic_spill_alignment_inventory/graphic_spill_alignment_inventory.json`
- Sheet: `analysis_outputs/source_audit/xx_wire_similarity_overfit/xx_wire_similarity_overfit_sheet.jpg`

## Candidate Fits

| fit | scale | rotation | reflected | non-X useful hits | min box inside page |
|---|---:|---:|---|---:|---:|
| `proper_left_to_left` | `0.6002` | `-25.12` | `False` | `2` | `1.0` |
| `proper_left_to_right` | `0.6002` | `154.88` | `False` | `2` | `1.0` |
| `reflected_left_to_left` | `0.6002` | `-28.54` | `True` | `2` | `1.0` |
| `reflected_left_to_right` | `0.6002` | `151.46` | `True` | `2` | `1.0` |

## Non-X Landing Details

### `proper_left_to_left`
- `p78_fuck_spill` -> [296.9, 299.1], inside=True, nearest: p79_wire_span=144.3px, p79_wire_left_knot=209.4px, p79_wire_right_knot=275.1px
- `p78_pullquote_blob` -> [373.0, 369.5], inside=True, nearest: p79_wire_span=133.5px, p79_wire_right_knot=248.6px, p79_wire_left_knot=254.6px

### `proper_left_to_right`
- `p78_fuck_spill` -> [378.1, 313.4], inside=True, nearest: p79_wire_span=83.5px, p79_wire_right_knot=209.4px, p79_wire_left_knot=275.1px
- `p78_pullquote_blob` -> [302.0, 243.0], inside=True, nearest: p79_wire_span=130.6px, p79_wire_left_knot=248.6px, p79_wire_right_knot=254.6px

### `reflected_left_to_left`
- `p78_fuck_spill` -> [319.2, 343.2], inside=True, nearest: p79_wire_span=146.7px, p79_wire_left_knot=209.4px, p79_wire_right_knot=275.1px
- `p78_pullquote_blob` -> [307.6, 240.2], inside=True, nearest: p79_wire_span=125.3px, p79_wire_right_knot=248.6px, p79_wire_left_knot=254.6px

### `reflected_left_to_right`
- `p78_fuck_spill` -> [355.8, 269.3], inside=True, nearest: p79_wire_span=79.1px, p79_wire_right_knot=209.4px, p79_wire_left_knot=275.1px
- `p78_pullquote_blob` -> [367.4, 372.3], inside=True, nearest: p79_wire_span=138.5px, p79_wire_left_knot=248.6px, p79_wire_right_knot=254.6px

## Assessment

- A two-point similarity transform can force the p78 X pair onto the p79 wire knots, but that is tautological and must be judged by the non-X objects.
- The best non-X result is `proper_left_to_left` with `2` non-X graphic centers within 180 px of any p79 mark.
- The p78 `FUCK` spill and pull-quote blob do not land on a page-76/page-79 extraction surface or produce an instruction under this forced fit.
- This branch remains source-registration/orientation evidence only; it still needs a higher-resolution Canva/original-layout/physical source or an explicit object-pair rule.

## Decision

- Forced XX-to-wire similarity alignment is an overfit under the current scan and does not unlock extraction.

## Next Move

- Do not derive from XX/wire/FUCK geometry locally. Reopen only if a higher-resolution Canva/original-layout/physical source specifies the graphic object pair or changes registration.
