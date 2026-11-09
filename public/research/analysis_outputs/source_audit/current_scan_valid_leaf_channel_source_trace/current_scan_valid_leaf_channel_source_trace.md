# Current Scan Valid Leaf Channel Source Trace

Scope: separated valid page 75 -> page 76 source-only pixels inside O4/B4/G5/O5 into orange, dark, and grey masks, then mapped each channel back to page-75 source words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T03:24:29`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/current_scan_valid_leaf_channel_source_trace_sheet.jpg`
- Target rows / channel rows: `8` / `24`
- Component rows / orange component rows / word rows: `5` / `0` / `5`
- Total components / component pixels / source-only pixels: `35` / `1494` / `2481`
- Source word hits / strict instruction hits / context hits: `6` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=2|targets=8|channels=24|componentRows=5|orangeComponentRows=0|wordRows=5|strictRows=0|contextRows=0|components=35|componentPixels=1494|sourcePixels=2481|words=6|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## Target Rows

| mode | target | dominant channel | pixels | components | source words | strict | context | source text preview | panel |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | `grey` | 159 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_natural_O4_channel_trace.jpg` |
| `valid_75_to_76_natural` | `B4` | `.` | 0 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_natural_B4_channel_trace.jpg` |
| `valid_75_to_76_natural` | `G5` | `grey` | 199 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_natural_G5_channel_trace.jpg` |
| `valid_75_to_76_natural` | `O5` | `grey` | 189 | 2 | 2 | 0 | 0 | gullible | gullible | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_natural_O5_channel_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | `grey` | 1 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_small_jitter_best_O4_channel_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | `.` | 0 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_small_jitter_best_B4_channel_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | `grey` | 1647 | 32 | 2 | 0 | 0 | experience. | experience. | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_small_jitter_best_G5_channel_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | `grey` | 286 | 1 | 2 | 0 | 0 | gullible and | `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/valid_75_to_76_small_jitter_best_O5_channel_trace.jpg` |

## Decision

- `valid_leaf_channel_source_trace_no_instruction_source`
- Orange source-only components are absent in the valid leaf; dark/grey components trace only to sparse ordinary page-75 words.
- Channel separation does not expose a source-side instruction, context cue, unit, or order.
- Keep this as the color/channel provenance stop-check for the current valid leaf.
