# Current Scan Lane Affine Source Trace

Scope: traced page-75 source words through the valid lane-affine transforms into O4/B4/G5/O5 on page 76. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T19:39:30`
- Valid affine modes traced: `3`
- Trace rows / source-word rows / source-word hits: `12` / `9` / `51`
- Supported rows / above-control-p95 rows: `6` / `0`
- Strict instruction rows / hits: `1` / `1`
- Context rows / hits: `0` / `0`
- All-four supported modes: `[]`
- Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`
- Sheet: `analysis_outputs/source_audit/current_scan_lane_affine_source_trace/current_scan_lane_affine_source_trace_sheet.jpg`
- Fingerprint: `modes=3|rows=12|wordRows=9|words=51|supported=6|aboveP95=0|strictRows=1|strictHits=1|contextRows=0|contextHits=0|allFour=0|sourceR3=0|triggers=0/9|selectors=0`

## Trace Rows

| mode | target | supported | above p95 | source fraction | word hits | strict | context | preview |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `natural_hflip` | `O4` | `0` | `0` | `0.094531` | `5` | `0` | `0` | the with up came Buterin |
| `natural_hflip` | `B4` | `0` | `0` | `0.0` | `0` | `0` | `0` |  |
| `natural_hflip` | `G5` | `0` | `0` | `0.036783` | `1` | `0` | `0` | experience. |
| `natural_hflip` | `O5` | `1` | `0` | `0.127504` | `6` | `0` | `0` | unloved. and gullible the for listening |
| `top_header_lane+footer_lane_affine` | `O4` | `1` | `0` | `0.115453` | `8` | `0` | `0` | riding by in cash to came Buterin Vitalik |
| `top_header_lane+footer_lane_affine` | `B4` | `0` | `0` | `0.0` | `0` | `0` | `0` |  |
| `top_header_lane+footer_lane_affine` | `G5` | `1` | `0` | `0.118973` | `3` | `0` | `0` | Maximalist, experience. Satoshi |
| `top_header_lane+footer_lane_affine` | `O5` | `0` | `0` | `0.060998` | `10` | `1` | `0` | con from words pleasant Nice, gullible the for listening easy |
| `top_header_lane+lower_body_lane_affine` | `O4` | `1` | `0` | `0.524714` | `0` | `0` | `0` |  |
| `top_header_lane+lower_body_lane_affine` | `B4` | `1` | `0` | `0.107111` | `4` | `0` | `0` | name. bad a it |
| `top_header_lane+lower_body_lane_affine` | `G5` | `0` | `0` | `0.063539` | `5` | `0` | `0` | mEthereum the at stake of |
| `top_header_lane+lower_body_lane_affine` | `O5` | `1` | `0` | `0.112625` | `9` | `0` | `0` | Satoshi whole the of BSR blindly digging be wouldn't |

## Decision

- `current_scan_lane_affine_source_trace_no_selector`
- The best lane-affine near miss traces to ordinary page-75 source words and does not provide source-backed instruction, unit, order, or transform language.
- No traced row supplies an action-plus-unit instruction such as read/take/select plus word/letter/line, and no all-four affine mode survives the control threshold.

## Next Move

- Keep current-scan held-to-light lane/affine registration closed; require a distinct physical/original-layout source or raw clue wording that supplies unit, order, and transform.
