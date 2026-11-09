# Current PDF Held-to-Light All-Target Phrase Gate

Scope: traced all four locked page-76 active target boxes through fixed PDF held-to-light orientation transforms, then assembled the page-75 source words in active order. No key derivation, hashes, seed/WIF/address checks, BIP39, candidate generation, or broad brute force was run.

- Created: `2026-05-24T17:36:39`
- Decision: `current_pdf_held_to_light_all_target_phrase_no_selector`
- PDFs / transforms / variants: `3` / `4` / `12`
- Active target rows: `48`
- All-four source-word variants: `6`
- Target rows with source words / source-word hits: `39` / `102`
- Strict instruction rows / hits: `0` / `0`
- Action/order rows / hits: `0` / `0`
- Context rows / hits: `6` / `6`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate/current_pdf_held_to_light_all_target_phrase_gate_sheet.jpg`
- Fingerprint: `pdfs=3|transforms=4|variants=12|targetRows=48|allFourWords=6|wordRows=39|words=102|strictRows=0|strict=0|actionRows=0|action=0|contextRows=6|context=6|sourceR3=0|triggers=0/9|selectors=0`

## Variant Rows

| PDF | transform | word rows | all-four words | strict rows | action/order rows | context rows | source words | assembled active-order source text |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | `physical_back_mirror` | 3 | 0 | 0 | 0 | 1 | 10 | O4:Buterin came up with \| B4: \| G5:experience. \| O5:for the gullible and unloved. |
| `magazine.pdf` | `same_side_no_mirror` | 4 | 1 | 0 | 0 | 1 | 12 | O4:(MRERREIGStY epithet. \| B4:Keep your \| G5:of the whole Satoshi \| O5:the gullible and unloved. |
| `magazine.pdf` | `back_mirror_rotate180` | 4 | 1 | 0 | 0 | 0 | 8 | O4:publishing the white \| B4:The markets \| G5:Yes. \| O5:TOXIC AF |
| `magazine.pdf` | `front_rotate180` | 2 | 0 | 0 | 0 | 0 | 4 | O4:The cypherpunks \| B4: \| G5: \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `physical_back_mirror` | 3 | 0 | 0 | 0 | 1 | 10 | O4:Buterin came up with \| B4: \| G5:experience. \| O5:for the gullible and unloved. |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | 4 | 1 | 0 | 0 | 1 | 12 | O4:(MRERREIGStY epithet. \| B4:Keep your \| G5:of the whole Satoshi \| O5:the gullible and unloved. |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | 4 | 1 | 0 | 0 | 0 | 8 | O4:publishing the white \| B4:The markets \| G5:Yes. \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `front_rotate180` | 2 | 0 | 0 | 0 | 0 | 4 | O4:The cypherpunks \| B4: \| G5: \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | 3 | 0 | 0 | 0 | 1 | 10 | O4:Buterin came up with \| B4: \| G5:experience. \| O5:for the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | 4 | 1 | 0 | 0 | 1 | 12 | O4:(MRERREIGStY epithet. \| B4:Keep your \| G5:of the whole Satoshi \| O5:the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | 4 | 1 | 0 | 0 | 0 | 8 | O4:publishing the white \| B4:The markets \| G5:Yes. \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | 2 | 0 | 0 | 0 | 0 | 4 | O4:The cypherpunks \| B4: \| G5: \| O5:TOXIC AF |

## Decision

- Do not promote all-target PDF held-to-light source phrasing as a selector.
- Some fixed orientations put ordinary page-75 prose under all four active target boxes, but none produce strict unit/order/action wording.
- The original `magazine.pdf` physical-back orientation has no complete active-order phrase, and all-four phrase rows only appear in orientation controls without source-backed R3 or reopen triggers.

## Next Move

- Stop extending PDF held-to-light text tracing unless new source material changes the geometry or a raw clue names a transform, unit, and read order.
