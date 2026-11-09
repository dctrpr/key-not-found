# Content-Box Physical Normalization

Scope: test whether content-box-normalized physical reflection fixes the p77 -> O5 near miss or creates repeated trusted O5/G5 contacts. No key candidates were generated.

- Created: `2026-05-20T13:06:36`
- Overlay: `analysis_outputs/source_audit/content_box_physical_normalization/content_box_physical_normalization_overlay.jpg`

## Content Boxes

| page | content bbox |
|---:|---|
| `75` | `[25.0, 40.0, 2536.0, 3250.0]` |
| `76` | `[29.0, 10.0, 2536.0, 3249.0]` |
| `77` | `[24.0, 8.0, 2536.0, 3256.0]` |
| `78` | `[24.0, 9.0, 2529.0, 3256.0]` |
| `79` | `[32.0, 8.0, 2536.0, 3256.0]` |
| `80` | `[26.0, 8.0, 2536.0, 3256.0]` |

## True Physical Comparison

- Baseline best true physical: page `77` `It does this by monetizing` -> `O5`, shift `71.93` px.
- Normalized best true physical: page `77` `It does this by monetizing` -> `O5`, shift `65.49` px.
- Active p77 -> O5 baseline shift: `71.93` px.
- Active p77 -> O5 normalized shift: `65.49` px.
- Shift change: `-6.44` px.
- p77 direct hits after normalization: `0`.

## Model Ranking

| mode | model | page | direct hits | best target | source phrase | shift |
|---|---|---:|---:|---|---|---:|
| `full_page_hflip` | same physical leaf/front-back candidate | `75` | `0` | `G5_trusted` | `Don't fall for shitcoinery` | `233.82` |
| `content_box_normalized_hflip` | same physical leaf/front-back candidate | `75` | `0` | `G5_trusted` | `Don't fall for shitcoinery` | `254.03` |
| `full_page_hflip` | true facing spread/gutter candidate | `77` | `0` | `O5` | `It does this by monetizing` | `71.93` |
| `content_box_normalized_hflip` | true facing spread/gutter candidate | `77` | `0` | `O5` | `It does this by monetizing` | `65.49` |
| `full_page_hflip` | non-physical p78 visual-control source | `78` | `0` | `G5_trusted` | `the game-theorized Bitcoin protocol,` | `492.0` |
| `content_box_normalized_hflip` | non-physical p78 visual-control source | `78` | `0` | `G5_trusted` | `the game-theorized Bitcoin protocol,` | `496.03` |
| `full_page_hflip` | non-physical p79 visual-control source | `79` | `0` | `O5` | `[pill/graphic fragment, no article text]` | `382.34` |
| `content_box_normalized_hflip` | non-physical p79 visual-control source | `79` | `0` | `G5_trusted` | `We are getting our souls back and our minds.` | `395.94` |
| `full_page_hflip` | non-physical p80 package-control source | `80` | `0` | `G5_trusted` | `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` | `446.0` |
| `content_box_normalized_hflip` | non-physical p80 package-control source | `80` | `0` | `G5_trusted` | `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` | `449.79` |

## Assessment

- Content-box normalization is a plausible crop/trim repair, but it does not create direct trusted O5/G5 contacts for the true physical p75/p77 models.
- For the active p77 `It does this by monetizing` -> O5 near miss, the required shift changes from 71.93 px to 65.49 px.
- p77 direct trusted-hit count remains 0 after normalization.
- This keeps C4 failed under the current scan and keeps physical/source acquisition as the dependency.

Next move: If a new physical/original-layout source appears, run this same full-page vs content-box benchmark first; do not treat content-box normalization as extraction material by itself.
