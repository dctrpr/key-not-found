# Source Packet Repaired Frame Expansion Leakage

Scope: measure whether current and dx-repaired reflected p78 frame expansions stay selective when forced to touch or fully cover O4/B4/G5/O5. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T06:43:12`
- Active visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- Scenario count: `9` (`base`, `edge_touch_all`, `full_cover_all` for each frame)
- Base max line-context word count: `72`
- Touch-expansion minimum line-context word count: `91`
- Full-cover minimum line-context word count: `102`
- Full-cover minimum non-target line-context word count: `92`
- Full-cover non-target density range: `[0.902, 0.902]`
- Full-cover OCR-map word-center count range: `[89, 89]`
- Full-cover non-active highlight/format entries: `4`
- Full-cover hard instruction hits: `0` transcript / `0` OCR-map
- Expansion leakage fingerprint: `scenarios=base,touch,full|baseMaxWords=72|touchMinWords=91|fullMinWords=102|fullMinNonTarget=92|fullSignals=4|fullHard=0|fullOcrHard=0`
- Sheet: `analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/source_packet_repaired_frame_expansion_leakage_sheet.jpg`

## Scenario Rows

| frame | scenario | frame | full targets | partial targets | line range | words | non-target words | non-active signals | transcript hard hits | OCR-map words |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `current` | `base` | `[1234, 2398, 2250, 2950]` | `0/4` | `1/4` | `25-32` | `72` | `72` | `4` | `0` | `22` |
| `current` | `edge_touch_all` | `[691, 2225, 2250, 2950]` | `1/4` | `2/4` | `23-32` | `91` | `89` | `4` | `0` | `68` |
| `current` | `full_cover_all` | `[428, 2177, 2250, 2982]` | `4/4` | `4/4` | `22-32` | `102` | `92` | `4` | `0` | `89` |
| `g5_edge_touch_dx_-38` | `base` | `[1196, 2398, 2212, 2950]` | `0/4` | `1/4` | `25-32` | `72` | `72` | `4` | `0` | `23` |
| `g5_edge_touch_dx_-38` | `edge_touch_all` | `[691, 2225, 2212, 2950]` | `1/4` | `2/4` | `23-32` | `91` | `89` | `4` | `0` | `68` |
| `g5_edge_touch_dx_-38` | `full_cover_all` | `[428, 2177, 2212, 2982]` | `4/4` | `4/4` | `22-32` | `102` | `92` | `4` | `0` | `89` |
| `nearest_grid_dx_-40` | `base` | `[1194, 2398, 2210, 2950]` | `0/4` | `2/4` | `25-32` | `72` | `72` | `4` | `0` | `23` |
| `nearest_grid_dx_-40` | `edge_touch_all` | `[691, 2225, 2210, 2950]` | `1/4` | `2/4` | `23-32` | `91` | `89` | `4` | `0` | `68` |
| `nearest_grid_dx_-40` | `full_cover_all` | `[428, 2177, 2210, 2982]` | `4/4` | `4/4` | `22-32` | `102` | `92` | `4` | `0` | `89` |

## Reference Check

- O4 frame-rescue content gate full coverage: `102` words, `92` non-target words, `4` non-active highlight entries, `0` hard instruction hits.
- O4 frame-rescue signal stream: layer stream `YBKKBMMY`, non-active signal groups `4`, hard instruction hits `0`.

## Decision

- Treat repaired frame expansion as context leakage, not as a selector.
- The full-cover expansions recover all four active boxes only by taking the broad lower-corridor line band (`22-32`) with 92 non-target words and four non-active format signals.
- The edge-touch expansions already pull a large lower-corridor context window while still failing to cover the active phrases.
- Hard instruction hits remain zero in both transcript-authority lines and OCR-map word centers.

## Next Move

- Keep repaired p78-frame expansion as a future source-registration stress test only. Do not resume extraction until an external/source-backed R3 unit and order rule appears.
