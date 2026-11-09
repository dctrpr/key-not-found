# C9 OVERDOSE Letter-Slot Gate

Scope: divide the C9 frame into eight equal horizontal slots named `OVERDOSE`, then map O4/B4/G5/O5 boxes and same-slot orange-highlight controls to center/span slot letters. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T02:59:53`
- Sheet: `analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate_sheet.jpg`
- Slot width: `244.5 px`.

## Active Rows

| target | phrase | color | line | center slot | span slots |
|---|---|---|---|---|---|
| `O4` | `buying the dip` | `Y` | `22` | `O` | `DOS` |
| `B4` | `$1 billion` | `K` | `25` | `V` | `OV` |
| `G5` | `Volcano Bonds` | `K` | `27` | `E` | `ER` |
| `O5` | `shitcoiner at heart` | `Y` | `32` | `D` | `RDO` |

## Streams

| stream | value | layout hits | strict instruction hits |
|---|---|---|---|
| `active_center_line_order` | `OVED` | `-` | `-` |
| `active_center_x_order` | `VEDO` | `-` | `-` |
| `active_span_line_order` | `DOSOVERRDO` | `OVER` | `-` |
| `active_span_x_order` | `OVERRDODOS` | `OVER` | `-` |
| `active_orange_only_span_x_order` | `RDODOS` | `-` | `-` |
| `active_black_only_span_x_order` | `OVER` | `OVER` | `-` |
| `active_center_line_order_reverse` | `DEVO` | `-` | `-` |
| `active_center_x_order_reverse` | `ODEV` | `-` | `-` |
| `active_span_line_order_reverse` | `ODRREVOSOD` | `-` | `-` |
| `active_span_x_order_reverse` | `SODODRREVO` | `-` | `-` |
| `active_orange_only_span_x_order_reverse` | `SODODR` | `-` | `-` |
| `active_black_only_span_x_order_reverse` | `REVO` | `-` | `-` |

## Control Orange Streams

| stream | value | layout hits |
|---|---|---|
| `p75_control_orange_span_x_order` | `VOVEDO` | `-` |
| `p79_control_orange_span_x_order` | `OOV` | `-` |

## Summary

- Active center line-order stream: `OVED`.
- Active center x-order stream: `VEDO`.
- Active span line-order stream: `DOSOVERRDO`.
- Active span x-order stream: `OVERRDODOS`.
- Active black-only span x-order stream: `OVER`.
- Active orange-only span x-order stream: `RDODOS`.
- Active strict instruction hits: `0`.
- OVER prefix requires black targets: `True`.

## Decision

- Do not promote C9 OVERDOSE 8-letter slot mapping as a selector.
- The only interesting string, `OVERRDODOS`, is a layout artifact of x-order span bins and depends on the completed black B4/G5 boxes.
- Reopen only if a new source/clue explicitly names OVERDOSE letters, slots, or an 8-column reading order.
