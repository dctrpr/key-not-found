# Registered 76/79 Word Alignment Audit

Scope: inspect the strongest registered 76/79 line pair at word level. OCR word boxes are used only as approximate labels after the high-res visual registration. No key derivation was run.

- Source p79 highlight: `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`
- Target p76 highlights: `B1 Gotta be this way... post-1971 fiat money` + `B2 nonsense`
- Overlay crop: `analysis_outputs/source_audit/registered_76_79_word_alignment.jpg`

## Word-Level Geometry

- Source OCR words inside p79 highlight: 16
- Target OCR words inside p76 B1/B2: 12
- Direct transformed-word overlaps: 0
  - None. The alignment is box/line-level, not word-box-level.

## Row Structure

- Transformed p79 source rows:
  - y=785.0: `efficient: more infinitely is bitcoin because — love`
  - y=934.1: `while even consumption, energy overall the — ORMBONG`
- p76 target rows:
  - y=854.5: `Gotta be S way. Forty years of dumb post-1971 flat money`
  - y=921.5: `RRECECy`

## Nearest Word Pairs

- `love` -> `flat` dist=68.1
- `—` -> `flat` dist=84.9
- `because` -> `post-1971` dist=67.0
- `bitcoin` -> `dumb` dist=68.5
- `is` -> `of` dist=72.9
- `infinitely` -> `years` dist=92.0
- `more` -> `way.` dist=77.4
- `efficient:` -> `be` dist=82.5
- `ORMBONG` -> `flat` dist=90.2
- `—` -> `post-1971` dist=120.8
- `the` -> `post-1971` dist=87.0
- `overall` -> `dumb` dist=99.3
- `energy` -> `of` dist=81.6
- `consumption,` -> `Forty` dist=75.6
- `even` -> `S` dist=75.9
- `while` -> `be` dist=72.9

## DOCM Font/Highlight State

- p79 source run variants: `{'TYPEKA_BOLD': 3}` highlights: `{'yellow': 3}`
- p76 target run variants: `{'TYPEKA_BOLD': 2}` highlights: `{'black': 2}`
- Relevant DOCM runs:
  - sourceP79:
    - run 299 p79 `infinitely more efficient` variant=TYPEKA_BOLD highlight=yellow bold=True
    - run 300 p79 `to transact and store wealth in than fiat, shitcoins` variant=TYPEKA_BOLD highlight=yellow bold=True
    - run 301 p79 `or gold` variant=TYPEKA_BOLD highlight=yellow bold=True
  - targetP76:
    - run 95 p76 `Gotta be this way. Forty years of dumb post-1971 fiat money` variant=TYPEKA_BOLD highlight=black bold=True
    - run 96 p76 `nonsense` variant=TYPEKA_BOLD highlight=black bold=True

## Assessment

- The strong 76/79 match is a real line/highlight-block alignment, but it does not resolve to word-level intersections under the current high-res transform.
- The nearest word pairs are positional neighbors only; they do not form readable instruction text or an obvious ordered selector.
- Both sides of the aligned pair are `TYPEKA_BOLD`; the source is yellow/orange highlight and the target is black/grey highlight. `Typeka Mix` is absent from this local anchor.
- This rules out the simple local rule “use the registered 76/79 line pair to pick overlapping words or Typeka Mix words.”
- Next best move: inspect line offsets around this anchor, especially whether the target row intentionally sits between transformed p79 source rows, or shift to the original Canva/source clue for a missing alignment instruction.
