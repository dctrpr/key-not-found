# C9 Mirrored Header Glyph Gate

Scope: test mirror variants of the actual p76/p78 `OVERDOSE` header glyph slots against active O4/B4/G5/O5 and the p75 grey control. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T03:34:04`
- Sheet: `analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/c9_mirrored_header_glyph_gate_sheet.jpg`

## Summary

- Variants tested: `8`.
- Active black `OVER` variants: `2`.
- Active black `REVO` variants: `2`.
- p75 control `OVER` variants: `2`.
- p75 control `REVO` variants: `2`.
- Variants where p75 control matches active black stream: `8`.
- Strict instruction hits: `0`.

## Variant Streams

- `p76_normal_labels_original_geometry`: slots `OVERDOSE`, active black `OVER`, p75 control `OVER`, strict hits `[]`
- `p76_normal_labels_mirror_x_geometry`: slots `OVERDOSE`, active black `DOSE`, p75 control `DOSE`, strict hits `[]`
- `p76_reverse_labels_original_geometry`: slots `ESODREVO`, active black `ESOD`, p75 control `ESOD`, strict hits `[]`
- `p76_reverse_labels_mirror_x_geometry`: slots `ESODREVO`, active black `REVO`, p75 control `REVO`, strict hits `[]`
- `p78_normal_labels_original_geometry`: slots `OVERDOSE`, active black `OVER`, p75 control `OVER`, strict hits `[]`
- `p78_normal_labels_mirror_x_geometry`: slots `OVERDOSE`, active black `DOSE`, p75 control `DOSE`, strict hits `[]`
- `p78_reverse_labels_original_geometry`: slots `ESODREVO`, active black `ESOD`, p75 control `ESOD`, strict hits `[]`
- `p78_reverse_labels_mirror_x_geometry`: slots `ESODREVO`, active black `REVO`, p75 control `REVO`, strict hits `[]`

## Decision

- Do not promote mirrored OVERDOSE header glyph slots as a selector.
- Mirroring header labels or C9 x-geometry only toggles the controlled B4/G5 signal among `OVER`, `DOSE`, `ESOD`, and `REVO`.
- The p75 grey control matches the active black stream in every tested variant.
- Reopen only if a new source/clue names mirrored header letters, glyph slots, or an 8-column reading order.
