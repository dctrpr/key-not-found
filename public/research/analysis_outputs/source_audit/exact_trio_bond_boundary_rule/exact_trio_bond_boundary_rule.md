# Exact Trio Bond-Boundary Rule

Scope: test `Bonds` as a literal word/phrase-boundary unit on the repaired exact-edge trio. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T10:58:35`
- Trio: `should sell | Volcano Bonds | shitcoiner at heart`

## Word Bonds

| phrase | word bond | inside last/first | outside first/last |
|---|---|---|---|
| `should sell` | `should / sell` | `ds` | `sl` |
| `Volcano Bonds` | `Volcano / Bonds` | `ob` | `vs` |
| `shitcoiner at heart` | `shitcoiner / at` | `ra` | `st` |
| `shitcoiner at heart` | `at / heart` | `th` | `at` |

## Phrase Bonds

| phrase bond | last/first | first/last |
|---|---|---|
| `should sell -> Volcano Bonds` | `lv` | `so` |
| `Volcano Bonds -> shitcoiner at heart` | `ss` | `br` |

## Streams

| stream | value | instruction hits |
|---|---|---|
| `wordBondInsideForward` | `dsobrath` | `[]` |
| `wordBondInsideReverse` | `thraobds` | `[]` |
| `wordBondOutsideForward` | `slvsstat` | `[]` |
| `wordBondOutsideReverse` | `atstvssl` | `[]` |
| `phraseBondLastFirstForward` | `lvss` | `[]` |
| `phraseBondLastFirstReverse` | `sslv` | `[]` |
| `phraseBondFirstLastForward` | `sobr` | `[]` |
| `phraseBondFirstLastReverse` | `brso` | `[]` |
| `wordBondPairsForward` | `ds ob ra th` | `[]` |
| `phraseBondPairsForward` | `lv ss` | `[]` |
| `allBondPairsForward` | `ds ob ra th lv ss` | `[]` |

## Assessment

- The `Bonds` unit is locally justified only because `Volcano Bonds` is one of the exact-edge phrases.
- Word-boundary and phrase-boundary streams produce short fragments such as `dsobrath`, `slvsstat`, `lvss`, and `sobr`.
- No boundary stream creates an instruction term or a readable unit that would tell us what to extract next.
- This closes literal bond/boundary extraction from the exact trio as a standalone selector.

## Decision

- Close literal bond/boundary extraction from the exact trio as a selector.

## Next Move

- The closest local path remains blocked on a source-backed extraction unit. Continue only with better source evidence or a new explicit rule.
