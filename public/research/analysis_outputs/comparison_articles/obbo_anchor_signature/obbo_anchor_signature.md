# O-B-B-O Anchor Signature Audit

Scope: visual recurrence audit for the page-76 O-B-B-O anchor signature using existing body-highlighter boxes. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-20T19:24:39`
- Body grammar source: `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json`
- Anchor source: `analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json`

## Summary

- Pages with an O-B-B-O sequence: `3`
- Issue 24 pages with O-B-B-O: `3`
- Independent comparison pages with O-B-B-O: `0`
- Page-76/template best score: `0.015`
- Best independent score: `None`

## Closest Matches

| source | page | O-B-B-O count | best score | grammar score | normalized centers |
|---|---:|---:|---:|---:|---|
| `issue24_toxic_af` | `4` | `32` | `0.015` | `15` | `[[0.617, 0.674], [0.22, 0.742], [0.391, 0.786], [0.53, 0.906]]` |
| `issue24_toxic_af` | `3` | `20` | `1.7` | `19` | `[[0.717, 0.309], [0.415, 0.397], [0.315, 0.725], [0.27, 0.747]]` |
| `issue24_toxic_af` | `6` | `12` | `2.3305` | `13` | `[[0.556, 0.301], [0.627, 0.345], [0.386, 0.346], [0.629, 0.62]]` |

## Assessment

- The active page-76 anchor order is O-B-B-O, but OBBO as a color sequence is not unique by itself.
- When normalized position is included, Issue 24 page 4 is the expected closest match because it contains the trusted page-76 anchors.
- Independent comparison pages can produce OBBO only when they have enough colored body bands, but their best matches are weak layout/style recurrences rather than the lower page-76 amount/bond/action/identity corridor.
- OBBO should remain a local page-76 signature, not an extraction rule. It is useful for future source comparison only if the same four semantic anchors are present.

## Decision

- Do not use OBBO alone as a selector; keep it as a source-comparison signature tied to the four page-76 semantic anchors.

## Next Move

- Inspect p80/package or pill-count mechanics only where they can choose among the four page-76 anchors; do not compare broad colored layout metrics further.
