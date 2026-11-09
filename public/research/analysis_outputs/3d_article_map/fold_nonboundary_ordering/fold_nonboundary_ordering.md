# 3D Fold Non-Boundary Ordering

Scope: inspect whether the 3D fold view reveals an ordering cue that is not just box boundaries. No text extraction, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T19:56:24`
- Overlay: `analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering_plan.jpg`

## Fold Pairing From Viewer

| pair | same row | same depth | rotations |
|---|---|---|---|
| `[75, 79]` | `True` | `True` | `[0.42, -0.42]` |
| `[76, 78]` | `True` | `True` | `[0.42, -0.42]` |
| `[79, 76]` | `False` | `False` | `[-0.42, 0.42]` |

## Active Anchor World Positions

| id | label | color | page center | fold world xyz |
|---|---|---|---|---|
| `buying_dip` | `buying the dip` | `orange` | `[1544.0, 2193.0]` | `[-225.36, -503.42, 105.6]` |
| `one_billion` | `$1 billion` | `black` | `[560.0, 2423.5]` | `[-423.03, -554.13, 193.87]` |
| `volcano_bonds` | `Volcano Bonds` | `black` | `[995.5, 2568.0]` | `[-335.54, -585.92, 154.8]` |
| `shitcoiner_heart` | `shitcoiner at heart` | `orange` | `[1350.5, 2957.0]` | `[-264.23, -671.5, 122.96]` |

## Orders Checked

- `page76VisualTopToBottom`: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`
- `foldDepthFrontToBackZLowToHigh`: `buying_dip -> shitcoiner_heart -> volcano_bonds -> one_billion`
- `foldXLeftToRight`: `one_billion -> volcano_bonds -> shitcoiner_heart -> buying_dip`

## Reflection Rows Near Active Anchors

| reflection | source | preview | best anchor | overlap | target distance | source-target fold distance |
|---|---:|---|---|---:|---:|---:|
| `79_76_5` | `79` | `trolling the International Monetary Fund (IMF) on Twitter? taunting them, telling them he'` | `buying_dip` | `7270.56` | `77.17` | `921.25` |
| `79_76_4` | `79` | `Have you seen the president of El Salvador` | `buying_dip` | `0.0` | `81.65` | `938.23` |

## Assessment

- The viewer's fold layout itself pairs pages 75/79 and 76/78 as symmetric rows; page 79 and page 76 are diagonal in the fold display, not a direct folded pair.
- Within page 76, the active O-B-B-O anchors keep ordinary page order top-to-bottom. The alternative depth ordering is just a yaw artifact of the page-76 plane, not an independent clue.
- Original p79 pill markers sit on the top-row p79 plane in the fold layout; their mirrored copies on page 76 are already an overlay hypothesis, not a new fold-view order.
- Reflected rectangles that land near the active lower corridor remain far apart from their source rectangles in fold-world distance; the 3D fold view does not create a new physical contact or ordering cue.
- This keeps the 3D fold view useful as orientation/provenance evidence only. A new selector must come from source/physical instruction, not another fold-display order.

## Decision

- Do not promote 3D fold display ordering to extraction evidence; it is an orientation view.
- Next move: Stop deriving selectors from display geometry; the next bounded pass should audit source/provenance clues for an explicit extraction instruction or compare physical/source images if available.
