# Source Registration Acceptance Test

Scope: consolidate active geometry/source constraints into a pass/fail benchmark. No key derivation was run.

- Created: `2026-05-20T12:07:07`

## Constraints

| id | name | status | requirement | current evidence | acceptance test |
|---|---|---|---|---|---|
| C1 | trusted source boxes | `PASS` | Use trusted high-res O5 and corrected trusted G5, not stale projected p76_grey_5 geometry. | Trusted O5/G5 are now fixed: O5 [1040,2932,1661,2982], G5 [795,2544,1196,2592]. | Any future source transform must report target boxes against these trusted units or a clearly better manual source. |
| C2 | p78 frame signature | `PARTIAL` | Explain current O5 bottom/left clip, trusted G5 38px near-edge relation, and the dx=-40 repair without arbitrary local fitting. | Current O5 overlap=0.24754; G5 gap=38.0px; nearest simultaneous repair dx=-40, dy=0. | A valid source registration should naturally make this signature coherent while preserving the same corridor. |
| C3 | extraction unit | `FAIL` | Name a word, letter, line, edge, pixel, font-state, or ordering unit before any key derivation. | Gap-repaired p78 streams produce instruction hits: none. | Must produce a human-readable instruction or checksum-valid compact key-like unit from a rule that follows from source/clue evidence. |
| C4 | physical leaf/spread support | `FAIL` | True physical page relationships should improve, not degrade, O5/G5 targeting. | Current best-scan physical models have total trusted O5/G5 direct overlaps=0. | A physical scan/photo should show real front/back, spread, bleed-through, or fold behavior that selects the corridor. |
| C5 | opener capsule provenance | `PARTIAL` | Preserve the real p73->p79 five-capsule artwork reuse while avoiding loose forced M3/M4 assignment. | Current endpoint sequence=M3M3M4M4M4; tight <=75px assigns 1/5, <=150px assigns 2/5. | A new transform should place all five ordered capsules tightly on text/selector units, or provide an explicit clue for M3/M4 binary/index use. |
| C6 | five-index locator | `PARTIAL` | Preserve the repeated five system without treating five, RRLL, or 1100 as key material by itself. | Five repeats across p73/p79/p80/p76; p73/p79 step signature=RRLL / RRLL; p79-p73 offsets=[5, 5, 5, 5, 5]; instruction hits=none. | A future source/clue must explain how five selects a unit such as word/letter/edge/font before extraction resumes. |
| C7 | announcement media coverage | `PARTIAL` | Use public media sequence as target confirmation, not overclaim it as exact order. | Media order unique page-76 initials=PpvV; missing units=buying_dip, one_billion, imf_loan. | Future use of media must add a new exact unit/order not already covered by page-76 Bukele/volcano targeting. |
| C8 | Canva/source image quality | `FAIL` | Do not use the 668x376 Canva thumbnail as geometry truth. | Current Canva witness is thumbnail-scale ([668, 376]) and documented as an investigator note board. | Need original embedded assets, higher-resolution export, browser screenshot, or physical source image. |
| C9 | orientation/source cache bridge | `PASS` | Compare future source images in the correct orientation before judging geometry. | Current 3D/readable layer matches source/PDF after `rotate180`; priority crop RMS range=1.132865 to 2.070533. | Use readable/upright geometry or rotate native source/PDF images 180 degrees before applying page-76 crop coordinates. |

## Witness Verdicts

| witness | status | verdict |
|---|---|---|
| current best high-res magazine.pdf | `PARTIAL` | Good for target discovery and source provenance; insufficient for precise extraction. |
| current p78 dx=-40 local repair | `FAIL_AS_SELECTOR` | Useful only as a future registration signature; it does not change the instruction-free phrase stream. |
| Canva 668x376 note board | `FAIL_GEOMETRY_TRUTH` | Orientation/provenance clue only; too small and secondary for measurement. |
| announcement media sequence | `PARTIAL` | Confirms page 76/Bukele/volcano area, but not exact order or unit. |
| future physical/source scan | `REQUIRED_NEXT` | Highest-value missing evidence: must be tested against C1-C9 before new extraction. |

## Decision

- Do not promote new local geometry streams unless they pass C2/C3 and explain C6; current local sources fail the extraction-unit requirement.

## Next Move

- Acquire or inspect a better source image/physical scan, then score it against this benchmark before extracting words/letters.
