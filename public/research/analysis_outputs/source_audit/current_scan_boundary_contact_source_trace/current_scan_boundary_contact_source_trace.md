# Current-Scan Boundary Contact Source Trace

Created: `2026-05-21T15:15:25`

## Scope

Trace the two weak all-four boundary light-table contacts back to their source-page regions. No key derivation, hashing, WIF, seed, address, BIP39, OCR-to-key extraction, or broad candidate generation.

## Summary

- Weak groups traced: `2`.
- Trace rows: `8`.
- Source word-hit rows: `4`.
- Source strict instruction rows: `0`.
- Source strict instruction hits: `-`.
- Source context rows / terms: `0` / `-`.
- p75 word rows / trace rows: `1/4`.
- p79 word rows / trace rows: `3/4`.
- Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
- Fingerprint: `weakGroups=2|rows=8|wordRows=4|strictRows=0|contextRows=0|strictTerms=-|contextTerms=-|p75Words=1/4|p79Words=3/4|sourceR3=0|triggers=0/9|selectors=0`.

## Trace Rows

| weak group | target | source page | source coverage | words | strict | context | source text |
|---|---|---:|---:|---:|---|---|---|
| `valid_75_to_76_forced_best:target_outer_edge:right` | `O4` | 75 | `0.691176` | 0 | `-` | `-` |  |
| `valid_75_to_76_forced_best:target_outer_edge:right` | `B4` | 75 | `0.148721` | 1 | `-` | `-` | epithet. |
| `valid_75_to_76_forced_best:target_outer_edge:right` | `G5` | 75 | `0.527836` | 0 | `-` | `-` |  |
| `valid_75_to_76_forced_best:target_outer_edge:right` | `O5` | 75 | `0.135204` | 0 | `-` | `-` |  |
| `benchmark_79_to_76_best:target_outer_edge:top` | `O4` | 79 | `0.355896` | 0 | `-` | `-` |  |
| `benchmark_79_to_76_best:target_outer_edge:top` | `B4` | 79 | `0.215674` | 3 | `-` | `-` | you with all |
| `benchmark_79_to_76_best:target_outer_edge:top` | `G5` | 79 | `0.249576` | 4 | `-` | `-` | peace with it replaces |
| `benchmark_79_to_76_best:target_outer_edge:top` | `O5` | 79 | `0.206318` | 1 | `-` | `-` | ore |

## Decision

- `weak_contacts_trace_to_source_prose_or_noise_no_selector`.
- The weak all-four boundary contacts do not trace to source-side instruction wording. They are explained by ordinary source-page print, blank/noisy regions, and a forced or non-physical transform.
- Next move: Stop following the weak boundary contacts. Future work should start from a new source/original-layout clue or from source-review gates, not another threshold or boundary-side variant.

## Artifacts

- Sheet: `analysis_outputs/source_audit/current_scan_boundary_contact_source_trace/current_scan_boundary_contact_source_trace_sheet.jpg`
