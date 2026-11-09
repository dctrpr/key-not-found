# Current PDF Form Overlay Placement Gate

Scope: applied the duplicate-PDF `OL2` form placement matrix to its form BBox to test whether the tiny offset is a page-76/original-layout selector or only an invisible OCR overlay. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T08:36:25`
- Form placements / page-76 form placements: `16` / `2`
- Overlay signature groups / page-76 unique groups: `1` / `0`
- Active unique overlay groups: `0`
- Near-full overlays / page-76 near-full overlays: `16` / `2`
- All-page repeating overlay groups: `1`
- Visible/invisible text placements: `0` / `16`
- Strict/context hits: `0` / `0`
- Top offset pt values: `0.119995`
- Active projection rows inside overlay: `8` / `8`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `forms=16|p76Forms=2|groups=1|p76Unique=0|activeUnique=0|nearFull=16|p76NearFull=2|allPageGroups=1|visiblePlacements=0|invisiblePlacements=16|strict=0|offsets=0.119995|activeInside=8/8|sourceR3=0|triggers=0/9|selectors=0`
- Sheet: `analysis_outputs/source_audit/current_pdf_form_overlay_placement_gate/current_pdf_form_overlay_placement_gate_sheet.jpg`

## Page-76 Form Overlay Rows

| PDF | form xref | matrix | form bbox | display bbox | coverage | visible | strict | repeats every page |
|---|---:|---|---|---|---:|---:|---:|---:|
| `keyser bitcoin .pdf` | 60 | `1.0/0.0/0.0/1.0/0.0/0.119995` | `0.0/0.0/612.0/791.76001` | `0.0/0.119995/612.0/791.880005` | 0.999697 | 0 | 0 | `1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 60 | `1.0/0.0/0.0/1.0/0.0/0.119995` | `0.0/0.0/612.0/791.76001` | `0.0/0.119995/612.0/791.880005` | 0.999697 | 0 | 0 | `1` |

## Decision

- Decision: `current_pdf_form_overlay_placement_no_selector`
- Reason: The repeated OL2 form matrix offset applies to a near-full-page OCR form BBox, not a local page-76 mark. The same overlay signature repeats across every duplicate-PDF article page, has no page-76-unique group, contains only invisible OCR text, and has no strict unit/order terms or source-backed R3 bridge.
- Next move: Treat the duplicate-PDF OCR form overlay as a text-search aid only. Keep the next best move on true source/original-layout/raw clue acquisition rather than PDF OCR-wrapper geometry.
