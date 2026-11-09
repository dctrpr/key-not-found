# Manual Correspondence Sheet 76/79

Scope: create a visual inspection sheet for manually marking true correspondences between page 76 and mirrored/transformed page 79.
This does not extract or check key material.

- Transform used: dx=20, dy=240, angle=2deg, scale=1.02
- Sheet: `analysis_outputs/source_audit/manual_correspondence_sheet_76_79.jpg`

## Regions

- `wire_open_heart`: `(1450, 120, 2544, 820)`
- `fiat_nonsense`: `(1450, 760, 2544, 1450)`
- `el_salvador_imf`: `(1450, 1450, 2544, 2350)`
- `pills_dollar_marks`: `(1450, 2280, 2544, 3264)`

## How To Use

- Look for points that are the same physical mark in the page76 panel and the transformed page79 panel.
- Good candidates should be visible in the blend and pink in the mask panel.
- Avoid using repeated body text as correspondence points because it creates false alignments.
- Candidate manual points should come from wire knots/crossings, pill tips, dollar/X strokes, or hard edges of black bars/highlights.

## Assessment

- This artifact turns the current best global transform into a practical manual-marking view.
- If no 4+ non-text correspondences are obvious here, the 76/79 visual system should remain orientation evidence rather than letter-level geometry.
- Visual inspection result:
  - `wire_open_heart`: the transformed page-79 wire crosses the page-76 opening orange line, but page 76 does not provide the same wire object as a direct correspondence point.
  - `fiat_nonsense`: overlap is dominated by body text and highlight bars; this region is not suitable for non-text correspondence marking.
  - `el_salvador_imf`: the side label and highlighted phrases align regionally, but the visible marks are mostly text/highlights, not stable shared art points.
  - `pills_dollar_marks`: the transformed page-79 pills and page-76 X/dollar marks coexist in the same region, but they are different mark families and do not give clear one-to-one correspondences.
- Conclusion: the current improved 76/79 overlay still does not provide four trustworthy non-text correspondence points for a manual affine transform.
- Next move: treat the 76/79 art system as orientation/region evidence and shift the next pass to another physical relationship, especially front/back leaf 76/75 or 78/77, where true hold-to-light correspondence may be more literal.
