# P78 Graphic Edge Reconciliation

Scope: test whether the reflected p78 graphic edges/corners reconcile the broad #4 band with the #5 G5/O5 pair. No key candidates, hashes, seed phrases, or address checks were generated.

- Created: `2026-05-20T06:39:33`
- Reflected p78 box on p76: `[1234, 2398, 2250, 2950]`
- Overlay: `analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation_overlay.jpg`

## Edge Contacts

| candidate | overlap | edge contacts | nearest corner |
|---|---:|---|---|
| `shitcoiner at heart` | 0.2475 | left cuts dist=0.0px overlap=18.0px; bottom cuts dist=0.0px overlap=427.0px | `bottomLeft` 0.0px |
| `should sell` | 0.7635 | left cuts dist=0.0px overlap=35.53px; top cuts dist=0.0px overlap=205.33px | `topLeft` 0.0px |
| `earnings` | 0.9331 | left cuts dist=0.0px overlap=40.11px | `topLeft` 69.15px |
| `trust that guy` | 1.0 | left left-adjacent dist=11.34px overlap=44.57px | `bottomLeft` 79.18px |
| `I tagged Mike` | 1.0 | left left-adjacent dist=24.41px overlap=44.56px | `topLeft` 212.5px |
| `Volcano Bonds` | 0.0 | left right-adjacent dist=38px overlap=48px | `topLeft` 150.86px |
| `pay off the IMF` | 1.0 | left left-adjacent dist=44.51px overlap=44.57px | `topLeft` 144.39px |

## Corner Nearest Words

- `topLeft`: `should`(0.0px), `volcanoes`(37.13px), `he`(66.39px), `earnings`(69.15px), `nation's`(72.88px)
- `topRight`: `Bitcoin`(486.06px), `Twitter?`(537.65px), `ByiiREeraipy"`(538.19px), `announced`(577.16px), `Magazine`(607.02px)
- `bottomLeft`: `siukbeodmensertslveaarty`(0.0px), `trust`(79.18px), `really`(82.61px), `pals,`(151.03px), `that`(166.61px)
- `bottomRight`: `siukbeodmensertslveaarty`(629.02px), `he`(686.1px), `guy`(690.74px), `IMF`(741.73px), `far`(749.4px)

## Assessment

- The filled p78 graphic remains broad, but the reflected p78 box edges do reconcile it with the #5 pair.
- The left edge runs immediately to the right of trusted G5 `Volcano Bonds` with a 38px gap and vertical overlap.
- The bottom edge cuts O5 `shitcoiner at heart`; the bottom-left corner lies inside O5.
- The top edge also cuts the #4 source row around `should sell`, explaining why the filled graphic selected #4 band words.
- This upgrades p78 graphic support for G5/O5 from broad corridor evidence to edge/framing evidence, but it still does not specify a final extraction unit.

Next move: Treat the p78 graphic as a frame: top edge starts in the #4 source band, left/bottom edges frame G5/O5. Next test should inspect edge order/corners only, not the filled mask.
