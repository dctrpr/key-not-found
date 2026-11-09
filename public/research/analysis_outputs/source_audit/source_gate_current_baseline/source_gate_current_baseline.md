# Source Gate Current-Baseline Dry Run

Scope: run the source-validation gate against the current canonical `magazine.pdf` baseline. No key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T10:26:46`
- Project md5: `2c454d800cf2971c1f86fd016f64b7a0`
- Desktop md5: `2c454d800cf2971c1f86fd016f64b7a0`
- Byte-identical desktop/project scan: `True`

## Gate Results

| gate | status | evidence | block |
|---|---|---|---|
| `source_quality` | `pass_baseline` | Project magazine.pdf md5=2c454d800cf2971c1f86fd016f64b7a0; desktop copy md5=2c454d800cf2971c1f86fd016f64b7a0; byte-identical=True. PDF placement report says full-bleed single 2544x3264 image per page. | - |
| `page76_priority_crops` | `pass_baseline` | 5/5 priority crops exist; O5/G5/frame context are baseline-visible. | - |
| `zero_hash0_hotspots` | `pass_baseline` | 8/8 trusted high-res zero/#0 crops exist; p77 baseline reads 100,000. | - |
| `p79_pill_geometry` | `pass_baseline` | Trusted p79 lower-left pill-fragment count is 5; alternate OCR/PDF witness also normalizes to five fragments but is not geometry truth. | - |
| `p78_frame_exact_edge` | `pass_baseline` | Repaired signature `should sell / Volcano Bonds / shitcoiner at heart` / `RKY`; exact+tri-contact stable dx=[-78, -38] dy=[-4, 20]; edge-touch frame=[1196.0, 2398.0, 2212.0, 2950.0]. | - |
| `extraction_permission` | `blocked` | No current-source or raw external clue names the extraction unit/order. | Need explicit unit/order such as word, letter, line, edge, font state, first/last, or a new source geometry change that supplies one. |

## Decision

- Current scan passes as canonical baseline, but extraction remains blocked. A future source must change/confirm benchmark geometry or name the extraction unit before key checks resume.

## Next Move

- Use this dry-run as the expected baseline comparison for any future physical/original-layout/source material.
