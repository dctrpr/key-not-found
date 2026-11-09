# Current Scan Valid Leaf Glyph-Slot Source Trace

Scope: subdivided O4/B4/G5/O5 by the actual page-76 OVERDOSE glyph slots under valid page 75 -> page 76 held-to-light alignment, then mapped slot-level source-only components back to page-75 source words. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T03:17:40`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/current_scan_valid_leaf_glyph_slot_source_trace_sheet.jpg`
- Target rows / slot rows: `8` / `20`
- Component rows / word rows: `4` / `4`
- Total components / component pixels: `19` / `830`
- Source word hits / strict instruction hits / context hits: `5` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=2|targets=8|slots=20|componentRows=4|wordRows=4|strictRows=0|contextRows=0|components=19|componentPixels=830|words=5|strict=0|context=0|streams=S.RD/...D;S.RR/..RR|sourceR3=0|triggers=0/9|selectors=0`

## Mode Streams

| mode | dominant pixel stream | dominant component stream |
|---|---|---|
| `valid_75_to_76_natural` | `S.RD` | `...D` |
| `valid_75_to_76_small_jitter_best` | `S.RR` | `..RR` |

## Target Rows

| mode | target | pixel letter | component letter | slot pixels | components | source words | strict | context | source text preview | panel |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | `S` | `.` | 83 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_natural_O4_glyph_slot_trace.jpg` |
| `valid_75_to_76_natural` | `B4` | `.` | `.` | 0 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_natural_B4_glyph_slot_trace.jpg` |
| `valid_75_to_76_natural` | `G5` | `R` | `.` | 111 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_natural_G5_glyph_slot_trace.jpg` |
| `valid_75_to_76_natural` | `O5` | `D` | `D` | 99 | 1 | 1 | 0 | 0 | gullible | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_natural_O5_glyph_slot_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | `S` | `.` | 1 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_small_jitter_best_O4_glyph_slot_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | `.` | `.` | 0 | 0 | 0 | 0 | 0 |  | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_small_jitter_best_B4_glyph_slot_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | `R` | `R` | 888 | 17 | 2 | 0 | 0 | experience. | experience. | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_small_jitter_best_G5_glyph_slot_trace.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | `R` | `R` | 158 | 1 | 2 | 0 | 0 | gullible and | `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/valid_75_to_76_small_jitter_best_O5_glyph_slot_trace.jpg` |

## Decision

- `valid_leaf_glyph_slot_source_trace_no_instruction_source`
- The valid same-leaf OVERDOSE glyph-slot source pixels do not trace to source-side unit/order instructions.
- Slot-aware streams remain non-extractive (`S.RD`/`...D` natural and `S.RR`/`..RR` small-jitter), and source-word hits are sparse ordinary page-75 text.
- Keep this as the glyph-slot provenance stop-check for the current valid leaf.
