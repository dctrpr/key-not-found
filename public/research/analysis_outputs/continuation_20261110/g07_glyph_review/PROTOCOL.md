# G07 printed glyph orientation review

Keiser's mirror-writing post links to a paper describing writing in the opposite direction with the shapes of the letters reversed. This review tests that literal visual property in the saved mirrored-baseline observations. The earlier G07 experiment checked OCR outputs for literal record formats. The current question is whether the source ink contains physically reversed glyphs that give a reading instruction. [Creator post](https://x.com/maxkeiser/status/1632391507008278528) · [Linked paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/) · [Earlier procedure](../batch20/G07/RESULT.md)

An earlier whole-page visual pass reported no individually reversed glyph. The fixed observation IDs and independent marks make this follow-up local and reproducible. [Earlier visual review](../../continuation_20261109/fresh_cryptanalysis/README.md)

## Source and crop identity

Use all 114 mirrored-baseline observation rectangles on printed pages 73–80. The coordinate export also retains the 207 normal baseline boxes for provenance. The reviewed population is the 114 mirrored-baseline boxes. Preserve their page and detector order and use stable page-local IDs.

Read the pinned public higher-resolution PDF. Decode the one embedded JPEG per page to RGB and rotate 180 degrees using the earlier baseline convention. Require both the embedded JPEG and upright RGB hashes from G07. Map the exact saved bottom-left normalized rectangles back to the upright frame with horizontal reflection and outward rounding. Add eight pixels of context per side and clip at the raster boundary. Save the upright and reflected crops at native resolution. Verify that they differ only by exact column reversal. Four crop pairs per sheet retain the same preview scale across both sides. Smaller sheet previews are for navigation and reading. Native crops remain available for any ambiguous details. [Source provenance](SOURCE.md) · [Coordinate export](BASELINE_BOXES.json)

## Independent review

Two fresh AI contexts inspect the complete frozen packet. They compare the upright ink with its reflected image. In the upright crop they mark ordinary, reversed, mixed, symmetric-only, nontext or unclear. Ordinary means visible asymmetric glyphs have their usual shapes and the crop supplies no credible reversed group. A reversed or mixed mark identifies the visible asymmetric glyphs and their positions. Symmetric characters, reversed word order, stylistic lettering and ordinary text rotated on the page receive their own visible interpretation. Preserve an unclear mark when clipping, blur, symmetry or unfamiliar artwork prevents a decision. Three synthetic controls check ordinary asymmetric glyphs, reflected asymmetric glyphs and exact left-right symmetry.

For an instruction candidate, record at least two visibly reversed asymmetric glyphs and a coherent action with the source unit or reading order. Mark uncertain readings as unclear. Keep ordinary editorial wording, isolated reversed marks and decorative lettering distinct from an actionable instruction. Store short visual notes and scope. Retain candidate or disagreement IDs for source adjudication. A machine comparison alone does not confirm a candidate's interpretation.

## Outcome rule

Report matched orientation and instruction judgments, disagreements, candidate IDs and control results. An agreed ordinary, reversed, mixed, symmetric-only or nontext judgment with two instruction-none marks is adjudicated within this review. A complete scoped nonrecognition result requires all 114 adjudicated, both sets of controls passed and no candidate reports. A failed control, disagreement, missing mark or uncertain source prevents a complete result for the affected scope. Retain any reversed glyph evidence even if no instruction was recognized.

This is a visual audit of the registered observation windows. It supplies no scan-wide claim about unobserved marks, no cryptographic check and no evidence of a verified key or prize.

## Reproduce

Use PyMuPDF 1.26.5 and Pillow 11.3.0 to prepare the image packet. Supply the full registered Git commit and fresh absolute output paths outside the repository.

```sh
G07_DIR=public/research/analysis_outputs/continuation_20261110/g07_glyph_review
python3 public/research/scripts/prepare_g07_glyph_review.py --self-test
python3 public/research/scripts/merge_g07_glyph_review.py --self-test
python3 public/research/scripts/prepare_g07_glyph_review.py \
  --research public/research --protocol "$G07_DIR/PROTOCOL.json" \
  --registration-commit "$REGISTRATION_COMMIT" \
  --registration-receipt "$G07_DIR/REGISTRATION.json" --out "$PRIVATE_PACKET"
python3 public/research/scripts/merge_g07_glyph_review.py --merge \
  --research public/research --protocol "$G07_DIR/PROTOCOL.json" \
  --registration-commit "$REGISTRATION_COMMIT" --registration-receipt "$G07_DIR/REGISTRATION.json" \
  --packet-manifest "$G07_DIR/PACKET_MANIFEST.json" --packet-directory "$PRIVATE_PACKET" \
  --reader-a "$G07_DIR/READER_A.json" --reader-b "$G07_DIR/READER_B.json" --out "$PRIVATE_MERGE"
```

Use the saved packet manifest with its original preparation timestamp for review-receipt chronology. Its asset hashes can be checked against the regenerated packet. [Exact pins](PROTOCOL.json)
