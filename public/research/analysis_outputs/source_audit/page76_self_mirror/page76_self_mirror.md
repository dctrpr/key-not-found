# Page 76 Self-Mirror Audit

Scope: reflect verified page-76 orange/grey highlight boxes across a few defensible vertical axes and measure whether they land on other page-76 highlights. No key candidates are generated.

- Overlay: `analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror_overlay.jpg`
- Crop: `analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror_crop.jpg`

## Axes

- `page_center` x=`1272.0`: meaningful edges `2` pattern `B5->O5|O5->B5`
  - B5 `Volcano Bonds` -> O5 `shitcoiner at heart.` (src=0.488, tgt=0.747, dist=163.5)
  - O5 `shitcoiner at heart.` -> B5 `Volcano Bonds` (src=0.747, tgt=0.488, dist=163.5)
- `all_highlight_bbox_center` x=`1303.5`: meaningful edges `2` pattern `B5->O5|O5->B5`
  - B5 `Volcano Bonds` -> O5 `shitcoiner at heart.` (src=0.554, tgt=0.849, dist=100.5)
  - O5 `shitcoiner at heart.` -> B5 `Volcano Bonds` (src=0.849, tgt=0.554, dist=100.5)
- `orange_bbox_center` x=`1322.0`: meaningful edges `2` pattern `B5->O5|O5->B5`
  - B5 `Volcano Bonds` -> O5 `shitcoiner at heart.` (src=0.593, tgt=0.908, dist=63.5)
  - O5 `shitcoiner at heart.` -> B5 `Volcano Bonds` (src=0.908, tgt=0.593, dist=63.5)
- `grey_bbox_center` x=`1303.5`: meaningful edges `2` pattern `B5->O5|O5->B5`
  - B5 `Volcano Bonds` -> O5 `shitcoiner at heart.` (src=0.554, tgt=0.849, dist=100.5)
  - O5 `shitcoiner at heart.` -> B5 `Volcano Bonds` (src=0.849, tgt=0.554, dist=100.5)

## Assessment

- The opener p73/p74 labels show true mirror symmetry. Page 76 has one repeatable local self-mirror pair: B5 `Volcano Bonds` <-> O5 `shitcoiner at heart`.
- The best of the tested axes is `orange_bbox_center` at x=1322.0, where the reflected pair reaches source overlap `0.593` / target overlap `0.908` with center distance `63.5 px`.
- No other verified page-76 highlight boxes participate, so this does not define a complete page self-fold selector.
- Page 76 should remain the target surface because external reflected systems point to it, not because the page self-folds.

## Next Best Move

- Stop page-76 self-fold tests unless a new source clue points there. The live gap is still the source/physical rule that maps p73/p79/p80 provenance evidence onto page-76 text.
