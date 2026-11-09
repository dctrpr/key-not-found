# Alternate PDF Pill Geometry Audit

Scope: compare the p79 lower-left pill fragments in the trusted high-res `magazine.pdf` scan and the local Google/OCR PDF. No key candidates are generated.

- Sheet: `analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry_sheet.jpg`
- ROI: `(0, 2210, 795, 3161)`

## Counts

- trusted high-res fragments: `5`
- Google/OCR normalized components: `5`

## Five-Point Fit

- affine mean residual: `0.31` px
- affine max residual: `0.45` px
- residuals: `[0.18, 0.37, 0.45, 0.41, 0.15]`

## Raw Nearest Distances

- Google order 1 center (247.5, 2241.0) nearest `[{'targetIndex': 6, 'distancePx': 183.69}, {'targetIndex': 7, 'distancePx': 275.42}, {'targetIndex': 8, 'distancePx': 513.4}]`
- Google order 2 center (485.0, 2279.0) nearest `[{'targetIndex': 7, 'distancePx': 186.63}, {'targetIndex': 6, 'distancePx': 339.47}, {'targetIndex': 8, 'distancePx': 351.01}]`
- Google order 3 center (661.5, 2417.5) nearest `[{'targetIndex': 8, 'distancePx': 198.9}, {'targetIndex': 7, 'distancePx': 242.84}, {'targetIndex': 9, 'distancePx': 426.81}]`
- Google order 4 center (507.0, 2579.5) nearest `[{'targetIndex': 8, 'distancePx': 103.16}, {'targetIndex': 7, 'distancePx': 151.44}, {'targetIndex': 9, 'distancePx': 212.84}]`
- Google order 5 center (272.0, 2757.0) nearest `[{'targetIndex': 9, 'distancePx': 166.67}, {'targetIndex': 10, 'distancePx': 228.81}, {'targetIndex': 7, 'distancePx': 337.43}]`

## Assessment

- The local Google/OCR PDF shows the same five lower-left p79 pill fragments, so it does not currently explain `diff pic` as a different visible picture.
- The same-normalized geometry is shifted/distorted, which agrees with the larger source-registration gap: OCR/Google PDF is useful as a witness, not final geometry truth.
- Do not reopen the ordered capsule projection from this PDF. Reopen only if a new source image or physical scan changes the five-fragment count/order/placement.

## Next Best Move

- Keep `magazine.pdf` as geometry truth. Use this sheet as the baseline if a new source image is supplied for the `pills don't line up / diff pic` clue.
