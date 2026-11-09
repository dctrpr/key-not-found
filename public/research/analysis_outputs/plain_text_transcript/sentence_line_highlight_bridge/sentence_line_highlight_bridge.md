# Sentence-Line Highlight Bridge

Scope: bridge canonical sentence rows to the page-76 visual line/highlight model. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.

- Created: `2026-05-20T11:25:15`

## Sentence Bridges

| sentence | page lines | corridor | line initials | highlights | text |
|---:|---|---|---|---|---|
| 43 | `20-21` | `2-3` | `Ht` | `[]` | `Have you seen the president of El Salvador trolling the International Monetary Fund (IMF) on Twitter?` |
| 44 | `22` | `4` | `H` | `['orange: buying the dip']` | `He's taunting them, telling them he's "buying the dip."` |
| 45 | `23-28` | `5-10` | `Ih$bcl` | `['grey: $1 billion', 'grey: Volcano Bonds', 'bold: IMF', 'bold-partial/full: Mike']` | `I tweeted President Nayib Bukele when he announced he was going to tap his nation's volcanoes to mine $1 billion in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized “Volcano Bonds” to pay off the IMF loan and get rid of those leeches.` |
| 46 | `28-31` | `10-13` | `lNbh` | `['bold-partial/full: Mike', 'bold-partial: Novogratz', "bold partial: I don't really trust that guy"]` | `I tagged Mike Novogratz in the tweet, figuring he could sell a bunch to his Wall Street crony pals, but so far he hasn't moved on it.` |
| 47 | `31` | `13` | `h` | `["bold partial: I don't really trust that guy"]` | `I don't really trust that guy.` |
| 48 | `32` | `14` | `M` | `['orange: shitcoiner at heart']` | `Maybe because he's a shitcoiner at heart.` |

## G5/O5 Metrics

- Sentence pair: `45 -> 48`
- Page-line pair: `27 -> 32`
- Corridor pair: `9 -> 14`
- Gaps: sentence `3`, page-line `5`, corridor `5`
- Sentence minus page-line diffs: `[18, 16]`

## Streams

| stream | value | instruction hits |
|---|---|---|
| `sentenceToLineSpans` | `43:20-21;44:22;45:23-28;46:28-31;47:31;48:32` | `[]` |
| `sentenceToCorridorSpans` | `43:2-3;44:4;45:5-10;46:10-13;47:13;48:14` | `[]` |
| `sentenceLineInitials` | `HtHIh$bcllNbhhM` | `[]` |
| `sentenceLineLastWords` | `Salvador Twitter | dip | announced mine sell earnings IMF Mike | Mike a he guy | guy | heart` | `[]` |
| `highlightCountsBySentence` | `0 1 4 3 1 1` | `[]` |
| `highlightTermsBySentence` | `- | orange: buying the dip | grey: $1 billion,grey: Volcano Bonds,bold: IMF,bold-partial/full: Mike | bold-partial/full: Mike,bold-partial: Novogratz,bold partial: I don't really trust that guy | bold partial: I don't really trust that guy | orange: shitcoiner at heart` | `[]` |
| `g5o5SentenceLineCorridorTriples` | `45-27-9 48-32-14` | `[]` |
| `g5o5Gaps` | `3 5 5` | `[]` |
| `g5o5SentenceMinusLine` | `18 16` | `[]` |

## Assessment

- Sentence row 45 cleanly carries the `Volcano Bonds`/Bukele/IMF source sentence and spans page lines 23-28.
- Sentence row 48 carries `shitcoiner at heart` and maps to page line 32.
- The G5/O5 pair is therefore sentence rows 45/48, page lines 27/32, and corridor indexes 9/14.
- The resulting gaps are sentence gap 3 and line/corridor gap 5; this is a stable locator but not an instruction.
- Line 28 and line 31 are mixed visual lines that cross sentence boundaries, so sentence units and printed line units do not collapse into one clean extraction grid.
- No sentence-line/highlight stream names a procedural unit such as read/take/first/last/word/letter.

## Decision

- Use sentence-line/highlight bridge as validation/locator evidence only; it does not supply the missing extraction unit.

## Next Move

- Keep source/physical/original-layout validation as priority. Reopen sentence-line bridge only if a new clue names sentence, line, or gap units.
