# Related Word Artifacts Audit

Scope: inspect two likely Word artifacts by filename only: `Text_by_sentences.docx` and `macro data.docx`. No key derivation, hashing, BIP39 use, WIF, seed, or address checks were run.

- Created: `2026-05-20T11:14:58`
- Puzzle-related by keyword: `['Text_by_sentences.docx']`

## Text_by_sentences.docx

- Path: `private_inputs/Desktop/Text_by_sentences.docx`
- MD5: `8fe5a7e0fdb36b37459a930b4f1fecda`
- Size: `9759` bytes
- Creator: ``
- Created: `2023-04-26T20:27:40Z`
- Modified: `2023-04-26T20:28:08Z`
- Paragraphs / words / chars: `172` / `1280` / `7655`
- Special parts: `{'comments': [], 'vba': [], 'customXml': [], 'media': [], 'embeddings': []}`
- Hidden runs: `0`
- Term hits: `{'bitcoin': 32, 'toxic': 5, 'keiser': 1, 'max': 1, 'shitcoin': 1, 'satoshi': 1, 'take': 1}`

### Hit Excerpts
- `bitcoin`: `Bitcoin is toxic af Here's the bitter truth. Bitcoin was not a reaction to the Global Financial Crisis of 2008.`
- `bitcoin`: `Bitcoin is toxic af Here's the bitter truth. Bitcoin was not a reaction to the Global Financial Crisis of 2008. It caused it. Really? Yes The markets sensed`
- `bitcoin`: `to the Global Financial Crisis of 2008. It caused it. Really? Yes The markets sensed Bitcoin was coming and started to crash. Markets are like that. They discount stuff in advance. Markets are the`
- `bitcoin`: `ing terrorists, stock traders, central bank arsonists, Wall Street and Jamie Dimon. The Bitcoin rabbit hole was opening — the black hole of the Cosmic Now — and it had fiat markets in its sight. In fact,`
- `bitcoin`: `markets in its sight. In fact, all the chaos you see around you these days is caused by Bitcoin. And nothing could be better. (15)Nocoiners and shitcoiners, and even some Bitcoiners, consider this view`
- `bitcoin`: `and even some Bitcoiners, consider this view toxic. Everybody's complaining about "Toxic Bitcoin Maximalists" these days. Look, toxicity is Layer 1 of the protocol. Fact: It's Layer 1 for every great thin`
- `bitcoin`: `proof of stake at the mEthereum lab. Don't fall for shitcoinery. Keep your dignity. Go Bitcoin Toxic Maximalist, the Layer 1 of the whole Satoshi experience. You wouldn't be digging blindly with your bar`
- `bitcoin`: `Satoshi experience. You wouldn't be digging blindly with your bare hands in the muck of Bitcoin's rabbit hole if this weren't true. Anything worth hearing is hard to listen to. Nice, pleasant words fro`
- `bitcoin`: `itcoiners are easy listening for the gullible and unloved. Get some toxicity. Get some bitcoin. Open your heart to Bitcoin. It's the freaking UTXO ghetto up in here, y'all. It's funkier than a whole`
- `bitcoin`: `or the gullible and unloved. Get some toxicity. Get some bitcoin. Open your heart to Bitcoin. It's the freaking UTXO ghetto up in here, y'all. It's funkier than a whole parallel universe full of noth`

## macro data.docx

- Path: `private_inputs/Documents/macro data.docx`
- MD5: `c2e6e1b824071f426085355609bdb3f9`
- Size: `321427` bytes
- Creator: `python-docx`
- Created: `2013-12-23T23:15:00Z`
- Modified: `2013-12-23T23:15:00Z`
- Paragraphs / words / chars: `32` / `259` / `1497`
- Special parts: `{'comments': [], 'vba': [], 'customXml': ['customXml/item1.xml', 'customXml/_rels/item1.xml.rels', 'customXml/itemProps1.xml'], 'media': ['word/media/image1.png'], 'embeddings': []}`
- Hidden runs: `0`
- Term hits: `{'macro': 1, 'line': 1}`

### Hit Excerpts
- `macro`: `Macro Data U.S. equity market value and wages as a share of GDP Figure 1. Solid lines are observed data; dotted li`
- `line`: `GDP, while wage and salary accruals were 42.0% of GDP. Projection note: using a straight-line trend fitted to the last 40 quarters, the 2030 Q4 baseline is 2.75x GDP for the equity-value ratio and 41.4%`

## Assessment

- Only files with puzzle keywords or hidden instruction structure should affect the solve path.
- If neither file contains `bitcoin` / `toxic` / `bip39` / `otrobip` / `typeka` / page-76 corridor terms, they are not source artifacts for this puzzle.
- This pass does not reopen BIP39 or key-generation branches.
