# C9 Highlight Edge Contact Control

Scope: control-test whether O4's C9 top-edge contact is distinctive among highlight boxes overlapping the same C9 lower-page slot on pages 75-80. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T02:27:02`
- C9 frame: `[294.0, 2176.81, 2250.0, 3023.73]`
- Sheet: `analysis_outputs/source_audit/c9_highlight_edge_contact_control/c9_highlight_edge_contact_control_sheet.jpg`

## Summary

- Overlapping highlight boxes: `8`.
- Page counts: `{'75': 3, '76': 2, '77': 0, '78': 0, '79': 3, '80': 0}`.
- Strict edge contacts <=4 px: `1`.
- Loose edge contacts <=25 px: `2`; loose control contacts: `1`.
- Wide edge contacts <=50 px: `3`.

## Closest Highlight Edge Contacts

| page | highlight | kind | active orange? | overlap | nearest edge | gap px |
|---:|---|---|---|---:|---|---:|
| `76` | `p76_orange_4` | `orange` | `True` | `1.0` | `top` | `0.19` |
| `75` | `p75_orange_6` | `orange` | `False` | `1.0` | `top` | `23.19` |
| `76` | `p76_orange_5` | `orange` | `True` | `1.0` | `bottom` | `41.73` |
| `79` | `p79_orange_7` | `orange` | `False` | `1.0` | `left` | `93.0` |
| `79` | `p79_orange_9` | `orange` | `False` | `1.0` | `left` | `114.0` |
| `75` | `p75_orange_7` | `orange` | `False` | `1.0` | `left` | `158.0` |
| `75` | `p75_orange_8` | `orange` | `False` | `1.0` | `left` | `250.0` |
| `79` | `p79_orange_8` | `orange` | `False` | `1.0` | `left` | `283.0` |

## Findings

- Strict contacts: `['p76 p76_orange_4 top=0.19px']`.
- Loose control contacts: `['p75 p75_orange_6 top=23.19px']`.
- O4 remains the only strict C9 edge contact, but a page-75 control highlight is near the same C9 top edge at the looser threshold.
- O5 is bottom-near at `41.73 px`, but not a strict frame-edge contact.

## Decision

- Do not promote O4's C9 top-edge contact as an extraction rule.
- Keep it as a source-registration detail only.
- Reopen extraction only if a new source/clue explicitly names frame-edge or top-edge reading.
