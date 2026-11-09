# P78 Frame Visual Marks

Scope: add known lower page-76 visual marks to the reflected p78 frame-edge audit. No key derivation was run.

- Created: `2026-05-20T06:53:45`
- Reflected p78 frame on p76: `[1234, 2398, 2250, 2950]`
- Overlay: `analysis_outputs/source_audit/p78_frame_visual_marks/p78_frame_visual_marks_overlay.jpg`

## Side Summary

| side | text contacts from prior audit | visual-mark contacts |
|---|---|---|
| `top` | should sell (cuts) | - |
| `left` | should sell (cuts); earnings (cuts); Volcano Bonds (right-adjacent); pay off the IMF (left-adjacent); I tagged Mike (left-adjacent); trust that guy (left-adjacent); shitcoiner at heart (cuts) | M2 text/highlight-false-positive (right-adjacent, 48px) |
| `right` | - | M3 standalone-mark (cuts, 265px) |
| `bottom` | shitcoiner at heart (cuts) | M4 standalone-mark (below-adjacent, 293px) |

## Mark Contacts

| mark | class | edge contacts | overlap of mark | nearest frame corner |
|---|---|---|---:|---|
| `M1` | `text/highlight-false-positive` | - | `0.0` | `topLeft` `544.0px` |
| `M2` | `text/highlight-false-positive` | left right-adjacent 48px d=38px | `0.0` | `topLeft` `150.86px` |
| `M3` | `standalone-mark` | right cuts 265px d=0.0px | `0.2097` | `bottomRight` `66.0px` |
| `M4` | `standalone-mark` | bottom below-adjacent 293px d=53px | `0.0` | `bottomRight` `140.39px` |

## Assessment

- The previous text-only frame read missed the unused right edge: the reflected p78 frame right side cuts true standalone mark M3 by a long vertical overlap.
- M4 is not cut by the frame, but sits just below the bottom edge with a 53px vertical gap and broad horizontal overlap.
- The frame is therefore not only a text-frame: top/left/bottom relate to corridor text, while the right/lower side also registers lower-right visual marks.
- This strengthens the p78 frame as an orientation/registration object, but still does not specify a word/letter extraction unit.

## Next Move

- Inspect M3 itself as a frame-side marker: compare its axis/ray with the reflected p78 right edge and test only simple adjacent-row labels, not key derivation.
