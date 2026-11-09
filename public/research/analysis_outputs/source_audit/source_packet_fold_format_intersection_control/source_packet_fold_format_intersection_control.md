# Source Packet Fold/Format Intersection Control

- Created: `2026-05-21T08:00:36`
- Scope: folded 3D geometry plus bold/highlight intersection control; no extraction or candidate generation.

## Findings

- Folded/reflected carriers touching all four active targets: `3`; single global all-four shifts: `0`.
- Shifted carrier slices: `12` active slices, `78` total words, `69` non-target words, `0` target-isolated slices.
- Fold/highlight axes tested: `141`; all-four active axes: `0`; non-tautological two-active axes: `0`.
- Format authority passes: `4/4`; witness conflicts: `2`.
- Intersection gates pass/partial/fail: `2` / `0` / `6`.
- Source-backed R3 hits / satisfied reopen triggers / selector unlocks: `0` / `0` / `0`.
- Fingerprint: `gates=8|pass=2|partial=0|singleShiftAll4=0|carrierNonTarget=69|isolated=0|axesAll4=0|formatPass=4|formatConflicts=2|sourceR3=0|selectors=0`.

## Decision

- Do not promote folded 3D geometry plus bold/highlight state as a selector.
- Keep the combination as source-validation context only.
- Reopen only if a distinct source names the fold/reflection/format operation and provides a unit/order rule that passes R1-R5.
