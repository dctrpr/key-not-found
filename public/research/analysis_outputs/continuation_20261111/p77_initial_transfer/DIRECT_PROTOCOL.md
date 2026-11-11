# Compare the surviving glyph shape within each scan

The optical transfer failed validation near the disputed initial. This follow-up asks a different question. How does the initial's surviving upper-right ink compare with the known capital and lowercase forms on the same printed row? Use the previously registered boxes, sources and upper/lower ratio. No high-to-low pixel transfer, estimated blur, target-specific luminance fitting or new source model is used. The earlier case opinions and the optical control outcomes were known when this design was fixed. The target ratios had not been measured. [Optical test design](PROTOCOL.md)

For each scan, move each base box independently by −1, 0 and +1 pixel on both axes. Use the three background levels obtained from the median of fitting-patch 10th, 15th and 20th percentiles. That gives 27 conditions per glyph. Measure both controls before opening the target for scoring. Each control's interval covers all 27 ratios. A missing ratio or less than 0.20 separation between the lowest `B` and highest `b` stops target scoring in that scan. The midpoint of those inner control bounds sets the threshold. Call the surviving target shape upper-rich or upper-poor only if its entire interval stays at least 0.10 on the same side of that midpoint. Report the nominal ratio and every condition. [Parameters](DIRECT_PROTOCOL.json)

These are shape comparisons using one control of each case. They do not prove the original glyph case or model localized ink loss. The range covers the declared box shifts and background levels only. It does not model all geometric uncertainty, missing ink, other print weights or scan-lineage differences. An unscored or ambiguous result remains unresolved.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/compare_p77_initial_shape.py --out p77-initial-shape.json
```
