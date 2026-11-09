# Exact High-Res Reflection Geometry

Scope: rematch the manual high-res highlight source against 3D page words, then test reflected highlight boxes against those exact spans.
OCR text is used only for approximate geometry boxes; exact span text comes from the high-res manual source.

## Page 76 Exact Span Hits

- orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` match=11 ratio=1.0 hits=79_76_1 src=79 ovRefl=0.9566 ovSpan=0.2967 text=`but George Clinton and James Brown clones. It's Martin Luther nailing `; 79_76_2 src=79 ovRefl=0.9374 ovSpan=0.056 text=`Gotta be S way. Forty years of (and loyears of watching Peter`; 79_76_3 src=79 ovRefl=0.5185 ovSpan=0.0123 text=`miss buying bitcoin`
- orange `by the rancid catnip of fiat money.` match=3 ratio=0.429 hits=78_76_4 src=78 ovRefl=0.525 ovSpan=0.0548 text=`Have you seen the president of El Salvador`; 78_76_3 src=78 ovRefl=0.4583 ovSpan=0.1349 text=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`; 79_76_4 src=79 ovRefl=0.2834 ovSpan=0.0499 text=`Have you seen the president of El Salvador`
- orange `“buying the dip.”` match=2 ratio=0.667 hits=78_76_1 src=78 ovRefl=1.0 ovSpan=0.0692 text=`honéy-badgering him`; 79_76_3 src=79 ovRefl=0.7133 ovSpan=0.0347 text=`miss buying bitcoin`; 79_76_2 src=79 ovRefl=0.4529 ovSpan=0.0554 text=`Gotta be S way. Forty years of (and loyears of watching Peter`
- orange `shitcoiner at heart.` match=1 ratio=0.333 hits=none
- grey_black `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` match=9 ratio=0.75 hits=79_76_2 src=79 ovRefl=0.1968 ovSpan=0.1634 text=`Gotta be S way. Forty years of (and loyears of watching Peter`
- grey_black `It’s a stun gun to the genitals.` match=7 ratio=1.0 hits=78_76_1 src=78 ovRefl=0.7905 ovSpan=0.0249 text=`honéy-badgering him`; 79_76_2 src=79 ovRefl=0.6508 ovSpan=0.0362 text=`Gotta be S way. Forty years of (and loyears of watching Peter`; 79_76_1 src=79 ovRefl=0.571 ovSpan=0.1651 text=`but George Clinton and James Brown clones. It's Martin Luther nailing `; 78_76_3 src=78 ovRefl=0.5554 ovSpan=0.1158 text=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`
- grey_black `$1 billion` match=2 ratio=1.0 hits=79_76_5 src=79 ovRefl=0.9489 ovSpan=0.0517 text=`trolling the International Monetary Fund (IMF) on Twitter? taunting th`; 79_76_4 src=79 ovRefl=0.9489 ovSpan=0.0477 text=`Have you seen the president of El Salvador`; 78_76_4 src=78 ovRefl=0.9477 ovSpan=0.0282 text=`Have you seen the president of El Salvador`; 78_76_2 src=78 ovRefl=0.9282 ovSpan=0.0105 text=`Our imaginations`
- grey_black `“Volcano Bonds”` match=1 ratio=0.5 hits=none

## Stable Page 76 Geometry

- orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` sources=[79] hits=79_76_1(79->76, ovRefl=0.9566); 79_76_2(79->76, ovRefl=0.9374); 79_76_3(79->76, ovRefl=0.5185)
- orange `by the rancid catnip of fiat money.` sources=[78] hits=78_76_4(78->76, ovRefl=0.525); 78_76_3(78->76, ovRefl=0.4583)
- orange `“buying the dip.”` sources=[78, 79] hits=78_76_1(78->76, ovRefl=1.0); 79_76_3(79->76, ovRefl=0.7133); 79_76_2(79->76, ovRefl=0.4529)
- grey_black `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` sources=[79] hits=79_76_2(79->76, ovRefl=0.1968)
- grey_black `It’s a stun gun to the genitals.` sources=[78, 79] hits=78_76_1(78->76, ovRefl=0.7905); 79_76_2(79->76, ovRefl=0.6508); 79_76_1(79->76, ovRefl=0.571); 78_76_3(78->76, ovRefl=0.5554)
- grey_black `$1 billion` sources=[78, 79] hits=79_76_5(79->76, ovRefl=0.9489); 79_76_4(79->76, ovRefl=0.9489); 78_76_4(78->76, ovRefl=0.9477); 78_76_2(78->76, ovRefl=0.9282)

## Non-Page-76 Intersections

- p75 orange `They are the sum of all our neuroses.` -> 79_75_3 ovRefl=0.5204 ovSpan=0.0094 text=`Markets are`
- p75 orange `Fact: It’s Layer 1 for every great thing that’s ever been invented or discovered.` -> 79_75_5 ovRefl=0.3142 ovSpan=0.0521 text=`only the language of the shameless opportunists trying cash in by riding Bitcoins coattail`
- p78 grey_black `money printing` -> 76_78_1 ovRefl=0.2242 ovSpan=0.0558 text=`We've never had an economy and a money`

## Assessment

- Re-running geometry from the corrected high-res highlight text preserves the same page-76 concentration: opening toxicity/UTXO area, Peter-Schiff/fiat-money area, El Salvador/Bukele corridor, and `$1 billion`/IMF corridor.
- `Volcano Bonds` and `shitcoiner at heart` still do not get a strong reflected-box hit in the current OCR-derived geometry, so they remain semantic anchors rather than geometric intersections.
- The p78 correction removes overcaptured connector prose from text streams but does not change the main geometry conclusion.
- Next best move: affine-register the visual anchors on pages 76/78/79 and re-run this exact-span intersection from registered boxes, because current OCR boxes are good enough for regions but not exact letters.
