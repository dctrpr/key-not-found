# Zero / #0 Index Rule Scope

Scope: test the Canva `#0` / zero clue as a zero-based or zero-count selector. No key candidates were generated.

- Created: `2026-05-20T13:23:14`
- Trusted scan top hotspot: `100,000` with `5` zeros.
- Unsupported transcript variant: `1000,000` with `6` zeros.
- Stream instruction hits: `{}`

## #0 Controls

| interpretation | selected |
|---|---|
| orange zero-based | `O1` `Get some toxicity / Open your heart to` |
| grey zero-based | `B1` `Gotta be this way... post-1971 fiat money` |
| all-units zero-based | `O1` `Get some toxicity / Open your heart to` |
| corridor zero-based | corridor `1` `Don't believe me?` |

## Zero-Count Rows

| source | page | token | zeros | orange | grey | corridor-by-count | modulo-corridor | active O5/G5? | instruction hits |
|---|---:|---|---:|---|---|---|---|---|---|
| `trusted_scan` | `75` | `2008` | `2` | `O2` | `B2` | `2:H` | `7:$` | `-` | `[]` |
| `trusted_scan` | `76` | `10` | `1` | `O1` | `B1` | `1:D` | `11:N` | `-` | `[]` |
| `trusted_scan` | `76` | `2011` | `1` | `O1` | `B1` | `1:D` | `10:l` | `-` | `[]` |
| `trusted_scan` | `77` | `20,000` | `4` | `O4` | `B4` | `4:H` | `9:c` | `-` | `[]` |
| `trusted_scan` | `77` | `100,000` | `5` | `O5` | `B5` | `5:I` | `13:h` | `O5,G5` | `[]` |
| `trusted_scan` | `77` | `2017` | `1` | `O1` | `B1` | `1:D` | `2:H` | `-` | `[]` |
| `trusted_scan` | `77` | `12,000` | `3` | `O3` | `B3` | `3:t` | `3:t` | `-` | `[]` |
| `trusted_scan` | `79` | `10` | `1` | `O1` | `B1` | `1:D` | `11:N` | `-` | `[]` |
| `unsupported_variant_from_user_annotated_transcript` | `77` | `1000,000` | `6` | `-` | `-` | `6:h` | `9:c` | `-` | `[]` |

## Streams

- `zeroCountOrangeUnitIds`: `O2 O1 O1 O4 O5 O1 O3 O1`
- `zeroCountGreyUnitIds`: `B2 B1 B1 B4 B5 B1 B3 B1`
- `zeroCountAllUnitIds`: `O2 O1 O1 B2 O3 O1 B1 O1`
- `zeroCountCorridorInitials`: `HDDHIDtD`
- `zeroCountCorridorLastInitials`: `SmmdamTm`
- `digitsModuloCorridorInitials`: `$NlchHtN`
- `sourceLineIndexCorridorInitials`: `t$bHt$hl`
- `hash0SelectedIds`: `O1 B1 O1 corridor1`

## Assessment

- `#0` as a literal zero-based selector chooses the first page-76 units/corridor line, not the active O5/G5 lower-corridor target.
- Trusted-scan `100,000` has five zeros, so a zero-count-as-highlight-index rule redundantly lands on O5/B5; this supports the existing five/O5 locator but does not name a unit, order, or extraction operation.
- The unsupported `1000,000` variant would have six zeros and no fifth page-76 orange/grey unit target, so it weakens rather than clarifies the selector under current materials.
- The all-zero streams do not produce instruction terms such as read/take/word/letter/line/first/last.

Decision: `keep_zero_hash0_as_source_fidelity_and_five_locator_evidence_only`.

Next move: If the exact Canva/browser/original source that showed a missed `#0` appears, compare it to the existing zero crop sheet first; do not promote zero-count indexing under the current trusted scan.
