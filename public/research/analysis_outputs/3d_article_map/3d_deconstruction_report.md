# 3D Article Map Deconstruction

## What Was Built

- High-res page planes for article pages 75-80.
- 7,299 OCR characters mapped onto the high-res page coordinate system.
- 1,243 OCR words mapped as selectable/scored text regions.
- Orange highlight boxes, reflected highlight boxes, visual anchors, and top anchor-ray selectors layered into one 3D scene.
- Text correction overlay:
  - page/line selector;
  - original OCR line preview;
  - exact-text input with manual markup;
  - browser-local saved corrections;
  - exportable correction JSON.
  - corrected lines rebuild the visible letter layer across the original line box without destroying the raw OCR source data.
  - supported markup:
    - `**bold word**` or `**l**` for bold words/letters;
    - `[[orange highlighted section]]` for manual orange highlights;
    - `{{black highlighted section}}` for manual black/inverted highlights.
- Three layouts:
  - `Spread`: readable page board.
  - `Fold`: physical/mirror hypothesis view.
  - `Stack`: depth comparison view.

## Immediate Read

- Page 76 remains the highest-density target. It has 95 currently important/scored words, far above the other pages.
- The 3D ray layer again points into the same semantic cluster: President, Nayib, El Salvador, IMF, volcanoes, Bitcoin Magazine, and bitcoin money.
- The anchor rays are contextual selectors, not clean key extractors. Their direct hash and index checks already returned zero activity.
- The reflected highlights remain intentional-looking, but they behave more like a clue/orientation layer than a finished key string.

## Current Interpretation

- The strongest visible structure is not “every highlighted phrase is the key.”
- It looks more like a multi-stage instruction system:
  1. Mirror/fold the page geometry.
  2. Use visual marks to identify the correct region.
  3. Use the El Salvador/Bukele/volcano cluster as the target zone.
  4. Apply an additional selector/order rule that has not been isolated yet.

## What This Rules Down

- Direct prose hashing from the ray-selected words is low-value.
- OCR word-index streams from ray-selected words are low-value.
- Repeating broad private-key checks over the same geometry is unlikely to help without a new selector.

## Best Next Experiment

Use the 3D map for manual geometric inspection and correction, not more automated hashing. First correct OCR lines that matter around page 76 and the reflected/mirror target regions, then compare other Max Keiser OVERDOSE layouts, especially `Bitcoin Is A Mirror That Reflects All`, looking for:

- repeated pill/wire/X/dollar marks;
- same fold pair geometry;
- repeated page-side placement;
- a repeated count/order convention;
- a visual rule that says which selected words or letters to keep.

If the same visual grammar appears in another OVERDOSE article, it can separate deliberate mechanism from coincidence.
