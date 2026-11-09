# P78 Frame Trusted-Target Sensitivity

Scope: test how the reflected p78 frame behaves against trusted G5/O5 after the stale G5 correction. No key derivation was run.

- Created: `2026-05-20T07:17:36`
- Overlay: `analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity_overlay.jpg`
- Frame: `[1234.0, 2398.0, 2250.0, 2950.0]`
- O5: `[1040.0, 2932.0, 1661.0, 2982.0]`
- Trusted G5: `[795.0, 2544.0, 1196.0, 2592.0]`

## Current Position

- O5 overlapVsTarget: `0.24754`; O5 verticalGap: `0.0px`
- G5 overlapVsTarget: `0.0`; G5 horizontalGap: `38.0px`; G5 verticalGap: `0.0px`

## Sensitivity Results

- Grid: dx `[-160, 160]` px, dy `[-80, 80]` px, step `5` px.
- Simultaneous true-overlap positions for O5 and trusted G5: `500`.
- G5 edge/near-edge plus O5 overlap positions: `660`.
- Nearest true simultaneous overlap: dx=`-40`, dy=`0`, O5=`0.27072`, G5=`0.00499`.
- Nearest G5 edge/near-edge plus O5 overlap: dx=`0`, dy=`0`, G5 gap=`38.0px`, O5=`0.24754`.
- Best combined overlap in this bounded grid: dx=`-160`, dy=`35`, O5=`0.94525`, G5=`0.30424`.
- Pure upward shift where O5 is lost: dy=`-20` px.

## Assessment

- The current p78 frame remains a lower-corridor pointer: it clips O5 and runs vertically beside trusted G5.
- Current G5 evidence is edge-adjacent, not an exact overlap: the trusted G5 right edge is 38px left of the p78 frame.
- A small left shift of about 40px is enough for the p78 frame to touch/overlap trusted G5 while preserving the O5 clip.
- The O5 clip is vertically fragile: moving the frame upward by about 20px loses O5, while moving downward strengthens it.
- Therefore p78 frame/O5/G5 should stay active as orientation/source-registration evidence, but not as a precise extraction unit without a better source transform.

## Next Move

- Use this p78-frame robustness profile when evaluating any new source image: a valid source registration should explain the 38px G5 near-miss and the O5 bottom-edge clip without arbitrary local shifting.
