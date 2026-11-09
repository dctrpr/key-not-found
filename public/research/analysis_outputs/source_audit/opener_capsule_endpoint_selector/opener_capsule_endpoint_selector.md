# Opener Capsule Endpoint Selector

Scope: test whether the five opener capsules, after projection near M3/M4, choose usable page-76 lower-corridor units. No key derivation was run.

- Created: `2026-05-20T07:31:09`

## Streams

- `forcedMarkSequence` hits=none: `M3M3M4M4M4`
- `forcedUnitLabels` hits=none: `trust that guy | trust that guy | shitcoiner at heart | shitcoiner at heart | shitcoiner at heart`
- `forcedInitials` hits=none: `ttsss`
- `forcedLasts` hits=none: `yyttt`
- `m3As0Binary` hits=none: `00111`
- `m3As1Binary` hits=none: `11000`
- `bracketStream` hits=none: `guy [O5: shitcoiner at heart]`

## Threshold Stability

- <= `75px`: assigned `1` / 5, sequence `M3----`
- <= `100px`: assigned `1` / 5, sequence `M3----`
- <= `150px`: assigned `2` / 5, sequence `M3--M4-`
- <= `250px`: assigned `4` / 5, sequence `M3M3M4M4-`
- <= `500px`: assigned `5` / 5, sequence `M3M3M4M4M4`

## Capsule Rows

| capsule | p79 box | nearest mark | distance | forced unit |
|---:|---:|---|---:|---|
| 1 | 6 | `M3` | `56.94` | trust that guy |
| 2 | 7 | `M3` | `228.27` | trust that guy |
| 3 | 8 | `M4` | `204.96` | shitcoiner at heart |
| 4 | 9 | `M4` | `130.54` | shitcoiner at heart |
| 5 | 10 | `M4` | `420.93` | shitcoiner at heart |

## Assessment

- The five opener capsules project into the M3/M4 visual endpoint region, but the geometry is only tight for the first capsule.
- Forced nearest-mark reading gives M3 M3 M4 M4 M4, which maps to repeated `trust that guy` and O5 `shitcoiner at heart` units.
- Thresholded readings are unstable: tight thresholds leave most capsules unassigned, while loose thresholds force a pattern without a rule.
- The M3/M4 endpoint system confirms O5 again, but it still does not specify a word/letter/line extraction unit.
- Close opener-capsule -> M3/M4 endpoint mapping as a direct selector under the current scan.

## Next Move

- Keep opener capsules as provenance/order evidence only. Reopen only if a new source transform places all five capsules tightly on text units or a clue names M3/M4 as a binary/index selector.
