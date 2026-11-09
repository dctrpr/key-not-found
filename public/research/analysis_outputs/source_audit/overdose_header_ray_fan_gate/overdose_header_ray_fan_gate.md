# OVERDOSE Header Ray Fan Gate

Scope: draw straight segments from the page-76 OVERDOSE header center to the locked O4/B4/G5/O5 target centers, then compare them with rays to non-active page-76 highlight centers. This pass only measures existing word/highlight intersections and strict instruction terms; it performs no OCR, hashing, key derivation, seed/WIF checks, address checks, or broad candidate generation.

## Summary
- active rays: `4`
- control rays: `3`
- active strict instruction hits: `0`
- control strict instruction hits: `0`
- active all-quartet rays: `0`
- active ray highlight-hit counts: `[2, 1, 1, 3]`
- control ray highlight-hit counts: `[1, 2, 2]`
- selector unlocked: `False`

## Active Rays

| target | angle | words | focus words | highlights | active highlight stream | strict hits | preview |
|---|---:|---:|---:|---:|---|---|---|
| buying_dip | 107.828 | 11 | 8 | 2 | buying_dip | - | y'all. nothing Luther being stake. back nocoiners' money genitals. chest. ByiiRE |
| one_billion | 126.411 | 20 | 4 | 1 | - | - | heart of Martin a post-1971 Schiff buy shitcoiners' now day have chase Stun defi |
| volcano_bonds | 117.058 | 18 | 9 | 1 | - | - | to y'all. nothing skin burning buying psychotic heads. euthanized ¥ortunately, B |
| shitcoiner_heart | 107.34 | 20 | 11 | 3 | buying_dip|shitcoiner_heart | - | y'all. nothing Luther being stake. bitcoin back nocoiners' genitals. chest. Twit |

## Control Rays

- `p76_orange_1` angle `162.015` words `1` focus `1` highlights `1` strict `-` preview `bitcoin.`
- `p76_orange_2` angle `166.806` words `5` focus `2` highlights `2` strict `-` preview `toxicity. Get some Biteoiny It's`
- `p76_orange_3` angle `138.28` words `14` focus `5` highlights `2` strict `-` preview `heart here, full clones. the bankers years of watching honéy-badgering dulled unconscious, "I'riends`

## Decision

- Do not promote OVERDOSE header rays as a selector.
- Active rays do not traverse the full active quartet and do not produce strict instruction wording.
- Control highlight rays are not worse in kind, so the ray fan is a visual aid rather than extraction permission.

## Outputs
- JSON: `analysis_outputs/source_audit/overdose_header_ray_fan_gate/overdose_header_ray_fan_gate.json`
- visual sheet: `analysis_outputs/source_audit/overdose_header_ray_fan_gate/overdose_header_ray_fan_gate_sheet.jpg`
