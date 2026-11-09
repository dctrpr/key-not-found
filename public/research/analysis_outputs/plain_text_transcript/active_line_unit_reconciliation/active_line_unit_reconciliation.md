# Active Line Unit Reconciliation

Scope: reconcile the locked O4/B4/G5/O5 units across corrected text, sentence rows, printed page lines, corridor indexes, and DOCM/font states. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T21:04:13`
- Active units checked: `4`
- Duplicate active units in same sentence row: `{45: ['one_billion', 'volcano_bonds']}`

## Active Units

| order | id | state | sentence | page line | corridor | DOCM | left | right | above | below | line text |
|---:|---|---|---:|---:|---:|---|---|---|---|---|---|
| 1 | `buying_dip` | `Y` | 44 | 22 | 4 | `Typeka bold=1.0 hi={'yellow': 14}` | `he's` | `-` | `on` | `announced` | He's taunting them, telling them he's “buying the dip.” |
| 2 | `one_billion` | `K` | 45 | 25 | 7 | `Typeka bold=1.0 hi={'black': 10}` | `-` | `in` | `was` | `billions` | $1 billion in bitcoin — that he should sell |
| 3 | `volcano_bonds` | `K` | 45 | 27 | 9 | `Typeka bold=1.0 hi={'black': 13}` | `collateralized` | `to` | `future` | `those` | collateralized “Volcano Bonds” to pay off the IMF |
| 4 | `shitcoiner_heart` | `Y` | 48 | 32 | 14 | `Typeka bold=1.0 hi={'yellow': 19}` | `a` | `-` | `trust` | `-` | Maybe because he's a shitcoiner at heart. |

## Streams

| stream | value | instruction hits |
|---|---|---|
| `visualStateOrder` | `YKKY` | - |
| `pageLines` | `22 25 27 32` | - |
| `sentenceRows` | `44 45 45 48` | - |
| `corridorIndexes` | `4 7 9 14` | - |
| `sentenceLinePairs` | `44-22 45-25 45-27 48-32` | - |
| `lineGaps` | `3 2 5` | - |
| `sentenceGaps` | `1 0 3` | - |
| `corridorGaps` | `3 2 5` | - |
| `phraseInitials` | `btd 1b vb sah` | - |
| `phraseEdges` | `bp 1n vs st` | - |
| `leftBoundaryWords` | `he's | - | collateralized | a` | - |
| `rightBoundaryWords` | `- | in | to | -` | - |
| `aboveWords` | `on | was | future | trust` | - |
| `belowWords` | `announced | billions | those | -` | - |
| `leftBoundaryInitials` | `h-ca` | - |
| `rightBoundaryInitials` | `-it-` | - |
| `aboveInitials` | `owft` | - |
| `belowInitials` | `abt-` | - |
| `leftBoundaryLasts` | `s-da` | - |
| `rightBoundaryLasts` | `-no-` | - |
| `aboveLasts` | `nset` | - |
| `belowLasts` | `dse-` | - |

## Findings

- O4/B4/G5/O5 are stable as visual/DOCM units, but they do not map one-to-one across sentence rows and printed line rows.
- B4 `$1 billion` and G5 `Volcano Bonds` share canonical sentence row 45 while occupying different printed lines; this blocks sentence-row numbering as a precise four-unit selector.
- The four active line units form page-line stream `22 25 27 32`, sentence stream `44 45 45 48`, and corridor-index stream `4 7 9 14`; none contains procedural terms or an obvious human-readable instruction.
- The O-B-B-O / Y-K-K-Y visual-state order remains real, but it is only a locator signature unless a clue names sentence, line, corridor index, or side words.
- The latest correction audit confirms no correction-added word grants selector permission, so line-unit reconciliation remains validation-only.

## Decision

- Use active line/sentence/corridor rows as locator evidence only. Do not extract by line, sentence, gap, or side-word streams without a new clue naming that unit.
- Next move: Keep source/original-layout validation as the next productive path; reopen line units only if a clue explicitly says sentence, line, gap, first/last, or side.
