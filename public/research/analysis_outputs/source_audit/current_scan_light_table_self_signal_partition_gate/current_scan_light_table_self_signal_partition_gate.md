# Current Scan Light-Table Self-Signal Partition Gate

Scope: valid page `75 -> 76` held-to-light average blend only. The mirrored page-75 source layer is separated from page-76 target-only ink, with line-shift controls and projected OVERDOSE slots included. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T16:44:41`
- Active / line-shift controls / OVERDOSE slots: `4` / `24` / `8`
- Active target-only dominant rows: `4/4`
- Active source-supported dominant rows: `0/4`
- Active source-supported mean above control p95 rows: `0/4`
- Active source-supported share above control p95 rows: `0/4`
- Active min target-only delta share: `0.847292`
- Active max source-supported delta share: `0.151722`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `active=4|controls=24|slots=8|alpha=0.70|activeTargetOnlyDominant=4/4|activeSourceDominant=0/4|activeSrcMeanAboveCtlP95=0/4|activeSrcShareAboveCtlP95=0/4|activeMinTargetOnly=0.8473|activeMaxSourceShare=0.1517|slotSrcMeanP95=28.9530|sourceR3=0|triggers=0/9|selectors=0`

## Active Rows

| id | target-only share | source-supported share | source-supported mean | avg delta | source ink |
|---|---:|---:|---:|---:|---:|
| `O4` | `0.886249` | `0.113351` | `9.880286` | `87.165311` | `0.140212` |
| `B4` | `0.995653` | `0.0` | `0.0` | `115.837158` | `0.0` |
| `G5` | `0.963745` | `0.032698` | `3.889743` | `118.958742` | `0.059643` |
| `O5` | `0.847292` | `0.151722` | `12.367515` | `81.514471` | `0.194042` |

## OVERDOSE Slot Controls

| slot | target-only share | source-supported share | source-supported mean | avg delta |
|---|---:|---:|---:|---:|
| `O0` | `0.9814` | `5.7e-05` | `0.000598` | `10.564467` |
| `V1` | `0.957363` | `0.020364` | `0.421062` | `20.676277` |
| `E2` | `0.650683` | `0.32972` | `10.396027` | `31.52985` |
| `R3` | `0.566246` | `0.417748` | `15.39431` | `36.8507` |
| `D4` | `0.507683` | `0.475111` | `17.401921` | `36.627086` |
| `O5` | `0.318052` | `0.666921` | `23.789232` | `35.670213` |
| `S6` | `0.035701` | `0.948586` | `31.733541` | `33.453523` |
| `E7` | `0.188936` | `0.791745` | `10.446344` | `13.194073` |

## Decision

- `light_table_visual_pop_is_target_self_signal`.
- Reason: The valid 75->76 average blend is dominated by page-76 target-only ink across all active boxes; no active row is source-supported-dominant, and source-backed R3 remains absent.
- Next move: Stop treating the attractive valid light-table blend as source evidence. Continue only with a new physical/original-layout source or raw clue wording that supplies a real source layer, unit, and order.

Sheet: `analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate/current_scan_light_table_self_signal_partition_gate_sheet.jpg`
