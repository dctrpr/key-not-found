# Page 76 Active Highlight Fill Audit

Scope: inspect the actual high-res scan pixels inside the four active O-B-B-O highlight boxes. This removes ordinary dark glyph strokes and looks for leftover hidden marks or readable residue inside the fill. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T21:16:10`
- Source image: `analysis_outputs/3d_article_map/page_76_upright.jpg`
- Review sheet: `analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill_sheet.jpg`
- Large residual components after glyph removal: `5`

## Target Metrics

| target | style | fill coverage | ink components | residual components | large residual components | largest residual areas |
|---|---|---:|---:|---:|---:|---|
| `buying_dip` | `orange/yellow highlight` | 0.4477 | 13 | 7 | 5 | `193, 150, 130, 108, 70` |
| `one_billion` | `black highlight` | 0.0014 | 6 | 0 | 0 | `-` |
| `volcano_bonds` | `black highlight` | 0.0025 | 12 | 0 | 0 | `-` |
| `shitcoiner_heart` | `orange/yellow highlight` | 0.5564 | 18 | 3 | 0 | `14, 11, 10` |

## Findings

- The four active highlight boxes are visually explained by normal scan-visible highlight fill plus ordinary text glyphs.
- After dark glyph pixels are removed, the residual maps do not expose a readable hidden word, symbol sequence, or ordering mark inside the active fills.
- The counted large residual pieces are not free-standing symbols; on the review sheet they sit on highlight/glyph-edge bands, especially around O4 `buying the dip`.
- This supports using O4/B4/G5/O5 as highlighted target boxes, but it does not supply the missing extraction unit or order.
- For black-highlight targets, the dark band itself is captured by the dark-pixel mask; the relevant check is whether any separate residue remains after that band is accounted for.
- One or more fill masks are sparse under automatic color thresholds; the review sheet should be treated as visual support, not a pixel-perfect segmentation model.

## Decision

- Close hidden-fill residue inside the current high-res active highlights as a standalone selector. Reopen only with a different physical/original scan or an explicit clue naming fill/ink/noise.
- Next move: Keep the active highlights as target evidence; future cadence should prioritize source/original-layout evidence or explicit instruction wording over more local highlight-fill permutations.
