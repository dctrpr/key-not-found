# Active Punctuation / Enclosure Gate

Scope: inspect quotes, dollar sign, and terminal punctuation around locked O4/B4/G5/O5 targets. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:40:54`
- Sheet: `analysis_outputs/plain_text_transcript/active_punctuation_enclosure_gate/active_punctuation_enclosure_gate_sheet.jpg`
- Decision: `active_punctuation_enclosure_is_text_authority_not_selector`

## Summary

- Class stream: `quote+period | dollar | quote | period`.
- Class initials: `QP D Q P`.
- Punctuation-directed edge stream: `bp $ Vs t`.
- Phrase edge stream: `bp $n Vs st`.
- Active punctuation corrections: `2`.
- Instruction hit count: `0`.

## Active Contexts

| order | id | line | corridor | class | left run | right run | pick | rule |
|---:|---|---:|---:|---|---|---|---|---|
| 1 | `buying_dip` | 22 | 4 | `quote+period` | `“` | `.”` | `bp` | quoted with terminal punctuation: phrase edges |
| 2 | `one_billion` | 25 | 7 | `dollar` | `-` | `-` | `$` | dollar amount: first visible character |
| 3 | `volcano_bonds` | 27 | 9 | `quote` | `“` | `”` | `Vs` | quoted phrase: phrase edges |
| 4 | `shitcoiner_heart` | 32 | 14 | `period` | `-` | `.` | `t` | terminal punctuation: last character |

## Active Correction Rows

| index | raw | fixed | targets | adds selector permission |
|---:|---|---|---|---:|
| 5 | `"buying the dip".` | `"buying the dip."` | `O4` | `False` |
| 6 | `collateralized to pay off the IMF` | `collateralized “Volcano Bonds” to pay off the IMF` | `G5` | `False` |
| 14 | `requires printing and wars` | `requires money printing and wars` | `-` | `False` |

## Assessment

- The active quartet has a real punctuation/enclosure pattern: O4 is quoted with terminal punctuation, B4 is a dollar amount, G5 is quoted, and O5 has terminal punctuation.
- That pattern is exact-text authority, not an extraction rule: the class stream and simple punctuation-directed edge picks contain no instruction terms.
- The correction layer matters for source fidelity because it moves O4 punctuation inside the quote and restores quoted `Volcano Bonds`, but those corrections add no selector permission.
- This closes punctuation/enclosure as a current-scan active quartet selector while preserving it as a source-comparison guardrail.

## Next Move

- Use active punctuation/enclosure only to validate exact source text in future scans/layout exports; reopen it as selector evidence only if raw clue wording names quote, dollar, punctuation, first/last, or edge extraction.
