# Full-page printed glyph review

Two readers each completed all 32 tiles from printed pages 73–80. They reported **zero reading instructions, zero reversed marks and zero possible-reversal marks**. They recorded 52 marks as ordinary lettering viewed at a turn and left 17 marks unclear. Those 17 marks require source adjudication. The result covers the features the readers recognized in the retained rasters. [Merged result](RESULT.json) · [Finding coordinates](MERGED.json)

Both readers passed all four controls for ordinary, reversed, symmetric-only and rotated ordinary lettering. Each declared a fresh review context without access to peer or earlier target marks. The merge checked all 64 tile reviews and the 68 packet asset hashes. It finished at 2026-11-11T00:20:57.677Z. [Reader A](READER_A.json) · [Reader B](READER_B.json)

## Unclear marks

The 17 marks consist of nine faint-band or heading marks described as possible show-through, two instances of small curled or clipped banknote printing, two views of a tiny lapel-pin mark, two views of merged painted strokes and two views of paint-obscured lettering. The saved boxes have 21 positive-area intersections. The triage preserves each reader's mark and its exact page coordinates, including across tile seams. These observations leave the underlying print layer and some glyph shapes unresolved. [Coordinate and cause triage](UNCLEAR_TRIAGE.json) · [Page 74 and 75 source exhibits](SOURCE_CHECK.md)

## Registration and replay

The public registration commit was `90188fb126ffa8434f0ae73dcddde30f344a95f8`. The receipt records verification before target pixels were opened for packet preparation. Replay reproduced all 68 assets byte for byte. All 32 native tiles and their 32 reflections verified, and reconstructing the eight complete rasters recovered the pinned page RGB hashes. The source grid covers every pixel. Some visible features still resist interpretation at this scan quality. No OCR, key validation or new reading stream was generated for this review. [Frozen protocol and commands](PROTOCOL.md) · [Registration](REGISTRATION.json) · [Packet manifest](PACKET_MANIFEST.json) · [Replay](PACKET_REPLAY.json)
