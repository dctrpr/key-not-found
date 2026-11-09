# G5/O5 Local Unit Rules Audit

Scope: test whether the narrowed page-76 pair provides a simple extraction unit through omitted overlap characters, adjacent words, line/word positions, or the visible 5/6 dosage numbers. No key candidates or hashing were generated.

- Created: `2026-05-20T05:38:17`

## Pair

- G5: `Volcano Bonds` on line `27` zero-based / `28` one-based, word positions `[224, 225]` one-based.
- O5: `shitcoiner at heart` on line `32` zero-based / `33` one-based, word positions `[275, 276, 277]` one-based.
- Line gap: `5`.
- G5 line + 5 equals O5 line: `True`.

## Local Units

| unit | result |
|---|---|
| omitted overlap | `s., .s` / reverse `.s, s.` |
| initials | `VBsah` |
| last letters | `osrtt` |
| word lengths | `[7, 5, 10, 2, 5]` |
| line word 5/6 | G5 `pay/off`, O5 `shitcoiner/at` |
| after/before phrase 5/6 | after G5 `IMF/loan`, before O5 `guy/that` |

## Context

- G5 line: `collateralized Volcano Bonds to pay off the IMF`
- O5 line: `Maybe because he's a shitcoiner at heart`
- G5 context before: `worth of future bitcoin earnings collateralized`
- G5 context after: `to pay off the IMF loan`
- O5 context before: `that guy Maybe because he's a`
- O5 context after: `(none)`

## Assessment

- The cleanest structural fact is the five-line locator: `Volcano Bonds` is exactly five text lines above `shitcoiner at heart` in the corrected page-76 model.
- That explains why repeated 5/dosage/symptom evidence keeps pointing here, but it does not provide the final extraction unit.
- Omitted characters, adjacent words, initials, endings, word lengths, and simple 5/6 word picks do not produce an instruction.
- Next best move: look for a source/provenance or physical-registration clue that says what to extract from the already-located G5/O5 target.
