# Current Scan Active Quartet Fingerprint Specificity Gate

Scope: bounded current-scan/PDF box-geometry control. No key derivation, hashing, WIF, seed, address, or broad brute-force checks were run.

- Created: `2026-05-24T13:07:05`
- Candidate page-76 rows after duplicate collapse: `13`
- Top-to-bottom quartets checked: `715`
- YKKY / OBBO hits: `54`
- YKKY / OBBO / line-gap `3/2/5` hits: `2`
- Slot-stream `OVED` hits: `4`
- Combined fingerprint hits: `1`
- Non-active combined hits: `0`
- Line pitch fitted from active boxes: `75.674528` px/line
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `candidates=13|quartets=715|YKKYOBBO=54|gap325=2|slotOVED=4|combined=1|nonActiveCombined=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Candidate Rows

| id | source | state | color | slot | center | label |
|---|---|---|---|---|---|---|
| `annotated_09_orange` | `annotated_color` | `Y` | `O` | `O5` | `1550.685,289.41` | Get some toxicity. Get some bitcoin. Open your heart to Bitcoin |
| `p76_orange_1` | `visual_orange` | `Y` | `O` | `D4` | `1511.5,399.0` | Get some toxicity. Get some bitcoin. Open your heart to |
| `p76_orange_2` | `visual_orange` | `Y` | `O` | `E2` | `916.5,474.5` | Biteoiny |
| `annotated_10_grey` | `annotated_color` | `K` | `B` | `D4` | `1366.89,843.26` | Gotta be this way. Forty years of dumb post-1971 fiat money nonsense |
| `p76_orange_3` | `visual_orange` | `Y` | `O` | `E2` | `867.5,1375.5` |  |
| `annotated_11_orange` | `annotated_color` | `Y` | `O` | `E2` | `952.59,1440.035` | by the rancid catnip of fiat money |
| `O4` | `active_index_slot` | `Y` | `O` | `O5` | `1567.5,2201.0` | buying the dip |
| `annotated_13_orange` | `annotated_color` | `Y` | `O` | `D4` | `1273.65,2265.93` | buying the dip |
| `B4` | `active_index_slot` | `K` | `B` | `V1` | `559.5,2421.5` | $1 billion |
| `annotated_14_grey` | `annotated_color` | `K` | `B` | `E2` | `961.885,2450.34` | $1 billion |
| `G5` | `active_index_slot` | `K` | `B` | `E2` | `995.5,2568.0` | Volcano Bonds |
| `annotated_15_grey` | `annotated_color` | `K` | `B` | `V1` | `765.625,2631.37` | Volcano Bonds |
| `O5` | `active_index_slot` | `Y` | `O` | `D4` | `1350.5,2957.0` | shitcoiner at heart |

## Near Hits

State/color plus line-gap hits:
- `O4 | B4 | G5 | O5` -> slots `OVED`, active `4/4`, exact active `True`
- `O4 | annotated_14_grey | G5 | O5` -> slots `OEED`, active `3/4`, exact active `False`

Slot-stream OVED hits:
- `annotated_09_orange | B4 | annotated_14_grey | O5` -> state `YKKY`, color `OBBO`, gaps `28/0/7`, active `2/4`
- `annotated_09_orange | B4 | G5 | O5` -> state `YKKY`, color `OBBO`, gaps `28/2/5`, active `3/4`
- `O4 | B4 | annotated_14_grey | O5` -> state `YKKY`, color `OBBO`, gaps `3/0/7`, active `3/4`
- `O4 | B4 | G5 | O5` -> state `YKKY`, color `OBBO`, gaps `3/2/5`, active `4/4`

Combined fingerprint hits:
- `O4 | B4 | G5 | O5` -> `YKKY/OBBO/3-2-5/OVED`, exact active `True`

## Decision

- keep_as_registration_fingerprint_not_extraction_selector.
- Reason: The combined scan-box fingerprint selects only O4/B4/G5/O5 among the available page-76 highlight/annotation controls, but it still supplies no source-backed R3 unit/order wording and unlocks no selector.
- Next move: Use the active quartet fingerprint as a future source-validation signature; do not extract until a physical/original-layout source or raw clue names the registration unit, order, transform, or read direction.

Sheet: `analysis_outputs/source_audit/current_scan_active_quartet_fingerprint_specificity_gate/current_scan_active_quartet_fingerprint_specificity_gate_sheet.jpg`
