# Best Scan Source Lock

User-supplied path: `private_inputs/Desktop/magazine.pdf`

Project source path: `magazine.pdf`

## Verification

- Desktop MD5: `2c454d800cf2971c1f86fd016f64b7a0`
- Project MD5: `2c454d800cf2971c1f86fd016f64b7a0`
- Result: byte-for-byte identical.

## PDF Metadata

- PDF version: 1.3
- Pages: 8
- Page size: 610.56 x 783.36 pts
- Page rotation: 180
- File size: 6,904,582 bytes
- Embedded image per page: 2544 x 3264 px, RGB, JPEG, 300 x 300 ppi

## Interpretation

This confirms the project has already been using the best available scan as `magazine.pdf`. The previous high-res image extraction, page-76 geometry, p80 package audit, and 3D viewer all derive from this source.

The unresolved issue is not choosing between local PDFs. It is the missing selector/registration rule inside this scan.

## Workflow Change

- Treat `magazine.pdf` as locked canonical geometry source.
- Do not ask for another digital PDF unless it is a materially different scan/export.
- Continue with high-res scan-native tests only.
- Keep OCR-PDF coordinates as labels only, not geometry truth.
