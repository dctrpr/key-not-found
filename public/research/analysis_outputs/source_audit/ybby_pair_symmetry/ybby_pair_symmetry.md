# Y-B-B-Y Pair Symmetry Audit

Scope: test whether the locked page-76 yellow/black/black/yellow sequence behaves as a mirror or bracket geometry. No key derivation, hashing, seed phrase, WIF, or address checks were run.

- Overlay: `analysis_outputs/source_audit/ybby_pair_symmetry/ybby_pair_symmetry_overlay.jpg`

## Anchor Rows

| id | color | label | center | box |
|---|---|---|---|---|
| `O4` | `yellow/orange` | `buying the dip` | `[1544.0, 2193.0]` | `[1328.0, 2160.0, 1760.0, 2226.0]` |
| `B4` | `black/grey` | `$1 billion` | `[560.0, 2423.5]` | `[430.0, 2400.0, 690.0, 2447.0]` |
| `G5` | `black/grey` | `Volcano Bonds` | `[995.5, 2568.0]` | `[795.0, 2544.0, 1196.0, 2592.0]` |
| `O5` | `yellow/orange` | `shitcoiner at heart` | `[1350.5, 2957.0]` | `[1040.0, 2932.0, 1661.0, 2982.0]` |

## Same-Color Pair Metrics

- Orange pair O4->O5 vector: `[-193.5, 764.0]`, angle `104.213` deg, midpoint `[1447.25, 2575.0]`.
- Black pair B4->G5 vector: `[435.5, 144.5]`, angle `18.356` deg, midpoint `[777.75, 2495.75]`.
- Segment angle delta: `85.857` deg.
- Common reflection-axis angle delta: `85.857` deg.
- Pair midpoint distance: `674.174` px.

## Streams Checked

| stream | text | instruction hits |
|---|---|---|
| `topToBottom` | `buying the dip \| $1 billion \| Volcano Bonds \| shitcoiner at heart` | `[]` |
| `bottomToTop` | `shitcoiner at heart \| Volcano Bonds \| $1 billion \| buying the dip` | `[]` |
| `sameColorOuterInner` | `buying the dip \| shitcoiner at heart \| $1 billion \| Volcano Bonds` | `[]` |
| `pairMidpoints` | `orange midpoint (1447.25, 2575.0) \| black midpoint (777.75, 2495.75)` | `[]` |

## Assessment

- The confirmed Y-B-B-Y sequence is a real active target signature, but the same-color pairs do not share a common mirror axis.
- Orange pair and black pair segment angles differ by 85.857 degrees.
- Their perpendicular-bisector axes differ by 85.857 degrees, so a single reflection axis cannot map O4->O5 and B4->G5.
- The orange-pair and black-pair midpoints are 674.174 px apart, so the four anchors do not form a clean 180-degree rotational bracket either.
- The simple order streams are only the known semantic labels and contain no instruction terms.

## Decision

- Keep Y-B-B-Y / O-B-B-O as a distinctive page-76 source-comparison signature, not a mirror/bracket extraction rule.

## Next Move

- Do not spend more local passes trying to infer an axis from the four color targets. The remaining blocker is still an external/source instruction or a new physical/original-layout image that changes the active target geometry.
