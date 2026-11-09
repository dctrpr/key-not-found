# Current Scan Valid Leaf Interior Source Trace

Scope: mapped source-only interior pixels inside O4/B4/G5/O5 from the valid page 75 -> page 76 held-to-light view back onto page 75, then checked whether those source regions contain source-side instruction words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T03:09:14`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/current_scan_valid_leaf_interior_source_trace_sheet.jpg`
- Trace rows / rows with components: `8` / `3`
- Total components / component pixels: `14` / `727`
- Rows with source words / strict instruction rows / context rows: `3` / `0` / `0`
- Source word hits / strict instruction hits / context hits: `4` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `rows=8|componentRows=3|totalComponents=14|componentPixels=727|wordRows=3|strictRows=0|contextRows=0|words=4|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## Trace Rows

| mode | target | interior src-only | pixels | components | source words | strict | context | source text preview | panel |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | 0.0037 | 83 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_natural_O4.jpg` |
| `valid_75_to_76_natural` | `B4` | 0.0000 | 0 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_natural_B4.jpg` |
| `valid_75_to_76_natural` | `G5` | 0.0058 | 111 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_natural_G5.jpg` |
| `valid_75_to_76_natural` | `O5` | 0.0032 | 99 | 1 | 1 | 0 | 0 | gullible | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_natural_O5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | 0.0000 | 1 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_small_jitter_best_O4.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | 0.0000 | 0 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_small_jitter_best_B4.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | 0.0461 | 888 | 12 | 1 | 0 | 0 | experience. | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_small_jitter_best_G5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | 0.0051 | 158 | 1 | 2 | 0 | 0 | gullible and | `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/valid_75_to_76_small_jitter_best_O5.jpg` |

## Decision

- `valid_leaf_interior_source_trace_no_instruction_source`
- The valid same-leaf interior source-only components do not trace to source-side unit/order instructions.
- Source-word hits are sparse ordinary page-75 article text; strict instruction terms remain absent.
- Keep this as a provenance stop-check for current-scan light-table interior bleed variants.
