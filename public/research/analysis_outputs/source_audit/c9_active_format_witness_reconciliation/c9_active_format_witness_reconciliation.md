# C9 Active Format Witness Reconciliation

Scope: reconcile DOCM/high-res/crop authority with line-level bold letters, Markdown markup, annotated transcript notes, and correction markup for O4/B4/G5/O5. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-21T02:53:23`
- Sheet: `analysis_outputs/source_audit/c9_active_format_witness_reconciliation/c9_active_format_witness_reconciliation_sheet.jpg`

## Summary

- Format authority pass count: `4/4`.
- Line-level exact bold matches: `2/4`.
- Markdown bold contains active phrase: `2/4`.
- Annotated bold+highlight claims: `4/4`.
- Witness conflicts: `2/4`.
- Correction report mentions: `2/4`.

## Witness Grid

| target | DOCM/high-res/crop authority | line-level bold letters | Markdown phrase bold? | annotated bold+highlight? | correction mentions? | conflict? | authority use |
|---|---|---|---|---|---|---|---|
| `O4 buying the dip` | bold `1.0`, `yellow:14`, visual `True`, crop `True` | `buyingthedip` / expected `buyingthedip` | `True` | `True` | `True` | `False` | `format authority` |
| `B4 $1 billion` | bold `1.0`, `black:10`, visual `True`, crop `True` | `-` / expected `$1billion` | `False` | `True` | `False` | `True` | `format authority` |
| `G5 Volcano Bonds` | bold `1.0`, `black:13`, visual `True`, crop `True` | `IMF` / expected `VolcanoBonds` | `False` | `True` | `True` | `True` | `format authority` |
| `O5 shitcoiner at heart` | bold `1.0`, `yellow:19`, visual `True`, crop `True` | `shitcoineratheart` / expected `shitcoineratheart` | `True` | `True` | `False` | `False` | `format authority` |

## Assessment

- DOCM/high-res/crop-pack authority agrees on all four active targets: each is Typeka, bold, highlighted, and visually matched.
- Line-level bold-letter helper data is not equivalent to that authority: it matches only O4/O5, omits B4, and reads G5 line-level bold letters as IMF.
- Markdown bold is transcript markup and matches only O4/O5 in the active quartet; it does not mark B4/G5 as bold target phrases.
- The annotated transcript claims all four active phrases are bold/highlighted, but it is a format witness, not exact-prose or selector authority.
- The correction report reinforces text authority for O4 punctuation and G5 Volcano Bonds omission, not a format-unit extraction rule.

## Decision

- Use DOCM/high-res/crop-pack witnesses as active format authority for source comparison only.
- Do not use line-level bold letters, Markdown bold, annotated notes, or correction mentions as extraction permission.
- Reopen extraction only if a new source/clue supplies R3 unit/order wording tied to one of these format witnesses.
