# Current Scan B4 Broad-Contact Provenance Gate

Scope: traced the nearest `all_content_box_translation:broad` contact around B4 back through the page-75 mirror transform, then checked whether the mapped source area carries source text or instruction terms. No key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:32:31+02:00`
- Mode/layer/target: `all_content_box_translation` / `broad` / `B4`
- B4 broad nearest distance / minimal expansion / first pixel expansion: `21.84` / `22` / `32` px
- Radius-32 broad / feature / broad-only pixels: `1` / `0` / `1`
- Nearest target point -> source point: `[711, 2450]` -> `[1864, 2511]`
- Target/source point RGB: `{'rgb': [242, 242, 242], 'luma': 242.0, 'saturation': 0.0}` / `{'rgb': [242, 242, 242], 'luma': 242.0, 'saturation': 0.0}`
- Source words within 64/128/256 px: `{'64': 0, '128': 0, '256': 4}`
- Nearest OCR word / nearest strict instruction word: `lab.` at `249.047` px / `words` at `913.859` px
- Strict/context hits in traced contact contexts: `0` / `0`
- Hidden broad-contact candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate/current_scan_b4_broad_contact_provenance_gate_sheet.jpg`
- Fingerprint: `mode=all_content_box_translation|target=B4|layer=broad|b4BroadMin=22|firstExpansion=32|r32BroadPx=1|r32FeaturePx=0|r32BroadOnlyPx=1|r32Components=1|pointLayers=broad|sourceWords64=0|sourceWords128=0|nearestWord=249.047:lab|nearestStrict=913.859:words|strict=0|context=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Radius Rows

| radius | broad px | feature px | broad-only px | components | source words | strict | context |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `16` | `0` | `0` | `0` | `0` | `0` | `0` | `0` |
| `32` | `1` | `0` | `1` | `1` | `0` | `0` | `0` |
| `64` | `1` | `0` | `1` | `1` | `0` | `0` | `0` |
| `128` | `2` | `0` | `2` | `2` | `0` | `0` | `0` |

## Nearest Source Words

| distance px | text | token | strict | context |
|---:|---|---|---:|---:|
| `249.047` | lab. | `lab` | `0` | `0` |
| `258.799` | bare | `bare` | `0` | `0` |
| `263.717` | this | `this` | `0` | `0` |
| `284.445` | listen | `listen` | `0` | `0` |
| `292.865` | epithet. | `epithet` | `0` | `0` |
| `323.053` | mEthereum | `methereum` | `0` | `0` |
| `348.71` | name. | `name` | `0` | `0` |
| `349.461` | if | `if` | `0` | `0` |
| `365.636` | bad | `bad` | `0` | `0` |
| `367.19` | to | `to` | `0` | `0` |

## Decision

- `current_scan_b4_broad_contact_provenance_noise`
- The B4 rescue contact is broad-only: it has broad-mask pixels but no feature-mask pixels at the 32 px expansion where contact first appears.
- The mapped source point is not on OCR text; the nearest page-75 OCR word is hundreds of pixels away and no traced context supplies source-side unit/order/transform wording.
- Keep the all-content broad B4 contact closed as a scan/halo/margin artifact, not as an extraction path.

## Next Move

- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
