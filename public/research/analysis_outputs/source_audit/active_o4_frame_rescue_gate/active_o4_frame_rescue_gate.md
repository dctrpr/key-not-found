# Active O4 Frame Rescue Gate

Scope: test whether the combined p78 same-layout/current-mirror frame envelope recovers the missing O4 target by a clean line-pitch extension. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.

- Created: `2026-05-21T01:33:44`
- Line-pitch benchmark: `73.73 px`
- Same-layout frame: `[294.0, 2398.0, 1310.0, 2950.0]`
- Current-mirror frame: `[1234.0, 2398.0, 2250.0, 2950.0]`
- Dual-frame envelope: `[294.0, 2398.0, 2250.0, 2950.0]`
- Sheet: `analysis_outputs/source_audit/active_o4_frame_rescue_gate/active_o4_frame_rescue_gate_sheet.jpg`

## Expansion Metrics

| frame | full expansion needed | touch expansion needed |
|---|---|---|
| same-layout | `{'left': 0.0, 'top': 221.0, 'right': 491.0, 'bottom': 32.0}` | `{'left': 0.0, 'top': 173.0, 'right': 24.0, 'bottom': 0.0}` |
| current mirror | `{'left': 806.0, 'top': 221.0, 'right': 0.0, 'bottom': 32.0}` | `{'left': 543.0, 'top': 173.0, 'right': 0.0, 'bottom': 0.0}` |
| dual envelope | `{'left': 0.0, 'top': 221.0, 'right': 0.0, 'bottom': 32.0}` | `{'left': 0.0, 'top': 173.0, 'right': 0.0, 'bottom': 0.0}` |

## Frame Checks

| frame | partial hits | full hits | hit ids | full-hit ids |
|---|---:|---:|---|---|
| `sameLayout` | `3` | `2` | `one_billion, volcano_bonds, shitcoiner_heart` | `one_billion, volcano_bonds` |
| `currentMirror` | `1` | `0` | `shitcoiner_heart` | `-` |
| `dualEnvelope` | `3` | `2` | `one_billion, volcano_bonds, shitcoiner_heart` | `one_billion, volcano_bonds` |
| `dualEnvelopeTopMinus3LinePitch` | `4` | `3` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` | `buying_dip, one_billion, volcano_bonds` |
| `dualEnvelopeFullRescue` | `4` | `4` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` | `buying_dip, one_billion, volcano_bonds, shitcoiner_heart` |

## Decision

- The dual-frame envelope already covers B4/G5 and clips O5, but misses O4 vertically.
- Full O4 recovery from the dual envelope requires a top extension of `221.0px`, which is `2.9974` line pitches.
- Extending the dual envelope upward by exactly three line pitches recovers O4/B4/G5 and still clips O5.
- This is a clean source-comparison benchmark, not extraction permission: it uses the union of two frames plus an extra vertical extension, and no source wording currently names that operation.
- Reopen only if source/original-layout wording names reading above the frame, extending the frame, or a three-line offset.
