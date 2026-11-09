# Active Quartet Capsule-Direction Gate

Scope: apply the shared p73/p79 `RRLL` capsule zigzag only to the locked O4/B4/G5/O5 side and vertical boundary words. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:36:37`
- Sheet: `analysis_outputs/source_audit/active_quartet_capsule_direction_gate/active_quartet_capsule_direction_gate_sheet.jpg`
- Decision: `rrll_capsule_direction_does_not_select_active_quartet_boundary_instruction`

## Summary

- Capsule step signs: `RRLL`.
- Same p73/p79 step signature: `True`.
- Active page lines: `22 25 27 32`.
- Active corridor indexes: `4 7 9 14`.
- Active visual state order: `YKKY`.
- Direction modes checked: `8`.
- Instruction hit count: `0`.

## Direction Modes

| mode | stream | reverse stream | initials | lasts | blanks | instruction hits |
|---|---|---|---|---|---:|---|
| `active_order_horizontal_outgoing` | `in collateralized a` | `a collateralized in` | `-ica` | `-nda` | `1` | - |
| `active_order_horizontal_incoming` | `he's to` | `to he's` | `h-t-` | `s-o-` | `2` | - |
| `active_order_vertical_outgoing` | `announced billions future trust` | `trust future billions announced` | `abft` | `dset` | `0` | - |
| `active_order_vertical_incoming` | `on was those` | `those was on` | `owt-` | `nse-` | `1` | - |
| `reverse_active_order_horizontal_outgoing` | `to he's` | `he's to` | `-t-h` | `-o-s` | `2` | - |
| `reverse_active_order_horizontal_incoming` | `a collateralized in` | `in collateralized a` | `aci-` | `adn-` | `1` | - |
| `reverse_active_order_vertical_outgoing` | `those was on` | `on was those` | `-two` | `-esn` | `1` | - |
| `reverse_active_order_vertical_incoming` | `trust future billions announced` | `announced billions future trust` | `tfba` | `tesd` | `0` | - |

## Active Target Inputs

| order | id | line | corridor | left | right | above | below |
|---:|---|---:|---:|---|---|---|---|
| 1 | `buying_dip` | 22 | 4 | `he's` | `-` | `on` | `announced` |
| 2 | `one_billion` | 25 | 7 | `-` | `in` | `was` | `billions` |
| 3 | `volcano_bonds` | 27 | 9 | `collateralized` | `to` | `future` | `those` |
| 4 | `shitcoiner_heart` | 32 | 14 | `a` | `-` | `trust` | `-` |

## Assessment

- The shared p73/p79 capsule direction signature is RRLL and is real as a five-index locator/provenance signal.
- Applying RRLL to horizontal side words around O4/B4/G5/O5 yields ordinary fragments such as `in collateralized a`, `he's to`, and `to he's`; no stream gives a word/letter/line/key instruction.
- Applying the same bounded test to vertical above/below neighbors yields ordinary fragments such as `announced billions future trust` and `on was those`; no stream gives a selector instruction.
- Reverse active order also fails to produce instruction-bearing text.
- This closes RRLL-as-active-quartet-side-selector for the current scan; it does not weaken page 76 as the target surface.

## Next Move

- Keep RRLL/five-index evidence as locator/provenance only; reopen side-word or vertical-neighbor extraction only if a raw clue names left/right, above/below, first/last word, or letter extraction.
