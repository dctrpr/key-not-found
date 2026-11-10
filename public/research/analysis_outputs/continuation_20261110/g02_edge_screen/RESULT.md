# One page pair has visible trim on both axes

**Pages 78/79 met the edge-visibility rule.** Both faces show the foot and fore-edge at enough of the fixed sampling lines to justify a separate registration study. The two reviewers also marked one visible foot-to-fore-edge corner on each face. They observed curvature along both fore-edges, which the next study must account for. [Merged marks](MERGED.json) · [Machine result](RESULT.json)

**Pages 76/77 have foot evidence only in common.** Both reviewers accepted all three foot crossings on each face. Neither face had an agreed fore-edge crossing. The two-axis rule therefore leaves this pair unresolved in the retained photographs.

| Printed page | Agreed head crossings | Agreed foot crossings | Agreed fore-edge crossings | Agreed corners |
| --- | ---: | ---: | ---: | ---: |
| 76 | 1 | 3 | 0 | 0 |
| 77 | 1 | 3 | 0 | 0 |
| 78 | 0 | 3 | 3 | 1 |
| 79 | 2 | 3 | 2 | 1 |

The fore-edge is the outer edge opposite the binding. Each eligible edge has three fixed sampling lines. The readers agreed on 21 trim crossings and two corner regions. One crossing was unresolved by disagreement. The remaining crossings supplied no agreed trim. At a matched crossing the retained interval spans both marks. [Page 76 outer-edge guide](exhibits/guide-p76-right.png) · [Page 78 outer-edge guide](exhibits/guide-p78-right.png)

## Method and limits

Two separate AI contexts each reported examining the complete 32-window packet and recording every registered crossing, side and corner. Each reports seeing neither the other's marks nor the earlier stencil outcomes. The validator checked all IDs, bounds, chronology and all 52 packet asset digests. The lower-resolution public PDF regenerated every packet image byte for byte, and merging the receipts against the regenerated images reproduced the same result fields apart from execution timestamps. [Protocol](PROTOCOL.md) · [Registration receipt](REGISTRATION.json) · [Packet manifest](PACKET_MANIFEST.json) · [Packet replay](PACKET_REPLAY.json) · [Reader instructions](READER_INSTRUCTIONS.md) · [Reader A](READER_A.json) · [Reader B](READER_B.json)

This is visibility evidence at fixed sample positions. Estimating a physical transform requires measurable correspondence between the two faces and a separately validated link into the higher-resolution word coordinates. The review supplies neither a displacement estimate nor a new stencil reading.

## Next source tests

For pages 78/79, test whether matching print landmarks can transfer the observed trim into each higher-resolution scan. Freeze those landmarks and the transform family before fitting, and measure residuals at independent landmarks near the relevant edges. Keep uncertainty where the photographs curve or the higher-resolution raster lacks coverage.

Pages 76/77 contain the remaining page-local syntax matches in the shared-query result. This screen supplies no two-axis witness for that pair, so calibrating 78/79 alone would leave those matches unresolved. A separate route is to compare the original and reflected pixels of the saved G07 mirror-view observations for genuinely reversed printed glyphs. The saved detector boxes and raster lineage have been recovered for that review. [Shared-query result](../g02_shared_query/RESULT.md) · [Earlier G07 procedure](../batch20/G07/RESULT.md)
