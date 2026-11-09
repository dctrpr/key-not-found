# Calibrated Anchor Visual-Marks Audit

Scope: inspect the immediate crop around the unique registered 76/79 anchor for non-text visual marks that could provide the missing ordering cue. The script masks OCR word boxes and then separately removes the known aligned highlight boxes. No key derivation was run.

- Crop: `(350, 650, 2200, 1050)`
- Transform: dx=20.0, dy=240.0, angle=2.0, scale=1.02
- Preview: `analysis_outputs/source_audit/calibrated_anchor_visual_marks.jpg`

## Known Anchor Removed

- p76: `B1 Gotta be this way... post-1971 fiat money` box=`[449, 827, 2233, 890]`
- p76: `B2 nonsense` box=`[374, 890, 701, 959]`
- p79_registered: `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` box=`[664, 748, 2037, 963]`

## Mask Statistics

- p76 residual after text masking: 32769 px, 35 components
- registered p79 residual after text masking: 96137 px, 12 components
- residual overlap before known-anchor removal: 16685 px
- p76 extra after known-anchor removal: 11453 px, 33 components
- registered p79 extra after known-anchor removal: 14442 px, 11 components
- extra overlap after known-anchor removal: 212 px

## Largest Extra Components

- p76 extra components:
  - area=737 box=[709, 908, 844, 961] size=135x53
  - area=736 box=[2152, 739, 2199, 772] size=47x33
  - area=558 box=[2154, 982, 2200, 1015] size=46x33
  - area=557 box=[2153, 917, 2200, 943] size=47x26
  - area=551 box=[2161, 674, 2200, 707] size=39x33
  - area=377 box=[597, 996, 619, 1020] size=22x24
  - area=328 box=[645, 681, 671, 704] size=26x23
  - area=327 box=[1402, 740, 1421, 774] size=19x34
- registered p79 extra components:
  - area=6592 box=[666, 650, 1125, 684] size=459x34
  - area=1843 box=[1769, 686, 1983, 738] size=214x52
  - area=1827 box=[686, 715, 834, 740] size=148x25
  - area=1714 box=[692, 998, 803, 1041] size=111x43
  - area=243 box=[1102, 710, 1118, 740] size=16x30
  - area=233 box=[1607, 702, 1621, 728] size=14x26
  - area=214 box=[1713, 982, 1725, 1015] size=12x33
  - area=177 box=[1867, 988, 1881, 1013] size=14x25

## Assessment

- The immediate calibrated anchor crop is dominated by the known p79 orange highlight / p76 grey highlight alignment.
- After removing text boxes and the known aligned highlight boxes, the remaining marks are edge fragments/noise rather than clear pills, wire knots, X marks, or ordering symbols.
- This means the unique anchor is useful for calibration but does not itself contain a visible local ordering cue.
- Next best move: inspect the broader page-76/page-79 visual system outside this crop, especially the Canva-mentioned `XX`/barbed-wire/`SHIT`/`FUCK ALL SHITCOINS` alignment, or acquire a higher-resolution physical/source overlay.
