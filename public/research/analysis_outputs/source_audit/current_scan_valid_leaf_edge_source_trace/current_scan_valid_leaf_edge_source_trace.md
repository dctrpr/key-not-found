# Current Scan Valid Leaf Edge Source Trace

Scope: mapped source-only edge contacts from the valid page 75 -> page 76 held-to-light view back onto page 75, then checked whether those source regions contain source-side instruction words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T02:56:34`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/current_scan_valid_leaf_edge_source_trace_sheet.jpg`
- Trace rows / rows with components: `8` / `6`
- Rows with source words / strict instruction rows / context rows: `6` / `0` / `0`
- Source word hits / strict instruction hits / context hits: `42` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `rows=8|components=6|wordRows=6|strictRows=0|contextRows=0|words=42|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## Trace Rows

| mode | target | edge src-only | pctl | components | source words | strict | context | source text preview | panel |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | 0.1198 | 0.748 | 6 | 15 | 0 | 0 | in by riding Bitcoins coattails Buterin came up with the slinging proof of stake at | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_natural_O4.jpg` |
| `valid_75_to_76_natural` | `B4` | 0.0000 | 0.293 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_natural_B4.jpg` |
| `valid_75_to_76_natural` | `G5` | 0.0309 | 0.446 | 6 | 1 | 0 | 0 | experience. | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_natural_G5.jpg` |
| `valid_75_to_76_natural` | `O5` | 0.0164 | 0.207 | 5 | 6 | 0 | 0 | listening for the gullible and unloved. | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_natural_O5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | 0.0102 | 0.185 | 5 | 10 | 0 | 0 | Vitalik Buterin came up with he's slinging proof of stake | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_small_jitter_best_O4.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | 0.0000 | 0.253 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_small_jitter_best_B4.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | 0.0125 | 0.210 | 3 | 4 | 0 | 0 | Satoshi experience. blindly with | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_small_jitter_best_G5.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | 0.0783 | 0.500 | 6 | 6 | 0 | 0 | listening for the gullible and unloved. | `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/valid_75_to_76_small_jitter_best_O5.jpg` |

## Decision

- `valid_leaf_edge_source_trace_no_instruction_source`
- The valid same-leaf edge contacts do not trace to source-side unit/order instructions.
- Source-word hits are ordinary page-75 article/header text or sparse context terms; strict instruction terms remain absent.
- Keep this as a provenance stop-check for current-scan light-table edge contacts.
