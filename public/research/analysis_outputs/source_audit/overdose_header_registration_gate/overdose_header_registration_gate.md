# OVERDOSE Header Registration Gate

Scope: compare the p78 source graphic against page-76 active targets using the repeated `OVERDOSE` header placement. No OCR, key derivation, hashing, seed/WIF checks, or address checks were run.

- Created: `2026-05-21T01:04:43`
- Sheet: `analysis_outputs/source_audit/overdose_header_registration_gate/overdose_header_registration_gate_sheet.jpg`
- p76 OVERDOSE center: `[2221.12, 168.65]`
- p78 OVERDOSE center: `[2231.8, 165.13]`
- Header translation: `dx=-10.68, dy=3.51`

## Scenario Summary

| scenario | p76 frame box | active full | active partial | active hits | strict unit hits |
|---|---:|---:|---:|---|---:|
| current p78 horizontal mirror | `[1234.0, 2398.0, 2250.0, 2950.0]` | `0` | `1` | O5 | `0` |
| same layout slot / no mirror | `[294.0, 2398.0, 1310.0, 2950.0]` | `2` | `1` | B4_text, G5, O5 | `0` |
| OVERDOSE header translation | `[283.32, 2401.51, 1299.32, 2953.51]` | `2` | `1` | B4_text, G5, O5 | `0` |

## Active Target Contacts

### current p78 horizontal mirror

| target | overlap vs target | gap px | relation |
|---|---:|---:|---|
| `O5` O5 shitcoiner at heart | `0.247536` | `0.0` | `partial` |
| `O4` O4 buying the dip | `0.0` | `197.0` | `miss` |
| `G5` G5 Volcano Bonds | `0.0` | `238.5` | `miss` |
| `B4_text` B4 $1 billion | `0.0` | `674.5` | `miss` |

### same layout slot / no mirror

| target | overlap vs target | gap px | relation |
|---|---:|---:|---|
| `B4_text` B4 $1 billion | `1.0` | `0.0` | `full` |
| `G5` G5 Volcano Bonds | `1.0` | `0.0` | `full` |
| `O5` O5 shitcoiner at heart | `0.156522` | `0.0` | `partial` |
| `O4` O4 buying the dip | `0.0` | `324.21` | `miss` |

### OVERDOSE header translation

| target | overlap vs target | gap px | relation |
|---|---:|---:|---|
| `G5` G5 Volcano Bonds | `1.0` | `0.0` | `full` |
| `B4_text` B4 $1 billion | `0.925319` | `0.0` | `full` |
| `O5` O5 shitcoiner at heart | `0.179648` | `0.0` | `partial` |
| `O4` O4 buying the dip | `0.0` | `334.85` | `miss` |

## Assessment

- The repeated OVERDOSE header placement gives only a tiny p78->p76 translation and is effectively a same-layout-slot test, not a fold/mirror instruction.
- The same-layout/header-translation frame fully covers B4 and G5 and partially clips O5, but it misses O4 and supplies no strict unit/order term.
- The current horizontal mirror frame preserves the known p78 registration benchmark, but it only clips O5 among the four active targets and also supplies no unit/order term.
- Therefore OVERDOSE header/layout registration is useful as a source-comparison benchmark only; it does not unlock extraction under the current scan.

## Decision

- `OVERDOSE` header/layout registration is closed as a current-scan selector.
- Keep same-layout-slot contacts as source-comparison validation only; no selector was unlocked.
- Next move: Use same-layout-slot contacts as a secondary validation check only if a future original-layout/source item explicitly points to repeated OVERDOSE page layout; otherwise keep the source/physical R1-R5 gate.
