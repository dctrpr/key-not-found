# Current Scan Paper Texture Microshift Gate

Scope: masked paper/background texture only. The second page is horizontally mirrored, then searched over a bounded +/-32 px global shift grid. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T18:12:56`
- Physical leaf pairs / control pairs: `3` / `6`
- Shift rows per pair / total shift rows: `81` / `729`
- Physical best above control p95 rows: `1/3`
- Physical best improved over zero by >0.02 rows: `2/3`
- Physical best within +/-16 px rows: `1/3`
- Max physical/control best correlation: `0.426065` / `0.369263`
- Control best-correlation p95: `0.355692`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `pairs=9|shifts=81|physAboveP95=1/3|physImproved=2/3|smallShift=1/3|physMax=0.4261|controlMax=0.3693|controlP95=0.3557|sourceR3=0|triggers=0/9|selectors=0`

## Pair Rows

| pair | class | zero corr | best corr | best dx | best dy | gain |
|---|---|---:|---:|---:|---:|---:|
| `75/76` | `physical_leaf` | `0.164008` | `0.212228` | `-32` | `-24` | `0.04822` |
| `77/78` | `physical_leaf` | `0.308967` | `0.311048` | `0` | `-8` | `0.002081` |
| `79/80` | `physical_leaf` | `0.242338` | `0.426065` | `32` | `-32` | `0.183727` |
| `75/78` | `control_pair` | `0.162463` | `0.230026` | `-24` | `-8` | `0.067563` |
| `75/80` | `control_pair` | `0.194627` | `0.369263` | `32` | `32` | `0.174636` |
| `76/77` | `control_pair` | `0.183036` | `0.264738` | `0` | `-8` | `0.081702` |
| `76/79` | `control_pair` | `0.267884` | `0.301407` | `0` | `16` | `0.033523` |
| `77/80` | `control_pair` | `None` | `None` | `None` | `None` | `None` |
| `78/79` | `control_pair` | `0.176241` | `0.198468` | `-8` | `8` | `0.022227` |

## Decision

- `paper_texture_microshift_not_a_selector`.
- Reason: Bounded global shifts after physical mirror do not separate physical leaf pairs from controls, do not keep physical best shifts in a consistent small registration window, and still have no source-backed R3 trigger.
- Next move: Keep paper-texture microshift rescue closed for the current scan. Reopen only with a distinct physical/original-layout source or raw clue wording that names side, mirror, paper texture, shift/registration, unit, and read order.

Sheet: `analysis_outputs/source_audit/current_scan_paper_texture_microshift_gate/current_scan_paper_texture_microshift_gate_sheet.jpg`
