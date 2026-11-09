# Page 76 Highlight Spill Direction

Scope: inspect high-res scan pixels just outside the four active O-B-B-O highlight boxes to see whether marker spill, tail, underline, or side bias chooses a reading side/order. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T21:22:05`
- Source image: `analysis_outputs/3d_article_map/page_76_upright.jpg`
- Review sheet: `analysis_outputs/source_audit/page76_highlight_spill_direction/page76_highlight_spill_direction_sheet.jpg`
- Margin checked around each target: `28` px
- Dominant-side stream: `RRRB`
- Side-strength streams: `RBLT | RBLT | RLBT | BTLR`

## Side Metrics

| target | style | left | right | top | bottom | dominant | side order | dominant share |
|---|---|---:|---:|---:|---:|---|---|---:|
| `buying_dip` | `orange/yellow highlight` | 0 | 1143 | 0 | 200 | `right` | `RBLT` | 0.8511 |
| `one_billion` | `black highlight` | 0 | 116 | 0 | 19 | `right` | `RBLT` | 0.8593 |
| `volcano_bonds` | `black highlight` | 85 | 108 | 0 | 36 | `right` | `RLBT` | 0.4716 |
| `shitcoiner_heart` | `orange/yellow highlight` | 90 | 50 | 114 | 286 | `bottom` | `BTLR` | 0.5296 |

## Findings

- The side-spill pixels do not create a stable human-readable side/order rule for the four active anchors.
- Orange highlights show expected marker/scan bleed around the text bands; black highlights are dominated by dark band/glyph pixels and adjacent prose risk.
- The dominant-side stream is `RRRB` and the per-target side-strength streams are `RBLT | RBLT | RLBT | BTLR`; neither names a selector such as read/take/line/word/letter/mirror/key.
- The review sheet shows no arrow, tail, underline, or repeated side cue that would choose first/last/left/right extraction.
- Some targets have a strong numerical side imbalance, but the imbalance follows visible crop/text geometry rather than a repeated puzzle grammar.

## Decision

- Close active-highlight spill/tail direction as a standalone selector under the current high-res scan.
- Next move: Keep the highlight boxes as target evidence; move future passes toward new source/original-layout clues or explicit instruction wording.
