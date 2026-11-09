# External Clue Unit/Order Intake

Scope: separate raw/raw-like external clue wording from derived report prose and test whether any archived clue satisfies R3 by naming the extraction unit/order. No extraction, hashing, seed, WIF, address, or candidate checks were run.

- Created: `2026-05-20T22:27:42`
- Raw/raw-like records: `5`
- Raw/raw-like R3 passes: `0`
- Derived R3 passes: `0`
- Decision: `no_archived_raw_external_clue_names_extraction_unit_order`

## Raw / Raw-Like Records

| id | rawness | unit hits | target hits | classification | R3 | reason |
|---|---|---|---|---|---|---|
| `tweet_announcement` | `raw` | `-` | `-` | `no_unit_order` | `FAIL` | No unit/order term appears in the raw text. |
| `tweet_schott_mirror_clue` | `raw` | `-` | `-` | `no_unit_order` | `FAIL` | No unit/order term appears in the raw text. |
| `announcement_text_inventory` | `raw` | `-` | `-` | `no_unit_order` | `FAIL` | No unit/order term appears in the raw text. |
| `schott_title` | `raw_linked_title` | `-` | `-` | `no_unit_order` | `FAIL` | No unit/order term appears in the raw text. |
| `canva_live_text` | `source_adjacent` | `line` | `-` | `orientation_not_extraction` | `FAIL` | `line` appears in geometric/orientation language, not as a line-index instruction. |

## Derived / Manual Labels

| id | rawness | unit hits | target hits | classification | use |
|---|---|---|---|---|---|
| `schott_operation_literal_mirror` | `derived` | `letters` | `-` | `unit_without_target` | target/provenance only |
| `schott_operation_handedness_left / right_hemisphere` | `derived` | `first, last` | `-` | `non_actionable_unit` | target/provenance only |
| `schott_operation_bimanual / corpus_callosum` | `derived` | `order` | `p76` | `targeting_not_extraction` | target/provenance only |
| `schott_operation_Leonardo / reversed writing` | `derived` | `-` | `-` | `no_unit_order` | target/provenance only |
| `announcement_media_1` | `derived_visual_label` | `-` | `bukele` | `no_unit_order` | target/provenance only |
| `announcement_media_2` | `derived_visual_label` | `-` | `el salvador, bukele` | `no_unit_order` | target/provenance only |
| `announcement_media_3` | `derived_visual_label` | `-` | `-` | `no_unit_order` | target/provenance only |
| `announcement_media_4` | `derived_visual_label` | `-` | `bukele` | `no_unit_order` | target/provenance only |
| `announcement_media_5` | `derived_visual_label` | `-` | `el salvador` | `no_unit_order` | target/provenance only |
| `announcement_media_6` | `derived_visual_label` | `-` | `el salvador, volcano` | `no_unit_order` | target/provenance only |
| `announcement_media_7` | `derived_visual_label` | `-` | `volcano` | `no_unit_order` | target/provenance only |

## Contamination Check

- Earlier external term frontier scanned `23` files and found `1` actionable raw-ish co-occurrence, but that hit was the Canva orientation/source-fidelity note rather than an extraction unit/order.
- Terms like `word`, `letter`, `read`, and `select` inside our generated reports are not eligible source evidence.
- The public clue index selector is already closed as a standalone selector; its direct index streams selected ordinary article words and no procedural language.

## Decision

- Archived raw clue text says: private Bitcoin key, encoded, this piece, Mr. President, 20 BTC.
- The Schott link says mirror writing and supports mirror/reversal/left-right concepts.
- The Canva note says pills/XX/barbed-wire/SHIT spills are orientation/positioning/source-fidelity clues.
- None names a source-backed unit/order such as take word N, read line X, select letters, use font state, first/last, edge, or similar.

## Next Move

- Keep archived clues as constraints: source piece, private Bitcoin key, mirror-writing operation family, page-76/Bukele/volcano target confirmation, and Canva source-registration gaps. Reopen only with new raw clue/provenance wording or new physical/original-layout source evidence.
