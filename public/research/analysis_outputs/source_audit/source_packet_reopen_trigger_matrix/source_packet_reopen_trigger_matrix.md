# Source Packet Reopen Trigger Matrix

- Created: `2026-05-21T07:13:04`
- Scope: source-packet reopen-trigger matrix; no OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation
- Decision: `no_current_reopen_trigger_satisfied`
- Trigger count: `9`
- Satisfied now: `0`
- Source-backed R3 bridge hits: `0`
- Guardrails still blocked: `9`
- Active order/state: lines `22 25 27 32`, corridors `4 7 9 14`, state `YKKY`
- Reopen trigger fingerprint: `triggers=9|satisfied=0|sourceR3=0|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|guardrailsBlocked=9|selectors=0`
- Sheet: `analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/source_packet_reopen_trigger_matrix_sheet.jpg`

## Trigger Rows

| guardrail | domain | exact external/source trigger | current blocker | decision |
|---|---|---|---|---|
| `color_or_state_only` | orange/black + bold state | A distinct source/original layout explicitly ties Y/K or orange/black order to a reading unit and preserves readable order 22/25/27/32. | YKKY/OBBO is palindromic and full-page Y/K has four non-active controls. | `wait_for_new_source_or_clue` |
| `native_unrotated_order` | native/source orientation | Source provenance states native coordinate direction, or a fresh extraction proves the active quartet after the documented 180-degree transform. | Native raw order reverses to 32/27/25/22 and 14/9/7/4 unless rotated 180 degrees. | `wait_for_new_source_or_clue` |
| `c9_frame_only` | C9/Y-K frame | Source shows the C9/Y-K frame as an intentional reading boundary and names the units/order inside it. | C9 frame fully contains the quartet but is broad, mirror-invariant, and source-validation only. | `wait_for_new_source_or_clue` |
| `overdose_black_over` | OVERDOSE glyph slots | Source explicitly links OVERDOSE glyph slots to active boxes and names which glyph/slot stream to read. | p75 control reproduces OVER-style slot streams; active mirrored variants are not unique. | `wait_for_new_source_or_clue` |
| `p78_contact_or_dx_repair` | folded/mirrored p78 frame geometry | Physical/original source naturally explains dx≈-38/-40 or shows the p78 frame shifted/cut in that position without manual tuning. | dx repair improves G5/O5 residuals but still gives max full containment 0/4 and max partial 2/4. | `wait_for_new_source_or_clue` |
| `p78_full_cover_leakage` | p78 frame full-cover expansion | New source isolates O4/B4/G5/O5 as units without taking the full L22-L32 lower-corridor context band. | Full cover spans 102 words, 92 non-target words, and four non-active format signals. | `wait_for_new_source_or_clue` |
| `bold_or_annotation_only` | bold/highlight/annotation witnesses | Source or provenance explicitly says to read/take/count bold, highlight, first/last, or a comparable format unit. | DOCM/high-res/crop-pack validate format only; line-level bold and annotations conflict or remain witness layers. | `wait_for_new_source_or_clue` |
| `active_box_ocr_text` | 3D box OCR text | A source text layer supplies exact text inside the target boxes, or OCR is replaced by canonical text authority tied to a unit/order instruction. | 3D active-box OCR has 0/4 exact matches and 4/4 corrupted/misread target boxes. | `wait_for_new_source_or_clue` |
| `loose_alignment` | alignment tolerance | New source explains any shift beyond the current ±4px tolerance through provenance, scaling, crop, or physical registration. | Future matches outside the current narrow tolerance are false positives unless the source explains the shift. | `wait_for_new_source_or_clue` |

## Interpretation

- Current local evidence supplies strong target-location and source-comparison benchmarks, not extraction permission.
- The reopen condition is now concrete for each tempting visual mechanism: a distinct source/provenance artifact must add the missing R3 wording or materially explain the geometry while passing R1-R5.
- Generated report prose, correction-report assessment text, and visual matches alone remain blocked.

## Next Move

Use this matrix when a new source/photo/original export/clue arrives: score the observed source change against the exact trigger row before any selector or key work resumes.
