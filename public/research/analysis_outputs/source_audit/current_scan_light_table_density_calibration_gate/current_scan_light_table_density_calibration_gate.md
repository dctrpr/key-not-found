# Current Scan Light-Table Density Calibration Gate

Scope: normalized the natural valid leaf held-to-light overlays against full-page, active-band, C9-frame, and matched line-control source density. This checks whether page 76 becomes special after compensating for different source-page ink density. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T12:21:46`
- Valid leaf pairs: `3`
- Active / line-shift control / OVERDOSE slot rows: `12` / `72` / `24`
- Page-76 normalized active ink / feature outliers: `0` / `0`
- All-four page-76 normalized active ink / feature outlier: `0` / `0`
- Page-76 normalized OVERDOSE slot ink outliers: `3`
- Hidden density-calibrated candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/current_scan_light_table_density_calibration_gate_sheet.jpg`
- Fingerprint: `pairs=3|active=12|controls=72|slots=24|p76NormInkOutliers=0|p76NormFeatureOutliers=0|all4NormInk=0|all4NormFeature=0|slotNormInkOutliers=3|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Pair Density Baselines

| pair | source->target | page ink | active-band ink | C9-frame ink | active ink mean | active/page | active/band | active/C9 | control p95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `valid_75_to_76` | `75->76` | 0.094023 | 0.098186 | 0.119083 | 0.098474 | 1.047346 | 1.002931 | 0.826941 | 0.398262 |
| `valid_77_to_78` | `77->78` | 0.961339 | 0.955510 | 0.968225 | 0.976723 | 1.016003 | 1.022201 | 1.008777 | 1.000000 |
| `valid_79_to_80` | `79->80` | 0.091807 | 0.080578 | 0.080737 | 0.077715 | 0.846500 | 0.964465 | 0.962574 | 0.841564 |

## Page-76 Normalized Active Comparison

| target | p76 ink/page | other-leaf ink/page max | control ink/page p95 | ink outlier | p76 feature/page | other-leaf feature/page max | control feature/page p95 | feature outlier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `O4` | 1.491261 | 1.022303 | 10.198322 | 0 | 1.423706 | 1.018509 | 10.954512 | 0 |
| `B4` | 0.000000 | 1.013455 | 1.022826 | 0 | 0.000000 | 0.986990 | 1.014397 | 0 |
| `G5` | 0.634342 | 1.013464 | 2.015585 | 0 | 0.612541 | 0.984301 | 2.024256 | 0 |
| `O5` | 2.063778 | 2.406142 | 3.050967 | 0 | 1.925194 | 2.510505 | 3.066999 | 0 |

## Decision

- `current_scan_light_table_density_calibration_no_selector`
- Density normalization does not promote page 76 into an all-four active or OVERDOSE selector.
- The high same-coordinate values on page 78 are source-density behavior, not a hidden page-76 rule.

## Next Move

- Treat current-scan light-table outputs as calibrated source-review witnesses only.
- Continue only with physical/original-layout source validation or raw clue wording that names unit/order/transform.
