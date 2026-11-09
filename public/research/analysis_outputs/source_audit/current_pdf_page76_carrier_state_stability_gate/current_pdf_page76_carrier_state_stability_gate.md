# Current PDF Page-76 Carrier State Stability Gate

Scope: compared byte-locked `magazine.pdf` embedded/render carriers against duplicate/lower-resolution PDF carriers over page-76 active target boxes, OVERDOSE slot boxes, and matched line-shift controls. This checks source/render provenance only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:54:20+02:00`
- Carriers total / magazine / duplicate: `6` / `2` / `4`
- Regions active / OVERDOSE slots / controls: `4` / `8` / `16`
- Active duplicate presence-mismatch rows: `10`
- OVERDOSE slot duplicate presence-mismatch rows: `32`
- Active / slot outliers above line-shift control p95: `0` / `0`
- All-four active outlier: `0`
- Control p95 max-layer delta: `0.999855`
- Max active / slot duplicate layer delta: `0.989695` / `0.984838`
- Hidden page-76 duplicate carrier candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_page76_carrier_state_stability_gate/current_pdf_page76_carrier_state_stability_gate_sheet.jpg`
- Fingerprint: `carriers=6|active=4|slots=8|controls=16|activeMismatchRows=10|slotMismatchRows=32|activeOutliers=0|slotOutliers=0|controlP95=0.999855|all4ActiveOutlier=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Active Targets

| id | expected | magazine state | duplicate state | max layer delta | duplicate mismatch rows | outlier |
|---|---|---|---|---:|---:|---:|
| `O4` | `Y` | `orange` | `grey` | `0.989695` | `4` | `0` |
| `B4` | `K` | `black` | `black` | `0.686434` | `0` | `0` |
| `G5` | `K` | `black` | `grey` | `0.721218` | `2` | `0` |
| `O5` | `Y` | `orange` | `grey` | `0.933413` | `4` | `0` |

## OVERDOSE Slots

| id | letter | magazine state | duplicate state | max layer delta | duplicate mismatch rows | outlier |
|---|---|---|---|---:|---:|---:|
| `slot0_O` | `O` | `black` | `grey` | `0.891188` | `4` | `0` |
| `slot1_V` | `V` | `black` | `grey` | `0.828619` | `4` | `0` |
| `slot2_E` | `E` | `black` | `grey` | `0.858223` | `4` | `0` |
| `slot3_R` | `R` | `black` | `orange` | `0.795568` | `4` | `0` |
| `slot4_D` | `D` | `orange` | `orange` | `0.855325` | `4` | `0` |
| `slot5_O` | `O` | `orange` | `grey` | `0.940977` | `4` | `0` |
| `slot6_S` | `S` | `blank` | `grey` | `0.984838` | `4` | `0` |
| `slot7_E` | `E` | `blank` | `grey` | `0.982189` | `4` | `0` |

## Decision

- `page76_duplicate_carrier_state_stability_no_selector`
- Duplicate/lower-resolution carriers introduce some state/raster deltas, but they do not create an all-four active target outlier relative to matched line-shift controls.
- OVERDOSE slot deltas also remain source-provenance evidence only; no source-backed unit/order cue is present.
- This keeps duplicate/current-PDF carrier differences closed as selectors.

## Next Move

- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
