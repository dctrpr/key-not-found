# Page 76 Highlight Edge Selector Audit

Scope: test whether the active O4/B4/G5/O5 highlight boxes select adjacent text at their left/right/top/bottom edges. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T20:43:21`
- Overlay: `analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector_overlay.jpg`

## Edge Neighbors

| target | phrase | left | right | above | below | first/last significant |
|---|---|---|---|---|---|---|
| `O4` | buying the dip. | he's (same-row-left, 24.56 px) | - | on (vertical-overlap-above, 17.11 px) | announced (vertical-overlap-below, 17.65 px) | `b/p` |
| `B4` | $1 billion | - | in (same-row-right, 52.76 px) | was (vertical-overlap-above, 39.13 px) | billions (vertical-overlap-below, 20.15 px) | `$/n` |
| `G5` | Volcano Bonds | collateralized (same-row-left, 6.53 px) | to (same-row-right, 23.2 px) | future (vertical-overlap-above, 36.74 px) | those (vertical-overlap-below, 17.09 px) | `V/s` |
| `O5` | shitcoiner at heart. | a (same-row-left, 13.79 px) | - | trust (vertical-overlap-above, 60.36 px) | - | `s/t` |

## Streams Checked

| stream | value | instruction hits |
|---|---|---|
| `targetFirstLiteral` | `b$Vs` | - |
| `targetLastLiteral` | `.ns.` | - |
| `targetFirstAlpha` | `b$Vs` | - |
| `targetLastAlpha` | `pnst` | - |
| `leftWords` | `he's \| - \| collateralized \| a` | - |
| `leftInitials` | `h-ca` | - |
| `leftLasts` | `s-da` | - |
| `rightWords` | `- \| in \| to \| -` | - |
| `rightInitials` | `-it-` | - |
| `rightLasts` | `-no-` | - |
| `aboveWords` | `on \| was \| future \| trust` | - |
| `aboveInitials` | `owft` | - |
| `aboveLasts` | `nset` | - |
| `belowWords` | `announced \| billions \| those \| -` | - |
| `belowInitials` | `abt-` | - |
| `belowLasts` | `dse-` | - |

## Edge Crossing Character Counts

| target | left | right | top | bottom |
|---|---:|---:|---:|---:|
| `O4` | 0 | 0 | 0 | 0 |
| `B4` | 0 | 0 | 3 | 0 |
| `G5` | 0 | 0 | 0 | 0 |
| `O5` | 0 | 0 | 24 | 0 |

## Findings

- The four active target boxes do not expose a consistent adjacent-edge selector: left/right sides are absent for some targets, and above/below words are ordinary neighboring prose.
- Literal target edges produce only the known phrase-edge streams, not instructions: first/significant `b$Vs`, last/significant `pnst`.
- Adjacent side streams also fail as instructions; they mostly restate local prose around El Salvador/Bukele/Volcano Bonds/O5.
- Edge-crossing characters are not one-letter selectors. Top/bottom crossings generally traverse whole highlighted text rows, while left/right often hit zero or arbitrary OCR character edges.
- This keeps the active highlights as target locators and source-comparison evidence, not a complete word/letter edge rule.

## Decision

- Do not use active highlight boundaries alone as selectors. Reopen this only if a new clue specifies a side such as left/right/top/bottom, or a physical/original-layout source changes the edge contacts.
- Next move: Shift back to external/source instructions: find a rule naming the unit/order, or compare a new physical/original-layout scan against these locked edge-adjacency baselines.
