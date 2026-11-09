# Max Article Layout Comparison

Scope: compare user-provided Max article PDFs against the Issue 24 puzzle scan as visual/layout witnesses. These PDFs are image-only, so this pass uses embedded page images and color/layout metrics, not text OCR.

## Sources

### Issue 24 / BITCOIN IS TOXIC AF

- path: `magazine.pdf`
- MD5: `2c454d800cf2971c1f86fd016f64b7a0`
- pages: `8`
- note: puzzle source, best local scan
- contact sheet: `analysis_outputs/comparison_articles/issue24_toxic_af/contact_sheet.jpg`
- page metrics:
  - p01: image `2544x3264`, orange/yellow/cyan/magenta `0.237/0.114/0.0/0.0%`, dark/white `0.0/61.707%`, colorScore `0.245%`
  - p02: image `2544x3264`, orange/yellow/cyan/magenta `0.018/0.017/0.0/0.0%`, dark/white `0.0/26.234%`, colorScore `0.021%`
  - p03: image `2544x3264`, orange/yellow/cyan/magenta `1.958/0.268/0.0/0.0%`, dark/white `2.073/87.173%`, colorScore `1.969%`
  - p04: image `2544x3264`, orange/yellow/cyan/magenta `1.423/0.197/0.0/0.0%`, dark/white `2.125/87.991%`, colorScore `1.442%`
  - p05: image `2544x3264`, orange/yellow/cyan/magenta `0.807/0.185/0.0/0.0%`, dark/white `86.084/3.065%`, colorScore `0.832%`
  - p06: image `2544x3264`, orange/yellow/cyan/magenta `1.672/0.254/0.0/0.0%`, dark/white `4.221/87.06%`, colorScore `1.694%`
  - p07: image `2544x3264`, orange/yellow/cyan/magenta `2.493/0.463/0.0/0.0%`, dark/white `1.812/88.458%`, colorScore `2.523%`
  - p08: image `2544x3264`, orange/yellow/cyan/magenta `22.214/21.693/0.0/26.979%`, dark/white `0.0/1.591%`, colorScore `49.344%`

### Issue_26.pdf

- path: `private_inputs/Desktop/Issue_26.pdf`
- MD5: `d03964451f5ebcdf54ee3b43b0de8d80`
- pages: `5`
- note: user-provided comparison article
- contact sheet: `analysis_outputs/comparison_articles/issue26/contact_sheet.jpg`
- page metrics:
  - p01: image `2040x2805`, orange/yellow/cyan/magenta `0.0/0.0/0.0/0.0%`, dark/white `4.651/0.837%`, colorScore `0.0%`
  - p02: image `2040x2805`, orange/yellow/cyan/magenta `0.043/0.004/0.0/0.001%`, dark/white `4.192/0.176%`, colorScore `0.047%`
  - p03: image `2040x2805`, orange/yellow/cyan/magenta `0.218/0.001/0.0/0.025%`, dark/white `1.769/0.041%`, colorScore `0.218%`
  - p04: image `2040x2805`, orange/yellow/cyan/magenta `0.613/0.002/0.0/0.028%`, dark/white `1.838/0.163%`, colorScore `0.621%`
  - p05: image `2040x2805`, orange/yellow/cyan/magenta `0.196/0.0/0.0/0.011%`, dark/white `0.844/0.149%`, colorScore `0.196%`

### bitcoin3.pdf

- path: `private_inputs/Desktop/bitcoin3.pdf`
- MD5: `fc8aad04fe91f78f26a9c2241a26a7dc`
- pages: `8`
- note: user-provided comparison article
- contact sheet: `analysis_outputs/comparison_articles/bitcoin3/contact_sheet.jpg`
- page metrics:
  - p01: image `2040x2805`, orange/yellow/cyan/magenta `0.0/0.0/0.0/0.958%`, dark/white `2.612/0.193%`, colorScore `0.958%`
  - p02: image `2040x2805`, orange/yellow/cyan/magenta `0.001/0.006/0.015/0.238%`, dark/white `3.751/0.259%`, colorScore `0.259%`
  - p03: image `2040x2805`, orange/yellow/cyan/magenta `0.001/0.001/0.0/0.244%`, dark/white `3.158/0.192%`, colorScore `0.245%`
  - p04: image `2040x2805`, orange/yellow/cyan/magenta `0.001/0.007/0.082/0.38%`, dark/white `3.056/0.159%`, colorScore `0.469%`
  - p05: image `2040x2805`, orange/yellow/cyan/magenta `0.0/0.0/0.0/0.403%`, dark/white `5.007/0.191%`, colorScore `0.403%`
  - p06: image `2040x2805`, orange/yellow/cyan/magenta `0.002/0.004/0.007/0.021%`, dark/white `1.957/1.261%`, colorScore `0.032%`
  - p07: image `2040x2805`, orange/yellow/cyan/magenta `9.312/6.594/0.192/0.325%`, dark/white `0.0/0.337%`, colorScore `10.149%`
  - p08: image `2040x2805`, orange/yellow/cyan/magenta `25.149/17.897/10.31/9.086%`, dark/white `0.175/0.243%`, colorScore `45.12%`

## Closest Coarse Visual Matches

These are average-hash matches only. They help spot reused page composition, not proof of puzzle relation.
- puzzle p08 ↔ bitcoin3 p04: hamming `33`, colorDelta `48.875`, darkDelta `3.056`
- puzzle p08 ↔ issue26 p05: hamming `36`, colorDelta `49.148`, darkDelta `0.844`
- puzzle p02 ↔ issue26 p04: hamming `37`, colorDelta `0.6`, darkDelta `1.838`
- puzzle p08 ↔ issue26 p02: hamming `40`, colorDelta `49.297`, darkDelta `4.192`
- puzzle p02 ↔ issue26 p02: hamming `41`, colorDelta `0.026`, darkDelta `4.192`
- puzzle p08 ↔ bitcoin3 p05: hamming `41`, colorDelta `48.941`, darkDelta `5.007`
- puzzle p02 ↔ bitcoin3 p04: hamming `44`, colorDelta `0.448`, darkDelta `3.056`
- puzzle p08 ↔ issue26 p04: hamming `44`, colorDelta `48.723`, darkDelta `1.838`
- puzzle p02 ↔ bitcoin3 p05: hamming `46`, colorDelta `0.382`, darkDelta `5.007`
- puzzle p03 ↔ issue26 p01: hamming `47`, colorDelta `1.969`, darkDelta `2.578`
- puzzle p05 ↔ issue26 p01: hamming `50`, colorDelta `0.832`, darkDelta `81.433`
- puzzle p04 ↔ bitcoin3 p06: hamming `50`, colorDelta `1.41`, darkDelta `0.168`

## Preliminary Assessment

- The two comparison PDFs use the same 2040 x 2805 embedded JPEG page format as the public/OCR article PDF branch, not the 2544 x 3264 best-scan geometry of `magazine.pdf`.
- The comparison set should help separate recurring Max/OVERDOSE layout conventions from article-specific puzzle marks.
- Any motif appearing across these comparison articles, especially orange/yellow highlights or large black editorial blocks, should be downgraded as house style unless it interacts with the page-76 mirror geometry.
- Any motif unique to Issue 24, especially the p76/p79 mirror corridor, p80 package-copy system, cyan `MNBILLION`, or page-76 Bukele/IMF/$1 billion cluster, remains higher priority.

## Manual Visual Review

- `Issue_26.pdf` appears to be a different Max/Keiser feature with a red/black censorship/redaction visual system.
  - It has large red typography and red emphasis marks, but not the Issue 24 orange highlighter plus grey/black highlighted text grammar.
  - It does not show the Issue 24 medicine-bottle/package-copy ending, five-symptom label, pill-count system, or page-76/page-79 mirror-compatible X/barbed-wire/pill cluster.
  - This downgrades generic black bars/redaction as house/editorial style, but does not downgrade the specific Issue 24 orange/grey highlight mirror system.
- `bitcoin3.pdf` is an OVERDOSE/Max comparison article with strong pink/blue/funk visual art.
  - It confirms that OVERDOSE articles commonly use loud, issue-specific art, full-page color end art, Max portraits, and large display typography.
  - Its text pages are mostly dark/colored editorial spreads, not the same orange/grey highlighted article-text system used in `BITCOIN IS TOXIC AF`.
  - It has no matching medicine-bottle/five-symptom packaging system and no obvious p76/p79-style reflected text corridor.
- Shared/common features:
  - OVERDOSE/Max branding.
  - Issue-specific collage/graphic language.
  - Occasional large blocks, high-contrast pages, and bold display type.
- More unique to Issue 24 among this local comparison set:
  - repeated orange article-text highlights paired with grey/black highlights;
  - medicine/pill/toxicity packaging system;
  - p80 `5 SYMPTOM RELIEF` label and five symptom list;
  - p76 Bukele/IMF/`$1 billion` corridor;
  - page 76/79 mirror/fold visual system with X/barbed-wire/pill/dollar context.

## Consequence For The Puzzle

- Treat broad OVERDOSE branding and loud Max collage art as background style.
- Treat the Issue 24 medicine/highlight/mirror system as still puzzle-specific enough to keep investigating.
- The comparison articles do not provide a new selector. They mainly rule out the idea that every strange visual mark in Issue 24 is automatically unique.
