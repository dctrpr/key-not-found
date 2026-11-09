# Source Packet OVERDOSE Transform Control

- Created: `2026-05-21T07:51:50`
- Scope: bounded OVERDOSE header glyph transform/control audit; no OCR extraction, hashes, WIF, seed phrase, address, or key checks.

## Findings

- Measured header glyph sequence: `OVERDOSE`.
- Actual glyph projection differs from equal C9 slots by at most `0.087628` px.
- Active center streams remain `OVED` line-order and `VEDO` x-order.
- The active black span gives `OVER`, but p75 control also gives `OVER`.
- Mirrored/reversed variants tested: `8`; p75 matched active black in `8` variants.
- Tolerance combinations: active black OVER `45/99`; p75 control OVER `49/99`; both `37/99`.
- Source-review extraction-ready paths / R3 failures: `0` / `7`.
- Fingerprint: `glyphDelta=0.087628|center=OVED/VEDO|black=OVER|p75=OVER|mirrors=8/8|tol=45/49|ready=0|sourceR3=0|selectors=0`.

## Decision

- Do not promote OVERDOSE transform/slot geometry as a selector.
- Keep it as a future source-validation guardrail only.
- Reopen only if a distinct source or clue names OVERDOSE/header slots and a unit/order rule that p75 and mirror/tolerance controls fail.
