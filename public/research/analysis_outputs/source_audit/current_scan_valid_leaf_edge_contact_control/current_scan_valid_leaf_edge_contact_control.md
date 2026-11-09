# Current Scan Valid Leaf Edge-Contact Control

Scope: tested whether the physically valid page 75 -> page 76 light-table view creates selective source-only contacts immediately around the O4/B4/G5/O5 target-box edges. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T02:45:15`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/current_scan_valid_leaf_edge_contact_control_sheet.jpg`
- Modes / target rows: `2` / `8`
- Natural edge-ring mean/min source-only coverage: `0.0418` / `0.0000`
- Natural targets >=10% / >=25% ring source-only coverage: `1` / `0`
- Natural targets at >=75th percentile vs controls: `0`
- Small-jitter shift: `-80,-20`
- Small-jitter edge-ring mean/min source-only coverage: `0.0252` / `0.0000`
- Small-jitter targets >=10% / >=25% ring source-only coverage: `0` / `0`
- Small-jitter targets at >=75th percentile vs controls: `0`
- All-four >=10% modes: `none`
- All-four >=25% modes: `none`
- All-four >=75th-percentile modes: `none`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=2|targets=8|natMean=0.0418|natMin=0.0000|nat10=1|nat25=0|natPctl75=0|jit=-80,-20|jitMean=0.0252|jitMin=0.0000|jit10=0|jit25=0|jitPctl75=0|sourceR3=0|triggers=0/9|selectors=0`

## Mode Rows

| mode | dx | dy | mean ring source-only | min ring source-only | >=.10 | >=.25 | pctl>=.75 | min percentile | decision signal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `valid_75_to_76_natural` | 0 | 0 | 0.0418 | 0.0000 | 1 | 0 | 0 | 0.207 | not selective |
| `valid_75_to_76_small_jitter_best` | -80 | -20 | 0.0252 | 0.0000 | 0 | 0 | 0 | 0.185 | not selective |

## Target Rows

| mode | target | ring source-only | best side | max side | control median | control p90 | control max | percentile | panel |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| `valid_75_to_76_natural` | `O4` | 0.1198 | top | 0.1398 | 0.0409 | 0.2773 | 0.7611 | 0.748 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_natural_O4.jpg` |
| `valid_75_to_76_natural` | `B4` | 0.0000 | top | 0.0000 | 0.0309 | 0.2125 | 0.8396 | 0.293 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_natural_B4.jpg` |
| `valid_75_to_76_natural` | `G5` | 0.0309 | right | 0.1592 | 0.0424 | 0.2638 | 0.8171 | 0.446 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_natural_G5.jpg` |
| `valid_75_to_76_natural` | `O5` | 0.0164 | right | 0.2371 | 0.0944 | 0.2893 | 0.4705 | 0.207 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_natural_O5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | 0.0102 | left | 0.1399 | 0.0944 | 0.2391 | 0.3186 | 0.185 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_small_jitter_best_O4.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | 0.0000 | top | 0.0000 | 0.0705 | 0.2339 | 0.4982 | 0.253 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_small_jitter_best_B4.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | 0.0125 | right | 0.1964 | 0.0924 | 0.2492 | 0.3411 | 0.210 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_small_jitter_best_G5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | 0.0783 | top | 0.1553 | 0.0777 | 0.2270 | 0.3179 | 0.500 | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/valid_75_to_76_small_jitter_best_O5.jpg` |

## Decision

- `valid_leaf_edge_contact_no_active_quartet_selector`
- Valid same-leaf edge collars do not create an all-four O4/B4/G5/O5 selector.
- Edge contacts are sparse and do not separate from same-size lower-page controls under natural or small-jitter alignment.
- Keep the edge panels as visual review material only; do not extract without new source/clue evidence that passes R1-R5.
