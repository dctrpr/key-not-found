# Current Scan Held-to-Light Active-Box Balance Gate

Scope: reused the current scan held-to-light simulator and checked whether any physically valid page-75-to-page-76 view isolates O4/B4/G5/O5 together. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.

- Created: `2026-05-24T08:18:12`
- Decision: `current_scan_held_to_light_active_box_balance_no_selector`
- Active simulator rows: `9`
- Physical natural selector candidates: `0`
- Same-leaf 75->76 all-four >=10% rows: `0`
- Same-leaf 75->76 all-four >=25% rows: `0`
- Nonphysical all-four >=10% rows: `2`
- Best physical natural min coverage: `0.0`
- Best same-leaf shifted min coverage: `0.054032`
- Best nonphysical min coverage: `0.113826`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/current_scan_held_to_light_active_box_balance_gate_sheet.jpg`
- Fingerprint: `activeRows=9|physicalCandidates=0|sameLeafAll4_10=0|sameLeafAll4_25=0|nonphysicalAll4_10=2|nonphysicalAll4_25=0|naturalMin=0.0000|sameLeafBestMin=0.0540@-220,200|nonphysicalBestMin=0.1138@nonphysical_79_to_76:40,80|sourceR3=0|triggers=0/9|selectors=0`

## Active Rows

| pair | mode | dx | dy | O4 | B4 | G5 | O5 | min | all4>=10 | physical natural | forced shift | nonphysical |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `nonphysical_78_to_76` | `natural_hflip` | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0139 | 0.0000 | False | False | False | True |
| `nonphysical_78_to_76` | `best_global_feature` | 220 | 180 | 0.8004 | 0.0001 | 0.0000 | 0.0451 | 0.0000 | False | False | True | True |
| `nonphysical_78_to_76` | `best_page76_active_boxes` | -220 | 180 | 0.2347 | 0.0000 | 0.0000 | 0.6058 | 0.0000 | False | False | True | True |
| `nonphysical_79_to_76` | `natural_hflip` | 0 | 0 | 0.0091 | 0.0714 | 0.0002 | 0.2109 | 0.0002 | False | False | False | True |
| `nonphysical_79_to_76` | `best_global_feature` | 40 | 80 | 0.8416 | 0.1138 | 0.1328 | 0.3203 | 0.1138 | True | False | True | True |
| `nonphysical_79_to_76` | `best_page76_active_boxes` | 40 | 80 | 0.8416 | 0.1138 | 0.1328 | 0.3203 | 0.1138 | True | False | True | True |
| `same_leaf_75_to_76` | `natural_hflip` | 0 | 0 | 0.1223 | 0.0000 | 0.0526 | 0.1654 | 0.0000 | False | True | False | False |
| `same_leaf_75_to_76` | `best_global_feature` | -220 | 200 | 0.9766 | 0.1299 | 0.0540 | 0.0999 | 0.0540 | False | False | True | False |
| `same_leaf_75_to_76` | `best_page76_active_boxes` | -220 | 200 | 0.9766 | 0.1299 | 0.0540 | 0.0999 | 0.0540 | False | False | True | False |

## Decision

- The physically valid natural page 75 -> page 76 light-table view does not isolate the active quartet: B4 coverage is `0.0000`, and all-four coverage fails.
- The best same-leaf 75 -> 76 row is a forced `-220,+200` translation and still fails all-four >=10% because G5 remains low.
- The only all-four >=10% row is nonphysical page 79 -> page 76 with a `+40,+80` shift, so it is useful as a control but not as a physical/source-backed rule.
- Keep current-scan held-to-light balance closed unless a new physical/original-layout source changes the page registration or provides explicit unit/order wording.

## Next Move

- Use this balance gate as the visual light-table stop-check. Best direction remains original/source-layout validation or raw clue wording that explicitly names transform, unit, and order.
