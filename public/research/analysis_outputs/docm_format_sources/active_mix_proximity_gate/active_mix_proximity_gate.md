# Active Typeka Mix Proximity Gate

Scope: test whether Typeka Mix islands near the locked O4/B4/G5/O5 targets create a clean selector. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T01:14:07`
- Sheet: `analysis_outputs/docm_format_sources/active_mix_proximity_gate/active_mix_proximity_gate_sheet.jpg`

## Summary

- Active targets: `4`
- Unique nearest Typeka Mix groups: `3`
- One-to-one Mix map: `False`
- Shared El/Mike band targets: `buying_dip, one_billion, volcano_bonds`
- Instruction hit count: `0`

## Streams

- Triplet initials: `EbM E$M EVM Is-`
- Previous Mix stream: `El Salvador | El Salvador | El Salvador | I don't really trust that guy.`
- Next Mix stream: `Mike Novogratz | Mike Novogratz | Mike Novogratz | -`
- Nearest Mix stream: `El Salvador | El Salvador | Mike Novogratz | I don't really trust that guy.`

## Active Rows

| order | target | group | prev Mix | prev gap | next Mix | next gap | triplet | nearest Mix |
|---:|---|---:|---|---:|---|---:|---|---|
| 1 | `buying_dip` | `12` | El Salvador | `1` | Mike Novogratz | `5` | `EbM` | El Salvador |
| 2 | `one_billion` | `14` | El Salvador | `3` | Mike Novogratz | `3` | `E$M` | El Salvador |
| 3 | `volcano_bonds` | `15` | El Salvador | `4` | Mike Novogratz | `2` | `EVM` | Mike Novogratz |
| 4 | `shitcoiner_heart` | `19` | I don't really trust that guy. | `1` | - | `-` | `Is-` | I don't really trust that guy. |

## Assessment

- Typeka Mix proximity does not map one-to-one onto the active quartet.
- O4, B4, and G5 are all bracketed by the same broad Mix anchors: `El Salvador` before and `Mike Novogratz` after.
- O5 is preceded by `I don't really trust that guy.` and has no following Mix anchor, so the active pattern is shared context plus endpoint, not four independent Mix pointers.
- The triplet and nearest-Mix streams contain no instruction terms.
- Keep Typeka Mix proximity as corridor/source-comparison evidence only unless a future raw clue names a font-state side or Mix-nearest rule.

## Decision

- Typeka Mix proximity is closed as a current-scan selector.
- Keep it as corridor/source-comparison evidence only; no selector was unlocked.
- Next move: Reopen Typeka Mix proximity only if source wording names nearest Mix, previous/next font state, or a font-side extraction unit.
