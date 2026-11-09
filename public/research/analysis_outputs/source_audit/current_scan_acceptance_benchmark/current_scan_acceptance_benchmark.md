# Current Scan Acceptance Benchmark

Scope: score the current canonical scan against the refreshed C1-C9 source-registration benchmark. No key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T12:09:59`
- Status counts: `PASS=2`, `PARTIAL=4`, `FAIL=3`
- Blocking constraints: `C2, C3, C4, C5, C6, C7, C8`
- Independent comparison five-sequence hits: `0`
- Lower-res Issue 24 witness five-sequence hits: `2`

## C1-C9 Dry Run

| id | status | current scan evidence | blocks extraction | future improvement needed |
|---|---|---|---|---|
| C1 | `PASS` | Trusted page-76 O5/G5 crop geometry is available and source-faithful. | `False` | Only if a future source gives cleaner manual boxes. |
| C2 | `PARTIAL` | p78 frame signature exists, including G5 near-edge and O5 bottom/left clip, but remains a registration signature. | `True` | Independent physical/source layer should explain the same p78->p76 contact naturally. |
| C3 | `FAIL` | No source-backed word/letter/line/edge/font unit or ordering rule has been found. | `True` | A clue/source must name the extraction unit before any key checks resume. |
| C4 | `FAIL` | Current physical leaf/spread models produce total direct trusted O5/G5 overlaps=0. | `True` | A true physical scan/photo should improve front/back, spread, fold, or bleed-through behavior. |
| C5 | `PARTIAL` | Issue 24 and bitcoin4 witness preserve the five-capsule sequence; independent comparison sequence hits=0. | `True` | Need a source rule that maps the capsule chain to a text/selector unit. |
| C6 | `PARTIAL` | Five repeats across p73/p79/p80/p76; p73/p79 step signature is RRLL and p79-p73 offsets are [5, 5, 5, 5, 5]; instruction hits=none. | `True` | Need source/clue wording that explains how five selects a word, letter, edge, or font state. |
| C7 | `PARTIAL` | Announcement/media evidence points to page-76 Bukele/volcano/IMF corridor, but does not add unit/order. | `True` | Need exact media-order or source instruction beyond target confirmation. |
| C8 | `FAIL` | Canva remains a low-resolution investigator note board, not geometry truth. | `True` | Need original embedded Canva assets, higher-resolution export, browser capture, or physical source image. |
| C9 | `PASS` | Desktop/project PDF are byte-identical=True; source-to-3D transform is rotate180; priority crop RMS range=1.132865 to 2.070533. | `False` | Always compare future source material in matching orientation. |

## Decision

- The current scan is a valid baseline and target/provenance witness, but extraction remains blocked by C3/C4/C8 and partial C2/C5/C6/C7.

## Next Move

- Future sources must improve at least one blocked constraint, especially C3 extraction unit or C4/C8 source quality, before any key-candidate work resumes.
