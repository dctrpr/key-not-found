# Current PDF Page-Box Pair Geometry Gate

Scope: checked current PDF page boxes, rotations, image placements, scale, and hidden-layer indicators for the valid article page 75 -> page 76 leaf pair. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation was run.

- Created: `2026-05-24T03:00:23`
- Sheet: `analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate/current_pdf_page_box_pair_geometry_gate_sheet.jpg`
- PDFs / page pairs: `3` / `3`
- Identical pair geometry: `3` / `3`
- Same boxes / rotations / image rects / scale: `3` / `3` / `3` / `3`
- Side-margin pairs / placement-offset pairs / hidden pair-layer candidates: `2` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pairs=3|pairGeometryPass=3|sameBoxes=3|sameRot=3|sameImageRect=3|sameScale=3|sideMargins=2|placementOffsets=0|hiddenPairLayers=0|sourceR3=0|triggers=0/9|selectors=0`

## Pair Rows

| PDF | p75 rotation | p76 rotation | p75 image rect | p76 image rect | image size | margins p75 | margins p76 | same pair geometry |
|---|---:|---:|---|---|---|---|---|---:|
| `magazine.pdf` | 180 | 180 | `[0.0, 0.0, 610.56, 783.36]` | `[0.0, 0.0, 610.56, 783.36]` | `2544x3264` | `0.0/0.0/0.0/0.0` | `0.0/0.0/0.0/0.0` | `True` |
| `keyser bitcoin .pdf` | 0 | 0 | `[18.0, 0.0, 594.0, 792.0]` | `[18.0, 0.0, 594.0, 792.0]` | `2040x2805` | `18.0/0.0/18.0/0.0` | `18.0/0.0/18.0/0.0` | `True` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 0 | 0 | `[18.0, 0.0, 594.0, 792.0]` | `[18.0, 0.0, 594.0, 792.0]` | `2040x2805` | `18.0/0.0/18.0/0.0` | `18.0/0.0/18.0/0.0` | `True` |

## Decision

- `current_pdf_page_box_pair_geometry_no_selector`
- Current PDFs do not supply an alternate page-box, rotation, or image-placement transform for the physically valid 75 -> 76 held-to-light pair.
- `magazine.pdf` is full-bleed on both pages; the two lower-resolution duplicate PDFs have side margins, but the margins and image scale are identical on page 75 and page 76.
- No hidden pair-layer, per-page offset, scale drift, source-backed instruction, or reopen trigger was found.

## Next Move

- Do not adjust valid 75->76 held-to-light geometry from current PDF page boxes; require a distinct physical/original-layout source or raw clue naming transform, unit, and order.
