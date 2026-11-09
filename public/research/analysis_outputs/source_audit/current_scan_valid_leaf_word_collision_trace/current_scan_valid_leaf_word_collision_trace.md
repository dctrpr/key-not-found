# Current Scan Valid Leaf Word-Collision Trace

Scope: projected page-75 OCR word boxes through the physically valid page 75 -> page 76 held-to-light transform, then checked whether they collide with O4/B4/G5/O5 target words as instruction, unit, or order language. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T03:33:11`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/current_scan_valid_leaf_word_collision_trace_sheet.jpg`
- Rows / source-word rows / collision rows: `8` / `6` / `5`
- Source words / target words / collision pairs: `32` / `18` / `27`
- Strict instruction rows / context rows: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=2|targets=8|sourceRows=6|collisionRows=5|sourceWords=32|targetWords=18|pairs=27|strictRows=0|contextRows=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## Target Rows

| mode | target | target text | source text | pairs | strict | context | initials | panel |
|---|---|---|---|---:|---:|---:|---|---|
| `valid_75_to_76_natural` | `O4` | ByiiREeraipy" | by riding Bitcoins coattails Buterin came up with the | 5 | 0 | 0 | `ctwbubcrbb` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_natural_O4_word_collision.jpg` |
| `valid_75_to_76_natural` | `B4` | eis |  | 0 | 0 | 0 | `e` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_natural_B4_word_collision.jpg` |
| `valid_75_to_76_natural` | `G5` | collateralized rid of those leeches. | experience. | 0 | 0 | 0 | `crotle` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_natural_G5_word_collision.jpg` |
| `valid_75_to_76_natural` | `O5` | a siukbeodmensertslveaarty | listening for the gullible and unloved. | 6 | 0 | 0 | `auasgtfl` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_natural_O5_word_collision.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | ByiiREeraipy" | Vitalik Buterin came up with | 4 | 0 | 0 | `wucbbv` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_small_jitter_best_O4_word_collision.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | eis |  | 0 | 0 | 0 | `e` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_small_jitter_best_B4_word_collision.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | collateralized rid of those leeches. | experience. blindly with your bare | 5 | 0 | 0 | `crbotyewlb` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_small_jitter_best_G5_word_collision.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | a siukbeodmensertslveaarty | listening for the gullible and unloved. | 7 | 0 | 0 | `uaagstfl` | `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/valid_75_to_76_small_jitter_best_O5_word_collision.jpg` |

## Decision

- `valid_leaf_word_collision_trace_no_instruction_source`
- Source words that reach the active boxes are ordinary page-75 prose and do not supply instruction, unit, or order wording.
- Word-box collisions do not satisfy any source-backed R3 or reopen trigger.
- Keep this as the word-level held-to-light collision stop-check for the current valid leaf.
