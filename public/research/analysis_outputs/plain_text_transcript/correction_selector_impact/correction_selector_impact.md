# Plain Correction Selector Impact

Scope: check whether the latest plain-text correction markup adds a human-readable selector/instruction, especially around the page-76 corridor. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T21:01:13`
- Corrections checked: `21`
- Corrections touching target/corridor terms: `3`
- Corrections adding selector-permission terms: `0`

## Corridor-Relevant Corrections

| # | raw | fixed | added tokens | target hits | added instruction hits | active phrase hits |
|---:|---|---|---|---|---|---|
| 5 | `"buying the dip".` | `"buying the dip."` | `.` | buying, dip | - | O4 |
| 6 | `collateralized to pay off the IMF` | `collateralized “Volcano Bonds” to pay off the IMF` | `“ Volcano Bonds ”` | volcano, bonds, imf | - | G5 |
| 14 | `requires printing and wars` | `requires money printing and wars` | `money` | money | - | - |

## Selector-Permission Check

- No correction-added token is a procedural selector term.

## Findings

- The correction layer repairs exact wording but does not add a source-backed extraction instruction.
- No correction-added token is a procedural unit/order term such as read/take/select/word/letter/line/edge/font/mirror/key.
- The important page-76 correction is the restored G5 phrase `Volcano Bonds`; it repairs a missing active target in the latest raw plain text rather than creating a new selector.
- The O4 correction only moves the period inside the quote for `buying the dip.`; this matters for exact text but not for geometry/order.
- Other target-adjacent corrections (`money`, `$2 trillion`, capitalization/punctuation) are text-authority guardrails, not extraction permission.

## Decision

- Use the corrected/DOCM text as wording authority, but do not treat the correction list itself as a selector or instruction stream.
- Next move: Continue to require an external/source rule naming unit and order before extraction; correction markup only locks exact wording.
