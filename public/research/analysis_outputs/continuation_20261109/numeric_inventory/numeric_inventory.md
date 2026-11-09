# Reconstructing the community256/264-bit claim

All digit-written body numbers plus spelled finite quantity words Forty, six, zero; apply explicit billion/trillion decimal scales to monetary amounts; exclude ordinal first and pronoun ONE in EVERY SINGLE ONE OF. Body only; titles/art/page folios are separate source classes.

{'bodyLines': 142, 'digitEvents': 21, 'quantityCardinalEvents': 3, 'pronounOneEvents': 1, 'ordinalFirstEvents': 3, 'indefiniteBillions': 2, 'selectedNumbers': 24, 'selectedBitLength': 256, 'variants': 30, 'exact256Variants': 1, 'exact264Variants': 1}

## Selected source-order values

[2008, 1, 1, 1, 40, 1971, 10, 1, 2011, 1000000000, 42, 20000, 100000, 6, 2017, 12000, 51, 85000000000, 2000000000000, 51, 95, 0, 1969, 10]

## Representation variants

| Scope | Scale handling | Binary encoding | Values | Bits |
|---|---|---|---:|---:|
| digits_only | mantissa_only | minimal_integer_binary | 21 | 148 |
| digits_only | mantissa_only | whole_byte_integer_binary | 21 | 240 |
| digits_only | full_decimal_scales | minimal_integer_binary | 21 | 246 |
| digits_only | full_decimal_scales | whole_byte_integer_binary | 21 | 336 |
| digits_only | scale_as_separate_integer_token | minimal_integer_binary | 24 | 248 |
| digits_only | scale_as_separate_integer_token | whole_byte_integer_binary | 24 | 344 |
| digits_and_quantity_cardinals | mantissa_only | minimal_integer_binary | 24 | 158 |
| digits_and_quantity_cardinals | mantissa_only | whole_byte_integer_binary | 24 | 264 |
| digits_and_quantity_cardinals | full_decimal_scales | minimal_integer_binary | 24 | 256 |
| digits_and_quantity_cardinals | full_decimal_scales | whole_byte_integer_binary | 24 | 360 |
| digits_and_quantity_cardinals | scale_as_separate_integer_token | minimal_integer_binary | 27 | 258 |
| digits_and_quantity_cardinals | scale_as_separate_integer_token | whole_byte_integer_binary | 27 | 368 |
| digits_quantity_and_pronoun_one | mantissa_only | minimal_integer_binary | 25 | 159 |
| digits_quantity_and_pronoun_one | mantissa_only | whole_byte_integer_binary | 25 | 272 |
| digits_quantity_and_pronoun_one | full_decimal_scales | minimal_integer_binary | 25 | 257 |
| digits_quantity_and_pronoun_one | full_decimal_scales | whole_byte_integer_binary | 25 | 368 |
| digits_quantity_and_pronoun_one | scale_as_separate_integer_token | minimal_integer_binary | 28 | 259 |
| digits_quantity_and_pronoun_one | scale_as_separate_integer_token | whole_byte_integer_binary | 28 | 376 |
| digits_quantity_and_ordinals | mantissa_only | minimal_integer_binary | 27 | 161 |
| digits_quantity_and_ordinals | mantissa_only | whole_byte_integer_binary | 27 | 288 |
| digits_quantity_and_ordinals | full_decimal_scales | minimal_integer_binary | 27 | 259 |
| digits_quantity_and_ordinals | full_decimal_scales | whole_byte_integer_binary | 27 | 384 |
| digits_quantity_and_ordinals | scale_as_separate_integer_token | minimal_integer_binary | 30 | 261 |
| digits_quantity_and_ordinals | scale_as_separate_integer_token | whole_byte_integer_binary | 30 | 392 |
| all_explicit_finite_including_pronoun_and_ordinal | mantissa_only | minimal_integer_binary | 28 | 162 |
| all_explicit_finite_including_pronoun_and_ordinal | mantissa_only | whole_byte_integer_binary | 28 | 296 |
| all_explicit_finite_including_pronoun_and_ordinal | full_decimal_scales | minimal_integer_binary | 28 | 260 |
| all_explicit_finite_including_pronoun_and_ordinal | full_decimal_scales | whole_byte_integer_binary | 28 | 392 |
| all_explicit_finite_including_pronoun_and_ordinal | scale_as_separate_integer_token | minimal_integer_binary | 31 | 262 |
| all_explicit_finite_including_pronoun_and_ordinal | scale_as_separate_integer_token | whole_byte_integer_binary | 31 | 400 |

## Boundaries and uncertainty

The 256-bit result depends on the linguistic distinction between finite quantity cardinals and pronouns/ordinals; all alternatives are disclosed.
Percentages are encoded as the printed integer magnitude (42,51,95), not as fractions. Their exact rational values /100 have nonterminating binary expansions and cannot be losslessly represented by finite minimal integer bits.
Commas in 20,000/100,000/12,000 are thousands separators. There is no printed decimal point in these body numbers.
Indefinite plural billions occurs twice and has no determinate integer value. No million occurrence exists in this body.
Body-only excludes page folios, package copy, graphic lettering and bill serial numbers. These are not silently mixed into the body-number claim.
No arbitrary trimming, zero-padding to32bytes, modulo, dropped occurrences, salt, or hash is used for the four declared mirror-family candidates.

## Four declared direct candidates

- source_order: 256 bits, hex `fb1e8f675fb7dcd65005538830d41bf0ddc19cf29944803a3529440019df7b1a`.
- complete_bit_reversal: 256 bits, hex `58defb98002294ac5c0122994f3983bb0fd82b0c11caa00a6b3bedfae6f178df`.
- reverse_number_order: 256 bits, hex `af62bf9f46a5288002794ca24019ddc1f8761a8271055dcd65007dbd7b3a3fd8`.
- reverse_bits_within_each_number: 256 bits, hex `1bfc5cdebdbe00a6b3baa08e41586e1f83bb980245329e400114a562f9fd46f5`.
