# P78 Pull-Quote Component Selector

Scope: split the lower p78 graphic pull-quote into connected components, mirror each component onto page 76, and check whether any component becomes a clean selector. No key derivation was run.

- Created: `2026-05-20T07:04:32`
- Graphic text: `The economy of love is infinitely more efficient than hate and war.`
- Component count: `13`
- P76 overlay: `analysis_outputs/source_audit/p78_pullquote_component_selector/p78_pullquote_component_selector_overlay.jpg`
- P78 source overlay: `analysis_outputs/source_audit/p78_pullquote_component_selector/p78_pullquote_component_source_overlay.jpg`

## Component Hits

| component | source box | reflected p76 box | target words | target highlights |
|---|---:|---:|---|---|
| `C01` | `[294, 2524, 409, 2630]` | `[2135, 2524, 2250, 2630]` | - | - |
| `C02` | `[418, 2484, 525, 2605]` | `[2019, 2484, 2126, 2605]` | - | - |
| `C03` | `[714, 2596, 730, 2614]` | `[1814, 2596, 1830, 2614]` | - | - |
| `C04` | `[773, 2589, 788, 2607]` | `[1756, 2589, 1771, 2607]` | - | - |
| `C05` | `[879, 2576, 894, 2594]` | `[1650, 2576, 1665, 2594]` | - | - |
| `C06` | `[1043, 2561, 1068, 2620]` | `[1476, 2561, 1501, 2620]` | the | - |
| `C07` | `[1047, 2616, 1086, 2662]` | `[1458, 2616, 1497, 2662]` | Mike | - |
| `C08` | `[1087, 2497, 1209, 2598]` | `[1335, 2497, 1457, 2598]` | off | - |
| `C09` | `[538, 2726, 553, 2744]` | `[1991, 2726, 2006, 2744]` | - | - |
| `C10` | `[361, 2398, 1139, 2950]` | `[1405, 2398, 2183, 2950]` | sell off the IMF Mike sella so far he that guy [O5: shitcoiner at heart] | p76_orange_5:shitcoiner at heart(0.1484) |
| `C11` | `[1155, 2629, 1209, 2750]` | `[1335, 2629, 1389, 2750]` | tagged could | - |
| `C12` | `[961, 2863, 1036, 2943]` | `[1508, 2863, 1583, 2943]` | - | p76_orange_5:shitcoiner at heart(0.0266) |
| `C13` | `[1266, 2750, 1310, 2938]` | `[1234, 2750, 1278, 2938]` | pals, trust | p76_orange_5:shitcoiner at heart(0.0085) |

## Streams

- `componentTargetStream`: `the | Mike | off | sell off the IMF Mike sella so far he that guy [O5: shitcoiner at heart] | tagged could | pals, trust`
- `componentSparseStream`: `C06:the | C07:Mike | C08:off | C10:sell off the IMF Mike sella so far he that guy [O5: shitcoiner at heart] | C11:tagged could | C12:- | C13:pals, trust`
- `highlightStream`: `C10:p76_orange_5 | C12:p76_orange_5 | C13:p76_orange_5`
- Instruction-term hits: `{}`

## Assessment

- Splitting the p78 pull-quote into individual visual components does not produce a cleaner selector than the whole frame/mask.
- Several components land on the same broad lower p76 corridor words already seen in the full-mask pass, especially IMF/Mike/sell/trust/O5-adjacent material.
- No component isolates an instruction or a single decisive extraction unit.
- This closes p78 pull-quote components as a standalone selector while preserving the p78 frame as registration evidence.

## Next Move

- Use p78 pull-quote only as a frame/orientation layer. The missing rule must come from source registration, Schott mirror operation ordering, or an external/physical source, not from component-by-component p78 text.
