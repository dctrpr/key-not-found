# Color Reflection Geometry

Scope: match annotated color-highlight phrases onto 3D OCR word boxes, then test whether reflected highlight boxes land on those colored phrase boxes.

## Page 76 Hits
- orange phrase=`Get some toxicity. Get some bitcoin. Open your heart to Bitcoin` match=11 ratio=1.0 reflectionHits=79_76_1 ovSpan=0.2967 text=`but George Clinton and James Brown clones. It's Martin Luther nailing `; 79_76_2 ovSpan=0.056 text=`Gotta be S way. Forty years of (and loyears of watching Peter`; 79_76_3 ovSpan=0.0123 text=`miss buying bitcoin`
- grey phrase=`Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` match=9 ratio=0.75 reflectionHits=79_76_2 ovSpan=0.1634 text=`Gotta be S way. Forty years of (and loyears of watching Peter`
- orange phrase=`by the rancid catnip of fiat money` match=3 ratio=0.429 reflectionHits=78_76_3 ovSpan=0.1349 text=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`; 78_76_4 ovSpan=0.0548 text=`Have you seen the president of El Salvador`; 79_76_4 ovSpan=0.0499 text=`Have you seen the president of El Salvador`
- grey phrase=`It's a stun gun to the genitals` match=7 ratio=1.0 reflectionHits=79_76_1 ovSpan=0.1651 text=`but George Clinton and James Brown clones. It's Martin Luther nailing `; 78_76_3 ovSpan=0.1158 text=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`; 79_76_2 ovSpan=0.0362 text=`Gotta be S way. Forty years of (and loyears of watching Peter`
- orange phrase=`buying the dip` match=2 ratio=0.667 reflectionHits=78_76_1 ovSpan=0.0692 text=`honéy-badgering him`; 79_76_2 ovSpan=0.0554 text=`Gotta be S way. Forty years of (and loyears of watching Peter`; 79_76_3 ovSpan=0.0347 text=`miss buying bitcoin`
- grey phrase=`$1 billion` match=2 ratio=1.0 reflectionHits=78_76_3 ovSpan=0.0632 text=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`; 79_76_5 ovSpan=0.0517 text=`trolling the International Monetary Fund (IMF) on Twitter? taunting th`; 79_76_4 ovSpan=0.0477 text=`Have you seen the president of El Salvador`
- grey phrase=`Volcano Bonds` match=1 ratio=0.5 reflectionHits=none
- orange phrase=`shitcoiner at heart` match=1 ratio=0.333 reflectionHits=none

## All Reflection Intersections
- p75 orange `They are the sum of all our neuroses` -> 79_75_3 overlapVsSpan=0.0094 overlapVsReflection=0.5204 reflectionText=`Markets are`
- p75 orange `Fact: It's Layer 1 for every great thing that's ever been invented or discovered` -> 79_75_5 overlapVsSpan=0.0521 overlapVsReflection=0.3142 reflectionText=`only the language of the shameless opportunists trying cash in by riding Bitcoins coattails that give it a bad`
- p76 orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin` -> 79_76_1 overlapVsSpan=0.2967 overlapVsReflection=0.9566 reflectionText=`but George Clinton and James Brown clones. It's Martin Luther nailing the Vatican with ultimatums. It's the so`
- p76 grey `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense` -> 79_76_2 overlapVsSpan=0.1634 overlapVsReflection=0.1968 reflectionText=`Gotta be S way. Forty years of (and loyears of watching Peter`
- p76 orange `by the rancid catnip of fiat money` -> 78_76_3 overlapVsSpan=0.1349 overlapVsReflection=0.4583 reflectionText=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`
- p76 grey `It's a stun gun to the genitals` -> 79_76_1 overlapVsSpan=0.1651 overlapVsReflection=0.571 reflectionText=`but George Clinton and James Brown clones. It's Martin Luther nailing the Vatican with ultimatums. It's the so`
- p76 orange `buying the dip` -> 78_76_1 overlapVsSpan=0.0692 overlapVsReflection=1.0 reflectionText=`honéy-badgering him`
- p76 grey `$1 billion` -> 78_76_3 overlapVsSpan=0.0632 overlapVsReflection=0.7513 reflectionText=`¥ortunately, bitcoin end to the paper chase Manhattan Bank money`
- p78 grey `money printing` -> 76_78_1 overlapVsSpan=0.0558 overlapVsReflection=0.2242 reflectionText=`We've never had an economy and a money`

## Assessment
- The mirror/reflection layer overlaps color-highlighted page-76 spans around the same “Gotta be this way / Peter Schiff” and El Salvador/Bukele corridor, not the whole article uniformly.
- This supports using color as a selector label, but the overlap still points to regions/phrases rather than a final ordering rule.
- Next branch should inspect only overlapped color spans and their neighboring partial-bold words by physical reading order: normal, mirrored, and fold-pair order.
