# Current Scan Valid Leaf Line-Band Trace

Scope: projected page-75 OCR line bands through the physically valid page 75 -> page 76 held-to-light transform, then checked whether they line up with O4/B4/G5/O5 target bands as instruction, unit, context, or order language. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T03:39:08`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/current_scan_valid_leaf_line_band_trace_sheet.jpg`
- Rows / source-line rows / line-overlap rows: `8` / `6` / `6`
- Source lines / target lines / source-target overlaps: `14` / `20` / `13`
- Strict instruction rows / context rows: `1` / `5`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=2|targets=8|sourceRows=6|overlapRows=6|sourceLines=14|targetLines=20|overlaps=13|strictRows=1|contextRows=5|strict=1|context=6|sourceR3=0|triggers=0/9|selectors=0`

## Target Rows

| mode | target | target text | source text | overlaps | strict | context | panel |
|---|---|---|---|---:|---:|---:|---|
| `valid_75_to_76_natural` | `O4` | trolling the International Monetary Fund (IMF) on Twitter? / He's taunting them, tell | to cash in by riding Bitcoins coattails that give it a bad name. / Vitalik Buterin came up with the (MRERREIGS | 3 | 0 | 1 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_natural_O4_line_band.jpg` |
| `valid_75_to_76_natural` | `B4` | he was going to tap his nation's volcanoes to mine / eis in bitcoin that he should se |  | 0 | 0 | 0 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_natural_B4_line_band.jpg` |
| `valid_75_to_76_natural` | `G5` | billions worth of future bitcoin earnings / collateralized to pay off the IMF / loan  | the BSR of the whole Satoshi experience. / You wouldn't be digging blindly with your bare | 2 | 0 | 1 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_natural_G5_line_band.jpg` |
| `valid_75_to_76_natural` | `O5` | Maybe because he's a siukbeodmensertslveaarty | to. Nice, pleasant words from con men and shitcoiners / are easy listening for the gullible and unloved. | 1 | 1 | 1 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_natural_O5_line_band.jpg` |
| `valid_75_to_76_small_jitter_best` | `O4` | trolling the International Monetary Fund (IMF) on Twitter? / He's taunting them, tell | to cash in by riding Bitcoins coattails that give it a bad name. / Vitalik Buterin came up with the (MRERREIGS | 3 | 0 | 1 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_small_jitter_best_O4_line_band.jpg` |
| `valid_75_to_76_small_jitter_best` | `B4` | he was going to tap his nation's volcanoes to mine / eis in bitcoin that he should se |  | 0 | 0 | 0 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_small_jitter_best_B4_line_band.jpg` |
| `valid_75_to_76_small_jitter_best` | `G5` | billions worth of future bitcoin earnings / collateralized to pay off the IMF / loan  | Go Bitcoin Toxic Maximalist, / the BSR of the whole Satoshi experience. / You wouldn't be digging blindly with | 3 | 0 | 2 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_small_jitter_best_G5_line_band.jpg` |
| `valid_75_to_76_small_jitter_best` | `O5` | Maybe because he's a siukbeodmensertslveaarty | are easy listening for the gullible and unloved. | 1 | 0 | 0 | `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/valid_75_to_76_small_jitter_best_O5_line_band.jpg` |

## Decision

- `valid_leaf_line_band_trace_no_instruction_source`
- Projected source line bands that reach the active target bands are ordinary page-75 prose and do not supply source-backed instruction, unit, or order wording.
- Line-band overlaps do not satisfy any source-backed R3 or reopen trigger.
- Keep this as the line-level held-to-light stop-check for the current valid leaf.
