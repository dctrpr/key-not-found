# High-Res Page 76 Mirror Selector

Scope: high-res magazine geometry only. Reflect orange highlight boxes from pages 78 and 79 onto high-res page 76, then measure intersections with high-res page-76 orange and black/grey highlight boxes.

- Overlay: `analysis_outputs/source_audit/highres_page76_mirror_selector_overlay.jpg`

## Summary

- Page-76 orange boxes: 5
- Page-76 manual grey/black text boxes: 5
- Reflected source boxes from p78/p79: 14
- Raw intersections: 4
- Meaningful intersections: 4
- Meaningful target pattern: `B1B1B2O3`
- Meaningful source-page pattern: `79797978`

## Meaningful Intersections

- p79 box 2 `That's right, Bitcoin will take all the energy.` -> p76 black 1 `Gotta be this way... post-1971 fiat money` (source=0.706, target=0.431, dist=297.8)
- p79 box 3 `all the energy.` -> p76 black 1 `Gotta be this way... post-1971 fiat money` (source=0.258, target=0.059, dist=420.2)
- p79 box 2 `That's right, Bitcoin will take all the energy.` -> p76 black 2 `nonsense` (source=0.022, target=0.068, dist=508.7)
- p78 box 3 `$2 trillion fiat cuck-bucks.` -> p76 orange 3 `buying the dip.` (source=0.164, target=0.650, dist=557.0)

## Assessment

- Direct high-res horizontal mirroring from pages 78/79 onto page 76 does not create a clean one-to-one selector across the page-76 highlighted phrases.
- The useful signal remains regional: page-76 lower/middle highlighted areas are plausible targets, but simple high-res page-center hflip alone is not the final rule.
- Next best move: use the high-res overlay as the base for a constrained manual mirror-writing rule, likely adding fold/spine translation or physical spread positioning rather than raw page-center hflip.
