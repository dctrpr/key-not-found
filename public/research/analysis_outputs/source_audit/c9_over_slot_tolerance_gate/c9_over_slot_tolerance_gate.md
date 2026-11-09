# C9 OVER Slot Tolerance Gate

Scope: test whether the B4/G5 `OVER` span is stable under fixed small horizontal C9 slot-grid shifts and overlap thresholds, while tracking the p75 grey control row. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T03:15:59`
- Sheet: `analysis_outputs/source_audit/c9_over_slot_tolerance_gate/c9_over_slot_tolerance_gate_sheet.jpg`

## Canonical

- Active black pair stream: `OVER`.
- p75 grey control span: `OVER`.
- Active pair has OVER: `True`.
- p75 control has OVER: `True`.

## Threshold Summary

| threshold px | active OVER shifts | p75 control OVER shifts | both OVER shifts | tested shifts |
|---|---|---|---|---|
| `1` | `7` | `11` | `7` | `11` |
| `4` | `7` | `11` | `7` | `11` |
| `25` | `8` | `10` | `7` | `11` |
| `50` | `9` | `9` | `8` | `11` |
| `75` | `7` | `6` | `6` | `11` |
| `100` | `5` | `2` | `2` | `11` |
| `120` | `2` | `0` | `0` | `11` |
| `150` | `0` | `0` | `0` | `11` |
| `200` | `0` | `0` | `0` | `11` |

## Summary

- Total combinations: `99`.
- Active B4/G5 OVER combinations: `45`.
- p75 control OVER combinations: `49`.
- Both OVER combinations: `37`.
- Active OVER fails completely at thresholds: `[150, 200]`.

## Decision

- Do not tune C9 OVER slot thresholds into an extraction rule.
- The active `OVER` is tolerance-sensitive and controlled by p75 at the canonical setting.
- Reopen only if a new source/clue names OVERDOSE slots or an 8-column reading order.
