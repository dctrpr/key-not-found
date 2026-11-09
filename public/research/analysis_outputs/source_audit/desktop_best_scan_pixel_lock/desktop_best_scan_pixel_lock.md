# Desktop Best-Scan Pixel Lock

Scope: verify that the Desktop `magazine.pdf` identified as the best scan is the same pixel source used by the current source-image and 3D/upright geometry caches. No key derivation, hashing of candidate text, seed checking, WIF checking, or address checking was run.

- Created: `2026-05-20T21:37:52`
- Desktop PDF: `private_inputs/Desktop/magazine.pdf`
- Workspace PDF: `magazine.pdf`
- Desktop/workspace byte-identical: `True`
- Review sheet: `analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock_sheet.jpg`

## Page Pixel Comparisons

| article page | PDF page | embedded size | fresh vs source RMS | fresh rot180 vs source RMS | fresh vs 3D RMS | fresh rot180 vs 3D RMS | source orientation | 3D orientation |
|---:|---:|---|---:|---:|---:|---:|---|---|
| 75 | `3` | `2544x3264` | `1.521296` | `79.671371` | `79.605161` | `2.246149` | `native` | `rot180` |
| 76 | `4` | `2544x3264` | `1.387905` | `76.443022` | `76.386999` | `2.069753` | `native` | `rot180` |
| 77 | `5` | `2544x3264` | `1.266827` | `86.670185` | `86.64517` | `1.901945` | `native` | `rot180` |
| 78 | `6` | `2544x3264` | `1.461057` | `90.114101` | `90.066067` | `2.125986` | `native` | `rot180` |
| 79 | `7` | `2544x3264` | `1.673382` | `73.753865` | `73.679267` | `2.426933` | `native` | `rot180` |
| 80 | `8` | `2544x3264` | `1.435913` | `60.628563` | `60.608171` | `1.894221` | `native` | `rot180` |

## Findings

- Desktop and workspace PDFs are byte-identical: `True`.
- Fresh embedded-page extraction matches `analysis_outputs/source_images` in native orientation for every page: `True`.
- Current 3D/upright page images match the same Desktop extraction after `rot180` within JPEG-resave tolerance for every page: `True`.
- This means page-76, page-79, and p78-frame geometry conclusions are using the user-supplied best scan, not an older OCR/source branch.

## Decision

- Do not reopen local PDF source selection. The Desktop best scan, workspace scan, `source_images`, and 3D upright cache are one source chain.
- Keep OCR PDF coordinates as labels only; exact geometry must stay tied to this high-res scan or a genuinely new physical/original-layout source.
- Next move: use the future-source validation packet only if a new scan/export/source appears; otherwise look for explicit selector wording rather than more local pixel permutations.
