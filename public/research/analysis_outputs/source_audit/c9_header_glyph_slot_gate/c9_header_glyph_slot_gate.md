# C9 Header Glyph Slot Gate

Scope: scale the actual `OVERDOSE` header glyph boxes from pages 76 and 78 into the C9 frame, then map active O4/B4/G5/O5 plus the p75 grey control. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T03:25:30`
- Sheet: `analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate_sheet.jpg`

## Summary

- Header projections tested: `2`.
- Max projected glyph-edge delta vs equal slots: `0.087628` px.
- Active B4/G5 `OVER` projections: `2`.
- p75 control `OVER` projections: `2`.
- Active strict instruction hits: `0`.

## Projection Streams

- `p76_header_glyph`:
  - active x-order span: `OVERRDODOS`
  - active black x-order span: `OVER`
  - active orange x-order span: `RDODOS`
  - p75 grey control span: `OVER`
- `p78_header_glyph`:
  - active x-order span: `OVERRDODOS`
  - active black x-order span: `OVER`
  - active orange x-order span: `RDODOS`
  - p75 grey control span: `OVER`

## Decision

- Do not promote actual OVERDOSE header glyph slots as a selector.
- The real glyph projection reproduces the equal-slot result and keeps B4/G5 `OVER` controlled by p75.
- Reopen only if a new source/clue names OVERDOSE header letters, glyph-width slots, or an 8-column reading order.
