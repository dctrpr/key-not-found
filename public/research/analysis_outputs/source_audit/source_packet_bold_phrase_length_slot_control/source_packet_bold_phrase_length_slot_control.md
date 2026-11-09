# Source Packet Bold Phrase Length Slot Control

- Active rows checked: `4`.
- Non-active grey control rows checked: `13`.
- Active word-count equals touched-slot-count rows: `4/4`.
- Non-active grey control word-count equals touched-slot-count rows: `3/13`.
- p75 `OVER` control also matches word-count/span-count: `True`.
- All-active count-to-center-slot fit metrics: `0`.
- Best partial count-to-center-slot fit: `2/4`.
- Source count/length cue hits: `0`.
- Generated/report count cue hits: `0`.
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
- Fingerprint: `active=4|controls=13|activeWordSpan=4/4|controlWordSpan=3/13|p75OverWordSpan=1|allCenterFitMetrics=0|partialCenterFitMax=2|sourceCountCues=0|generatedCountCues=0|sourceR3=0|triggers=0/9|selectors=0`.

Focused rows:

- `active` `O4`: text `buying the dip`, span `DOS`, word count `3`, word lengths `6,3,3`, alnum `12`, glyph/no-space `12`, highlight count `14`, word-count/span-count match `True`, layout `-`.
- `active` `B4`: text `$1 billion`, span `OV`, word count `2`, word lengths `2,7`, alnum `8`, glyph/no-space `9`, highlight count `10`, word-count/span-count match `True`, layout `-`.
- `active` `G5`: text `Volcano Bonds`, span `ER`, word count `2`, word lengths `7,5`, alnum `12`, glyph/no-space `12`, highlight count `13`, word-count/span-count match `True`, layout `-`.
- `active` `O5`: text `shitcoiner at heart`, span `RDO`, word count `3`, word lengths `10,2,5`, alnum `17`, glyph/no-space `17`, highlight count `19`, word-count/span-count match `True`, layout `-`.
- `control_grey` `p75_grey_2`: text `terrorists, stock traders, central bank arsonists`, span `OVERDO`, word count `6`, word lengths `10,5,7,7,4,9`, alnum `42`, glyph/no-space `44`, highlight count `None`, word-count/span-count match `True`, layout `OVER`.
- `control_grey` `p75_grey_3`: text `Don't fall for shitcoinery`, span `OVER`, word count `4`, word lengths `5,4,3,11`, alnum `22`, glyph/no-space `23`, highlight count `None`, word-count/span-count match `True`, layout `OVER`.
- `control_grey` `p76_grey_1`: text `Gotta be this way... post-1971 fiat money`, span `OVERDOSE`, word count `8`, word lengths `5,2,4,3,4,4,4,5`, alnum `31`, glyph/no-space `35`, highlight count `None`, word-count/span-count match `True`, layout `OVER,DOSE,OVERDOSE`.
- `control_grey` `p77_grey_1`: text `Sorry Bhutan... shitcoin hell`, span `OVERDOS`, word count `4`, word lengths `5,6,8,4`, alnum `23`, glyph/no-space `26`, highlight count `None`, word-count/span-count match `False`, layout `OVER`.
- `control_grey` `p78_grey_1`: text `gargantuanly wasteful`, span `DOSE`, word count `2`, word lengths `12,8`, alnum `20`, glyph/no-space `20`, highlight count `None`, word-count/span-count match `False`, layout `DOSE`.

Decision: phrase count and length mechanics do not reopen OVERDOSE-slot extraction.
