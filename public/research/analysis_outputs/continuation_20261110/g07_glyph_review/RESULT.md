# No printed reading instruction recognized

Two separate AI readers compared the same 114 archived mirrored-baseline regions with the upright ink. **Neither reported an actionable reading instruction.** They agreed on 113 regions, including one with symmetric lettering. Both passed all three orientation controls. They differed on the handedness of one banknote fragment on page 73. Under the frozen rule, the overall review remains inconclusive for that region. [Machine result](RESULT.json) · [Merged decisions](MERGED.json)

## The disputed banknote fragment

Reader A flagged two apparently backward letters in `p73-04`. Reader B saw ordinary letters on an upside-down banknote. A separate lossless 180° turn of the native crop exposes conventional letter shapes in the curved denomination legend. The same turn of the reflected crop leaves the letter shapes mirrored. Two follow-up inspections saw an ordinary engraved fragment and no reading operation. The original disagreement stays in the frozen result. [Exact four-panel comparison](exhibits/p73-04-turned.png) · [Diagnostic receipt](ORIENTATION_DIAGNOSTIC.json)

Reader B also used temporary diagnostic rotations on seven native crops, including this fragment. The rotated views informed those orientation judgments. This display step went beyond the fixed pair views and is documented separately. Both original receipts are preserved. [Reader A](READER_A.json) · [Reader B](READER_B.json) · [Reader B’s display notes](READER_B_ROTATION_NOTE.md)

## Coverage and reproduction

The two readers report viewing all 32 sheets and using native crops where needed. The merge checked every row ID, source digest and declared exposure flag. The 263 packet assets replayed byte for byte. The two merges produced identical detailed decisions. The controls check three known glyph orientations and give no measured detection rate for the magazine. The review used the exact saved detector windows. [Protocol and commands](PROTOCOL.md) · [Packet manifest](PACKET_MANIFEST.json) · [Source coordinates](SOURCE.md) · [Packet replay](PACKET_REPLAY.json)

A separate pixel-coverage audit compared the 114 padded review windows with 207 ordinary-view detector boxes. **83 boxes were entirely outside the review windows**, and another 29 were partially covered. That count measures detector-box overlap. It gives a source-specific starting point for checking missed areas and supplies no page-wide claim about reversed printing. [Coverage audit](COVERAGE.json)

To reproduce the two follow-up checks, first regenerate the packet with the registered command. Supply fresh output paths.

```sh
G07_DIR=public/research/analysis_outputs/continuation_20261110/g07_glyph_review
python3 public/research/scripts/audit_g07_crop_coverage.py \
  --baseline "$G07_DIR/BASELINE_BOXES.json" --packet-manifest "$G07_DIR/PACKET_MANIFEST.json" \
  --out "$PRIVATE_COVERAGE"
python3 public/research/scripts/make_g07_orientation_diagnostic.py \
  --packet "$PRIVATE_PACKET" --out "$PRIVATE_DIAGNOSTIC"
```

A detector-independent review of the uncovered source regions comes next. The separate 78/79 transfer check found no print landmarks in the six fixed foot windows. A validated physical alignment remains open. [Transfer feasibility](../g02_transfer_feasibility/RESULT.md)
