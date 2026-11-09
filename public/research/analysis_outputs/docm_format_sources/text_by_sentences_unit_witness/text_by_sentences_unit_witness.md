# Text By Sentences Unit Witness

Scope: audit `Text_by_sentences.docx` as a possible sentence-unit witness. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.

- Created: `2026-05-20T11:17:18`
- Rows: `87`
- Missing priority terms: `['volcano_bonds']`

## Marker Rows

| row | marker | row-marker | text |
|---:|---:|---:|---|
| 15 | 15 | 0 | `(15)Nocoiners and shitcoiners, and even some Bitcoiners, consider this view toxic.` |
| 35 | 35 | 0 | `(35)Gotta be this way.` |
| 51 | 50 | 1 | `(50)At this rate the whole country will be Toxic Bitcoin Maximalists within six months.` |
| 71 | 70 | 1 | `(70)Bitcoin fixes all this by replacing oil-dripping, corpse-ridden, poppy-harvesting fiat money with perfect bitcoin.` |
| 86 | 85 | 1 | `(85)Happy to share it all with you - the agony and ecstasy - as Bitcoin conquers fear and hate and replaces it with peace and love.` |

## Active Corridor Rows

| row | text |
|---:|---|
| 40 | `It's a stun gun to the genitals.` |
| 41 | `A monetary defibrillator to the treasure chest.` |
| 42 | `Don't believe me?` |
| 43 | `Have you seen the president of El Salvador trolling the International Monetary Fund (IMF) on Twitter?` |
| 44 | `He's taunting them, telling them he's "buying the dip".` |
| 45 | `I tweeted President Nayib Bukele when he announced he was going to tap his nation's volcanoes to mine $1 billion in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized to pay off the IMF loan and get rid of those leeches.` |
| 46 | `I tagged Mike Novogratz in the tweet, figuring he could sell a bunch to his Wall Street crony pals, but so far he hasn't moved on it.` |
| 47 | `I don't really trust that guy.` |
| 48 | `Maybe because he's a shitcoiner at heart.` |
| 49 | `Meanwhile, back in El Salvador, 42% of the country is now hyperbitcoinized (at the time of writing).` |

## Target Term Rows

| term | rows |
|---|---|
| `el_salvador` | `[43, 49]` |
| `imf` | `[43, 45]` |
| `buying_the_dip` | `[44]` |
| `bukele` | `[45]` |
| `volcanoes` | `[45]` |
| `volcano_bonds` | `[]` |
| `one_billion` | `[45]` |
| `should_sell` | `[45]` |
| `novogratz` | `[46]` |
| `trust_that_guy` | `[47]` |
| `shitcoiner_at_heart` | `[48]` |

## Low-Parameter Streams

| stream | value | instruction hits |
|---|---|---|
| `markerValues` | `15 35 50 70 85` | `[]` |
| `markerRowDeltas` | `0 0 1 1 1` | `[]` |
| `priorityRowNumbers` | `43 44 45 46 47 48` | `[]` |
| `priorityInitials` | `hhiiim` | `[]` |
| `priorityLastWords` | `twitter dip leeches it guy heart` | `[]` |
| `g5o5SentencePair` | `45 48` | `[]` |
| `g5o5SentenceGap` | `3` | `[]` |
| `sentence45InitialLast` | `is` | `[]` |
| `sentence48InitialLast` | `mt` | `[]` |

## Assessment

- `Text_by_sentences.docx` is article-related and supplies a sentence-unit layer, but it is a working transcript rather than original layout/geometry.
- The active page-76 corridor is represented by sentence rows 43-49.
- The crucial `Volcano Bonds` phrase is missing from this witness, so it cannot be trusted as the source for the G5/O5 pair.
- Sentence markers `(15)`, `(35)`, `(50)`, `(70)`, and `(85)` are mostly row/count aids, not a clean selector.
- Low-parameter sentence streams from the active corridor produce no instruction hits.

## Decision

- Keep Text_by_sentences.docx as a sentence-count working witness only; do not use it as a source-backed selector because it lacks `Volcano Bonds` and original formatting.

## Next Move

- If sentence units are ever named by an external clue, rebuild them from the corrected canonical article text, not this imperfect witness.
