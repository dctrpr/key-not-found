# The scans leave page 75’s first break unresolved

The first line ends with `reaction` and the second starts with `to`. The sharper scan puts the estimated appended word beyond the second line’s visible footprint. The lower-resolution scan leaves an overlap after measurement allowances. Neither scan establishes the original right edge of the text frame or confirms spare room for the word.

## Measured bounds

Each coordinate is a horizontal native-pixel position in its own scan. The lower-resolution positions follow the opening lines’ mean baseline slope. The candidate bounds include all three reference gaps and contrast thresholds, with both baseline inventories used for the lower-resolution scan.

| Scan | Appended word’s right endpoint | Row 2 lower bound before the period | Row 2 upper extent including period | Minimum candidate minus upper extent |
| --- | ---: | ---: | ---: | ---: |
| Sharper | 1723.4–1740.6 | 1691.0 | 1715.0 | +8.4 px |
| Lower resolution | 1327.2–1352.1 | 1310.5 | 1331.7 | −4.5 px |

Both scans passed the registered left-edge and reference-width checks. The upper appended endpoint exceeds the conservative pre-period bound by 49.6 and 41.6 pixels respectively. The visible footprint supplies only a conditional lower bound on the full measure. Even the sharper scan’s excess over the full ink extent leaves room for a wider original text frame. The two scans do not establish whether the next word actually fit. [All nine threshold and baseline conditions](MEASUREMENTS.json) · [Comparison chart](WORD_FIT_COMPARISON.png)

## Evidence that would resolve the break

The strongest witness would be a publisher-authorized production excerpt for the first paragraph of printed page 75 in Issue 24. A native layout or documented view with the text-frame boundary, composition settings and hidden characters visible could distinguish a hard or soft return after `reaction` from automatic line composition. A dated author draft could establish whether a break was present before layout. Even an explicit break would still need evidence connecting it to Keiser’s clues. [Publisher’s Issue 24 listing](https://store.bitcoinmagazine.com/collections/featured-issues/products/el-salvador-issue)

A vector press proof could improve the glyph measurements. It ordinarily leaves the nonprinting break markers invisible. A paragraph composer can also place a word on the next line even if a line-by-line fit test would allow it. These are documented production possibilities. The two retained scans do not identify the software or composer used on page 75. [Adobe composition documentation](https://helpx.adobe.com/indesign/desktop/format-and-style-text/composition-and-text-wrapping/set-text-composition.html) · [Adobe hidden characters documentation](https://helpx.adobe.com/indesign/desktop/language-and-proofing/glyphs-characters-and-expressions/hidden-character-glossary.html)

Keep the printed break in the transcription. Leave the forced-break hypothesis open until the production witness or an independently specified pattern across other lines can distinguish it.

## Replay

The [protocol](PROTOCOL.md) was [registered before scoring](https://github.com/dctrpr/key-not-found/commit/c7976ababb7ce4ef3099b1d7717b29bb15224967). Synthetic fit, overlap, footprint-excess and locator checks passed. The two runs on the source PDFs reproduced byte for byte. [Receipt](RESULT.json)

```sh
python3 public/research/scripts/measure_page75_word_fit.py --out word-fit.json
python3 public/research/scripts/render_page75_word_fit.py --input word-fit.json --out word-fit.png
```
