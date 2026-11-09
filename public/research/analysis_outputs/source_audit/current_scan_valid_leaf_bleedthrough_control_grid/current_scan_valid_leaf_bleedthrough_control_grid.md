# Current Scan Valid Leaf Bleed-Through Control Grid

Scope: tested the physically valid page 75 -> page 76 held-to-light model from the current scan/PDF. Page 75 was mirrored onto page 76, then source-only signal inside O4/B4/G5/O5 was ranked against same-size lower-page control boxes. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad candidate generation was run.

- Created: `2026-05-24T02:38:43`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/current_scan_valid_leaf_bleedthrough_control_grid_sheet.jpg`
- Modes / target rows: `2` / `8`
- Natural 75->76 mean/min source-only coverage: `0.0032` / `0.0000`
- Natural targets >=10% / >=25% source-only coverage: `0` / `0`
- Natural targets at >=75th percentile vs controls: `0`
- Small-jitter best shift: `-80,-20`
- Small-jitter mean/min source-only coverage: `0.0128` / `0.0000`
- Small-jitter targets >=10% / >=25% source-only coverage: `0` / `0`
- Small-jitter targets at >=75th percentile vs controls: `0`
- All-four >=10% modes: `none`
- All-four >=25% modes: `none`
- All-four >=75th-percentile modes: `none`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=2|targets=8|natMean=0.0032|natMin=0.0000|nat10=0|nat25=0|natPctl75=0|jit=-80,-20|jitMean=0.0128|jitMin=0.0000|jit10=0|jit25=0|jitPctl75=0|sourceR3=0|triggers=0/9|selectors=0`

## Mode Rows

| mode | dx | dy | mean source-only | min source-only | >=.10 | >=.25 | pctl>=.75 | min percentile | decision signal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `valid_75_to_76_natural` | 0 | 0 | 0.0032 | 0.0000 | 0 | 0 | 0 | 0.255 | not selective |
| `valid_75_to_76_small_jitter_best` | -80 | -20 | 0.0128 | 0.0000 | 0 | 0 | 0 | 0.205 | not selective |

## Target Rows

| mode | target | source-only | control median | control p90 | control max | percentile | dominant source | panel |
|---|---|---:|---:|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | 0.0037 | 0.0893 | 0.2634 | 0.8685 | 0.269 | grey | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_natural_O4.jpg` |
| `valid_75_to_76_natural` | `B4` | 0.0000 | 0.0259 | 0.2119 | 0.8558 | 0.343 | none | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_natural_B4.jpg` |
| `valid_75_to_76_natural` | `G5` | 0.0058 | 0.0943 | 0.2594 | 0.8798 | 0.320 | grey | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_natural_G5.jpg` |
| `valid_75_to_76_natural` | `O5` | 0.0032 | 0.1329 | 0.2704 | 0.6552 | 0.255 | grey | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_natural_O5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | 0.0000 | 0.0506 | 0.2177 | 0.5960 | 0.205 | grey | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_small_jitter_best_O4.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | 0.0000 | 0.0469 | 0.2327 | 0.8157 | 0.352 | none | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_small_jitter_best_B4.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | 0.0461 | 0.0522 | 0.2235 | 0.6890 | 0.448 | grey | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_small_jitter_best_G5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | 0.0051 | 0.0510 | 0.1435 | 0.3859 | 0.226 | grey | `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/valid_75_to_76_small_jitter_best_O5.jpg` |

## Decision

- `valid_leaf_bleedthrough_no_active_quartet_selector`
- Natural valid same-leaf bleed-through does not create an all-four O4/B4/G5/O5 source-only selector.
- The small-jitter best shift is still a bounded alignment search and does not produce all-four >=25% coverage or all-four high-percentile control separation.
- Treat the current light-table view as visual review material only; do not extract from it without new source/clue evidence that passes R1-R5.
