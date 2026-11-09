# Local Page Raster Lineage Gate

Scope: mapped loose root JPEGs, source-image cache files, and 3D upright page images against current PDF embedded page rasters for article pages 73-80. This is source/provenance validation only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T16:13:45`
- Decision: `local_page_raster_lineage_no_distinct_source`
- PDF reference rows / local candidates: `24` / `24`
- Near duplicates / derivative-like rows: `24` / `24`
- Distinct local raster candidates / promoted source candidates: `0` / `0`
- Higher-resolution-than-best-reference rows / sharper rows: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/local_page_raster_lineage_gate/local_page_raster_lineage_gate_sheet.jpg`
- Fingerprint: `refs=24|candidates=24|nearDup=24|derivative=24|distinct=0|promoted=0|higher=0|sharper=0|sourceR3=0|triggers=0/9|selectors=0`

## Candidate Rows

| image | kind | page hint | best PDF page | MAD | candidate orient | ref orient | higher-res | sharper | near duplicate | derivative-like |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| `keyser bitcoin -1_1.jpg` | `root_keyser_jpeg` | `-` | `73` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -2_1.jpg` | `root_keyser_jpeg` | `-` | `74` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -3_1.jpg` | `root_keyser_jpeg` | `-` | `75` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -4_1.jpg` | `root_keyser_jpeg` | `-` | `76` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -5_1.jpg` | `root_keyser_jpeg` | `-` | `77` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -6_1.jpg` | `root_keyser_jpeg` | `-` | `78` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -7_1.jpg` | `root_keyser_jpeg` | `-` | `79` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `keyser bitcoin -8_1.jpg` | `root_keyser_jpeg` | `-` | `80` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `magazine-1_1.jpg` | `root_magazine_jpeg` | `-` | `73` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `magazine-2_1.jpg` | `root_magazine_jpeg` | `-` | `74` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `magazine-3_1.jpg` | `root_magazine_jpeg` | `-` | `75` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `magazine-4_1.jpg` | `root_magazine_jpeg` | `-` | `76` | 0.0000 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/source_images/magazine_page_75.jpg` | `source_image_cache` | `75` | `75` | 0.0528 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/source_images/magazine_page_76.jpg` | `source_image_cache` | `76` | `76` | 0.0498 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/source_images/magazine_page_77.jpg` | `source_image_cache` | `77` | `77` | 0.1601 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/source_images/magazine_page_78.jpg` | `source_image_cache` | `78` | `78` | 0.0460 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/source_images/magazine_page_79.jpg` | `source_image_cache` | `79` | `79` | 0.0563 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/source_images/magazine_page_80.jpg` | `source_image_cache` | `80` | `80` | 0.1876 | `identity` | `identity` | 0 | 0 | 1 | 1 |
| `analysis_outputs/3d_article_map/page_75_upright.jpg` | `upright_3d_cache` | `75` | `75` | 0.0997 | `identity` | `rotate180` | 0 | 0 | 1 | 1 |
| `analysis_outputs/3d_article_map/page_76_upright.jpg` | `upright_3d_cache` | `76` | `76` | 0.0930 | `identity` | `rotate180` | 0 | 0 | 1 | 1 |
| `analysis_outputs/3d_article_map/page_77_upright.jpg` | `upright_3d_cache` | `77` | `77` | 0.2477 | `identity` | `rotate180` | 0 | 0 | 1 | 1 |
| `analysis_outputs/3d_article_map/page_78_upright.jpg` | `upright_3d_cache` | `78` | `78` | 0.0838 | `identity` | `rotate180` | 0 | 0 | 1 | 1 |
| `analysis_outputs/3d_article_map/page_79_upright.jpg` | `upright_3d_cache` | `79` | `79` | 0.1077 | `identity` | `rotate180` | 0 | 0 | 1 | 1 |
| `analysis_outputs/3d_article_map/page_80_upright.jpg` | `upright_3d_cache` | `80` | `80` | 0.2995 | `identity` | `rotate180` | 0 | 0 | 1 | 1 |

## Decision

- `local_page_raster_lineage_no_distinct_source`.
- Every loose/local page raster maps back to the current PDF embedded page-image family as a near duplicate or derivative-like match.
- The local raster set does not provide a distinct higher-quality/original-layout source candidate or source-backed unit/order wording.

## Next Move

- Keep local loose page rasters as duplicate witnesses only. Reopen extraction only if a new physical/original-layout asset or raw clue wording passes the source-reopen requirements.
