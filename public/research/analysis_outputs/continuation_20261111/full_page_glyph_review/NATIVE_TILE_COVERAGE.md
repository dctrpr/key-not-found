# Native tile coverage and review priority

The 32 fixed windows cover every pixel of all eight 2544×3264 pages. Each of the 112 previously disjoint or partially covered ordinary-view boxes is fully covered by the tile union. **Only 22 fit within a single tile.** Reviewers need adjoining tiles for the other 90.

| Archived mirror-window coverage | Ordinary boxes | Whole in at least one tile | Split across tiles |
| --- | ---: | ---: | ---: |
| Disjoint | 83 | 15 | 68 |
| Partial | 29 | 7 | 22 |
| Full | 95 | 42 | 53 |
| Total | 207 | 64 | 143 |

The page axes cover [0,2544) and [0,3264) because adjacent windows overlap by 96 px along each axis. The Cartesian product gives the four tiles per page. An ordinary box can fit in a single tile exactly when its x interval fits either x span and its y interval fits either y span. A box fails this test when left < 1224 and right > 1320, or top < 1584 and bottom > 1680. For the priority cohort, 88 fail on x and two fail on y. None fail on both axes.

The exact inventory lists every priority box and all its intersecting tile IDs, with source and tile-local intersection coordinates. An independent two-axis boundary partition reproduced all 207 archived covered-pixel counts and classifications from the 114 original padded windows. It also checked every box's new tile union against its original area. Total page union is 66,428,928 distinct source pixels.

## Review implications

- The 83 disjoint boxes were the clearest archived coverage gap. Pages 78, 75 and 77 contribute 20, 18 and 16 of those boxes. These are review-effort priorities. The full page remains the source scope, including regions the detector never boxed.
- Page 77 has 21 priority boxes and every one spans a tile seam. Use the mapped adjacent tiles and shared overlap to establish continuity. The two boxes split beyond the y overlap are on pages 73 and 77. An overlap preserves visibility but gives no guarantee that the whole word or detector box appears in one view.
- If a candidate glyph fragment or reading direction needs context outside one view, carry its source rectangle across the adjoining tile IDs. Record one source observation so overlapping views do not multiply leads. Keep a visibility judgment unresolved when the tiles cannot establish continuity.

## Reproduce

From the repository root, run the metadata auditor with Python 3.9 or later and a fresh private JSON path. It checks the exact three public metadata digests before evaluation.

```sh
python3 -B public/research/scripts/audit_native_tile_coverage.py \
  --research public/research --out "$FRESH_PRIVATE_JSON"
```

The inventory measures source geometry. No raster pixels, glyph judgments, reading strings or key results were opened.
