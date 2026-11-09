# Page 76 Anchor Adjacency Units

Scope: small source-gated adjacency/unit audit around the four active page-76 anchors. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-20T19:20:54`
- Overlay source: `analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.json`

## Anchor Reads

| anchor | style | same-line left edge | same-line right edge | above center | below center |
|---|---|---|---|---|---|
| `buying the dip` | `orange; Typeka; bold 1.0; hl {'yellow': 14}` | `he's` | `-` | `on` | `announced` |
| `$1 billion` | `black; Typeka; bold 1.0; hl {'black': 10}` | `-` | `in` | `was` | `billions` |
| `Volcano Bonds` | `black; Typeka; bold 1.0; hl {'black': 13}` | `collateralized` | `to` | `future` | `those` |
| `shitcoiner at heart` | `orange; Typeka; bold 1.0; hl {'yellow': 19}` | `a` | `-` | `trust` | `-` |

## Compact Streams

- `visualOrderColors`: `OBBO`
- `visualOrderPhraseInitials`: `btd 1b vb sah`
- `visualOrderPhraseEdges`: `bp 1n vs st`
- `visualOrderRightBoundaryWords`: `- | in | to | -`
- `visualOrderLeftBoundaryWords`: `he's | - | collateralized | a`
- `visualOrderAboveCenterWords`: `on | was | future | trust`
- `visualOrderBelowCenterWords`: `announced | billions | those | -`
- `blackThenOrangeInitials`: `1b vb btd sah`
- `orangeThenBlackInitials`: `btd sah 1b vb`

## Assessment

- Adjacency around the four anchors gives coherent local context but no instruction-like message.
- The only compact structure is the color order O-B-B-O and the paired highlight classes: black amount/bond anchors, orange action/identity anchors.
- Right-boundary words mostly reproduce prose continuation rather than a selector: buying dip has no right word, $1 billion points to in/bitcoin, Volcano Bonds points to to/pay, O5 has no right word.
- Vertical center probes land on ordinary corridor prose and do not form read/fold/mirror/page/line/word/letter instructions.
- This closes typography-adjacency as a standalone rule unless a new source tells us which side or edge to read.

## Decision

- Do not promote anchor adjacency to extraction evidence; it is only a local context check.

## Next Move

- Use the O-B-B-O anchor structure as a comparison signature against OVERDOSE/package/pill layout mechanics, especially whether other Max articles use the same four-anchor pattern.
