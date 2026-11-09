# Active Label Index Provenance Audit

Scope: check whether `O4/B4/G5/O5` is a source-backed index rule or an analysis handle. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T20:24:05`
- Overlay: `analysis_outputs/source_audit/active_label_index_provenance/active_label_index_provenance_overlay.jpg`

## Target Labels

| label | phrase | DOCM highlight | DOCM paragraph | best orange match | status |
|---|---|---|---|---|---|
| O4 | buying the dip. | yellow:13 | 63 | p76_orange_4 / IoU 0.6709 | source-backed orange ordinal |
| B4 | $1 billion | black:9 | 66 | p76_orange_1 / IoU 0.0 | analysis alias, not source-backed global index |
| G5 | Volcano Bonds | black:12 | 68 | p76_orange_1 / IoU 0.0 | analysis alias, not source-backed global index |
| O5 | shitcoiner at heart. | yellow:18 | 73 | p76_orange_5 / IoU 1.0 | source-backed orange ordinal |

## Compact Streams Checked

| stream | value | instruction hits |
|---|---|---|
| activeLabelStream | `O4B4G5O5` | - |
| activeNumberStream | `4455` | - |
| activeColorStream | `OBBO` | - |
| docmParagraphStream | `63 66 68 73` | - |
| docmRunStream | `124 131 137 151` | - |
| phraseInitialStream | `b1vs` | - |

## Findings

- O4 and O5 are source-backed only as orange-highlight ordinals on page 76.
- B4 and G5 are confirmed target handles, but their numeric suffixes are not derived from a canonical source-side B/G highlight index in the current files.
- The active visual order is O4 -> B4 -> G5 -> O5, but this is a report order, not an independent instruction.
- No compact stream from labels, digits, colors, DOCM paragraph indexes, DOCM run indexes, or phrase initials contains instruction terms.
- Therefore 4455, O4B4G5O5, and mixed B/G/O numbering should not be promoted into key material or selectors without a new clue naming numbers/indexes.

## Decision

- Use O4/B4/G5/O5 as report handles only. The only source-backed numeric part is the orange local order for O4/O5; the mixed label stream is not a puzzle rule under current evidence.
- Next move: Stop local label-number inference. Future progress should come from a new source/original-layout/physical witness or a clue that names an extraction unit and order.
