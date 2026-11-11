# Detector-independent printed glyph review

The G07 mirror review left 83 normal-view boxes entirely outside its observation windows and another 29 partly covered. The creator's linked paper describes reversed letter forms as a visible feature of mirror writing. This follow-up examines the eight complete scan rasters directly, including display type, artwork and margins. [G07 review and coverage](../../continuation_20261110/g07_glyph_review/RESULT.md) · [Mirror-writing paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/)

## Source and registered tile grid

Use the eight single embedded JPEGs in the pinned public higher-resolution PDF. Decode RGB and transpose 180° to match the archived upright baseline hashes. Each page is 2544 × 3264 pixels. For each page, cut two columns at `[0,1320)` and `[1224,2544)` and two rows at `[0,1680)` and `[1584,3264)`. The 96-pixel overlap along each seam covers the complete raster without resizing. Each tile has an exact horizontal reflection. Review the tile in its upright position on the page. Neighboring tiles and reconstructed source crops allow inspection across seams.

The old detector coordinates serve only for the separate coverage check. Readers see the fixed source tiles. The archived boxes and their relationship to the tile seams remain available as geometry metadata. [Pinned source](../../../magazine.pdf) · [Earlier raster identity](../../continuation_20261110/batch20/G07/RESULT.json)

## Marking and decision

Two separate fresh AI contexts review all 32 native upright tiles and four synthetic controls. Each uses the reflected tiles where needed and reads across seams when a feature continues. Report a brief visual note per tile. Record local half-open pixel boxes for physically reversed, possibly reversed, rotated ordinary and materially unclear marks. Record the asymmetric glyph shapes where visible. A reading-instruction report requires reversed source glyphs with at least two examples, a coherent reading action and its source unit or order.

For a suspect, preserve the upright source evidence. A lossless 90°, 180° or 270° counterclockwise turn may test rotated ordinary lettering. The diagnostic uses the same pixels and can show a corresponding reflection after the turn. Record the exact turn and any across-seam crop. Keep undecidable marks open. The controls check ordinary asymmetric type, reflected type, symmetric type and ordinarily printed type rotated 180°.

The validator confirms source IDs, asset hashes, controls and the two receipt populations. It maps local observations into page coordinates and preserves each reviewer's reported mark. It counts reports separately even where boxes overlap. Any instruction report or unresolved reversed mark requires separate source adjudication. Readable visual coverage depends on the source and the readers. Geometric coverage of every pixel supplies no guarantee that every glyph was recognized. The result is limited to reported visible features in the retained scan. No new OCR or cryptographic tests run.

## Reproduce

Use PyMuPDF 1.26.5 and Pillow 11.3.0. From the repository root, supply the full registered Git commit and fresh absolute output paths outside the repository.

```sh
DIR=public/research/analysis_outputs/continuation_20261111/full_page_glyph_review
python3 public/research/scripts/prepare_full_page_glyph_review.py --self-test
python3 public/research/scripts/merge_full_page_glyph_review.py --self-test
python3 public/research/scripts/prepare_full_page_glyph_review.py --prepare \
  --research public/research --protocol "$DIR/PROTOCOL.json" \
  --registration-commit "$REGISTRATION_COMMIT" --registration-receipt "$DIR/REGISTRATION.json" \
  --out "$PRIVATE_PACKET"
python3 public/research/scripts/merge_full_page_glyph_review.py --merge \
  --research public/research --protocol "$DIR/PROTOCOL.json" \
  --registration-commit "$REGISTRATION_COMMIT" --registration-receipt "$DIR/REGISTRATION.json" \
  --packet-manifest "$DIR/PACKET_MANIFEST.json" --packet-directory "$PRIVATE_PACKET" \
  --reader-a "$DIR/READER_A.json" --reader-b "$DIR/READER_B.json" --out "$PRIVATE_MERGE"
```

The saved manifest preserves the original preparation timestamp. Use it to replay the saved review chronology and regenerated assets. [Exact parameters and pins](PROTOCOL.json)
