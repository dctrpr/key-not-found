# Opening Spread Instruction Surface

Scope: inventory the visible text/objects on opener pages 73-74 and ask whether that layer names an extraction unit/order. No OCR extraction, key derivation, hashing, seed checking, WIF checking, or address checking was run.

- Created: `2026-05-20T21:47:32`
- Review sheet: `analysis_outputs/source_audit/opening_spread_instruction_surface/opening_spread_instruction_surface_sheet.jpg`

## Visible Surface Inventory

| id | page | kind | text/count | instruction hits |
|---|---:|---|---|---|
| `p73_small_overdose` | `73` | `label` | OVERDOSE | - |
| `p73_large_overdose` | `73` | `title` | OVERDOSE | - |
| `p73_with_max_keiser` | `73` | `credit` | with Max Keiser | - |
| `p73_vertical_footer` | `73` | `footer` | Bitcoin Magazine | El Salvador | - |
| `p73_page_number` | `73` | `page_number` | 73 | - |
| `p73_five_capsules` | `73` | `capsule_sequence` | five orange-white capsules; count=5; order=top-to-bottom on page 73 | - |
| `p74_small_overdose` | `74` | `label` | OVERDOSE | - |
| `p74_vertical_footer` | `74` | `footer` | Bitcoin Magazine | El Salvador | - |
| `p74_page_number` | `74` | `page_number` | 74 | - |
| `p74_max_and_money` | `74` | `provenance_art` | Max Keiser with thrown dollar bills in El Salvador field | - |

## Streams

| stream | value | instruction hits |
|---|---|---|
| `visibleText` | `OVERDOSE | OVERDOSE | with Max Keiser | Bitcoin Magazine | El Salvador | 73 | five orange-white capsules | OVERDOSE | Bitcoin Magazine | El Salvador | 74 | M...` | - |
| `visibleTextNoRepeats` | `OVERDOSE | with Max Keiser | Bitcoin Magazine | El Salvador | 73 | five orange-white capsules | 74 | Max Keiser with thrown dollar bills in El Salvador field` | - |
| `initialsBySurface` | `OOwMKBMES7fowcOBMES7MKwtdbiESf` | - |
| `lastsBySurface` | `EEhxrnelr3eeesEnelr4xrhnrsnlrd` | - |
| `pageNumbers` | `73 74` | - |
| `capsuleCount` | `5` | - |
| `pagePlusCapsule` | `73 74 5` | - |

## Findings

- The opener visibly confirms the provenance layer: `OVERDOSE`, `with Max Keiser`, `Bitcoin Magazine | El Salvador`, page numbers `73/74`, dollar imagery, and a five-capsule motif.
- It does not visibly state a procedural extraction rule such as read/take/select word/letter/line, mirror, fold, key, or private.
- The five-capsule motif remains a real Issue 24 ordering/provenance feature, but the existing endpoint mapping only reconfirmed O5 and did not name a unit.

## Decision

- Close the opening spread as a standalone selector under the current scan.
- Keep opener pages 73-74 as provenance/source-validation evidence for any future physical/original-layout source.
- Reopen only if a future clue explicitly names capsules, opener pages, page numbers, or the opening spread as the extraction surface.
