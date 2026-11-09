# G5/O5 Symmetric Line-Fold Audit

Scope: test a Schott-style two-handed/mirror read on the confirmed page-76 G5/O5 interval. The six printed lines from `Volcano Bonds` to `shitcoiner at heart` are paired outside-in and inside-out. No key candidates, hashes, seed phrases, or address checks were generated.

- Created: `2026-05-20T08:06:13`
- Diagram: `analysis_outputs/source_audit/g5_o5_symmetric_line_fold/g5_o5_symmetric_line_fold_diagram.jpg`

## Fold Lines

| line | text | highlights | bold/partial |
|---:|---|---|---|
| 27 | `collateralized “Volcano Bonds” to pay off the IMF` | `grey: Volcano Bonds; bold: IMF` | `IMF` |
| 28 | `loan and get rid of those leeches. I tagged Mike` | `bold-partial/full: Mike` | `loanie / ie` |
| 29 | `Novogratz in the tweet, figuring he could sell a` | `bold-partial: Novogratz` | `Nvz / Nvz` |
| 30 | `bunch to his Wall Street crony pals, but so far he` | `-` | `-` |
| 31 | `hasn't moved on it. I don't really trust that guy.` | `bold partial: I don't really trust that guy` | `Idelluhu / delluhu` |
| 32 | `Maybe because he's a shitcoiner at heart.` | `orange: shitcoiner at heart` | `shitcoineratheart` |

## Outside-In Pairs

| pair | lines | first initials | last initials | word counts | edge words | highlights |
|---|---|---|---|---|---|---|
| P1 | `27 / 32` | `cM` | `Ft` | `[8, 8]` | `collateralized IMF Maybe heart` | `grey: Volcano Bonds | bold: IMF | orange: shitcoiner at heart` |
| P2 | `28 / 31` | `lh` | `ey` | `[10, 12]` | `loan Mike hasn guy` | `bold-partial/full: Mike | bold partial: I don't really trust that guy` |
| P3 | `29 / 30` | `Nb` | `ae` | `[9, 11]` | `Novogratz a bunch he` | `bold-partial: Novogratz` |

## Streams

- `outsideInLineInitials`: `cMlhNb`; instruction hits: `none`
- `insideOutLineInitials`: `NblhcM`; instruction hits: `none`
- `outsideInLastInitials`: `Fteyae`; instruction hits: `none`
- `insideOutLastInitials`: `aeeyFt`; instruction hits: `none`
- `outsideInEdgeWordsTopBottom`: `collateralized IMF Maybe heart | loan Mike hasn guy | Novogratz a bunch he`; instruction hits: `none`
- `outsideInEdgeWordsBottomTop`: `Maybe heart collateralized IMF | hasn guy loan Mike | bunch he Novogratz a`; instruction hits: `none`
- `insideOutEdgeWordsTopBottom`: `Novogratz a bunch he | loan Mike hasn guy | collateralized IMF Maybe heart`; instruction hits: `none`
- `outsideInWordCountDiffs`: `022`; instruction hits: `none`
- `outsideInHighlightStream`: `grey: Volcano Bonds | bold: IMF | orange: shitcoiner at heart | bold-partial/full: Mike | bold partial: I don't really trust that guy | bold-partial: Novogratz`; instruction hits: `none`
- `outsideInBoldLetters`: `IMFshitcoineratheartloanieIdelluhuNvz`; instruction hits: `none`
- `outsideInPartialBoldLetters`: `iedelluhuNvz`; instruction hits: `none`
- `outsideInFullLineRead`: `collateralized “Volcano Bonds” to pay off the IMF | Maybe because he's a shitcoiner at heart. | loan and get rid of those leeches. I tagged Mike | hasn't moved on it. I don't really trust that guy. | Novogratz in the tweet, figuring he could sell a | bunch to his Wall Street crony pals, but so far he`; instruction hits: `none`
- `insideOutFullLineRead`: `Novogratz in the tweet, figuring he could sell a | bunch to his Wall Street crony pals, but so far he | loan and get rid of those leeches. I tagged Mike | hasn't moved on it. I don't really trust that guy. | collateralized “Volcano Bonds” to pay off the IMF | Maybe because he's a shitcoiner at heart.`; instruction hits: `none`

## Assessment

- The symmetric six-line fold is human-plausible from the Schott clue and the confirmed five-line G5/O5 gap, but it does not produce a selector.
- Outside-in and inside-out initials, last initials, edge words, highlight streams, word-count differences, and bold/partial-bold streams are ordinary corridor prose or short non-words.
- The only instruction-term hits are inherited visible words like `sell`, not procedural terms such as read/take/word/letter/key.
- This closes the G5/O5 symmetric line-fold as a standalone extraction rule under the current corrected text model.
- The G5/O5 relation remains a locator and source-registration validation point, not key material.

## Next Best Move

- Stop local G5/O5 text-unit permutations unless a new clue names a unit. Use future source images or physical scans to test whether the G5/O5 geometry changes or finally names how to read the target.
