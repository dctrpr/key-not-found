# Current PDF All-Leaf Imposition Consistency Gate

Scope: inspected page boxes, rotation, embedded image placement, scale, and hidden-layer indicators across article leaf pairs `75/76`, `77/78`, and `79/80` in the current PDFs. This checks original-layout/imposition provenance only; no key extraction, candidates, hashing-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T12:04:42`
- PDFs / inspected page records / leaf pairs: `3` / `18` / `9`
- Identical front/back pair geometry: `9` / `9`
- PDFs with uniform page geometry across pages 75-80: `3` / `3`
- Unique geometry families: `2`
- Side-margin pairs: `6`
- Placement-offset pairs / hidden pair-layer candidates: `0` / `0`
- All-leaf imposition candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate/current_pdf_all_leaf_imposition_consistency_gate_sheet.jpg`
- Fingerprint: `pdfs=3|pages=18|leafPairs=9|pairPass=9|withinPdfUniform=3|geometryFamilies=2|sideMarginPairs=6|placementOffsetPairs=0|hiddenPairLayers=0|impositionCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | pages | uniform pages 75-80 | rotations | image sizes |
|---|---:|---:|---|---|
| `magazine.pdf` | `6` | `1` | `[180]` | `['2544x3264']` |
| `keyser bitcoin .pdf` | `6` | `1` | `[0]` | `['2040x2805']` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `6` | `1` | `[0]` | `['2040x2805']` |

## Leaf Pair Rows

| PDF | pair | same geometry | side margins | placement delta | hidden layer |
|---|---|---:|---:|---|---:|
| `magazine.pdf` | `75/76` | `1` | `0` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `magazine.pdf` | `77/78` | `1` | `0` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `magazine.pdf` | `79/80` | `1` | `0` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `keyser bitcoin .pdf` | `75/76` | `1` | `1` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `keyser bitcoin .pdf` | `77/78` | `1` | `1` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `keyser bitcoin .pdf` | `79/80` | `1` | `1` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75/76` | `1` | `1` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77/78` | `1` | `1` | `[0.0, 0.0, 0.0, 0.0]` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79/80` | `1` | `1` | `[0.0, 0.0, 0.0, 0.0]` | `0` |

## Decision

- `current_pdf_all_leaf_imposition_consistency_no_selector`
- All inspected leaf pairs preserve identical front/back geometry inside each PDF.
- The duplicate PDFs' side margins are global derivative-PDF layout, not a page-76 or active-target imposition cue.
- This keeps PDF original-layout/imposition differences closed as a held-to-light selector.

## Next Move

- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
