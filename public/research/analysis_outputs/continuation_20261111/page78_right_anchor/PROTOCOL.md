# Compare the right margin of page 78 with adjacent print

The final four lines on page 78 look flush right. Test whether that layout reproduces in both retained scans and whether the same criterion also identifies nearby right-aligned print. Page 78 contributes its preceding three paragraphs. Page 77 contributes a visually right-aligned paragraph and centered display quote. Page 79 contributes the four lines above the signature. These are visually selected controls from the same article. The test is a targeted comparison informed by inspection of the scans.

## Fixed measurement

The [configuration](PROTOCOL.json) pins the PDFs, zero-based face indexes, embedded JPEGs, row locators and two existing baseline receipts. Extract each embedded JPEG and apply the PDF orientation. In the sharper scan, extend the canonical vertical row bands by eight pixels. In the lower-resolution scan, average the two reader baselines endpoint by endpoint and retain pixels from 28 pixels above to nine below the resulting sloped line. Project lower-resolution pixel positions along the median row slope of each block. Use native x positions in the sharper scan. The fixed horizontal lanes exclude gutters and adjacent artwork.

For each row and each fixed shade threshold (96, 120, 144), select dark pixels using the maximum RGB channel or light pixels using 255 minus the minimum channel. Measure the 0.5th and 99.5th percentiles of projected x and their midpoint. These are contrast-support edges and can include a highlight bar. Require 40 selected pixels and a three-pixel clearance from both lane boundaries for the native x quantiles. Save every row and threshold, including failures.

Normalize the spans across rows by raster width. A right-aligned block requires a right-edge span of at most 1.2% and a left-edge span of at least 4.5% and four times the right-edge span. Reverse the conditions for left alignment. Center alignment requires the midpoint span to pass the same tightness gate and both side spans to pass the raggedness gates. A block counts in a two-scan result only when its classification agrees across all three thresholds in both scans. A failed clearance or contrast check invalidates that block. The preceding page 78 paragraph and the centered quote provide contrasting controls.

## How to read the outcome

If the target and a neighboring paragraph both classify as right-aligned in both scans, right alignment alone cannot uniquely select the target from these blocks. If the target alone passes, an independent printed or creator-linked direction cue is still required to interpret it as a reading instruction. Scans cannot establish the original typesetting coordinates, intent, or independent physical acquisition. The endpoints test contains no letter selection or decoding.

Replay with Python, PyMuPDF, Pillow and NumPy.

```sh
python3 public/research/scripts/measure_page78_right_anchor.py --out alignment.json
```
