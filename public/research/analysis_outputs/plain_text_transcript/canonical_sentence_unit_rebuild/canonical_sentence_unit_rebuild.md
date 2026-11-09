# Canonical Sentence Unit Rebuild

Scope: rebuild sentence units from corrected canonical article text. No key derivation, hashing, BIP39, WIF, seed, or address checks were run.

- Created: `2026-05-20T11:20:50`
- Sentence count: `87`

## Active Corridor Rows

| row | text |
|---:|---|
| 40 | `It's a stun gun to the genitals.` |
| 41 | `A monetary defibrillator to the treasure chest.` |
| 42 | `Don't believe me?` |
| 43 | `Have you seen the president of El Salvador trolling the International Monetary Fund (IMF) on Twitter?` |
| 44 | `He's taunting them, telling them he's "buying the dip."` |
| 45 | `I tweeted President Nayib Bukele when he announced he was going to tap his nation's volcanoes to mine $1 billion in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized “Volcano Bonds” to pay off the IMF loan and get rid of those leeches.` |
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
| `volcano_bonds` | `[45]` |
| `one_billion` | `[45]` |
| `should_sell` | `[45]` |
| `novogratz` | `[46]` |
| `trust_that_guy` | `[47]` |
| `shitcoiner_at_heart` | `[48]` |

## Text-Witness Marker Rows Applied To Canonical Text

| marker row | canonical sentence |
|---:|---|
| 15 | `Nocoiners and shitcoiners, and even some Bitcoiners, consider this view toxic.` |
| 35 | `Gotta be this way.` |
| 50 | `Jack Mallers' Strike app has gone from 20,000 new sign-ups a day to a mind-bending 100,000 and growing.` |
| 70 | `The energy industry in its current form is gargantuanly wasteful and requires money printing and wars to keep it going - all in the service of an uber class of banksters who profit from war, poverty and misery with their fiat money Ponzi schemes.` |
| 85 | `Stacy and I have been living in here for 10 years.` |

## Low-Parameter Streams

| stream | value | instruction hits |
|---|---|---|
| `activeRowNumbers` | `43 44 45 46 47 48` | `[]` |
| `activeInitials` | `hhiiim` | `[]` |
| `activeLastWords` | `twitter dip leeches it guy heart` | `[]` |
| `activeFirstLastPairs` | `hr hp is it iy mt` | `[]` |
| `g5o5SentencePair` | `45 48` | `[]` |
| `g5o5SentenceGap` | `3` | `[]` |
| `g5o5Initials` | `im` | `[]` |
| `g5o5LastWords` | `leeches heart` | `[]` |
| `markerRowsFromTextWitness` | `15 35 50 70 85` | `[]` |
| `markerRowInitials` | `ngjts` | `[]` |
| `markerRowLastWords` | `toxic way growing schemes years` | `[]` |

## Assessment

- Corrected canonical text rebuilds to 87 sentence rows, matching the rough count from Text_by_sentences.docx.
- The active page-76 corridor remains sentence rows 43-49.
- `Volcano Bonds` is restored in canonical row 45, paired with `shitcoiner at heart` at row 48; the sentence gap is 3.
- The low-parameter active sentence streams still do not produce a procedural instruction.
- The marker numbers from Text_by_sentences.docx are not reliable extraction indices against the corrected canonical text: rows 50/70/85 land on normal body sentences, not instructions.

## Decision

- Canonical sentence units are a documented validation layer only; they do not name an extraction rule under current clues.

## Next Move

- Only use sentence rows if a future source/clue explicitly says to read by sentence; otherwise keep source/physical/original-layout validation as the priority.
