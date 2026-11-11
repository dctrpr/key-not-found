# Source review receipt format

Inspect only the two supplied image views for the assigned stage. `u.png` shows the native upright crop and `r.png` its exact horizontal reflection. Each crop measures 2040 × 1683 pixels. Report all bounds in the specific view in which you located the feature. Use half-open XYXY image coordinates with a top-left origin. The verifier maps reflected boxes back to the upright pixel grid.

For stage 1, locate the faint heading-like mark in the pale illustration area. Record the most certain contiguous words if you can read them. Use an empty word list when you cannot read any. Record only individually locatable asymmetric glyphs from those words. Other artwork labels can appear in observations without entering the reading or glyph fields. A faint band whose location you can mark may still have no reliable orientation or reading.

For stage 2, record the conspicuous printed heading and which view reads upright. The stage 1 receipt must remain unchanged.

Each receipt is a JSON object with these fields.

| Field | Contents |
| --- | --- |
| `reader` | Assigned ID, `A` or `B` |
| `stage` | `1` or `2` |
| `packetManifestSha256` | Exact supplied packet manifest SHA-256 |
| `startedAtUTC`, `completedAtUTC` | ISO 8601 UTC timestamps |
| `bothViewsInspected` | Boolean |
| `peerMarksSeen`, `priorComparisonSeen` | Booleans |
| `page75ReferenceSeen` | Boolean |
| `stage1ReceiptSha256` | Stage 2 only, exact locked stage 1 hash |
| `view` | `upright`, `reflected` or `uncertain` |
| `featureBoxXYXY` | Bounds in the named view, or `null`. Use the upright view if orientation is uncertain. |
| `words` | Consecutive readable words as uppercase ASCII tokens, or empty |
| `glyphs` | Array of objects containing zero-based `wordIndex` and `charIndex` in `words`, `glyph`, and `boxXYXY` in the chosen view. Include only confident asymmetric glyphs. |
| `diagnosticCrops` | Any inspection-only subcrops with `view` and `boxXYXY`, or empty |
| `observations` | Concise visual findings and any limitations |

Include exact local bounds when visible. An approximate box may localize a feature if you label the uncertainty in observations. Omit any glyph whose identity or position you cannot support. Preserve a doubtful reading as an observation, not a confirmed word.
