# Page-76 Target Text Authority Lock

Scope: verify the target phrases used by the source-acquisition packet across corrected canonical text, DOCM text, raw user plain text, Markdown transcript, and annotated transcript. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.

- Created: `2026-05-20T23:24:03`
- Sheet: `analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock_sheet.jpg`
- Decision: `page76_target_text_authority_locked_to_canonical_docm_markdown_annotated`

## Source Phrase Coverage

| source | authoritative | present | missing | note |
|---|---:|---:|---:|---|
| `canonical_plain` | `True` | `10` | `0` | all target phrases present |
| `docm_text` | `True` | `10` | `0` | all target phrases present |
| `user_raw_plain` | `False` | `9` | `1` | volcano_bonds |
| `markdown_transcript` | `True` | `10` | `0` | all target phrases present |
| `annotated_transcript` | `False` | `9` | `1` | trust_that_guy |

## Active Corridor Corrections

- Correction `5`: `"buying the dip".` -> `"buying the dip."`; active hits `['O4']`; selector permission `False`
- Correction `6`: `collateralized to pay off the IMF` -> `collateralized “Volcano Bonds” to pay off the IMF`; active hits `['G5']`; selector permission `False`
- Correction `14`: `requires printing and wars` -> `requires money printing and wars`; active hits `[]`; selector permission `False`

## Authority Lock

- Target text authority: `canonical_plain + docm_text + markdown_transcript`
- Raw plain text use: `context_only_not_authority_for_G5`
- Annotated transcript use: `format/highlight witness, not exact-prose authority`
- Reason: The latest raw plain-text paste omits the G5 `Volcano Bonds` phrase; the annotated transcript inserts notes into prose. Canonical/DOCM/Markdown witnesses preserve the exact active target wording cleanly.

## Next Move

- Use canonical/DOCM/Markdown witnesses for page-76 target wording; keep annotated text as a format witness and raw plain text as context only. Continue requiring new source/clue R1-R5 before extraction.
