# Current Scan Paper Texture Shift Gate

Scope: paper/background-only duplex registration check for current upright page rasters. Foreground text and highlight ink are masked out, then the physical horizontal mirror is allowed a small global shift. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T16:33:43`
- Physical leaf pairs / control pairs: `3` / `6`
- Shift grid: `-32..32` px in 8 px steps (`81` shifts per pair)
- Shift rows: `729`
- Physical best above control-best p95 rows: `1/3`
- Physical best at <= 16px rows: `1/3`
- Physical zero-shift above control-best p95 rows: `0/3`
- Physical best max correlation: `0.426065`
- Control best max / p95 correlation: `0.369263` / `0.355692`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `pairs=9|shifts=81|rows=729|physAboveControlP95=1/3|physSmallShiftBest=1/3|zeroShiftAboveControlP95=0/3|physBestMax=0.4261|controlBestMax=0.3693|controlBestP95=0.3557|sourceR3=0|triggers=0/9|selectors=0`

## Physical Best Rows

| pair | dx | dy | shift | corr | bg IoU |
|---|---:|---:|---:|---:|---:|
| `75/76` | `-32` | `-24` | `32` | `0.212228` | `0.740099` |
| `77/78` | `0` | `-8` | `8` | `0.311048` | `0.039737` |
| `79/80` | `32` | `-32` | `32` | `0.426065` | `0.073403` |

## Physical Zero-Shift Rows

| pair | corr | rank | pair best dx | pair best dy |
|---|---:|---:|---:|---:|
| `75/76` | `0.164008` | `10` | `-32` | `-24` |
| `77/78` | `0.308967` | `2` | `0` | `-8` |
| `79/80` | `0.242338` | `40` | `32` | `-32` |

## Decision

- `paper_texture_shift_not_a_selector`.
- Reason: Allowing small global shifts after the physical mirror does not produce a source-backed, all-physical leaf registration rule that separates from shifted controls.
- Next move: Keep paper/fiber duplex registration closed for the current scan, including small global shift rescue. Reopen only with a new physical/original-layout source or raw clue wording that names side, mirror, paper texture, shift/registration, unit, and read order.

Sheet: `analysis_outputs/source_audit/current_scan_paper_texture_shift_gate/current_scan_paper_texture_shift_gate_sheet.jpg`
