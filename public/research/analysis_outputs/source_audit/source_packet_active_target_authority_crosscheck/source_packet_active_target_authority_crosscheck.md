# Source Packet Active Target Authority Crosscheck

- Created: `2026-05-21T08:11:30`
- Scope: active target wording and format authority crosscheck; no extraction or candidate generation.

## Findings

- Active targets present in canonical / Markdown / annotated witnesses: `4` / `4` / `4` of `4`.
- Format authority pass count / visual exact match count: `4` / `4`.
- Raw plain missing targets: `volcano_bonds`.
- Active-corridor corrections / selector-permission corrections: `3` / `0`.
- Witness conflicts / terminal ready areas / source-backed R3 hits: `2` / `0` / `0`.
- Fingerprint: `targets=4|canon=4|markdown=4|annotated=4|format=4|rawMissing=volcano_bonds|activeCorr=3|selectorCorr=0|witnessConflicts=2|ready=0|sourceR3=0`.

## Decision

- Keep canonical/DOCM/Markdown as exact text authority.
- Keep DOCM/high-res/crop-pack as format authority.
- Do not treat correction markup, Markdown bold, or annotated notes as extraction permission.
