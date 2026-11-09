# P78 Frame Order Read

Scope: read only the reflected p78 frame edges/corners. The filled mask is ignored. No key candidates, hashes, seed phrases, or address checks were generated.

- Created: `2026-05-20T06:43:43`
- Reflected p78 box on p76: `[1234, 2398, 2250, 2950]`
- Overlay: `analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read_overlay.jpg`

## Edge Streams

- `topEdgeLeftToRight`: `should sell`
- `leftEdgeTopToBottom`: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `leftEdgeBottomToTop`: `shitcoiner at heart | trust that guy | could sell | I tagged Mike | Volcano Bonds | pay off the IMF | earnings | should sell`
- `bottomEdgeLeftToRight`: `shitcoiner at heart`
- `bottomEdgeRightToLeft`: `shitcoiner at heart`
- `lShapeTopLeftDown`: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`
- `lShapeReverse`: `shitcoiner at heart | trust that guy | could sell | I tagged Mike | Volcano Bonds | pay off the IMF | earnings | should sell`
- `minimalCornerFrame`: `should sell | Volcano Bonds | shitcoiner at heart`
- `minimalCornerFrameInitials`: `svs`
- `leftEdgeInitialsTopDown`: `sepvicts`
- `leftEdgeInitialsBottomUp`: `stcivpes`
- Instruction-term hits: `{}`
- Action-phrase observation: `should sell Volcano Bonds`

## Edge Events

| edge | order | label | relation | distance | overlap |
|---|---:|---|---|---:|---:|
| `top` | 1 | `should sell` | `cuts` | 0.0 | 205.33 |
| `left` | 1 | `should sell` | `cuts` | 0.0 | 35.53 |
| `left` | 2 | `earnings` | `cuts` | 0.0 | 40.11 |
| `left` | 3 | `pay off the IMF` | `left-adjacent` | 44.51 | 44.57 |
| `left` | 4 | `Volcano Bonds` | `right-adjacent` | 38 | 48 |
| `left` | 5 | `I tagged Mike` | `left-adjacent` | 24.41 | 44.56 |
| `left` | 6 | `could sell` | `left-adjacent` | 51.54 | 40.11 |
| `left` | 7 | `trust that guy` | `left-adjacent` | 11.34 | 44.57 |
| `left` | 8 | `shitcoiner at heart` | `cuts` | 0.0 | 18.0 |
| `bottom` | 1 | `shitcoiner at heart` | `cuts` | 0.0 | 427.0 |

## Corners

| corner | nearest labels |
|---|---|
| `topLeft` | `should sell` (0.0px), `earnings` (69.15px), `pay off the IMF` (144.39px), `Volcano Bonds` (150.86px) |
| `topRight` | `pay off the IMF` (657.32px), `I tagged Mike` (738.74px), `could sell` (774.33px), `shitcoiner at heart` (795.03px) |
| `bottomRight` | `shitcoiner at heart` (589.0px), `trust that guy` (690.74px), `pay off the IMF` (741.73px), `could sell` (752.71px) |
| `bottomLeft` | `shitcoiner at heart` (0.0px), `trust that guy` (79.18px), `could sell` (229.55px), `I tagged Mike` (297.35px) |

## Assessment

- Frame reading produces a coherent article phrase path, not a puzzle extraction instruction.
- The strongest minimal frame phrase is `should sell | Volcano Bonds | shitcoiner at heart`.
- `should sell Volcano Bonds` is semantically coherent in the article context, but it does not name an extraction unit such as word, letter, line, key, or mirror.
- The left-edge stream is `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`, again ordinary corridor prose.
- Close p78 frame-order streams as standalone selectors; keep p78 as a frame/registration clue for the G5/O5 target pair.

Next move: Inspect whether the G5/O5 pair plus the phrase `should sell Volcano Bonds` points to a public/source instruction outside page 76, such as the original tweet/Canva clue or physical p78 graphic labels.
