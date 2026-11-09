# 3D Viewer Layer Provenance

Scope: audit what the 3D browser viewer itself draws and whether it adds any hidden fold/mirror selector. No key derivation, hashing, seed phrase, WIF, or address checks were run.

## Viewer Controls

- Layout modes: `spread, fold, stack`
- Layer toggles: `togglePages, toggleChars, toggleImportant, toggleHighlights, toggleReflections, toggleAnchors, toggleRays`
- Hidden/extra layout modes: `none`
- Data source: `magazine.pdf` with OCR source `keyser bitcoin .pdf`

## Layer Findings

- Reflection pairs in JSON: `{(79, 75): 10, (78, 76): 4, (76, 78): 5, (79, 76): 10}`
- Mirror boxes use precomputed `targetBox`: `True`
- Ray endpoint page pairs: `{(76, 76): 40}`
- Rays total/visible/hidden: `40` / `28` / `12`
- `addRays()` forces page-76 world coordinates: `True`
- Original p79 anchor endpoint uses in raySelections: `0`
- Mirrored p79 anchor endpoint uses in raySelections: `43`

## Fold Geometry

| fold group | pages | fixed positions `[x,y,z,rotY]` |
|---|---|---|
| `topRow` | `75, 79` | `{'75': [-280.0, 320.0, -130.0, 0.42], '79': [280.0, 320.0, -130.0, -0.42]}` |
| `bottomRow` | `76, 78` | `{'76': [-280.0, -380.0, 130.0, 0.42], '78': [280.0, -380.0, 130.0, -0.42]}` |
| `centerBack` | `77` | `{'77': [0.0, -20.0, 330.0, 0.0]}` |
| `sideBack` | `80` | `{'80': [610.0, -20.0, 420.0, -0.2]}` |

## Hidden Ray Rows

| rank | mode | endpoints | text preview |
|---:|---|---|---|
| 29 | `ray_ab` | `p79_pill_1_mirror -> p79_pill_2_mirror` | `off the IMF those leeches. I tagged Novogratz in the tweet, bunch` |
| 30 | `ray_ab` | `p79_pill_4_mirror -> p76_black_bar_2` | `money bitcoin heads. psychotic and some Schiff It's` |
| 31 | `ray_ab` | `p79_pill_4_mirror -> p76_black_bar_2` | `It's Schiff some and psychotic heads. bitcoin money` |
| 32 | `ray_ba` | `p76_black_bar_2 -> p76_x_mark` | `Get freaking of buy euthanized bitcoin money` |
| 33 | `ray_ab` | `p79_pill_2_mirror -> p76_black_bar_2` | `money bitcoin euthanized heads. psychotic buy Schiff dumb bankers Brown parallel UTXO some` |
| 34 | `ray_ab` | `p79_pill_2_mirror -> p76_black_bar_2` | `some UTXO parallel Brown bankers dumb Schiff buy psychotic heads. euthanized bitcoin money` |
| 35 | `ray_ba` | `p79_pill_3_mirror -> p76_x_mark` | `trolling taunting President Nayib nation's should sell` |
| 36 | `ray_ab` | `p79_pill_2_mirror -> p76_black_bar_2` | `money bitcoin euthanized bankers Brown some` |
| 37 | `ray_ab` | `p79_pill_2_mirror -> p76_black_bar_2` | `some Brown bankers euthanized bitcoin money` |
| 38 | `ray_ab` | `p79_pill_5_mirror -> p76_black_bar_2` | `money bitcoin euthanized buy bankers Brown` |
| 39 | `ray_ab` | `p79_pill_5_mirror -> p76_black_bar_2` | `Brown bankers buy euthanized bitcoin money` |
| 40 | `segment` | `p79_pill_4_mirror -> p76_wire_left_knot` | `minds. in bitcoin skin nothing heart` |

## Assessment

- The 3D viewer exposes only the expected layout modes: spread, fold, and stack.
- Mirror boxes are drawn from precomputed targetBox coordinates in article_3d_map_data.json; the viewer does not calculate a new fold/mirror solution at runtime.
- Ray selectors are a page-76 hypothesis layer: all ray endpoint anchors used by raySelections are page-76 anchors, including mirrored p79-pill anchors already projected onto page 76.
- The viewer draws only the first 28 of 40 raySelections, so the browser view is an inspection aid rather than the complete ray dataset.
- The fold layout pairs pages 75/79 and 76/78 visually; it does not make 79/76 a physical contact pair.
- Browser-local text corrections can change the visible labels, but they are not geometry truth and do not alter the JSON source model.

## Decision

- Keep the 3D viewer as a manual orientation/review surface. Do not treat viewer fold depth, ray visibility, or browser-local correction state as a new selector. Measurements and source truth must come from high-res scan geometry, corrected/DOCM text witnesses, and generated reports.

## Next Move

- If the 3D view is used again, inspect it through the Text Authority/bridge sheets and avoid drawing conclusions from hidden rays or runtime layout depth. The next meaningful progress requires a new source image/original layout clue or an explicit unit/order rule.
