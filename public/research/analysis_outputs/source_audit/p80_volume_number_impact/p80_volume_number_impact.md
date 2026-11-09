# P80 Volume Number Impact Audit

Scope: check what changes if the p80 package volume is read as `16 FL OZ (473 mL)` instead of the clipped `6 FL OZ (473 mL)`. No key candidates or hashing were generated.

- Created: `2026-05-20T06:02:38`

## Key Comparison

- `16` zero-based page-76 line: `laundering lobotomy. It’s a stun gun to the genitals.`
- `16` one-based page-76 line: `Fortunately, bitcoin puts an end to the paper chase Manhattan Bank money`
- `16` one-based word: `ghetto`
- `6` zero-based page-76 line: `Gotta be this way. Forty years of dumb post-1971 fiat money`
- `6` one-based page-76 line: `ripped off live central bankers tied to a burning stake.`
- `6` one-based word: `bitcoin`

## Number Checks

| source | number | zero-based line | one-based line | one-based word | matching line-offset landing |
|---|---:|---|---|---|---|
| `5_symptom_relief` | 5 | ripped off live central bankers tied to a burning stake. | nailing the Vatican with ultimatums. It's the sound of skin being | `some` | `-` |
| `16_fl_oz_likely` | 16 | laundering lobotomy. It’s a stun gun to the genitals. | Fortunately, bitcoin puts an end to the paper chase Manhattan Bank money | `ghetto` | `O3+3 zero` |
| `6_fl_oz_clipped_crop` | 6 | Gotta be this way. Forty years of dumb post-1971 fiat money | ripped off live central bankers tied to a burning stake. | `bitcoin` | `-` |
| `100_percent_pow` | 100 |  |  | `dulled` | `-` |
| `473_ml` | 473 |  |  | `` | `-` |
| `page_number` | 80 |  |  | `Peter` | `-` |

## Assessment

- `16 FL OZ (473 mL)` should be treated as the canonical package volume; `6 FL OZ` is a clipped-crop reading.
- Using 16 as a zero-based page-76 line selector lands exactly on `laundering lobotomy. It’s a stun gun to the genitals.`, the O3+3 -> B3 line-offset hit.
- Using 6 instead lands on the B1/Gotta line and does not explain the p80 volume/metric pair.
- This strengthens p80 as provenance support for the B3/stun-gun line, but it does not explain #2/#4 or name an extraction unit.
- Future p80 audits should record the volume as `16 FL OZ (473 mL)` while noting the old cropped `6` reading as a source-fidelity artifact.
