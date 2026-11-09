# Source Packet False-Positive Guardrail

Scope: identify visually tempting future source-match classes that must be rejected without source-backed unit/order wording. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T06:57:19`
- Guardrail count: `9`
- Hard rejects without R3: `9`
- Selector unlocks: `0`
- Active visual-state order: `YKKY`
- Active page lines: `22 25 27 32`
- Active corridor indexes: `4 7 9 14`
- False-positive guardrail fingerprint: `guardrails=9|hardReject=9|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|selectorUnlocks=0|requiresR3=1`
- Sheet: `analysis_outputs/source_audit/source_packet_false_positive_guardrail/source_packet_false_positive_guardrail_sheet.jpg`

## Guardrail Rows

| id | tempting match | controlled by | reject reason | required to reopen |
|---|---|---|---|---|
| `color_or_state_only` | OBBO/YKKY color-state match: color palindrome=True, visual palindrome=True | full-page Y/K non-active controls=4; OVERDOSE controls=NNNNNNNNN | Color/state alone cannot prove orientation or extraction order. | line order 22/25/27/32; corridor order 4/7/9/14; source-backed unit/order wording |
| `native_unrotated_order` | Native raw order 32 27 25 22 or 14 9 7 4 | readable/upright order 22 25 27 32 / 4 7 9 14 | A visually matched native source that is not rotated 180 degrees reverses line/corridor order. | rotate native source images 180 degrees; recover readable/upright active order; reject raw-native reversed order as orientation error |
| `c9_frame_only` | C9/Y-K frame contains active targets 4/4 | C9 is broad, horizontally mirror-invariant, and source-validation only | Frame containment is a benchmark, not a selector. | source wording that names the frame as a reading boundary; unit/order wording inside or tied to the frame; controls must fail under the same rule |
| `overdose_black_over` | Active black OVER projections=2 | p75 control OVER projections=2; mirrored p75 matches active=8/8 | OVER/REVO/DOSE-style slot matches are controlled by p75 and have no instruction wording. | raw/source instruction tying OVERDOSE glyph slots to active boxes; control pages must not reproduce the same slot stream; explicit unit/order extraction wording |
| `p78_contact_or_dx_repair` | repaired p78 max partial=2/4; max full=0/4 | B4/O4 need touch expansions 503/173 px | dx repair improves residual contact but does not cover the active quartet. | source-backed reason for dx repair; all four active boxes inside without context-band leakage; unit/order wording |
| `p78_full_cover_leakage` | full-cover repair spans 102 words | non-target words=92; hard hits=0 | Forcing coverage takes the whole lower-corridor context band. | new source must avoid L22-L32 context-band leakage; new source must isolate target units; hard instruction wording must be present |
| `bold_or_annotation_only` | format pass=4; line-bold exact=2/4 | witness conflicts=2; Markdown/notes are witness layers | Bold/highlight witnesses validate formatting but do not supply a unit/order selector. | DOCM/high-res/crop-pack agreement; source-backed unit/order wording; do not rely on Markdown bold or annotated notes alone |
| `active_box_ocr_text` | active box exact OCR matches=0/4 | corrupted/misread boxes=4/4; usable=False | 3D map OCR inside target boxes is not text authority. | use canonical plain text + DOCM text + Markdown transcript; use 3D OCR only as geometry witness; do not extract key text from corrupted target-box OCR |
| `loose_alignment` | common shift tolerance=4 px | alignment first pad failure is already below loose visual matching | A future source match that only works outside the current narrow tolerance is a false positive unless explained. | explain any shift larger than current tolerance; preserve line/corridor order and visual state; pass all R1-R5 source-reopen gates |

## Decision

- Reject visual-only matches for future source comparison.
- Color/state, native raw order, C9 frame containment, OVERDOSE slot spelling, repaired p78 contacts, bold/highlight witness state, and 3D target-box OCR each have an existing control or ambiguity.
- A future source can reopen extraction only if it preserves the active order/visual state and supplies source-backed R3 unit/order wording.

## Next Move

- Use these guardrails with the handoff integrity matrix when reviewing any new source asset. Do not reopen extraction for visual-only matches.
