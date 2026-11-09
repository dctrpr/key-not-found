# Current Scan Lane Affine Registration Gate

Scope: tested whether two-anchor article-lane affine registration (translation plus x/y scale) improves mirrored page-75 held-to-light support for O4/B4/G5/O5 on page 76. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T19:34:34`
- Valid source page / target page: `75` -> `76`
- Invalid source controls: `[77, 78, 79, 80]`
- Valid affine rows / control rows: `3` / `13`
- Best valid mode: `top_header_lane+lower_body_lane_affine`
- Best valid transform: `{'sx': 1.013988, 'sy': 1.150444, 'tx': -280.62, 'ty': -39.654}`
- Best valid supported / above-control-p95 count: `3/4` / `0/4`
- Max control supported / above-control-p95 count: `4/4` / `4/4`
- All-four valid affine modes: `[]`
- Affine registration candidate / selectors: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_lane_affine_registration_gate/current_scan_lane_affine_registration_gate_sheet.jpg`
- Fingerprint: `valid=3|controls=13|modes=4|best=top_header_lane+lower_body_lane_affine|bestSupport=3/4|bestAboveP95=0/4|bestMean=0.201997|controlMax=4|controlAboveMax=4|allFour=0|sourceR3=0|triggers=0/9|selectors=0`

## Valid Page-75 -> Page-76 Rows

| mode | sx | sy | tx | ty | mean fraction | O4 | B4 | G5 | O5 | supported | above p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `natural_hflip` | `1.0` | `1.0` | `0.0` | `0.0` | `0.064704` | `0.094531` | `0.0` | `0.036783` | `0.127504` | `1/4` | `0/4` |
| `top_header_lane+footer_lane_affine` | `1.0178` | `1.01339` | `-287.234` | `15.371` | `0.073856` | `0.115453` | `0.0` | `0.118973` | `0.060998` | `2/4` | `0/4` |
| `top_header_lane+lower_body_lane_affine` | `1.013988` | `1.150444` | `-280.62` | `-39.654` | `0.201997` | `0.524714` | `0.107111` | `0.063539` | `0.112625` | `3/4` | `0/4` |

## Control P95 By Mode

| mode | O4 p95 | B4 p95 | G5 p95 | O5 p95 |
|---|---:|---:|---:|---:|
| `lower_body_lane+footer_lane_affine` | `0.0` | `0.0` | `0.021976` | `0.482641` |
| `natural_hflip` | `0.839225` | `0.837016` | `0.854689` | `0.766968` |
| `top_header_lane+footer_lane_affine` | `0.888762` | `1.017078` | `1.049335` | `1.050119` |
| `top_header_lane+lower_body_lane_affine` | `0.636862` | `0.915933` | `0.805913` | `0.895744` |

## Decision

- `current_scan_lane_affine_registration_no_selector`
- Two-anchor article-lane affine transforms do not make valid mirrored page-75 source ink support all four active page-76 targets above invalid source-page controls.
- Best valid affine mode is `top_header_lane+lower_body_lane_affine`, but it supports only `3/4` active boxes and beats invalid controls on only `0/4` boxes.
- Two-anchor lane scaling therefore does not rescue B4/G5/O5 as a selective physical held-to-light landing.

## Next Move

- Keep current-scan held-to-light registration closed; require a distinct physical/original-layout source or raw clue wording that supplies unit, order, and transform.
