# Lower Corridor Font-State Selector

Scope: phrase-level Typeka/font-state audit for the page-76 lower corridor selected by p78 frame/marks. No key derivation was run.

- Created: `2026-05-20T07:21:42`

## Streams

- `corridorDominantStyles` hits=none: `YBKRRKRBRRMY`
- `corridorStyleRuns` hits=none: `Y|B|K|R|R|K|RB|B|RM|R|M|Y`
- `corridorInitials` hits=none: `bP$seVpIIcts`
- `corridorLasts` hits=none: `penlssFnelyt`
- `frameDominantStyles` hits=none: `RRKRRRMY`
- `frameInitials` hits=none: `seVpIcts`
- `frameLasts` hits=none: `lssFelyt`
- `highlightMixDominantStyles` hits=none: `YKKRMY`
- `highlightMixInitials` hits=none: `b$VIts`
- `highlightMixLasts` hits=none: `pnseyt`

## Phrase Ledger

| id | phrase | style | style run | variants | highlights | p78 frame relation |
|---|---|---:|---|---|---|---|
| O4 | buying the dip | `Y` | `Y` | `{'TYPEKA_BOLD': 14}` | `{'yellow': 1}` | overlap `0.0` |
| bukele | President Nayib Bukele | `B` | `B` | `{'TYPEKA_BOLD': 22}` | `{'none': 1}` | - |
| B4_text | $1 billion | `K` | `K` | `{'TYPEKA_BOLD': 10}` | `{'black': 1}` | overlap `0.0` |
| should_sell | should sell | `R` | `R` | `{'TYPEKA': 11}` | `{'none': 1}` | overlap `0.7635`; left cuts; top cuts |
| earnings | earnings | `R` | `R` | `{'TYPEKA': 8}` | `{'none': 1}` | overlap `0.9331`; left cuts |
| G5 | Volcano Bonds | `K` | `K` | `{'TYPEKA_BOLD': 13}` | `{'black': 1}` | overlap `0.0`; left right-adjacent |
| pay_imf | pay off the IMF | `R` | `RB` | `{'TYPEKA': 12, 'TYPEKA_BOLD': 3}` | `{'none': 2}` | overlap `1.0`; left left-adjacent |
| IMF_loan | IMF loan | `B` | `B` | `{'TYPEKA_BOLD': 8}` | `{'none': 2}` | - |
| tagged_mike | I tagged Mike | `R` | `RM` | `{'TYPEKA': 9, 'MIX': 4}` | `{'none': 2}` | overlap `1.0`; left left-adjacent |
| could_sell | could sell | `R` | `R` | `{'TYPEKA': 10}` | `{'none': 1}` | overlap `1.0` |
| trust_guy | trust that guy | `M` | `M` | `{'MIX': 14}` | `{'none': 1}` | overlap `1.0`; left left-adjacent |
| O5 | shitcoiner at heart | `Y` | `Y` | `{'TYPEKA_BOLD': 19}` | `{'yellow': 1}` | overlap `0.2475`; left cuts; bottom cuts |

## Assessment

- The lower corridor has a real visual/font pattern, but it follows visible formatting: yellow/black highlights, regular prose, Typeka Mix names/phrases, then O5.
- The p78-frame-touched phrase stream mixes regular text, black highlight, Typeka Mix, and yellow highlight; it does not collapse to a readable instruction or a clear first/last/middle selector.
- Typeka Mix in this corridor marks semantic names/phrases (`Mike`, `trust that guy`) rather than a clean ordered alphabetic stream.
- This keeps Typeka as a formatting witness, not a final selector, unless a new external rule names which font state to read.

## Next Move

- Do not rerun Typeka initials/lengths locally. Reopen font states only if a source clue specifies a font state or if a new source registration picks exact phrase units.
