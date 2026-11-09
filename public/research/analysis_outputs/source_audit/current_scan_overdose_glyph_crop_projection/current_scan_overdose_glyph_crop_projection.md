# Current Scan OVERDOSE Glyph Crop Projection

Scope: projected actual measured OVERDOSE header glyph slots into the current scan held-to-light crop windows for O4/B4/G5/O5. This checks glyph geometry plus source ink, not key material. No OCR-to-key extraction, hashes, WIF, seed phrase, address, BIP39, or broad candidate generation was run.

- Created: `2026-05-21T14:49:53`
- Sheet: `analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection/current_scan_overdose_glyph_crop_projection_sheet.jpg`
- Glyph projections / scenario-projection rows / target rows: `2` / `8` / `32`
- All-four dominant >=10% / touched >=25% / touched >=50%: `4` / `0` / `0`
- Layout-hit streams / strict instruction hits: `6` / `0`
- Valid natural 75->76 dominant line stream: `S.RD`
- Valid forced 75->76 dominant line stream: `OVRR`
- Benchmark 79->76 best dominant line stream: `DVRR`
- Valid natural / forced / benchmark black >=10% x streams: `R` / `VR` / `OVER`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `glyphs=2|scenarioProj=8|targets=32|allDom10=4|all25=0|all50=0|layoutStreams=6|strict=0|validNat=S.RD|validForced=OVRR|bench79=DVRR|black10=R/VR/OVER|sourceR3=0|triggers=0/9|selectors=0`

## Scenario Rows

| scenario | projection | dx | dy | dominant line | dominant x | black >=10 x | all dom >=10 | all >=25 | layout streams | decision |
|---|---|---:|---:|---|---|---|---:|---:|---:|---|
| `valid_75_to_76_natural` | `p76_header_glyph` | 0 | 0 | `S.RD` | `.RDS` | `R` | 0 | 0 | 0 | no active quartet glyph-ink selector |
| `valid_75_to_76_natural` | `p78_header_glyph` | 0 | 0 | `S.RD` | `.RDS` | `R` | 0 | 0 | 0 | no active quartet glyph-ink selector |
| `valid_75_to_76_forced_best` | `p76_header_glyph` | -220 | 200 | `OVRR` | `VRRO` | `VR` | 1 | 0 | 0 | weak all-target glyph coverage |
| `valid_75_to_76_forced_best` | `p78_header_glyph` | -220 | 200 | `OVRR` | `VRRO` | `VR` | 1 | 0 | 0 | weak all-target glyph coverage |
| `benchmark_79_to_76_natural` | `p76_header_glyph` | 0 | 0 | `...D` | `..D.` | `` | 0 | 0 | 0 | no active quartet glyph-ink selector |
| `benchmark_79_to_76_natural` | `p78_header_glyph` | 0 | 0 | `...D` | `..D.` | `` | 0 | 0 | 0 | no active quartet glyph-ink selector |
| `benchmark_79_to_76_best` | `p76_header_glyph` | 40 | 80 | `DVRR` | `VRRD` | `OVER` | 1 | 0 | 3 | weak all-target glyph coverage |
| `benchmark_79_to_76_best` | `p78_header_glyph` | 40 | 80 | `DVRR` | `VRRD` | `OVER` | 1 | 0 | 3 | weak all-target glyph coverage |

## Decision

- `glyph_crop_projection_no_active_quartet_selector`
- Do not promote actual OVERDOSE glyph rectangles inside the current light-table crop windows as an extraction selector.
- The glyph-aware pass does not create a physically valid all-four O4/B4/G5/O5 selector at meaningful thresholds.
- Any remaining layout fragments are still controlled by prior OVERDOSE/p75 results or depend on forced/non-physical registration, and no source-backed unit/order wording appears.
- Next move: Use this as the glyph-aware stop-check for the current scan. The next bounded move is not another slot permutation; inspect whether page-76 highlight edges or crop-window boundaries supply a source-backed instruction term, or wait for distinct source/original-layout material.
