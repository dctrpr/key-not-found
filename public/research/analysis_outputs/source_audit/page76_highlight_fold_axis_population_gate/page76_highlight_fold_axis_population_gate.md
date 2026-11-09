# Page 76 Highlight Fold-Axis Population Gate

Scope: enumerate horizontal, vertical, and point-reflection axes from the full page-76 highlight population, then test whether any single axis re-hits the locked O4/B4/G5/O5 quartet. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T03:50:40`
- Sheet: `analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate/page76_highlight_fold_axis_population_gate_sheet.jpg`

## Summary

- Line pitch threshold: `73.73 px`.
- Population targets: `10` (`4` active).
- Axis candidates tested: `141`.
- Axes with any active re-hit: `46`.
- All-four active axes: `0`.
- Three-plus active axes: `0`.
- Two-active axes: `6`.
- Tautological two-active point axes: `6`.
- Non-tautological two-active axes: `0`.
- Max non-tautological active hits: `1`.
- Strict instruction axis hits: `0`.

## Top Active-Rehit Axes

- `point` source `['B4', 'G5']` axisX `777.5` axisY `2494.75`: active hits `2`, all hits `2` tautological; B4->G5(0.0), G5->B4(0.0)
- `point` source `['B4', 'O5']` axisX `955.0` axisY `2689.25`: active hits `2`, all hits `2` tautological; B4->O5(0.0), O5->B4(0.0)
- `point` source `['G5', 'O5']` axisX `1173.0` axisY `2762.5`: active hits `2`, all hits `2` tautological; G5->O5(0.0), O5->G5(0.0)
- `point` source `['O4', 'B4']` axisX `1063.5` axisY `2311.25`: active hits `2`, all hits `2` tautological; O4->B4(0.0), B4->O4(0.0)
- `point` source `['O4', 'G5']` axisX `1281.5` axisY `2384.5`: active hits `2`, all hits `2` tautological; O4->G5(0.0), G5->O4(0.0)
- `point` source `['O4', 'O5']` axisX `1459.0` axisY `2579.0`: active hits `2`, all hits `2` tautological; O4->O5(0.0), O5->O4(0.0)
- `horizontal` source `['O3', 'O5']` axisX `None` axisY `2166.25`: active hits `1`, all hits `1`; O4->O4(69.5)
- `horizontal` source `['O4', 'O5']` axisX `None` axisY `2579.0`: active hits `1`, all hits `1`; G5->G5(22.0)
- `horizontal` source `['active_bbox_center']` axisX `None` axisY `2579.5`: active hits `1`, all hits `1`; G5->G5(23.0)
- `vertical` source `['G1', 'O5']` axisX `1345.75` axisY `None`: active hits `1`, all hits `1`; O5->O5(9.5)

## Decision

- Do not promote page-76 highlight-population fold axes as a selector.
- No single simple fold/mirror axis recovers all four active targets or even three active targets.
- The only two-active results are tautological point axes chosen from the same two active target centers.
- Reopen only if a new source/clue names a specific axis, fold operation, or reading unit/order.
