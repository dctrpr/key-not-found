# Reader B rotation note

I first inspected the sheet pairs and the original native upright and reflected PNGs. I used the following rotations on native upright crops in memory to check the handedness of tilted or upside-down type.

| Target IDs | Rotation |
| --- | --- |
| p73-04, p73-07, p73-08 | 180° |
| p73-05 | 155° counterclockwise |
| p74-02, p74-05 | 135° counterclockwise |
| p80-05 | 90° clockwise |

I rendered the rotations with AppKit's NSImage drawing at the source scale, on a canvas sized to contain the rotated crop. I left interpolation at its default. The exact resampling kernel is unknown. The rotated views I inspected were JPEG-encoded at an AppKit compression factor of 0.87. No rotated files were saved.

The rotated views informed the recorded orientation judgments for all seven targets. The source scans still have blur, clipped strokes or warped lettering in several of these crops. The exact angles needed to straighten the photographed baselines were approximate, and some individual glyphs remain only partly legible. I did not change the receipt after writing it.
