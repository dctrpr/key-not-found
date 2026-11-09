# Typeka Reflection Intersection Audit

Scope: intersect `Article with Fonts.docm` Typeka states with the medium/strong page-76 reflected-highlight graph. This is a selector test only; no key candidates were generated.

## Target Summary

- `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.` (orange, orange_7): targetVariants=TYPEKA_BOLD:53; edges=3; reflectionStatus=exact:2, fuzzy:1; reflectionVariants=MIX:38, TYPEKA:132, TYPEKA_BOLD:44; edgesWithMix=1
- `by the rancid catnip of fiat money.` (orange, orange_8): targetVariants=TYPEKA_BOLD:26; edges=2; reflectionStatus=exact:1, fuzzy:1; reflectionVariants=MIX:10, TYPEKA:86; edgesWithMix=1
- `“buying the dip.”` (orange, orange_9): targetVariants=TYPEKA_BOLD:12; edges=3; reflectionStatus=exact:2, fuzzy:1; reflectionVariants=TYPEKA:35, TYPEKA_BOLD:44; edgesWithMix=0
- `It’s a stun gun to the genitals.` (grey_black, grey_black_4): targetVariants=TYPEKA_BOLD:25; edges=4; reflectionStatus=exact:2, fuzzy:2; reflectionVariants=MIX:38, TYPEKA:194, TYPEKA_BOLD:44; edgesWithMix=1
- `$1 billion` (grey_black, grey_black_5): targetVariants=TYPEKA_BOLD:9; edges=5; reflectionStatus=exact:3, fuzzy:2; reflectionVariants=MIX:20, TYPEKA:209, TYPEKA_BOLD:7; edgesWithMix=2

## Edge Details

### orange_7 orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.`
- target match `fuzzy` score=0.9917 variants=TYPEKA_BOLD:53 highlights=yellow:53
- strong 79->76 79_76_1 ovRefl=0.957 ovSpan=0.297: refMatch=exact score=1.0 variants=MIX:38, TYPEKA:115 text=`but George Clinton and James Brown clones. It's Martin Luther nailing the Vatican with ultimatums. It's the sound of skin being ripped off l...`
- strong 79->76 79_76_2 ovRefl=0.937 ovSpan=0.056: refMatch=fuzzy score=0.6847 variants=TYPEKA_BOLD:44 text=`Gotta be this way. Forty years of dumb post-1971 fiat`
- medium 79->76 79_76_3 ovRefl=0.518 ovSpan=0.012: refMatch=exact score=1.0 variants=TYPEKA:17 text=`miss buying bitcoin`

### orange_8 orange `by the rancid catnip of fiat money.`
- target match `fuzzy` score=0.9538 variants=TYPEKA_BOLD:26 highlights=yellow:26
- medium 78->76 78_76_4 ovRefl=0.525 ovSpan=0.055: refMatch=exact score=1.0 variants=MIX:10, TYPEKA:25 text=`Have you seen the president of El Salvador`
- medium 78->76 78_76_3 ovRefl=0.458 ovSpan=0.135: refMatch=fuzzy score=0.9474 variants=TYPEKA:61 text=`Fortunately, bitcoinputs an end to the paper chase Manhattan Bank money`

### orange_9 orange `“buying the dip.”`
- target match `exact` score=1.0 variants=TYPEKA_BOLD:12 highlights=yellow:12
- strong 78->76 78_76_1 ovRefl=1.000 ovSpan=0.069: refMatch=exact score=1.0 variants=TYPEKA:18 text=`honey-badgering him`
- strong 79->76 79_76_3 ovRefl=0.713 ovSpan=0.035: refMatch=exact score=1.0 variants=TYPEKA:17 text=`miss buying bitcoin`
- medium 79->76 79_76_2 ovRefl=0.453 ovSpan=0.055: refMatch=fuzzy score=0.6847 variants=TYPEKA_BOLD:44 text=`Gotta be this way. Forty years of dumb post-1971 fiat`

### grey_black_4 grey_black `It’s a stun gun to the genitals.`
- target match `exact` score=1.0 variants=TYPEKA_BOLD:25 highlights=black:25
- strong 78->76 78_76_1 ovRefl=0.790 ovSpan=0.025: refMatch=exact score=1.0 variants=TYPEKA:18 text=`honey-badgering him`
- medium 79->76 79_76_2 ovRefl=0.651 ovSpan=0.036: refMatch=fuzzy score=0.6847 variants=TYPEKA_BOLD:44 text=`Gotta be this way. Forty years of dumb post-1971 fiat`
- medium 79->76 79_76_1 ovRefl=0.571 ovSpan=0.165: refMatch=exact score=1.0 variants=MIX:38, TYPEKA:115 text=`but George Clinton and James Brown clones. It's Martin Luther nailing the Vatican with ultimatums. It's the sound of skin being ripped off l...`
- medium 78->76 78_76_3 ovRefl=0.555 ovSpan=0.116: refMatch=fuzzy score=0.9474 variants=TYPEKA:61 text=`Fortunately, bitcoinputs an end to the paper chase Manhattan Bank money`

### grey_black_5 grey_black `$1 billion`
- target match `exact` score=1.0 variants=TYPEKA_BOLD:9 highlights=black:9
- strong 79->76 79_76_5 ovRefl=0.949 ovSpan=0.052: refMatch=fuzzy score=0.9146 variants=TYPEKA:83, TYPEKA_BOLD:7 text=`trolling the International Monetary Fund (IMF) on Twitter? He's taunting them, telling them he's "buying`
- strong 79->76 79_76_4 ovRefl=0.949 ovSpan=0.048: refMatch=exact score=1.0 variants=MIX:10, TYPEKA:25 text=`Have you seen the president of El Salvador`
- strong 78->76 78_76_4 ovRefl=0.948 ovSpan=0.028: refMatch=exact score=1.0 variants=MIX:10, TYPEKA:25 text=`Have you seen the president of El Salvador`
- medium 78->76 78_76_2 ovRefl=0.928 ovSpan=0.011: refMatch=exact score=1.0 variants=TYPEKA:15 text=`Our imaginations`
- strong 78->76 78_76_3 ovRefl=0.751 ovSpan=0.063: refMatch=fuzzy score=0.9474 variants=TYPEKA:61 text=`Fortunately, bitcoinputs an end to the paper chase Manhattan Bank money`

## Assessment

- The confirmed page-76 target spans are almost entirely `TYPEKA_BOLD`, which mostly restates that the high-signal target spans are highlighted/bold article phrases.
- `Typeka Mix` shows up in nearby/reflected snippet matches around semantic anchors, especially `George Clinton` and `El Salvador`, but it does not create a cleaner one-edge-per-letter or one-edge-per-word selector.
- This rules out a simple rule such as “take Typeka Mix inside the reflected target spans.”
- Keep Typeka as a layer, but it needs stricter visual registration or another instruction before it is useful for extraction.
