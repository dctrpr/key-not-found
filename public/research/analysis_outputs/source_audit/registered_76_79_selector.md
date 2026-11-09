# Registered 76/79 Selector Audit

Scope: apply the best high-res 76/79 mirror registration transform to page-79 orange highlight boxes, then remeasure which page-76 orange/grey targets they hit. This is a visual-selector test, not key derivation.

- Transform source: `analysis_outputs/source_audit/registration_rotation_scale_76_79.md`
- Transform: dx=20.0, dy=240.0, angle=2.0, scale=1.02
- Overlay: `analysis_outputs/source_audit/registered_76_79_selector_overlay.jpg`
- Crop: `analysis_outputs/source_audit/registered_76_79_selector_crop.jpg`

## Summary

- Raw p79 hflip intersections: 3 pattern `B1B1B2`
- Registered p79 intersections: 2
- Meaningful registered intersections: 2 pattern `B1B2`

## Meaningful Registered Intersections

- p79 box 1 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` -> p76 black 1 `Gotta be this way... post-1971 fiat money` (source=0.293, target=0.770, dist=10.0)
- p79 box 1 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` -> p76 black 2 `nonsense` (source=0.009, target=0.113, dist=815.9)

## Assessment

- The improved visual registration changes the p79 hit pattern and gives one strong line-level alignment.
- p79 box 1 (`infinitely more efficient...`) lands almost exactly on p76 grey box 1 (`Gotta be this way... post-1971 fiat money`): 77.0% of the target box is covered and the centers are only about 10 px apart.
- The same source box also clips the p76 `nonsense` continuation, so this is probably a broad line/row alignment rather than a word- or character-level selector.
- This promotes the transform as a useful orientation/registration clue, but it still does not provide a final extraction rule by itself.
- Next best move: use this registered line pair as a local anchor and inspect whether nearby p79/p76 typography, highlights, or Typeka states produce a smaller readable rule around the page-76 corridor.
