# High-Res Exact Highlight Streams

Inputs are the manual high-res orange and grey/black highlight readings, not OCR.

## Summary

- Orange spans: 20
- Grey/black spans: 14
- Streams generated: 96
- Credible direct WIF/minikey/exact-hex candidates: 2
- Accidental hex-like prose windows ignored: 41
- Contiguous checksum-valid BIP39 12/24-word mnemonics: 0
- Filtered BIP39-word checksum hits, treated as accidental: 11

## High-Signal Streams

- `orange:phrase_initials`: `FKLLTMGbsbTh2ATtETi5`
- `orange:word_initials`: `FIsL1fegttsebiodKydL1L1TatsoaonMGstGsbOyhtBbtrcofmsahbtdTBMwsmhowac2tfcbAl8BwohtiATndtltgtBpEwltoeitrhWagosbaomTsrBwtateimettaswitfsog5SRNHIUSS6FO4m`
- `orange:word_lasts`: `ttsr1rytgtsrndrdpryr1r1yeemflrstteytennrtonyedpftyrttgepcnsnxssdndn2ntksat5Nhfesnnesnteeednlelerneneteeegrskdrststnleleyyetotdehnntsrd5MFANNTHS6LZ3L`
- `grey_black:phrase_initials`: `Dm1GIVSFIsgmww`
- `grey_black:word_initials`: `Dtffsmpbtstcba1bGbtwFyodp1fmnIsasgttgVBSByfftsosoaXGrteshFIdtbmsuRgwmpwtkigwave`
- `grey_black:word_lasts`: `ntlryysgskslks1naesyysfbt1tyetsannoesosynulrtelnrtPtyoenlitssygsssylygsoptgrdey`
- `combined:interleaved_span_phrase_initials`: `FDKmL1LGTIMVGSbFsIbsTghm2wAwTtETi5`

## Per-Page Phrase Initials

- `orange:p75:phrase_initials`: `FKLLTM`
- `orange:p76:phrase_initials`: `Gbsb`
- `orange:p77:phrase_initials`: `Th`
- `orange:p78:phrase_initials`: `2ATt`
- `orange:p79:phrase_initials`: `ETi`
- `orange:p80:phrase_initials`: `5`
- `grey_black:p75:phrase_initials`: `Dm`
- `grey_black:p76:phrase_initials`: `1GIV`
- `grey_black:p77:phrase_initials`: `SFIs`
- `grey_black:p78:phrase_initials`: `gmw`
- `grey_black:p79:phrase_initials`: `w`

## Direct Key Shapes

- Local checksum/key-shape candidates found. These need chain validation before being treated as meaningful:
- minikey from `orange:word_initials` / `reverse_chars`: `SSUHNRS5gosftiwsattemietat`
- minikey from `combined:orange_then_grey:text` / `letters_only`: `SFLZmLDontfaforshitcoi`
- Hex-looking windows made from ordinary prose letters `a-f` are counted separately as accidental and ignored.
- Chain check result: both minikeys were tested as SHA256 minikey secrets across compressed P2PKH, uncompressed P2PKH, P2SH-P2WPKH, P2WPKH, and P2TR addresses. Activity found: 0.

## BIP39 Word Presence

- Highlight spans containing at least one BIP39 word: 25
- This is expected with normal English prose and is not enough by itself.
- orange p75: `Layer, great, thing, that`
- orange p75: `Keep, dignity`
- orange p75: `Layer`
- orange p75: `Layer`
- orange p75: `They, all`
- orange p76: `Open, heart`
- orange p76: `heart`
- orange p77: `six`
- orange p77: `old`
- orange p78: `left, worth`
- orange p78: `game`
- orange p79: `will, live, own, rabbit, hole`
- Additional BIP39-bearing spans omitted from this summary: 13

## Conclusion

- Exact high-res highlighted text does not directly contain a contiguous checksum-valid BIP39 mnemonic, WIF, or exact 64-hex private key.
- Minikey checksum windows can occur by chance inside long prose-derived streams; they require address activity or a strong selector rule before being considered real.
- The useful signal is still selector/order: phrase initials, page grouping, color grouping, and page-76/El-Salvador intersections should be used as labels for geometry, not as direct keys.
- OCR-derived highlight text should stay excluded from text-stream candidate generation.
