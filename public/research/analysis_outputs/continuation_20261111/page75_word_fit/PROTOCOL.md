# Could the next word have fit on page 75?

Page 75 opens with a sentence split after “reaction.” Its next line begins with “to.” Both scans show the same two lines with similar-looking type and left setting. Treat them as one text frame for a conditional test. The frame boundary, exact typesetting settings and the cause of the break are unobserved.

## Fixed measurement

The [configuration](PROTOCOL.json) pins both PDFs, the embedded images for pages 75 and 78, two saved baseline inventories and the native scan windows. The word windows were placed by visual inspection before measuring their endpoints. Use upright native pixels and the maximum RGB channel at thresholds 112, 136 and 160. Keep the 0.2nd and 99.8th percentiles of the selected horizontal coordinates. Require 20 pixels for text and four for the isolated final period, with at least one pixel of horizontal locator clearance. Repeat the lower-resolution analysis with each reader’s baseline separately. Keep pixels from 33 pixels above to ten pixels below each baseline and project the opening rows along the mean slope of those two rows. Project each reference phrase along its own slope.

Measure the printed width of the first word on row 2. Estimate the interword space after the last glyph of row 1 from the visible gaps in “started to” and “hard to” on page 75 and “listen to” on page 78. The last phrase supplies the same preceding letter. Scale each reference gap by the ratio of the target word’s ink width to the reference word’s ink width. Use every reference and both lower-resolution baseline readings. Require positive gaps, reference word widths within a factor of 1.25 of the target and opening left-edge separation no greater than 12 pixels in every condition. These checks support an empirical comparison. They do not certify equivalent tracking, kerning or bearings.

For each scan, extend row 1’s right endpoint by the target word width and the observed range of reference spaces. Take the outer envelope across all conditions. Subtract four pixels from the minimum space and floor it at zero. Allow another four pixels on each uncertain endpoint. For the candidate upper endpoint this gives eight pixels of total allowance beyond the largest measured extension. Subtract four pixels from the smallest row 2 endpoint before its final period for the conditional width lower bound. Add four to the largest full row 2 endpoint to describe the upper extent of that row’s visible footprint.

## Decision

A conditional fit requires the upper appended endpoint to fall strictly inside the pre-period lower bound in both scans with all comparison checks passing. If the lower appended endpoint exceeds the full visible footprint, record the excess against that footprint. The actual frame could be wider. Any other result is inconclusive under these comparisons. A fit would challenge single-line greedy wrapping under the shared-frame assumptions. Paragraph composition, manual styling and variable text measures can also shape a break. A press-layout excerpt showing the frame and break marks would supply stronger evidence. The two scans’ acquisition history remains unknown.

```sh
python3 public/research/scripts/measure_page75_word_fit.py --out word-fit.json
```
