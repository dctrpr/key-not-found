# Current PDF Held-to-Light Component Readability Gate

- Created: `2026-05-24T17:56:33`
- Decision: `current_pdf_held_to_light_component_readability_no_selector`
- Fingerprint: `rows=23|active=15|slots=8|componentRows=23|components=203|letterlike=168|clean=122|visualRows=5|mergedRows=18|wordRows=19|words=110|strict=0|context=5|candidates=0|sourceR3=0|triggers=0/9|selectors=0`
- Sheet: `analysis_outputs/source_audit/current_pdf_held_to_light_component_readability_gate/current_pdf_held_to_light_component_readability_gate_sheet.jpg`

## Summary

- Candidate rows checked: `23`
- Active / OVERDOSE-slot rows: `15` / `8`
- Total source-only components: `203`
- Letter-like / clean letter-like components: `168` / `122`
- Visual-readable-like rows: `5`
- Merged or edge-dominated rows: `18`
- Source-word rows / hits: `19` / `110`
- Strict instruction hits / selector candidates: `0` / `0`
- Source-backed R3 / satisfied reopen triggers: `0` / `0/9`

## Top Rows

| pdf | transform | label | components | clean letterlike | edge comps | largest source fraction | words | strict | visual-like | source preview |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| analysis_outputs/external_clues/google_drive_article_download.pdf | back_mirror_rotate180 | O4 | 16 | 14 | 2 | 0.124 | 12 | 0 | True | global economy. RSyiERSitieisumios were publishing the white paper and a collective panic |
| keyser bitcoin .pdf | back_mirror_rotate180 | O4 | 16 | 14 | 2 | 0.124 | 12 | 0 | True | global economy. RSyiERSitieisumios were publishing the white paper and a collective panic |
| analysis_outputs/external_clues/google_drive_article_download.pdf | front_rotate180 | O4 | 15 | 12 | 3 | 0.197 | 14 | 0 | True | nervous system of the global aiaourmieurosess The cypherpunks were time after years of trying |
| keyser bitcoin .pdf | front_rotate180 | O4 | 15 | 12 | 3 | 0.197 | 14 | 0 | True | nervous system of the global aiaourmieurosess The cypherpunks were time after years of trying |
| magazine.pdf | same_side_no_mirror | B4 | 11 | 10 | 1 | 0.137 | 6 | 0 | True | Don't fa Keep your Go Bitcoin |
| analysis_outputs/external_clues/google_drive_article_download.pdf | physical_back_mirror | slot0_O_O | 15 | 13 | 1 | 0.980 | 0 | 0 | False |  |
| keyser bitcoin .pdf | physical_back_mirror | slot0_O_O | 15 | 13 | 1 | 0.980 | 0 | 0 | False |  |
| analysis_outputs/external_clues/google_drive_article_download.pdf | same_side_no_mirror | slot7_E_E | 11 | 8 | 1 | 0.982 | 0 | 0 | False |  |
| keyser bitcoin .pdf | same_side_no_mirror | slot7_E_E | 11 | 8 | 1 | 0.982 | 0 | 0 | False |  |
| analysis_outputs/external_clues/google_drive_article_download.pdf | back_mirror_rotate180 | slot7_E_E | 7 | 4 | 3 | 0.569 | 1 | 0 | False | RSyiERSitieisumios |
| keyser bitcoin .pdf | back_mirror_rotate180 | slot7_E_E | 7 | 4 | 3 | 0.569 | 1 | 0 | False | RSyiERSitieisumios |
| analysis_outputs/external_clues/google_drive_article_download.pdf | back_mirror_rotate180 | B4 | 12 | 3 | 9 | 0.157 | 6 | 0 | False | The markets sensed Markets are like |

## Decision

- Do not promote PDF-native held-to-light residue as a readable extraction layer.
- Some threshold-crossing rows contain isolated source-only components, but they trace to ordinary page-75 prose and produce no strict unit/order/action terms.
- Rows with the most residue are still merged or edge-dominated; visual-like residue does not satisfy any source-backed R3 reopen trigger.

## Next Move

- Stop extending current-PDF held-to-light component/word/color permutations unless a new source changes geometry or clue wording names transform, unit, and read order.
