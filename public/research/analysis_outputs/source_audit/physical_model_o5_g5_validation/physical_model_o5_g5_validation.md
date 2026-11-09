# Physical Model O5/G5 Validation

Scope: validate physical leaf/spread assumptions against trusted O5/G5 page-76 boxes. No key derivation was run.

- Created: `2026-05-20T07:13:15`
- Overlay: `analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation_overlay.jpg`

## Target Boxes

- O5 `shitcoiner at heart`: `[1040.0, 2932.0, 1661.0, 2982.0]`
- Trusted G5 `Volcano Bonds`: `[795.0, 2544.0, 1196.0, 2592.0]`
- Stale projected `p76_grey_5`: `[1039.78, 2919.78, 1674.29, 2995.21]`

## Physical / Source Model Checks

| model | source page | source items | overlaps with trusted O5/G5 | nearest item summary |
|---|---:|---:|---:|---|
| same physical leaf front/back candidate: 75 -> 76 | `75` | `11` | `0` | orange `“Maximalist”` -> G5_trusted dist 360.86px |
| true facing spread candidate: 77 -> 76 | `77` | `5` | `0` | grey `It does this by monetizing` -> O5 dist 324.72px |
| non-physical control / known p78 visual source: 78 -> 76 | `78` | `7` | `0` | orange `the game-theorized Bitcoin protocol,` -> G5_trusted dist 546.03px |
| non-physical control / known p79 visual source: 79 -> 76 | `79` | `11` | `0` | orange `Everyone will live their own experience in the rabbit hole.` -> G5_trusted dist 555.54px |
| non-physical control / package source: 80 -> 76 | `80` | `2` | `0` | orange `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` -> G5_trusted dist 664.9px |

## P78 Graphic Frame Check

- p78 frame -> `O5` `shitcoiner at heart`: overlapVsTarget `0.24754`, horizontalGap `0px`, verticalGap `0px`, distance `483.07px`
- p78 frame -> `G5_trusted` `Volcano Bonds`: overlapVsTarget `0.0`, horizontalGap `38.0px`, verticalGap `0px`, distance `753.99px`

## Stale vs Trusted G5 Self-Mirror

### `page_center` x=`1272.0`
- stale projected `p76_grey_5` -> O5: overlapVsTarget `0.74754`, distance `163.54px`
- trusted G5 -> O5: overlapVsTarget `0.0`, distance `436.49px`, verticalGap `340.0px`
### `old_orange_bbox_center_axis` x=`1322.0`
- stale projected `p76_grey_5` -> O5: overlapVsTarget `0.90857`, distance `63.54px`
- trusted G5 -> O5: overlapVsTarget `0.0`, distance `490.03px`, verticalGap `340.0px`

## Assessment

- Using the trusted high-res G5 `Volcano Bonds` box, true physical page models do not naturally validate the O5/G5 pair on page 76.
- The old page-76 self-mirror B5/O5 result is driven by stale projected `p76_grey_5` geometry near O5, not by the trusted Volcano Bonds box at its actual page-76 location.
- The p78 graphic frame still supports the lower corridor: it overlaps O5 and sits adjacent to trusted G5, but it is not a true leaf/spread validation.
- This demotes page-76 G5/O5 self-mirror as exact geometry and keeps G5/O5 as semantic/corridor evidence only until source registration improves.

## Next Move

- Update future geometry tests to use only trusted lower boxes for G5. Re-run any high-value G5/O5 conclusions only when they depend on exact geometry; keep p78 frame/O5 endpoint as active orientation evidence.
