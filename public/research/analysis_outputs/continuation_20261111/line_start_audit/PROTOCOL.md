# Cross-scan body line boundaries

Keiser's December 2022 post points to a printed first-word reading. Any application to Issue 24 depends on which words actually start the physical lines. The existing high-resolution reconstruction is the canonical comparison model. This check gives two fresh readers the second scan and asks where its body lines and edge words are visible. [Creator clue register](../../../sources/creator-clues.json) · [Existing printed model](../../../sources/printed-lines.json) · [Machine protocol](PROTOCOL.json)

## Freeze the sources

Use the sole embedded JPEG at PDF indices 2–6 in the retained lower-resolution PDF. The preparation verifies each preexisting JPEG pin, decodes native upright 2040 × 2805 RGB and makes two exact full-width strips per page. The top strip covers rows `[0,1483)` and the bottom strip `[1322,2805)`. The overlap supports deduplication and keeps edge cases visible. No alignment, interpolation, contrast enhancement or OCR runs in packet preparation. The acquisition relationship between the two raster families is undocumented. [Lower-resolution source](../../../keyser%20bitcoin%20.pdf) · [Higher-resolution source](../../../magazine.pdf)

## Review and match

1. Two fresh AI contexts each inspect all ten strips before seeing the canonical model, expected counts or peer marks. Record each physical body baseline once. Preserve line order, separate first and last whitespace chunks, one adjacent interior cue pair when available, native coordinates, and uncertainty. Track display elements separately. A large horizontal gap on one physical baseline does not split the row. Keep the tilted page 79 writing in native coordinates.
2. Lock both complete receipts. Reconcile same-page rows using overlapping native bounds and an agreeing normalized cue pair. Short rows with no cue in either receipt require exact agreement on both edge chunks. A forced pair appears in every maximum-cardinality monotone matching. Keep nonforced matches unresolved.
3. Compare forced low-resolution pairs to canonical rows on the same page using the recorded adjacent interior cue. Normalize case and punctuation only for alignment. Inspect any unmatched interval bounded by forced pairs in both native raster contexts. A short line with no interior cue needs manual source confirmation. The high-resolution page 79 locator rotation belongs to its fixed high-resolution coordinate system. No projected y coordinate supplies a match.
4. Treat edge spelling or punctuation disagreement as tentative until the actual print is inspected. A changed first or last word, baseline membership or row order needs both low-resolution receipts plus a separate high-resolution adjudication. Preserve raw chunks and distinguish crop or legibility limits, layout differences between witnesses, and confirmed transcription errors. Record any further verification and source-pixel coordinates separately.

If the comparison finds a confirmed source change, record it as a correction before registering the affected reading. With no confirmed change, report coverage, ambiguity and any rows the sources cannot settle. This protocol concerns the article's printed inputs.

## Reproduction

Use PyMuPDF 1.26.5 and Pillow 11.3.0. Run from the repository root after publication of the receipts. Set `PRIVATE_PACKET` to a fresh directory, `PRIVATE_RESULT` to a fresh output file, and `REGISTERED_COMMIT` to the full commit in `REGISTRATION.json`.

```sh
DIR=public/research/analysis_outputs/continuation_20261111/line_start_audit
python3 public/research/scripts/prepare_issue24_line_start_audit.py \
  --research public/research --protocol "$DIR/PROTOCOL.json" \
  --registration-commit "$REGISTERED_COMMIT" --registration-receipt "$DIR/REGISTRATION.json" \
  --out "$PRIVATE_PACKET"
python3 public/research/scripts/reconcile_issue24_line_start_audit.py \
  --protocol "$DIR/PROTOCOL.json" --packet-manifest "$DIR/PACKET_MANIFEST.json" \
  --receipt-a "$DIR/READER_A.json" --receipt-b "$DIR/READER_B.json" \
  --receipt-lock "$DIR/RECEIPT_LOCK.json" --canonical public/research/sources/printed-lines.json \
  --out "$PRIVATE_RESULT"
```

The published manifest binds the receipts to the original packet. Compare replayed native asset and RGB hashes with that manifest.
