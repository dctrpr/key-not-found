# Active Corridor Witness Consistency

Scope: check the exact text witnesses for the active lower page-76 corridor. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

## Target Phrases

| id | phrase | role |
| --- | --- | --- |
| `buying_dip` | `buying the dip` | orange-highlighted target phrase |
| `one_billion` | `$1 billion` | grey-highlighted money phrase |
| `should_sell` | `should sell` | p78-frame source/edge anchor |
| `future_bitcoin_earnings` | `future bitcoin earnings` | p78-frame source band |
| `volcano_bonds` | `Volcano Bonds` | G5 trusted target |
| `imf_loan` | `IMF loan` | G5 neighboring target |
| `tagged_mike` | `I tagged Mike` | lower corridor source band |
| `novogratz` | `Novogratz` | lower corridor source band |
| `trust_that_guy` | `I don't really trust that guy` | Typeka Mix nearby phrase |
| `shitcoiner_heart` | `shitcoiner at heart` | O5 primary target |

## Witness Results

| witness | role | authoritative | present | missing | notes |
| --- | --- | --- | ---: | --- | --- |
| `canonical_plain_article_body` | canonical corrected plain text | `True` | 10/10 | none |  |
| `article_with_fonts_text` | DOCM text/font witness | `True` | 10/10 | none |  |
| `full_article_corrected` | earlier corrected plain text | `True` | 10/10 | none |  |
| `full_article_raw` | earlier plain text | `False` | 10/10 | none |  |
| `user_plain_article_latest` | latest user plain text before correction | `False` | 9/10 | `volcano_bonds` | Contains the corridor sentence with `Volcano Bonds` omitted between `collateralized` and `to pay off the IMF`. |
| `user_markdown_transcript` | user markdown with bold markup | `False` | 10/10 | none |  |
| `user_annotated_transcript` | user prose annotation with formatting notes | `False` | 9/10 | `trust_that_guy` |  |
| `article_3d_map_page76_chars` | 3D viewer OCR/char labels for page 76 | `False` | 6/10 | `buying_dip`, `one_billion`, `volcano_bonds`, `shitcoiner_heart` | Contains the corridor sentence with `Volcano Bonds` omitted between `collateralized` and `to pay off the IMF`. 3D OCR/char labels are incomplete for exact wording; use for navigation only. |

## Important Failure

- `user_plain_article_latest` is not safe as the exact G5 source because it contains the local sentence but omits `Volcano Bonds`.
- `article_3d_map_page76_chars` is not safe as exact text because it misses active targets already identified by source crops and corrected transcript.

## Decision

- Use `analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt` and `analysis_outputs/docm_format_sources/article_with_fonts_text.txt` for exact wording.
- Use the 3D view, bridge sheet, and source crops for geometry/navigation only.
- Do not reopen text/font extraction unless a new source or clue names the extraction unit/order.
