# Registration Workbench 76/79

Scope: sweep simple x/y translations of horizontally mirrored page 79 over page 76 in the right-side visual corridor.
Feature masks include dark, orange, and yellow art/highlight pixels. This is a visual-registration diagnostic, not a key search.

- Crop region: `(1450, 0, 2544, 3264)`
- Translation sweep: dx/dy -260..280 px in 20 px steps
- Contact sheet: `analysis_outputs/source_audit/registration_workbench_76_79_contact_sheet.jpg`
- Best overlay crop: `analysis_outputs/source_audit/registration_workbench_76_79_best_overlay.jpg`
- Best mask preview: `analysis_outputs/source_audit/registration_workbench_76_79_best_masks.jpg`

## Top Translation Scores

- dx=-20 dy=240 balanced=0.16754 jaccard=0.09142 overBase=0.16480 overOverlay=0.17033
- dx=0 dy=240 balanced=0.16645 jaccard=0.09078 overBase=0.16658 overOverlay=0.16632
- dx=20 dy=240 balanced=0.16426 jaccard=0.08946 overBase=0.16730 overOverlay=0.16128
- dx=-40 dy=240 balanced=0.16390 jaccard=0.08921 overBase=0.15822 overOverlay=0.16980
- dx=40 dy=240 balanced=0.16278 jaccard=0.08853 overBase=0.16898 overOverlay=0.15681
- dx=-60 dy=240 balanced=0.16078 jaccard=0.08729 overBase=0.15284 overOverlay=0.16912
- dx=-80 dy=240 balanced=0.16026 jaccard=0.08690 overBase=0.14984 overOverlay=0.17140
- dx=-100 dy=240 balanced=0.15716 jaccard=0.08492 overBase=0.14392 overOverlay=0.17160
- dx=100 dy=240 balanced=0.15565 jaccard=0.08405 overBase=0.16980 overOverlay=0.14267
- dx=-120 dy=240 balanced=0.15371 jaccard=0.08274 overBase=0.13809 overOverlay=0.17111
- dx=80 dy=240 balanced=0.15365 jaccard=0.08298 overBase=0.16530 overOverlay=0.14283
- dx=180 dy=160 balanced=0.15322 jaccard=0.08226 overBase=0.17369 overOverlay=0.13516

## Assessment

- Best shift is dx=-20 dy=240 with balanced=0.16754; unshifted balanced=0.07172.
- Translation improves feature overlap, so a visual registration workbench is warranted before further exact-span geometry.
- This does not promote the pill anchors to a selector. It only narrows how to inspect the overlay visually.
