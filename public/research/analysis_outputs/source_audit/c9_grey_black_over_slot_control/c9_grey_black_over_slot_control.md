# C9 Grey/Black OVER Slot Control

Scope: control-test the `OVER` span from the active black B4/G5 boxes against grey/black rows that overlap the same C9 lower-page frame. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T03:06:31`
- Sheet: `analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control_sheet.jpg`

## C9 Grey/Black Rows

| page | id | text | source | center | span | single OVER? | active corrected? |
|---|---|---|---|---|---|---|---|
| `75` | `p75_grey_3` | `Don't fall for shitcoinery` | `manual_grey_highres_crops.highresBox` | `E` | `OVER` | `True` | `False` |
| `76` | `p76_grey_4` | `$1 billion` | `page76_active_target_crop_completion.one_billion` | `V` | `OV` | `False` | `True` |
| `76` | `p76_grey_5` | `Volcano Bonds` | `page76_active_target_crop_completion.volcano_bonds` | `E` | `ER` | `False` | `True` |

## Adjacent Pair Streams

| page | pair | stream | layout hits | active corrected pair? |
|---|---|---|---|---|
| `76` | `p76_grey_4 + p76_grey_5` | `OVER` | `OVER` | `True` |

## Summary

- C9 grey/black rows: `3`.
- Single-row OVER hits: `1`.
- Control single-row OVER hits: `1`.
- Pair OVER hits: `1`.
- Active corrected pair OVER hits: `1`.
- Strict instruction hits: `0`.

## Decision

- Do not promote B4/G5's `OVER` slot stream as extraction permission.
- The same C9 lower-frame slot rule gives a non-active p75 grey control row an `OVER` span by itself.
- Reopen only if a new source/clue explicitly names grey/black OVER slots or supplies an 8-column reading rule.
