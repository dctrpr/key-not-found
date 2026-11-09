# Graphic Spill Alignment Inventory

Scope: inventory the Canva-named `XX` / barbed-wire / `SHIT`-spill graphic layer across pages 78-80. This is a visual registration pass only; no key derivation was run.

- Created: `2026-05-20T08:54:01`
- Sheet: `analysis_outputs/source_audit/graphic_spill_alignment_inventory/graphic_spill_alignment_inventory_sheet.jpg`
- Manual object boxes are approximate visual annotations on the current high-res magazine scan.

## P78 `XX` / FUCK Graphic To P79 Barbed Wire

- P79 wire angle: `-26.83` degrees.

| transform | X-pair angle | angle delta vs wire | left X to wire | right X to wire | FUCK center to wire | nearest left X | nearest right X |
|---|---:|---:|---:|---:|---:|---|---|
| `identity` | `-1.71` | `25.12` | `2257.7` | `2598.5` | `2367.5` | `p79_pill_4 136.5px` | `p79_max_signature 176.7px` |
| `hflip` | `-178.29` | `28.54` | `3119.4` | `2735.8` | `2917.7` | `p79_max_signature 1040.4px` | `p79_max_signature 279.4px` |
| `vflip` | `1.71` | `28.54` | `90.2` | `473.9` | `291.9` | `p79_wire_left_knot 195.0px` | `p79_wire_right_knot 617.7px` |
| `rot180` | `178.29` | `25.12` | `951.9` | `611.1` | `842.1` | `p79_wire_right_knot 1688.4px` | `p79_wire_right_knot 905.0px` |

## P80 Package / SHITCOINS To P79 Marks

| source | transform | nearest p79 marks |
|---|---|---|
| `p80_symptoms` | `hflip` | p79_pill_3=283.5px, p79_pill_2=431.8px, p79_pill_4=520.1px |
| `p80_symptoms` | `rot180` | p79_wire_right_knot=668.4px, p79_wire_span=688.2px, p79_wire_left_knot=823.9px |
| `p80_symptoms` | `vflip` | p79_wire_right_knot=1284.4px, p79_wire_span=1370.1px, p79_wire_left_knot=1612.7px |
| `p80_shitcoins` | `hflip` | p79_pill_3=235.3px, p79_pill_2=439.2px, p79_pill_4=449.3px |
| `p80_shitcoins` | `rot180` | p79_wire_right_knot=561.6px, p79_wire_span=592.7px, p79_wire_left_knot=765.9px |
| `p80_shitcoins` | `vflip` | p79_wire_right_knot=1246.7px, p79_wire_span=1340.5px, p79_wire_left_knot=1601.9px |
| `p80_volume_16` | `hflip` | p79_max_signature=529.1px, p79_pill_3=853.5px, p79_pill_2=1036.3px |
| `p80_volume_16` | `rot180` | p79_wire_right_knot=1055.1px, p79_wire_span=1135.8px, p79_wire_left_knot=1373.4px |
| `p80_volume_16` | `vflip` | p79_wire_right_knot=763.0px, p79_wire_span=818.9px, p79_wire_left_knot=1018.7px |
| `p80_cap_5_symptom` | `hflip` | p79_wire_span=701.9px, p79_wire_right_knot=704.2px, p79_wire_left_knot=784.4px |
| `p80_cap_5_symptom` | `rot180` | p79_pill_3=265.3px, p79_pill_2=344.2px, p79_pill_4=505.1px |
| `p80_cap_5_symptom` | `vflip` | p79_max_signature=831.6px, p79_pill_3=1194.7px, p79_pill_2=1361.3px |

## Assessment

- The obvious p78 `XX` pair does not become collinear with the p79 barbed-wire line under identity, hflip, vflip, or 180-degree rotation.
- The best simple p78 transform for keeping both X marks near the p79 wire is `vflip`, but its worst X-to-wire distance is 473.9 px and the angle delta is 28.54 degrees.
- p80 `SHITCOINS` and symptom text continue to map only as broad package/provenance evidence under simple flips; they do not pick a page-79 or page-76 unit.
- This supports the Canva note as an orientation/source-registration warning, not as a solved selector in the current high-res scan.

## Next Move

- Do not derive key material from `XX`/wire/SHIT spill geometry in the current scan. Reopen this branch only with a higher-resolution Canva/original-layout/physical overlay, or if a new source rule names which graphic object pair is meant.
