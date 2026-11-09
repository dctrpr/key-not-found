# Current PDF Partial Image Placement Gate

Scope: resolved the two page-76 `partialImagePlacement` rows from the current PDF object/layout report. This checks whether they are local overlays/original-layout carriers or just inset full-page raster pages. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T08:28:26`
- PDFs / image placements / page-76 image placements: `3` / `24` / `3`
- Page-76 partial placements: `2`
- Object-layout page-76 partial placement count: `2`
- Partial signature groups / unique page-76 partial groups: `1` / `0`
- Near-full content partial rows / local overlay partial rows: `2` / `0`
- All-page repeating partial groups: `1`
- Partial rows containing all four active boxes: `2`
- Active projection rows inside placement: `8` / `8`
- Partial coverage range: `0.941176` - `0.941176`
- Strict hits / special keys / visible painted spans: `0` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `p76Partial=2|partialGroups=1|uniqueP76Partial=0|nearFull=2|localPartial=0|allPageGroups=1|allFourInside=2|activeInside=8/8|strict=0|special=0|visible=0|sourceR3=0|triggers=0/9|selectors=0`
- Sheet: `analysis_outputs/source_audit/current_pdf_partial_image_placement_gate/current_pdf_partial_image_placement_gate_sheet.jpg`

## Page-76 Partial Placement Rows

| PDF | image xref | image size | rect norm | page coverage | repeats every page | all four active boxes inside | verdict |
|---|---:|---|---|---:|---:|---:|---|
| `keyser bitcoin .pdf` | 59 | `2040x2805` | `0.029412/0.000000/0.970588/1.000000` | 0.941176 | `1` | `1` | inset full-page raster |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 59 | `2040x2805` | `0.029412/0.000000/0.970588/1.000000` | 0.941176 | `1` | `1` | inset full-page raster |

## Decision

- Decision: `current_pdf_partial_image_placement_no_selector`
- Reason: The only page-76 partial image placements are the duplicate lower-resolution PDFs' inset full-page raster images. They cover about 94.1% of the page, span the full page height, repeat across every article page, and carry no page-76-unique local overlay, hidden placement, visible text, special resource key, strict unit/order term, or source-backed R3 bridge. They contain O4/B4/G5/O5 only because the entire page content is inside the raster image.
- Next move: Stop treating current-PDF partial placements as original-layout evidence. The next useful move is still source acquisition or raw clue wording that supplies transform, unit, and order, with the current scan used only as a visual comparison witness.
