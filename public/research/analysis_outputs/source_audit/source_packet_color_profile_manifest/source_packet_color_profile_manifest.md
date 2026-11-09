# Source Packet Color Profile Manifest

Scope: record active O4/B4/G5/O5 orange/black color profiles and OVERDOSE header/glyph controls for future source comparison. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T06:19:15`
- Active order: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`
- Active visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- Active Y orange-ratio range: `[0.7124, 0.7666]`
- Active K dark-ratio range: `[0.6592, 0.6994]`
- Active K orange-ratio range: `[0.0, 0.0]`
- OVERDOSE control classified-state stream: `NNNNNNNNN`
- OVERDOSE control max orange ratio: `0.277`
- OVERDOSE control max dark ratio: `0.0`
- Y/control orange separation margin: `0.4354`
- K/control dark separation margin: `0.6592`
- Max native rotate180 mean abs diff: `2.9794`
- Color-profile fingerprint: `states=YKKY|Yorange=0.7124-0.7666|Kdark=0.6592-0.6994|KorangeMax=0.0|ctrlOrangeMax=0.277|ctrlDarkMax=0.0|roundtripMeanMax=2.9794`
- Sheet: `analysis_outputs/source_audit/source_packet_color_profile_manifest/source_packet_color_profile_manifest_sheet.jpg`

## Active Profiles

| id | expected | classified | mean RGB | median RGB | orange | dark | native mean diff |
|---|---|---|---:|---:|---:|---:|---:|
| `buying_dip` | `Y` | `Y` | `[197.819, 114.868, 42.791]` | `[241.0, 135.0, 37.0]` | `0.7666` | `0.2411` | `2.8964` |
| `one_billion` | `K` | `K` | `[88.885, 88.888, 88.906]` | `[20.0, 20.0, 20.0]` | `0.0` | `0.6592` | `1.0606` |
| `volcano_bonds` | `K` | `K` | `[77.38, 77.353, 77.395]` | `[18.0, 18.0, 18.0]` | `0.0` | `0.6994` | `1.1095` |
| `shitcoiner_heart` | `Y` | `Y` | `[187.161, 112.461, 44.95]` | `[239.0, 136.0, 34.0]` | `0.7124` | `0.284` | `2.9794` |

## Decision

- Keep this as a source-validation color manifest only.
- Active orange/black profiles remain visually separated from OVERDOSE controls under the current classification rules.
- This does not reopen highlight-color, bold-letter, C9, OVERDOSE, or fold/mirror selectors.
- Use it only to judge future source/original-layout visual matches; extraction remains blocked until R3 unit/order evidence appears.
