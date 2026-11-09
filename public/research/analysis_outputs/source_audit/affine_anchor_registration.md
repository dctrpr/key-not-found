# Affine Anchor Registration Check

Scope: test whether the mirrored page-79 pill centers can be registered onto the page-76 X/dollar/black-bar/wire anchor set using a simple similarity transform.
This is a pattern-registration test only; it does not generate key candidates.

## Best Fits By Pair Count

- 3 pairs: meanNearestAll=140.1 maxNearestAll=269.41 fitRms=536.0 scale=0.47516 theta=-20.803deg
  - source=['p79_pill_2_mirror', 'p79_pill_3_mirror', 'p79_pill_5_mirror']
  - target=['p76_wire_right_knot', 'p76_black_bar_2', 'p76_black_bar_1']
  - mappedAll=[('p79_pill_1_mirror', 'p76_black_bar_1', 185.76), ('p79_pill_2_mirror', 'p76_black_bar_1', 67.65), ('p79_pill_3_mirror', 'p76_black_bar_1', 48.2), ('p79_pill_4_mirror', 'p76_black_bar_1', 129.5), ('p79_pill_5_mirror', 'p76_black_bar_1', 269.41)]
- 4 pairs: meanNearestAll=167.16 maxNearestAll=267.32 fitRms=568.66 scale=0.49538 theta=-60.262deg
  - source=['p79_pill_1_mirror', 'p79_pill_2_mirror', 'p79_pill_4_mirror', 'p79_pill_5_mirror']
  - target=['p76_wire_right_knot', 'p76_black_bar_1', 'p76_black_bar_2', 'p76_wire_left_knot']
  - mappedAll=[('p79_pill_1_mirror', 'p76_black_bar_1', 267.32), ('p79_pill_2_mirror', 'p76_black_bar_1', 155.11), ('p79_pill_3_mirror', 'p76_black_bar_1', 39.86), ('p79_pill_4_mirror', 'p76_black_bar_1', 109.18), ('p79_pill_5_mirror', 'p76_black_bar_1', 264.32)]
- 5 pairs: meanNearestAll=258.56 maxNearestAll=432.87 fitRms=1063.19 scale=0.85022 theta=44.801deg
  - source=['p79_pill_1_mirror', 'p79_pill_2_mirror', 'p79_pill_3_mirror', 'p79_pill_4_mirror', 'p79_pill_5_mirror']
  - target=['p76_black_bar_2', 'p76_wire_right_knot', 'p76_wire_left_knot', 'p76_dollar', 'p76_black_bar_1']
  - mappedAll=[('p79_pill_1_mirror', 'p76_black_bar_1', 432.87), ('p79_pill_2_mirror', 'p76_black_bar_1', 222.11), ('p79_pill_3_mirror', 'p76_black_bar_1', 174.5), ('p79_pill_4_mirror', 'p76_black_bar_2', 312.97), ('p79_pill_5_mirror', 'p76_black_bar_2', 150.36)]

## Assessment

- No strong 4- or 5-point similarity registration appears from the current manual anchor set. The best low-residual fits are likely overfit 3-point coincidences.
- The best 5-point fit still leaves mean/max nearest distances of 258.56 / 432.87 px, too loose for letter-level extraction.
- Current conclusion: these anchors remain orientation/region evidence. Precise affine registration needs either more corresponding visual marks or a manual overlay chosen from the actual page images, not just the current anchor list.
- Next best move: create a visual registration workbench/contact sheet for 76/79 and manually mark true corresponding points before re-running exact highlight geometry.
