# Registration Rotation/Scale Sweep 76/79

Scope: small rotation/scale/translation sweep around the best simple translation from the 76/79 workbench.
This is still a visual-registration diagnostic, not a key search.

- Working scale: `0.25`
- Full-resolution crop region represented: `(1450, 0, 2544, 3264)`
- Search center: `dx=-20`, `dy=240`, `angle=0`, `scale=1.0`
- Contact sheet: `analysis_outputs/source_audit/registration_rotation_scale_76_79_contact_sheet.jpg`
- Best overlay crop: `analysis_outputs/source_audit/registration_rotation_scale_76_79_best_overlay.jpg`
- Best mask preview: `analysis_outputs/source_audit/registration_rotation_scale_76_79_best_masks.jpg`

## Top Scores

- dx=20.0 dy=240.0 angle=2 scale=1.02 balanced=0.16152 jaccard=0.08779 overBase=0.16742 overOverlay=0.15583
- dx=-20.0 dy=200.0 angle=-2 scale=0.96 balanced=0.15578 jaccard=0.08433 overBase=0.14762 overOverlay=0.16439
- dx=20.0 dy=220.0 angle=2 scale=1.00 balanced=0.15542 jaccard=0.08424 overBase=0.15858 overOverlay=0.15232
- dx=20.0 dy=200.0 angle=-3 scale=0.96 balanced=0.15534 jaccard=0.08420 overBase=0.15319 overOverlay=0.15752
- dx=0.0 dy=240.0 angle=2 scale=1.02 balanced=0.15523 jaccard=0.08413 overBase=0.15805 overOverlay=0.15246
- dx=20.0 dy=260.0 angle=2 scale=1.04 balanced=0.15447 jaccard=0.08358 overBase=0.16247 overOverlay=0.14686
- dx=-40.0 dy=200.0 angle=-2 scale=0.96 balanced=0.15439 jaccard=0.08341 overBase=0.14355 overOverlay=0.16604
- dx=20.0 dy=200.0 angle=-2 scale=0.96 balanced=0.15407 jaccard=0.08345 overBase=0.15133 overOverlay=0.15686
- dx=0.0 dy=200.0 angle=-3 scale=0.96 balanced=0.15374 jaccard=0.08323 overBase=0.14886 overOverlay=0.15879
- dx=0.0 dy=200.0 angle=-2 scale=0.96 balanced=0.15342 jaccard=0.08303 overBase=0.14815 overOverlay=0.15888
- dx=0.0 dy=220.0 angle=2 scale=1.00 balanced=0.15327 jaccard=0.08299 overBase=0.15354 overOverlay=0.15300
- dx=-60.0 dy=200.0 angle=-2 scale=0.96 balanced=0.15224 jaccard=0.08200 overBase=0.13869 overOverlay=0.16711

## Assessment

- Translation baseline in this local grid: balanced=0.14172, jaccard=0.07626.
- Best local transform: dx=20.0, dy=240.0, angle=2, scale=1.02, balanced=0.16152.
- Improvement over translation baseline: 1.140x.
- Rotation/scale materially improves feature overlap; use the best transform for the next visual inspection pass.
- No key material is produced by this pass.
