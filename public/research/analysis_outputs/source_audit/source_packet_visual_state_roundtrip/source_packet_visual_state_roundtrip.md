# Source Packet Visual-State Roundtrip

Scope: measure per-box visual-state and native-rotation stability for the current source packet. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T05:46:09`
- Active expected visual-state order: `YKKY`
- Active classified visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- All active states match: `True`
- All active DOCM bold fraction one: `True`
- Active max mean abs diff after native rotate180: `2.9794`
- Active max pixel diff after native rotate180: `25`
- Active Y orange-ratio range: `[0.7124, 0.7666]`
- Active K dark-ratio range: `[0.6592, 0.6994]`
- OVERDOSE glyph sequence: `OVERDOSE`
- OVERDOSE glyph max dark ratio: `0.0`
- OVERDOSE glyph max orange ratio: `0.277`
- Sheet: `analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip_sheet.jpg`

## Active Records

| id | state | page/corridor | orange ratio | dark ratio | DOCM bold | mean abs diff |
|---|---|---:|---:|---:|---:|---:|
| `buying_dip` | `Y -> Y` | `22/4` | `0.7666` | `0.2411` | `1.0` | `2.8964` |
| `one_billion` | `K -> K` | `25/7` | `0.0` | `0.6592` | `1.0` | `1.0606` |
| `volcano_bonds` | `K -> K` | `27/9` | `0.0` | `0.6994` | `1.0` | `1.1095` |
| `shitcoiner_heart` | `Y -> Y` | `32/14` | `0.7124` | `0.284` | `1.0` | `2.9794` |

## Decision

- Keep this as a source-validation benchmark, not a selector.
- The active visual states and DOCM bold status are stable under the native `rotate180` source transform.
- The OVERDOSE header/glyph controls distinguish header art from active black highlight bands, but they supply no extraction unit or order.
