# P78 Contact-Role Grammar

Scope: test whether the repaired p78 frame contacts form a small human-readable extraction grammar. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T19:38:34`
- Overlay: `analysis_outputs/source_audit/p78_contact_role_grammar/p78_contact_role_grammar_overlay.jpg`
- Chosen frame: `g5_edge_touch` `[1196.0, 2398.0, 2212.0, 2950.0]`
- Tri-contact pass: `True`
- G5/O5 line gap: `5`; G5 line + 5 equals O5 line: `True`
- M3/M4 wedge selected anchors from prior audit: `shitcoiner at heart`

## Contacts

| edge | id | label | kind | role | evidence |
|---|---|---|---|---|---|
| `T` | `T-cut` | `should sell` | `text` | top edge text cut | edge-adjacent audit top_cut_inside |
| `L` | `G5_trusted` | `Volcano Bonds` | `black_text` | left edge touches G5 after dx=-38 repair | left edge gap 0.0 px, vertical overlap 48.0 px |
| `R` | `M3` | `standalone mark` | `visual_mark` | right edge cuts M3 and M3 axis remains in the mark | right-edge M3 overlap 265.0 px, axis in mark True |
| `B` | `O5` | `shitcoiner at heart` | `orange_text` | bottom edge clips O5 | bottom O5 width 465.0 px, O5 overlap 0.26957 |

## Read Orders

| order | edges | ids | labels | initials | instruction hits |
|---|---|---|---|---|---|
| `clockwise_top_start` | `TRBL` | `T-cut | M3 | O5 | G5_trusted` | `should sell | standalone mark | shitcoiner at heart | Volcano Bonds` | `ss sm sah VB` | `` |
| `counterclockwise_top_start` | `TLBR` | `T-cut | G5_trusted | O5 | M3` | `should sell | Volcano Bonds | shitcoiner at heart | standalone mark` | `ss VB sah sm` | `` |
| `tri_contact_edges_left_right_bottom` | `LRB` | `G5_trusted | M3 | O5` | `Volcano Bonds | standalone mark | shitcoiner at heart` | `VB sm sah` | `` |
| `tri_contact_clockwise_left_start` | `LRB` | `G5_trusted | M3 | O5` | `Volcano Bonds | standalone mark | shitcoiner at heart` | `VB sm sah` | `` |
| `tri_contact_counterclockwise_left_start` | `LBR` | `G5_trusted | O5 | M3` | `Volcano Bonds | shitcoiner at heart | standalone mark` | `VB sah sm` | `` |
| `text_contacts_only` | `LB` | `G5_trusted | O5` | `Volcano Bonds | shitcoiner at heart` | `VB sah` | `` |
| `color_or_medium_black_mark_orange` | `LRB` | `G5_trusted | M3 | O5` | `Volcano Bonds | standalone mark | shitcoiner at heart` | `VB sm sah` | `` |
| `top_then_text_contacts` | `TLB` | `T-cut | G5_trusted | O5` | `should sell | Volcano Bonds | shitcoiner at heart` | `ss VB sah` | `` |
| `bottom_then_left_then_right` | `BLR` | `O5 | G5_trusted | M3` | `shitcoiner at heart | Volcano Bonds | standalone mark` | `sah VB sm` | `` |

## Assessment

- The dx=-38 p78 frame has a stable three-object contact grammar: left touches G5, right cuts M3, and bottom clips O5.
- Adding the top edge gives ordinary nearby article text ('should sell'), not an instruction.
- Clockwise, counterclockwise, edge-role, medium/color, and text-only readings produce labels/initials only; no instruction-like terms appear in the content streams.
- The grammar reconfirms registration and the G5/O5 five-line structure, but it still does not name a word, letter, line, direction, or key unit.
- This closes p78 contact-role ordering as a standalone selector under the current scan.

## Decision

- Do not promote p78 contact-role grammar to extraction evidence; use it only as source-registration validation.
- Next move: Use the Typeka/font layer and comparison articles to ask whether the three fonts regular/mix/bold provide the missing extraction unit around the page-76 G5/O5 corridor.
