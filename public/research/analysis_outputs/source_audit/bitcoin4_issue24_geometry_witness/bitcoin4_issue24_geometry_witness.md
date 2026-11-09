# bitcoin4 Issue 24 Geometry Witness

Scope: test whether `bitcoin4.pdf`, now identified as a low-res Issue 24 witness, naturally fixes the p78-to-p76 G5/O5 registration gap. No key derivation was run.

- Created: `2026-05-20T07:52:31`
- Overlay: `analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness_overlay.jpg`
- Best scan page size: `[2544, 3264]`
- bitcoin4 page size: `[2040, 2805]`

## Registration Fit

- p76 orange-band affine residual: mean `3.618px`, max `10.079px`.
- p78 orange-band affine residual: mean `4.595px`, max `14.08px`.

## p78 Frame Result In bitcoin4 Geometry

- Reflected frame on bitcoin4 p76: `[1040.837, 1903.729, 1849.818, 2345.457]`
- O5 overlapVsTarget: `0.43908`, gap `0.0x0.0px`.
- G5 overlapVsTarget: `0.0`, gap `84.098x0.0px`.

## Scaled High-Res Baseline

- Simple scaled O5 overlapVsTarget: `0.24754`.
- Simple scaled G5 overlapVsTarget: `0.0`, horizontal gap `30.472px`.

## Decision

- bitcoin4.pdf does not repair the p78 -> p76 G5/O5 registration. In its own low-res geometry, the reflected p78 frame still clips O5, but it sits farther from trusted G5 than the current best scan.

## Next Move

- Keep bitcoin4.pdf as a source-fidelity witness only. Do not use it as geometry truth unless a separate rule explains why G5 should be ignored or re-registered.
