# G5/O5 High-Res Boundary Cut

Scope: inspect whether the repaired p78 frame's high-res visual edge creates a side-specific extraction unit at G5/O5. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T19:47:31`
- Overlay: `analysis_outputs/source_audit/g5_o5_highres_boundary_cut/g5_o5_highres_boundary_cut_overlay.jpg`
- Frame scenario: `g5_edge_touch`; frame left x: `1196.0`; grid left x: `1194.0`
- G5 box: `[795.0, 2544.0, 1196.0, 2592.0]` / text `Volcano Bonds`
- O5 box: `[1040.0, 2932.0, 1661.0, 2982.0]` / text `shitcoiner at heart.`

## O5 Pixel Boundary

- O5 dark-glyph ink box: `[1042, 2932, 1658, 2967]`
- O5 glyph groups: `[{'x0': 1042, 'x1': 1067, 'width': 25}, {'x0': 1073, 'x1': 1106, 'width': 33}, {'x0': 1113, 'x1': 1164, 'width': 51}, {'x0': 1169, 'x1': 1195, 'width': 26}, {'x0': 1202, 'x1': 1229, 'width': 27}, {'x0': 1235, 'x1': 1258, 'width': 23}, {'x0': 1264, 'x1': 1295, 'width': 31}, {'x0': 1300, 'x1': 1326, 'width': 26}, {'x0': 1333, 'x1': 1362, 'width': 29}, {'x0': 1386, 'x1': 1444, 'width': 58}, {'x0': 1469, 'x1': 1502, 'width': 33}, {'x0': 1507, 'x1': 1533, 'width': 26}, {'x0': 1540, 'x1': 1570, 'width': 30}, {'x0': 1576, 'x1': 1605, 'width': 29}, {'x0': 1610, 'x1': 1636, 'width': 26}, {'x0': 1644, 'x1': 1658, 'width': 14}]`
- O5 large word-like gaps: `[{'from': 1362, 'to': 1386, 'width': 24}, {'from': 1444, 'to': 1469, 'width': 25}]`
- Exact frame relation: `{'type': 'inside_gap', 'gapIndex': 4, 'gap': {'from': 1195, 'to': 1202, 'width': 7}, 'distanceToLeftGlyph': 1.0, 'distanceToRightGlyph': 6.0, 'isLargeWordGap': False}`
- Grid-frame relation: `{'type': 'inside_glyph_group', 'groupIndex': 4, 'group': {'x0': 1169, 'x1': 1195, 'width': 26}, 'distanceToLeft': 25.0, 'distanceToRight': 1.0}`
- Distance from exact frame edge to large word gaps: `[{'gap': {'from': 1362, 'to': 1386, 'width': 24}, 'distanceFromFrameLeft': 166.0}, {'gap': {'from': 1444, 'to': 1469, 'width': 25}, 'distanceFromFrameLeft': 248.0}]`

## Approximate Text Splits

| cut | split | right side | note |
|---|---|---|---|
| G5 at exact frame | `Volcano Bonds|` | `` | frame touches G5 right endpoint |
| O5 at exact dx=-38 frame | `shitc|oiner at heart.` | `oiner at heart.` | proportional text estimate; line is in a small intra-word glyph gap |
| O5 at grid dx=-40 frame | `shitc|oiner at heart.` | `oiner at heart.` | proportional text estimate; line is inside/near the same glyph cluster |

## Streams Checked

- `g5LeftOfFrame` hits=none: `Volcano Bonds`
- `g5RightOfFrame` hits=none: ``
- `o5ApproxSplitAtExactFrame` hits=none: `shitc|oiner at heart.`
- `o5ApproxSplitAtGridFrame` hits=none: `shitc|oiner at heart.`
- `o5ExactRightSide` hits=none: `oiner at heart.`
- `o5GridRightSide` hits=none: `oiner at heart.`
- `combinedExact` hits=none: `Volcano Bonds | oiner at heart.`
- `combinedGrid` hits=none: `Volcano Bonds | oiner at heart.`

## Assessment

- The repaired p78 frame left edge exactly coincides with the trusted G5 right boundary, so G5 is an endpoint registration contact.
- The same vertical edge cuts through O5 inside the word 'shitcoiner', not at a large visual word gap.
- The exact dx=-38 line lands in a small glyph gap near the approximate split 'shitc|oiner at heart.'; the dx=-40 grid variant is inside the same glyph cluster and only weakly supports a 'shit|coiner' visual snap.
- The nearest large O5 word gaps are the spaces after 'shitcoiner' and after 'at'; the frame edge is far from both, so this is not a clean word-boundary selector.
- This preserves the G5/O5 pair as source-registration evidence but closes side-specific high-res boundary cutting as a standalone extraction unit.

## Decision

- Do not use the G5/O5 side cut as extraction evidence; it is not a clean word/letter boundary under the current high-res scan.
- Next move: Inspect the high-res visual highlight boundaries for the broader four-anchor O-B-B-O set, looking only for exact boundary coincidences before any text extraction.
