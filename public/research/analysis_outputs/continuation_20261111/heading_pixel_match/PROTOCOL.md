# Test whether the faint band matches opposite-face print

The sharper scan shows a faint trace on printed page 74 that resembles the heading on page 75. The lower-resolution review found the trace but could not read it. The observed binding pairs 74 and 75. This is a quantitative local comparison of that pair, with the two raster families scored separately. [Pairing](../../continuation_20261109/state_audit.md) · [Earlier visual evidence](../full_page_glyph_review/SOURCE_CHECK.md) · [Lower-resolution result](../second_scan_heading_review/RESULT.md)

## Frozen measurement

Use native embedded JPEGs, correct PDF orientation, convert to grayscale and flip each receiver horizontally. Subtract a 25-pixel box blur from a 3-pixel box blur. Clip receiver contrast at ±18 grayscale units to limit the influence of strong foreground edges. Select two disjoint heading templates and five subsequent body regions from upright page 75 alone. Boxes are in half-open native coordinates. The registered [configuration](PROTOCOL.json) pins the sources, boxes and gates. The earlier visual evidence and a nonreproduced external pilot informed the choice of test, so this is a targeted follow-up. It is not a blind discovery study.

For each feature, search zero-mean normalized cross-correlation at every integer translation within ±100 horizontal and ±65 vertical pixels of the nominal same coordinate in the reflected raster. Record the maximum, the strongest runner outside a 12-pixel square around the maximum, and equally searched controls. Controls are the wrong-handed template on the same receiver, the correct template on pages 76 and 78 in the same orientation and coordinate convention, and the same template on page 74 at vertical offsets of −160 and +160 pixels. Those controls test local uniqueness rather than provide a population null distribution. For sensitivity, inject 18% of the centered template in the filtered wrong-page-76 window at the fixed shift [19, −11]. Recovery must be within two pixels. This checks the matching implementation at one signal level and background, not sensitivity to actual ink show-through.

A feature passes locally if its peak is interior, at least 0.27, exceeds its runner by 0.025 and every control by 0.05, and recovers the injection. A candidate shift exists only when both heading halves pass and their peaks are within eight pixels in both coordinates. Use their rounded mean without refitting on the body. A body holdout needs a local pass, a residual of at most 12 pixels and a score at the frozen shift at least 0.05 above its maximum control. Require two passing body regions with top edges at least 100 pixels apart to describe the translation as locally supported beyond the heading. The full score and failure receipts will be retained. Thresholds are operational checks, not statistical significance levels.

## Interpretation

This protocol tests pixel-content correspondence under a narrow local transform. The retained scans have no independent physical fiducials, documented camera geometry or proven independent acquisition. Even a positive result cannot establish the source layer, whether the phenomenon is physical show-through, exact paper alignment or a cipher instruction. An unfavorable result does not exclude differences in local scale, curvature, contrast or acquisition. No OCR, character selection or credential checking is part of the measurement.

Run the [measurement script](../../../scripts/measure_issue24_heading_pixels.py) from the repository root with Python, PyMuPDF, Pillow and NumPy installed.

```sh
python3 public/research/scripts/measure_issue24_heading_pixels.py --out heading-pixel-match.json
```
