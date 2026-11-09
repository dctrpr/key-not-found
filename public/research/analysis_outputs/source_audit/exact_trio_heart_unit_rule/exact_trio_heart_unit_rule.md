# Exact Trio Heart-Unit Rule

Scope: test the printed word `heart` as a literal middle-letter unit on the repaired exact-edge trio only. No OCR extraction, key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T10:55:10`
- Trio: `should sell | Volcano Bonds | shitcoiner at heart`

## Phrase Hearts

| phrase | words | letters | middle word(s) | heart width 1/2 | heart width 3 | heart width 4 | width-4 variants | per-word hearts |
|---|---|---|---|---|---|---|---|---|
| `should sell` | `['should', 'sell']` | `shouldsell` | `['should', 'sell']` | `ld` | `lds` | `ulds` | `{'leftBiased': 'ulds', 'rightBiased': 'ldse'}` | `['ou', 'el']` |
| `Volcano Bonds` | `['Volcano', 'Bonds']` | `volcanobonds` | `['Volcano', 'Bonds']` | `no` | `nob` | `anob` | `{'leftBiased': 'anob', 'rightBiased': 'nobo'}` | `['c', 'n']` |
| `shitcoiner at heart` | `['shitcoiner', 'at', 'heart']` | `shitcoineratheart` | `['at']` | `e` | `ner` | `iner` | `{'leftBiased': 'iner', 'rightBiased': 'iner'}` | `['co', 'at', 'a']` |

## Streams

| stream | value | instruction hits |
|---|---|---|
| `middleWordsForward` | `should sell Volcano Bonds at` | `[]` |
| `middleWordsReverse` | `at Volcano Bonds should sell` | `[]` |
| `phraseHeartWidth1Forward` | `ldnoe` | `[]` |
| `phraseHeartWidth1Reverse` | `enold` | `[]` |
| `phraseHeartWidth3Forward` | `ldsnobner` | `[]` |
| `phraseHeartWidth3Reverse` | `nernoblds` | `[]` |
| `phraseHeartWidth4Forward` | `uldsanobiner` | `[]` |
| `phraseHeartWidth4Reverse` | `ineranobulds` | `[]` |
| `perWordHeartsForward` | `ou el c n co at a` | `[]` |
| `perWordHeartsReverse` | `co at a c n ou el` | `[]` |
| `shitcoinerHeartLeftBiased4` | `tcoi` | `[]` |
| `shitcoinerHeartRightBiased4` | `coin` | `[]` |

## Assessment

- The literal `heart` unit is locally justified only because the exact-edge trio contains `shitcoiner at heart`.
- Middle/heart extraction from the exact trio produces fragments such as `ldnoe`, `ldsnobner`, and `uldsanobiner`, plus ambiguous center windows from `shitcoiner`.
- A right-biased 4-letter heart of `shitcoiner` gives `coin`, while the left-biased 4-letter heart gives `tcoi`; that ambiguity makes it thematic support, not a defensible selector.
- The rule does not supply the missing extraction unit for page-76 key material; it only explains why O5 keeps acting as semantic support.

## Decision

- Close literal heart extraction from the exact trio as a selector. Preserve the ambiguous `coin`/`tcoi` heart of `shitcoiner` as thematic support only.

## Next Move

- The closest local path remains blocked on a source-backed unit. Continue with source/original-layout/physical evidence or a new explicit rule, not local key candidates.
