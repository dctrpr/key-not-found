# 3D Reflection Line-Pitch Stack Gate

Scope: shift the already-registered page-76 reflected boxes by integer page-76 line pitches and compare contacts with active O4/B4/G5/O5 plus all page-76 highlighted controls. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T03:40:51`
- Sheet: `analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/reflection_line_pitch_stack_gate_sheet.jpg`

## Summary

- Line pitch: `73.73` px.
- Reflections tested: `14`.
- Integer shifts tested: `-14` through `14`.
- Strong overlap threshold: `0.2` of target area.
- All-four active carriers: `3`.
- Single global shifts covering all four active targets: `0`.
- Strict instruction hits in carrier text: `0`.

## All-Four Active Carriers

- `78_76_4` `78->76` text `Have you seen the president of El Salvador`: active `buying_dip@+2(0.440), one_billion@+5(0.731), volcano_bonds@+7(0.746), shitcoiner_heart@+12(0.309)`; all-highlight controls `G3, G4, G5, O3, O4, O5`; instruction hits `[]`
- `79_76_4` `79->76` text `Have you seen the president of El Salvador`: active `buying_dip@+2(1.000), one_billion@+5(0.695), volcano_bonds@+7(1.000), shitcoiner_heart@+12(0.983)`; all-highlight controls `G3, G4, G5, O3, O4, O5`; instruction hits `[]`
- `79_76_5` `79->76` text `trolling the International Monetary Fund (IMF) on Twitter? taunting them, telling them he's ByiiREeraipy"`: active `buying_dip@+1(1.000), one_billion@+4(0.695), volcano_bonds@+6(1.000), shitcoiner_heart@+11(1.000)`; all-highlight controls `G3, G4, G5, O3, O4, O5`; instruction hits `[]`

## Decision

- Do not promote line-pitch walking of 3D reflected boxes as a selector.
- The operation can recover O4/B4/G5/O5 only by using different shifts per target; no single global shift covers the quartet.
- The same carriers also sweep broad page-76 highlighted controls, so the hits are not active-specific.
- Reopen only if a new source/clue names a specific reflection id plus target-specific line offsets or a global line-shift rule.
