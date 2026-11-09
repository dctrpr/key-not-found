# Magazine PDF Image Placement Audit

Scope: check whether `magazine.pdf` itself contains per-page image placement, crop, rotation, or hidden image-layer differences that could explain the p78->p76 registration repair. No key derivation was run.

- Created: `2026-05-20T08:57:11`
- PDF: `magazine.pdf`
- Pages: `8`
- Image counts by page: `[1, 1, 1, 1, 1, 1, 1, 1]`
- Unique image sizes: `[(2544, 3264)]`
- Page rotations: `[180]`
- Full-bleed single image every page: `True`
- Pixel/point scales: `[(4.166667, 4.166667)]`

## Page Placement

| pdf page | article page | rotation | image count | image px | image rect pt | gaps L/T/R/B pt | scale px/pt |
|---:|---:|---:|---:|---|---|---|---|
| 1 | 73 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 2 | 74 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 3 | 75 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 4 | 76 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 5 | 77 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 6 | 78 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 7 | 79 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |
| 8 | 80 | 180 | 1 | `2544x3264` | `[0.0, 0.0, 610.56, 783.36]` | `0.0/0.0/-0.0/-0.0` | `4.166667/4.166667` |

## Assessment

- Every page is a single 2544x3264 RGB JPEG image at 300 ppi.
- Each page image fills the crop/media box exactly with no per-page image offset or scale drift.
- All pages share the same PDF rotation and the same pixel-to-point scale.
- Therefore the p78 dx=-38/-40 registration repair is not explained by hidden PDF placement, crop-box mismatch, or extra embedded images inside magazine.pdf.
- The remaining source-registration gap must come from the printed/physical source, Canva/original-layout image, browser/source variant, or the puzzle's intended visual operation.

## Next Move

- Do not look inside magazine.pdf for a hidden higher-resolution layer. Continue with source/physical acquisition, or test only human-readable selector rules on the already locked high-res page-76 corridor.
