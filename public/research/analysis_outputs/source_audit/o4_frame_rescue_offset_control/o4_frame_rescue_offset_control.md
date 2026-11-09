# O4 Frame Rescue Offset Control

Scope: control-test the three-line O4 frame rescue against nearby line-pitch offsets. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:38:07`
- Line-pitch benchmark: `73.73 px`
- Dual-frame envelope: `[294.0, 2398.0, 2250.0, 2950.0]`
- Top-only offsets checked: `7`
- Top/bottom grid offsets checked: `28`
- Sheet: `analysis_outputs/source_audit/o4_frame_rescue_offset_control/o4_frame_rescue_offset_control_sheet.jpg`

## Top-Only Offset Control

| top line offset | partial hits | full hits | hit ids | full-hit ids |
|---:|---:|---:|---|---|
| `0` | `3` | `2` | `one_billion, volcano_bonds, shitcoiner_heart` | `one_billion, volcano_bonds` |
| `1` | `3` | `2` | `one_billion, volcano_bonds, shitcoiner_heart` | `one_billion, volcano_bonds` |
| `2` | `3` | `2` | `one_billion, volcano_bonds, shitcoiner_heart` | `one_billion, volcano_bonds` |
| `3` | `4` | `3` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` | `buying_dip, one_billion, volcano_bonds` |
| `4` | `4` | `3` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` | `buying_dip, one_billion, volcano_bonds` |
| `5` | `4` | `3` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` | `buying_dip, one_billion, volcano_bonds` |
| `6` | `4` | `3` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` | `buying_dip, one_billion, volcano_bonds` |

## Minimums

- Minimum integer top-only offset that touches all four active targets: `3` line pitches.
- Top-only offsets that touch all four active targets: `[3, 4, 5, 6]`.
- Top-only offsets that fully cover all four active targets: `[]`.
- Minimum top/bottom grid offset that fully covers all four active targets: top `3`, bottom `1`, total `4` line pitches.

## Decision

- The three-line top extension is the minimum integer top-only offset that recovers all four active targets.
- It is not unique once larger top extensions are allowed, so it is not a standalone selector.
- Full coverage of all four targets requires a `3-up / 1-down` line-pitch envelope.
- Keep these as future source/original-layout validation benchmarks only; reopen extraction only if source wording names line-pitch frame extension or above/below frame reading.
