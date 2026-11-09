# Leaf Hold-To-Light Sheet

Scope: inspect physical front/back leaves by overlaying each page with the horizontally mirrored page on the back side.
This is a visual geometry pass only; it does not generate key candidates.

- Sheet: `analysis_outputs/source_audit/leaf_hold_to_light_sheet.jpg`

## Scores

- 77_view_78_through: balanced=0.26451 jaccard=0.07910 overBase=0.08001 overBack=0.87442 highlightBalanced=0.00612 highlightJaccard=0.00287
- 78_view_77_through: balanced=0.26451 jaccard=0.07910 overBase=0.87442 overBack=0.08001 highlightBalanced=0.00612 highlightJaccard=0.00287
- 79_view_80_through: balanced=0.11608 jaccard=0.05150 overBase=0.21138 overBack=0.06374 highlightBalanced=0.08640 highlightJaccard=0.02729
- 80_view_79_through: balanced=0.11608 jaccard=0.05150 overBase=0.06374 overBack=0.21138 highlightBalanced=0.08640 highlightJaccard=0.02729
- 75_view_76_through: balanced=0.10400 jaccard=0.05479 overBase=0.09940 overBack=0.10882 highlightBalanced=0.00319 highlightJaccard=0.00158
- 76_view_75_through: balanced=0.10400 jaccard=0.05479 overBase=0.10882 overBack=0.09940 highlightBalanced=0.00319 highlightJaccard=0.00158

## Assessment

- Strongest feature-overlap view is `77_view_78_through` with balanced=0.26451.
- Strongest highlight-only view is `79_view_80_through` with highlightBalanced=0.08640.
- Full feature scores include text/background/art pixels; highlight-only scores are better for checking literal highlighted-mask correspondence.
- Use this sheet to decide whether a physical leaf pair has cleaner correspondence than the 76/79 art overlay.
- If no leaf pair shows clean non-text correspondence, the missing selector is probably not a direct hold-to-light affine overlay.
