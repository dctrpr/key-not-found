# P78 Graphic Word-Intersection Audit

Scope: intersect the mirrored p78 lower graphic with p76 word labels, using dark brush pixels and approximate negative text holes. OCR boxes are labels only. No key derivation was run.

- Reflected p76 box: `[1234, 2398, 2250, 2950]`
- Overlay: `analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections_overlay.jpg`
- Words considered: `32`
- Words inside reflected box: `22`
- Dark-mask hits: `14`
- Negative-hole hits: `12`

## Streams

- `bboxStream`: `should sell earnings pay off the IMF I tagged Mike he could sella pals, but so far he trust that guy siukbeodmensertslveaarty`
- `darkHitStream`: `earnings off the IMF tagged Mike could sella pals, far he trust guy siukbeodmensertslveaarty`
- `holeHitStream`: `off the IMF tagged Mike could sella pals, far trust guy siukbeodmensertslveaarty`

## Top Dark Hits

- `siukbeodmensertslveaarty` idx `264` darkPixels=`2339` density=`0.048964` center=`False`
- `IMF` idx `220` darkPixels=`2054` density=`0.691582` center=`True`
- `sella` idx `238` darkPixels=`1942` density=`0.449537` center=`True`
- `off` idx `218` darkPixels=`1617` density=`0.704575` center=`True`
- `Mike` idx `230` darkPixels=`1500` density=`0.396825` center=`False`
- `tagged` idx `229` darkPixels=`1379` density=`0.237554` center=`True`
- `he` idx `249` darkPixels=`1296` density=`0.981818` center=`True`
- `pals,` idx `245` darkPixels=`945` density=`0.256793` center=`False`
- `could` idx `237` darkPixels=`797` density=`0.19925` center=`False`
- `trust` idx `257` darkPixels=`631` density=`0.138834` center=`False`
- `guy` idx `259` darkPixels=`379` density=`0.120317` center=`False`
- `the` idx `219` darkPixels=`322` density=`0.130101` center=`False`
- `earnings` idx `214` darkPixels=`185` density=`0.026278` center=`False`
- `far` idx `248` darkPixels=`177` density=`0.086765` center=`False`

## Top Negative-Hole Hits

- `Mike` idx `230` holePixels=`2154` density=`0.569841` center=`True`
- `sella` idx `238` holePixels=`1149` density=`0.265972` center=`False`
- `siukbeodmensertslveaarty` idx `264` holePixels=`541` density=`0.011325` center=`False`
- `IMF` idx `220` holePixels=`399` density=`0.134343` center=`False`
- `tagged` idx `229` holePixels=`255` density=`0.043928` center=`False`
- `guy` idx `259` holePixels=`253` density=`0.080317` center=`False`
- `the` idx `219` holePixels=`238` density=`0.096162` center=`False`
- `could` idx `237` holePixels=`149` density=`0.03725` center=`False`
- `off` idx `218` holePixels=`85` density=`0.037037` center=`False`
- `far` idx `248` holePixels=`66` density=`0.032353` center=`False`
- `pals,` idx `245` holePixels=`63` density=`0.01712` center=`False`
- `trust` idx `257` holePixels=`28` density=`0.006161` center=`False`

## Assessment

- The mirrored p78 graphic lands on a coherent p76 phrase band: `should sell`, `earnings`, `to pay off the IMF`, `I tagged Mike`, `he could sell`, `but so far he`, `trust that guy`, plus the lower `shitcoiner at heart` OCR blob.
- The dark and hole masks do not select a clean word order or instruction. They are too broad and include visual-art collision.
- Keep this as corroborating evidence for the lower p76 corridor, not as a standalone selector. A future rule would still need to specify whether to read through dark brush, white holes, bounding box, or adjacent words.
