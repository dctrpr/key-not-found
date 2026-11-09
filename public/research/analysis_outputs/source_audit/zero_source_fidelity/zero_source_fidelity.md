# Zero / #0 Source-Fidelity Audit

Scope: inventory zero-bearing numeric tokens across local text witnesses. This does not generate keys or treat zeros as key material.

## Canonical Page Rows

- p75 L3: `2008` zeros=2 context `to the Global Financial Crisis of 2008. It caused it.`
- p76 L7: `10` zeros=1 context `nonsense (and 10 years of watching Peter Schiff miss buying bitcoin`
- p76 L8: `2011` zeros=1 context `since I started honey-badgering him to buy some at $1 back in 2011)`
- p77 L2: `20,000` zeros=4 context `Jack Mallers' Strike app nas gone from 20,000 new sign-ups`
- p77 L3: `100,000` zeros=5 context `a day to a mind-bending 100,000 and growing. At this rate, the whole country will be Toxic Bitcoin Maximalists within six months. (Sorry Bhutan, you fell for that snake oil salesmen over at XRP.          Get ready to experience shitcoin hell.`
- p77 L7: `2017` zeros=1 context `Size War of 2017 and it's been going downhill ever since.`
- p77 L13: `12,000` zeros=3 context `EVERY SINGLE ONE OF THE BITCOIN WANNABES — BCH, BSV, ETH, XRP, ADA, AND 12,000 OTHER SHITCOINS, PLUS FIAT MONEY AND GOLD — IS FACING THE IGNOMINIOUS`
- p79 L10: `10` zeros=1 context `Stacy and I have been living in here for 10 years`

## Witness Differences Vs Canonical Body

### canonical_with_signature [ok]
- token count: `8`
- missing: `{}`
- extra: `{}`

### user_plain_latest [ok]
- token count: `8`
- missing: `{}`
- extra: `{}`

### user_annotated_transcript [DIFF]
- token count: `9`
- missing: `{'10': 1, '100,000': 1}`
- extra: `{'10years': 1, '1000,000': 1, '0': 1}`

### user_markdown_transcript [DIFF]
- token count: `8`
- missing: `{'10': 1}`
- extra: `{'0': 1}`

### article_with_fonts_text [ok]
- token count: `8`
- missing: `{}`
- extra: `{}`

### full_article [DIFF]
- token count: `8`
- missing: `{'10': 1}`
- extra: `{'10years': 1}`

### full_article_corrected [DIFF]
- token count: `8`
- missing: `{'10': 1}`
- extra: `{'10years': 1}`

## Visual Check Hotspots

- score 12 p77 L3 `100,000`: a day to a mind-bending 100,000 and growing. At this rate, the whole country will be Toxic Bitcoin Maximalists within six months. (Sorry Bhutan, you fell for that snake oil salesmen over at XRP.          Get ready to experience shitcoin hell.
- score 11 p77 L2 `20,000`: Jack Mallers' Strike app nas gone from 20,000 new sign-ups
- score 10 p77 L13 `12,000`: EVERY SINGLE ONE OF THE BITCOIN WANNABES — BCH, BSV, ETH, XRP, ADA, AND 12,000 OTHER SHITCOINS, PLUS FIAT MONEY AND GOLD — IS FACING THE IGNOMINIOUS
- score 7 p75 L3 `2008`: to the Global Financial Crisis of 2008. It caused it.
- score 6 p76 L8 `2011`: since I started honey-badgering him to buy some at $1 back in 2011)
- score 6 p77 L7 `2017`: Size War of 2017 and it's been going downhill ever since.
- score 4 p76 L7 `10`: nonsense (and 10 years of watching Peter Schiff miss buying bitcoin
- score 4 p79 L10 `10`: Stacy and I have been living in here for 10 years

## Assessment

- The strongest local discrepancy is `1000,000` in the user annotated transcript versus canonical `100,000` in the corrected witnesses.
- That makes `100,000` the first zero token to visually inspect if the exact browser/PDF view or higher-resolution Canva/original image is recovered.
- Other high-value zero checks are `20,000`, `12,000`, the years `2008` / `2011` / `2017`, and both `10 years` references.
- This closes local zero inventory as a source-fidelity checklist. It does not supply a selector or justify key generation.

## Next Best Move

- With a new visual source: compare these zero hotspots first, then rerun only the affected page-registration or text-mapping pass.
