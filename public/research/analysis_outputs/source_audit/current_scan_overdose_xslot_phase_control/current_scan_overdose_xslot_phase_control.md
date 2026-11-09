# Current Scan OVERDOSE X-Slot Phase Control

Scope: kept the active O4/B4/G5/O5 vertical positions, box sizes, and within-slot offsets, then shifted their OVERDOSE center-slot indexes through all eight horizontal phases. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:29:54`
- Sheet: `analysis_outputs/source_audit/current_scan_overdose_xslot_phase_control/current_scan_overdose_xslot_phase_control_sheet.jpg`
- Scenario rows / active phases / control phases: `8` / `3` / `5`
- Total target rows / total OCR word hits: `32` / `53`
- Strict instruction scenario rows / token hits: `0` / `0`
- Context scenario rows / token hits: `4` / `6`
- Active-phase strict/context token hits: `0` / `1`
- Control-phase strict/context token hits: `0` / `5`
- Active/control visual-orange hits: `6` / `2`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `phases=8|active=3|controls=5|targets=32|words=53|strictRows=0|strict=0|contextRows=4|context=6|activeStrict=0|activeContext=1|controlStrict=0|controlContext=5|activeOrange=6|controlOrange=2|sourceR3=0|triggers=0/9|selectors=0`

## Scenario Rows

| phase | kind | slots | words | visual orange | annotated color | strict tokens | context tokens | snippets |
|---:|---|---|---:|---:|---:|---|---|---|
| 0 | active | OVED | 3 | 2 | 1 | - | - | O4:ByiiREeraipy" / B4:eis / G5:(no OCR words) / O5:siukbeodmensertslveaarty |
| 1 | active | SERO | 7 | 2 | 1 | - | bitcoin | O4:ByiiREeraipy" / B4:in bitcoin / G5:to pay off / O5:siukbeodmensertslveaarty |
| 2 | control | ERDS | 8 | 1 | 1 | - | bitcoin, imf | O4:(no OCR words) / B4:bitcoin that he / G5:pay off the IMF / O5:siukbeodmensertslveaarty |
| 3 | control | ODOE | 5 | 0 | 1 | - | imf, sell | O4:He's / B4:he should sell / G5:IMF / O5:(no OCR words) |
| 4 | control | VOSO | 6 | 0 | 1 | - | sell | O4:He's taunting them, / B4:sell / G5:(no OCR words) / O5:Maybe because |
| 5 | control | ESEV | 6 | 0 | 0 | - | - | O4:taunting them, telling / B4:(no OCR words) / G5:(no OCR words) / O5:Maybe because he's |
| 6 | control | REOE | 10 | 1 | 0 | - | - | O4:them, telling them he's / B4:(no OCR words) / G5:collateralized / O5:Maybe because he's a siukbeodmensertslveaarty |
| 7 | active | DOVR | 8 | 2 | 0 | - | - | O4:them he's ByiiREeraipy" / B4:(no OCR words) / G5:collateralized / O5:because he's a siukbeodmensertslveaarty |

## Decision

- `current_scan_overdose_xslot_phase_control_no_instruction_source`
- Horizontal phase is not selective: multiple shifted phases still re-overlap all four active boxes because the active boxes are wide relative to OVERDOSE slot spacing.
- Shifted phases sample ordinary article text and format regions, while strict instruction hits remain 0.
- OVERDOSE x-slot phase remains validation geometry only; it does not unlock extraction from O4/B4/G5/O5.

## Next Move

- Keep horizontal slot phase as a source-comparison benchmark. Reopen extraction only with distinct source/original-layout material or raw clue wording that explicitly names the unit/order/transform.
