# BOLD vs Article Active Corridor

Scope: compare `BOLD.docm` and `Article with Fonts.docm` only around the locked page-76 active corridor. DOCM files were inspected as zipped Word packages; no macros were executed, and no key candidates were generated.

- Created: `2026-05-20T21:10:12`
- `BOLD.docm` active set complete: `False`
- `Article with Fonts.docm` active set complete: `True`

## Document Summary

| document | macros | paragraphs | runs | words | fonts | highlights | active present | corridor context present |
|---|---:|---:|---:|---:|---|---|---|---|
| `BOLD.docm` | `True` | 25 | 140 | 230 | `Typeka:139, Stencil:1` | `(none):97, yellow:43` | `-` | `IMF, Nayib Bukele, IMF loan` |
| `Article with Fonts.docm` | `False` | 149 | 344 | 1281 | `Typeka:295, Typeka Mix:47, LonestarW00-Regular:1, Stencil:1` | `(none):278, yellow:35, black:28, cyan:3` | `buying the dip, $1 billion, Volcano Bonds, shitcoiner at heart` | `El Salvador, International Monetary Fund, IMF, Nayib Bukele, should sell, future bitcoin earnings, IMF loan, Mike Novogratz, trust that guy` |

## Phrase Witnesses

| phrase | role | BOLD.docm | Article with Fonts.docm |
|---|---|---|---|
| `buying the dip` | active orange target | absent | present para `63`, fonts `Typeka:1`, highlights `yellow:1`, bold `1.0` |
| `$1 billion` | active black target | absent | present para `66`, fonts `Typeka:1`, highlights `black:1`, bold `1.0` |
| `Volcano Bonds` | active grey target | absent | present para `68`, fonts `Typeka:1`, highlights `black:1`, bold `1.0` |
| `shitcoiner at heart` | active orange target | absent | present para `73`, fonts `Typeka:1`, highlights `yellow:1`, bold `1.0` |
| `El Salvador` | page-76 corridor context | absent | present para `61`, fonts `Typeka Mix:1`, highlights `(none):1`, bold `0.0` |
| `International Monetary Fund` | page-76 corridor context | absent | present para `62`, fonts `Typeka:1`, highlights `(none):1`, bold `0.0` |
| `IMF` | page-76 corridor context | present para `8`, fonts `Typeka:1`, highlights `(none):1`, bold `1.0` | present para `62`, fonts `Typeka:1`, highlights `(none):1`, bold `0.0` |
| `Nayib Bukele` | page-76 corridor context | present para `7`, fonts `Typeka:1`, highlights `(none):1`, bold `1.0` | present para `64`, fonts `Typeka:1`, highlights `(none):1`, bold `1.0` |
| `should sell` | p78 source/target-adjacent context | absent | present para `66`, fonts `Typeka:1`, highlights `(none):1`, bold `0.0` |
| `future bitcoin earnings` | p78 source/target-adjacent context | absent | present para `67`, fonts `Typeka:1`, highlights `(none):1`, bold `0.0` |
| `IMF loan` | page-76 corridor context | present para `8`, fonts `Typeka:2`, highlights `(none):1, yellow:1`, bold `1.0` | present para `68`, fonts `Typeka:2`, highlights `(none):2`, bold `1.0` |
| `Mike Novogratz` | page-76 corridor context | absent | present para `69`, fonts `Typeka Mix:2`, highlights `(none):2`, bold `0.0` |
| `trust that guy` | page-76 corridor context | absent | present para `72`, fonts `Typeka Mix:1`, highlights `(none):1`, bold `0.0` |

## Findings

- Article with Fonts.docm contains all four locked active units and the surrounding El Salvador/IMF/Bukele/Novogratz corridor, so it remains the best Word-level formatting witness for the page-76 target cluster.
- BOLD.docm does not cover the full O4/B4/G5/O5 active set, so it cannot be the primary source for active-corridor extraction.
- BOLD.docm does not improve original-source authority because it contains an embedded VBA project and remains tied to the unrecovered word-list highlighting workflow already seen in the macro audit.
- BOLD.docm is useful only as a generated-markup witness. Any phrase or bold state found there must be confirmed against Article with Fonts.docm or the high-res magazine scan before it can drive extraction.
- No instruction-bearing phrase is introduced by the BOLD-vs-Article comparison; the visible instruction-like terms are ordinary article prose such as `sell`, not `read/take/line/word/letter/mirror/key` selector language.

## Decision

- Keep Article with Fonts.docm as the trusted DOCM formatting witness; keep BOLD.docm on the generated-artifact branch unless the missing `otrobip.txt` source list is recovered.
- Next move: Return to high-res magazine geometry and page-76 corridor ordering; use BOLD.docm only for sanity checks, not as a selector.
