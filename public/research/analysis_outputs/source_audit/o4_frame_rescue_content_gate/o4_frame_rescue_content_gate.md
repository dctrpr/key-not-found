# O4 Frame Rescue Content Gate

Scope: check whether the `3-up / 1-down` O4 frame-rescue envelope isolates the active quartet. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:48:02`
- Full-coverage frame: `[294.0, 2176.81, 2250.0, 3023.73]`
- Included line range: `22-32`
- Included corridor range: `4-14`
- Included words: `102`
- Active-target words: `10`
- Non-target words: `92`
- Active-target word density: `0.098`
- Non-active highlight entries: `4`
- Non-active bold-context lines: `5`
- Hard instruction hits: `[]`
- Sheet: `analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate_sheet.jpg`

## Included Lines

| line | corridor | words | active targets | hard hits | context hits | text |
|---:|---:|---:|---|---|---|---|
| `22` | `4` | `11` | `buying_dip` | `-` | `dip` | He's taunting them, telling them he's “buying the dip.” |
| `23` | `5` | `8` | `-` | `-` | `-` | I tweeted President Nayib Bukele when he announced |
| `24` | `6` | `11` | `-` | `-` | `-` | he was going to tap his nation's volcanoes to mine |
| `25` | `7` | `8` | `one_billion` | `-` | `bitcoin, sell` | $1 billion in bitcoin — that he should sell |
| `26` | `8` | `6` | `-` | `-` | `bitcoin` | billions worth of future bitcoin earnings |
| `27` | `9` | `8` | `volcano_bonds` | `-` | `bonds, imf, volcano` | collateralized “Volcano Bonds” to pay off the IMF |
| `28` | `10` | `10` | `-` | `-` | `mike` | loan and get rid of those leeches. I tagged Mike |
| `29` | `11` | `9` | `-` | `-` | `sell` | Novogratz in the tweet, figuring he could sell a |
| `30` | `12` | `11` | `-` | `-` | `-` | bunch to his Wall Street crony pals, but so far he |
| `31` | `13` | `12` | `-` | `-` | `-` | hasn't moved on it. I don't really trust that guy. |
| `32` | `14` | `8` | `shitcoiner_heart` | `-` | `heart, shitcoiner` | Maybe because he's a shitcoiner at heart. |

## Non-Active Highlight/Bold Content

- L27: `bold: IMF`
- L28: `bold-partial/full: Mike`
- L29: `bold-partial: Novogratz`
- L31: `bold partial: I don't really trust that guy`
- L23 C5: bold `PresidentNayibBukele` partial `` active `-`
- L27 C9: bold `IMF` partial `` active `volcano_bonds`
- L28 C10: bold `loanie` partial `ie` active `-`
- L29 C11: bold `Nvz` partial `Nvz` active `-`
- L31 C13: bold `Idelluhu` partial `delluhu` active `-`

## Decision

- The `3-up / 1-down` frame fully covers the active quartet, but it captures a full L22-L32 corridor band rather than isolating only the target phrases.
- It contains `92` non-target words and `4` non-active highlight entries.
- It has zero hard instruction hits in the exact corridor text.
- Treat this as a future source/original-layout validation benchmark only, not extraction permission under the current scan.
