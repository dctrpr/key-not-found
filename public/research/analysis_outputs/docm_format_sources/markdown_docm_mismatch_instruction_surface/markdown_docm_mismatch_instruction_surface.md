# Markdown-DOCM Mismatch Instruction Surface

Scope: align user Markdown bold spans to DOCM font/highlight runs and test the page-76 corridor mismatch streams for instruction-like wording. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.

- Created: `2026-05-20T23:39:36`
- Sheet: `analysis_outputs/docm_format_sources/markdown_docm_mismatch_instruction_surface/markdown_docm_mismatch_instruction_surface_sheet.jpg`
- Decision: `markdown_docm_mismatch_no_r3_instruction`

## Summary

- Markdown bold spans: `230`
- Aligned to DOCM text: `229`
- Unaligned: `1`
- Page-76 corridor Markdown bold spans: `18`
- Corridor Markdown-only/not-DOCM-bold spans: `13`
- Corridor DOCM-only active targets: `2`
- Total instruction-term hits in tested mismatch streams: `0`

## Corridor Streams

- `corridorMarkdownOnlyStream`: `lv d i e N v z I d e ll u h u`
  - instruction hits: `[]`
- `corridorHighlightedAlignedStream`: `“buying the dip.” shitcoiner at heart.`
  - instruction hits: `[]`
- `corridorDocmOnlyActiveTargetStream`: `$1 billion Volcano Bonds`
  - instruction hits: `[]`

## Corridor Markdown Rows

| order | text | DOCM font | bold | highlight | classification |
|---:|---|---|---:|---|---|
| 77 | `lv` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 78 | `d` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 79 | `“buying the dip.”` | `Typeka` | `1.0` | `yellow` | `visual_highlight_or_docm_highlight` |
| 80 | `President Nayib Bukele` | `Typeka` | `1.0` | `none` | `docm_bold_aligned` |
| 81 | `IMF` | `Typeka` | `1.0` | `none` | `docm_bold_aligned` |
| 82 | `loan` | `Typeka` | `1.0` | `none` | `docm_bold_aligned` |
| 83 | `i` | `Typeka` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 84 | `e` | `Typeka` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 85 | `N` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 86 | `v` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 87 | `z` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 88 | `I d` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 89 | `e` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 90 | `ll` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 91 | `u` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 92 | `h` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 93 | `u` | `Typeka Mix` | `0.0` | `none` | `markdown_only_not_docm_bold` |
| 94 | `shitcoiner at heart.` | `Typeka` | `1.0` | `yellow` | `visual_highlight_or_docm_highlight` |

## DOCM-Only Active Targets

- `$1 billion`: DOCM bold `1.0`, DOCM highlights `{'black': 10}`, Markdown bold `0.0`
- `Volcano Bonds`: DOCM bold `1.0`, DOCM highlights `{'black': 13}`, Markdown bold `0.0`

## Next Move

- Keep Markdown bold as an annotation/transcript layer and DOCM/high-res as format authority. Do not use mismatch streams unless a new source clue explicitly names Markdown-vs-font mismatch as the unit.
