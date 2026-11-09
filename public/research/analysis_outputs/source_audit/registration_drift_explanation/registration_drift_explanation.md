# Registration Drift Explanation Audit

Scope: check whether the p78->p76 `dx=-38/-40` repair is likely ordinary source/page drift. No key derivation was run.

- Created: `2026-05-20T09:08:57`
- Current high-res G5 gap before repair: `38.0 px`
- Tri-contact repair: edge-touch dx `-38.0 px`, nearest grid dx `-40.0 px`
- Stability window: dx `[-78, -38]`, dy `[-4, 20]`, count `1025`

## Witness Comparison

| witness | measurement | value | implication |
|---|---|---|---|
| magazine.pdf embedded page placement | per-page image offset/scale drift | `0 pt gaps; one full-bleed image per page` | does not explain dx=-38/-40 |
| alternate OCR/Google p79 pill geometry | affine residual after mapping to high-res p79 | `mean 0.31 px, max 0.45 px` | alternate p79 has same pill geometry after affine normalization |
| bitcoin4.pdf p76/p78 low-res transforms | page transform residuals | `p76 mean 3.618 px; p78 mean 4.595 px` | low-res source has page-specific distortion, but not a useful repair |
| bitcoin4.pdf natural p78->p76 geometry | reflected frame gap to trusted G5 | `84.098 low-res px (~105.619 high-res px)` | worse than current high-res G5 gap, so it does not validate the dx repair |
| current high-res p78 frame | gap to trusted G5 before repair | `38.0 px` | the only coherent repair is local dx about -38/-40 |
| p78 frame tri-contact repair | dx needed to touch G5 while preserving M3/O5 contact | `edge-touch dx -38.0 px; nearest grid dx -40.0 px` | use as a benchmark for future sources, not as extraction |
| repaired exact-edge stability window | dx/dy cells satisfying exact trio plus tri-contact | `dx [-78, -38], dy [-4, 20], count 1025` | stable local signature, but still no extraction unit |

## Assessment

- The dx=-38/-40 repair is not explained by hidden placement inside magazine.pdf; page placement is uniform.
- The alternate OCR/Google PDF preserves the p79 pill geometry after affine normalization and does not supply a new global offset.
- The low-res bitcoin4.pdf witness has page-specific distortion, but its natural p78->p76 geometry makes the G5 gap worse, not better.
- So ordinary source/page drift is a weak explanation for dx=-38/-40 under currently available files.
- The repair remains useful only as a source-registration benchmark; it still does not name an extraction unit.

## Next Move

- Do not treat dx=-38/-40 as a solved physical correction. Keep it as a benchmark for future physical/Canva/original-layout imagery, and only resume extraction if a new source also names the unit to read.
