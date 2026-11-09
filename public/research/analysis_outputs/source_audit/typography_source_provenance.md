# Typography Source Provenance

Scope: determine which local sources can actually witness font usage, especially Typeka / Typeka Mix / Typeka-bold. This is a provenance check only; no key derivation was run.

- Created: `2026-05-20T10:46:49`

## PDF Font Evidence

- `issue24_best_scan`: pages=8, fonts=['Helvetica'], pdftotextChars=7785, imageCounts=[1, 1, 1, 1, 1, 1, 1, 1], TypekaFontResource=False
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      14  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      21  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      28  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      35  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      42  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      49  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      56  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      63  0`
- `issue24_desktop_scan`: pages=8, fonts=['Helvetica'], pdftotextChars=7785, imageCounts=[1, 1, 1, 1, 1, 1, 1, 1], TypekaFontResource=False
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      14  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      21  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      28  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      35  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      42  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      49  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      56  0`
  - font row: `Helvetica                            Type 1            WinAnsi          no  no  no      63  0`
- `issue26_comparison`: pages=5, fonts=none, pdftotextChars=0, imageCounts=[1, 1, 1, 1, 1], TypekaFontResource=False
- `issue27_comparison`: pages=8, fonts=none, pdftotextChars=0, imageCounts=[1, 1, 1, 1, 1, 1, 1, 1], TypekaFontResource=False
- `bitcoin3_comparison`: pages=8, fonts=none, pdftotextChars=0, imageCounts=[1, 1, 1, 1, 1, 1, 1, 1], TypekaFontResource=False
- `bitcoin4_issue24_witness`: pages=8, fonts=none, pdftotextChars=0, imageCounts=[1, 1, 1, 1, 1, 1, 1, 1], TypekaFontResource=False

## DOCM Font Evidence

- `article_with_fonts`: runs=338, chars=7478, hasVBA=False, Typeka chars={'Typeka': 6568, 'Typeka Mix': 883}
  - font chars: `{'Typeka': 6568, 'Typeka Mix': 883, 'Stencil': 19, 'LonestarW00-Regular': 8}`
  - highlight chars: `{'yellow': 746, 'black': 474, 'cyan': 9}`
- `bold_docm`: runs=140, chars=1393, hasVBA=True, Typeka chars={'Typeka': 1374}
  - font chars: `{'Typeka': 1374, 'Stencil': 19}`
  - highlight chars: `{'yellow': 205}`

## Assessment

- `Article with Fonts.docm` remains the only local source that directly records the Typeka family states.
- `magazine.pdf` does not embed visible Typeka fonts; the only reported PDF fonts are Helvetica OCR/text-layer resources. That layer should not be interpreted as printed typography.
- `Issue_26.pdf`, `Issue_27.pdf`, and `bitcoin3.pdf` expose no useful embedded Typeka font evidence; they cannot prove or disprove Typeka usage by metadata.
- `bitcoin4.pdf` is a low-resolution Issue 24 witness. It can preserve visual style, but it still does not expose printed Typeka as a usable font layer.
- The existing visual comparison still matters: those comparison articles show loud OVERDOSE art, but not the same Issue 24 orange/grey highlighted text grammar. Font uniqueness needs original layout/source files or better visual OCR, not these flattened PDFs.
- Next best move: treat Typeka as a confirmed Issue 24 formatting witness only inside `Article with Fonts.docm`; do not run more Typeka-only selectors unless a separate instruction tells us which font state to use.
