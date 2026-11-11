# Inspect the native printed lines

Open the assigned ten images in both halves of each page. Use only those source pixels. Record all visible article-body baselines in top-to-bottom page order. Number locally as you work. Count a line that appears in both strips once. All positions are half-open native upright XYXY on a 2040 × 2805 raster. The top image has origin y = 0 and the bottom image origin y = 1322. Add this offset to bottom-strip coordinates.

For each row, record the exact leftmost and rightmost printed whitespace chunks. Keep case and punctuation. Exclude a freestanding separator that has no letters or digits and record it in uncertainty if it affects the edge. Preserve a printed hyphen at a line break. For a one-word row, use the same chunk for both edges. Use `null` for an unreadable edge and say which edge is affected. Record the first clearly readable adjacent pair of interior words when it exists. Use `null` when the row has fewer than two interior words or those words are uncertain. Record a loose ink box and two estimated points along the lower edge of the line's text so the tilt is visible. A wide blank gap on a single baseline stays one row.

Log headings, running text, folios, artwork lettering, signature and distinct display quotations separately in exclusions. Record uncertain roles explicitly. Keep any exact lossless diagnostic subcrops in the receipt with their native boxes. No resampling, character inference from another scan, OCR or prior transcript use.

Save one JSON receipt with the assigned reader ID, the supplied packet hash, UTC timestamps and these keys.

| Field | Contents |
| --- | --- |
| `reader` | `A` or `B` |
| `packetManifestSha256` | Supplied packet digest |
| `startedAtUTC`, `completedAtUTC` | ISO 8601 UTC timestamps |
| `priorCanonicalRowsSeen`, `peerMarksSeen` | Truthful booleans |
| `inspectedAssets` | Exact ten manifest paths, such as `assets/p75-top.png` |
| `rows` | Ordered records with `id`, `page`, `boxXYXY`, `baseline` as two [x,y] points, `firstChunk`, `lastChunk`, `cue` as a pair or null, `paragraphStart` as boolean or null, and `uncertainties` as an array of short observations |
| `exclusions` | Records with `page`, `boxXYXY`, `role` and `notes` |
| `diagnosticCrops` | Records with `page` and `boxXYXY` |
| `notes` | Review limits and decisions |

Use the integer printed page number. Choose unique IDs such as `p75-l01`. Box and baseline coordinates are visual estimates. Keep unavailable evidence explicit. Save the receipt before viewing any other research record.
