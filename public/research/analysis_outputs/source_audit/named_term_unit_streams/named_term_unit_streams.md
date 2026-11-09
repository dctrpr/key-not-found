# Named Term Unit Streams Audit

Scope: test whether externally named words from the page-76 line-offset map form a readable instruction. No key candidates, hashes, seed phrases, or address checks were generated.

- Created: `2026-05-20T06:12:13`

## Named Term Rows

| source | line | named terms | preferred | provenance | target text |
|---|---:|---|---|---|---|
| `O1` | 1 | `bitcoin` | `bitcoin` | highlighttarget, reflectedhighlightgraph | Bitcoin. It's the freaking UTXO ghetto up in here, y'all. |
| `O2` | 3 | `george clinton james brown clones martin luther` | `george` | reflectedcarrierterms | but George Clinton and James Brown clones. It's Martin Luther |
| `B1` | 7 | `bitcoin` | `bitcoin` | highlighttarget, reflectedhighlightgraph | nonsense (and 10 years of watching Peter Schiff miss buying bitcoin |
| `B2` | 9 | `dulled shitcoiners` | `dulled` | p80number100, p80termsymptoms | have dulled shitcoiners' and nocoiners' minds. |
| `O3` | 16 | `stun genitals` | `genitals` | highlighttarget, reflectedhighlightgraph | laundering lobotomy. It’s a stun gun to the genitals. |
| `B3` | 19 | `-` | `-` | - | Don't believe me? |
| `O4` | 26 | `bitcoin earnings` | `earnings` | p78bboxwords, p78darkwords, reflectedhighlightgraph | billions worth of future bitcoin earnings |
| `B4` | 29 | `could sell` | `sell` | p78bboxwords, p78darkwords, p78holewords | Novogratz in the tweet, figuring he could sell a |
| `B5` | 32 | `heart` | `heart` | highlighttarget, reflectedhighlightgraph, targetconvergence | Maybe because he's a shitcoiner at heart. |

## Stream Checks

| stream | spaced | compact | instruction hits |
|---|---|---|---|
| `preferred_terms_forward` | `bitcoin george bitcoin dulled genitals earnings sell heart` | `bitcoingeorgebitcoindulledgenitalsearningssellheart` | `-` |
| `preferred_terms_reverse` | `heart sell earnings genitals dulled bitcoin george bitcoin` | `heartsellearningsgenitalsdulledbitcoingeorgebitcoin` | `-` |
| `all_named_terms_forward` | `bitcoin george clinton james brown clones martin luther bitcoin dulled shitcoiners stun genitals bitcoin earnings could sell heart` | `bitcoingeorgeclintonjamesbrownclonesmartinlutherbitcoindulledshitcoinersstungenitalsbitcoinearningscouldsellheart` | `-` |
| `all_named_terms_reverse` | `heart sell could earnings bitcoin genitals stun shitcoiners dulled bitcoin luther martin clones brown james clinton george bitcoin` | `heartsellcouldearningsbitcoingenitalsstunshitcoinersdulledbitcoinluthermartinclonesbrownjamesclintongeorgebitcoin` | `-` |
| `first_named_term_per_row` | `bitcoin george bitcoin dulled stun bitcoin could heart` | `bitcoingeorgebitcoindulledstunbitcoincouldheart` | `-` |
| `last_named_term_per_row` | `bitcoin luther bitcoin shitcoiners genitals earnings sell heart` | `bitcoinlutherbitcoinshitcoinersgenitalsearningssellheart` | `-` |
| `source_index_selected_terms` | `bitcoin clinton bitcoin shitcoiners stun earnings sell heart` | `bitcoinclintonbitcoinshitcoinersstunearningssellheart` | `-` |
| `color_rule_O_first_B_last` | `bitcoin george bitcoin shitcoiners stun bitcoin sell heart` | `bitcoingeorgebitcoinshitcoinersstunbitcoinsellheart` | `-` |
| `color_rule_O_last_B_first` | `bitcoin luther bitcoin dulled genitals earnings could heart` | `bitcoinlutherbitcoindulledgenitalsearningscouldheart` | `-` |
| `preferred_initials` | `b g b d g e s h` | `bgbdgesh` | `-` |
| `all_named_initials` | `b g c j b c m l b d s s g b e c s h` | `bgcjbcmlbdssgbecsh` | `-` |
| `source_index_letters_first_terms` | `b e b u u c l t` | `bebuuclt` | `-` |
| `source_index_letters_last_terms` | `b u b h n n l t` | `bubhnnlt` | `-` |
| `source_index_letters_first_terms_from_end` | `n g n e t c o h` | `ngnetcoh` | `-` |
| `source_index_letters_last_terms_from_end` | `n e n r a i s h` | `nenraish` | `-` |

## Assessment

- Adding the secondary-supported #2 terms does not turn the named-term streams into a readable instruction.
- The strongest expanded preferred sequence is `bitcoin george bitcoin dulled genitals earnings sell heart`, with initials `bgbdgesh`; reversed and color-rule variants are also not instruction-like.
- All-named terms mainly restate source provenance: `bitcoin george clinton james brown clones martin luther bitcoin dulled shitcoiners stun genitals bitcoin earnings could sell heart`.
- Source-index letter picks and O/B first-last rules produce short nonsense strings rather than `read/take/mirror/word/letter/key` language.
- This closes externally named terms as a standalone extraction unit, while preserving them as a cleaner locator ledger.

Next move: Use the named-term ledger to drive a visual/typography audit around only those exact words on page 76, especially whether Typeka states or highlight edges mark one letter per named word.
