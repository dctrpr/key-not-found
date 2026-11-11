# Page 74 and 75 in the second scan

The high-resolution scan shows a faint reflected page 74 trace whose spacing, size and slope resemble the page 75 title. This source check asks whether the second retained scan preserves readable evidence for the same association. The lower-resolution copy and its public archive alias contain the same bytes. The acquisition history of the two raster families is unknown. [First comparison](../full_page_glyph_review/SOURCE_CHECK.md) · [Source register](../../../sources/provenance.json) · [Machine protocol](PROTOCOL.json)

## Fixed scope

Use the embedded JPEGs at PDF indices 1 and 2 in the 2040 × 2805 lower-resolution source, with their registered orientation. On each face take the native half-open XYXY box `[0,0,2040,1683]` and make its exact horizontal reflection. The area covers the full upper 60% of each raster. There is no fitted transform, cross-scan coordinate transfer, interpolation or contrast enhancement. Exact subcrops for inspection are permitted and must be disclosed with their coordinates. No OCR, extracted reading streams or key checks are part of this comparison.

Two fresh AI contexts receive only the two page 74 images first. Each records its upright/reflected orientation judgment, the pale heading-like feature's bounds, any clearly readable contiguous words and at least two independently locatable asymmetric glyphs when available. A visible ordinary label elsewhere in the illustration is background context. A faint or unreadable feature stays uncertain. Save both receipts and lock their hashes before showing either reviewer the page 75 images.

Page 75 is the reference and orientation control. Each reader independently marks the normal printed headline and reports which image reads upright, the contiguous reading and source locations of any comparable asymmetric glyphs. Report any incidental earlier exposure, incomplete coverage, review uncertainty and diagnostic subcrops. Preserve the page 74 receipts as recorded.

## Decision rules

- **Corroborated** requires both orientation controls to pass, a shared page 74 feature and both locked page 74 receipts to read the same contiguous group of at least three words in reflection. That group must occur in both upright page 75 readings. Both readers must locate at least two shared asymmetric glyphs in order in that group on both faces. A shared feature or glyph requires positive-area overlap of the two readers' boxes on that page.
- **Contradicted at the observed feature** requires both controls, agreement on the location of the pale feature and a clear incompatible reading. Both readers must report the same complete group of at least three words, with at least two shared asymmetric glyphs located in the feature. An incompatible group absent from both reference receipts or an agreed ordinary upright orientation qualifies. This applies only to that feature in the lower-resolution source.
- **Inconclusive** includes an unlocatable, clipped, faint, disputed or inadequately readable trace, a failed control or no concordant source glyph anchors. Non-detection has unknown sensitivity at this scan quality. Close this fixed comparison without repeating it with a larger search.

Readable agreement can corroborate a common printed heading in the two images. It cannot determine the optical layer, whether the photographs were independently acquired, or a physical displacement. The original reader records remain frozen.

## Reproduction

Use PyMuPDF 1.26.5 and Pillow 11.3.0. Run these commands from the repository root after publication of the registration and receipts. Point `PRIVATE_PACKET` to a fresh output directory, `PRIVATE_RESULT` to a fresh output file and `REGISTERED_COMMIT` to the commit in `REGISTRATION.json`.

```sh
DIR=public/research/analysis_outputs/continuation_20261111/second_scan_heading_review
python3 public/research/scripts/prepare_issue24_second_scan_heading.py \
  --research public/research --protocol "$DIR/PROTOCOL.json" \
  --registration-commit "$REGISTERED_COMMIT" --registration-receipt "$DIR/REGISTRATION.json" \
  --out "$PRIVATE_PACKET"
python3 public/research/scripts/merge_issue24_second_scan_heading.py \
  --protocol "$DIR/PROTOCOL.json" --packet-manifest "$DIR/PACKET_MANIFEST.json" \
  --receipts "$DIR" --out "$PRIVATE_RESULT"
```

The recorded packet manifest binds the receipts to the original preparation timestamp. A replay uses the newly generated manifest to compare the four asset hashes and source pixel hashes.
