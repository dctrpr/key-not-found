# BOLD.docm Highlighted Text Reconstruction

Scope: reconstruct the actual yellow-highlighted text in `BOLD.docm` from the recovered Word run layer. No macros were executed, and no extraction, hashing, BIP39, WIF/Base58 scanning, OCR extraction, seed generation, or address checks were run.

- Created: `2026-05-21T00:19:59`
- Sheet: `analysis_outputs/docm_format_sources/bold_highlighted_text_reconstruction/bold_highlighted_text_reconstruction_sheet.jpg`
- Decision: `bold_highlighted_stream_not_source_or_selector`

## Summary

- Yellow-highlighted runs: `43`.
- Highlighted words: `43`.
- Highlighted fonts: `Typeka`.
- Highlighted bold values: `True`.
- Locked active targets in BOLD full text: `0/4`.
- Locked active targets in highlighted stream: `0/4`.
- Instruction-like highlighted terms: `right, one, loan`.

## Highlighted Word Stream

`You rabbit hole this true loan ONE OTHER GOLD never economy that love before until Love inner economy love more ALL THIS oil perfect Remove you remove gap love into right there Poverty because because express sea all connect rabbit hole peace love`

## Phrase Coverage

| phrase | role | in BOLD text | in highlighted stream | highlighted token overlap |
|---|---|---:|---:|---|
| `buying the dip` | locked active page-76 target | `False` | `False` | `` |
| `$1 billion` | locked active page-76 target | `False` | `False` | `` |
| `Volcano Bonds` | locked active page-76 target | `False` | `False` | `` |
| `shitcoiner at heart` | locked active page-76 target | `False` | `False` | `` |
| `El Salvador` | active-corridor or target-adjacent context | `False` | `False` | `` |
| `International Monetary Fund` | active-corridor or target-adjacent context | `False` | `False` | `` |
| `IMF` | active-corridor or target-adjacent context | `True` | `False` | `` |
| `Nayib Bukele` | active-corridor or target-adjacent context | `True` | `False` | `` |
| `should sell` | active-corridor or target-adjacent context | `False` | `False` | `` |
| `future bitcoin earnings` | active-corridor or target-adjacent context | `False` | `False` | `` |
| `IMF loan` | active-corridor or target-adjacent context | `True` | `False` | `loan` |
| `Mike Novogratz` | active-corridor or target-adjacent context | `False` | `False` | `` |
| `trust that guy` | active-corridor or target-adjacent context | `False` | `False` | `` |

## Paragraph Reconstruction

| paragraph | highlighted words | context |
|---:|---|---|
| `4` | `You rabbit hole this true` | You wouldn't be digging blindly with your bare hands in the muck of Bitcoin's rabbit hole if this weren't true. |
| `8` | `loan` | IMF loan |
| `10` | `ONE OTHER GOLD` | EVERY SINGLE ONE OF THE BITCOIN WANNABES - BCH, BSV, ETH, XRP, ADA, AND 12,000 OTHER SHITCOINS, PLUS FIAT MONEY AND GOLD - IS FACI |
| `11` | `never economy that love before until` | We've never had an economy and a money that incentivizes love before until bitcoin. |
| `12` | `Love inner` | Love opens up the collective unconscious and our joint inner cosmic being. |
| `13` | `economy love more` | The economy of love is infinitely more efficient than hate and war. |
| `16` | `ALL THIS oil perfect` | BITCOIN FIXES ALL THIS by replacing oil-dripping, corpse-ridden, poppy-harvesting fiat money with perfect bitcoin. |
| `17` | `Remove you remove` | Remove the war incentive, and you remove the hate incentive. |
| `18` | `gap love` | Bitcoin fills in the gap with love; our most natural tendency if given a chance. |
| `19` | `into` | It's a fact baked into |
| `20` | `right there` | observable by anyone choosing to see it, right there in the Genesis Block. |
| `21` | `Poverty because because express sea all connect` | Poverty disappears because the fear of being poor disappears because Bitcoin allows us to fully express ourselves individually in  |
| `22` | `rabbit hole` | Bitcoin rabbit hole |
| `24` | `peace love` | as Bitcoin conquers fear and hate and replaces it with peace and love. |

## Assessment

- The highlighted stream contains none of the locked active O4/B4/G5/O5 targets.
- `IMF loan` is only a partial context overlap: `loan` is highlighted, but `IMF` is not.
- The highlighted word `right` is generic context from `right there in the Genesis Block`; it is not paired with a source-backed unit/order instruction.
- The stream is consistent with a generated BIP39/word-list markup artifact already identified by the macro audit, not with native page-76 source typography.

## Next Move

- Keep BOLD.docm on the generated-artifact branch; reopen only if `otrobip.txt` or original workflow/source files are recovered and pass R1-R5.
