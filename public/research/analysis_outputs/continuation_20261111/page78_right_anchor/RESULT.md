# Right alignment repeats across three pages

The last paragraph on page 78 has a shared right margin in both retained scans. A paragraph on page 77 and the closing paragraph on page 79 pass the same right-alignment test in both scans. Right alignment alone therefore cannot pick out the page 78 paragraph from the neighboring print.

## Measured edges

These spans are rounded native pixels at the middle shade threshold. Low-resolution positions are projected along each block’s median row slope. Every classification held at all three registered thresholds in both scans.

| Printed rows | Layout | Sharper left / right span | Lower-resolution left / right span |
| --- | --- | ---: | ---: |
| Page 77, 8–16 | Right | 397 / 17 | 315 / 14 |
| Page 77, 17–21 | Center | 360 / 359 | 285 / 286 |
| Page 78, 1–5 | Left | 3 / 267 | 2 / 210 |
| Page 78, 6–14 | Mixed or unresolved | 305 / 448 | 242 / 357 |
| Page 78, 15–18 | Left | 4 / 554 | 2 / 441 |
| **Page 78, 19–22** | **Right** | **960 / 4** | **766 / 3** |
| Page 79, 22–25 | Right | 280 / 1 | 222 / 1 |

The midpoint of the page 77 display quote varies by about three and two pixels respectively. The page 78 target’s right span is about 0.16% and 0.12% of the corresponding raster widths at the middle threshold. These values describe contrast support, which can include highlight bars. [Full measurements](MEASUREMENTS.json) · [Alignment comparison](ALIGNMENT_COMPARISON.png)

## Reading direction

Two visual reviews checked the upright page 78 paragraph and its nearby display art in both scans. Both saw ordinary letter orientation and recognized no explicit instruction such as an arrow or reversed print. The ending “right there in the Genesis Block” reads as part of the preceding sentence about the Bitcoin protocol. Its wording could carry a second meaning, which the margin measurement does not resolve.

The controls were chosen by visual inspection of neighboring print. The scans’ acquisition histories and the original typesetting coordinates remain unknown. A readable printed cue or a creator-linked statement could reopen the direction hypothesis. For the line-boundary hypothesis, a separate source test can ask whether an intact word would have fit before a physical line break in the plain opening paragraph on page 75.

## Replay

The [method and inputs](PROTOCOL.md) were [registered before scoring](https://github.com/dctrpr/key-not-found/commit/adea7aa1f66e4c69d8e481b5c5718b81d706449e). Synthetic flat and sloped controls passed the left, center and right checks, and a clipped lane was rejected. Two executions on the pinned scans produced byte-identical measurement receipts. [Result receipt](RESULT.json)

```sh
python3 public/research/scripts/measure_page78_right_anchor.py --out alignment.json
python3 public/research/scripts/render_page78_right_anchor.py --input alignment.json --out alignment.png
```
