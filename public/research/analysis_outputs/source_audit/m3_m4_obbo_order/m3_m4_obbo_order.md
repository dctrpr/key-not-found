# M3/M4 O-B-B-O Ordering Audit

Scope: bounded M3/M4 ordering audit over the four page-76 OBBO anchors. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-20T19:34:07`
- Overlay: `analysis_outputs/source_audit/m3_m4_obbo_order/m3_m4_obbo_order_overlay.jpg`
- Axis intersection vertex: `[999.28, 2900.36]`

## Anchor Metrics

| anchor | color | M3 center | M4 center | M3 axis | M4 axis | inside wedge |
|---|---|---:|---:|---:|---:|---|
| `buying the dip` | `orange` | `987.18` | `996.78` | `643.83` | `799.39` | `False` |
| `$1 billion` | `black` | `1827.67` | `1563.82` | `521.86` | `382.84` | `False` |
| `Volcano Bonds` | `black` | `1374.8` | `1109.77` | `330.79` | `325.34` | `False` |
| `shitcoiner at heart` | `orange` | `1028.24` | `637.57` | `94.56` | `12.39` | `True` |

## Ordering Streams

- `visualTopToBottom`: `buying the dip | $1 billion | Volcano Bonds | shitcoiner at heart`
- `nearestM3Center`: `buying the dip | shitcoiner at heart | Volcano Bonds | $1 billion`
- `nearestM4Center`: `shitcoiner at heart | buying the dip | Volcano Bonds | $1 billion`
- `nearestAnyAxis`: `shitcoiner at heart | Volcano Bonds | $1 billion | buying the dip`
- `m3ProjectionForward`: `buying the dip | shitcoiner at heart | Volcano Bonds | $1 billion`
- `m4ProjectionForward`: `buying the dip | shitcoiner at heart | Volcano Bonds | $1 billion`
- `insideWedge`: `shitcoiner at heart`
- Instruction hits: `{}`

## Assessment

- M3/M4 do not order all four O-B-B-O anchors.
- The M3/M4 wedge selects only the O5 endpoint (`shitcoiner at heart`) among the four anchors.
- Distance and projection rankings are dominated by geometry around the lower-right endpoint; they do not produce an instruction-like sequence.
- G5/Volcano Bonds is not chosen by the M3/M4 wedge; it remains part of the p78 frame/G5/O5 path, not the standalone mark path.
- M3/M4 should stay classified as endpoint/bracket evidence for O5, not as the final extraction-order rule.

## Decision

- Do not use M3/M4 as an OBBO ordering selector; keep them as O5 endpoint/bracket evidence.

## Next Move

- Return to the p78 frame/G5/O5 source-registration path and ask what external/source rule supplies the extraction unit.
