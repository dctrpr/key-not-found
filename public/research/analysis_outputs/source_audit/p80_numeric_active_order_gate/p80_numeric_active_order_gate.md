# P80 Numeric Active-Order Gate

Scope: compare visible p80 package numbers against the locked O4/B4/G5/O5 page-line and corridor order. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:29:16`
- Sheet: `analysis_outputs/source_audit/p80_numeric_active_order_gate/p80_numeric_active_order_gate_sheet.jpg`
- Decision: `p80_numbers_do_not_explain_active_quartet_order`

## Summary

- Raw p80 numbers: `5,100,5,16,473,6,473,80`.
- Canonical p80 numbers excluding clipped volume duplicate: `5,100,5,16,473,80`.
- Active page lines: `22 25 27 32`.
- Active corridor indexes: `4 7 9 14`.
- Active line/corridor gaps: `3 2 5` / `3 2 5`.
- Exact sequence successes: `0`.
- Ordered subsequence successes: `0`.

## Number Records

| label | text | number | note |
|---|---|---:|---|
| `cap_front` | `5 SYMPTOM RELIEF` | `5` | visible/canonical |
| `claim_1` | `100% Proof of Work Liquid` | `100` | visible/canonical |
| `bottle_front` | `5 SYMPTOM RELIEF` | `5` | visible/canonical |
| `volume_visible_likely` | `16 FL OZ (473 mL)` | `16` | visible/canonical |
| `volume_visible_likely` | `16 FL OZ (473 mL)` | `473` | visible/canonical |
| `volume_crop_recorded` | `6 FL OZ (473 mL)` | `6` | clipped duplicate reading |
| `volume_crop_recorded` | `6 FL OZ (473 mL)` | `473` | clipped duplicate reading |
| `page_number` | `80` | `80` | visible/canonical |

## Sequence Checks

| basis | target | sequence | exact contiguous | ordered subsequence | intersection | gap hits |
|---|---|---|---:|---:|---|---|
| `raw` | `active_page_lines` | `[22, 25, 27, 32]` | `False` | `False` | `[]` | `[5]` |
| `raw` | `active_corridor_indexes` | `[4, 7, 9, 14]` | `False` | `False` | `[]` | `[5]` |
| `raw` | `active_sentence_rows` | `[44, 45, 45, 48]` | `False` | `False` | `[]` | `[]` |
| `raw` | `active_page_line_gaps` | `[3, 2, 5]` | `False` | `False` | `[5]` | `[]` |
| `raw` | `active_corridor_gaps` | `[3, 2, 5]` | `False` | `False` | `[5]` | `[]` |
| `canonical` | `active_page_lines` | `[22, 25, 27, 32]` | `False` | `False` | `[]` | `[5]` |
| `canonical` | `active_corridor_indexes` | `[4, 7, 9, 14]` | `False` | `False` | `[]` | `[5]` |
| `canonical` | `active_sentence_rows` | `[44, 45, 45, 48]` | `False` | `False` | `[]` | `[]` |
| `canonical` | `active_page_line_gaps` | `[3, 2, 5]` | `False` | `False` | `[5]` | `[]` |
| `canonical` | `active_corridor_gaps` | `[3, 2, 5]` | `False` | `False` | `[5]` | `[]` |

## Assessment

- P80 package numbers do not contain the active quartet page-line order 22 25 27 32 or corridor order 4 7 9 14.
- The repeated number 5 remains real count/theme evidence for the broader five-symptom/five-highlight model, but it does not select or order O4/B4/G5/O5.
- The likely 16 FL OZ reading supports the already-known B3/stun-gun line-offset evidence, not the lower active quartet.
- The clipped 6 reading and repeated 473 mL value add source-fidelity caveats, not selector permission.

## Next Move

- Keep p80 numeric copy as C6 count/theme/source-validation evidence only; reopen numeric selection only if a raw clue names page line, corridor index, dose, volume, or symptom number as the extraction unit.
