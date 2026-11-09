# C9 Bold/Highlight Format Density

Scope: check page-76 line-level bold/highlight evidence inside the C9 frame band. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T02:31:37`
- C9 frame: `[294.0, 2176.81, 2250.0, 3023.73]`
- Sheet: `analysis_outputs/source_audit/c9_bold_highlight_format_density/c9_bold_highlight_format_density_sheet.jpg`

## Summary

- C9 corridor line count: `11`.
- Active target lines: `4`.
- Format-signal lines: `8`; non-active format-signal lines: `4`.
- Active bold-letter stream: `buyingthedipIMFshitcoineratheart`.
- Non-active bold-letter stream: `PresidentNayibBukeleloanieNvzIdelluhu`.
- Exact active phrase matches in bold letters: `2/4`.
- Hard instruction hits in bounded format streams: `0` (`[]`).

## C9 Line Format Rows

| line/corridor | active target | bold letters | partial bold | highlight tags |
|---|---|---|---|---|
| `L22/C4` | `O4` | `buyingthedip` | `-` | `orange: buying the dip` |
| `L23/C5` | `-` | `PresidentNayibBukele` | `-` | `-` |
| `L24/C6` | `-` | `-` | `-` | `-` |
| `L25/C7` | `B4` | `-` | `-` | `grey: $1 billion` |
| `L26/C8` | `-` | `-` | `-` | `-` |
| `L27/C9` | `G5` | `IMF` | `-` | `grey: Volcano Bonds; bold: IMF` |
| `L28/C10` | `-` | `loanie` | `ie` | `bold-partial/full: Mike` |
| `L29/C11` | `-` | `Nvz` | `Nvz` | `bold-partial: Novogratz` |
| `L30/C12` | `-` | `-` | `-` | `-` |
| `L31/C13` | `-` | `Idelluhu` | `delluhu` | `bold partial: I don't really trust that guy` |
| `L32/C14` | `O5` | `shitcoineratheart` | `-` | `orange: shitcoiner at heart` |

## Active Bold Match Check

- Match: `buying_dip` on line `22` has bold letters `buyingthedip`.
- Match: `shitcoiner_heart` on line `32` has bold letters `shitcoineratheart`.
- Mismatch: `one_billion` on line `25` expected `$1billion` but line-level bold letters are `-`.
- Mismatch: `volcano_bonds` on line `27` expected `VolcanoBonds` but line-level bold letters are `IMF`.

## Decision

- Do not promote C9 bold-letter or general highlight density as a selector.
- The line-level bold stream does not match all four active targets and includes non-active controls.
- Keep C9/YK as source-validation only. Reopen extraction only if a new source/clue explicitly names bold letters, highlight colors, or a format-unit order.
