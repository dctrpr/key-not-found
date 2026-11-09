# Current PDF Held-to-Light Color Phrase Gate

Scope: grouped the fixed held-to-light source-word trace by active page-76 color/format states (`Y/orange` and `K/black`) and tested whether color order supplies unit/order wording. No key derivation, hashes, seed/WIF/address checks, BIP39, candidate generation, or broad brute force was run.

- Created: `2026-05-24T17:44:21`
- Decision: `current_pdf_held_to_light_color_phrase_no_selector`
- Variant rows / stream rows: `12` / `60`
- All-four source-word variants imported: `6`
- Populated stream rows / source-word hits: `60` / `510`
- Strict instruction hits / action-order hits: `0` / `0`
- Context hits: `30`
- Color selector candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_held_to_light_color_phrase_gate/current_pdf_held_to_light_color_phrase_gate_sheet.jpg`
- Fingerprint: `variants=12|streams=60|allFourWords=6|populatedStreams=60|allFourStreams=30|words=510|strict=0|action=0|context=30|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## Stream Rows

| PDF | transform | mode | targets | populated | words | strict | action | context | source text |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | `physical_back_mirror` | `active_order` | `O4-B4-G5-O5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| B4: \| G5:experience. \| O5:for the gullible and unloved. |
| `magazine.pdf` | `physical_back_mirror` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| O5:for the gullible and unloved. \| B4: \| G5:experience. |
| `magazine.pdf` | `physical_back_mirror` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 3 | 10 | 0 | 0 | 1 | B4: \| G5:experience. \| O4:Buterin came up with \| O5:for the gullible and unloved. |
| `magazine.pdf` | `physical_back_mirror` | `orange_then_black` | `O4-O5-B4-G5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| O5:for the gullible and unloved. \| B4: \| G5:experience. |
| `magazine.pdf` | `physical_back_mirror` | `black_then_orange` | `B4-G5-O4-O5` | 3 | 10 | 0 | 0 | 1 | B4: \| G5:experience. \| O4:Buterin came up with \| O5:for the gullible and unloved. |
| `magazine.pdf` | `same_side_no_mirror` | `active_order` | `O4-B4-G5-O5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| B4:Keep your \| G5:of the whole Satoshi \| O5:the gullible and unloved. |
| `magazine.pdf` | `same_side_no_mirror` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. \| B4:Keep your \| G5:of the whole Satoshi |
| `magazine.pdf` | `same_side_no_mirror` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 4 | 12 | 0 | 0 | 1 | B4:Keep your \| G5:of the whole Satoshi \| O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. |
| `magazine.pdf` | `same_side_no_mirror` | `orange_then_black` | `O4-O5-B4-G5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. \| B4:Keep your \| G5:of the whole Satoshi |
| `magazine.pdf` | `same_side_no_mirror` | `black_then_orange` | `B4-G5-O4-O5` | 4 | 12 | 0 | 0 | 1 | B4:Keep your \| G5:of the whole Satoshi \| O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. |
| `magazine.pdf` | `back_mirror_rotate180` | `active_order` | `O4-B4-G5-O5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| B4:The markets \| G5:Yes. \| O5:TOXIC AF |
| `magazine.pdf` | `back_mirror_rotate180` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| O5:TOXIC AF \| B4:The markets \| G5:Yes. |
| `magazine.pdf` | `back_mirror_rotate180` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 4 | 8 | 0 | 0 | 0 | B4:The markets \| G5:Yes. \| O4:publishing the white \| O5:TOXIC AF |
| `magazine.pdf` | `back_mirror_rotate180` | `orange_then_black` | `O4-O5-B4-G5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| O5:TOXIC AF \| B4:The markets \| G5:Yes. |
| `magazine.pdf` | `back_mirror_rotate180` | `black_then_orange` | `B4-G5-O4-O5` | 4 | 8 | 0 | 0 | 0 | B4:The markets \| G5:Yes. \| O4:publishing the white \| O5:TOXIC AF |
| `magazine.pdf` | `front_rotate180` | `active_order` | `O4-B4-G5-O5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| B4: \| G5: \| O5:TOXIC AF |
| `magazine.pdf` | `front_rotate180` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| O5:TOXIC AF \| B4: \| G5: |
| `magazine.pdf` | `front_rotate180` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 2 | 4 | 0 | 0 | 0 | B4: \| G5: \| O4:The cypherpunks \| O5:TOXIC AF |
| `magazine.pdf` | `front_rotate180` | `orange_then_black` | `O4-O5-B4-G5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| O5:TOXIC AF \| B4: \| G5: |
| `magazine.pdf` | `front_rotate180` | `black_then_orange` | `B4-G5-O4-O5` | 2 | 4 | 0 | 0 | 0 | B4: \| G5: \| O4:The cypherpunks \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `physical_back_mirror` | `active_order` | `O4-B4-G5-O5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| B4: \| G5:experience. \| O5:for the gullible and unloved. |
| `keyser bitcoin .pdf` | `physical_back_mirror` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| O5:for the gullible and unloved. \| B4: \| G5:experience. |
| `keyser bitcoin .pdf` | `physical_back_mirror` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 3 | 10 | 0 | 0 | 1 | B4: \| G5:experience. \| O4:Buterin came up with \| O5:for the gullible and unloved. |
| `keyser bitcoin .pdf` | `physical_back_mirror` | `orange_then_black` | `O4-O5-B4-G5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| O5:for the gullible and unloved. \| B4: \| G5:experience. |
| `keyser bitcoin .pdf` | `physical_back_mirror` | `black_then_orange` | `B4-G5-O4-O5` | 3 | 10 | 0 | 0 | 1 | B4: \| G5:experience. \| O4:Buterin came up with \| O5:for the gullible and unloved. |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | `active_order` | `O4-B4-G5-O5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| B4:Keep your \| G5:of the whole Satoshi \| O5:the gullible and unloved. |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. \| B4:Keep your \| G5:of the whole Satoshi |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 4 | 12 | 0 | 0 | 1 | B4:Keep your \| G5:of the whole Satoshi \| O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | `orange_then_black` | `O4-O5-B4-G5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. \| B4:Keep your \| G5:of the whole Satoshi |
| `keyser bitcoin .pdf` | `same_side_no_mirror` | `black_then_orange` | `B4-G5-O4-O5` | 4 | 12 | 0 | 0 | 1 | B4:Keep your \| G5:of the whole Satoshi \| O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | `active_order` | `O4-B4-G5-O5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| B4:The markets \| G5:Yes. \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| O5:TOXIC AF \| B4:The markets \| G5:Yes. |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 4 | 8 | 0 | 0 | 0 | B4:The markets \| G5:Yes. \| O4:publishing the white \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | `orange_then_black` | `O4-O5-B4-G5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| O5:TOXIC AF \| B4:The markets \| G5:Yes. |
| `keyser bitcoin .pdf` | `back_mirror_rotate180` | `black_then_orange` | `B4-G5-O4-O5` | 4 | 8 | 0 | 0 | 0 | B4:The markets \| G5:Yes. \| O4:publishing the white \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `front_rotate180` | `active_order` | `O4-B4-G5-O5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| B4: \| G5: \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `front_rotate180` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| O5:TOXIC AF \| B4: \| G5: |
| `keyser bitcoin .pdf` | `front_rotate180` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 2 | 4 | 0 | 0 | 0 | B4: \| G5: \| O4:The cypherpunks \| O5:TOXIC AF |
| `keyser bitcoin .pdf` | `front_rotate180` | `orange_then_black` | `O4-O5-B4-G5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| O5:TOXIC AF \| B4: \| G5: |
| `keyser bitcoin .pdf` | `front_rotate180` | `black_then_orange` | `B4-G5-O4-O5` | 2 | 4 | 0 | 0 | 0 | B4: \| G5: \| O4:The cypherpunks \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | `active_order` | `O4-B4-G5-O5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| B4: \| G5:experience. \| O5:for the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| O5:for the gullible and unloved. \| B4: \| G5:experience. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 3 | 10 | 0 | 0 | 1 | B4: \| G5:experience. \| O4:Buterin came up with \| O5:for the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | `orange_then_black` | `O4-O5-B4-G5` | 3 | 10 | 0 | 0 | 1 | O4:Buterin came up with \| O5:for the gullible and unloved. \| B4: \| G5:experience. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `physical_back_mirror` | `black_then_orange` | `B4-G5-O4-O5` | 3 | 10 | 0 | 0 | 1 | B4: \| G5:experience. \| O4:Buterin came up with \| O5:for the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | `active_order` | `O4-B4-G5-O5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| B4:Keep your \| G5:of the whole Satoshi \| O5:the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. \| B4:Keep your \| G5:of the whole Satoshi |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 4 | 12 | 0 | 0 | 1 | B4:Keep your \| G5:of the whole Satoshi \| O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | `orange_then_black` | `O4-O5-B4-G5` | 4 | 12 | 0 | 0 | 1 | O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. \| B4:Keep your \| G5:of the whole Satoshi |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `same_side_no_mirror` | `black_then_orange` | `B4-G5-O4-O5` | 4 | 12 | 0 | 0 | 1 | B4:Keep your \| G5:of the whole Satoshi \| O4:(MRERREIGStY epithet. \| O5:the gullible and unloved. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | `active_order` | `O4-B4-G5-O5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| B4:The markets \| G5:Yes. \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| O5:TOXIC AF \| B4:The markets \| G5:Yes. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 4 | 8 | 0 | 0 | 0 | B4:The markets \| G5:Yes. \| O4:publishing the white \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | `orange_then_black` | `O4-O5-B4-G5` | 4 | 8 | 0 | 0 | 0 | O4:publishing the white \| O5:TOXIC AF \| B4:The markets \| G5:Yes. |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `back_mirror_rotate180` | `black_then_orange` | `B4-G5-O4-O5` | 4 | 8 | 0 | 0 | 0 | B4:The markets \| G5:Yes. \| O4:publishing the white \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | `active_order` | `O4-B4-G5-O5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| B4: \| G5: \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | `visual_state_y_then_k` | `O4-O5-B4-G5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| O5:TOXIC AF \| B4: \| G5: |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | `visual_state_k_then_y` | `B4-G5-O4-O5` | 2 | 4 | 0 | 0 | 0 | B4: \| G5: \| O4:The cypherpunks \| O5:TOXIC AF |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | `orange_then_black` | `O4-O5-B4-G5` | 2 | 4 | 0 | 0 | 0 | O4:The cypherpunks \| O5:TOXIC AF \| B4: \| G5: |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `front_rotate180` | `black_then_orange` | `B4-G5-O4-O5` | 2 | 4 | 0 | 0 | 0 | B4: \| G5: \| O4:The cypherpunks \| O5:TOXIC AF |

## Decision

- Do not promote the active color split as a held-to-light source selector.
- Y/orange and K/black grouping changes the read order of ordinary page-75 prose, but it adds no strict unit/order/action wording.
- The color split remains useful as a source-validation fingerprint (`YKKY` / `OBBO`), not as an extraction rule.

## Next Move

- Keep color/format streams as source-comparison guardrails. A new source or raw clue still needs to provide transform, unit, and read order before any selector/key branch reopens.
