# Joint color membership audit for the two-sided stencil

The original G02 run retained zero complete readings. Its 97 flagged word-color occurrences blocked all 40 selector/order scopes, including cases where the uncertainty might not change the chosen category. Later mirror envelopes considered one reflected source color and at most one edge word per row. They did not evaluate G02's joint source-and-target color table or its retention of multiple words in a row.

## Fixed input and operation

Use only the original four directed physical pairs: 76→77, 77→76, 78→79 and 79→78. The existing 142 body rows contain 1,258 whitespace-delimited tokens, of which 1,243 have lexical word geometry under the original rule. The four target pages contribute 263, 274, 226 and 199 lexical positions in that pair order. Source preparation verified these identities and counts without classifying joint memberships.

Keep the owning inverse rotation, word order and orange/black rectangle definitions. The center guard is `max(12, frozen centerUncertaintyPx)`. Freeze the existing finite floating-point centers, mask coordinates and guard as exact binary rationals. The new enclosure uses every point in the closed guard square, with no clipping or added tolerance. This is a new, declared arithmetic model; it does not silently replace the old floating-point procedure or assert calibrated physical uncertainty.

Partition both axes at all relevant rectangle edges and square endpoints, then evaluate each endpoint and the midpoint of each open interval. Those Cartesian cells cover all Boolean mask-membership states in the model. Evaluate both sides at the **same displaced point**. The source color is evaluated at `(2544−x, y)` in the original rectangle coordinates; target color at `(x, y)`. This preserves the source reflection's opposite endpoint orientation rather than treating reflected rectangles as left-closed/right-open.

Each side has three ordinary states: none, orange or black. The original four classes are same nonzero color, opposite nonzero colors, source-only and target-only; neither color yields no selection. Any cell with both colors on one side leaves that word unresolved. Do not guess a color or treat overlap as none. Also leave a word unresolved if the nominal rational and original floating-point color pairs differ, or an original guard-unambiguous class conflicts with the new class set. Reproduce the legacy 20/25/23/29 flag counts before reporting complete coverage.

## Outputs and stop rule

Record ordered row/word IDs, centers, guards, joint states and membership labels only. For each existing selector, a word is `must`, `optional`, `out` or `unresolved`. When every word is classifiable, `2^optional` bounds the number of independent include/omit assignments. The global count uses the sum of optional positions across the four directed pairs. Shared geometry can correlate positions; selectors and directions are not independent observations. These bounds are strings to preserve exact large integers. A cohort with any unresolved word has a null bound.

The code stops on changed pins, incomplete geometry, wrong frozen counts or the 200,000 partition-point cap. The independent implementation reconstructs and compares the entire ordered metadata inventory and aggregate counts from the pinned files. The preparation receipt records synthetic controls only; the target membership audit begins after public registration. The maintainer verifies the remote commit and its pinned blobs, then supplies the registration receipt to the offline runners.

This audit adds no new image, OCR, geometry fit, word string, candidate, decoder, format check, derivation, history query or wallet action. Even a complete model only establishes the finite geometry inventory. A later reading procedure requires its own fixed protocol and feasibility decision. No exclusion, prize authentication or solution follows from these counts.
