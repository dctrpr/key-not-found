# Body Highlighter Grammar Audit

Scope: detect line-shaped orange and dark/grey highlighter components across the local Max/OVERDOSE comparison page images. No OCR, key derivation, hashing, seed checking, WIF checking, or address checking was run.

- Created: `2026-05-20T10:38:55`
- Sheet: `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar_sheet.jpg`

## Source Summary

| source | pages | orange line bands | dark line bands | same-row pairs | sustained pages | mixed pages | max score |
|---|---:|---:|---:|---:|---:|---:|---:|
| `bitcoin3` | `8` | `4` | `4` | `0` | `[8]` | `[8]` | `7` |
| `issue24_toxic_af` | `8` | `28` | `14` | `0` | `[3, 4, 6, 7]` | `[3, 4, 6, 7]` | `19` |
| `issue26` | `5` | `11` | `4` | `0` | `[3, 4]` | `[3]` | `14` |
| `issue27` | `8` | `2` | `3` | `0` | `[]` | `[]` | `3` |

## Decision

- Line-shaped orange/dark body highlights are sustained across Issue 24 body pages and remain much less sustained in the independent comparison articles. This keeps the Issue 24 body-highlighter grammar puzzle-relevant, while broad colored OVERDOSE art stays downgraded as house style.
- Issue 24 body grammar: sustained pages `[3, 4, 6, 7]`, mixed orange/dark pages `[3, 4, 6, 7]`.
- Independent comparison articles still contain colored marks, but they do not reproduce the same sustained body-text orange/grey pattern across article pages.

- Strongest independent comparison by max score is `issue26` with max score `14`, but its sustained/mixed pages are `[3, 4]` / `[3]`.
## Next Move

- Keep orange/grey body highlights active only where they interact with page-76 geometry; do not pursue comparison-article style metrics as selectors.
