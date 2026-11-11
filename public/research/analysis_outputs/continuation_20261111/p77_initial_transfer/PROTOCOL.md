# Test scan degradation on the disputed page 77 initial

The same printed row appears in two retained scans. The earlier sharper-scan reader reported an uppercase initial, and both readers on the lower-resolution crop ultimately favored lowercase. The word identity and line break agree. This experiment tests whether a fixed, local scan-transfer model can predict the surviving shape. The prior visual readings were known at registration. [Line-start audit](../line_start_audit/RESULT.md)

## Source and fitting

Use the two exact public context PNGs, in their native orientation. In each scan select five paired ordinary print patches for fitting, five disjoint ordinary holdouts, and two isolated known case controls from the same row. The additional `ig` holdout immediately follows the disputed glyph. It supplies the nearby geometry for projecting the target box and stays outside model fitting. One ordinary holdout shares a word with a fit patch and serves as a local check. The known capital control is heavier than the near-left text. [Fixed coordinates and settings](PROTOCOL.json) · [Control coordinate receipt](CONTROL_COORDINATES.json) · [Paired print crops](CONTROL_EXHIBIT.png) · [Neighboring letters](IG_ANCHOR.png)

Convert the pinned crops to grayscale. Resize the high patch to the dimensions of its paired low patch with Lanczos. Search the listed additional Gaussian blur radii and one common integer translation within two pixels on each axis. Edge-pad the resized patch for blur. Compare only the four-pixel-inset core after applying translation. For every grid point, fit one shared gain and offset by equal-patch-weight least squares, accepting gains from 0.2 to 1.5 and offsets from −40 to 160. Select the lowest equal-patch-weight RMSE, with smaller blur and translation magnitude breaking exact ties. Save the best no-added-blur fit as a comparison. No per-target alignment, contrast adjustment or threshold selection is allowed. The paired manual boxes supply local scale and placement, which are known imperfectly.

## Held-out gates

Normalize mean absolute luminance error by the median 95th-to-15th percentile span of the low fitting cores. This span must reach 40 grayscale levels. At least four ordinary holdouts must have normalized MAE at most 0.16 and correlation at least 0.60. The adjacent `ig` patch must be among them. Both case controls must also meet the same whole-glyph transfer thresholds.

Measure an upper-right to lower-right ink ratio in the fixed relative subregions from the protocol. Ink is positive grayscale excess above the median of the fitting patches' 15th percentiles, using the appropriate scan's background. The lower-region mean must reach 12 grayscale units. On the original high, predicted low and observed low case controls, the capital must exceed the lowercase ratio by at least 0.20. The midpoint of each control pair fixes its channel threshold. The ambiguity band is ±0.10. This is a scoped comparison with one example of each case, not a general typeface classifier.

## Disputed initial

If any held-out gate fails, stop before scoring the initial. The higher-resolution target box starts from the previously marked native box and stops before the adjacent `i`. Project it to the low crop by scaling around the corresponding `ig` boxes. Compute the same case ratio on the original high, predicted low and observed low patches, and apply the frozen whole-glyph error thresholds.

A compatible result requires a clearly upper-rich original high patch, upper-poor predicted and observed low patches, and acceptable whole-glyph error. If the three channels land on the same side of their thresholds and the whole glyph transfers, report metric consistency. A value inside the ambiguity band leaves case unresolved. Other outcomes show that the fixed model was insufficient for this comparison. No outcome authenticates an original print state or proves that scan blur, paper or ink variation caused a difference. The scan lineage and local ink distress remain unknown. No text-reading stream or key check is part of this test.

## Replay

From the repository root with Pillow 11.3.0 and NumPy 2.0.2:

```sh
python3 public/research/scripts/measure_p77_initial_transfer.py --out p77-initial-transfer.json
```
