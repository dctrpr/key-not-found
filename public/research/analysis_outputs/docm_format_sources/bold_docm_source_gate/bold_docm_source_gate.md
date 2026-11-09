# BOLD.docm Source Gate

Scope: consolidate whether `BOLD.docm` can serve as a source witness for the active page-76 corridor. No macros were executed, and no extraction, hashing, BIP39, WIF/Base58 scanning, OCR extraction, seed generation, or address checks were run.

- Created: `2026-05-21T00:11:28`
- Sheet: `analysis_outputs/docm_format_sources/bold_docm_source_gate/bold_docm_source_gate_sheet.jpg`
- Decision: `bold_docm_generated_artifact_not_source_or_selector`

## Summary

- BOLD active targets present: `0/4`.
- Article with Fonts active targets present: `4/4`.
- BOLD has VBA project: `True`.
- BOLD has VBA data: `True`.
- Referenced `otrobip.txt` recovered locally: `False`.

## Document Rows

| document | VBA | words | active set | context hits | use |
|---|---:|---:|---:|---:|---|
| `BOLD.docm` | `True` | `230` | `0/4` | `3` | generated/annotation sanity witness only |
| `Article with Fonts.docm` | `False` | `1281` | `4/4` | `9` | trusted formatting witness |

## Macro Evidence

- Referenced path: `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt'`.
- Local `otrobip` matches recovered: `0`.
- Routine identified: `HighlightWordsFromTextFile`.

## Gate Result

| gate | status | evidence |
|---|---|---|
| R1 source identity | `FAIL for BOLD` | BOLD.docm has a VBA highlighting workflow and is not an original layout/font source. |
| R2 target preservation | `FAIL for BOLD` | BOLD.docm contains 0/4 locked O4/B4/G5/O5 active targets; Article with Fonts contains 4/4. |
| R3 unit/order evidence | `FAIL` | The macro points to a missing word list and provides no page-76 word/letter/line/font order. |
| R4 orientation/source discipline | `PASS as classified` | BOLD is kept separate from DOCM/high-res format authority and is not used for geometry. |
| R5 controlled improvement | `FAIL` | BOLD does not improve active-corridor coverage or source registration. |

## Assessment

- `BOLD.docm` is not an independent source for the active page-76 corridor because it is macro-enabled, references a missing external word list, and omits all four locked O4/B4/G5/O5 targets.
- `Article with Fonts.docm` remains the Word-level formatting witness because it has no embedded VBA project and preserves all four active targets plus surrounding corridor terms.
- The `BOLD.docm` branch should only reopen if `otrobip.txt` or original workflow files are recovered and independently pass the source-reopen gate.

## Next Move

- Use BOLD.docm only as generated-artifact sanity evidence unless the referenced `otrobip.txt` or original workflow files are recovered; keep Article with Fonts.docm as the Word formatting witness.
