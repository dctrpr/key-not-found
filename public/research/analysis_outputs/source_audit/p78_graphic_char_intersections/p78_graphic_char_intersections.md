# P78 Graphic Character-Intersection Audit

Scope: check whether the mirrored p78 graphic selects a sharper p76 letter stream than the previous word-level pass. OCR char boxes are labels only. No key derivation was run.

- Reflected p76 box: `[1234, 2398, 2250, 2950]`
- Overlay: `analysis_outputs/source_audit/p78_graphic_char_intersections/p78_graphic_char_intersections_overlay.jpg`
- Chars considered: `147`
- Bbox chars: `92`
- Dark center hits: `14`
- Hole center hits: `8`
- Dark pixel hits: `44`
- Hole pixel hits: `34`

## Streams

- `bbox`: `ouldsellarningsopayofftheIMFItaggedMikeecouldsellals,butsofarhetrustthatguydmensertslveaarty`
- `bboxLetters`: `ouldsellarningsopayofftheIMFItaggedMikeecouldsellalsbutsofarhetrustthatguydmensertslveaarty`
- `darkCenter`: `offIMgdelelshe`
- `darkCenterLetters`: `offIMgdelelshe`
- `holeCenter`: `FMiklatr`
- `holeCenterLetters`: `FMiklatr`
- `darkPixels`: `gsofftheIMFggedMikeuldsellals,rhetrgydmaarty`
- `darkPixelsLetters`: `gsofftheIMFggedMikeuldsellalsrhetrgydmaarty`
- `holePixels`: `offtheIFedMikeldellas,arhtgymaarty`
- `holePixelsLetters`: `offtheIFedMikeldellasarhtgymaarty`

## Assessment

- Character centers under the mirrored dark/negative masks still read as fragments of the same ordinary p76 corridor, not an instruction.
- The useful result remains target confirmation: p78 graphic -> p76 lower corridor.
- Close this micro-selector unless a new rule explicitly says to use dark strokes, white holes, or character centers from the graphic.
