# Named Term Visual / Typography Audit

Scope: inspect only the named page-76 words for Typeka state changes and highlight-edge contacts. No key candidates, hashes, seed phrases, or address checks were generated.

- Created: `2026-05-20T06:22:02`
- Overlay: `analysis_outputs/source_audit/named_term_visual_typography/named_term_visual_typography_overlay.jpg`

## Summary

- Font-state counts: `{'MIX': 2, 'TYPEKA': 11, 'TYPEKA_BOLD': 1, 'TYPEKA_BOLD+BLACK': 2, 'TYPEKA_BOLD+YELLOW': 2}`
- Highlight-contact counts: `{"It's a stun gun to the genitals": 2, 'O2/orange/Bitcoin line': 1, 'O5/orange/shitcoiner-heart': 1}`
- `fontStateEntryLetters`: `gs`
- `fontStateExitLetters`: `nndsst`
- `highlightEdgeLetters`: `-`

## Records

| source | term | line | DOCM state | state boundary | high-res match | highlight contacts |
|---|---|---:|---|---|---|---|
| `O1` | `bitcoin` | 1 | `TYPEKA_BOLD+YELLOW` | `exit` | `Biteoiny / row-token OCR fuzzy match 0.80` | `O2/orange/Bitcoin line 0.706` |
| `O2` | `george` | 3 | `MIX` | `entry` | `George / row-token fuzzy match` | `-` |
| `O2` | `clinton` | 3 | `MIX` | `exit` | `Clinton / row-token fuzzy match` | `-` |
| `O2` | `james` | 3 | `TYPEKA` | `-` | `James / row-token fuzzy match` | `-` |
| `O2` | `brown` | 3 | `TYPEKA` | `-` | `Brown / row-token fuzzy match` | `-` |
| `O2` | `clones` | 3 | `TYPEKA` | `-` | `clones. / row-token fuzzy match` | `-` |
| `O2` | `martin` | 3 | `TYPEKA` | `-` | `Martin / row-token fuzzy match` | `-` |
| `O2` | `luther` | 3 | `TYPEKA` | `-` | `Luther / row-token fuzzy match` | `-` |
| `B1` | `bitcoin` | 7 | `TYPEKA` | `-` | `bitcoin / row-token fuzzy match` | `-` |
| `B2` | `dulled` | 9 | `TYPEKA` | `exit` | `dulled / row-token fuzzy match` | `-` |
| `B2` | `shitcoiners` | 9 | `TYPEKA_BOLD` | `entry,exit` | `shitcoiners' / row-token fuzzy match` | `-` |
| `O3` | `stun` | 16 | `TYPEKA_BOLD+BLACK` | `-` | `Stun / row-token fuzzy match` | `It's a stun gun to the genitals 1.0` |
| `O3` | `genitals` | 16 | `TYPEKA_BOLD+BLACK` | `exit` | `genitals. / row-token fuzzy match` | `It's a stun gun to the genitals 1.0` |
| `O4` | `bitcoin` | 26 | `TYPEKA` | `-` | `bitcoin / row-token fuzzy match` | `-` |
| `O4` | `earnings` | 26 | `TYPEKA` | `-` | `earnings / row-token fuzzy match` | `-` |
| `B4` | `could` | 29 | `TYPEKA` | `-` | `could / row-token fuzzy match` | `-` |
| `B4` | `sell` | 29 | `TYPEKA` | `-` | `sella / row-token fuzzy match` | `-` |
| `B5` | `heart` | 32 | `TYPEKA_BOLD+YELLOW` | `exit` | `heart / approx canonical proportional` | `O5/orange/shitcoiner-heart 0.587` |

## Assessment

- Named terms do not produce a one-letter-per-word typography selector.
- The strongest font fact is local and expected: `George Clinton` is Typeka Mix, while the rest of the O2 carrier terms are ordinary Typeka.
- `shitcoiners`, `stun/genitals`, the top `bitcoin`, and final `heart` are Typeka-bold or highlighted because they sit inside visible emphasized phrases, not because only one letter is isolated.
- Highlight-edge contacts are sparse and mostly boundary contacts around whole highlighted phrases, not a repeated per-word letter selector.
- Close named-term Typeka/highlight-edge extraction as a standalone path; keep the overlay as a visual checklist if a later clue names font edges or highlight borders.

Next move: Check whether the unmatched B3+3 landing (`Don't believe me?`) is a deliberate gap/instruction break, or whether another source layer points to it.
