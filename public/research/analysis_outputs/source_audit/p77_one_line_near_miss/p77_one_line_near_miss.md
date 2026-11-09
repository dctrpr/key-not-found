# P77 One-Line Near-Miss Audit

Scope: test whether the p77 -> O5 physical near miss is a stable one-line-up rule. No key candidates were generated.

- Created: `2026-05-20T13:14:43`
- Baseline p77 -> O5 vertical gap: `71.93` px.
- Content-box p77 -> O5 vertical gap: `65.49` px.
- Page-76 lower-corridor median line pitch: `73.73` px.
- Baseline gap minus median pitch: `-1.8` px.
- Content-box gap minus median pitch: `-8.24` px.

## Shift Hits

| page | shift | hits | hit labels |
|---:|---|---:|---|
| `75` | `one_line_up_median` | `0` | - |
| `75` | `one_line_down_median` | `0` | - |
| `75` | `exact_gap_up_control` | `0` | - |
| `75` | `content_box_gap_up_control` | `0` | - |
| `77` | `one_line_up_median` | `1` | It does this by monetizing -> O5 (0.02694) |
| `77` | `one_line_down_median` | `0` | - |
| `77` | `exact_gap_up_control` | `0` | - |
| `77` | `content_box_gap_up_control` | `0` | - |

## Line Pitch Deltas

- `[74.8, 75.96, 68.2, 74.89, 74.89, 72.66, 73.72, 70.44, 73.73, 74.89, 72.66, 70.44, 90.04]`

## Assessment

- The p77 `It does this by monetizing` near miss is line-quantized: its 71.93 px vertical gap is close to the measured lower-corridor median line pitch of 73.73 px.
- However, applying a one-line-up shift to all p77 reflected highlights creates only a single trusted O5/G5 contact, not a repeated physical selector.
- The exact-gap control is merely a touch/repair control; it does not add an independent instruction or a second target hit.
- Because no source clue says `line up`, `one line`, or `move up`, this remains a physical-scan benchmark rather than extraction material.

Decision: `do_not_promote_one_line_shift_to_selector`.

Next move: Use the 71.93 px / 73.73 px one-line relationship as a benchmark for future physical/source scans. A real source should make the contact natural and repeated, not require an invented line shift.
