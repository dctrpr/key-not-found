# Registered 76/79 Gap-Recurrence Audit

Scope: test whether the `between the lines` geometry from the strongest p79/p76 anchor recurs across other registered p79 highlight boxes and page-76 highlight rows. OCR words are labels only; no key derivation was run.

## Summary

- Registered p79 sources checked: 10
- Sources with OCR words: 4
- Sources with two-row gaps: 3
- Candidate target-row/gap comparisons: 30
- Strong recurrences (abs delta <= 12 px and target coverage >= 10%): 1

## Strong Recurrences

- p79 box 1 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` gap mid y=859.5 -> p76 black 1 `Gotta be this way... post-1971 fiat money` row y=854.5 delta=-5.0 px, targetCoverage=0.770
  - between `efficient: more infinitely is bitcoin because — love` / `while even consumption, energy overall the — ORMBONG`
  - target row `Gotta be S way. Forty years of dumb post-1971 flat money`

## Nearest Rows

- delta=-5.0 px cov=0.770: p79 1 -> p76 black 1 `Gotta be S way. Forty years of dumb post-1971 flat money`
- delta=62.0 px cov=0.113: p79 1 -> p76 black 2 `RRECECy`
- delta=-187.3 px cov=0.000: p79 2 -> p76 black 2 `RRECECy`
- delta=-193.8 px cov=0.000: p79 3 -> p76 black 2 `RRECECy`
- delta=-254.3 px cov=0.000: p79 2 -> p76 black 1 `Gotta be S way. Forty years of dumb post-1971 flat money`
- delta=-260.8 px cov=0.000: p79 3 -> p76 black 1 `Gotta be S way. Forty years of dumb post-1971 flat money`
- delta=397.4 px cov=0.000: p79 3 -> p76 black 3 `AE-hbbelel-nabetomolomomea lcs &2 Stun gun to the genitals.`
- delta=-398.4 px cov=0.000: p79 1 -> p76 orange 2 `Biteoiny`
- delta=403.9 px cov=0.000: p79 2 -> p76 black 3 `AE-hbbelel-nabetomolomomea lcs &2 Stun gun to the genitals.`
- delta=-464.9 px cov=0.000: p79 1 -> p76 orange 1 `Get some toxicity. Get some bitcoin. Open your heart to`
- delta=-647.7 px cov=0.000: p79 2 -> p76 orange 2 `Biteoiny`
- delta=653.2 px cov=0.000: p79 1 -> p76 black 3 `AE-hbbelel-nabetomolomomea lcs &2 Stun gun to the genitals.`

## Source Row/Gaps

- p79 box 1 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold` words=16
  - row y=785.0: `efficient: more infinitely is bitcoin because — love`
  - row y=934.1: `while even consumption, energy overall the — ORMBONG`
  - gap mid=859.5 height=149.1
- p79 box 2 `That's right, Bitcoin will take all the energy.` words=8
  - row y=1069.1: `Iebaices toons inteba IAs`
  - row y=1148.4: `consumption energy our doing,`
  - gap mid=1108.8 height=79.3
- p79 box 3 `all the energy.` words=6
  - row y=1075.3: `more. or 95%`
  - row y=1155.3: `so In SlhSIeneREY`
  - gap mid=1115.3 height=80.0
- p79 box 4 `Everyone will live their own experience in the rabbit hole.` words=10
  - row y=2261.9: `holer rabbit the in experience own their Live will Everyone`

## Assessment

- Under the strict recurrence filter, the only strong `between the lines` hit is the already-known p79 box 1 -> p76 grey B1 alignment.
- Other p79 boxes do have two OCR rows after transformation, but their gap midpoints do not coincide with page-76 target rows that also have meaningful box overlap.
- This makes the p79 box 1 / p76 B1 anchor a unique high-quality registration marker in the current 76/79 transform, not a repeated ordered sequence.
- Next best move: treat this anchor as a calibration marker, then look for a separate ordering/instruction clue from the Canva/source clue or from unique visual marks.
