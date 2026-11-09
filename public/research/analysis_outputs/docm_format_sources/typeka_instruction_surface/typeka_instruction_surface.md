# Typeka Instruction Surface

Scope: scan non-regular Typeka font-state runs for explicit extraction wording. No key derivation, hashing, seed checking, WIF checking, address checking, or broad brute force was run.

- Created: `2026-05-20T21:52:04`
- Source: `analysis_outputs/docm_format_sources/typeka_variant_state_audit.json`

## Run Counts

- Variant run counts: `{'TYPEKA_BOLD': 115, 'MIX': 47}`
- Strong instruction records: `0`
- Procedural/directional/index terms without unit: `9`
- Unit terms without action: `0`

## Term Counts

- `procedural`: `{'see': 1, 'take': 1}`
- `unit`: `{}`
- `mirror`: `{'up': 2, 'left': 1, 'right': 2}`
- `index_word`: `{'one': 1, 'zero': 1, 'first': 1}`

## Procedural / Directional Hits Without Extraction Unit

| run | page | variant | highlight | terms | text |
|---:|---:|---|---|---|---|
| `83` | `76` | `TYPEKA_BOLD` | `none` | `up` | UTXO ghetto up in here |
| `198` | `77` | `TYPEKA_BOLD` | `none` | `one` | EVERY SINGLE ONE OF |
| `229` | `78` | `TYPEKA_BOLD` | `none` | `up` | Love opens up the collective unconscious and |
| `262` | `78` | `TYPEKA_BOLD` | `yellow` | `left` | America left $85 |
| `288` | `78` | `TYPEKA_BOLD` | `none` | `see` | observable by anyone choosing to see it, |
| `289` | `78` | `TYPEKA_BOLD` | `none` | `right` | right there in the Genesis Block. |
| `307` | `79` | `TYPEKA_BOLD` | `yellow` | `right, take` | That's right, Bitcoin will take |
| `313` | `79` | `MIX` | `none` | `zero` | drops to near zero because our natural tendency toward |
| `316` | `79` | `MIX` | `none` | `first` | monetized for the first time in |

## Active Corridor Overlap

| run | page | variant | active terms | instruction terms | text |
|---:|---:|---|---|---|---|
| `43` | `75` | `MIX` | `shitcoiner` | `-` | ocoiners and shitcoiners, |
| `66` | `75` | `TYPEKA_BOLD` | `shitcoiner` | `-` | Don't fall for shitcoinery. |
| `80` | `76` | `TYPEKA_BOLD` | `heart` | `-` | Get some toxicity. Get some bitcoin. Open your heart to |
| `102` | `76` | `TYPEKA_BOLD` | `shitcoiner` | `-` | shitcoiners' |
| `120` | `76` | `MIX` | `el salvador` | `-` | El Salvador |
| `124` | `76` | `TYPEKA_BOLD` | `buying the dip` | `-` | "buying the dip |
| `131` | `76` | `TYPEKA_BOLD` | `$1 billion` | `-` | $1 billion |
| `137` | `76` | `TYPEKA_BOLD` | `volcano bonds` | `-` | “Volcano Bonds” |
| `140` | `76` | `TYPEKA_BOLD` | `imf` | `-` | IMF |
| `143` | `76` | `MIX` | `mike` | `-` | Mike |
| `144` | `76` | `MIX` | `novogratz` | `-` | Novogratz |
| `148` | `76` | `MIX` | `trust` | `-` | I don't really trust that guy. |
| `151` | `76` | `TYPEKA_BOLD` | `shitcoiner, heart` | `-` | shitcoiner at heart. |
| `190` | `77` | `TYPEKA_BOLD` | `shitcoiner` | `-` | shitcoiners, |

## Findings

- Typeka Mix / bold Typeka contains contextual prose terms such as `first`, `right`, `take`, and `see`, but none is paired with `word`, `letter`, `line`, `page`, `font`, `mirror`, `fold`, `reverse`, `key`, `private`, `seed`, or `address` as an extraction instruction.
- The active page-76 corridor still appears in the expected font-state runs: `El Salvador`, `buying the dip`, `$1 billion`, `Volcano Bonds`, `IMF`, `Mike Novogratz`, `trust`, and `shitcoiner at heart`.
- Those active runs explain emphasis/provenance; they do not provide the missing unit/order.

## Decision

- Close Typeka-as-instruction-surface under the current DOCM witness.
- Keep Typeka as a formatting witness and corridor support layer only.
- Reopen only if a source clue explicitly names font state, Typeka, Mix, bold, first/last letters, or another concrete unit.
