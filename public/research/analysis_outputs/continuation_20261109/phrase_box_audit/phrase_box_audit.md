# Historical phrase geometry audit

## Summary

{
  "rows": 34,
  "oldFullRatio": 7,
  "oldContiguousIndices": 13,
  "strictContiguousExact": 2,
  "compactContiguousExact": 2,
  "mediumStrongEdges": 17,
  "mediumStrongTargetRows": 5,
  "mediumStrongTargetsWithExactCompact": 0,
  "mediumStrongEdgesWithNoncontiguousOldIndices": 17
}

## Cause and dependency

analyze_exact_highres_reflection_geometry.py:62-78 greedily scans forward across entire page and skips wanted tokens it cannot find.
analyze_exact_highres_reflection_geometry.py:104-105 unions every matched word regardless contiguity/completeness.
analyze_reflected_highlight_graph.py:17 consumes the resulting exact_highres_reflection_geometry.json.
analyze_reflected_highlight_graph.py:47-70 promotes those overlap records into medium/strong graph edges.

Invalidates the all-17 graph statistic as evidence for intentional phrase-aligned overlap. Does not invalidate later independent scan-native target boxes or independently supported p76 clues.

## Per-span audit

| ID | Page | Old ratio | Old indices contiguous | Exact compact phrase found | Medium/strong edges |
|---|---:|---:|---|---|---:|
| orange_1 | 75 | 0.625 | False | False | 0 |
| orange_2 | 75 | 0.5 | True | False | 0 |
| orange_3 | 75 | 0.214 | False | False | 0 |
| orange_4 | 75 | 1.0 | True | True | 0 |
| orange_5 | 75 | 1.0 | True | True | 0 |
| orange_6 | 75 | 0.5 | True | False | 0 |
| orange_7 | 76 | 1.0 | False | False | 3 |
| orange_8 | 76 | 0.429 | False | False | 2 |
| orange_9 | 76 | 0.667 | False | False | 3 |
| orange_10 | 76 | 0.333 | True | False | 0 |
| orange_11 | 77 | 0.167 | True | False | 0 |
| orange_12 | 77 | 0.8 | True | False | 0 |
| orange_13 | 78 | 0.25 | True | False | 0 |
| orange_14 | 78 | 0.3 | False | False | 0 |
| orange_15 | 78 | 0.25 | True | False | 0 |
| orange_16 | 78 | 0.5 | False | False | 0 |
| orange_17 | 79 | 0.429 | False | False | 0 |
| orange_18 | 79 | 0.375 | False | False | 0 |
| orange_19 | 79 | 0.526 | False | False | 0 |
| orange_20 | 80 | 0.0 | False | False | 0 |
| grey_black_1 | 75 | 0.667 | True | False | 0 |
| grey_black_2 | 75 | 0.5 | False | False | 0 |
| grey_black_3 | 76 | 0.75 | False | False | 0 |
| grey_black_4 | 76 | 1.0 | False | False | 4 |
| grey_black_5 | 76 | 1.0 | False | False | 5 |
| grey_black_6 | 76 | 0.5 | True | False | 0 |
| grey_black_7 | 77 | 0.222 | False | False | 0 |
| grey_black_8 | 77 | 0.0 | False | False | 0 |
| grey_black_9 | 77 | 1.0 | False | False | 0 |
| grey_black_10 | 77 | 0.8 | True | False | 0 |
| grey_black_11 | 78 | 0.0 | False | False | 0 |
| grey_black_12 | 78 | 1.0 | False | False | 0 |
| grey_black_13 | 78 | 0.2 | True | False | 0 |
| grey_black_14 | 79 | 0.5 | False | False | 0 |

## Examples

- Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.: old box `[810.11, 363.37, 2145.33, 948.27]`, indices `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 82]`; exact compact matches `[]`.
- by the rancid catnip of fiat money.: old box `[952.84, 1128.27, 1583.4, 2069.16]`, indices `[107, 131, 165]`; exact compact matches `[]`.
- “buying the dip.”: old box `[571.89, 894.79, 1966.32, 1168.38]`, indices `[81, 102]`; exact compact matches `[]`.
- shitcoiner at heart.: old box `[1369.98, 1046.7, 1639.05, 1095.73]`, indices `[98]`; exact compact matches `[]`.
- Gotta be this way. Forty years of dumb post-1971 fiat money nonsense: old box `[739.75, 834.42, 2139.92, 874.53]`, indices `[62, 63, 65, 66, 67, 68, 69, 70, 72]`; exact compact matches `[]`.
- It’s a stun gun to the genitals.: old box `[1041.29, 436.57, 1805.41, 1532.75]`, indices `[12, 24, 140, 141, 142, 143, 144]`; exact compact matches `[]`.
- $1 billion: old box `[484.44, 979.74, 1844.75, 2507.26]`, indices `[92, 209]`; exact compact matches `[]`.
- “Volcano Bonds”: old box `[1207.14, 2320.76, 1402.54, 2360.87]`, indices `[198]`; exact compact matches `[]`.
