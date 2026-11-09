# Current Scan Light-Table Blend-Mode Gate

Scope: tested whether alternate held-to-light blend modes make O4/B4/G5/O5 uniquely stand out against nearby line-shifted controls. The pass uses the current scan/PDF page images and the existing held-to-light registrations only. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T08:48:54`
- Scenarios / blend rows: `4` / `60`
- Blend modes / alphas: `multiply, darken, average, difference, source_ink` / `0.35, 0.50, 0.70`
- Active boxes / line-shift control boxes: `4` / `24`
- Estimated line pitch: `74.55px`
- Best natural 75->76 outliers: `4/4` via `average@0.70` with min active-control p95 gain `29.55`
- Best natural source-supported outliers: `3/4` with min active source-ink ratio `0.0000`
- Best forced/control outliers: `3/4` via `nonphysical_79_to_76_forced_active` / `average@0.35` with min active-control p95 gain `-10.50`
- Best forced/control source-supported outliers: `3/4`
- Natural all-four active-outlier rows / forced-or-control all-four rows: `3` / `0`
- Natural all-four source-supported rows / forced-or-control all-four source-supported rows: `0` / `0`
- Selector candidates before R3 / final selectors: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/current_scan_light_table_blend_mode_gate_sheet.jpg`
- Fingerprint: `scenarios=4|modes=5|alphas=3|blendRows=60|controls=24|naturalAll4Outlier=3|controlAll4Outlier=0|naturalAll4Source=0|controlAll4Source=0|bestNatural=4/4:3/4src:average@0.70:29.55|bestControl=3/4:3/4src:nonphysical_79_to_76_forced_active:average@0.35:-10.50|preR3=0|sourceR3=0|triggers=0/9|selectors=0`

## Top Blend Rows

| scenario | mode | alpha | outliers | source-supported | min active-control p95 gain | source ink min | active mean delta | control p95 mean | balance |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `valid_75_to_76_natural` | `average` | 0.70 | 4/4 | 3/4 | 29.55 | 0.0000 | 103.97 | 46.85 | 0.74 |
| `valid_75_to_76_natural` | `average` | 0.50 | 4/4 | 3/4 | 21.18 | 0.0000 | 74.32 | 33.46 | 0.74 |
| `valid_75_to_76_natural` | `average` | 0.35 | 4/4 | 3/4 | 14.48 | 0.0000 | 51.79 | 23.45 | 0.74 |
| `nonphysical_79_to_76_forced_active` | `average` | 0.35 | 3/4 | 3/4 | -10.50 | 0.1260 | 44.73 | 23.42 | 0.38 |
| `nonphysical_79_to_76_forced_active` | `average` | 0.50 | 3/4 | 3/4 | -14.77 | 0.1260 | 64.09 | 33.39 | 0.38 |
| `nonphysical_79_to_76_forced_active` | `average` | 0.70 | 3/4 | 3/4 | -20.73 | 0.1260 | 89.68 | 46.76 | 0.38 |
| `valid_75_to_76_forced_active` | `average` | 0.35 | 3/4 | 3/4 | -20.91 | 0.0554 | 43.70 | 23.76 | 0.22 |
| `valid_75_to_76_forced_active` | `average` | 0.50 | 3/4 | 3/4 | -29.61 | 0.0554 | 62.67 | 33.83 | 0.22 |
| `valid_75_to_76_forced_active` | `average` | 0.70 | 3/4 | 3/4 | -41.51 | 0.0554 | 87.67 | 47.38 | 0.22 |
| `nonphysical_78_to_76_forced_active` | `average` | 0.35 | 3/4 | 1/4 | -11.91 | 0.0000 | 51.25 | 33.53 | 0.67 |
| `nonphysical_78_to_76_forced_active` | `average` | 0.50 | 3/4 | 1/4 | -16.81 | 0.0000 | 73.44 | 47.78 | 0.67 |
| `nonphysical_78_to_76_forced_active` | `average` | 0.70 | 3/4 | 1/4 | -23.58 | 0.0000 | 102.76 | 66.92 | 0.67 |
| `nonphysical_79_to_76_forced_active` | `source_ink` | 0.35 | 0/4 | 0/4 | -9.39 | 0.1260 | 9.65 | 16.28 | 0.18 |
| `nonphysical_79_to_76_forced_active` | `multiply` | 0.35 | 0/4 | 0/4 | -13.12 | 0.1260 | 8.19 | 16.06 | 0.21 |
| `nonphysical_79_to_76_forced_active` | `source_ink` | 0.50 | 0/4 | 0/4 | -13.48 | 0.1260 | 13.54 | 23.05 | 0.17 |
| `nonphysical_79_to_76_forced_active` | `multiply` | 0.50 | 0/4 | 0/4 | -18.72 | 0.1260 | 11.54 | 22.75 | 0.21 |
| `nonphysical_79_to_76_forced_active` | `darken` | 0.35 | 0/4 | 0/4 | -18.77 | 0.1260 | 6.16 | 15.81 | 0.25 |
| `nonphysical_79_to_76_forced_active` | `source_ink` | 0.70 | 0/4 | 0/4 | -18.85 | 0.1260 | 19.00 | 32.30 | 0.17 |
| `valid_75_to_76_forced_active` | `multiply` | 0.35 | 0/4 | 0/4 | -22.22 | 0.0554 | 5.61 | 18.28 | 0.10 |
| `valid_75_to_76_forced_active` | `source_ink` | 0.35 | 0/4 | 0/4 | -22.72 | 0.0554 | 7.20 | 18.75 | 0.07 |
| `valid_75_to_76_natural` | `source_ink` | 0.35 | 0/4 | 0/4 | -22.95 | 0.0000 | 2.88 | 14.62 | 0.01 |
| `valid_75_to_76_natural` | `multiply` | 0.35 | 0/4 | 0/4 | -23.43 | 0.0000 | 2.47 | 14.53 | 0.01 |
| `valid_75_to_76_natural` | `darken` | 0.35 | 0/4 | 0/4 | -23.98 | 0.0000 | 2.03 | 14.42 | 0.01 |
| `valid_75_to_76_forced_active` | `darken` | 0.35 | 0/4 | 0/4 | -24.84 | 0.0554 | 3.28 | 17.77 | 0.23 |
| `nonphysical_79_to_76_forced_active` | `multiply` | 0.70 | 0/4 | 0/4 | -26.33 | 0.1260 | 16.08 | 31.84 | 0.21 |
| `nonphysical_79_to_76_forced_active` | `darken` | 0.50 | 0/4 | 0/4 | -26.77 | 0.1260 | 8.63 | 22.39 | 0.25 |
| `valid_75_to_76_forced_active` | `multiply` | 0.50 | 0/4 | 0/4 | -31.56 | 0.0554 | 7.87 | 25.90 | 0.10 |
| `nonphysical_78_to_76_forced_active` | `darken` | 0.35 | 0/4 | 0/4 | -31.86 | 0.0000 | 6.86 | 26.67 | 0.00 |
| `valid_75_to_76_forced_active` | `source_ink` | 0.50 | 0/4 | 0/4 | -32.22 | 0.0554 | 10.08 | 26.52 | 0.07 |
| `nonphysical_78_to_76_forced_active` | `multiply` | 0.35 | 0/4 | 0/4 | -32.69 | 0.0000 | 7.61 | 26.96 | 0.00 |

## Decision

- `current_scan_light_table_blend_mode_no_selector`
- Alternate blend modes can create natural 75->76 all-four active outliers in average mode, but those rows are not source-ink-supported across O4/B4/G5/O5.
- The strongest apparent effect is a target-highlight washout under arbitrary average blend/alpha, not a readable back-page ink landing pattern.
- This reinforces the earlier held-to-light active-box balance and opacity closures; current scan/PDF material remains useful for visual validation, not extraction.

## Next Move

- Stop varying current-scan light-table blend modes unless a new source/clue supplies a specific blend, opacity, transform, unit, and order.
- Continue with original-layout/physical source acquisition or raw clue wording scored against the source-acquisition packet and R1-R5 reopen requirements.
