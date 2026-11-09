# Future Source Scoring Rubric

Scope: turn the current page-76 and p78-frame evidence into explicit acceptance thresholds for future physical/original-layout/raw-clue material. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.

- Created: `2026-05-20T23:16:30`
- Sheet: `analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric_sheet.jpg`
- Decision: `future_source_scoring_rubric_created_no_selector_unlocked`

## R1-R5 Rubric

| gate | name | blocking | current baseline | pass threshold |
|---|---|---:|---|---|
| `R1` | source identity | `True` | Current workspace and Desktop magazine.pdf are byte-identical; current local source set has zero actionable unknowns. | Physical scan/photo, native layout export, browser/source asset, or raw clue source with provenance that is not only a resave of the current PDF. |
| `R2` | target preservation | `True` | Active targets: O5 'shitcoiner at heart', G5 'Volcano Bonds', L26 future bitcoin earnings; crop pack has five line/context panels. | O5 and G5 are readable/locatable, plus at least one context band from L25-L32 is visible enough to compare against the crop pack. |
| `R3` | unit/order evidence | `True` | Active unlock matrix checks 8 paths; all 8 fail R3. Existing raw-like clue intake has zero R3 passes. | Source-backed wording or layer metadata names word, letter, line, edge, font, first/last, left/right, fold, mirror read direction, page/order, key/private format, or equivalent. |
| `R4` | orientation discipline | `True` | 3D/crop layer is readable/upright; source_images and fresh PDF extraction are native upside-down and need rotate180. | New material states/readably shows orientation; comparisons are made in upright coordinates or with documented 180-degree rotation. |
| `R5` | controlled improvement | `True` | C2 is partial: p78 frame clips O5, cuts M3, and is 38px from G5; dx -38/-40 repairs tri-contact but remains registration evidence only. | Natural source registration preserves/explains O5 bottom contact, M3 right-edge cut, and G5 edge repair, or creates repeated direct O5/G5 physical contacts. |

## Numeric Benchmarks

- p78 current frame: `[1234.0, 2398.0, 2250.0, 2950.0]`
- p78 current G5 gap: `38.0` px
- p78 current M3 right-edge overlap: `265.0` px
- p78 current O5 overlap vs target: `0.24754`
- p78 repair frame: `[1194.0, 2398.0, 2210.0, 2950.0]` with dx `-40.0` and tri-contact pass `True`
- p77 baseline vertical near-miss gap: `71.93` px
- p77 median lower-corridor line pitch: `73.73` px

## Extraction Gate

- Allow extraction only if: R1, R2, R3, R4, and R5 all pass on the same new source/clue item, with R3 providing a source-backed unit/order.

Block extraction if:
- R3 is absent, even if target geometry improves.
- material is only a duplicate/resaved current scan.
- orientation is ambiguous or mixed between upright/native coordinates.
- geometry requires arbitrary shifts not explained by source/physical evidence.

First allowed actions after a full pass:
- transcribe exact selected unit/order
- run one low-parameter extraction following the source-backed rule
- only then test checksum-valid key-like output or address activity

## Next Move

- Use this rubric together with the source-acquisition packet when new physical/original-layout/raw clue material appears. Do not resume extraction from the current scan.
