# Numerical claim: traceable reconstruction and finite result

A source-faithful body-only rule produces exactly **256 bits**, but none of its four declared mirror forms has activity across the five standard address types checked. The community’s alternate264-bit count can also be reproduced by a different ordinary serialization. Neither count establishes an intentional encoding.

## The exact256-bit rule

Read all142 printed body lines on pages75–79 in source order. Take every digit-written numerical magnitude, interpret the explicit monetary scales normally, and include the spelled finite quantity words **Forty**, **six**, and **zero**. Convert each resulting integer to its shortest binary representation, with zero represented by one`0`bit. Concatenate the representations in printed order.

This yields21 digit-bearing values plus3 spelled quantities =24 values. The digit-bearing full-scale values contribute246 bits; Forty contributes6, six contributes3, and zero contributes1: **246+6+3+1=256**. The rule was applied without trimming, target-length padding, modulo, salting, or hashing.

| Event | Source line | Printed token / scale | Integer value | Bits |
|---|---|---|---:|---:|
| n01 | p75r02 | 2008 | 2008 | 11 |
| n02 | p75r17 | 1 | 1 | 1 |
| n03 | p75r18 | 1 | 1 | 1 |
| n04 | p75r27 | 1 | 1 | 1 |
| n05 | p76r07 | Forty | 40 | 6 |
| n06 | p76r07 | 1971 | 1971 | 11 |
| n07 | p76r08 | 10 | 10 | 4 |
| n08 | p76r09 | 1 | 1 | 1 |
| n09 | p76r09 | 2011 | 2011 | 11 |
| n10 | p76r24 | 1 billion | 1000000000 | 30 |
| n11 | p77r01 | 42 | 42 | 6 |
| n12 | p77r03 | 20,000 | 20000 | 15 |
| n13 | p77r04 | 100,000 | 100000 | 17 |
| n14 | p77r05 | six | 6 | 3 |
| n15 | p77r10 | 2017 | 2017 | 11 |
| n17 | p77r19 | 12,000 | 12000 | 14 |
| n19 | p77r24 | 51 | 51 | 6 |
| n21 | p78r12 | 85 BILLION (scale on p78r13) | 85000000000 | 37 |
| n22 | p78r14 | 2 trillion | 2000000000000 | 41 |
| n23 | p79r06 | 51 | 51 | 6 |
| n24 | p79r07 | 95 | 95 | 7 |
| n25 | p79r09 | zero | 0 | 1 |
| n27 | p79r19 | 1969 | 1969 | 11 |
| n28 | p79r22 | 10 | 10 | 4 |

## Choices that matter

- `$1 billion` is1,000,000,000. `$85` at the end of p78r12 is continued by `BILLION` at the start of p78r13, giving85,000,000,000. `$2 trillion` is2,000,000,000,000. There is no explicit million in this body.
- The pronoun`ONE` in`EVERY SINGLE ONE OF` is excluded from the quantity-cardinal rule. Including it gives257 bits.
- Three occurrences of ordinal`first` are excluded. Including those alone gives259 bits; including them and pronoun`ONE` gives260 bits. These distinctions are disclosed because they make the256-bit coincidence interpretation-sensitive.
- The plural`billions` occurs twice without a finite mantissa. It has no determinate integer value and is separately inventoried.
- Percent signs retain their printed integer magnitude:42,51,95. Treating them as exact fractions of100 yields nonterminating binary expansions for these values, not finite minimal integer bit strings.
- Commas are thousands separators in20,000 /100,000 /12,000. No decimal point occurs in these body numbers.
- The rule concerns body text only. Printed page folios, medicine-package art, opener currency art and bill serial numbers are different source scopes; they are not silently included or selectively removed.

## A possible264-bit reconciliation

[Private context omitted from this public copy.]

Thirty small declared representation variants (five linguistic scopes ×three scale treatments ×two binary serializations) were counted offline. Exactly one gives256 bits and one gives264 bits. Only the above256-bit rule was promoted to direct-key activity checking. No variant was trimmed or reduced to make it fit.

## Direct check, exactly four forms

The four tested forms are the2×2 family obtained by independently reversing source number order and reversing bits within each number:

| Form | Distinct scalars | Addresses checked | Confirmed/mempool transaction activity |
|---|---:|---:|---:|
| Source order |1|5|0|
| Reverse entire bit string |1|5|0|
| Reverse source number order only |1|5|0|
| Reverse bits inside each number only |1|5|0|

All20 Blockstream API responses succeeded. One initial timeout was retried successfully; there are no unresolved errors. Address types were compressed/uncompressed P2PKH, P2SH-P2WPKH, P2WPKH and Taproot. Per-address URLs, check timestamps and raw statistics are stored in`numeric_activity.json`. No transactions or wallet imports were performed.

## Comparison with archived work

`scripts/run_ten_registered_experiments.py:140–145` used a handpicked number list as page76 word/letter **indices**, including tweet-prize numbers. It did not concatenate all source-order integer binary encodings. `scripts/run_second_wave_crypto_experiments.py:200–217` tested byte transformations/modulo/scaling mainly for geometry-derived and identifier-derived streams. `scripts/search_visual_private_keys.py:236–258` uses word lengths/alphabet positions. A targeted search of archived scripts found no implementation of the exact24-number scaled minimal-binary rule.

[Private context omitted from this public copy.]

## Files

- `all_142_source_lines.md`: every printed body line, locator coordinates/rotation, and explicit numerical readings, including lines with no numbers. Locator boxes are broad bands, not glyph-tight word boxes.
- `numeric_inventory.json`: lexical categories, character offsets, scale attachments across lines, values, bits, all declared offline representation counts, and the four candidate scalars.
- `numeric_activity.json`: the finite20-address read-only check.

This closes these four concrete key forms under the stated24-number rule. It does not establish that every conceivable number interpretation is exhausted.
