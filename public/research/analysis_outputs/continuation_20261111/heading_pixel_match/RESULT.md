# The reflected trace matches locally in the sharper scan

**The sharper scan supports a shared shift for the page 75 heading and four held-out body regions on reflected page 74.** The lower-resolution scan produced two individually qualifying heading matches with an 18-pixel disagreement in vertical shift, exceeding the eight-pixel tolerance. No single translation met the criteria in that scan. The measurements support local opposite-face content correspondence in one raster. The optical mechanism and physical placement remain unresolved.

| Native raster | Heading peak correlations | Heading offsets (x, y) | Held-out result |
| --- | --- | --- | --- |
| Higher resolution | 0.550, 0.419 | (−44, −2), (−44, 0) | Frozen shift (−44, −1). Four of five pass, each within two pixels of the shift. The fifth falls below its strongest control. |
| Lower resolution | 0.287, 0.276 | (+21, +27), (+20, +9) | No shared shift qualifies. All five body regions fail the local gate. |

Offsets are receiver positions minus template positions, in native pixels of horizontally reflected page 74. At the sharper scan’s frozen shift, the four passing body correlations are 0.445, 0.315, 0.400 and 0.325. The passing regions span 291 native pixels vertically by their top edges. Five controls per feature receive the same search range as the intended match. All 14 synthetic injections recover the known shift at the tested amplitude. The [exact scores](SCORES.json) retain all runner-up peaks, controls, offsets and decisions. [Visual comparison](https://keynotfound.com/#visual-issue24-heading-pixel-match)

The heading was selected because of the earlier visual resemblance. The five body windows were declared from page 75 before this scorer examined the receivers. The [registered GitHub commit](https://github.com/dctrpr/key-not-found/commit/785b45c6254449a798b45d2ea54f85b035e03b90) precedes the run. [Protocol and rerun command](PROTOCOL.md) · [Exact boxes and thresholds](PROTOCOL.json) · [Replay receipt](RESULT.json)

Both PDFs are flattened raster sources, and independent acquisition is unproven. These local coordinates cannot establish physical show-through, rule out a duplicated image layer or define a general mirror transform. The tested regions stop in the upper part of one leaf. The result gives no new first-word rule, and it leaves the disputed page 77 initial untouched. [Physical source limits](../../continuation_20261110/g02_shared_query/PHYSICAL_SOURCE.md) · [Line-start audit](../line_start_audit/RESULT.md)

Next, test whether geometry estimated from visible same-face print and artwork outside the ghost region can predict the weaker scan’s match without fitting to it. If the independent landmarks cannot predict held-out same-face positions, retain the local one-raster result. A claim about physical show-through needs independently captured faces and a measured physical reference.
