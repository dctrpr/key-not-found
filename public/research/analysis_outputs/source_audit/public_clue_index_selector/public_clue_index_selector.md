# Public Clue Index Selector

Scope: test whether the public clue words and numbers provide a simple index into page 76 or the confirmed page-76 corridor. No private-key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T08:10:01`
- Sheet: `analysis_outputs/source_audit/public_clue_index_selector/public_clue_index_selector_sheet.jpg`

## Streams

- `termInitials`: `hpBkepwBPNfoy2BMwnrup`; instruction hits: `none`
- `indexValues`: `3 7 7 3 7 5 5 15 9 6 7 3 3 20 3 6 7 12 11 7 10`; instruction hits: `none`
- `page76WordsByIndex`: `toxicity Open Open toxicity Open some some UTXO heart bitcoin Open toxicity toxicity y'all toxicity bitcoin Open It's Bitcoin Open to`; instruction hits: `none`
- `corridorWordsByIndex`: `believe seen seen believe seen Have Have International president you seen believe believe Twitter believe you seen Salvador El seen of`; instruction hits: `none`
- `corridorWordsByLetterLength`: `believe seen seen believe seen Have Have International president you seen believe believe t believe you seen Salvador El seen of`; instruction hits: `none`
- `corridorLineInitialsByIndex`: `t$$t$IIch$ttth$bN$l`; instruction hits: `none`
- `page76LineInitialsByIndex`: `IGGIGnnsrGIIDIrGTGh`; instruction hits: `none`
- `g5o5ModuloLineInitials`: `NccNchhNNMcNNlNMcMhcb`; instruction hits: `none`
- `g5o5ModuloLastWords`: `a IMF IMF a IMF guy guy a a heart IMF a a Mike a heart IMF heart guy IMF he`; instruction hits: `none`

## Rows

| clue term | index | page-76 word | corridor word | corridor line | G5/O5 modulo line |
|---|---:|---|---|---|---|
| `hid` | `3` | `toxicity` | `believe` | `trolling the International Monetary Fund (IMF) on Twitter?` | `Novogratz in the tweet, figuring he could sell a` |
| `private` | `7` | `Open` | `seen` | `$1 billion in bitcoin — that he should sell` | `collateralized “Volcano Bonds” to pay off the IMF` |
| `Bitcoin` | `7` | `Open` | `seen` | `$1 billion in bitcoin — that he should sell` | `collateralized “Volcano Bonds” to pay off the IMF` |
| `key` | `3` | `toxicity` | `believe` | `trolling the International Monetary Fund (IMF) on Twitter?` | `Novogratz in the tweet, figuring he could sell a` |
| `encoded` | `7` | `Open` | `seen` | `$1 billion in bitcoin — that he should sell` | `collateralized “Volcano Bonds” to pay off the IMF` |
| `piece` | `5` | `some` | `Have` | `I tweeted President Nayib Bukele when he announced` | `hasn't moved on it. I don't really trust that guy.` |
| `wrote` | `5` | `some` | `Have` | `I tweeted President Nayib Bukele when he announced` | `hasn't moved on it. I don't really trust that guy.` |
| `BitcoinMagazine` | `15` | `UTXO` | `International` | `-` | `Novogratz in the tweet, figuring he could sell a` |
| `President` | `9` | `heart` | `president` | `collateralized “Volcano Bonds” to pay off the IMF` | `Novogratz in the tweet, figuring he could sell a` |
| `Nobody` | `6` | `bitcoin` | `you` | `he was going to tap his nation's volcanoes to mine` | `Maybe because he's a shitcoiner at heart.` |
| `figured` | `7` | `Open` | `seen` | `$1 billion in bitcoin — that he should sell` | `collateralized “Volcano Bonds” to pay off the IMF` |
| `out` | `3` | `toxicity` | `believe` | `trolling the International Monetary Fund (IMF) on Twitter?` | `Novogratz in the tweet, figuring he could sell a` |
| `yet` | `3` | `toxicity` | `believe` | `trolling the International Monetary Fund (IMF) on Twitter?` | `Novogratz in the tweet, figuring he could sell a` |
| `20` | `20` | `y'all` | `Twitter` | `-` | `loan and get rid of those leeches. I tagged Mike` |
| `BTC` | `3` | `toxicity` | `believe` | `trolling the International Monetary Fund (IMF) on Twitter?` | `Novogratz in the tweet, figuring he could sell a` |
| `Mirror` | `6` | `bitcoin` | `you` | `he was going to tap his nation's volcanoes to mine` | `Maybe because he's a shitcoiner at heart.` |
| `writing` | `7` | `Open` | `seen` | `$1 billion in bitcoin — that he should sell` | `collateralized “Volcano Bonds” to pay off the IMF` |
| `neurological` | `12` | `It's` | `Salvador` | `bunch to his Wall Street crony pals, but so far he` | `Maybe because he's a shitcoiner at heart.` |
| `reflections` | `11` | `Bitcoin` | `El` | `Novogratz in the tweet, figuring he could sell a` | `hasn't moved on it. I don't really trust that guy.` |
| `unusual` | `7` | `Open` | `seen` | `$1 billion in bitcoin — that he should sell` | `collateralized “Volcano Bonds” to pay off the IMF` |
| `phenomenon` | `10` | `to` | `of` | `loan and get rid of those leeches. I tagged Mike` | `bunch to his Wall Street crony pals, but so far he` |

## Assessment

- Public clue word lengths and the explicit numeric values `20` and `BTC=3` do not provide a clean selector into page 76.
- Direct index streams select ordinary article words, not procedural language such as read/take/word/letter/key.
- Modulo indexing into the G5/O5 six-line interval just cycles through the already-known lower corridor and does not add order.
- This closes public-clue word/number indexing as a standalone local selector.
- The public clue remains useful only for target type (`private Bitcoin key`), source (`piece`), value (`20 BTC`), and operation family (`mirror writing`).

## Next Best Move

- Keep the public clue as constraint language only. The missing selector still has to come from source/visual provenance, a better physical/source image, or an original layout/Canva asset.
