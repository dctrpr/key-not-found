# G05 paragraph eligibility audit

G05 retained displacement proxies for **98 of 142 printed rows**. A replay from saved public metadata accounts for the 44 unavailable rows. The shared optical guard rejected 38, and six more fell below the paragraph minimum. Even if every row passed the optical guard, the frozen paragraph rule could retain at most **136 of 142 rows**. [Original G05 result](../batch20/G05/RESULT.json)

| Saved reason | Rows |
|---|---:|
| `ink-touches-vertical-region-boundary` | 13 |
| `ink-touches-word-region-boundary` | 23 |
| `no-robust-ink-columns` | 1 |
| `no-robust-ink-rows` | 1 |
| `paragraph-too-short-to-detrend` | 6 |

G04 and G05 use the same helper to find ink inside each frozen word region. The G04 guard trace records agreement with the saved outcomes for all 142 rows. The replay takes the exact 38 failure IDs and reasons from the original G04 result, checks them against the trace counts and groups the remaining rows by their frozen page and paragraph IDs. G05 requires three surviving rows per paragraph before fitting a baseline trend. [G04 guard trace](../g04_guard_trace/RESULT.json), [G04 row records](../batch20/G04/RESULT.json), [printed row metadata](../../../sources/printed-lines.json), [geometry code](../../../scripts/batch20_geometry.py)

Two two-row paragraphs account for four of the six extra exclusions, p75r01–02 and p79r20–21. A four-row paragraph lost p79r22 and p79r24 at the optical guard, leaving p79r23 and p79r25 below the minimum. Two singleton paragraphs, p75r03 and p76r31, currently fail optics and would fail the paragraph gate even if their optical support were recovered. The four inherently short paragraphs account for the six rows below the theoretical ceiling.

| Printed page | Rows | Shared failures | Paragraph exclusions | Retained | Ceiling with perfect optics |
|---|---:|---:|---:|---:|---:|
| 75 | 32 | 7 | 2 | 23 | 29 |
| 76 | 31 | 6 | 0 | 25 | 30 |
| 77 | 32 | 11 | 0 | 21 | 32 |
| 78 | 22 | 5 | 0 | 17 | 22 |
| 79 | 25 | 9 | 4 | 12 | 23 |

The earlier availability audit compared all 98 saved retained row IDs and all 44 unknown IDs and reasons with the frozen paragraph groups. The public replay independently reconstructs eligibility and agrees with that comparison. Repeating the earlier exact comparison requires its original availability artifact, whose whole-file SHA256 is recorded in the result. [Machine result](RESULT.json)

The earlier G04 source review marked 12 top contacts and one left contact across p77r30, p78r09 and p78r10. All three rows failed the shared optical guard. The proposed G05 pilot would ask whether the lower ink contours and every contributing column could be certified on those same three rows. It remains unexecuted. Field residue and unassigned components still affect what can be claimed about column bottoms. [Aperture annotations](../g04_source_support/aperture/APERTURES.json), [source review](../g04_source_support/aperture/VISUAL_REVIEW.json)

G05 uses the 75th percentile of eligible ink-column bottoms as an optical proxy. Glyph shape, print and scan effects can change that statistic. Measured coverage remains 98/142 and the saved run retained zero labelled decodes. Even with perfect optics, pages 75, 76 and 79 and the global scope remain incomplete under the frozen paragraph rule. G05 and the puzzle remain open. [Registered geometry protocol](../batch20/GEOMETRY_PROTOCOL.json)

## Reproduce the public replay

Run this from the research archive root with Python 3.8 or newer. The script verifies the whole-file SHA256 of all three inputs and prints the same object stored under `publicReplay` in the machine result. [Replay script](../../../scripts/g05_paragraph_scope_audit.py)

```sh
python3 scripts/g05_paragraph_scope_audit.py --research-root .
```

The output records all 142 row IDs and eligibility dispositions across 20 paragraphs. Only saved metadata is used. Activity counters record zero image measurements, OCR runs, residuals, bit conversions, decoder calls, key checks and network queries.
