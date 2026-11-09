# 3D Viewer Correction Alignment

Scope: align corrected canonical transcript lines to the 3D viewer OCR line model. No key derivation, hashing, seed phrases, WIF checks, or address checks were run.

- Created: `2026-05-20T09:32:28`
- Canonical lines: `147`
- Viewer OCR lines: `161`
- High-confidence preload lines: `101`
- Usable but not preloaded lines: `25`
- Weak matches: `13`
- Safe global preload: `False`

## Page Summary

| page | canonical | viewer | matches | high | usable | weak |
|---|---:|---:|---:|---:|---:|---:|
| p75 | 33 | 31 | 31 | 26 | 5 | 0 |
| p76 | 31 | 36 | 31 | 24 | 5 | 2 |
| p77 | 32 | 33 | 29 | 22 | 4 | 3 |
| p78 | 26 | 30 | 25 | 14 | 5 | 6 |
| p79 | 25 | 31 | 23 | 15 | 6 | 2 |

## Notable Extra Viewer Rows

### p76
- `p76l0`: `OVERDOSE`
- `p76l16`: `Salvador`
- `p76l19`: `|`
- `p76l20`: `Magazine`
- `p76l21`: `Bitcoin`

### p77
- `p77l4`: `aA este) stat rat`
- `p77l15`: `> -=`
- `p77l16`: `= rc)`
- `p77l32`: `DEA SE-B 1a Grol MMos sa iF`

### p78
- `p78l0`: `OVERDOSE`
- `p78l15`: `Salvador`
- `p78l19`: `Magazine`
- `p78l21`: `Bitcoin`
- `p78l27`: `aa peste aed`

### p79
- `p79l10`: `of being poor because the fear`
- `p79l13`: `Sea of billions of in a cyber`
- `p79l17`: `s`
- `p79l18`: `= &`
- `p79l19`: `x 5`
- `p79l20`: `= ®`

## Weak Match Examples

### p76
- `p76l14` score `0.5`: canonical `by the rancid catnip of fiat money. Fortunately, bitcoin` vs viewer `¥ortunately, bitcoin`
- `p76l17` score `0.6296`: canonical `laundering lobotomy. It's a stun gun to the genitals.` vs viewer `AE-hbbelel-nabetomolomomea lcs &2 Stun gun to the genitals.`

### p77
- `p77l3` score `0.5931`: canonical `a day to a mind-bending 100,000 and growing. At this rate, the whole` vs viewer `aday toa mind-bending 100,000 and se Se) Bb aye G a Reb We a-ha ME dele a Sten r =`
- `p77l28` score `0.6504`: canonical `And as bitcoin starves shitcoins, fiat and gold to death,` vs viewer `PU oCCUr: twa obaelonO OMEN hant{ sts shitcoins, fiat and gold to death,`
- `p77l30` score `0.6909`: canonical `the state itself. It does this by monetizing, for the first` vs viewer `Leta mamaee 1v does this by monetizing, ites the first`

### p78
- `p78l10` score `0.6261`: canonical `and requires money printing and wars to keep it going - all in` vs viewer `pelompacepema-mmoney printing Ememwars to eeeeNg — all in`
- `p78l13` score `0.5`: canonical `BILLION worth of hate toys in Afghanistan, for example, for a war` vs viewer `any for gnample: for a war`
- `p78l14` score `0.6329`: canonical `that some estimate cost $2 trillion fiat cuck-bucks.` vs viewer `that some estimate cost Suez`
- `p78l23` score `0.6353`: canonical `It's a fact baked into the game-theorized Bitcoin protocol,` vs viewer `It's a fact baked into @ nrot`
- `p78l24` score `0.6389`: canonical `observable by anyone choosing to see it,` vs viewer `cbasrene ee anyone ees to see otk.`

### p79
- `p79l5` score `0.6186`: canonical `drops by 95% or more. That's right, Bitcoin will take` vs viewer `drops by 95% or more. IAs inteba toons Iebaices`
- `p79l16` score `0.5957`: canonical `of peace is the same as a smile - virtually nothing.` vs viewer `ro |e r™~. of VARI NESSES pMlle — virtually nothing.`

## Assessment

- Global automatic correction preload is unsafe: the viewer line model includes extra visual/OCR rows and some article rows are missing, split, or shifted.
- High-confidence matches are suitable as a review aid, not as silent replacement.
- The existing investigation rule still stands: high-res scan for geometry, corrected DOCM/plain text for wording, 3D viewer only for navigation and manual review.

## Next Move

- If the viewer is improved, add an optional high-confidence import/review step rather than replacing every OCR line automatically.
