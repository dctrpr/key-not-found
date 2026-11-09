# G5 Axis Bold/Highlight Rescue Gate

Scope: test whether the G5-centered page-line/corridor mirror near miss becomes a selector when constrained to bold/highlight-bearing reflected rows. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T04:03:44`
- Sheet: `analysis_outputs/source_audit/g5_axis_bold_highlight_rescue_gate/g5_axis_bold_highlight_rescue_gate_sheet.jpg`

## Summary

- Axis page line / corridor: `27` / `9`.
- Active hits: `3`.
- Active misses: `1`.
- Non-active signal hits: `1`.
- Reflected style stream: `OBGO`.
- Reflected active-target stream: `shitcoiner_heart|-|volcano_bonds|buying_dip`.
- Initial stream: `MNcH`.
- Last-initial stream: `haId`.
- Bold stream length: `35`.
- Bold stream: `shitcoineratheartNvzIMFbuyingthedip`.
- Partial-bold stream: `Nvz`.
- Strict instruction hits: `0`.

## Active-Order Reflections

- `buying_dip` -> L`32`/C`14` `active` `O`: `Maybe because he's a shitcoiner at heart.`
- `one_billion` -> L`29`/C`11` `bold_control` `B`: `Novogratz in the tweet, figuring he could sell a`
- `volcano_bonds` -> L`27`/C`9` `active` `G`: `collateralized “Volcano Bonds” to pay off the IMF`
- `shitcoiner_heart` -> L`22`/C`4` `active` `O`: `He's taunting them, telling them he's “buying the dip.”`

## Decision

- Do not promote the G5-centered mirror axis via a bold/highlight rescue filter.
- The B4 reflection remains the non-active `Novogratz in the tweet, figuring he could sell a` row; it is signal-bearing but not one of the locked active targets.
- The reflected bold and initial streams are ordinary corridor material and supply no unit/order instruction.
- Reopen only if a new source/clue explicitly names Novogratz/sell as a replacement for B4 or names a line/corridor mirror unit/order rule.
