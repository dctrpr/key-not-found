# Typeka Transition Boundaries

Scope: audit whether changes between Typeka regular, Typeka Mix, and Typeka bold identify a readable boundary selector in the active page-76 corridor. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T19:42:45`
- Focus: page `76`, paragraphs `60-73`, runs `118-151`
- Font variant counts: `{'R': 16, 'M': 4, 'B': 9}`
- Visual state counts: `{'R': 16, 'M': 4, 'Y': 4, 'B': 3, 'K': 2}`

## Font-Only Variant Audit

- Codes: `R` Typeka regular, `M` Typeka Mix, `B` Typeka bold.
- `path` hits=none: `RMRBRBRBRBRBRMRMRB`
- `transitions` hits=none: `R>M M>R R>B B>R R>B B>R R>B B>R R>B B>R R>B B>R R>M M>R R>M M>R R>B`
- `entryInitials` hits=none: `EtbIPw$iVtIaMiIMs`
- `boundaryPairs` hits=none: `fE rt sb pI dP ew e$ ni dV st eI na dM zi tI yM as`
- `rightEntryWords` hits=none: `El | trolling | buying | I | President | when | $1 | in | Volcano | to | IMF | and | Mike | in | I | Maybe | shitcoiner`
- `leftExitWords` hits=none: `of | Salvador | s | dip | tweeted | Bukele | mine | billion | collateralized | Bonds | the | loan | tagged | Novogratz | it | guy | a`
- `nonRegularInitials` hits=none: `EbP$VIMIs`
- `nonRegularWords` hits=none: `El | buying | President | $1 | Volcano | IMF | Mike | I | shitcoiner`
- `highlightMixInitials` hits=none: `EMI`
- `highlightMixWords` hits=none: `El | Mike | I`

### Font-Only Segments

| code | runs | text |
|---|---|---|
| `R` | `118-119` | `Don't believe me? Have you seen the president of` |
| `M` | `120-120` | `El Salvador` |
| `R` | `122-123` | `trolling the International Monetary Fund (IMF) on Twitter? He's taunting them, telling them he's` |
| `B` | `124-126` | `"buying the dip . "` |
| `R` | `127-127` | `I tweeted` |
| `B` | `128-128` | `President Nayib Bukele` |
| `R` | `129-130` | `when he announced he was going to tap his nation's volcanoes to mine` |
| `B` | `131-131` | `$1 billion` |
| `R` | `133-135` | `in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized` |
| `B` | `137-137` | `“Volcano Bonds”` |
| `R` | `139-139` | `to pay off the` |
| `B` | `140-141` | `IMF loan` |
| `R` | `142-142` | `and get rid of those leeches. I tagged` |
| `M` | `143-144` | `Mike Novogratz` |
| `R` | `145-147` | `in the tweet, figuring he could sell a bunch to his Wall Street crony pals, but so far he hasn't moved on it.` |
| `M` | `148-148` | `I don't really trust that guy.` |
| `R` | `150-150` | `Maybe because he's a` |
| `B` | `151-151` | `shitcoiner at heart.` |

## Highlight-Aware Visual State Audit

- Codes: `R` Typeka regular, `M` Typeka Mix, `B` Typeka bold, `K` black-highlighted bold, `Y` yellow-highlighted bold.
- `path` hits=none: `RMRYRBRKRKRBRMRMRY`
- `transitions` hits=none: `R>M M>R R>Y Y>R R>B B>R R>K K>R R>K K>R R>B B>R R>M M>R R>M M>R R>Y`
- `entryInitials` hits=none: `EtbIPw$iVtIaMiIMs`
- `boundaryPairs` hits=none: `fE rt sb pI dP ew e$ ni dV st eI na dM zi tI yM as`
- `rightEntryWords` hits=none: `El | trolling | buying | I | President | when | $1 | in | Volcano | to | IMF | and | Mike | in | I | Maybe | shitcoiner`
- `leftExitWords` hits=none: `of | Salvador | s | dip | tweeted | Bukele | mine | billion | collateralized | Bonds | the | loan | tagged | Novogratz | it | guy | a`
- `nonRegularInitials` hits=none: `EbP$VIMIs`
- `nonRegularWords` hits=none: `El | buying | President | $1 | Volcano | IMF | Mike | I | shitcoiner`
- `highlightMixInitials` hits=none: `Eb$VMIs`
- `highlightMixWords` hits=none: `El | buying | $1 | Volcano | Mike | I | shitcoiner`

### Visual-State Segments

| code | runs | text |
|---|---|---|
| `R` | `118-119` | `Don't believe me? Have you seen the president of` |
| `M` | `120-120` | `El Salvador` |
| `R` | `122-123` | `trolling the International Monetary Fund (IMF) on Twitter? He's taunting them, telling them he's` |
| `Y` | `124-126` | `"buying the dip . "` |
| `R` | `127-127` | `I tweeted` |
| `B` | `128-128` | `President Nayib Bukele` |
| `R` | `129-130` | `when he announced he was going to tap his nation's volcanoes to mine` |
| `K` | `131-131` | `$1 billion` |
| `R` | `133-135` | `in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized` |
| `K` | `137-137` | `“Volcano Bonds”` |
| `R` | `139-139` | `to pay off the` |
| `B` | `140-141` | `IMF loan` |
| `R` | `142-142` | `and get rid of those leeches. I tagged` |
| `M` | `143-144` | `Mike Novogratz` |
| `R` | `145-147` | `in the tweet, figuring he could sell a bunch to his Wall Street crony pals, but so far he hasn't moved on it.` |
| `M` | `148-148` | `I don't really trust that guy.` |
| `R` | `150-150` | `Maybe because he's a` |
| `Y` | `151-151` | `shitcoiner at heart.` |

## Boundary Records

| mode | transition | pair | left word | right word |
|---|---|---|---|---|
| `fontVariant` | `R>M` | `fE` | `of` | `El` |
| `fontVariant` | `M>R` | `rt` | `Salvador` | `trolling` |
| `fontVariant` | `R>B` | `sb` | `s` | `buying` |
| `fontVariant` | `B>R` | `pI` | `dip` | `I` |
| `fontVariant` | `R>B` | `dP` | `tweeted` | `President` |
| `fontVariant` | `B>R` | `ew` | `Bukele` | `when` |
| `fontVariant` | `R>B` | `e$` | `mine` | `$1` |
| `fontVariant` | `B>R` | `ni` | `billion` | `in` |
| `fontVariant` | `R>B` | `dV` | `collateralized` | `Volcano` |
| `fontVariant` | `B>R` | `st` | `Bonds` | `to` |
| `fontVariant` | `R>B` | `eI` | `the` | `IMF` |
| `fontVariant` | `B>R` | `na` | `loan` | `and` |
| `fontVariant` | `R>M` | `dM` | `tagged` | `Mike` |
| `fontVariant` | `M>R` | `zi` | `Novogratz` | `in` |
| `fontVariant` | `R>M` | `tI` | `it` | `I` |
| `fontVariant` | `M>R` | `yM` | `guy` | `Maybe` |
| `fontVariant` | `R>B` | `as` | `a` | `shitcoiner` |
| `visualState` | `R>M` | `fE` | `of` | `El` |
| `visualState` | `M>R` | `rt` | `Salvador` | `trolling` |
| `visualState` | `R>Y` | `sb` | `s` | `buying` |
| `visualState` | `Y>R` | `pI` | `dip` | `I` |
| `visualState` | `R>B` | `dP` | `tweeted` | `President` |
| `visualState` | `B>R` | `ew` | `Bukele` | `when` |
| `visualState` | `R>K` | `e$` | `mine` | `$1` |
| `visualState` | `K>R` | `ni` | `billion` | `in` |
| `visualState` | `R>K` | `dV` | `collateralized` | `Volcano` |
| `visualState` | `K>R` | `st` | `Bonds` | `to` |
| `visualState` | `R>B` | `eI` | `the` | `IMF` |
| `visualState` | `B>R` | `na` | `loan` | `and` |
| `visualState` | `R>M` | `dM` | `tagged` | `Mike` |
| `visualState` | `M>R` | `zi` | `Novogratz` | `in` |
| `visualState` | `R>M` | `tI` | `it` | `I` |
| `visualState` | `M>R` | `yM` | `guy` | `Maybe` |
| `visualState` | `R>Y` | `as` | `a` | `shitcoiner` |

## Uniqueness Inside DOCM Witness

| mode | focus path | page occurrences |
|---|---|---|
| `fontVariant` | `RMRBRBRBRBRBRMRMRB` | `{'75': 0, '76': 1, '77': 0, '78': 0, '79': 0}` |
| `visualState` | `RMRYRBRKRKRBRMRMRY` | `{'75': 0, '76': 1, '77': 0, '78': 0, '79': 0}` |

## Comparison Note

- Comparison font metadata available: `False`.
- Reason: Existing comparison PDFs are image-only in the OVERDOSE style audit, so Typeka font metadata cannot be extracted from them.

## Assessment

- Font-change boundaries in the page-76 El Salvador corridor are real and concentrated, but their left/right boundary characters and entry words do not spell an instruction.
- Ignoring highlights, the focus font-variant path is a unique page-76 sequence in the DOCM witness; this supports the corridor as deliberate formatting/provenance, not a solved selector.
- With highlights included, the visual-state path is also unique to page 76, but it follows visible emphasis: El Salvador, buying the dip, Bukele, $1 billion, Volcano Bonds, IMF, Mike/Novogratz, trust, and O5.
- The comparison Max PDFs cannot adjudicate Typeka because they are image-only locally; they can only downgrade broad OVERDOSE style, not supply a font-layer extraction rule.
- Do not use font-boundary initials, boundary pairs, or transition codes as key material without a new rule naming a boundary side, font state, or exact order.

## Decision

- Keep Typeka/font transitions as source and corridor evidence only; they do not currently supply the missing extraction unit.
- Next move: Inspect whether the high-res visual highlight boundaries, not DOCM font boundaries, produce a manual side-specific unit at the G5/O5 five-line corridor.
