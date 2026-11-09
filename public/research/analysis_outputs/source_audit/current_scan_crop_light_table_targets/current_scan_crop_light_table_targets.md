# Current Scan Crop Light-Table Targets

Scope: zoomed the current held-to-light simulation into the active page-76 O4/B4/G5/O5 boxes. Compared the physically valid 75->76 same-leaf view against the strongest non-physical 79->76 visual-registration benchmark. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad candidate generation was run.

- Created: `2026-05-21T14:43:38`
- HTML crop viewer: `analysis_outputs/source_audit/current_scan_crop_light_table_targets/index.html`
- Sheet: `analysis_outputs/source_audit/current_scan_crop_light_table_targets/current_scan_crop_light_table_targets_sheet.jpg`
- Scenarios / target crop rows: `4` / `16`
- All-four active target coverage at >=10% / >=25% / >=50%: `1` / `0` / `0`
- Best mean active coverage: `benchmark_79_to_76_best` at `0.3521`
- Best >=50% target count: `valid_75_to_76_forced_best` with `1/4` targets
- Valid natural 75->76 O4/B4/G5/O5 source coverage: `0.1223,0.0000,0.0526,0.1654`
- Valid forced 75->76 O4/B4/G5/O5 source coverage: `0.9766,0.1299,0.0540,0.0999`
- Benchmark 79->76 best O4/B4/G5/O5 source coverage: `0.8416,0.1138,0.1328,0.3203`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `scenarios=4|targets=16|all10=1|all25=0|all50=0|bestMean=benchmark_79_to_76_best:0.3521|best50=valid_75_to_76_forced_best:1|validNat=0.1223,0.0000,0.0526,0.1654|validForced=0.9766,0.1299,0.0540,0.0999|bench79=0.8416,0.1138,0.1328,0.3203|sourceR3=0|triggers=0/9|selectors=0`

## Scenario Rows

| scenario | topology | dx | dy | O4 | B4 | G5 | O5 | >=.25 | >=.50 | decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `valid_75_to_76_natural` | valid same leaf | 0 | 0 | 0.1223 | 0.0000 | 0.0526 | 0.1654 | 0 | 0 | no active quartet crop selector |
| `valid_75_to_76_forced_best` | valid same leaf, forced boundary shift | -220 | 200 | 0.9766 | 0.1299 | 0.0540 | 0.0999 | 1 | 1 | single-target ink concentration |
| `benchmark_79_to_76_natural` | non-physical benchmark | 0 | 0 | 0.0091 | 0.0714 | 0.0002 | 0.2109 | 0 | 0 | no active quartet crop selector |
| `benchmark_79_to_76_best` | non-physical benchmark | 40 | 80 | 0.8416 | 0.1138 | 0.1328 | 0.3203 | 2 | 1 | single-target ink concentration |

## Target Crop Rows

| scenario | target | source coverage | box jaccard | crop jaccard | dominant source signal | image |
|---|---|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | 0.1223 | 0.1208 | 0.0593 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_natural_O4.jpg` |
| `valid_75_to_76_natural` | `B4` | 0.0000 | 0.0000 | 0.0033 | none | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_natural_B4.jpg` |
| `valid_75_to_76_natural` | `G5` | 0.0526 | 0.0592 | 0.0425 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_natural_G5.jpg` |
| `valid_75_to_76_natural` | `O5` | 0.1654 | 0.1696 | 0.1110 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_natural_O5.jpg` |
| `valid_75_to_76_forced_best` | `O4` | 0.9766 | 0.9841 | 0.3703 | dark | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_forced_best_O4.jpg` |
| `valid_75_to_76_forced_best` | `B4` | 0.1299 | 0.1169 | 0.1540 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_forced_best_B4.jpg` |
| `valid_75_to_76_forced_best` | `G5` | 0.0540 | 0.0521 | 0.1074 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_forced_best_G5.jpg` |
| `valid_75_to_76_forced_best` | `O5` | 0.0999 | 0.0963 | 0.0880 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/valid_75_to_76_forced_best_O5.jpg` |
| `benchmark_79_to_76_natural` | `O4` | 0.0091 | 0.0089 | 0.0798 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_natural_O4.jpg` |
| `benchmark_79_to_76_natural` | `B4` | 0.0714 | 0.0516 | 0.0157 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_natural_B4.jpg` |
| `benchmark_79_to_76_natural` | `G5` | 0.0002 | 0.0002 | 0.0042 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_natural_G5.jpg` |
| `benchmark_79_to_76_natural` | `O5` | 0.2109 | 0.2072 | 0.1367 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_natural_O5.jpg` |
| `benchmark_79_to_76_best` | `O4` | 0.8416 | 0.8421 | 0.2704 | dark | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_best_O4.jpg` |
| `benchmark_79_to_76_best` | `B4` | 0.1138 | 0.1015 | 0.0450 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_best_B4.jpg` |
| `benchmark_79_to_76_best` | `G5` | 0.1328 | 0.1331 | 0.0542 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_best_G5.jpg` |
| `benchmark_79_to_76_best` | `O5` | 0.3203 | 0.3203 | 0.1682 | grey | `analysis_outputs/source_audit/current_scan_crop_light_table_targets/benchmark_79_to_76_best_O5.jpg` |

## Decision

- `crop_light_table_no_active_quartet_selector`
- At crop level, the valid 75->76 leaf does not cover all four O4/B4/G5/O5 targets, even with the forced boundary shift. The strongest 79->76 overlay is still non-physical and concentrates source ink mainly on O4/O5 rather than the full active quartet.
- Use the crop panels for manual visual review, but do not extract from them. The next bounded pass should test whether actual OVERDOSE glyph rectangles projected into these crop windows change the result, because current light-table ink alone does not supply the missing source-backed unit/order rule.
