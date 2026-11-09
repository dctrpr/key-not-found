# Current PDF Low-Res Render Source Trace

Scope: traced the anomalous low-resolution derivative PDF held-to-light source-only pixels back through the valid page 75 -> page 76 horizontal mirror transform into page-75 OCR word boxes. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:03:02`
- Sheet: `analysis_outputs/source_audit/current_pdf_lowres_render_source_trace/current_pdf_lowres_render_source_trace_sheet.jpg`
- Trace threshold: `0.05` source-only coverage
- Trace rows / unique trace shapes: `12` / `6`
- Skipped below threshold: `4`
- Source word rows / total word hits: `8` / `36`
- Strict instruction rows / token hits: `0` / `0`
- Context rows / token hits: `4` / `4`
- All-four eligible trace-pair count: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=2|pairs=4|traceRows=12|unique=6|skipped=4|wordRows=8|words=36|strictRows=0|strict=0|contextRows=4|context=4|allFour=0|sourceR3=0|triggers=0/9|selectors=0`

## Trace Rows

| pair | target | source-only | source trace box | strict tokens | context tokens | source page-75 snippet |
|---|---:|---:|---|---|---|---|
| `keyser bitcoin .pdf:rendered_300dpi` | O4 | 0.5128 | `743,2177,1126,2225` | - | buterin | in by riding Bitcoins Buterin came up with |
| `keyser bitcoin .pdf:rendered_300dpi` | B4 | 0.2693 | `1998,2398,2116,2445` | - | - | (no OCR words in source trace box) |
| `keyser bitcoin .pdf:rendered_300dpi` | G5 | 0.0652 | `1357,2544,1726,2592` | - | - | experience. |
| `keyser bitcoin .pdf:embedded_primary_image` | O4 | 0.5790 | `743,2177,1117,2225` | - | buterin | in by riding Bitcoins Buterin came up with |
| `keyser bitcoin .pdf:embedded_primary_image` | B4 | 0.0553 | `2048,2398,2116,2445` | - | - | (no OCR words in source trace box) |
| `keyser bitcoin .pdf:embedded_primary_image` | G5 | 0.0628 | `1359,2544,1749,2592` | - | - | experience. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:rendered_300dpi` | O4 | 0.5128 | `743,2177,1126,2225` | - | buterin | in by riding Bitcoins Buterin came up with |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:rendered_300dpi` | B4 | 0.2693 | `1998,2398,2116,2445` | - | - | (no OCR words in source trace box) |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:rendered_300dpi` | G5 | 0.0652 | `1357,2544,1726,2592` | - | - | experience. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:embedded_primary_image` | O4 | 0.5790 | `743,2177,1117,2225` | - | buterin | in by riding Bitcoins Buterin came up with |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:embedded_primary_image` | B4 | 0.0553 | `2048,2398,2116,2445` | - | - | (no OCR words in source trace box) |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:embedded_primary_image` | G5 | 0.0628 | `1359,2544,1749,2592` | - | - | experience. |

## Skipped Rows

| pair | target | source-only | reason |
|---|---:|---:|---|
| `keyser bitcoin .pdf:rendered_300dpi` | O5 | 0.0003 | below trace threshold |
| `keyser bitcoin .pdf:embedded_primary_image` | O5 | 0.0003 | below trace threshold |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:rendered_300dpi` | O5 | 0.0003 | below trace threshold |
| `analysis_outputs/external_clues/google_drive_article_download.pdf:embedded_primary_image` | O5 | 0.0003 | below trace threshold |

## Decision

- `current_pdf_lowres_render_source_trace_no_instruction_source`
- The low-resolution PDF inflation traces to ordinary page-75 article prose or blank/grey derivative margins.
- The repeated O4/B4/G5 pattern is duplicated by the two derivative PDFs and still does not include O5, so there is no all-four held-to-light selector.
- No traced source region supplies source-backed R3 instruction wording for fold, mirror, order, slot, read/take, or extraction.

## Next Move

- Stop spending cycles on derivative-PDF renderer toggles. The best next move is a new-source/original-layout comparison, or a raw clue that explicitly authorizes how O4/B4/G5/O5 should be ordered or transformed.
