# Current Scan Header/Footer Lane Registration Gate

Scope: tested whether registering mirrored source pages by visible article top-header, footer, or lower-body lanes improves current-scan held-to-light support for O4/B4/G5/O5. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T19:29:27`
- Valid source page / target page: `75` -> `76`
- Invalid source controls: `[77, 78, 79, 80]`
- Valid lane rows / control rows: `5` / `20`
- Best valid mode: `lower_body_lane`
- Best valid supported / above-control-p95 count: `3/4` / `0/4`
- Best valid mean source fraction: `0.263549`
- Max control supported count: `4`
- All-four supported lane modes: `[]`
- Lane registration candidate / selectors: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_header_footer_lane_registration_gate/current_scan_header_footer_lane_registration_gate_sheet.jpg`
- Fingerprint: `valid=5|controls=20|modes=5|best=lower_body_lane|bestSupport=3/4|bestAboveP95=0/4|bestMean=0.263549|controlMax=4|allFour=0|sourceR3=0|triggers=0/9|selectors=0`

## Valid Page-75 -> Page-76 Rows

| mode | dx | dy | mean fraction | O4 | B4 | G5 | O5 | supported | above p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `natural_hflip` | `0.0` | `0.0` | `0.064704` | `0.094531` | `0.0` | `0.036783` | `0.127504` | `1/4` | `0/4` |
| `top_header_lane` | `-256.35` | `20.747` | `0.041358` | `0.026365` | `0.0` | `0.011274` | `0.127794` | `1/4` | `0/4` |
| `footer_lane` | `151.583` | `53.827` | `0.051796` | `0.139231` | `0.0` | `0.0` | `0.067955` | `1/4` | `0/4` |
| `lower_body_lane` | `-188.588` | `288.599` | `0.263549` | `0.645253` | `0.083893` | `0.115389` | `0.209662` | `3/4` | `0/4` |
| `header_footer_mean` | `-52.383` | `37.287` | `0.033461` | `0.09056` | `0.0` | `0.0` | `0.043285` | `0/4` | `0/4` |

## Control P95 By Mode

| mode | O4 p95 | B4 p95 | G5 p95 | O5 p95 |
|---|---:|---:|---:|---:|
| `footer_lane` | `0.759859` | `0.953891` | `0.828476` | `0.906623` |
| `header_footer_mean` | `0.868399` | `0.920091` | `0.917797` | `0.882014` |
| `lower_body_lane` | `0.676232` | `0.828452` | `0.816212` | `0.847306` |
| `natural_hflip` | `0.839225` | `0.837016` | `0.854689` | `0.766968` |
| `top_header_lane` | `0.886731` | `0.867483` | `0.824702` | `0.681981` |

## Decision

- `current_scan_header_footer_lane_registration_no_selector`
- Visible article header/footer/lower-body lane translations do not make mirrored page-75 source ink support all four active page-76 targets above invalid source-page controls.
- Best valid lane mode is `lower_body_lane`, but it supports only `3/4` active boxes and beats invalid controls on only `0/4` boxes.
- Header/footer/body-lane registration therefore does not rescue B4/G5/O5 as a selective physical held-to-light landing.

## Next Move

- Keep current-scan held-to-light registration closed unless a distinct physical/original-layout source or raw clue wording supplies the missing unit, order, and transform.
