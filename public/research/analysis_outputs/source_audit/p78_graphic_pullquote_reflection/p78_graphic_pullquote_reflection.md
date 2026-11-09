# P78 Graphic Pull-Quote Reflection Audit

Scope: treat the lower page-78 brush/pull-quote as scan-visible graphic text outside the 3D map text layer, then mirror it onto page 76. No key derivation was run.

- Graphic text: `The economy of love is infinitely more efficient than hate and war.`
- p78 graphic box: `[294, 2398, 1310, 2950]`
- reflected p76 box: `[1234, 2398, 2250, 2950]`
- component count: `13`
- crop: `analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_crop.jpg`
- overlay: `analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflected_on_p76.jpg`

## Intersections With Page-76 Highlight Units

- `p76_orange_5` orange `shitcoiner at heart`: bboxOverlapVsTarget=`0.247536`, maskPixels=`227`, maskDensity=`0.007311`
- `p76_grey_5` grey `Volcano Bonds`: bboxOverlapVsTarget=`0.277603`, maskPixels=`936`, maskDensity=`0.019685`

## Assessment

- This confirms a missing visual/text layer: the lower p78 graphic repeats the `economy of love... hate and war` line, but it is not captured as exact 3D-map article text.
- Mirroring the graphic's dark pixels onto p76 puts them over the lower-right page-76 art/corridor zone, not into a clean single word/letter target.
- The strongest overlap is broad-area context, not a precise selector. Keep this as orientation/provenance evidence tied to the `FUCK`/X/brush system unless a physical scan or explicit rule says how to use the graphic.
- Next best move: if the Canva `FUCK ALL SHITCOINS` alignment is reopened with higher-resolution evidence, include this p78 graphic layer as a first-class visual object rather than treating it as normal article text.
