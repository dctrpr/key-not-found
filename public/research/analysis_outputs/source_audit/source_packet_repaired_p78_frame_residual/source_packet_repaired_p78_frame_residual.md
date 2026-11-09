# Source Packet Repaired P78 Frame Residual

Scope: measure current and dx-repaired reflected p78 frame variants against the active O4/B4/G5/O5 source-packet boxes. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T06:29:10`
- Active order: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`
- Active visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- Common source-packet all-direction shift tolerance: `4px`
- Max full-inside active count across frames: `0/4`
- Max partial-hit active count across frames: `2/4`
- Best G5 horizontal gap: `g5_edge_touch_dx_-38` at `0.0px`
- Best O5 overlap: `nearest_grid_dx_-40` at `0.270725` of target area
- Minimum repaired-frame B4 left expansion to touch/full-cover: `503px` / `766px`
- Minimum repaired-frame O4 top expansion to touch/full-cover: `173px` / `221px`
- Frame residual fingerprint: `frames=current,-38,-40|maxFull=0|maxPartial=2|bestG5Gap=g5_edge_touch_dx_-38:0.0|bestO5Overlap=nearest_grid_dx_-40:0.270725|minRepairedB4TouchLeft=503|minRepairedB4FullLeft=766|minRepairedO4TouchTop=173|minRepairedO4FullTop=221`
- Sheet: `analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/source_packet_repaired_p78_frame_residual_sheet.jpg`

## Frame Residuals

| frame | dx | full inside | partial hits | strong partial hits | G5 gap | G5 overlap | O5 overlap | B4 left touch/full | O4 top touch/full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `current` | `0.0` | `0/4` | `1/4` | `1/4` | `38` | `0.0` | `0.247536` | `543/806` | `173/221` |
| `g5_edge_touch_dx_-38` | `-38.0` | `0/4` | `1/4` | `1/4` | `0.0` | `0.0` | `0.269565` | `505/768` | `173/221` |
| `nearest_grid_dx_-40` | `-40.0` | `0/4` | `2/4` | `1/4` | `0.0` | `0.004988` | `0.270725` | `503/766` | `173/221` |

## Decision

- Keep this as source-registration evidence only.
- The repaired dx variants improve the G5 edge/near-edge benchmark and slightly improve O5 clipping, but they still do not fully contain the active quartet.
- B4 remains far outside the repaired p78 frame and O4 still requires a large top expansion, so this does not reopen folded/mirrored p78 geometry as a selector.
- The result is useful for future physical/original-layout comparison; extraction remains blocked until source-backed unit/order wording appears.

## Next Move

- Use repaired-frame residuals only as future physical/original-layout comparison metrics. Do not reopen p78 frame, fold/mirror, OVERDOSE, or highlight extraction without source-backed R3 unit/order wording.
