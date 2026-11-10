# Issue 24 paper-edge visibility screen

The lower-resolution photographs preserve partial paper outlines around the printed faces. This screen tests whether both faces of pages 76/77 or 78/79 show enough directly visible trim to justify a separate physical registration study. The recorded quantities are image coordinates and marking intervals. [Source audit](../g02_shared_query/PHYSICAL_SOURCE.md)

## Frozen images and sampling lines

Use the single 2040 × 2805 JPEG from each of PDF indices 3–6 in the pinned lower-resolution PDF. Printed pages are 76–79. Use the native decoded RGB pixels with a top-left origin. Split the canvas at x = 0, 306, 1734, 2040 and y = 0, 421, 2384, 2805. The eight outer windows run clockwise NW, N, NE, E, SE, S, SW, W. The center is omitted. Guide sheets copy native pixel strips around the sampling lines and place coordinate ticks outside the copied pixels. The overview replaces the center with a neutral fill. [Frozen source](../../../keyser%20bitcoin%20.pdf)

For the head and foot, sample the perpendicular y crossing at x = 510, 1020 and 1530. For the left and right sides, sample the perpendicular x crossing at y = 701, 1402 and 2103. All coordinate intervals are inclusive integer pixel positions inside the fixed strip. Inspect a corner within its fixed window. The crop rectangles in the packet manifest use exclusive right and bottom bounds.

## Marking

Each of two separate AI contexts reviews the entire packet before seeing the other marks. Provide the visibility method, page-side orientation, source windows, overviews and guides. Record prior outcome or peer-mark exposure. Readers identify paper-to-background trim with continuity from the neighboring paper surface. Printed rules, image crop boundaries, gutter shadows and edges of other leaves can resemble trim. Record the competing cue and uncertainty.

- On each fixed crossing, mark the pixel interval that can contain the observed trim. A trim mark requires the expected physical edge label and direct visibility. Top is head, bottom is foot. The fore-edge is right on 76 and 78 and left on 77 and 79. Use a non-trim label and null interval for binding, adjacent leaf or shadow, image crop, obscured or ambiguous evidence.
- For each side, record the start and end of each visible trim run in the along-edge coordinate. Record observed curvature separately. Leave unmeasured areas outside the windows unresolved.
- Mark a corner only if the two paper boundaries visibly meet. Keep its inclusive bounding rectangle inside the corner window.
- Cover all 32 windows, 48 crossings, 16 sides and 16 corner windows. The receipt records observations and mark uncertainty. It gives no fitted transform.

Reader JSON has `version`, `reviewerId`, `registrationCommit`, `packetManifestSha256`, UTC start and completion, and flags `peerMarksSeen` and `priorShapeOutcomesSeen`. Its arrays are `windows` with an ID and note, `crossings` with an ID, label, interval and note, `edges` with an ID, runs, curvature and note, and `corners` with an ID, label, box and note. The packet and validator enumerate the allowed IDs and labels.

## Decision

An accepted crossing needs the expected physical trim label from both readers and overlapping intervals. Preserve their union. Unmatched, absent and disjoint marks stay unresolved. Summarize corner marks and curvature separately. A pair has two-axis visibility support for a separate study only when both faces have at least two accepted crossings on the same horizontal edge (head or foot) and at least two accepted fore-edge crossings. Two points on a side establish a witnessed segment at the screen's sampling resolution. Physical alignment additionally requires calibrated geometry and a validated link between the lower- and higher-resolution views of each face. No displacement, rotation or scale is inferred from this screen.

Freeze the protocol, image hashes and code before opening the packet. Verify current and registered blobs and all packet asset digests. Record both reviews and the merged decision. AI agreement supports repeatability of these marks under the stated method. No new reading or key check is part of this screen.

## Reproduce

Use PyMuPDF 1.26.5 and Pillow 11.3.0 for the image preparation. From the Git repository root, give the commands the published registration commit and absolute fresh output paths outside the repository. The two review receipts are linked from the result.

```sh
G02_DIR=public/research/analysis_outputs/continuation_20261110/g02_edge_screen
python3 public/research/scripts/prepare_edge_screen.py --self-test
python3 public/research/scripts/merge_edge_screen.py --self-test
python3 public/research/scripts/prepare_edge_screen.py \
  --research public/research --protocol "$G02_DIR/PROTOCOL.json" \
  --registration-commit "$REGISTRATION_COMMIT" \
  --registration-receipt "$G02_DIR/REGISTRATION.json" --out "$PRIVATE_PACKET"
python3 public/research/scripts/merge_edge_screen.py --merge \
  --research public/research --protocol "$G02_DIR/PROTOCOL.json" \
  --registration-commit "$REGISTRATION_COMMIT" \
  --registration-receipt "$G02_DIR/REGISTRATION.json" \
  --packet-manifest "$G02_DIR/PACKET_MANIFEST.json" --packet-directory "$PRIVATE_PACKET" \
  --reader-a "$G02_DIR/READER_A.json" --reader-b "$G02_DIR/READER_B.json" --out "$PRIVATE_MERGE"
```

The preparation timestamp belongs to each run. The saved manifest binds the original readers' packet and receipt chronology. Its asset digests can be checked against a regenerated packet. [Exact pins and parameters](PROTOCOL.json)
