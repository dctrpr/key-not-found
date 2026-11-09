# Page-76 Active Target Crop Completion

Scope: build a complete visual reference for O4/B4/G5/O5 on the high-res upright page-76 image. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.

- Created: `2026-05-20T23:44:12`
- Sheet: `analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion_sheet.jpg`
- Decision: `page76_active_target_crop_authority_complete_no_selector`

## Summary

- Crop coverage: `4/4`
- Active color pattern: `OBBO`
- Active visual-state order: `YKKY`
- Page lines: `22 25 27 32`
- Corridor indexes: `4 7 9 14`
- Selector unlocked: `False`

## Targets

| target | line/corridor | visual | box | crop | source | output |
|---|---|---|---|---|---|---|
| `O4 buying the dip` | `L22/C4` | `Y` | `[1334, 2177, 1801, 2225]` | `[1120, 2125, 1910, 2265]` | highres_highlight_audit.visualOrangeRows.p76_orange_4 | `analysis_outputs/source_audit/page76_active_target_crop_completion/buying_dip_crop.jpg` |
| `B4 $1 billion` | `L25/C7` | `K` | `[428, 2398, 691, 2445]` | `[250, 2350, 1520, 2460]` | full-page visual inspection; old projected grey box was known wrong | `analysis_outputs/source_audit/page76_active_target_crop_completion/one_billion_crop.jpg` |
| `G5 Volcano Bonds` | `L27/C9` | `K` | `[795, 2544, 1196, 2592]` | `[720, 2505, 1650, 2625]` | page76_priority_crop_pack.L27_G5_pair | `analysis_outputs/source_audit/page76_active_target_crop_completion/volcano_bonds_crop.jpg` |
| `O5 shitcoiner at heart` | `L32/C14` | `Y` | `[1040, 2932, 1661, 2982]` | `[850, 2860, 1770, 3038]` | highres_highlight_audit.visualOrangeRows.p76_orange_5 + page76_priority_crop_pack.L32_O5_primary | `analysis_outputs/source_audit/page76_active_target_crop_completion/shitcoiner_heart_crop.jpg` |

## Caveat

- The older grey projection boxes for p76 `$1 billion` and `Volcano Bonds` are not used as geometry authority here because the grey-reading audit already flags them as landing on wrong lower-page text.
- This sheet completes crop documentation only; it does not add unit/order evidence.

## Next Move

- Use this completed O4/B4/G5/O5 sheet for future physical/original-layout/source comparison. Do not reopen current-scan extraction without R3 unit/order evidence.
