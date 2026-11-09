# Current-Scan Held-To-Light Simulator

Scope: built a visual held-to-light simulator from the existing Bitcoin Magazine PDF/page images. PDF-extracted `source_images` are rotated 180 degrees into readable/upright coordinates, then back pages are horizontally mirrored over target pages. No OCR extraction, key derivation, hashing, seed/WIF/address checks, or broad candidate generation was run.

- Created: `2026-05-21T14:19:30`
- HTML simulator: `analysis_outputs/source_audit/current_scan_held_to_light_simulator/index.html`
- Sheet: `analysis_outputs/source_audit/current_scan_held_to_light_simulator/current_scan_held_to_light_simulator_sheet.jpg`
- Pair/mode rows: `9` / `21`
- Natural same-leaf 75->76 active coverage: `0.1003`
- Best bounded same-leaf 75->76 active coverage: `0.3242` at dx/dy `-220,200`
- Best page-76 active overlay: `nonphysical_79_to_76` / `best_global_feature` at active coverage `0.3840` with dx/dy `40,80`
- Best global feature overlay: `same_leaf_77_to_78` / `best_global_feature` balanced `0.5220`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pairs=9|rows=21|sameLeaf75natural=0.1003|sameLeaf75best=0.3242@-220,200|bestP76=nonphysical_79_to_76:best_global_feature:0.3840@40,80|bestGlobal=same_leaf_77_to_78:0.5220|sourceR3=0|triggers=0/9|selectors=0`

## Page-76 Rows

| pair | mode | dx | dy | active coverage | O4 | B4 | G5 | O5 | image |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| same_leaf_75_to_76 | `natural_hflip` | 0 | 0 | 0.1003 | 0.1223 | 0.0000 | 0.0526 | 0.1654 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/same_leaf_75_to_76_natural_hflip.jpg` |
| same_leaf_75_to_76 | `best_global_feature` | -220 | 200 | 0.3242 | 0.9766 | 0.1299 | 0.0540 | 0.0999 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/same_leaf_75_to_76_best_global_feature.jpg` |
| same_leaf_75_to_76 | `best_page76_active_boxes` | -220 | 200 | 0.3242 | 0.9766 | 0.1299 | 0.0540 | 0.0999 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/same_leaf_75_to_76_best_page76_active_boxes.jpg` |
| nonphysical_78_to_76 | `natural_hflip` | 0 | 0 | 0.0047 | 0.0000 | 0.0000 | 0.0000 | 0.0139 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/nonphysical_78_to_76_natural_hflip.jpg` |
| nonphysical_78_to_76 | `best_global_feature` | 220 | 180 | 0.2226 | 0.8004 | 0.0001 | 0.0000 | 0.0451 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/nonphysical_78_to_76_best_global_feature.jpg` |
| nonphysical_78_to_76 | `best_page76_active_boxes` | -220 | 180 | 0.2921 | 0.2347 | 0.0000 | 0.0000 | 0.6058 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/nonphysical_78_to_76_best_page76_active_boxes.jpg` |
| nonphysical_79_to_76 | `natural_hflip` | 0 | 0 | 0.0849 | 0.0091 | 0.0714 | 0.0002 | 0.2109 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/nonphysical_79_to_76_natural_hflip.jpg` |
| nonphysical_79_to_76 | `best_global_feature` | 40 | 80 | 0.3840 | 0.8416 | 0.1138 | 0.1328 | 0.3203 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/nonphysical_79_to_76_best_global_feature.jpg` |
| nonphysical_79_to_76 | `best_page76_active_boxes` | 40 | 80 | 0.3840 | 0.8416 | 0.1138 | 0.1328 | 0.3203 | `analysis_outputs/source_audit/current_scan_held_to_light_simulator/nonphysical_79_to_76_best_page76_active_boxes.jpg` |

## Decision

- `simulator_created_no_current_selector_unlocked`
- The simulator makes the current scan usable for visual leaf/spread inspection, but the physically valid 75->76 same-leaf view does not naturally select the lower O4/B4/G5/O5 corridor. Forced active-box alignment remains a translation search, not source-backed unit/order evidence.
- Use the simulator for manual visual review and for testing any source clue that names a page pair or transform. Next automated pass should inspect the PDF object layout/layer assets for original embedded-image provenance rather than key material.
