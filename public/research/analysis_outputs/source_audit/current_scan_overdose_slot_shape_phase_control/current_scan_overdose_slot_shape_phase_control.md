# Current Scan OVERDOSE Slot-Shape Phase Control

Scope: preserved the active O4/B4/G5/O5 x-positions, box sizes, OVERDOSE slot stream, and 3/2/5 line-gap shape, then shifted that shape across the possible lower-page line phases. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T04:20:38`
- Sheet: `analysis_outputs/source_audit/current_scan_overdose_slot_shape_phase_control/current_scan_overdose_slot_shape_phase_control_sheet.jpg`
- Scenario rows / active phases / control phases: `3` / `1` / `2`
- Total target rows / total OCR word hits: `12` / `30`
- Strict instruction scenario rows / token hits: `0` / `0`
- Context scenario rows / token hits: `2` / `3`
- Active-phase strict/context token hits: `0` / `0`
- Control-phase strict/context token hits: `0` / `3`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `lines=13|scenarios=3|active=1|controls=2|targets=12|words=30|strictRows=0|strict=0|contextRows=2|context=3|activeStrict=0|activeContext=0|controlStrict=0|controlContext=3|sourceR3=0|triggers=0/9|selectors=0`

## Scenario Rows

| start | phase | lines | slots | words | strict tokens | context tokens | snippets |
|---:|---|---|---|---:|---|---|---|
| 0 | control | 0,3,5,10 | OVED | 12 | - | bitcoin | O4: Salvador / B4: I tweeted / G5: bitcoin that he / O5: crony pals, but so far he |
| 1 | control | 1,4,6,11 | OVED | 15 | - | bitcoin, imf | O4: Fund (IMF) on Twitter? / B4: he was going / G5: of future bitcoin / O5: don't really trust that guy |
| 2 | active | 2,5,7,12 | OVED | 3 | - | - | O4: ByiiREeraipy" / B4: eis / G5: (no OCR words) / O5: siukbeodmensertslveaarty |

## Decision

- `current_scan_overdose_slot_shape_phase_control_no_instruction_source`
- The active vertical phase is the only phase that overlaps all four manual active boxes, but that is a location validation fact, not an extraction instruction.
- Shifted same-shape control phases still hit ordinary article context words, while no active or control phase contains strict instruction language.
- OVERDOSE slot-shape phase remains a source-comparison guardrail only; it does not name a unit/order/transform.

## Next Move

- Keep active OVERDOSE slot-shape phase as validation geometry. Reopen extraction only with distinct source/original-layout material or raw clue wording that explicitly names the unit/order/transform.
