# Page 76 Axis-Spine Selector Audit

Scope: test whether the mirror axis linking `Volcano Bonds` and `shitcoiner at heart` selects a vertical word/letter spine on page 76. No key candidates or hashing were generated.

- Created: `2026-05-20T05:35:01`
- Overlay: `analysis_outputs/source_audit/page76_axis_spine_selector/page76_axis_spine_selector_overlay.jpg`

## Axis Streams

### page_center x=1272.0

- Edge pattern: `B5->O5|O5->B5`
- Lower crossing words: `Salvador - he's - volcanoes should earnings - - - pals, trust siukbeodmensertslveaarty`
- Lower nearest words within 120px: `Salvador Fund he's when volcanoes should earnings pay I he pals, trust siukbeodmensertslveaarty`
- Lower crossing chars: `a-'-lur---,re`
- Lower nearest chars within 25px: `ay'wlurpIc,re`

### all_highlight_bbox_center x=1303.5

- Edge pattern: `B5->O5|O5->B5`
- Lower crossing words: `Salvador - - when volcanoes should earnings pay tagged could - trust siukbeodmensertslveaarty`
- Lower nearest words within 120px: `Salvador Fund he's when volcanoes should earnings pay I could but trust siukbeodmensertslveaarty`
- Lower crossing chars: `l--walnatc-un`
- Lower nearest chars within 25px: `lFswalnatcbun`

### orange_bbox_center x=1322.0

- Edge pattern: `B5->O5|O5->B5`
- Lower crossing words: `Salvador Fund - when volcanoes should earnings pay tagged could but trust siukbeodmensertslveaarty`
- Lower nearest words within 120px: `Salvador Fund he's when volcanoes should earnings pay tagged could but trust siukbeodmensertslveaarty`
- Lower crossing chars: `vF-hndiyaobss`
- Lower nearest chars within 25px: `vF-hndiyaobss`

### grey_bbox_center x=1303.5

- Edge pattern: `B5->O5|O5->B5`
- Lower crossing words: `Salvador - - when volcanoes should earnings pay tagged could - trust siukbeodmensertslveaarty`
- Lower nearest words within 120px: `Salvador Fund he's when volcanoes should earnings pay I could but trust siukbeodmensertslveaarty`
- Lower crossing chars: `l--walnatc-un`
- Lower nearest chars within 25px: `lFswalnatcbun`

## Primary Axis Detail

Primary axis: `orange_bbox_center`, because it is the axis used by the B5/O5 pair drilldown.

| line | y | crossing word(s) | nearest word | crossing char | line text |
|---:|---:|---|---|---|---|
| 21 | 2046.9 | `Salvador` | `Salvador (17.2px)` | `v` | Have you seen the president of El Salvador |
| 22 | 2122.8 | `Fund` | `Fund (24.3px)` | `F` | trolling the International Monetary Fund (IMF) on Twitter? |
| 23 | 2191.0 | `-` | `he's (53.1px)` | `-` | He's taunting them, telling them he's ByiiREeraipy" |
| 24 | 2265.9 | `when` | `when (5.6px)` | `h` | I tweeted President Nayib Bukele when he announced |
| 25 | 2340.8 | `volcanoes` | `volcanoes (17.2px)` | `n` | he was going to tap his nation's volcanoes to mine |
| 26 | 2413.5 | `should` | `should (57.1px)` | `d` | eis in bitcoin — that he should sell |
| 27 | 2487.2 | `earnings` | `earnings (11.8px)` | `i` | billions worth of future bitcoin earnings |
| 28 | 2557.6 | `pay` | `pay (15.6px)` | `y` | collateralized to pay off the IMF |
| 29 | 2631.4 | `tagged` | `tagged (34.2px)` | `a` | loan and get rid of those leeches. I tagged Mike |
| 30 | 2706.3 | `could` | `could (13.8px)` | `o` | Novogratz in the tweet, figuring he could sella |
| 31 | 2778.9 | `but` | `but (21.2px)` | `b` | bunch to his Wall Street crony pals, but so far he |
| 32 | 2849.4 | `trust` | `trust (26.4px)` | `s` | hasn't moved on it. I don't really trust that guy |
| 33 | 2939.4 | `siukbeodmensertslveaarty` | `siukbeodmensertslveaarty (18.2px)` | `s` | Maybe because he's a siukbeodmensertslveaarty |

## Assessment

- The vertical axis is a useful registration clue, but not a standalone selector.
- The lower-corridor stream reads as normal page text around `El Salvador`, `IMF`, `volcanoes`, `pay`, `Mike`, `trust`, and `shitcoiner at heart`.
- No read/take/fold/mirror/word/letter/key instruction appears in the crossing-word or crossing-character streams.
- Next best move: keep G5/O5 as the target pair, but look outside this axis for the rule that says what unit to extract.
