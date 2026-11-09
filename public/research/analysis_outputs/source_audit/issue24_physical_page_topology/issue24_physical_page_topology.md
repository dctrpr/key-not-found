# Issue 24 Physical Page Topology

Scope: record the physical page/leaf topology implied by the locked best scan. No key derivation, hashing, seed checking, WIF checking, address checking, OCR extraction, or broad brute force was run.

- Created: `2026-05-20T22:00:38`
- Review sheet: `analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology_sheet.jpg`

## Page Order

| PDF page | magazine page | role | side |
|---:|---:|---|---|
| `1` | `73` | `opener` | `recto/right/odd` |
| `2` | `74` | `opener` | `verso/left/even` |
| `3` | `75` | `article` | `recto/right/odd` |
| `4` | `76` | `article` | `verso/left/even` |
| `5` | `77` | `article` | `recto/right/odd` |
| `6` | `78` | `article` | `verso/left/even` |
| `7` | `79` | `article` | `recto/right/odd` |
| `8` | `80` | `article` | `verso/left/even` |

## Physical Leaves

| leaf | magazine pages | PDF pages |
|---|---|---|
| `opener leaf` | `73/74` | `1/2` |
| `article leaf 1` | `75/76` | `3/4` |
| `article leaf 2` | `77/78` | `5/6` |
| `article leaf 3` | `79/80` | `7/8` |

## Facing Spreads

| spread | magazine pages | PDF pages |
|---|---|---|
| `entry spread` | `74/75` | `2/3` |
| `article spread 1` | `76/77` | `4/5` |
| `article spread 2` | `78/79` | `6/7` |

## Pair Classification

| pair | topology | meaning |
|---|---|---|
| `78 -> 76` | `not same leaf and not facing spread` | visual/registration signal only under current scan, not literal magazine leaf physics |
| `79 -> 76` | `not same leaf and not facing spread` | visual/registration signal only under current scan, not literal magazine leaf physics |
| `75 <-> 76` | `same physical leaf` | valid hold-to-light pair, but prior refined leaf tests did not reproduce the lower p76 corridor |
| `77 <-> 78` | `same physical leaf` | valid hold-to-light pair; supports checking only with new physical/source evidence |
| `78 <-> 79` | `facing spread` | valid facing-spread pair; useful for visual registration, not front/back bleed-through |

## Findings

- Same-leaf hold-to-light candidates are `73/74`, `75/76`, `77/78`, and `79/80`.
- Facing-spread candidates inside this scan are `74/75`, `76/77`, and `78/79`.
- The repeatedly strong `78 -> 76` and `79 -> 76` page-76 signals are not literal same-leaf or facing-spread relations under normal magazine pagination.
- That keeps page 76 important, but classifies the 78/79 -> 76 behavior as visual registration/orientation evidence under the current scan, not proof of physical bleed-through.

## Decision

- Close literal leaf-physics interpretation for `78/79 -> 76` under the current scan.
- Keep the topology as a guardrail: future physical/source transforms must say which physical pair they use before extracting text.
