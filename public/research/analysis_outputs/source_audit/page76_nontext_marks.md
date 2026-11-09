# Page 76 Non-Text Marks

Scope: high-res visual geometry only. Detect large non-text black marks on page 76 and test whether mirrored page-79 pill fragments register to them under simple translation.

- Overlay: `analysis_outputs/source_audit/page76_nontext_marks_overlay.jpg`

## Summary

- Page-76 non-text marks detected: 4
- Page-79 pill fragments tested: 5
- Best translation: dx=-50 dy=350 mean=196.43 max=405.49 px

## Best Pairing

- pill 6 -> mark 3 distance=35.6 shiftedCenter=(2323.0, 2758.0)
- pill 7 -> mark 3 distance=290.38 shiftedCenter=(2072.5, 2804.5)
- pill 8 -> mark 4 distance=158.95 shiftedCenter=(1888.0, 2958.5)
- pill 9 -> mark 4 distance=91.74 shiftedCenter=(2057.0, 3130.5)
- pill 10 -> mark 4 distance=405.49 shiftedCenter=(2310.5, 3318.0)

## Marks

- mark 1: box=(430, 2400, 690, 2447) center=(560.0, 2423.5) area=12220
- mark 2: box=(795, 2544, 1196, 2592) center=(995.5, 2568.0) area=19248
- mark 3: box=(2172, 2619, 2544, 2884) center=(2358.0, 2751.5) area=98580
- mark 4: box=(1827, 3003, 2120, 3182) center=(1973.5, 3092.5) area=52447

## Assessment

- The page-79 pill fragments do not register cleanly to page-76 X/brush marks under simple high-res mirror plus translation.
- The best fit is still hundreds of pixels off on at least one fragment, so this is not a reliable anchor system.
- The non-text marks are useful visual context, but they do not currently supply the missing selector.
- Next best move: physical scan/photo alignment or manual line-level inspection of the page-76 corridor; avoid more generic affine/pill-anchor searches unless new anchor evidence appears.
