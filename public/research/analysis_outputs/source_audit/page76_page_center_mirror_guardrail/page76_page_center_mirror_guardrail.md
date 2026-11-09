# Page-76 Page-Center Mirror Guardrail

Scope: test the page-center 180-degree rotation and page-center horizontal/vertical mirrors as selectors for the locked O4/B4/G5/O5 quartet. This is an orientation/geometry guardrail only; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.

## Summary
- scenario count: `3`
- modes: `point_180, vertical_mirror, horizontal_mirror`
- page center: `[1272.0, 1632.0]`
- all-four active re-hit scenarios: `0`
- total highlight contacts: `1`
- strict instruction hits: `0`
- selector unlocked: `False`

## Scenario Results

| mode | active re-hits | word hits | focus words | highlight contacts | strict instruction hits |
|---|---:|---:|---:|---:|---|
| point_180 | 0 | 7 | 3 | 0 | - |
| vertical_mirror | 0 | 9 | 4 | 1 | - |
| horizontal_mirror | 0 | 6 | 1 | 0 | - |

## Projected Text Previews

### Page-center 180-degree rotation

- `buying_dip` -> box `[743.0, 1039.0, 1210.0, 1087.0]`; words `1`; highlights `0`; active re-hits `0`; preview `have`
- `one_billion` -> box `[1853.0, 819.0, 2116.0, 866.0]`; words `2`; highlights `0`; active re-hits `0`; preview `flat money`
- `volcano_bonds` -> box `[1348.0, 672.0, 1749.0, 720.0]`; words `4`; highlights `0`; active re-hits `0`; preview `ultimatums. It's the sound`
- `shitcoiner_heart` -> box `[883.0, 282.0, 1504.0, 332.0]`; words `0`; highlights `0`; active re-hits `0`; preview `-`

### Vertical page-center mirror

- `buying_dip` -> box `[743.0, 2177, 1210.0, 2225]`; words `3`; highlights `0`; active re-hits `0`; preview `them, telling them`
- `one_billion` -> box `[1853.0, 2398, 2116.0, 2445]`; words `0`; highlights `0`; active re-hits `0`; preview `-`
- `volcano_bonds` -> box `[1348.0, 2544, 1749.0, 2592]`; words `3`; highlights `0`; active re-hits `0`; preview `off the IMF`
- `shitcoiner_heart` -> box `[883.0, 2932, 1504.0, 2982]`; words `3`; highlights `1`; active re-hits `0`; preview `he's a siukbeodmensertslveaarty`

### Horizontal page-center mirror

- `buying_dip` -> box `[1334, 1039.0, 1801, 1087.0]`; words `2`; highlights `0`; active re-hits `0`; preview `shitcoiners' and`
- `one_billion` -> box `[428, 819.0, 691, 866.0]`; words `0`; highlights `0`; active re-hits `0`; preview `-`
- `volcano_bonds` -> box `[795, 672.0, 1196, 720.0]`; words `4`; highlights `0`; active re-hits `0`; preview `nailing the Vatican with`
- `shitcoiner_heart` -> box `[1040, 282.0, 1661, 332.0]`; words `0`; highlights `0`; active re-hits `0`; preview `-`

## Decision

- Do not promote page-center 180-degree rotation, vertical page-center mirroring, or horizontal page-center mirroring as a selector.
- The transforms do not re-hit the active quartet, do not produce a strict instruction surface, and do not improve the current OVERDOSE/layout evidence.
- Keep the operation as a coordinate-frame guardrail for future source comparison only.

## Outputs
- JSON: `analysis_outputs/source_audit/page76_page_center_mirror_guardrail/page76_page_center_mirror_guardrail.json`
- visual sheet: `analysis_outputs/source_audit/page76_page_center_mirror_guardrail/page76_page_center_mirror_guardrail_sheet.jpg`
