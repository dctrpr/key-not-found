# Current Scan Active Envelope Transform Gate

Scope: transformed the current page-76 O4/B4/G5/O5 active boxes around their own active-quartet envelope. Checked horizontal mirror, vertical mirror, 180-degree rotation, and normalized diagonal folds against active re-hits, non-active page-76 highlight controls, and C9/OVERDOSE slots. This is geometry inspection only; no key extraction, candidates, hashing, WIF/seed/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T10:30:12`
- Active / highlight-control boxes: `4` / `7`
- Active envelope: `[428.0, 2177.0, 1801.0, 2982.0]` center `[1114.5, 2579.5]`
- Transform modes: `hmirror, vmirror, rot180, diag_main, diag_anti`
- Best active-other hit count <=32 / <=64 px: `0` / `1`
- Any transform all-four active-other re-hit <=32 / <=64 px: `0` / `0`
- Any transform all-four active-any re-hit <=32 / <=64 px: `0` / `0`
- Best transform by active-other <=64 px: `diag_anti`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Hidden active-envelope transform candidate: `0`
- Sheet: `analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/current_scan_active_envelope_transform_gate_sheet.jpg`
- Fingerprint: `active=4|highlightControls=7|transforms=hmirror,vmirror,rot180,diag_main,diag_anti|allFourAny32=0|allFourAny64=0|allFourOther32=0|allFourOther64=0|bestOther32=0|bestOther64=1|bestTransform=diag_anti|streams=hmirror:VORE/0/0,vmirror:OVED/0/0,rot180:VORE/0/0,diag_main:OERO/0/0,diag_anti:ODRO/0/1|sourceR3=0|triggers=0/9|selectors=0`

## Transform Summary

| transform | slot stream | active-other hits <=32 | active-other hits <=64 | highlight-control hits <=32 | mean active-other distance | best active-box overlap | best control-box overlap |
|---|---|---:|---:|---:|---:|---:|---:|
| `hmirror` | `VORE` | `0` | `0` | `0` | `324.58` | `0.000` | `0.000` |
| `vmirror` | `OVED` | `0` | `0` | `0` | `342.40` | `0.700` | `0.000` |
| `rot180` | `VORE` | `0` | `0` | `0` | `417.30` | `0.000` | `0.000` |
| `diag_main` | `OERO` | `0` | `0` | `0` | `461.85` | `0.000` | `0.252` |
| `diag_anti` | `ODRO` | `0` | `1` | `0` | `322.89` | `0.324` | `0.000` |

## Projected Rows

| transform | source | projected slot | nearest active-other | distance | nearest highlight control | distance |
|---|---|---|---|---:|---|---:|
| `hmirror` | `O4` | `V` | `B4` | `242.95` | `G4` | `604.45` |
| `hmirror` | `B4` | `O` | `O4` | `242.95` | `G3` | `929.17` |
| `hmirror` | `G5` | `R` | `O5` | `406.21` | `G4` | `663.69` |
| `hmirror` | `O5` | `E` | `G5` | `406.21` | `G4` | `306.68` |
| `vmirror` | `O4` | `O` | `O5` | `217.00` | `G4` | `966.92` |
| `vmirror` | `B4` | `V` | `G5` | `467.79` | `G4` | `84.96` |
| `vmirror` | `G5` | `E` | `B4` | `467.79` | `G4` | `437.56` |
| `vmirror` | `O5` | `D` | `O4` | `217.00` | `G3` | `686.17` |
| `rot180` | `O4` | `V` | `G5` | `513.47` | `G4` | `161.93` |
| `rot180` | `B4` | `O` | `O5` | `387.22` | `G4` | `1058.56` |
| `rot180` | `G5` | `R` | `O5` | `384.25` | `G4` | `655.88` |
| `rot180` | `O5` | `E` | `G5` | `384.25` | `G4` | `657.49` |
| `diag_main` | `O4` | `O` | `B4` | `433.17` | `G4` | `149.95` |
| `diag_main` | `B4` | `E` | `G5` | `348.11` | `G4` | `596.38` |
| `diag_main` | `G5` | `R` | `O5` | `515.16` | `G4` | `564.37` |
| `diag_main` | `O5` | `O` | `O4` | `550.98` | `G4` | `1148.56` |
| `diag_anti` | `O4` | `O` | `O5` | `762.44` | `G3` | `855.16` |
| `diag_anti` | `B4` | `D` | `O5` | `61.93` | `G4` | `777.62` |
| `diag_anti` | `G5` | `R` | `O5` | `376.19` | `G4` | `543.46` |
| `diag_anti` | `O5` | `O` | `B4` | `91.00` | `G4` | `389.33` |

## Decision

- `current_scan_active_envelope_transform_no_selector`
- The active quartet does not fold/mirror back onto itself around its own envelope under the tested transforms.
- This closes the remaining active-envelope version of the fold/mirror idea; it does not change the broader source-dependent frontier.

## Next Move

- Use original-layout, physical scan, or raw clue material to supply a distinct source and an explicit unit/order instruction before reopening extraction.
