# Source Packet Alignment Tolerance

Scope: measure how much the active O4/B4/G5/O5 boxes can be padded or shifted while preserving Y/K visual-state evidence and native rotate180 roundtrip. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T05:54:09`
- Active expected visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- Common outward pad all targets pass: `+4px`
- Common inset pad all targets pass: `-12px`
- Common all-direction shift all targets pass: `±4px`
- Largest any-target outward pad pass: `+16px`
- Smallest first outward pad failure: `+8px`
- Max variant mean abs diff after native rotate180: `3.021`
- OVERDOSE control classified-state stream: `NNNNNNNNN`
- OVERDOSE control max dark ratio: `0.0`
- OVERDOSE control max orange ratio: `0.277`
- Sheet: `analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance_sheet.jpg`

## Target Tolerance

| id | state | line/corridor | outward pass max | inset pass max | first outward fail |
|---|---|---:|---:|---:|---:|
| `buying_dip` | `Y` | `22/4` | `+16` | `-12` | `+24` |
| `one_billion` | `K` | `25/7` | `+4` | `-12` | `+8` |
| `volcano_bonds` | `K` | `27/9` | `+8` | `-12` | `+12` |
| `shitcoiner_heart` | `Y` | `32/14` | `+12` | `-12` | `+16` |

## Decision

- Keep this as a source-alignment benchmark only.
- Future source matches should be judged with narrow tolerance: common all-target pass is `+4px` outward padding and `±4px` full-direction shift.
- Larger drift starts breaking visual-state classification, especially black-highlight boxes, so do not accept loose visual matches as source confirmation.
- This supplies no extraction unit or order and does not reopen highlight, fold, or OVERDOSE selectors.
