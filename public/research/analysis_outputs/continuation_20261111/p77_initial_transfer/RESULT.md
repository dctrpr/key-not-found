# The sharper scan’s initial is closer to lowercase

The disputed initial on page 77 has an upper-right to lower-right ink ratio of **0.13–0.29** in the sharper scan. The lowercase `b` on the same row ranges from **0.15–0.31**. The uppercase `B` ranges from **0.53–0.66**. The disputed mark stays on the lower-ink side in every declared condition. This favors the lowercase-shaped reading of the surviving sharper-scan pixels and gives a quantitative reason to reconsider the earlier uppercase visual reading. It uses one comparator of each case, with a heavier capital from the end of the line. [Exact native crops](CASE_COMPARISON.png) · [Per-condition measurements](DIRECT_MEASUREMENTS.json)

## Can one scan predict the other?

The best shared optical model used one pixel of additional Gaussian blur, zero common translation, gain 0.533 and offset 73.89 grayscale units. Training RMSE was 23.35 gray levels versus 25.82 for the best no-added-blur fit. Four of six ordinary holdouts passed. Both near-left checks fell short. The adjacent `ig` had normalized mean error 0.193 and correlation 0.563, against limits of 0.160 and 0.600. The uppercase comparator also failed the whole-glyph error limit at 0.173. The optical-transfer test stopped before scoring the disputed initial. [Optical scores](MEASUREMENTS.json) · [Registered model](PROTOCOL.md)

## What each scan shows on its own

| Scan | Known `b` interval | Known `B` interval | Control separation | Disputed initial |
| --- | ---: | ---: | ---: | --- |
| Sharper | 0.153–0.307 | 0.530–0.659 | 0.223 | 0.132–0.285, lower-ink side in all conditions |
| Lower resolution | 0.117–0.269 | 0.430–0.617 | 0.161 | Unscored under the 0.200 separation gate |

The direct test varies crop position by one pixel and background percentile across three fixed values. It does not predict how one scan was made from the other. Both lower-resolution readers previously favored lowercase on visual review. The direct lower-resolution test does not add a quantitative target call. The initial could still reflect distressed ink, local processing or a difference in capture. The scans do not establish the original typeset letter. [Direct protocol](DIRECT_PROTOCOL.md) · [Earlier visual assessments](../line_start_audit/RESULT.md)

Both numeric runs reproduced byte for byte. The optical protocol was [registered first](https://github.com/dctrpr/key-not-found/commit/a36ee7d5ac47569116c8b6e1f66ebe33b8045a18). After its validation failure, the direct protocol was [registered before measuring the disputed initial](https://github.com/dctrpr/key-not-found/commit/df1912b0f9c78acaa2c9f424dd109f4423568d0e). [Replay receipt](RESULT.json) · [Ordinary and case control boxes](CONTROL_COORDINATES.json) · [Visual log](https://keynotfound.com/#visual-issue24-p77-initial-transfer)

Treat `B` and `b` as alternatives in any interpretation that depends on exact case. A new full-page image of printed page 77 from an independently documented physical Issue 24 copy, with a close-up of this row and both known case controls, would give a stronger source test. The finding provides no new reading rule or puzzle solution.

To reproduce the native crop comparison after replaying the direct test, run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/render_p77_initial_exhibit.py --out p77-case-comparison.png
```
