# Registered 76/79 Line-Offset Rule Audit

Scope: test whether the strongest registered 76/79 line pair gives a small `read between the lines` style selector. This uses only the one aligned anchor and does not derive keys.

## Exact Text Pair

- p79 orange source: `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`
- p76 grey target: `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense`
- Source words: 14
- Target words: 12

## Vertical Offset

- Transformed p79 source row centers: `785.0` and `934.1`
- Source-row gap midpoint: `859.5`
- p76 row `Gotta be S way. Forty years of dumb post-1971 flat money` y=854.5 deltaFromMid=-5.0 gapFraction=-0.0339
- p76 row `RRECECy` y=921.5 deltaFromMid=62.0 gapFraction=0.4155

## Low-Parameter Text Streams

- `sourceInitials` hits=none: `imettaswitfsog`
- `targetInitials` hits=none: `GbtwFyodpfmn`
- `sourceInitialsReversed` hits=none: `gosftiwsattemi`
- `targetInitialsReversed` hits=none: `nmfpdoyFwtbG`
- `sourceLasts` hits=none: `yetotdehnntsrd`
- `targetLasts` hits=none: `aesyysfb1tye`
- `sourceLengthMod10` hits=none: `04928356244924`
- `targetLengthMod10` hits=none: `524355244458`
- `sandwichTargetInitials` hits=none: `GbSwFyodpfm`
- `sandwichAboveInitials` hits=none: `eemmiiibbll`
- `sandwichBelowInitials` hits=none: `wweeceeotOO`
- `sandwichAboveBelowInitialPairs` hits=none: `ewewmemeicieiebobtlOlO`

## Above / Target / Below Sandwich

- `efficient:` / `Gotta` / `while` (dx above=-145.1, below=-95.1)
- `efficient:` / `be` / `while` (dx above=-29.7, below=20.3)
- `more` / `S` / `even` (dx above=-92.5, below=22.5)
- `more` / `way.` / `even` (dx above=-21.1, below=93.9)
- `infinitely` / `Forty` / `consumption,` (dx above=-87.1, below=3.4)
- `infinitely` / `years` / `energy` (dx above=57.4, below=-92.6)
- `is` / `of` / `energy` (dx above=18.8, below=18.3)
- `bitcoin` / `dumb` / `overall` (dx above=0.0, below=-56.0)
- `because` / `post-1971` / `the` (dx above=-11.8, below=-18.3)
- `love` / `flat` / `ORMBONG` (dx above=-25.8, below=-23.8)
- `love` / `money` / `ORMBONG` (dx above=102.1, below=104.1)

## Assessment

- The geometry strongly supports a `between the lines` observation: the main p76 grey row is nearly centered in the vertical gap between the two transformed p79 source rows.
- The actual between-lines text is `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense`, which is coherent article prose but not a visible instruction.
- The exact-text streams and above/below sandwich initials do not produce readable selector language.
- Conclusion: keep the 76/79 alignment as a registration clue, but do not promote this anchor into a direct text selector.
- Next best move: test whether this same line-gap behavior recurs across other p76/p79 or p76/p78 highlight alignments; if it is unique, it may be a visual confirmation marker rather than extraction material.
