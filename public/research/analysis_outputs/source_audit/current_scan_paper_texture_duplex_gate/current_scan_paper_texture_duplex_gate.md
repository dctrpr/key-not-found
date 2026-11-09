# Current Scan Paper Texture Duplex Gate

Scope: paper/background-only duplex registration check for current upright page rasters. Foreground text and highlight ink are masked out, then high-pass paper texture is compared across fixed transforms. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T16:26:03`
- Physical leaf pairs / control pairs: `3` / `6`
- Transform rows: `36`
- Physical mirror best pair rows: `1/3`
- Physical mirror above control p95 rows: `0/3`
- Physical mirror max correlation: `0.308967`
- Control max / p95 correlation: `0.349464` / `0.322037`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `pairs=9|rows=36|physMirrorBest=1/3|physAboveControlP95=0/3|physMax=0.3090|controlMax=0.3495|controlP95=0.3220|sourceR3=0|triggers=0/9|selectors=0`

## Physical Leaf Rows

| pair | transform | rank | corr | pair best | bg IoU |
|---|---|---:|---:|---|---:|
| `75/76` | `identity` | `1` | `0.219175` | `identity` | `0.830024` |
| `75/76` | `hmirror` | `2` | `0.164008` | `identity` | `0.828135` |
| `75/76` | `vmirror` | `3` | `0.135427` | `identity` | `0.822789` |
| `75/76` | `rot180` | `4` | `0.134133` | `identity` | `0.822109` |
| `77/78` | `identity` | `2` | `0.246531` | `hmirror` | `0.039754` |
| `77/78` | `hmirror` | `1` | `0.308967` | `hmirror` | `0.03767` |
| `77/78` | `vmirror` | `4` | `0.117699` | `hmirror` | `0.038463` |
| `77/78` | `rot180` | `3` | `0.147608` | `hmirror` | `0.038794` |
| `79/80` | `identity` | `2` | `0.244323` | `rot180` | `0.067512` |
| `79/80` | `hmirror` | `3` | `0.242338` | `rot180` | `0.069061` |
| `79/80` | `vmirror` | `4` | `0.175946` | `rot180` | `0.067829` |
| `79/80` | `rot180` | `1` | `0.258874` | `rot180` | `0.069167` |

## Decision

- `paper_texture_duplex_not_a_selector`.
- Reason: Masked paper/background texture does not make the physical back-side mirror the best registration for all physical leaf pairs, does not beat controls consistently, and still has no source-backed R3 trigger.
- Next move: Keep paper/fiber duplex registration closed for the current scan. Reopen only with a new physical/original-layout source that changes duplex registration, or raw clue wording that names paper texture, side, mirror, unit, and read order.

Sheet: `analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/current_scan_paper_texture_duplex_gate_sheet.jpg`
