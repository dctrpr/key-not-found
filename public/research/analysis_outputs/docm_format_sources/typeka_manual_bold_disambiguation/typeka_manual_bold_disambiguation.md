# Typeka / Manual Bold Disambiguation

Scope: active lower page-76 corridor only. This compares the DOCM font/bold/highlight witness against the user Markdown bold markup. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

## Summary

- Targets checked: `11`.
- Dominant Typeka Mix targets in DOCM: `el_salvador, novogratz, trust_that_guy`.
- Markdown-bold but not DOCM-bold targets: `none`.
- DOCM-bold but not Markdown-bold targets: `one_billion, volcano_bonds`.
- Disagreement count: `5`.

## Active Corridor Rows

| id | phrase | DOCM dominant font | DOCM bold | DOCM Typeka Mix | DOCM highlights | Markdown bold |
| --- | --- | --- | ---: | ---: | --- | ---: |
| `el_salvador` | `El Salvador` | `Typeka Mix` | `0.0` | `1.0` | none:11 | `0.455` |
| `buying_dip` | `buying the dip` | `Typeka` | `1.0` | `0.0` | yellow:14 | `1.0` |
| `one_billion` | `$1 billion` | `Typeka` | `1.0` | `0.0` | black:10 | `0.0` |
| `should_sell` | `should sell` | `Typeka` | `0.0` | `0.0` | none:11 | `0.0` |
| `future_bitcoin_earnings` | `future bitcoin earnings` | `Typeka` | `0.0` | `0.0` | none:23 | `0.0` |
| `volcano_bonds` | `Volcano Bonds` | `Typeka` | `1.0` | `0.0` | black:13 | `0.0` |
| `imf_loan` | `IMF loan` | `Typeka` | `0.889` | `0.0` | none:8 | `0.7` |
| `tagged_mike` | `I tagged Mike` | `Typeka` | `0.0` | `0.308` | none:13 | `0.154` |
| `novogratz` | `Novogratz` | `Typeka Mix` | `0.0` | `1.0` | none:9 | `0.333` |
| `trust_that_guy` | `I don't really trust that guy` | `Typeka Mix` | `0.0` | `1.0` | none:29 | `0.31` |
| `shitcoiner_heart` | `shitcoiner at heart` | `Typeka` | `1.0` | `0.0` | yellow:19 | `1.0` |

## Decision

- `Article with Fonts.docm` is the formatting witness for Typeka, Typeka Mix, bold, and highlight labels.
- Manual Markdown bold should be treated as a user annotation layer, not as original puzzle typography.
- Typeka Mix remains contextual/provenance evidence unless a new clue explicitly names font state or a stronger geometry selector first chooses exact units.
