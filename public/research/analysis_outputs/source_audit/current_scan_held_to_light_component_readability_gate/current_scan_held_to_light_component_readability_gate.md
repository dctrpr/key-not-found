# Current Scan Held-To-Light Component Readability Gate

Scope: bounded current-scan/PDF held-to-light component-readability inspection. No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T13:43:05`
- Modes checked: `3`
- Target rows checked: `12`
- Natural valid-leaf readable rows: `0`
- All-four readable modes: `0`
- Strict instruction rows: `0`
- Hidden readability candidates: `0`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `modes=3|rows=12|naturalReadable=0|forcedReadable=2|allFourReadable=0|strictRows=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Mode Summary

| mode | source-only pixels | component rows | letterlike rows | readable rows | all-four readable | strict rows | source-word rows |
|---|---:|---:|---:|---:|---|---:|---:|
| `valid_75_to_76_natural` | `293` | `1` | `0` | `0` | `False` | `0` | `0` |
| `valid_75_to_76_small_jitter_best` | `1047` | `2` | `1` | `1` | `False` | `0` | `0` |
| `valid_75_to_76_forced_best` | `1122` | `4` | `2` | `2` | `False` | `0` | `0` |

## Target Rows

| mode | target | source-only coverage | components | letterlike | largest letterlike | source words | strict | preview |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `valid_75_to_76_natural` | `O4` | `0.003702712` | `0` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_natural` | `B4` | `0.0` | `0` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_natural` | `G5` | `0.005766833` | `0` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_natural` | `O5` | `0.003188406` | `1` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_small_jitter_best` | `O4` | `4.4611e-05` | `0` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_small_jitter_best` | `B4` | `0.0` | `0` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_small_jitter_best` | `G5` | `0.046134663` | `10` | `7` | `170` | `0` | `0` |  |
| `valid_75_to_76_small_jitter_best` | `O5` | `0.005088567` | `1` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_forced_best` | `O4` | `0.007048537` | `1` | `0` | `0` | `0` | `0` |  |
| `valid_75_to_76_forced_best` | `B4` | `0.039964404` | `10` | `2` | `38` | `0` | `0` |  |
| `valid_75_to_76_forced_best` | `G5` | `0.012468828` | `3` | `2` | `111` | `0` | `0` |  |
| `valid_75_to_76_forced_best` | `O5` | `0.007407407` | `1` | `0` | `0` | `0` | `0` |  |

## Decision

- current_scan_held_to_light_components_not_readable_selector.
- Reason: The physically valid natural 75->76 view has no readable active quartet, and even the forced same-leaf guardrail does not make all four active boxes readable or produce strict instruction text. Any mapped words remain ordinary page-75 prose/context without source-backed R3 permission.
- Next move: Do not treat held-to-light residue as readable source text under the current scan. Further local work should inspect a different source/provenance surface, or wait for a true physical/original-layout source or raw clue that names the unit/order/transform.

Sheet: `analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate/current_scan_held_to_light_component_readability_gate_sheet.jpg`
