# Corrected Topology 77 -> 76 Light-Table Audit

Scope: test the external proposal that page 77, not page 75, is the physical back-side partner of page 76. This is visual/source triage only; no key derivation, hashing, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-06-09T22:27:36`
- Source/target: page `77` -> page `76`
- Modes checked: `243`
- Control boxes per target: `{'O4': 64, 'B4': 64, 'G5': 64, 'O5': 64}`
- White-mask whole-page coverage: `0.079801`
- Sheet: `analysis_outputs/source_audit/corrected_topology_77_76_light_table/corrected_topology_77_76_light_table_sheet.jpg`
- Fingerprint: `pair=77->76|whiteMask=0.0798|grid=dxdy+-80x20,rot=-1/0/+1|modes=243|all4Signal=0|bestGe10=3/4|bestGtP95=1/4|paperConfirmed=0|sourceR3=0|selectors=0`

## Step 0: Topology Texture Check

- Old assumed leaves: `[(75, 76), (77, 78), (79, 80)]`.
- Proposed corrected leaves: `[(74, 75), (76, 77), (78, 79)]`.
- Paper-texture fingerprint: `oldBest=1/3|oldAboveP95=1/3|corrBest=1/3|corrAboveP95=0/3|oldMean=0.2384|corrMean=0.1725|controlP95=0.3018|confirmed=0`.
- Topology confirmed by paper texture: `False`.

| class | hmirror best | hmirror above control p95 | mean hmirror corr | best transforms |
|---|---:|---:|---:|---|
| old assumed | `1/3` | `1/3` | `0.238384` | `{'75/76': 'identity', '77/78': 'hmirror', '79/80': 'rot180'}` |
| proposed corrected | `1/3` | `0/3` | `0.172497` | `{'74/75': 'identity', '76/77': 'vmirror', '78/79': 'hmirror'}` |

## Step 1: Page 77 White-Mask Landing

- Best mode: `hmirror p77 white, rot=-1.0, dx=-40, dy=+0`.
- Best active boxes with >=10% source coverage: `3/4`.
- Best active boxes above same-size nearby-control p95: `1/4`.
- All-four signal candidate modes: `0`.
- Source-backed R3 bridge hits: `0`.
- Selector unlocked: `False`.

| target | source coverage | control p95 | percentile | source-only | above p95 |
|---|---:|---:|---:|---:|---|
| `O4` | `0.039302` | `0.326180` | `0.406` | `0.000401` | `False` |
| `B4` | `0.126042` | `0.121608` | `0.953` | `0.031874` | `True` |
| `G5` | `0.129468` | `0.163014` | `0.859` | `0.026236` | `False` |
| `O5` | `0.106795` | `0.328221` | `0.812` | `0.002093` | `False` |

## Decision

- Result: `fail_no_target_specific_white_mask_signal`.
- The proposal is worth testing because the old topology was assumption-driven, but this scan-only run does not yet make `77 -> 76` an extraction selector.
- A physical copy bench test may still adjudicate the topology visually, but current pixels do not supply R3 unit/order evidence.
- Do not resume selector/key checks from this branch without a source-backed unit/order instruction.
