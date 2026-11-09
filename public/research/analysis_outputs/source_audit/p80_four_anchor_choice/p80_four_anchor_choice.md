# P80 Four-Anchor Choice Audit

Scope: bounded test of whether p80 package/pill copy chooses among the four active page-76 anchors. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-20T19:27:36`
- P80 source: `analysis_outputs/3d_article_map/p80_package_copy_audit.json`
- Anchor source: `analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json`

## Anchor Order

| index | anchor | color |
|---:|---|---|
| `1` | `buying the dip` | `orange` |
| `2` | `$1 billion` | `black` |
| `3` | `Volcano Bonds` | `black` |
| `4` | `shitcoiner at heart` | `orange` |

## Direct P80 Matches

| p80 term | best anchor(s) | evidence |
|---|---|---|
| `product`: `Bitcoin FixesThis` | `$1 billion` | $1 billion: label=[] context=['bitcoin'] substr=[] |
| `symptoms`: `NAUSEA HEARTBURN INDIGESTION UPSET STOMACH SHITCOINS` | `shitcoiner at heart` | shitcoiner at heart: label=['shitcoin'] context=[] substr=['heartburn<->heart', 'shitcoin<->shitcoiner'] |
| `symptom:HEARTBURN`: `HEARTBURN` | `shitcoiner at heart` | shitcoiner at heart: label=[] context=[] substr=['heartburn<->heart'] |
| `symptom:SHITCOINS`: `SHITCOINS` | `shitcoiner at heart` | shitcoiner at heart: label=['shitcoin'] context=[] substr=['shitcoin<->shitcoiner'] |

## Number Check

- Numbers seen on p80: `[5, 100, 16, 473, 6, 80]`
- Four-anchor modulo choices are registered in JSON only; they are treated as arbitrary because no p80/source text asks for modulo.

## Assessment

- The p80 copy does not choose all four page-76 anchors.
- Lexical signal collapses onto O5/shitcoiner at heart: SHITCOINS matches shitcoiner, and HEARTBURN weakly matches heart.
- The black-anchor hits are context-only or absent: Bitcoin FixesThis touches the $1 billion line because the line contains bitcoin, while no p80 term names amount/billion/Volcano/Bonds.
- The repeated number 5 conflicts with a four-anchor selector unless an extra rule supplies a fifth unit; modulo-4 number choices are arbitrary and repeat only anchors 1/4.
- P80 therefore remains thematic/count corroboration, not the missing chooser for OBBO.

## Decision

- Do not use p80 package copy as a four-anchor chooser without a new alignment/source clue.

## Next Move

- Return to geometry: inspect whether p80 bottle/package regions physically align to page 76 anchors under the existing fold/mirror models; if not, keep p80 closed.
